"""
Knowledge Curator - GPT-5.4 sub-agent driven knowledge curation pipeline
Fetches external data via Tavily, structures it with LLM, saves as Markdown
"""

import fcntl
import json
import os
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from ..config import Config
from ..utils.llm_client import LLMClient
from ..utils.logger import get_logger
from .external_data_fetcher import ExternalDataFetcher

logger = get_logger('mirofish.knowledge')


class KnowledgeCurator:
    """GPT-5.4 sub-agent that curates industry knowledge from external sources"""

    def __init__(self):
        self.llm = LLMClient(use_chat_model=True)  # GPT-5.4
        self.fetcher = ExternalDataFetcher()
        self.knowledge_dir = Config.KNOWLEDGE_DIR

    def curate_for_ontology(
        self,
        ontology_entities: List[Dict[str, Any]],
        candidate_context: str = "",
        graph_id: str = ""
    ) -> Dict[str, Any]:
        """Main entry: curate knowledge based on ontology entities

        Flow: Ontology → GPT-5.4(classify) → GPT-5.4(queries) → Tavily(search) → GPT-5.4(structure) → Markdown

        Args:
            ontology_entities: List of entity types from ontology
            candidate_context: Candidate document text (optional, for better classification)
            graph_id: Zep graph ID (for logging)

        Returns:
            {
                "classification": {...},
                "curated_files": [...],
                "stats": {"queries": N, "results": N, "files": N}
            }
        """
        logger.info(f"Starting knowledge curation for graph {graph_id}")

        # Step 1: Classify candidate's industry/profession
        classification = self._classify_candidate(ontology_entities, candidate_context)
        logger.info(f"Classification: {classification}")

        # Step 2: Generate search queries
        queries = self._generate_search_queries(classification)
        logger.info(f"Generated {len(queries)} search queries")

        # Step 3: Fetch external data via Tavily
        raw_data = self._fetch_external_data(queries)
        logger.info(f"Fetched {len(raw_data)} raw results")

        # Step 4: Curate content with GPT-5.4
        curated = self._curate_content(raw_data, classification)
        logger.info(f"Curated {len(curated)} knowledge files")

        # Step 5: Save to preset_knowledge/
        saved_files = self._save_knowledge_files(curated, classification)

        return {
            "classification": classification,
            "curated_files": saved_files,
            "stats": {
                "queries": len(queries),
                "results": len(raw_data),
                "files": len(saved_files)
            }
        }

    def _classify_candidate(
        self,
        ontology_entities: List[Dict[str, Any]],
        candidate_context: str = ""
    ) -> Dict[str, Any]:
        """Use LLM to classify candidate's industry and profession"""
        try:
            return self._classify_candidate_inner(ontology_entities, candidate_context)
        except Exception as e:
            logger.warning(f"Candidate classification failed, using defaults: {e}")
            return {
                "industry": "一般",
                "industry_key": "general",
                "profession": "不明",
                "profession_key": "unknown",
                "sub_industries": [],
                "key_skills": [],
                "experience_level": "mid"
            }

    def _classify_candidate_inner(
        self,
        ontology_entities: List[Dict[str, Any]],
        candidate_context: str = ""
    ) -> Dict[str, Any]:
        """Inner implementation of candidate classification"""
        entity_summary = json.dumps(ontology_entities[:5], ensure_ascii=False, indent=2) if ontology_entities else "（エンティティ情報なし）"
        context_snippet = candidate_context[:2000] if candidate_context else "（候補者コンテキストなし）"

        result = self.llm.chat_json(
            messages=[
                {
                    "role": "system",
                    "content": "あなたはHRキャリア分析の専門家です。候補者の情報から業界・職種を正確に分類してください。純粋なJSON形式で返してください。"
                },
                {
                    "role": "user",
                    "content": f"""以下の候補者情報から業界・職種を分類してください。

## オントロジーエンティティ
{entity_summary}

## 候補者コンテキスト
{context_snippet}

以下のJSON形式で返してください:
{{
    "industry": "業界名（日本語、例: IT/ソフトウェア、コンサルティング、金融等）",
    "industry_key": "業界キー（英字スネークケース、例: it_software, consulting, finance）",
    "profession": "主要職種（日本語、例: プロダクトマネージャー、ソフトウェアエンジニア等）",
    "profession_key": "職種キー（英字スネークケース）",
    "sub_industries": ["関連サブ業界1", "関連サブ業界2"],
    "key_skills": ["主要スキル1", "主要スキル2", "主要スキル3"],
    "experience_level": "junior/mid/senior/executive"
}}"""
                }
            ],
            temperature=0.3
        )

        # Ensure required keys
        result.setdefault("industry", "一般")
        result.setdefault("industry_key", "general")
        result.setdefault("profession", "不明")
        result.setdefault("profession_key", "unknown")
        result.setdefault("sub_industries", [])
        result.setdefault("key_skills", [])
        result.setdefault("experience_level", "mid")

        # Sanitize keys to alphanumeric + underscore only (prevent path traversal)
        result["industry_key"] = self._sanitize_key(result["industry_key"])
        result["profession_key"] = self._sanitize_key(result["profession_key"])

        return result

    @staticmethod
    def _sanitize_key(key: str) -> str:
        """Sanitize key to alphanumeric and underscore only (prevent path traversal)"""
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', str(key))
        return sanitized or "unknown"

    def _generate_search_queries(self, classification: Dict[str, Any]) -> List[Dict[str, str]]:
        """Use LLM to generate Tavily search queries"""
        result = self.llm.chat_json(
            messages=[
                {
                    "role": "system",
                    "content": "あなたはリサーチ専門家です。候補者の業界・職種に関する最新の市場情報を収集するための検索クエリを生成してください。純粋なJSON形式で返してください。"
                },
                {
                    "role": "user",
                    "content": f"""以下の候補者分類に基づき、Tavily Web検索用のクエリを生成してください。

## 候補者分類
- 業界: {classification['industry']}
- 職種: {classification['profession']}
- スキル: {', '.join(classification.get('key_skills', []))}
- 経験レベル: {classification.get('experience_level', 'mid')}

以下のカテゴリ別に検索クエリを生成してください:

1. industries (業界動向): 業界の最新動向・将来予測・主要プレイヤー
2. job_market (求人市場): 年収相場・求人動向・採用トレンド
3. career_patterns (キャリアパターン): キャリアパス・転職パターン・成功要因

JSON形式:
{{
    "queries": [
        {{"query": "検索クエリ文字列", "category": "industries|job_market|career_patterns", "topic": "general|news"}}
    ]
}}

各カテゴリ2-3個、合計6-9個のクエリを生成してください。日本市場の情報を優先してください。"""
                }
            ],
            temperature=0.5
        )

        return result.get("queries", [])

    def _fetch_external_data(self, queries: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Fetch data from Tavily for each query"""
        if not self.fetcher.is_available:
            logger.info("Tavily not available, will use LLM fallback for content generation")
            return []

        all_results = []
        for q in queries:
            query_text = q.get("query", "")
            topic = q.get("topic", "general")
            category = q.get("category", "general")

            results = self.fetcher.search(
                query=query_text,
                topic=topic,
                search_depth="advanced",
                max_results=5
            )

            for r in results:
                r["category"] = category
                r["query"] = query_text
            all_results.extend(results)

        return all_results

    def _curate_content(
        self,
        raw_data: List[Dict[str, Any]],
        classification: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Use GPT-5.4 to structure raw search results into Markdown files"""

        # Group by category
        by_category: Dict[str, List[Dict]] = {}
        for item in raw_data:
            cat = item.get("category", "general")
            by_category.setdefault(cat, []).append(item)

        curated_files = []

        # Define file generation tasks
        safe_industry_key = self._sanitize_key(classification['industry_key'])
        tasks = [
            {
                "category": "industries",
                "filename": f"{safe_industry_key}.md",
                "title": f"{classification['industry']}業界動向",
                "instruction": "業界の最新動向、主要プレイヤー、技術トレンド、将来予測をまとめてください。"
            },
            {
                "category": "job_market",
                "filename": "salary_benchmarks.md",
                "title": f"{classification['profession']}の年収・求人動向",
                "instruction": "この職種の年収相場（ジュニア/ミドル/シニア/エグゼクティブ別）、求人倍率、採用トレンドをまとめてください。"
            },
            {
                "category": "job_market",
                "filename": "hiring_trends.md",
                "title": f"{classification['industry']}の採用トレンド",
                "instruction": "この業界の採用動向、求められるスキルの変化、リモートワーク動向、AI/DXの影響をまとめてください。"
            },
            {
                "category": "job_market",
                "filename": "skill_demand.md",
                "title": f"{classification['profession']}のスキル需要",
                "instruction": "この職種で需要が高いスキル（現在＋今後3-5年）、資格、経験をまとめてください。"
            },
            {
                "category": "career_patterns",
                "filename": "common_transitions.md",
                "title": f"{classification['profession']}のキャリアパス",
                "instruction": "この職種からの典型的なキャリアパス、転職パターン、マネジメント/スペシャリスト分岐をまとめてください。"
            },
            {
                "category": "career_patterns",
                "filename": "success_factors.md",
                "title": f"{classification['profession']}の成功要因",
                "instruction": "この職種でトップクラスに到達するための要因、差別化ポイント、成長ステップをまとめてください。"
            },
        ]

        for task in tasks:
            try:
                category_data = by_category.get(task["category"], [])

                # Format raw data for LLM
                if category_data:
                    raw_text = "\n\n---\n\n".join([
                        f"**{d.get('title', '')}** ({d.get('url', '')})\n{d.get('content', '')}"
                        for d in category_data[:10]
                    ])
                    data_section = f"## 検索結果データ\n{raw_text}"
                else:
                    data_section = "（外部検索データなし — あなたの知識に基づいて生成してください）"

                content = self.llm.chat(
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "あなたはHR・キャリア分野の調査アナリストです。"
                                "提供されたデータ（ある場合）と自身の知識を組み合わせて、"
                                "構造化されたMarkdownドキュメントを生成してください。"
                                "具体的な数値・企業名・事例を含め、キャリアシミュレーションの参考資料として使えるようにしてください。"
                                "出力はMarkdown形式のみ（コードブロック不要）。"
                            )
                        },
                        {
                            "role": "user",
                            "content": f"""# {task['title']}

{task['instruction']}

## 候補者プロファイル
- 業界: {classification['industry']}
- 職種: {classification['profession']}
- スキル: {', '.join(classification.get('key_skills', []))}
- 経験レベル: {classification.get('experience_level', 'mid')}

{data_section}

上記を踏まえ、以下の構成でMarkdownドキュメントを生成してください:
1. 概要（2-3文）
2. 主要トピック別の詳細（各3-5箇条書き）
3. 数値データ（年収、求人数、成長率等 — 可能な限り具体的に）
4. 今後の展望（1-2年、3-5年）

最終更新: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
"""
                        }
                    ],
                    temperature=0.5,
                    max_tokens=4096
                )

                curated_files.append({
                    "category": task["category"],
                    "filename": task["filename"],
                    "title": task["title"],
                    "content": content
                })
            except Exception as e:
                logger.warning(f"LLM curation failed for task '{task['title']}', skipping: {e}")
                continue

        return curated_files

    def _save_knowledge_files(
        self,
        curated: List[Dict[str, str]],
        classification: Dict[str, Any]
    ) -> List[str]:
        """Save curated content to preset_knowledge/ and update meta index"""
        saved_paths = []

        for item in curated:
            category_dir = os.path.join(self.knowledge_dir, item["category"])
            os.makedirs(category_dir, exist_ok=True)

            filepath = os.path.join(category_dir, item["filename"])
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(item["content"])

            saved_paths.append(filepath)
            logger.info(f"Saved knowledge file: {filepath}")

        # Update meta index
        self._update_meta_index(curated, classification)

        return saved_paths

    def _update_meta_index(
        self,
        curated: List[Dict[str, str]],
        classification: Dict[str, Any]
    ) -> None:
        """Update _meta/index.json with file tags and timestamps"""
        meta_dir = os.path.join(self.knowledge_dir, "_meta")
        os.makedirs(meta_dir, exist_ok=True)
        index_path = os.path.join(meta_dir, "index.json")

        lock_path = index_path + ".lock"
        lock_fd = None
        try:
            lock_fd = open(lock_path, 'w')
            fcntl.flock(lock_fd, fcntl.LOCK_EX)

            # Load existing index
            if os.path.exists(index_path):
                with open(index_path, 'r', encoding='utf-8') as f:
                    index = json.load(f)
            else:
                index = {"files": {}, "last_updated": None}

            now = datetime.now(timezone.utc).isoformat()

            for item in curated:
                rel_path = f"{item['category']}/{item['filename']}"
                index["files"][rel_path] = {
                    "title": item["title"],
                    "category": item["category"],
                    "industry_key": classification.get("industry_key", "general"),
                    "profession_key": classification.get("profession_key", "unknown"),
                    "tags": [
                        classification.get("industry", ""),
                        classification.get("profession", ""),
                    ] + classification.get("key_skills", [])[:3],
                    "updated_at": now
                }

            index["last_updated"] = now

            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index, f, ensure_ascii=False, indent=2)
        finally:
            if lock_fd:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
                lock_fd.close()

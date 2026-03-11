"""
Knowledge Loader - Reads preset_knowledge/ files and returns relevant knowledge
for prompt injection at different injection points
"""

import json
import os
import hashlib
from typing import Dict, List, Optional

from ..config import Config
from ..utils.llm_client import LLMClient
from ..utils.logger import get_logger

logger = get_logger('mirofish.knowledge')


class KnowledgeLoader:
    """Loads and matches preset industry knowledge for prompt injection"""

    KNOWLEDGE_DIR = Config.KNOWLEDGE_DIR

    # In-memory cache: {filepath: (mtime, content)}
    _file_cache: Dict[str, tuple] = {}

    # Classification cache: {context_hash: classification_result}
    _classification_cache: Dict[str, Dict] = {}

    # Maximum cache entries
    _MAX_CACHE_SIZE = 100

    # Injection point → category priority and max chars
    INJECTION_CONFIG = {
        "top_player": {
            "categories": ["industries", "job_market"],
            "preferred_files": ["skill_demand.md", "salary_benchmarks.md"],
            "max_chars": 3000
        },
        "target_company": {
            "categories": ["job_market", "industries"],
            "preferred_files": ["salary_benchmarks.md", "hiring_trends.md"],
            "max_chars": 3000
        },
        "hr_specialist": {
            "categories": ["job_market", "career_patterns"],
            "preferred_files": ["hiring_trends.md", "common_transitions.md"],
            "max_chars": 2000
        },
        "group_persona": {
            "categories": ["industries", "career_patterns"],
            "preferred_files": ["success_factors.md"],
            "max_chars": 1500
        },
    }

    @classmethod
    def get_relevant_knowledge(
        cls,
        candidate_context: str,
        injection_point: str,
        max_chars: Optional[int] = None
    ) -> str:
        """Get relevant knowledge for a specific injection point

        Args:
            candidate_context: Candidate document text
            injection_point: One of "top_player", "target_company", "hr_specialist", "group_persona"
            max_chars: Override max chars (default from INJECTION_CONFIG)

        Returns:
            Formatted knowledge text for prompt injection, or empty string if no knowledge available
        """
        if not os.path.isdir(cls.KNOWLEDGE_DIR):
            return ""

        config = cls.INJECTION_CONFIG.get(injection_point, {
            "categories": ["industries", "job_market", "career_patterns"],
            "preferred_files": [],
            "max_chars": 2000
        })

        if max_chars is None:
            max_chars = min(config["max_chars"], Config.KNOWLEDGE_MAX_INJECTION_CHARS)

        # Try to match files via meta index
        matched_files = cls._match_files_from_index(candidate_context, config)

        if not matched_files:
            # Fallback: scan directories based on category priority
            matched_files = cls._scan_category_files(config)

        if not matched_files:
            return ""

        # Collect content from matched files up to max_chars
        parts = []
        total_chars = 0

        for filepath in matched_files:
            content = cls._read_file_cached(filepath)
            if not content:
                continue

            remaining = max_chars - total_chars
            if remaining <= 0:
                break

            if len(content) > remaining:
                content = content[:remaining] + "\n...(省略)"

            parts.append(content)
            total_chars += len(content)

        if not parts:
            return ""

        return "\n\n---\n\n".join(parts)

    @classmethod
    def search_knowledge(cls, query: str, category: str = "all") -> str:
        """Free-text search across knowledge files (for Report Agent)

        Args:
            query: Search query
            category: "industries", "job_market", "career_patterns", or "all"

        Returns:
            Matching knowledge text
        """
        if not os.path.isdir(cls.KNOWLEDGE_DIR):
            return "プリセット知識が見つかりません。/api/knowledge/curate を実行して知識をキュレーションしてください。"

        # Collect all relevant files
        categories = [category] if category != "all" else ["industries", "job_market", "career_patterns"]
        all_content = []

        for cat in categories:
            cat_dir = os.path.join(cls.KNOWLEDGE_DIR, cat)
            if not os.path.isdir(cat_dir):
                continue
            for fname in sorted(os.listdir(cat_dir)):
                if fname.endswith('.md'):
                    filepath = os.path.join(cat_dir, fname)
                    content = cls._read_file_cached(filepath)
                    if content and cls._text_matches_query(content, query):
                        all_content.append(f"### [{cat}/{fname}]\n{content}")

        if not all_content:
            # Fallback: try filename-based matching
            query_lower = query.lower()
            for cat in categories:
                cat_dir = os.path.join(cls.KNOWLEDGE_DIR, cat)
                if not os.path.isdir(cat_dir):
                    continue
                for fname in sorted(os.listdir(cat_dir)):
                    if fname.endswith('.md'):
                        fname_lower = fname.lower().replace('.md', '').replace('_', ' ')
                        if any(kw in fname_lower for kw in query_lower.split()):
                            filepath = os.path.join(cat_dir, fname)
                            content = cls._read_file_cached(filepath)
                            if content:
                                all_content.append(f"### [{cat}/{fname}]\n{content[:1000]}")

        if not all_content:
            return "クエリに一致するプリセット知識が見つかりませんでした。"

        result = "\n\n---\n\n".join(all_content)
        # Truncate to reasonable size for report agent
        if len(result) > 5000:
            result = result[:5000] + "\n...(省略)"
        return result

    @classmethod
    def classify_candidate_industry(cls, candidate_context: str) -> Dict:
        """Classify candidate's industry/profession using LLM (cached)"""
        context_hash = hashlib.sha256(candidate_context[:500].encode()).hexdigest()

        if context_hash in cls._classification_cache:
            return cls._classification_cache[context_hash]

        try:
            llm = LLMClient(use_chat_model=True)
            result = llm.chat_json(
                messages=[
                    {
                        "role": "system",
                        "content": "候補者情報から業界と職種を分類してください。純粋なJSON形式で返してください。"
                    },
                    {
                        "role": "user",
                        "content": f"""候補者コンテキスト（先頭500文字）:
{candidate_context[:500]}

JSON形式:
{{"industry_key": "英字スネークケース", "profession_key": "英字スネークケース"}}"""
                    }
                ],
                temperature=0.3,
                max_tokens=256
            )
            # Evict oldest entries if cache is full
            if len(cls._classification_cache) >= cls._MAX_CACHE_SIZE:
                oldest_key = next(iter(cls._classification_cache))
                del cls._classification_cache[oldest_key]
            cls._classification_cache[context_hash] = result
            return result
        except Exception as e:
            logger.warning(f"Candidate classification failed: {e}")
            return {"industry_key": "general", "profession_key": "unknown"}

    @classmethod
    def _match_files_from_index(cls, candidate_context: str, config: Dict) -> List[str]:
        """Match files using _meta/index.json tags"""
        index_path = os.path.join(cls.KNOWLEDGE_DIR, "_meta", "index.json")
        if not os.path.exists(index_path):
            return []

        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                index = json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

        files_meta = index.get("files", {})
        if not files_meta:
            return []

        # Score files by category match and preferred files
        scored = []
        for rel_path, meta in files_meta.items():
            score = 0
            category = meta.get("category", "")

            # Category match
            if category in config.get("categories", []):
                score += 10
                # Higher score for primary category
                if config["categories"] and category == config["categories"][0]:
                    score += 5

            # Preferred file match
            filename = os.path.basename(rel_path)
            if filename in config.get("preferred_files", []):
                score += 8

            if score > 0:
                full_path = os.path.join(cls.KNOWLEDGE_DIR, rel_path)
                if os.path.exists(full_path):
                    scored.append((score, full_path))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        return [path for _, path in scored]

    @classmethod
    def _scan_category_files(cls, config: Dict) -> List[str]:
        """Fallback: scan directories for files based on category priority"""
        preferred = []
        others = []
        preferred_names = set(config.get("preferred_files", []))
        for cat in config.get("categories", []):
            cat_dir = os.path.join(cls.KNOWLEDGE_DIR, cat)
            if not os.path.isdir(cat_dir):
                continue
            for fname in sorted(os.listdir(cat_dir)):
                if fname.endswith('.md'):
                    filepath = os.path.join(cat_dir, fname)
                    if fname in preferred_names:
                        preferred.append(filepath)
                    else:
                        others.append(filepath)
        return preferred + others

    @classmethod
    def _read_file_cached(cls, filepath: str) -> str:
        """Read file with mtime-based cache"""
        try:
            mtime = os.path.getmtime(filepath)
            cached = cls._file_cache.get(filepath)
            if cached and cached[0] == mtime:
                return cached[1]

            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Evict oldest entries if cache is full
            if len(cls._file_cache) >= cls._MAX_CACHE_SIZE:
                oldest_key = next(iter(cls._file_cache))
                del cls._file_cache[oldest_key]
            cls._file_cache[filepath] = (mtime, content)
            return content
        except (IOError, OSError) as e:
            logger.warning(f"Failed to read knowledge file {filepath}: {e}")
            return ""

    @classmethod
    def get_status(cls) -> Dict:
        """Get status of curated knowledge files"""
        if not os.path.isdir(cls.KNOWLEDGE_DIR):
            return {"available": False, "files_count": 0, "categories": {}}

        index_path = os.path.join(cls.KNOWLEDGE_DIR, "_meta", "index.json")
        last_updated = None
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    index = json.load(f)
                last_updated = index.get("last_updated")
            except (json.JSONDecodeError, IOError):
                pass

        categories = {}
        for cat in ["industries", "job_market", "career_patterns"]:
            cat_dir = os.path.join(cls.KNOWLEDGE_DIR, cat)
            if os.path.isdir(cat_dir):
                files = [f for f in os.listdir(cat_dir) if f.endswith('.md')]
                categories[cat] = files

        total = sum(len(v) for v in categories.values())
        return {
            "available": total > 0,
            "files_count": total,
            "categories": categories,
            "last_updated": last_updated
        }

    @classmethod
    def clear_cache(cls) -> None:
        """Clear all in-memory caches"""
        cls._file_cache.clear()
        cls._classification_cache.clear()
        logger.info("Knowledge loader caches cleared")

    @staticmethod
    def _text_matches_query(text: str, query: str) -> bool:
        """Simple keyword matching for search"""
        text_lower = text.lower()
        keywords = query.lower().split()
        # Match if at least half of keywords found
        matches = sum(1 for kw in keywords if kw in text_lower)
        return matches >= max(1, len(keywords) // 2)

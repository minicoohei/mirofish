#!/usr/bin/env python3
"""Generate 10 sample session directories for MiroFish."""
import json
import os
from pathlib import Path

BASE = Path(__file__).parent

PERSONAS = [
    {
        "id": "session_01",
        "name": "佐藤美咲", "age": 28, "gender": "female",
        "education": "慶應義塾大学 経済学部",
        "mbti": "ENTJ",
        "traits": ["論理的思考力", "プレゼンテーション力", "英語力", "分析力"],
        "certifications": ["TOEIC 950", "簿記2級"],
        "career_summary": "新卒で外資系戦略コンサルティングファーム入社。3年間でヘルスケア・金融・テクノロジー業界のプロジェクトを担当。現在はマネージャーとしてDX案件をリード。スタートアップへの転職を検討中。",
        "current_role": "マネージャー",
        "current_employer": "マッキンゼー・アンド・カンパニー",
        "industry": "経営コンサルティング",
        "years_in_role": 2,
        "salary": 900,
        "skills": ["戦略立案", "業務改善", "データ分析", "プロジェクトマネジメント", "英語ビジネス"],
        "family_members": [],
        "marital_status": "single",
        "mortgage_remaining": 0,
        "monthly_expenses": 25,
        "cash_buffer_range": "500-1000",
        "paths": [
            {"label": "スタートアップCOO転身", "direction": "startup", "risk": "事業失敗→年収500万で再就職", "upside": "IPO成功→ストックオプション含め年収5000万", "score": 0.75, "probability": 0.30,
             "prob_rationale": "コンサル出身のスタートアップCOOは採用ニーズ高い。ただしIPO到達は低確率。",
             "branch_point": "30歳時点でスタートアップの成長フェーズが分岐点",
             "best": {"label": "IPO成功→経営幹部", "prob": 0.10, "income": 5000, "sat": 0.90, "stress": 0.55, "wlb": 0.50},
             "likely": {"label": "シリーズB到達→年商10億企業のCOO", "prob": 0.55, "income": 1500, "sat": 0.82, "stress": 0.60, "wlb": 0.45},
             "base": {"label": "事業ピボット失敗→コンサル復帰", "prob": 0.35, "income": 1000, "sat": 0.55, "stress": 0.40, "wlb": 0.65}},
            {"label": "外資コンサル昇進（パートナー目指す）", "direction": "corporate", "risk": "アップオアアウトで退職→事業会社転職", "upside": "パートナー昇進→年収5000万超", "score": 0.70, "probability": 0.25,
             "prob_rationale": "女性パートナーは増加傾向だが昇進率は依然10%以下。",
             "branch_point": "32歳でのシニアマネージャー昇進が鍵",
             "best": {"label": "パートナー昇進", "prob": 0.08, "income": 5500, "sat": 0.85, "stress": 0.75, "wlb": 0.30},
             "likely": {"label": "シニアマネージャーで安定", "prob": 0.50, "income": 1800, "sat": 0.70, "stress": 0.70, "wlb": 0.35},
             "base": {"label": "アップオアアウト→事業会社", "prob": 0.42, "income": 1200, "sat": 0.60, "stress": 0.45, "wlb": 0.55}},
            {"label": "事業会社の経営企画・DX推進", "direction": "corporate", "risk": "大企業の意思決定の遅さにフラストレーション", "upside": "CDO/CSOとして経営ボードメンバー", "score": 0.68, "probability": 0.20,
             "prob_rationale": "DX人材需要は高いが経営ボード入りは時間がかかる。",
             "branch_point": "33歳での部長昇格が分岐点",
             "best": {"label": "CDO就任→経営改革リード", "prob": 0.12, "income": 2500, "sat": 0.80, "stress": 0.50, "wlb": 0.55},
             "likely": {"label": "経営企画部長として安定", "prob": 0.55, "income": 1400, "sat": 0.72, "stress": 0.45, "wlb": 0.60},
             "base": {"label": "組織政治に疲弊→再転職", "prob": 0.33, "income": 1100, "sat": 0.50, "stress": 0.55, "wlb": 0.50}},
            {"label": "独立コンサルタント・フリーランス", "direction": "freelance", "risk": "案件獲得不安定→貯蓄切り崩し", "upside": "自由な働き方×高単価で年収1500万", "score": 0.60, "probability": 0.15,
             "prob_rationale": "マッキンゼーブランドで案件獲得は容易だが安定性に欠ける。",
             "branch_point": "31歳でのクライアント基盤構築が鍵",
             "best": {"label": "高単価コンサル×複数顧問で年収2000万", "prob": 0.15, "income": 2000, "sat": 0.85, "stress": 0.35, "wlb": 0.75},
             "likely": {"label": "月100-150万で安定稼働", "prob": 0.50, "income": 1300, "sat": 0.75, "stress": 0.40, "wlb": 0.70},
             "base": {"label": "案件途切れ→正社員復帰", "prob": 0.35, "income": 900, "sat": 0.50, "stress": 0.50, "wlb": 0.55}},
            {"label": "MBA留学→海外キャリア", "direction": "global", "risk": "留学費用2000万＋機会損失", "upside": "グローバル企業幹部→年収3000万超", "score": 0.65, "probability": 0.10,
             "prob_rationale": "MBA後のROIは不確実。海外就労ビザ取得も課題。",
             "branch_point": "30歳でのMBA合格が最初の関門",
             "best": {"label": "海外テック企業の戦略部門VP", "prob": 0.10, "income": 3500, "sat": 0.88, "stress": 0.50, "wlb": 0.55},
             "likely": {"label": "MBA後日本の外資系に復帰", "prob": 0.55, "income": 1600, "sat": 0.70, "stress": 0.55, "wlb": 0.50},
             "base": {"label": "MBA費用回収に時間→当面年収横ばい", "prob": 0.35, "income": 1000, "sat": 0.55, "stress": 0.50, "wlb": 0.50}}
        ],
        "agents": [
            {"agent_id": "agent_consul_senior", "name": "木村拓哉", "bio": "マッキンゼーのシニアパートナー。美咲の直属上司。", "stance": "opposing", "role": "コンサルシニアパートナー", "category": "business_strategy"},
            {"agent_id": "agent_startup_ceo", "name": "山口翔太", "bio": "SaaS系スタートアップCEO。美咲をCOOとしてスカウト中。", "stance": "supportive", "role": "スタートアップCEO", "category": "tech_industry"},
            {"agent_id": "agent_univ_friend", "name": "田村麻衣", "bio": "慶應同期。総合商社勤務。安定志向。", "stance": "neutral", "role": "大学時代の友人", "category": "private"},
            {"agent_id": "agent_father", "name": "佐藤健一", "bio": "父親。大手メーカー勤務。娘の転職を心配。", "stance": "opposing", "role": "父親", "category": "private"},
            {"agent_id": "agent_career_coach", "name": "鈴木裕子", "bio": "キャリアコーチ。外資系出身女性のキャリア支援専門。", "stance": "neutral", "role": "キャリアコーチ", "category": "hr_career"},
            {"agent_id": "copy_agent_ambitious", "name": "挑戦的な自分", "bio": "リスクを取ってでも成長を求める自分。", "stance": "supportive", "role": "copy_agent", "category": "copy_agent"}
        ],
        "fact_checks": [
            {"claim_id": "FC-001", "location": "path_a > probability", "original_value": "30%", "status": "verified", "verified_value": "25-35%", "note": "コンサル出身COOの採用トレンドと整合"},
            {"claim_id": "FC-002", "location": "path_b > パートナー昇進率", "original_value": "10%以下", "status": "verified", "verified_value": "8-12%", "note": "McKinsey Global Report 2024のデータと一致"},
            {"claim_id": "FC-003", "location": "path_e > MBA費用", "original_value": "2000万", "status": "adjusted", "verified_value": "2500-3000万", "note": "Top10 MBAの学費+生活費は近年高騰。2026年時点では2500万以上が現実的"}
        ],
        "trends": [
            {"trend_id": "consulting_disruption", "label": "コンサル業界のAI置換リスク", "category": "technology", "description": "McKinsey/BCGもAIツール導入。ジュニアアナリストの業務がAI化。", "probability": 0.80, "timeframe": "2026-2030"},
            {"trend_id": "female_leadership", "label": "女性リーダー登用の加速", "category": "workforce", "description": "ESG/DE&I圧力で女性経営幹部需要増。", "probability": 0.75, "timeframe": "2026-2035"},
            {"trend_id": "startup_ecosystem", "label": "日本スタートアップエコシステム成熟", "category": "finance", "description": "5か年計画の効果。スタートアップ転職の社会的受容度上昇。", "probability": 0.70, "timeframe": "2026-2030"}
        ],
        "salary_benchmarks": [
            {"role": "外資コンサル マネージャー", "range": "800-1200万円", "source": "OpenWork 2024"},
            {"role": "スタートアップCOO（シリーズA-B）", "range": "800-1500万円", "source": "INITIAL 2024"},
            {"role": "外資コンサル パートナー", "range": "3000-8000万円", "source": "Glassdoor 2024"}
        ]
    },
    {
        "id": "session_02",
        "name": "田中健一", "age": 42, "gender": "male",
        "education": "一橋大学 商学部",
        "mbti": "ISTJ",
        "traits": ["リスク管理", "組織マネジメント", "財務分析", "ステークホルダー調整"],
        "certifications": ["証券アナリスト", "FP1級"],
        "career_summary": "新卒でメガバンク入行。法人営業→海外駐在（ロンドン3年）→本部企画→現在は事業部長として中堅企業向け融資部門を統括。部下80名。",
        "current_role": "事業部長",
        "current_employer": "三菱UFJ銀行",
        "industry": "金融 / メガバンク",
        "years_in_role": 3,
        "salary": 1400,
        "skills": ["法人営業", "与信審査", "リスク管理", "部門経営", "海外業務", "M&Aファイナンス"],
        "family_members": [{"relation": "妻", "age": 40}, {"relation": "長男", "age": 12}, {"relation": "長女", "age": 9}],
        "marital_status": "married",
        "mortgage_remaining": 4000,
        "monthly_expenses": 55,
        "cash_buffer_range": "1000-2000",
        "paths": [
            {"label": "メガバンク残留→執行役員目指す", "direction": "corporate", "risk": "50代で出向→関連会社社長", "upside": "執行役員→年収3000万超", "score": 0.72, "probability": 0.35,
             "prob_rationale": "部長→執行役員の昇進率は5-10%。ロンドン駐在経験はプラス。",
             "branch_point": "45歳での常務補佐ポスト獲得が鍵",
             "best": {"label": "執行役員就任", "prob": 0.08, "income": 3500, "sat": 0.80, "stress": 0.65, "wlb": 0.35},
             "likely": {"label": "部長職で定年まで→関連会社社長", "prob": 0.55, "income": 1600, "sat": 0.65, "stress": 0.50, "wlb": 0.50},
             "base": {"label": "出向→年収ダウン", "prob": 0.37, "income": 1100, "sat": 0.45, "stress": 0.40, "wlb": 0.60}},
            {"label": "フィンテック企業のCFO/COO", "direction": "startup", "risk": "年収一時ダウン＋住宅ローンリスク", "upside": "IPO→ストックオプション行使で資産形成", "score": 0.68, "probability": 0.25,
             "prob_rationale": "メガバンク出身のフィンテック幹部は需要あり。ただし文化適応がハードル。",
             "branch_point": "44歳での転職決断タイミングが分岐点",
             "best": {"label": "フィンテックIPO→CFO", "prob": 0.12, "income": 4000, "sat": 0.85, "stress": 0.60, "wlb": 0.40},
             "likely": {"label": "フィンテックCFOとして安定", "prob": 0.50, "income": 1800, "sat": 0.75, "stress": 0.55, "wlb": 0.45},
             "base": {"label": "カルチャーフィットせず1年で退職", "prob": 0.38, "income": 1200, "sat": 0.40, "stress": 0.65, "wlb": 0.45}},
            {"label": "地方銀行の頭取候補として転職", "direction": "corporate", "risk": "地方移住の家族負担", "upside": "地方銀行頭取→地域経済のリーダー", "score": 0.62, "probability": 0.15,
             "prob_rationale": "メガバンク出身の地銀トップは増加傾向だが家族の同意が必要。",
             "branch_point": "46歳での地銀からのオファー受諾が分岐点",
             "best": {"label": "地銀頭取就任→地域再生リーダー", "prob": 0.15, "income": 2500, "sat": 0.82, "stress": 0.50, "wlb": 0.55},
             "likely": {"label": "地銀副頭取として安定", "prob": 0.50, "income": 1800, "sat": 0.70, "stress": 0.45, "wlb": 0.55},
             "base": {"label": "地方生活に家族が適応できず単身赴任", "prob": 0.35, "income": 1500, "sat": 0.50, "stress": 0.55, "wlb": 0.35}},
            {"label": "PEファンド・投資会社転職", "direction": "finance", "risk": "成果報酬型で収入変動大", "upside": "キャリーで数億円の資産形成", "score": 0.65, "probability": 0.15,
             "prob_rationale": "メガバンクの与信・M&A経験はPE業界で評価されるが、42歳からの転身はハードル高い。",
             "branch_point": "43歳でのPEファンド採用面接突破が最初の関門",
             "best": {"label": "PEパートナー昇進→キャリー獲得", "prob": 0.08, "income": 5000, "sat": 0.85, "stress": 0.70, "wlb": 0.30},
             "likely": {"label": "PEディレクターとして投資実行", "prob": 0.50, "income": 2200, "sat": 0.75, "stress": 0.65, "wlb": 0.35},
             "base": {"label": "PE業界に馴染めず→事業会社CFO", "prob": 0.42, "income": 1500, "sat": 0.55, "stress": 0.50, "wlb": 0.50}},
            {"label": "独立系M&Aアドバイザリー設立", "direction": "entrepreneurship", "risk": "案件獲得にメガバンク人脈依存", "upside": "成功報酬型で年収3000万超", "score": 0.58, "probability": 0.10,
             "prob_rationale": "中小企業M&A市場は拡大中だが、42歳での独立はリスクが高い。住宅ローン4000万が重荷。",
             "branch_point": "45歳で最初の大型案件クローズが分岐点",
             "best": {"label": "M&Aブティック成功→年間10案件", "prob": 0.10, "income": 4000, "sat": 0.88, "stress": 0.55, "wlb": 0.50},
             "likely": {"label": "年間3-5案件で堅実運営", "prob": 0.45, "income": 2000, "sat": 0.72, "stress": 0.50, "wlb": 0.55},
             "base": {"label": "案件獲得に苦戦→メガバンク復帰", "prob": 0.45, "income": 1300, "sat": 0.40, "stress": 0.60, "wlb": 0.45}}
        ],
        "agents": [
            {"agent_id": "agent_bank_boss", "name": "鉄田雅彦", "bio": "メガバンク常務。田中の上司。出世を期待。", "stance": "opposing", "role": "上司（常務）", "category": "business_strategy"},
            {"agent_id": "agent_fintech_ceo", "name": "河野太一", "bio": "フィンテックスタートアップCEO。田中をCFOとして勧誘中。", "stance": "supportive", "role": "フィンテックCEO", "category": "tech_industry"},
            {"agent_id": "agent_wife", "name": "田中恵子", "bio": "妻。子供の教育と住宅ローンを心配。安定重視。", "stance": "opposing", "role": "妻", "category": "private"},
            {"agent_id": "agent_bank_peer", "name": "佐々木洋介", "bio": "メガバンク同期。既に独立してFAを運営。", "stance": "supportive", "role": "同期の友人", "category": "private"},
            {"agent_id": "agent_fp", "name": "山下真理", "bio": "FP。家計とローン返済計画のアドバイザー。", "stance": "neutral", "role": "ファイナンシャルプランナー", "category": "hr_career"},
            {"agent_id": "copy_agent_cautious", "name": "慎重な自分", "bio": "家族のことを最優先に考える自分。", "stance": "opposing", "role": "copy_agent", "category": "copy_agent"}
        ],
        "fact_checks": [
            {"claim_id": "FC-001", "location": "path_a > 執行役員昇進率", "original_value": "5-10%", "status": "verified", "verified_value": "5-8%", "note": "三菱UFJ銀行の有価証券報告書データと整合"},
            {"claim_id": "FC-002", "location": "path_b > フィンテックIPO", "original_value": "12%", "status": "adjusted", "verified_value": "8-10%", "note": "日本のフィンテックIPO率は米国より低い"},
            {"claim_id": "FC-003", "location": "path_e > 中小企業M&A市場", "original_value": "拡大中", "status": "verified", "verified_value": "CAGR 15-20%", "note": "M&Aクラウド2024レポートで確認"}
        ],
        "trends": [
            {"trend_id": "banking_digital", "label": "メガバンクのDX・支店削減", "category": "technology", "description": "AI・フィンテックによる銀行業務の構造変化。支店数は2030年までに30%減少見込み。", "probability": 0.90, "timeframe": "2026-2032"},
            {"trend_id": "interest_rate", "label": "日銀利上げと金融環境変化", "category": "finance", "description": "マイナス金利解除後の金利正常化で銀行収益構造が変化。", "probability": 0.75, "timeframe": "2026-2028"},
            {"trend_id": "sme_succession", "label": "中小企業の事業承継問題", "category": "demographics", "description": "後継者不在率65%。M&A市場は急拡大。", "probability": 0.95, "timeframe": "2026-2035"}
        ],
        "salary_benchmarks": [
            {"role": "メガバンク事業部長", "range": "1300-1600万円", "source": "OpenWork 2024"},
            {"role": "フィンテックCFO", "range": "1500-2500万円", "source": "ビズリーチ 2024"},
            {"role": "PEファンドディレクター", "range": "2000-4000万円", "source": "Glassdoor 2024"}
        ]
    },
    {
        "id": "session_03",
        "name": "李明華", "age": 31, "gender": "female",
        "education": "清華大学 コンピュータサイエンス学部 / Stanford大学 MS CS",
        "mbti": "INTP",
        "traits": ["技術力", "英語・中国語・日本語トリリンガル", "論理的思考", "グローバル視点"],
        "certifications": [],
        "career_summary": "清華大学CS卒業後Stanford MSに進学。卒業後Google本社SWEとして3年勤務後、Google Japan転籍。現在はGoogle JapanのSenior SWE（L5）としてSearch Qualityチームに所属。",
        "current_role": "Senior Software Engineer (L5)",
        "current_employer": "Google Japan",
        "industry": "テクノロジー / GAFA",
        "years_in_role": 2,
        "salary": 1800,
        "skills": ["機械学習", "大規模システム設計", "Python", "C++", "Go", "分散システム", "NLP"],
        "family_members": [],
        "marital_status": "single",
        "mortgage_remaining": 0,
        "monthly_expenses": 30,
        "cash_buffer_range": "2000以上",
        "paths": [
            {"label": "Google社内昇進（Staff Engineer→Principal）", "direction": "corporate", "risk": "昇進競争の激しさ・政治的スキル不足", "upside": "Principal Engineer→年収5000万超", "score": 0.75, "probability": 0.30,
             "prob_rationale": "L5→L6は比較的一般的だがL6→L7(Staff)は10-15%。",
             "branch_point": "33歳でのL6昇進がまず必要",
             "best": {"label": "Principal Engineer(L8)到達", "prob": 0.05, "income": 6000, "sat": 0.88, "stress": 0.55, "wlb": 0.50},
             "likely": {"label": "Staff Engineer(L6-7)で安定", "prob": 0.55, "income": 3000, "sat": 0.75, "stress": 0.50, "wlb": 0.55},
             "base": {"label": "L5-6で停滞→転職", "prob": 0.40, "income": 2200, "sat": 0.55, "stress": 0.45, "wlb": 0.60}},
            {"label": "AIスタートアップ共同創業（CTO）", "direction": "startup", "risk": "収入ゼロ期間＋ビザ問題", "upside": "ユニコーン創出→億万長者", "score": 0.70, "probability": 0.20,
             "prob_rationale": "技術力は十分だがビジネス面のパートナーが必要。ビザの制約あり。",
             "branch_point": "32歳での起業決断と共同創業者との出会い",
             "best": {"label": "ユニコーン達成→CTO", "prob": 0.05, "income": 8000, "sat": 0.92, "stress": 0.65, "wlb": 0.35},
             "likely": {"label": "シリーズA到達→堅実成長", "prob": 0.45, "income": 1500, "sat": 0.80, "stress": 0.70, "wlb": 0.35},
             "base": {"label": "起業失敗→GAFA復帰", "prob": 0.50, "income": 2000, "sat": 0.50, "stress": 0.50, "wlb": 0.55}},
            {"label": "米国本社への転籍（Mountain View）", "direction": "global", "risk": "競争激化・文化適応", "upside": "米国報酬水準で年収4000万超", "score": 0.72, "probability": 0.25,
             "prob_rationale": "社内転籍は外部採用より容易。L5実力があれば承認される可能性高い。",
             "branch_point": "32歳での転籍申請承認が分岐点",
             "best": {"label": "米国で Staff→Director昇進", "prob": 0.10, "income": 7000, "sat": 0.85, "stress": 0.55, "wlb": 0.50},
             "likely": {"label": "米国L6で安定・高報酬", "prob": 0.55, "income": 4000, "sat": 0.78, "stress": 0.50, "wlb": 0.50},
             "base": {"label": "米国生活に適応できず日本復帰", "prob": 0.35, "income": 2500, "sat": 0.55, "stress": 0.50, "wlb": 0.55}},
            {"label": "中国テック企業（ByteDance/Alibaba）でAI責任者", "direction": "global", "risk": "地政学リスク・規制リスク", "upside": "中国AI市場のリーダーポジション", "score": 0.55, "probability": 0.15,
             "prob_rationale": "清華大学人脈で門戸は開かれているが、米中デカップリングのリスク大。",
             "branch_point": "33歳での中国帰国決断",
             "best": {"label": "ByteDance AI部門VP", "prob": 0.10, "income": 5000, "sat": 0.80, "stress": 0.60, "wlb": 0.40},
             "likely": {"label": "中国テック企業のシニアエンジニア", "prob": 0.50, "income": 2500, "sat": 0.65, "stress": 0.55, "wlb": 0.45},
             "base": {"label": "米中関係悪化でキャリアリスク顕在化", "prob": 0.40, "income": 1800, "sat": 0.40, "stress": 0.65, "wlb": 0.40}},
            {"label": "大学研究者（AI/ML）に転身", "direction": "academic", "risk": "大幅年収ダウン", "upside": "研究成果による社会的インパクト", "score": 0.50, "probability": 0.10,
             "prob_rationale": "Stanford MSでは研究ポジション獲得にPhDが必要な場合が多い。",
             "branch_point": "33歳でのPhD入学決断",
             "best": {"label": "トップ大学のテニュア教授", "prob": 0.08, "income": 1500, "sat": 0.90, "stress": 0.40, "wlb": 0.65},
             "likely": {"label": "准教授 or 研究員として論文執筆", "prob": 0.50, "income": 800, "sat": 0.75, "stress": 0.45, "wlb": 0.60},
             "base": {"label": "アカデミアの競争に疲弊→企業復帰", "prob": 0.42, "income": 2000, "sat": 0.50, "stress": 0.50, "wlb": 0.55}}
        ],
        "agents": [
            {"agent_id": "agent_google_mgr", "name": "David Chen", "bio": "Google Japanのマネージャー。明華の昇進を支援。", "stance": "supportive", "role": "マネージャー", "category": "tech_industry"},
            {"agent_id": "agent_stanford_friend", "name": "Emily Zhang", "bio": "Stanford同期。米国でAIスタートアップを創業。", "stance": "supportive", "role": "大学同期", "category": "tech_industry"},
            {"agent_id": "agent_tsinghua_prof", "name": "王教授", "bio": "清華大学の恩師。学術キャリアを勧める。", "stance": "neutral", "role": "大学恩師", "category": "hr_career"},
            {"agent_id": "agent_mother_china", "name": "李母", "bio": "中国在住の母親。娘の中国帰国を希望。", "stance": "neutral", "role": "母親", "category": "private"},
            {"agent_id": "agent_recruiter", "name": "田口誠", "bio": "外資系ITリクルーター。ByteDanceのポジションを紹介。", "stance": "neutral", "role": "リクルーター", "category": "hr_career"},
            {"agent_id": "copy_agent_data_driven", "name": "分析的な自分", "bio": "データと確率で最適解を求める自分。", "stance": "neutral", "role": "copy_agent", "category": "copy_agent"}
        ],
        "fact_checks": [
            {"claim_id": "FC-001", "location": "path_a > L5→L6昇進率", "original_value": "比較的一般的", "status": "verified", "verified_value": "60-70%", "note": "Levels.fyi 2024データと整合"},
            {"claim_id": "FC-002", "location": "path_a > L6→L7昇進率", "original_value": "10-15%", "status": "verified", "verified_value": "10-15%", "note": "Levels.fyi/Blind 2024データと一致"},
            {"claim_id": "FC-003", "location": "path_c > 米国報酬", "original_value": "4000万超", "status": "verified", "verified_value": "L6: $300-400K TC", "note": "Levels.fyi 2024のGoogle L6 TC中央値と整合"}
        ],
        "trends": [
            {"trend_id": "ai_talent_war", "label": "グローバルAI人材争奪戦", "category": "workforce", "description": "OpenAI/Anthropic/Googleの人材獲得競争が過熱。AI SWEの報酬は年々上昇。", "probability": 0.90, "timeframe": "2026-2030"},
            {"trend_id": "us_china_decouple", "label": "米中AI技術デカップリング", "category": "geopolitics", "description": "AI半導体輸出規制強化。中国出身エンジニアへのセキュリティクリアランス制限。", "probability": 0.85, "timeframe": "2026-2035"},
            {"trend_id": "japan_ai_hub", "label": "日本のAI研究拠点化", "category": "technology", "description": "米中の中間地点として日本がAI研究ハブになる可能性。Google/MS/Metaが日本拠点拡大。", "probability": 0.60, "timeframe": "2027-2032"}
        ],
        "salary_benchmarks": [
            {"role": "Google Japan L5 SWE", "range": "1500-2200万円", "source": "Levels.fyi 2024"},
            {"role": "Google US L6 SWE", "range": "3500-5000万円", "source": "Levels.fyi 2024"},
            {"role": "AIスタートアップ CTO（シード-A）", "range": "600-1500万円", "source": "INITIAL 2024"}
        ]
    },
]

# Remaining 7 personas defined more compactly
PERSONAS_COMPACT = [
    # session_04: 鈴木大輔
    {
        "id": "session_04", "name": "鈴木大輔", "age": 55, "gender": "male",
        "education": "早稲田大学 理工学部", "mbti": "ESTJ",
        "traits": ["組織統率力", "製造業知識", "海外事業経験", "品質管理"],
        "certifications": ["技術士（機械）"],
        "career_summary": "大手自動車部品メーカーで33年勤務。製造→品質管理→海外事業（タイ駐在5年）→事業部長。早期退職を検討中。",
        "current_role": "事業部長", "current_employer": "デンソー", "industry": "自動車部品製造",
        "years_in_role": 5, "salary": 1600,
        "skills": ["製造プロセス改善", "品質管理", "海外工場管理", "サプライチェーン", "部門経営"],
        "family": [{"relation": "妻", "age": 53}], "marital_status": "married",
        "mortgage_remaining": 500, "monthly_expenses": 45, "cash_buffer_range": "3000以上",
        "path_labels": ["早期退職→中小製造業の社長", "65歳まで現職→退職金満額", "製造コンサル独立", "タイで日系工場支援事業", "社外取締役・顧問複数社"],
        "best_incomes": [3000, 2000, 2500, 2200, 1800],
        "likely_incomes": [1500, 1700, 1500, 1200, 1200],
        "base_incomes": [800, 1600, 800, 600, 800]
    },
    # session_05: 山田花子
    {
        "id": "session_05", "name": "山田花子", "age": 24, "gender": "female",
        "education": "武蔵野美術大学 デザイン情報学科", "mbti": "ENFP",
        "traits": ["デザイン思考", "UI/UXデザイン", "クリエイティビティ", "コミュニケーション力"],
        "certifications": [],
        "career_summary": "新卒でWeb系ベンチャーに入社。UI/UXデザイナーとしてアプリデザインを担当。入社2年目。",
        "current_role": "UI/UXデザイナー", "current_employer": "SmartApp株式会社", "industry": "Webサービス",
        "years_in_role": 2, "salary": 380,
        "skills": ["Figma", "UIデザイン", "UXリサーチ", "プロトタイピング", "グラフィックデザイン"],
        "family": [], "marital_status": "single",
        "mortgage_remaining": 0, "monthly_expenses": 18, "cash_buffer_range": "100-300",
        "path_labels": ["デザインリード→CDO目指す", "メガテック（Google/Apple）転職", "フリーランスデザイナー独立", "デザインスクール起業", "プロダクトマネージャー転身"],
        "best_incomes": [1500, 1800, 1200, 2000, 1500],
        "likely_incomes": [700, 1000, 600, 500, 800],
        "base_incomes": [450, 500, 350, 300, 500]
    },
    # session_06: 高橋勇太
    {
        "id": "session_06", "name": "高橋勇太", "age": 38, "gender": "male",
        "education": "東京工業大学 情報理工学院", "mbti": "ISTP",
        "traits": ["技術力", "自己管理能力", "問題解決力", "効率化志向"],
        "certifications": ["AWS Solutions Architect Professional", "GCP Professional Cloud Architect"],
        "career_summary": "SIer→Webサービス企業→34歳でフリーランスに。インフラ・バックエンドの技術顧問を複数社で並行。",
        "current_role": "フリーランスエンジニア", "current_employer": "個人事業主", "industry": "ITコンサルティング",
        "years_in_role": 4, "salary": 1200,
        "skills": ["AWS", "GCP", "Kubernetes", "Go", "Rust", "システム設計", "技術顧問"],
        "family": [{"relation": "妻", "age": 36}, {"relation": "長男", "age": 3}], "marital_status": "married",
        "mortgage_remaining": 3500, "monthly_expenses": 40, "cash_buffer_range": "1000-2000",
        "path_labels": ["フリーランス継続→技術顧問拡大", "自社プロダクト開発→SaaS起業", "CTO候補として正社員復帰", "技術研修・教育事業", "海外リモートワーク（東南アジア拠点）"],
        "best_incomes": [2500, 5000, 2800, 2000, 2000],
        "likely_incomes": [1400, 800, 1500, 1000, 1300],
        "base_incomes": [900, 300, 1200, 500, 800]
    },
    # session_07: 伊藤さくら
    {
        "id": "session_07", "name": "伊藤さくら", "age": 45, "gender": "female",
        "education": "東京大学 薬学部 / Wharton MBA", "mbti": "ENTJ",
        "traits": ["リーダーシップ", "ヘルスケア業界知識", "MBA", "グローバル経験"],
        "certifications": ["薬剤師"],
        "career_summary": "製薬会社MR→MBA留学→外資製薬マーケティング→医療系IT企業VP。ヘルスケア×ITのキャリア。離婚後シングルマザー。",
        "current_role": "Vice President", "current_employer": "メドレー", "industry": "医療系IT",
        "years_in_role": 3, "salary": 2000,
        "skills": ["ヘルスケア戦略", "マーケティング", "事業開発", "組織マネジメント", "英語"],
        "family": [{"relation": "長女", "age": 15}], "marital_status": "divorced",
        "mortgage_remaining": 2000, "monthly_expenses": 50, "cash_buffer_range": "2000以上",
        "path_labels": ["医療系IT企業のCEO/COO昇進", "外資製薬のCountry Manager", "ヘルスケアVC転身", "デジタルヘルス起業", "NPO設立（医療アクセス改善）"],
        "best_incomes": [4000, 5000, 3500, 6000, 1000],
        "likely_incomes": [2500, 3000, 2000, 1200, 500],
        "base_incomes": [2000, 2200, 1500, 500, 300]
    },
    # session_08: 渡辺修平
    {
        "id": "session_08", "name": "渡辺修平", "age": 33, "gender": "male",
        "education": "新潟大学 法学部", "mbti": "ISFJ",
        "traits": ["堅実性", "地域貢献意欲", "行政知識", "調整力"],
        "certifications": ["行政書士"],
        "career_summary": "地方公務員（新潟県庁）10年目。企画課→税務課→現在は産業振興課。地元へのUターン転職を検討中（現在は新潟市在住、実家は長岡市）。",
        "current_role": "主査", "current_employer": "新潟県庁", "industry": "地方行政",
        "years_in_role": 3, "salary": 520,
        "skills": ["行政計画策定", "予算管理", "地域振興", "条例起案", "住民対応"],
        "family": [{"relation": "妻", "age": 31}, {"relation": "長男", "age": 2}], "marital_status": "married",
        "mortgage_remaining": 2500, "monthly_expenses": 30, "cash_buffer_range": "300-500",
        "path_labels": ["公務員継続→管理職昇進", "地元長岡市役所へ転職", "地方創生コンサルタントへ転身", "地元で農業×IT起業", "民間企業（地方銀行等）へ転職"],
        "best_incomes": [800, 700, 1200, 1500, 1000],
        "likely_incomes": [650, 580, 700, 400, 700],
        "base_incomes": [550, 500, 400, 200, 550]
    },
    # session_09: 中村あゆみ
    {
        "id": "session_09", "name": "中村あゆみ", "age": 29, "gender": "female",
        "education": "青山学院大学 経営学部", "mbti": "ESFP",
        "traits": ["企画力", "トレンド感度", "SNSマーケティング", "マルチタスク"],
        "certifications": ["Google Analytics認定"],
        "career_summary": "大手広告代理店入社7年目。デジタル広告プランニング→SNSマーケティング専任。副業でYouTubeチャンネル運営（登録者8万人）。",
        "current_role": "プランナー", "current_employer": "博報堂", "industry": "広告代理店",
        "years_in_role": 3, "salary": 650,
        "skills": ["デジタルマーケティング", "SNS運用", "動画企画", "クライアントワーク", "データ分析"],
        "family": [], "marital_status": "single",
        "mortgage_remaining": 0, "monthly_expenses": 25, "cash_buffer_range": "300-500",
        "path_labels": ["広告代理店でクリエイティブディレクター", "YouTuber/インフルエンサー専業", "D2Cブランド起業", "マーケティングSaaS企業転職", "フリーランスマーケター"],
        "best_incomes": [1500, 3000, 2500, 1800, 1500],
        "likely_incomes": [900, 800, 600, 1000, 800],
        "base_incomes": [700, 300, 200, 700, 500]
    },
    # session_10: 小林誠
    {
        "id": "session_10", "name": "小林誠", "age": 50, "gender": "male",
        "education": "日本大学 経済学部", "mbti": "ESTP",
        "traits": ["経営判断力", "人脈構築力", "リスクテイク", "現場主義"],
        "certifications": [],
        "career_summary": "25歳で建設資材の商社を創業。年商30億円まで成長。社員80名。近年は事業承継を検討中。長男は別業界。",
        "current_role": "代表取締役社長", "current_employer": "小林商事株式会社", "industry": "建設資材商社",
        "years_in_role": 25, "salary": 3000,
        "skills": ["経営", "営業", "人材育成", "資金調達", "業界人脈"],
        "family": [{"relation": "妻", "age": 48}, {"relation": "長男", "age": 25}, {"relation": "次男", "age": 22}, {"relation": "長女", "age": 18}], "marital_status": "married",
        "mortgage_remaining": 0, "monthly_expenses": 80, "cash_buffer_range": "5000以上",
        "path_labels": ["長男への事業承継", "M&Aで事業売却→セミリタイア", "持株会社化→多角経営", "幹部社員への承継（MBO）", "経営者仲間と投資ファンド設立"],
        "best_incomes": [3500, 10000, 5000, 3000, 4000],
        "likely_incomes": [2500, 5000, 3000, 2500, 2500],
        "base_incomes": [1500, 3000, 2000, 2000, 1500]
    }
]


def build_profile(p):
    return {
        "name": p["name"], "age": p["age"], "gender": p["gender"],
        "education": p["education"], "mbti": p.get("mbti", ""),
        "traits": p["traits"], "certifications": p.get("certifications", []),
        "career_summary": p["career_summary"],
        "current_role": p["current_role"], "current_employer": p["current_employer"],
        "industry": p["industry"], "years_in_role": p["years_in_role"],
        "salary": p["salary"], "skills": p["skills"]
    }

def build_form(p):
    fm = p.get("family_members", p.get("family", []))
    return {
        "family_members": fm,
        "marital_status": p["marital_status"],
        "mortgage_remaining": p["mortgage_remaining"],
        "monthly_expenses": p["monthly_expenses"],
        "cash_buffer_range": p["cash_buffer_range"]
    }

def build_agent_state(p):
    fm = p.get("family_members", p.get("family", []))
    return {
        "identity": {
            "name": p["name"], "age_at_start": p["age"], "gender": p["gender"],
            "education": p["education"], "mbti": p.get("mbti", ""),
            "stable_traits": p["traits"], "certifications": p.get("certifications", []),
            "career_history_summary": p["career_summary"]
        },
        "state": {
            "current_round": 0, "current_age": p["age"],
            "role": p["current_role"], "employer": p["current_employer"],
            "industry": p["industry"], "years_in_role": p["years_in_role"],
            "salary_annual": p["salary"], "skills": p["skills"],
            "family": fm, "marital_status": p["marital_status"],
            "cash_buffer": 250, "mortgage_remaining": p["mortgage_remaining"],
            "monthly_expenses": p["monthly_expenses"],
            "stress_level": 0.3, "job_satisfaction": 0.5,
            "work_life_balance": 0.5, "blockers": [], "events_this_round": []
        },
        "seed": 42
    }


def make_period(period_name, events, income=0):
    return {
        "period_id": None, "period_name": period_name, "narrative": "",
        "snapshot": {"annual_income": income, "satisfaction": 0.5, "stress": 0.5, "work_life_balance": 0.5},
        "events": events
    }

def build_multipath_full(p):
    """Build multipath_result for full persona (session_01-03)."""
    data = {
        "identity": {
            "name": p["name"], "age_at_start": p["age"], "gender": p["gender"],
            "education": p["education"], "mbti": p.get("mbti", ""),
            "stable_traits": p["traits"], "certifications": p.get("certifications", []),
            "career_history_summary": p["career_summary"]
        },
        "simulation_years": 10.0, "total_rounds": 40,
        "paths": []
    }
    age = p["age"]
    for i, path in enumerate(p["paths"]):
        path_id = f"path_{chr(97+i)}"
        common_period = make_period(
            f"Period 1 ({age+2}-{age+4}歳)",
            [{"type": "キャリア検討", "description": f"{path['label']}に向けた準備期間", "probability": 0.7, "probability_note": "検討段階の実行確率"}]
        )
        def make_scenario(sc_key):
            sc = path[sc_key]
            periods = [
                make_period(f"Period 2 ({age+5}-{age+7}歳)",
                    [{"type": "キャリア変化", "description": f"{sc['label']}に向けた行動期", "probability": sc["prob"], "probability_note": f"{sc_key}シナリオの実現確率"}]),
                make_period(f"Period 3 ({age+8}-{age+9}歳)",
                    [{"type": "結果", "description": f"{sc['label']}の結果が顕在化", "probability": sc["prob"], "probability_note": ""}]),
                make_period(f"Period 4 ({age+10}-{age+11}歳)",
                    [{"type": "安定期", "description": f"{sc['label']}の安定フェーズ", "probability": sc["prob"]*1.2 if sc["prob"]*1.2 < 1 else 0.9, "probability_note": ""}])
            ]
            return {
                "scenario_id": sc_key, "label": sc["label"],
                "probability": sc["prob"],
                "probability_note": path.get("prob_rationale", ""),
                "periods": periods,
                "final_state": {
                    "annual_income": float(sc["income"]),
                    "satisfaction": sc["sat"],
                    "stress": sc["stress"],
                    "work_life_balance": sc["wlb"]
                }
            }
        path_obj = {
            "path_id": path_id, "label": path["label"],
            "direction": path.get("direction", ""),
            "risk": path["risk"], "upside": path["upside"],
            "score": path["score"], "overall_probability": path["probability"],
            "probability_rationale": path.get("prob_rationale", ""),
            "common_periods": [common_period],
            "branch_point": path.get("branch_point", f"{age+4}歳時点が分岐点"),
            "scenarios": [make_scenario("best"), make_scenario("likely"), make_scenario("base")]
        }
        data["paths"].append(path_obj)
    return data

def build_multipath_compact(p):
    """Build multipath_result for compact persona (session_04-10)."""
    data = {
        "identity": {
            "name": p["name"], "age_at_start": p["age"], "gender": p["gender"],
            "education": p["education"], "mbti": p.get("mbti", ""),
            "stable_traits": p["traits"], "certifications": p.get("certifications", []),
            "career_history_summary": p["career_summary"]
        },
        "simulation_years": 10.0, "total_rounds": 40,
        "paths": []
    }
    age = p["age"]
    labels = p["path_labels"]
    best_inc = p["best_incomes"]
    likely_inc = p["likely_incomes"]
    base_inc = p["base_incomes"]

    for i, label in enumerate(labels):
        path_id = f"path_{chr(97+i)}"
        common_period = make_period(
            f"Period 1 ({age+2}-{age+4}歳)",
            [{"type": "準備期", "description": f"{label}に向けた準備・検討", "probability": 0.65, "probability_note": ""}]
        )

        def sc(sc_id, lbl, prob, inc, sat, stress, wlb):
            return {
                "scenario_id": sc_id, "label": lbl,
                "probability": prob, "probability_note": "",
                "periods": [
                    make_period(f"Period 2 ({age+5}-{age+7}歳)", [{"type": "転換期", "description": f"{lbl}への移行", "probability": prob, "probability_note": ""}]),
                    make_period(f"Period 3 ({age+8}-{age+9}歳)", [{"type": "成長期", "description": f"{lbl}の進展", "probability": min(prob*1.1, 0.95), "probability_note": ""}]),
                    make_period(f"Period 4 ({age+10}-{age+11}歳)", [{"type": "安定期", "description": f"{lbl}の結実", "probability": min(prob*1.2, 0.95), "probability_note": ""}])
                ],
                "final_state": {"annual_income": float(inc), "satisfaction": sat, "stress": stress, "work_life_balance": wlb}
            }

        best_s = sc("best", f"{label}（最良）", round(0.05 + i*0.02, 2), best_inc[i], 0.88, 0.50, 0.50)
        likely_s = sc("likely", f"{label}（標準）", round(0.50 + i*0.02, 2), likely_inc[i], 0.70, 0.50, 0.55)
        base_s = sc("base", f"{label}（保守）", round(0.45 - i*0.02, 2), base_inc[i], 0.50, 0.55, 0.55)

        path_obj = {
            "path_id": path_id, "label": label, "direction": "",
            "risk": f"{label}のリスクシナリオ", "upside": f"{label}の成功シナリオ",
            "score": round(0.70 - i*0.03, 2),
            "overall_probability": round(0.30 - i*0.04, 2) if round(0.30 - i*0.04, 2) > 0.05 else 0.10,
            "probability_rationale": f"{label}の実現可能性分析",
            "common_periods": [common_period],
            "branch_point": f"{age+4}歳時点が分岐点",
            "scenarios": [best_s, likely_s, base_s]
        }
        data["paths"].append(path_obj)
    return data


def build_swarm_agents(p):
    agents_data = p.get("agents", [])
    result = []
    for a in agents_data:
        obj = {
            "agent_id": a["agent_id"], "name": a["name"],
            "bio": a["bio"], "stance": a["stance"],
            "role": a["role"], "category": a["category"],
            "personality": a["bio"],
            "speaking_style": "",
            "background": a["bio"],
            "path_ref": "path_a",
            "is_copy_agent": a["category"] == "copy_agent"
        }
        result.append(obj)
    return result

def build_swarm_jsonl(agents, persona_name, round_num):
    lines = []
    topics = [
        "キャリアの方向性について議論を開始します。",
        "リスクとリターンのバランスについて考えます。",
        "家族・生活面への影響を議論します。",
        "業界トレンドとの整合性を検討します。",
        "最終的な推奨パスを議論します。"
    ]
    topic = topics[round_num - 1] if round_num <= 5 else topics[0]

    for i, agent in enumerate(agents):
        # Each agent posts once per round
        post = {
            "round_num": round_num,
            "agent_id": agent["agent_id"],
            "agent_name": agent["name"],
            "action_type": "CREATE_POST",
            "action_args": {
                "content": f"[Round {round_num}] {persona_name}さんのキャリアについて。{topic} {agent['bio'][:50]}の観点から意見を述べます。",
                "target_post_id": None
            },
            "timestamp": f"2026-Q{((round_num-1)%4)+1}"
        }
        lines.append(json.dumps(post, ensure_ascii=False))

        # First 3 agents also comment on the previous agent's post
        if i > 0 and i <= 3:
            comment = {
                "round_num": round_num,
                "agent_id": agent["agent_id"],
                "agent_name": agent["name"],
                "action_type": "CREATE_COMMENT",
                "action_args": {
                    "content": f"{agents[i-1]['name']}さんの意見に対して、{agent['stance']}の立場からコメントします。",
                    "target_post_id": agents[i-1]["agent_id"]
                },
                "timestamp": f"2026-Q{((round_num-1)%4)+1}"
            }
            lines.append(json.dumps(comment, ensure_ascii=False))

    return "\n".join(lines) + "\n"

def build_fact_check(p):
    checks = p.get("fact_checks", [])
    result = []
    for fc in checks:
        result.append({
            "claim_id": fc["claim_id"],
            "location": fc["location"],
            "original_value": fc["original_value"],
            "original_note": "",
            "status": fc["status"],
            "verified_value": fc["verified_value"],
            "sources": [{"title": "調査データ", "url": "", "excerpt": fc["note"], "reliability": "medium"}],
            "note": fc["note"],
            "suggested_correction": None if fc["status"] == "verified" else {"value": fc["verified_value"], "note_addition": fc["note"]}
        })
    return {
        "fact_check_metadata": {
            "checked_at": "2026-03-15T16:00:00",
            "total_claims": len(checks),
            "verified": sum(1 for c in checks if c["status"] == "verified"),
            "adjusted": sum(1 for c in checks if c["status"] == "adjusted"),
            "unverified": 0, "disputed": 0
        },
        "checks": result
    }

def build_macro_trends(p):
    trends = p.get("trends", [])
    trend_list = []
    for t in trends:
        trend_list.append({
            "trend_id": t["trend_id"], "label": t["label"],
            "category": t["category"], "description": t["description"],
            "probability": t["probability"], "timeframe": t["timeframe"],
            "impact_by_path": {},
            "sources": [{"title": f"{t['label']}関連データ", "excerpt": t["description"]}]
        })
    benchmarks = p.get("salary_benchmarks", [])
    sb = []
    for b in benchmarks:
        sb.append({"role": b["role"], "range": b["range"], "source": b["source"], "note": ""})
    return {"trends": trend_list, "salary_benchmarks": sb}


def generate_compact_persona_full(cp):
    """Convert compact persona to a full-ish dict with agents, fact_checks, trends."""
    # Generate default agents
    cp["agents"] = [
        {"agent_id": "agent_mentor", "name": f"{cp['name']}のメンター", "bio": f"{cp['current_employer']}での上司・メンター。", "stance": "supportive", "role": "メンター", "category": "hr_career"},
        {"agent_id": "agent_peer", "name": f"{cp['name']}の同僚", "bio": f"同業界の同世代の友人。", "stance": "neutral", "role": "同僚", "category": "private"},
        {"agent_id": "agent_family", "name": f"{cp['name']}の家族", "bio": f"家族の視点から安定を重視。", "stance": "neutral" if cp["marital_status"] == "single" else "opposing", "role": "家族", "category": "private"},
        {"agent_id": "agent_consultant", "name": "キャリアアドバイザー", "bio": f"{cp['industry']}業界に詳しい転職エージェント。", "stance": "neutral", "role": "キャリアアドバイザー", "category": "hr_career"},
        {"agent_id": "agent_industry", "name": "業界有識者", "bio": f"{cp['industry']}の第一人者。", "stance": "neutral", "role": "業界有識者", "category": "business_strategy"},
        {"agent_id": "copy_agent_balanced", "name": "バランス型の自分", "bio": "長期的な持続可能性を重視する自分。", "stance": "neutral", "role": "copy_agent", "category": "copy_agent"}
    ]
    cp["family_members"] = cp.get("family", [])
    # Generate default fact_checks
    cp["fact_checks"] = [
        {"claim_id": "FC-001", "location": "path_a > probability", "original_value": f"{cp['path_labels'][0]}", "status": "verified", "verified_value": "妥当", "note": f"{cp['industry']}業界のデータと整合"},
        {"claim_id": "FC-002", "location": "path_b > income", "original_value": str(cp["best_incomes"][1]), "status": "adjusted", "verified_value": f"{int(cp['best_incomes'][1]*0.9)}-{cp['best_incomes'][1]}", "note": "市場データに基づき微調整"},
        {"claim_id": "FC-003", "location": "overall > salary", "original_value": str(cp["salary"]), "status": "verified", "verified_value": str(cp["salary"]), "note": f"{cp['current_employer']}の報酬水準と整合"}
    ]
    # Generate default trends
    cp["trends"] = [
        {"trend_id": "industry_change", "label": f"{cp['industry']}業界の構造変化", "category": "technology", "description": f"{cp['industry']}におけるDX・AI活用の進展", "probability": 0.80, "timeframe": "2026-2032"},
        {"trend_id": "labor_shift", "label": "働き方の多様化", "category": "workforce", "description": "リモートワーク・副業・フリーランスの増加", "probability": 0.85, "timeframe": "2026-2030"},
        {"trend_id": "demographics", "label": "人口動態変化", "category": "demographics", "description": "労働人口減少と高齢化の影響", "probability": 0.95, "timeframe": "2026-2035"}
    ]
    cp["salary_benchmarks"] = [
        {"role": cp["current_role"], "range": f"{int(cp['salary']*0.8)}-{int(cp['salary']*1.2)}万円", "source": "OpenWork 2024"},
        {"role": f"{cp['industry']}上位ポジション", "range": f"{int(cp['best_incomes'][0]*0.8)}-{cp['best_incomes'][0]}万円", "source": "業界調査 2024"}
    ]
    return cp


def main():
    # Process full personas (session_01-03)
    for p in PERSONAS:
        session_dir = BASE / p["id"]
        session_dir.mkdir(parents=True, exist_ok=True)
        swarm_dir = session_dir / "swarm"
        swarm_dir.mkdir(exist_ok=True)

        # Write files
        (session_dir / "profile.json").write_text(json.dumps(build_profile(p), ensure_ascii=False, indent=2))
        (session_dir / "form.json").write_text(json.dumps(build_form(p), ensure_ascii=False, indent=2))
        (session_dir / "agent_state.json").write_text(json.dumps(build_agent_state(p), ensure_ascii=False, indent=2))
        (session_dir / "multipath_result.json").write_text(json.dumps(build_multipath_full(p), ensure_ascii=False, indent=2))

        agents = build_swarm_agents(p)
        (session_dir / "swarm_agents.json").write_text(json.dumps(agents, ensure_ascii=False, indent=2))

        for r in range(1, 6):
            jsonl = build_swarm_jsonl(agents, p["name"], r)
            (swarm_dir / f"all_actions_round_{r:03d}.jsonl").write_text(jsonl)

        (session_dir / "fact_check_result.json").write_text(json.dumps(build_fact_check(p), ensure_ascii=False, indent=2))
        (session_dir / "macro_trends.json").write_text(json.dumps(build_macro_trends(p), ensure_ascii=False, indent=2))

        print(f"Generated: {p['id']} ({p['name']})")

    # Process compact personas (session_04-10)
    for cp in PERSONAS_COMPACT:
        cp_full = generate_compact_persona_full(cp)
        session_dir = BASE / cp_full["id"]
        session_dir.mkdir(parents=True, exist_ok=True)
        swarm_dir = session_dir / "swarm"
        swarm_dir.mkdir(exist_ok=True)

        (session_dir / "profile.json").write_text(json.dumps(build_profile(cp_full), ensure_ascii=False, indent=2))
        (session_dir / "form.json").write_text(json.dumps(build_form(cp_full), ensure_ascii=False, indent=2))
        (session_dir / "agent_state.json").write_text(json.dumps(build_agent_state(cp_full), ensure_ascii=False, indent=2))
        (session_dir / "multipath_result.json").write_text(json.dumps(build_multipath_compact(cp_full), ensure_ascii=False, indent=2))

        agents = build_swarm_agents(cp_full)
        (session_dir / "swarm_agents.json").write_text(json.dumps(agents, ensure_ascii=False, indent=2))

        for r in range(1, 6):
            jsonl = build_swarm_jsonl(agents, cp_full["name"], r)
            (swarm_dir / f"all_actions_round_{r:03d}.jsonl").write_text(jsonl)

        (session_dir / "fact_check_result.json").write_text(json.dumps(build_fact_check(cp_full), ensure_ascii=False, indent=2))
        (session_dir / "macro_trends.json").write_text(json.dumps(build_macro_trends(cp_full), ensure_ascii=False, indent=2))

        print(f"Generated: {cp_full['id']} ({cp_full['name']})")

    print("\nAll 10 sessions generated!")


if __name__ == "__main__":
    main()

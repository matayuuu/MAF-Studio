from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta

COMMON_TRAINING = [
    {"week": 1, "day": 1, "title": "会社概要・経営理念", "duration": "1時間", "format": "対面", "mandatory": True},
    {"week": 1, "day": 1, "title": "就業規則・勤務ルール", "duration": "1時間", "format": "対面", "mandatory": True},
    {"week": 1, "day": 1, "title": "社内ツール操作研修", "duration": "2時間", "format": "対面", "mandatory": True},
    {"week": 1, "day": 2, "title": "情報セキュリティ基礎 (eラーニング)", "duration": "2時間", "format": "eラーニング", "mandatory": True},
    {"week": 1, "day": 3, "title": "コンプライアンス研修 (eラーニング)", "duration": "1.5時間", "format": "eラーニング", "mandatory": True},
    {"week": 1, "day": 4, "title": "個人情報保護研修 (eラーニング)", "duration": "1時間", "format": "eラーニング", "mandatory": True},
]

ROLE_TRAINING = {
    "engineer": [
        {"week": 1, "title": "開発環境構築", "duration": "4時間", "format": "ハンズオン"},
        {"week": 2, "title": "アーキテクチャ・システム構成理解", "duration": "1日", "format": "講義+ハンズオン"},
        {"week": 2, "title": "Git/CI/CD ワークフロー研修", "duration": "2時間", "format": "ハンズオン"},
        {"week": 3, "title": "コーディング規約・レビュー基準", "duration": "2時間", "format": "講義"},
        {"week": 3, "title": "テスト戦略・テストの書き方", "duration": "2時間", "format": "ハンズオン"},
        {"week": 4, "title": "小規模タスク実践 (バグ修正 or 軽微機能追加)", "duration": "1週間", "format": "OJT"},
    ],
    "sales": [
        {"week": 1, "title": "製品ラインナップ・機能概要", "duration": "1日", "format": "講義"},
        {"week": 2, "title": "競合比較・差別化ポイント", "duration": "半日", "format": "講義"},
        {"week": 2, "title": "営業プロセス (リード→クロージング)", "duration": "半日", "format": "講義"},
        {"week": 3, "title": "Salesforce操作・見積書作成", "duration": "半日", "format": "ハンズオン"},
        {"week": 3, "title": "提案書テンプレートの使い方", "duration": "2時間", "format": "ハンズオン"},
        {"week": 4, "title": "同行営業 (3件以上)", "duration": "1週間", "format": "OJT"},
    ],
    "hr": [
        {"week": 2, "title": "労務管理基礎", "duration": "1日", "format": "講義"},
        {"week": 3, "title": "SmartHR操作研修", "duration": "半日", "format": "ハンズオン"},
        {"week": 4, "title": "採用プロセス研修", "duration": "半日", "format": "講義"},
    ],
    "finance": [
        {"week": 2, "title": "経理業務フロー全体像", "duration": "1日", "format": "講義"},
        {"week": 3, "title": "freee操作研修", "duration": "半日", "format": "ハンズオン"},
        {"week": 3, "title": "請求書処理フロー", "duration": "半日", "format": "講義"},
        {"week": 4, "title": "月次決算の流れ", "duration": "半日", "format": "講義"},
    ],
}

parser = argparse.ArgumentParser(description="Generate training plan based on role.")
parser.add_argument("--start_date", type=str, required=True, help="Start date (YYYY-MM-DD)")
parser.add_argument("--role", type=str, required=True, choices=["engineer", "sales", "hr", "finance", "other"])
parser.add_argument("--level", type=str, default="junior", choices=["junior", "mid", "senior"])
args = parser.parse_args()

start = datetime.strptime(args.start_date, "%Y-%m-%d")

# Build schedule
schedule = {"common": [], "role_specific": [], "milestones": []}

for t in COMMON_TRAINING:
    date = start + timedelta(days=t["day"] - 1)
    schedule["common"].append({
        "date": date.strftime("%Y-%m-%d"),
        "title": t["title"],
        "duration": t["duration"],
        "format": t["format"],
        "mandatory": t["mandatory"],
    })

role_items = ROLE_TRAINING.get(args.role, [])
for t in role_items:
    week_start = start + timedelta(weeks=t["week"] - 1)
    schedule["role_specific"].append({
        "week": f"第{t['week']}週 ({week_start.strftime('%m/%d')}〜)",
        "title": t["title"],
        "duration": t["duration"],
        "format": t["format"],
    })

# Senior can skip some basic training
if args.level == "senior":
    schedule["note"] = "シニアレベルのため、基礎研修は短縮可能。メンターと相談の上、スキップする項目を決定してください。"

# Milestones
schedule["milestones"] = [
    {"timing": "1週間後", "date": (start + timedelta(days=7)).strftime("%Y-%m-%d"), "milestone": "全社共通研修の完了"},
    {"timing": "1ヶ月後", "date": (start + timedelta(days=30)).strftime("%Y-%m-%d"), "milestone": "部門別基礎研修の完了・初回1on1"},
    {"timing": "3ヶ月後", "date": (start + timedelta(days=90)).strftime("%Y-%m-%d"), "milestone": "試用期間終了・評価面談"},
]

result = {
    "training_plan": {
        "start_date": args.start_date,
        "role": args.role,
        "level": args.level,
    },
    "schedule": schedule,
}

print(json.dumps(result, ensure_ascii=False, indent=2))

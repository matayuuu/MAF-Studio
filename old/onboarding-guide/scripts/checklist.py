from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta

COMMON_TASKS = [
    {"category": "書類提出", "task": "マイナンバー通知カードのコピー提出", "deadline_days": 0, "owner": "本人"},
    {"category": "書類提出", "task": "給与振込口座届の提出", "deadline_days": 0, "owner": "本人"},
    {"category": "書類提出", "task": "扶養控除等申告書の提出", "deadline_days": 0, "owner": "本人"},
    {"category": "書類提出", "task": "通勤経路届の提出", "deadline_days": 3, "owner": "本人"},
    {"category": "環境構築", "task": "PC受取・初期セットアップ", "deadline_days": 0, "owner": "情シス"},
    {"category": "環境構築", "task": "Entra ID 初回ログイン・パスワード変更", "deadline_days": 0, "owner": "本人"},
    {"category": "環境構築", "task": "Microsoft 365 動作確認 (Outlook, Teams)", "deadline_days": 0, "owner": "本人"},
    {"category": "環境構築", "task": "VPN接続テスト", "deadline_days": 1, "owner": "情シス"},
    {"category": "研修", "task": "情報セキュリティ研修 (eラーニング)", "deadline_days": 5, "owner": "本人"},
    {"category": "研修", "task": "コンプライアンス研修 (eラーニング)", "deadline_days": 5, "owner": "本人"},
    {"category": "研修", "task": "個人情報保護研修 + 同意書署名", "deadline_days": 5, "owner": "本人"},
    {"category": "研修", "task": "社内ツール操作研修", "deadline_days": 3, "owner": "人事"},
    {"category": "申請", "task": "勤怠管理システムの打刻テスト", "deadline_days": 1, "owner": "人事"},
    {"category": "申請", "task": "経費精算システムの申請者登録", "deadline_days": 5, "owner": "経理"},
]

ROLE_SPECIFIC_TASKS = {
    "engineer": [
        {"category": "環境構築", "task": "GitHub Enterprise アカウント申請", "deadline_days": 1, "owner": "メンター"},
        {"category": "環境構築", "task": "開発環境構築 (IDE, SDK, Docker等)", "deadline_days": 3, "owner": "本人"},
        {"category": "環境構築", "task": "Azure DevOps アクセス申請", "deadline_days": 2, "owner": "メンター"},
        {"category": "環境構築", "task": "クラウド検証環境アクセス申請", "deadline_days": 5, "owner": "上長"},
        {"category": "研修", "task": "アーキテクチャ・システム構成の理解", "deadline_days": 10, "owner": "テックリード"},
        {"category": "研修", "task": "コーディング規約の確認", "deadline_days": 5, "owner": "メンター"},
    ],
    "sales": [
        {"category": "環境構築", "task": "Salesforce アカウント申請", "deadline_days": 2, "owner": "営業企画"},
        {"category": "研修", "task": "製品知識研修", "deadline_days": 5, "owner": "営業企画"},
        {"category": "研修", "task": "営業プロセス研修", "deadline_days": 10, "owner": "営業マネージャー"},
        {"category": "実践", "task": "先輩営業への同行 (3件以上)", "deadline_days": 20, "owner": "メンター"},
    ],
    "hr": [
        {"category": "環境構築", "task": "SmartHR アカウント申請", "deadline_days": 1, "owner": "人事部"},
        {"category": "研修", "task": "労務管理基礎研修", "deadline_days": 10, "owner": "人事マネージャー"},
    ],
    "finance": [
        {"category": "環境構築", "task": "freee アカウント申請 (一般権限)", "deadline_days": 2, "owner": "経理部"},
        {"category": "環境構築", "task": "マネーフォワード アカウント申請", "deadline_days": 2, "owner": "経理部"},
        {"category": "研修", "task": "経理業務フロー研修", "deadline_days": 10, "owner": "経理マネージャー"},
    ],
}

TYPE_SPECIFIC_TASKS = {
    "fulltime": [
        {"category": "書類提出", "task": "身元保証書の提出 (2名分)", "deadline_days": 5, "owner": "本人"},
        {"category": "申請", "task": "確定拠出年金(DC)加入手続き", "deadline_days": 20, "owner": "人事"},
    ],
    "contract": [],
    "parttime": [],
    "dispatch": [
        {"category": "確認", "task": "アクセス権限の範囲確認 (最小限)", "deadline_days": 1, "owner": "情シス"},
    ],
}

parser = argparse.ArgumentParser(description="Generate onboarding checklist.")
parser.add_argument("--start_date", type=str, required=True, help="Start date (YYYY-MM-DD)")
parser.add_argument("--department", type=str, required=True, choices=["engineer", "sales", "hr", "finance", "other"])
parser.add_argument("--employment_type", type=str, default="fulltime", choices=["fulltime", "contract", "parttime", "dispatch"])
args = parser.parse_args()

start = datetime.strptime(args.start_date, "%Y-%m-%d")

tasks = list(COMMON_TASKS)
tasks.extend(ROLE_SPECIFIC_TASKS.get(args.department, []))
tasks.extend(TYPE_SPECIFIC_TASKS.get(args.employment_type, []))

checklist = []
for t in tasks:
    deadline = start + timedelta(days=t["deadline_days"])
    checklist.append({
        "category": t["category"],
        "task": t["task"],
        "deadline": deadline.strftime("%Y-%m-%d"),
        "owner": t["owner"],
        "status": "未着手",
    })

checklist.sort(key=lambda x: x["deadline"])

result = {
    "onboarding_checklist": {
        "start_date": args.start_date,
        "department": args.department,
        "employment_type": args.employment_type,
        "total_tasks": len(checklist),
    },
    "tasks": checklist,
}

print(json.dumps(result, ensure_ascii=False, indent=2))

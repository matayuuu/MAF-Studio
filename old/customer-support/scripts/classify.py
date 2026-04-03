from __future__ import annotations

import argparse
import json
import re

# Priority classification rules
KEYWORDS_P1 = ["停止", "ダウン", "全面", "データ損失", "セキュリティ", "不正アクセス", "情報漏洩", "侵害"]
KEYWORDS_P2 = ["障害", "エラー", "使えない", "動かない", "ログインできない", "500エラー", "タイムアウト"]
KEYWORDS_P3 = ["不具合", "表示されない", "遅い", "文字化け", "おかしい", "反映されない"]
KEYWORDS_P4 = ["方法", "やり方", "教えて", "設定", "変更", "エクスポート", "要望", "改善"]

TEAM_MAP = {
    "P1": "インフラチーム + マネージャー",
    "P2": "L2テクニカルサポート",
    "P3": "L1サポート（必要に応じてL2）",
    "P4": "L1サポート",
}

SLA_MAP = {
    "P1": {"first_response": "30分以内", "resolution": "4時間以内"},
    "P2": {"first_response": "2時間以内", "resolution": "8時間以内"},
    "P3": {"first_response": "4時間以内", "resolution": "3営業日以内"},
    "P4": {"first_response": "1営業日以内", "resolution": "5営業日以内"},
}

ESCALATION_IMMEDIATE = [
    {"keyword": "セキュリティ|不正アクセス|情報漏洩", "team": "セキュリティチーム + CISO", "reason": "セキュリティインシデントの疑い"},
    {"keyword": "訴訟|弁護士|法的", "team": "法務部 + 部長", "reason": "法的リスク"},
    {"keyword": "SNS|Twitter|報道|メディア", "team": "広報部 + 経営層", "reason": "メディア・SNSリスク"},
]

parser = argparse.ArgumentParser(description="Classify customer inquiry and determine priority.")
parser.add_argument("--inquiry", type=str, required=True, help="Customer inquiry text")
parser.add_argument("--plan", type=str, default="standard", help="Customer's plan (standard/enterprise)")
args = parser.parse_args()

inquiry = args.inquiry.lower()
priority = "P4"
matched_keywords = []

# Check immediate escalation triggers first
immediate_escalation = None
for rule in ESCALATION_IMMEDIATE:
    if re.search(rule["keyword"], args.inquiry):
        immediate_escalation = rule
        priority = "P1"
        break

# Priority classification
if not immediate_escalation:
    for kw in KEYWORDS_P1:
        if kw in inquiry:
            priority = "P1"
            matched_keywords.append(kw)
            break
    if priority != "P1":
        for kw in KEYWORDS_P2:
            if kw in inquiry:
                priority = "P2"
                matched_keywords.append(kw)
                break
    if priority not in ("P1", "P2"):
        for kw in KEYWORDS_P3:
            if kw in inquiry:
                priority = "P3"
                matched_keywords.append(kw)
                break

# Enterprise plan escalation
if args.plan == "enterprise" and priority in ("P3", "P4"):
    priority = "P" + str(max(1, int(priority[1]) - 1))

sla = SLA_MAP[priority]
team = TEAM_MAP[priority]

result = {
    "classification": {
        "priority": priority,
        "team": team,
        "matched_keywords": matched_keywords,
    },
    "sla": sla,
}

if immediate_escalation:
    result["immediate_escalation"] = {
        "required": True,
        "team": immediate_escalation["team"],
        "reason": immediate_escalation["reason"],
    }

if args.plan == "enterprise":
    result["note"] = "エンタープライズプラン顧客のため、優先度を1段階引き上げています"

print(json.dumps(result, ensure_ascii=False, indent=2))

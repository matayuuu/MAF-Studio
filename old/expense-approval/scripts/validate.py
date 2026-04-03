from __future__ import annotations

import argparse
import json

# Approval thresholds
APPROVAL_RULES = [
    (5000, "承認不要（自動承認）", []),
    (30000, "直属の上長", ["領収書"]),
    (100000, "部長", ["領収書", "事前申請推奨"]),
    (500000, "本部長", ["領収書", "事前承認必須"]),
    (float("inf"), "役員（CFO）", ["領収書", "事前承認", "稟議書"]),
]

SPECIAL_CATEGORIES = {
    "交際費": {"approver_override": "部長以上", "extra_docs": ["参加者リスト", "目的・議題"]},
    "タクシー代": {"extra_docs": ["利用理由書（23時以降 or 荷物大量の場合は不要）"]},
    "IT機器": {"extra_docs": ["情報システム部の事前承認メール"], "note": "10,000円以上は情報システム部の確認必須"},
    "海外出張": {"approver_override": "本部長", "extra_docs": ["事前承認書", "出張計画書"]},
}

# Meeting vs entertainment threshold
MEETING_THRESHOLD_PER_PERSON = 5000

parser = argparse.ArgumentParser(description="Validate expense and determine approval route.")
parser.add_argument("--amount", type=int, required=True, help="Expense amount in JPY")
parser.add_argument("--category", type=str, required=True, help="Expense category")
parser.add_argument("--participants", type=int, default=1, help="Number of participants (for dining)")
parser.add_argument("--description", type=str, default="", help="Expense description")
args = parser.parse_args()

amount = args.amount
category = args.category
per_person = amount // max(args.participants, 1)

# Determine approval route
approver = ""
required_docs = []
for threshold, appr, docs in APPROVAL_RULES:
    if amount < threshold:
        approver = appr
        required_docs = list(docs)
        break

warnings = []
notes = []

# Special category checks
if category in SPECIAL_CATEGORIES:
    special = SPECIAL_CATEGORIES[category]
    if "approver_override" in special:
        approver = f"{special['approver_override']}（{category}のため）"
    required_docs.extend(special.get("extra_docs", []))
    if "note" in special:
        notes.append(special["note"])

# Dining: meeting vs entertainment classification
if category in ("飲食", "会議費", "交際費"):
    if per_person <= MEETING_THRESHOLD_PER_PERSON:
        suggested_category = "会議費（科目: 7210）"
        notes.append(f"1名あたり {per_person:,}円 → 会議費として処理可能（損金算入OK）")
    else:
        suggested_category = "交際費（科目: 7220）"
        warnings.append(f"1名あたり {per_person:,}円（5,000円超）→ 交際費に該当します")
        required_docs.extend(["参加者リスト", "目的"])
        approver = "部長以上"
else:
    suggested_category = category

# Deadline warning
notes.append("申請締め日: 毎月25日。締め日を過ぎると翌月処理になります。")

result = {
    "input": {
        "amount": f"{amount:,}円",
        "category": category,
        "participants": args.participants,
        "per_person": f"{per_person:,}円",
    },
    "approval": {
        "approver": approver,
        "required_documents": list(dict.fromkeys(required_docs)),  # dedupe preserving order
    },
    "suggested_category": suggested_category,
    "warnings": warnings,
    "notes": notes,
}

print(json.dumps(result, ensure_ascii=False, indent=2))

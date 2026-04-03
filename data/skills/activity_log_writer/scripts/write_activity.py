"""
write_activity.py — 顧客対応履歴を activities.csv に追記する
Usage: python write_activity.py --customer_id C016 --activity_type チャット --agent_name FrontAgent --subject 問合せ --content 内容 --outcome 提案済み --next_action フォロー --next_action_date 2026-05-01
"""
import argparse
import csv
import json
from pathlib import Path
from datetime import date

DATA_FILE = Path(__file__).resolve().parents[4] / "demo_app" / "data" / "activities.csv"


def next_activity_id() -> str:
    with open(DATA_FILE, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return "A001"
    max_num = max(int(r["activity_id"][1:]) for r in rows if r["activity_id"].startswith("A"))
    return f"A{max_num + 1:03d}"


def write_activity(
    customer_id: str,
    activity_type: str,
    agent_name: str,
    subject: str,
    content: str,
    outcome: str,
    next_action: str,
    next_action_date: str,
) -> dict:
    new_id = next_activity_id()
    row = {
        "activity_id": new_id,
        "customer_id": customer_id,
        "activity_type": activity_type,
        "activity_date": date.today().isoformat(),
        "agent_name": agent_name,
        "subject": subject,
        "content": content,
        "outcome": outcome,
        "next_action": next_action,
        "next_action_date": next_action_date,
    }
    with open(DATA_FILE, encoding="utf-8") as f:
        fieldnames = csv.DictReader(f).fieldnames

    with open(DATA_FILE, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(row)

    return {"success": True, "activity_id": new_id, "message": f"活動履歴 {new_id} を記録しました。"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--customer_id", required=True)
    parser.add_argument("--activity_type", default="チャット")
    parser.add_argument("--agent_name", default="")
    parser.add_argument("--subject", default="")
    parser.add_argument("--content", default="")
    parser.add_argument("--outcome", default="情報提供")
    parser.add_argument("--next_action", default="")
    parser.add_argument("--next_action_date", default="")
    args = parser.parse_args()
    result = write_activity(
        args.customer_id, args.activity_type, args.agent_name,
        args.subject, args.content, args.outcome,
        args.next_action, args.next_action_date,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))

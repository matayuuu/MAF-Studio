"""
verify_identity.py — 顧客IDで本人確認を行う
Usage: python verify_identity.py --customer_id C001
"""
import argparse
import csv
import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[4] / "demo_app" / "data" / "customers.csv"


def verify(customer_id: str) -> dict:
    with open(DATA_FILE, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["customer_id"].strip() == customer_id.strip():
                return {
                    "verified": True,
                    "customer_id": row["customer_id"],
                    "full_name": f"{row['last_name']} {row['first_name']}",
                    "full_name_kana": f"{row['last_name_kana']} {row['first_name_kana']}",
                    "message": f"本人確認が完了しました。{row['last_name']} {row['first_name']} 様でお間違いないでしょうか？",
                }
    return {"verified": False, "message": "お客様情報が見つかりません。顧客IDをご確認ください。"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--customer_id", required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.customer_id), ensure_ascii=False, indent=2))

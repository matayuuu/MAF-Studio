"""
lookup_by_id.py — 顧客IDで顧客マスタを検索する
Usage: python lookup_by_id.py --customer_id C016
"""
import argparse
import csv
import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[4] / "demo_app" / "data" / "customers.csv"


FIELDS = ["customer_id", "last_name", "first_name", "last_name_kana", "first_name_kana", "gender", "birth_date", "age", "phone", "email", "prefecture"]


def lookup(customer_id: str) -> dict | None:
    with open(DATA_FILE, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["customer_id"].strip() == customer_id.strip():
                return {k: row[k] for k in FIELDS if k in row}
    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--customer_id", required=True)
    args = parser.parse_args()
    result = lookup(args.customer_id)
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"error": f"顧客ID '{args.customer_id}' は見つかりませんでした。"}, ensure_ascii=False))

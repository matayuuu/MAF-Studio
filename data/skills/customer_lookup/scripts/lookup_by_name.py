"""
lookup_by_name.py — 氏名（姓・名）で顧客マスタを検索する
Usage: python lookup_by_name.py --last_name 又吉 [--first_name 佑樹]
"""
import argparse
import csv
import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[4] / "demo_app" / "data" / "customers.csv"


FIELDS = ["customer_id", "last_name", "first_name", "last_name_kana", "first_name_kana", "gender", "birth_date", "age", "phone", "email", "prefecture"]


def lookup(last_name: str, first_name: str = "") -> list[dict]:
    results = []
    with open(DATA_FILE, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["last_name"].strip() == last_name.strip():
                if not first_name or row["first_name"].strip() == first_name.strip():
                    results.append({k: row[k] for k in FIELDS if k in row})
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--last_name", required=True)
    parser.add_argument("--first_name", default="")
    args = parser.parse_args()
    results = lookup(args.last_name, args.first_name)
    if results:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"error": f"氏名 '{args.last_name} {args.first_name}' のお客様は見つかりませんでした。"}, ensure_ascii=False))

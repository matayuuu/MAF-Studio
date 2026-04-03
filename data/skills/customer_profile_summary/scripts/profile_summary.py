"""
profile_summary.py — 顧客の統合サマリーを生成する
Usage: python profile_summary.py --customer_id C016
"""
import argparse
import csv
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[4] / "demo_app" / "data"


def load_csv(name: str) -> list[dict]:
    with open(BASE / name, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def summarize(customer_id: str) -> dict:
    customers = load_csv("customers.csv")
    contracts = load_csv("contracts.csv")
    products = load_csv("products.csv")
    activities = load_csv("activities.csv")

    customer = next((r for r in customers if r["customer_id"] == customer_id), None)
    if not customer:
        return {"error": f"顧客ID '{customer_id}' は見つかりませんでした。"}

    product_map = {p["product_id"]: p["product_name"] for p in products}

    active_contracts = [
        {
            "contract_id": c["contract_id"],
            "product_name": product_map.get(c["product_id"], c["product_id"]),
            "monthly_premium": c["monthly_premium"],
            "contract_status": c["contract_status"],
            "start_date": c["start_date"],
            "next_review_date": c["next_review_date"],
        }
        for c in contracts
        if c["customer_id"] == customer_id and c["contract_status"] == "有効"
    ]

    recent_activities = sorted(
        [a for a in activities if a["customer_id"] == customer_id],
        key=lambda x: x["activity_date"],
        reverse=True,
    )[:3]

    income = int(customer.get("annual_income") or 0)
    age = int(customer.get("age") or 0)
    segment = "中間層"
    if income >= 10_000_000:
        segment = "富裕層"
    elif age >= 60:
        segment = "リタイア層"

    total_premium = sum(int(c["monthly_premium"]) for c in active_contracts)

    return {
        "customer": {
            "customer_id": customer["customer_id"],
            "full_name": f"{customer['last_name']} {customer['first_name']}",
            "age": customer["age"],
            "gender": customer["gender"],
            "occupation": customer["occupation"],
            "annual_income": customer["annual_income"],
            "prefecture": customer["prefecture"],
            "segment": segment,
            "assigned_agent": customer["assigned_agent"],
        },
        "contracts": {
            "count": len(active_contracts),
            "total_monthly_premium": total_premium,
            "items": active_contracts,
        },
        "recent_activities": recent_activities,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--customer_id", required=True)
    args = parser.parse_args()
    print(json.dumps(summarize(args.customer_id), ensure_ascii=False, indent=2))

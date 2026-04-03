from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta

SLA_HOURS = {
    "P1": {"first_response": 0.5, "resolution": 4},
    "P2": {"first_response": 2, "resolution": 8},
    "P3": {"first_response": 4, "resolution": 24},   # 3 business days ≈ 24 biz hours
    "P4": {"first_response": 8, "resolution": 40},    # 5 business days ≈ 40 biz hours
}

parser = argparse.ArgumentParser(description="Check SLA compliance for a support ticket.")
parser.add_argument("--priority", type=str, required=True, choices=["P1", "P2", "P3", "P4"])
parser.add_argument("--received_at", type=str, required=True, help="Ticket received datetime (ISO format)")
parser.add_argument("--first_response_at", type=str, default="", help="First response datetime (ISO format, empty if not yet)")
parser.add_argument("--resolved_at", type=str, default="", help="Resolution datetime (ISO format, empty if not yet)")
args = parser.parse_args()

received = datetime.fromisoformat(args.received_at)
now = datetime.now()
sla = SLA_HOURS[args.priority]

# First response check
fr_deadline = received + timedelta(hours=sla["first_response"])
if args.first_response_at:
    fr_actual = datetime.fromisoformat(args.first_response_at)
    fr_met = fr_actual <= fr_deadline
    fr_status = "SLA達成 ✅" if fr_met else "SLA違反 ❌"
    fr_elapsed = str(fr_actual - received)
else:
    fr_met = now <= fr_deadline
    fr_status = "対応中（期限内）" if fr_met else "SLA超過リスク ⚠️"
    fr_elapsed = str(now - received)

# Resolution check
res_deadline = received + timedelta(hours=sla["resolution"])
if args.resolved_at:
    res_actual = datetime.fromisoformat(args.resolved_at)
    res_met = res_actual <= res_deadline
    res_status = "SLA達成 ✅" if res_met else "SLA違反 ❌"
    res_elapsed = str(res_actual - received)
else:
    res_met = now <= res_deadline
    remaining = res_deadline - now
    if remaining.total_seconds() > 0:
        hours_remaining = remaining.total_seconds() / 3600
        res_status = f"未解決（残り {hours_remaining:.1f} 時間）"
    else:
        res_status = "SLA超過 ❌"
    res_elapsed = str(now - received)

result = {
    "ticket": {
        "priority": args.priority,
        "received_at": args.received_at,
        "elapsed": fr_elapsed,
    },
    "first_response": {
        "sla_target": f"{sla['first_response']}時間以内",
        "deadline": fr_deadline.isoformat(),
        "status": fr_status,
    },
    "resolution": {
        "sla_target": f"{sla['resolution']}時間以内",
        "deadline": res_deadline.isoformat(),
        "status": res_status,
    },
}

print(json.dumps(result, ensure_ascii=False, indent=2))

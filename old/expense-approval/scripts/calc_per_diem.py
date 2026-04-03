from __future__ import annotations

import argparse
import json

# Per diem rates by role
PER_DIEM = {
    "一般社員": {"国内日帰り": 2000, "国内宿泊": 2500, "海外": 5000},
    "主任": {"国内日帰り": 2500, "国内宿泊": 3000, "海外": 6000},
    "係長": {"国内日帰り": 2500, "国内宿泊": 3000, "海外": 6000},
    "課長": {"国内日帰り": 3000, "国内宿泊": 3500, "海外": 8000},
    "部長": {"国内日帰り": 3500, "国内宿泊": 4500, "海外": 10000},
    "本部長": {"国内日帰り": 5000, "国内宿泊": 6000, "海外": 15000},
}

# Hotel rate caps
HOTEL_RATES = {
    "一般社員": {"東京23区": 10000, "大阪市": 9000, "名古屋市": 9000, "政令指定都市": 8500, "その他": 8000, "海外先進国": 20000, "海外新興国": 15000},
    "管理職": {"東京23区": 14000, "大阪市": 12000, "名古屋市": 12000, "政令指定都市": 11000, "その他": 10000, "海外先進国": 30000, "海外新興国": 20000},
}

DESIGNATED_CITIES = ["札幌市", "仙台市", "さいたま市", "千葉市", "横浜市", "川崎市", "相模原市",
                     "新潟市", "静岡市", "浜松市", "京都市", "堺市", "神戸市", "岡山市",
                     "広島市", "北九州市", "福岡市", "熊本市"]

parser = argparse.ArgumentParser(description="Calculate per diem and hotel allowance for business trips.")
parser.add_argument("--destination", type=str, required=True, help="Destination city")
parser.add_argument("--days", type=int, required=True, help="Number of days")
parser.add_argument("--nights", type=int, default=0, help="Number of nights (0 for day trip)")
parser.add_argument("--role", type=str, default="一般社員", help="Employee role/title")
args = parser.parse_args()

# Determine role category
role = args.role
per_diem_rates = PER_DIEM.get(role, PER_DIEM["一般社員"])
is_manager = role in ("課長", "部長", "本部長")
hotel_key = "管理職" if is_manager else "一般社員"
hotel_rates = HOTEL_RATES[hotel_key]

# Determine destination category
dest = args.destination
is_overseas = any(kw in dest for kw in ["海外", "アメリカ", "欧州", "中国", "韓国", "台湾", "シンガポール", "タイ"])

if is_overseas:
    trip_type = "海外"
    hotel_region = "海外先進国"
elif args.nights > 0:
    trip_type = "国内宿泊"
    if "東京" in dest or "23区" in dest:
        hotel_region = "東京23区"
    elif "大阪" in dest:
        hotel_region = "大阪市"
    elif "名古屋" in dest:
        hotel_region = "名古屋市"
    elif any(city in dest for city in DESIGNATED_CITIES):
        hotel_region = "政令指定都市"
    else:
        hotel_region = "その他"
else:
    trip_type = "国内日帰り"
    hotel_region = None

daily_per_diem = per_diem_rates[trip_type]
total_per_diem = daily_per_diem * args.days

hotel_limit = hotel_rates.get(hotel_region, 0) if hotel_region else 0
total_hotel = hotel_limit * args.nights

transport_notes = []
if is_overseas:
    transport_notes.append("飛行機: エコノミークラス" + ("（本部長以上はビジネスクラス可）" if role == "本部長" else ""))
    transport_notes.append("事前承認: 本部長の承認が必要です")
else:
    transport_notes.append("新幹線: 普通車指定席" + ("（課長以上はグリーン車可）" if is_manager else ""))

report_required = "出張報告書＋成果報告（部門会議で共有）" if is_overseas else (
    "出張報告書（帰社後5営業日以内）" if args.nights > 0 else "不要（経費精算のみ）"
)

result = {
    "trip_summary": {
        "destination": dest,
        "days": args.days,
        "nights": args.nights,
        "role": role,
        "trip_type": trip_type,
    },
    "per_diem": {
        "daily_rate": f"{daily_per_diem:,}円",
        "total": f"{total_per_diem:,}円",
    },
    "hotel": {
        "region": hotel_region or "—",
        "nightly_limit": f"{hotel_limit:,}円" if hotel_limit else "—",
        "total_limit": f"{total_hotel:,}円" if total_hotel else "—",
    },
    "estimated_total": f"{total_per_diem + total_hotel:,}円",
    "transport_notes": transport_notes,
    "report_required": report_required,
}

print(json.dumps(result, ensure_ascii=False, indent=2))

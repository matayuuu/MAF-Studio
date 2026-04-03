from __future__ import annotations

import argparse
import json

# Demo weather data (matches CITY_WEATHER_DATA.md)
WEATHER_DB = {
    "東京": {"city": "東京", "temp_c": 18, "humidity": 55, "weather": "晴れ", "wind": 3.2, "icon": "☀️"},
    "大阪": {"city": "大阪", "temp_c": 17, "humidity": 60, "weather": "曇り", "wind": 2.8, "icon": "☁️"},
    "名古屋": {"city": "名古屋", "temp_c": 16, "humidity": 58, "weather": "晴れ", "wind": 2.5, "icon": "☀️"},
    "札幌": {"city": "札幌", "temp_c": 8, "humidity": 65, "weather": "雪", "wind": 4.1, "icon": "❄️"},
    "福岡": {"city": "福岡", "temp_c": 19, "humidity": 62, "weather": "晴れ", "wind": 3.0, "icon": "☀️"},
    "那覇": {"city": "那覇", "temp_c": 24, "humidity": 72, "weather": "曇り", "wind": 5.5, "icon": "☁️"},
    "仙台": {"city": "仙台", "temp_c": 12, "humidity": 50, "weather": "晴れ", "wind": 2.2, "icon": "☀️"},
    "京都": {"city": "京都", "temp_c": 16, "humidity": 55, "weather": "晴れ", "wind": 1.8, "icon": "☀️"},
    "ニューヨーク": {"city": "ニューヨーク", "temp_c": 12, "humidity": 48, "weather": "晴れ", "wind": 4.5, "icon": "☀️"},
    "ロンドン": {"city": "ロンドン", "temp_c": 10, "humidity": 70, "weather": "雨", "wind": 5.2, "icon": "🌧️"},
    "パリ": {"city": "パリ", "temp_c": 14, "humidity": 55, "weather": "曇り", "wind": 3.1, "icon": "☁️"},
    "シドニー": {"city": "シドニー", "temp_c": 22, "humidity": 60, "weather": "晴れ", "wind": 3.8, "icon": "☀️"},
    "ソウル": {"city": "ソウル", "temp_c": 13, "humidity": 45, "weather": "晴れ", "wind": 2.9, "icon": "☀️"},
    "バンコク": {"city": "バンコク", "temp_c": 34, "humidity": 80, "weather": "雷雨", "wind": 2.0, "icon": "⛈️"},
    "ドバイ": {"city": "ドバイ", "temp_c": 32, "humidity": 40, "weather": "晴れ", "wind": 4.0, "icon": "☀️"},
}

parser = argparse.ArgumentParser(description="Retrieve weather forecast for a city.")
parser.add_argument("--city", type=str, required=True, help="City name (Japanese)")
args = parser.parse_args()

city = args.city.strip()
data = WEATHER_DB.get(city)

if data:
    result = {
        **data,
        "temp_f": round(data["temp_c"] * 9 / 5 + 32, 1),
        "report": f"{data['icon']} {data['city']}: {data['weather']} {data['temp_c']}°C (湿度{data['humidity']}%)",
    }
else:
    result = {
        "city": city,
        "error": f"都市 '{city}' のデータが見つかりません。",
        "available_cities": list(WEATHER_DB.keys()),
    }

print(json.dumps(result, ensure_ascii=False))

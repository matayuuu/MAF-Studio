---
name: weather-report
description: 都市別の天気データを参照し、温度変換や天気レポートを生成するスキル。
license: Apache-2.0
---

# Weather Report

天気に関する質問に回答するためのスキルです。

## Scripts

- `scripts/forecast.py` — 都市名を受け取り、参照データから天気予報 JSON を返します。
- `scripts/temp_convert.py` — 摂氏と華氏の間で温度を変換します。

## References

- `references/CITY_WEATHER_DATA.md` — 主要都市の天気データ（気温・湿度・天気）
- `references/WEATHER_ICONS.md` — 天気アイコンと状態コードの対応表

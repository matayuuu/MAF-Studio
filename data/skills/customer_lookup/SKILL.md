---
name: customer-lookup
description: Search for a customer by ID or name from customers.csv.
---

# Skill: customer_lookup

## 目的
顧客IDまたは氏名で顧客マスタ（customers.csv）を検索し、顧客の基本情報を取得する。

## エージェントが使う判断ルール
- 顧客IDが提供された場合は `lookup_by_id.py` を使用する
- 氏名のみの場合は `lookup_by_name.py` を使用する（追加情報は聞かずにそのまま実行する）
- 顧客が見つからない場合のみ「お客様情報が見つかりません」と案内する

## 業務上の暗黙知
- 顧客IDは「C」+数字3桁の形式（例: C001）
- 担当者名（assigned_agent）は参考情報として提示する
- 個人情報のため、検索結果は必要最小限の項目のみ表示する

## 使用するスクリプト
- `scripts/lookup_by_id.py` — 顧客IDによる検索（引数: `customer_id`）
- `scripts/lookup_by_name.py` — 氏名による検索（引数: `last_name` 必須, `first_name` 任意）
  - 氏名は必ず姓と名に分けて渡す。例: `{"last_name": "田中", "first_name": "健太"}`
  - 氏名をまとめて `name` で渡すのは誤り

## 使用するデータ
- `demo_app/data/customers.csv`

---
name: customer-profile-summary
description: 契約情報・活動履歴を含む顧客の統合プロファイルを生成する。
---

# Skill: customer_profile_summary

## 目的
顧客IDをもとに、顧客の基本情報・契約情報・対応履歴を統合し、担当エージェントが全体像を把握できるサマリーを生成する。

## エージェントが使う判断ルール
- 顧客IDで呼び出し、顧客の基本情報・契約情報・対応履歴を把握する
- 契約情報（contracts.csv）から有効契約を抽出し商品名も付与する
- 最新の対応履歴（activities.csv）から直近3件を表示する

## 業務上の暗黙知
- 年収1,000万円以上 → 富裕層フラグ（法人保険・高額保障の提案余地あり）
- 60歳以上・職業「退職者」→ リタイア層（年金・介護保険の提案余地あり）

## 使用するスクリプト
- `scripts/profile_summary.py` — 統合サマリー生成（引数: `customer_id` 必須）
  - 例: `{"customer_id": "C016"}`

## 使用するデータ
- `demo_app/data/customers.csv`
- `demo_app/data/contracts.csv`
- `demo_app/data/products.csv`
- `demo_app/data/activities.csv`

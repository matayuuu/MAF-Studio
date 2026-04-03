---
name: auto-insurance-contract-create
description: Register a new auto insurance contract in contracts.csv.
---

# Skill: auto_insurance_contract_create

## 目的
顧客が選択した自動車保険プランで新規契約を contracts.csv に登録する。

## エージェントが使う判断ルール
- 契約前に必ず内容（プラン・保険料・開始日）をお客様に口頭確認してから登録する
- 開始日は「今日以降の日付」のみ有効
- 支払方法は「口座振替」または「クレジットカード」から選択（デフォルト: 口座振替）
- 登録後に contract_id を伝え、activity_log_writer で契約内容を活動履歴に記録する

## 業務上の暗黙知
- 納車日が決まっている場合は開始日を納車日に合わせる
- 被保険者名は原則お客様本人だが、家族名義も可能

## 使用するスクリプト
- `scripts/create_contract.py` — 新規契約の登録

## 使用するデータ
- `demo_app/data/contracts.csv`
- `demo_app/data/products.csv`

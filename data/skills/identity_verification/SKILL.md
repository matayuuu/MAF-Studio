---
name: identity-verification
description: Verify customer identity by confirming the customer ID exists in the database.
---

# Skill: identity_verification

## 目的
顧客IDの存在を確認し、本人確認を行う。必ずこのSkillで確認を実施すること。

## エージェントが使う判断ルール
- 顧客IDが存在した場合のみ「本人確認完了」とする
- 存在しない場合は「お客様情報が確認できません」と案内し、再度IDを確認する
- 本人確認完了後、フルネームを読み上げてお客様に確認する

## 業務上の暗黙知
- 本人確認は全ての操作（解約・変更含む）の前提条件

## 使用するスクリプト
- `scripts/verify_identity.py` — 顧客IDの照合（引数: `customer_id`）

## 使用するデータ
- `demo_app/data/customers.csv`

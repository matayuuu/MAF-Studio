---
name: customer-support
description: 顧客対応のエスカレーション基準・SLA・対応テンプレート・過去事例を集約し、正確で一貫した顧客サポートを実現するスキル。
license: Apache-2.0
---

# 顧客サポートアシスタント

顧客からの問い合わせ対応を支援します。社内の対応ルール・SLA・過去事例に基づき、適切な回答とエスカレーション判断を行います。

## Scripts

- `scripts/classify.py` — 問い合わせ内容を分類し、優先度・対応SLA・担当チームを判定します。
- `scripts/sla_check.py` — 受付日時から対応期限を計算し、SLA遵守状況を確認します。

## References

- `references/ESCALATION_RULES.md` — エスカレーション基準と判断フロー
- `references/RESPONSE_TEMPLATES.md` — 状況別の定型応答テンプレート
- `references/KNOWN_ISSUES.md` — 既知の障害・FAQ・ワークアラウンド一覧

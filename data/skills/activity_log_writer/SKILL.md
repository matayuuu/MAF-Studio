---
name: activity-log-writer
description: Write a customer service activity record to activities.csv.
---

# Skill: activity_log_writer

## 目的
顧客対応の結果を activities.csv に記録する。対応終了時に必ず呼び出すこと。

## エージェントが使う判断ルール
- 対応完了時（契約・解約・提案・ヒアリング問わず）に必ず記録する
- 次回アクション（next_action）と次回アクション日（next_action_date）も必ず記入する
- 結果（outcome）は以下から選択: 契約完了/解約完了/要フォロー/提案済み/情報提供/継続フォロー/対応不要

## 業務上の暗黙知
- activity_typeは「電話」「訪問」「チャット」「システム」から選択
- agent_nameは対応エージェント名（例: FrontAgent, AutoInsuranceAgent）
- contentには会話の要点と結論を簡潔に記入する

## 使用するスクリプト
- `scripts/write_activity.py` — 活動履歴の追記

## 使用するデータ
- `demo_app/data/activities.csv`

---
name: life-insurance-contract-cancel
description: 既存の生命保険契約を解約する。解約前に代替プランの提案も行う。
---

# life_insurance_contract_cancel

生命保険の既存契約を解約するスキル。

## 概要
有効な生命保険契約を解約処理する。解約前に補償内容の確認と代替案の提示を必ず行う。

## 入力パラメータ
- `customer_id` (str): 顧客ID
- `contract_id` (str): 解約対象の契約ID（例: CT008）
- `reason` (str): 解約理由（例: 保険料負担、補償見直し、その他）

## 出力
- `status`: `success` / `error`
- `message`: 処理結果メッセージ
- `contract_id`: 契約ID
- `product_name`: 解約した商品名
- `cancel_date`: 解約日

## 使用スクリプト
- `scripts/cancel_contract.py`

## 関連スキル
- `life_insurance_recommendation`: 解約前に代替プランを提示すること
- `activity_log_writer`: 解約完了後にアクティビティを記録

## 注意
- 引き継ぎコンテキストに customer_id / contract_id が含まれている場合は、そのまま使用する（顧客に再確認しない）

## 注意事項
- 解約はエージェントが単独で判断せず、必ず顧客の意思確認を行うこと
- 解約前に「補償の見直しで保険料を下げる方法がある」旨を案内する（解約防止）
- 解約後の返戻金は概算を案内（詳細は書面確認を促す）
- 自動車保険との同時解約の場合は無保険リスクを説明すること

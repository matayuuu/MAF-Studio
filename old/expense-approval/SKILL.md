---
name: expense-approval
description: 社内の経費精算ルール・承認フロー・勘定科目の暗黙知をもとに、経費申請の妥当性チェックと承認ルート判定を行うスキル。
license: Apache-2.0
---

# 経費精算アシスタント

経費精算に関する質問や申請内容の妥当性確認を支援します。

## Scripts

- `scripts/validate.py` — 経費の金額・カテゴリ・出張先から、承認ルート・必要添付書類・注意事項を判定します。
- `scripts/calc_per_diem.py` — 出張先と日数から日当・宿泊費の上限額を自動計算します。

## References

- `references/APPROVAL_RULES.md` — 金額別の承認フロー、特別承認が必要なケース
- `references/EXPENSE_CATEGORIES.md` — 勘定科目・経費カテゴリの一覧と注意事項
- `references/TRAVEL_POLICY.md` — 出張旅費規程（日当・宿泊費・交通費の上限）

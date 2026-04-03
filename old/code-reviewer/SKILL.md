---
name: code-reviewer
description: コードの品質チェックとレビューコメント生成を行うスキル。ガイドラインに従ったレビューを支援します。
license: Apache-2.0
---

# Code Reviewer

コードレビューを支援するスキルです。ガイドラインに従い、品質チェックやレビューコメントを生成します。

## Scripts

- `scripts/analyze.py` — Python コードファイルまたはコード文字列を静的解析し、問題点を JSON で返します。
- `scripts/complexity.py` — コードの行数・関数数・複雑度を計測します。

## References

- `references/REVIEW_GUIDELINES.md` — コードレビューのチェックリストとベストプラクティス
- `references/NAMING_CONVENTIONS.md` — 命名規則ガイド

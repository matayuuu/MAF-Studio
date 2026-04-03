---
name: text-analyzer
description: テキストの形態素解析風処理、文字数カウント、キーワード抽出、要約スコアリングを行うスキル。
license: Apache-2.0
---

# Text Analyzer

テキスト分析タスクを支援するスキルです。文字数・単語数カウント、キーワード抽出、読みやすさスコアの計算を行います。

## Scripts

- `scripts/count.py` — テキストの文字数、単語数、文数、段落数を JSON で返します。
- `scripts/keywords.py` — テキストからキーワードを抽出し、出現頻度とともに返します。

## References

- `references/STOPWORDS_JA.md` — 日本語ストップワード一覧（キーワード抽出時に除外）
- `references/READABILITY_GUIDE.md` — 読みやすさスコアの基準と改善ガイド

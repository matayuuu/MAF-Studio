from __future__ import annotations

import argparse
import json
import re
import unicodedata


def count_text(text: str) -> dict:
    """Count characters, words, sentences, and paragraphs in text."""
    # Character counts
    total_chars = len(text)
    chars_no_space = len(text.replace(" ", "").replace("\u3000", ""))

    # Paragraphs (split by blank lines)
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]

    # Sentences (split by Japanese/English sentence endings)
    sentences = [s.strip() for s in re.split(r'[。！？!?.]+', text) if s.strip()]

    # Words (rough: split by spaces for English, count CJK chars individually)
    cjk_chars = sum(1 for c in text if unicodedata.category(c).startswith('Lo'))
    ascii_words = len(re.findall(r'[a-zA-Z]+', text))
    word_count = cjk_chars + ascii_words

    # Kanji ratio
    kanji_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    kanji_ratio = round(kanji_count / chars_no_space * 100, 1) if chars_no_space else 0

    # Readability score (simplified)
    avg_sentence_len = chars_no_space / max(len(sentences), 1)
    score = max(0, min(100, round(100 - (avg_sentence_len - 40) * 1.5 - abs(kanji_ratio - 30) * 0.5)))

    return {
        "characters": total_chars,
        "characters_no_space": chars_no_space,
        "words": word_count,
        "sentences": len(sentences),
        "paragraphs": len(paragraphs),
        "kanji_ratio": f"{kanji_ratio}%",
        "avg_sentence_length": round(avg_sentence_len, 1),
        "readability_score": score,
    }


parser = argparse.ArgumentParser(description="Count text metrics.")
parser.add_argument("--text", type=str, required=True, help="Text to analyze")
args = parser.parse_args()

result = count_text(args.text)
print(json.dumps(result, ensure_ascii=False, indent=2))

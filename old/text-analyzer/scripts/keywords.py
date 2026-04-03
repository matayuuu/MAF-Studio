from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter

# Japanese stopwords
STOPWORDS = set(
    "は が の を に へ と で も や か から まで より ので のに けど けれど "
    "です ます ました でした ません ない ある いる れる られる せる させる "
    "そして しかし また さらに ただし なお つまり すなわち ところで 一方 "
    "これ それ あれ この その あの ここ そこ あそこ "
    "とても 非常に かなり 少し もう まだ すでに ぜひ たぶん おそらく "
    "こと もの ため ところ よう わけ はず つもり "
    "する した して する される された なる なった いう いった".split()
)


def extract_keywords(text: str, top_n: int = 10) -> dict:
    """Extract keywords from text using simple character n-gram approach."""
    # Extract CJK character bigrams and trigrams as candidate keywords
    candidates: list[str] = []

    # Extract ASCII words
    for word in re.findall(r'[a-zA-Z]{2,}', text):
        candidates.append(word.lower())

    # Extract CJK bigrams/trigrams
    cjk_chars = [c for c in text if unicodedata.category(c).startswith('Lo')]
    for i in range(len(cjk_chars) - 1):
        bigram = cjk_chars[i] + cjk_chars[i + 1]
        if bigram not in STOPWORDS:
            candidates.append(bigram)
    for i in range(len(cjk_chars) - 2):
        trigram = cjk_chars[i] + cjk_chars[i + 1] + cjk_chars[i + 2]
        if trigram not in STOPWORDS:
            candidates.append(trigram)

    # Count and rank
    counter = Counter(candidates)
    # Filter out single-occurrence items
    keywords = [
        {"keyword": word, "count": count}
        for word, count in counter.most_common(top_n)
        if count >= 2
    ]

    return {
        "total_candidates": len(candidates),
        "unique_candidates": len(counter),
        "top_keywords": keywords,
    }


parser = argparse.ArgumentParser(description="Extract keywords from text.")
parser.add_argument("--text", type=str, required=True, help="Text to analyze")
parser.add_argument("--top", type=int, default=10, help="Number of top keywords to return")
args = parser.parse_args()

result = extract_keywords(args.text, args.top)
print(json.dumps(result, ensure_ascii=False, indent=2))

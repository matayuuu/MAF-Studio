from __future__ import annotations

import argparse
import json


parser = argparse.ArgumentParser(description="Multiply a value by a factor and return JSON.")
parser.add_argument("--value", type=float, required=True)
parser.add_argument("--factor", type=float, required=True)
args = parser.parse_args()

result = {
    "value": args.value,
    "factor": args.factor,
    "result": round(args.value * args.factor, 4),
}
print(json.dumps(result, ensure_ascii=False))

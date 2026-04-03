from __future__ import annotations

import argparse
import json

parser = argparse.ArgumentParser(description="Convert between Celsius and Fahrenheit.")
parser.add_argument("--value", type=float, required=True, help="Temperature value")
parser.add_argument("--to", type=str, choices=["celsius", "fahrenheit"], default="celsius",
                    help="Target unit: celsius or fahrenheit")
args = parser.parse_args()

if args.to == "celsius":
    converted = round((args.value - 32) * 5 / 9, 2)
    result = {
        "input": f"{args.value}°F",
        "output": f"{converted}°C",
        "value": converted,
        "unit": "celsius",
    }
else:
    converted = round(args.value * 9 / 5 + 32, 2)
    result = {
        "input": f"{args.value}°C",
        "output": f"{converted}°F",
        "value": converted,
        "unit": "fahrenheit",
    }

print(json.dumps(result, ensure_ascii=False))

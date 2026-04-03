from __future__ import annotations

import argparse
import json
import re


def measure_complexity(code: str) -> dict:
    """Measure basic code metrics."""
    lines = code.splitlines()
    total_lines = len(lines)
    blank_lines = sum(1 for line in lines if not line.strip())
    comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
    code_lines = total_lines - blank_lines - comment_lines

    functions = []
    classes = []
    max_indent = 0

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("def "):
            name = re.match(r'def\s+(\w+)', stripped)
            functions.append({"name": name.group(1) if name else "?", "line": i})
        elif stripped.startswith("class "):
            name = re.match(r'class\s+(\w+)', stripped)
            classes.append({"name": name.group(1) if name else "?", "line": i})

        indent = len(line) - len(line.lstrip()) if line.strip() else 0
        max_indent = max(max_indent, indent)

    nesting_depth = max_indent // 4  # Assuming 4-space indent

    # Simple complexity rating
    if len(functions) <= 5 and nesting_depth <= 3 and code_lines <= 100:
        rating = "Low"
    elif len(functions) <= 15 and nesting_depth <= 5 and code_lines <= 300:
        rating = "Medium"
    else:
        rating = "High"

    return {
        "metrics": {
            "total_lines": total_lines,
            "code_lines": code_lines,
            "blank_lines": blank_lines,
            "comment_lines": comment_lines,
            "functions": len(functions),
            "classes": len(classes),
            "max_nesting_depth": nesting_depth,
        },
        "complexity_rating": rating,
        "functions": functions,
        "classes": classes,
    }


parser = argparse.ArgumentParser(description="Measure code complexity metrics.")
parser.add_argument("--code", type=str, required=True, help="Python code string to measure")
args = parser.parse_args()

result = measure_complexity(args.code)
print(json.dumps(result, ensure_ascii=False, indent=2))

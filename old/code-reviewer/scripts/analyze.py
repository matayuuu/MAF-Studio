from __future__ import annotations

import argparse
import json
import re
import sys


def analyze_code(code: str) -> dict:
    """Perform basic static analysis on Python code."""
    issues = []
    lines = code.splitlines()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Check for hardcoded secrets
        if re.search(r'(api_key|password|secret|token)\s*=\s*["\'][^"\']+["\']', stripped, re.IGNORECASE):
            issues.append({"line": i, "severity": "MUST", "message": "機密情報がハードコードされています", "category": "security"})

        # Check for bare except
        if stripped == "except:" or stripped.startswith("except: "):
            issues.append({"line": i, "severity": "MUST", "message": "ベア except は避けてください。具体的な例外型を指定してください", "category": "error-handling"})

        # Check for eval/exec
        if re.search(r'\b(eval|exec)\s*\(', stripped):
            issues.append({"line": i, "severity": "MUST", "message": f"eval/exec の使用はセキュリティリスクです", "category": "security"})

        # Check long lines
        if len(line) > 120:
            issues.append({"line": i, "severity": "NIT", "message": f"行が長すぎます ({len(line)}文字 > 120文字)", "category": "readability"})

        # Check TODO/FIXME
        if re.search(r'\b(TODO|FIXME|HACK|XXX)\b', stripped):
            issues.append({"line": i, "severity": "SHOULD", "message": "未解決の TODO/FIXME があります", "category": "maintainability"})

        # Check for print statements (should use logging)
        if re.search(r'\bprint\s*\(', stripped) and not stripped.startswith('#'):
            issues.append({"line": i, "severity": "SHOULD", "message": "print() ではなく logging モジュールの使用を推奨します", "category": "best-practice"})

    # Check for missing docstring
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("def ") or stripped.startswith("class "):
            next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
            if not next_line.startswith('"""') and not next_line.startswith("'''"):
                issues.append({"line": i + 1, "severity": "NIT", "message": f"docstring がありません: {stripped[:50]}", "category": "readability"})

    summary = {
        "total_issues": len(issues),
        "by_severity": {
            "MUST": len([i for i in issues if i["severity"] == "MUST"]),
            "SHOULD": len([i for i in issues if i["severity"] == "SHOULD"]),
            "NIT": len([i for i in issues if i["severity"] == "NIT"]),
        },
        "issues": issues,
    }
    return summary


parser = argparse.ArgumentParser(description="Analyze Python code for common issues.")
parser.add_argument("--code", type=str, required=True, help="Python code string to analyze")
args = parser.parse_args()

result = analyze_code(args.code)
print(json.dumps(result, ensure_ascii=False, indent=2))

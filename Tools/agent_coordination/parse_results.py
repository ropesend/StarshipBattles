"""Parse the ## Results section from a completed request file.

Only supports Option B format (## Results section). Rejects legacy flat-field
files (no ## Results heading). Prints fields as JSON to stdout.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def parse_results(path: Path) -> dict[str, str]:
    """Extract fields from the ## Results section. Adds review_dir derived from Report."""
    content = path.read_text(encoding="utf-8")
    m = re.search(r"\n## Results\b(.*?)(?:\n## |\Z)", content, re.DOTALL)
    if not m:
        return {}
    section = m.group(1)
    fields: dict[str, str] = {}
    for fm in re.finditer(r"\*\*(.+?):\*\*\s*(.+)", section):
        fields[fm.group(1)] = fm.group(2).strip()
    # Derive review_dir from Report path's parent directory
    if "Report" in fields:
        report_path = Path(fields["Report"])
        fields["review_dir"] = str(report_path.parent).replace("\\", "/")
    return fields


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: parse_results.py <request_file>", file=sys.stderr)
        return 1
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 1
    content = path.read_text(encoding="utf-8")
    if "## Results" not in content:
        print("No ## Results section found. Only Option B format is supported.", file=sys.stderr)
        return 2
    fields = parse_results(path)
    if not fields:
        print("No fields found in ## Results section", file=sys.stderr)
        return 1
    print(json.dumps(fields, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

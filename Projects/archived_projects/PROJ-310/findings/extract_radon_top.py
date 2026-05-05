"""Extract top-20 by cyclomatic complexity from radon output."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
raw = (HERE / "radon_complexity.txt").read_text(encoding="utf-8")
lines = raw.splitlines()
# Find first non-Exit line that is JSON
for i, line in enumerate(lines):
    if line.strip().startswith("{"):
        data = json.loads(line)
        break

items = []
for fname, blocks in data.items():
    for b in blocks:
        if b.get("type") in ("function", "method"):
            items.append((b["complexity"], fname.replace("\\", "/"),
                          b.get("classname", ""), b["name"]))

items.sort(reverse=True)
out_lines = ["Top 30 by cyclomatic complexity (radon cc):", ""]
for c, f, cls, n in items[:30]:
    full = f"{cls}.{n}" if cls else n
    out_lines.append(f"cc={c:>3}  {f}::{full}")
(HERE / "radon_top30.txt").write_text("\n".join(out_lines) + "\n", encoding="utf-8")
print("\n".join(out_lines))

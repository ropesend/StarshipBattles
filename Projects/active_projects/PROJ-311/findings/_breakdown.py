"""Quick subdir breakdown of game/ui/ from the audit CSV."""
from __future__ import annotations
import csv
from collections import defaultdict
from pathlib import Path

INV = Path(__file__).parent / "inventory.csv"

ui_bucket: dict[str, dict[str, int]] = defaultdict(lambda: {"tot": 0, "unann": 0})
other_bucket: dict[str, dict[str, int]] = defaultdict(lambda: {"tot": 0, "unann": 0})

with INV.open(encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["is_dunder"] == "true":
            continue
        path = row["file"].replace("\\", "/")
        if path.startswith("game/ui/"):
            rest = path[len("game/ui/"):]
            if "/" not in rest:
                key = "game/ui/<top-level>"
            else:
                first = rest.split("/", 1)[0]
                key = f"game/ui/{first}/"
            ui_bucket[key]["tot"] += 1
            if row["has_return_annotation"] == "false":
                ui_bucket[key]["unann"] += 1
        else:
            # 'other' bucket detail (everything not under the 5 known subsystems)
            for prefix in (
                "game/core/",
                "game/ai/",
                "game/simulation/",
                "game/strategy/",
                "game/ui/",
            ):
                if path.startswith(prefix):
                    break
            else:
                # actually 'other'
                if "/" in path[len("game/"):]:
                    first = path[len("game/"):].split("/", 1)[0]
                    key = f"game/{first}/"
                else:
                    key = "game/<top-level>"
                other_bucket[key]["tot"] += 1
                if row["has_return_annotation"] == "false":
                    other_bucket[key]["unann"] += 1

print("=== game/ui/ subdir breakdown (non-dunder) ===")
print(f'{"path":<40} {"total":>7} {"unann":>7} {"cov%":>7}')
for k in sorted(ui_bucket.keys()):
    b = ui_bucket[k]
    cov = (b["tot"] - b["unann"]) / b["tot"] * 100 if b["tot"] else 0.0
    print(f'{k:<40} {b["tot"]:>7} {b["unann"]:>7} {cov:>6.1f}%')

print()
print("=== 'other' bucket detail (non-dunder) ===")
print(f'{"path":<40} {"total":>7} {"unann":>7} {"cov%":>7}')
for k in sorted(other_bucket.keys()):
    b = other_bucket[k]
    cov = (b["tot"] - b["unann"]) / b["tot"] * 100 if b["tot"] else 0.0
    print(f'{k:<40} {b["tot"]:>7} {b["unann"]:>7} {cov:>6.1f}%')

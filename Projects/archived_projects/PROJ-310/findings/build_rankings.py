"""PROJ-310: Build top-30 rankings from nesting_metrics.csv.

Outputs:
    findings/top30_by_function.md   - top 30 functions by max_depth
    findings/top30_by_file.md       - top 30 files by sum(max(0, max_depth-3))
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "nesting_metrics.csv"


def main() -> None:
    rows: list[dict] = []
    with CSV_PATH.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            r["max_depth"] = int(r["max_depth"])
            r["visual_depth"] = int(r["visual_depth"])
            r["elif_run"] = int(r["elif_run"])
            r["total_loc"] = int(r["total_loc"])
            rows.append(r)

    # ---- top 30 by function (BY AST max_depth — captures elif-chain offenders) ----
    rows.sort(key=lambda r: (-r["max_depth"], -r["total_loc"]))
    top_func = rows[:30]
    with (HERE / "top30_by_function.md").open("w", encoding="utf-8") as fh:
        fh.write("# Top 30 Functions by max_depth\n\n")
        fh.write("Sorted by AST `max_depth` desc, then `total_loc` desc. "
                 "**`visual_depth`** treats `elif` chains as flat (this is the human-readable depth). "
                 "**`elif_run`** is the longest if/elif/.../elif run; high values here with high `max_depth` "
                 "and low `visual_depth` indicate dispatch ladders, not nested logic.\n\n")
        fh.write("| Rank | AST | Visual | elif_run | LOC | File | Function | Longest Ladder |\n")
        fh.write("|-----:|----:|-------:|---------:|----:|------|----------|----------------|\n")
        for i, r in enumerate(top_func, start=1):
            fh.write(
                f"| {i} | {r['max_depth']} | {r['visual_depth']} | {r['elif_run']} | "
                f"{r['total_loc']} | `{r['file']}` | `{r['function']}` | `{r['longest_ladder_kind']}` |\n"
            )

    # ---- top 30 by VISUAL depth (the genuinely-nested ones) ----
    rows.sort(key=lambda r: (-r["visual_depth"], -r["total_loc"]))
    top_visual = rows[:30]
    with (HERE / "top30_by_visual_depth.md").open("w", encoding="utf-8") as fh:
        fh.write("# Top 30 Functions by Visual Depth\n\n")
        fh.write("Sorted by `visual_depth` descending. This metric ignores elif-chain artifacts "
                 "and reflects how a human reads the code's indentation.\n\n")
        fh.write("| Rank | Visual | AST | elif_run | LOC | File | Function | Longest Ladder |\n")
        fh.write("|-----:|-------:|----:|---------:|----:|------|----------|----------------|\n")
        for i, r in enumerate(top_visual, start=1):
            fh.write(
                f"| {i} | {r['visual_depth']} | {r['max_depth']} | {r['elif_run']} | "
                f"{r['total_loc']} | `{r['file']}` | `{r['function']}` | `{r['longest_ladder_kind']}` |\n"
            )

    # ---- top 30 by file ----
    file_score: dict[str, dict] = defaultdict(
        lambda: {"score": 0, "deep_funcs": 0, "max_depth": 0}
    )
    for r in rows:
        if r["max_depth"] >= 4:
            f = file_score[r["file"]]
            f["score"] += r["max_depth"] - 3
            f["deep_funcs"] += 1
            f["max_depth"] = max(f["max_depth"], r["max_depth"])

    file_ranked = sorted(
        file_score.items(),
        key=lambda kv: (-kv[1]["score"], -kv[1]["max_depth"]),
    )[:30]

    with (HERE / "top30_by_file.md").open("w", encoding="utf-8") as fh:
        fh.write("# Top 30 Files by Aggregate Deep-Nesting Score\n\n")
        fh.write("Score = sum of `max(0, max_depth - 3)` across functions in the file.\n\n")
        fh.write("| Rank | Score | # Deep Funcs | Worst Depth | File |\n")
        fh.write("|-----:|------:|-------------:|------------:|------|\n")
        for i, (fname, data) in enumerate(file_ranked, start=1):
            fh.write(
                f"| {i} | {data['score']} | {data['deep_funcs']} | "
                f"{data['max_depth']} | `{fname}` |\n"
            )

    # ---- distribution histogram (also dump for the review) ----
    from collections import Counter
    hist = Counter(r["max_depth"] for r in rows)
    print("Wrote top30_by_function.md and top30_by_file.md")
    print("Depth histogram:")
    for d in sorted(hist):
        print(f"  depth={d:>2}  count={hist[d]}")


if __name__ == "__main__":
    main()

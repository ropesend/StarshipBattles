"""Return-type annotation audit for game/.

Walks game/**/*.py (skipping tests/), records every FunctionDef and
AsyncFunctionDef and whether it carries a return-type annotation
(node.returns is not None). Emits a CSV inventory and a summary
breakdown by subsystem.

Output (when --csv is passed):
    file,function,has_return_annotation,is_dunder,is_public

Console output: totals, non-dunder coverage %, per-subsystem breakdown.

Usage:
    python annotation_audit.py [--root <repo-root>] [--csv <path>]

If --root is omitted, the repo root is inferred by walking up from this
script's location until a directory containing 'game' is found.

This script is read-only — it does NOT modify any source code.
"""

from __future__ import annotations

import argparse
import ast
import csv
import sys
from collections import defaultdict
from pathlib import Path


# Subsystem buckets we care about. Anything else falls into "other".
SUBSYSTEMS: tuple[str, ...] = (
    "game/core/",
    "game/ai/",
    "game/simulation/",
    "game/strategy/",
    "game/ui/",
)


def find_repo_root(start: Path) -> Path:
    """Walk upward from `start` until a directory containing 'game/' is found."""
    cur = start.resolve()
    for candidate in (cur, *cur.parents):
        if (candidate / "game").is_dir():
            return candidate
    raise SystemExit(
        f"Could not locate repo root (no 'game/' dir) starting from {start}"
    )


def is_dunder(name: str) -> bool:
    """True for names like __init__, __str__, etc."""
    return name.startswith("__") and name.endswith("__") and len(name) > 4


def is_public(name: str) -> bool:
    """Public = does not start with underscore. Dunders count as not-public-API for our purposes."""
    return not name.startswith("_")


class _FunctionRecord:
    __slots__ = (
        "rel_path",
        "qualified_name",
        "has_return_annotation",
        "is_dunder",
        "is_public",
    )

    def __init__(
        self,
        rel_path: str,
        qualified_name: str,
        has_return_annotation: bool,
        dunder: bool,
        public: bool,
    ) -> None:
        self.rel_path = rel_path
        self.qualified_name = qualified_name
        self.has_return_annotation = has_return_annotation
        self.is_dunder = dunder
        self.is_public = public


def _qualified_name(node: ast.AST, class_stack: list[str]) -> str:
    """Build a name like 'MyClass.foo' or 'MyClass.Inner.bar' for methods, else just 'foo'."""
    func_name = getattr(node, "name", "<anon>")
    if class_stack:
        return ".".join(class_stack) + "." + func_name
    return func_name


def collect_functions(tree: ast.AST, rel_path: str) -> list[_FunctionRecord]:
    """Return one record per FunctionDef/AsyncFunctionDef in the tree.

    Tracks class context so methods get qualified names. Uses ast.walk-equivalent
    behavior but with manual recursion so we can maintain class_stack.
    """
    records: list[_FunctionRecord] = []

    def visit(node: ast.AST, class_stack: list[str]) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            qname = _qualified_name(node, class_stack)
            simple_name = node.name
            records.append(
                _FunctionRecord(
                    rel_path=rel_path,
                    qualified_name=qname,
                    has_return_annotation=node.returns is not None,
                    dunder=is_dunder(simple_name),
                    public=is_public(simple_name),
                )
            )
            # Recurse into nested defs (e.g., closures, nested classes inside methods).
            for child in ast.iter_child_nodes(node):
                visit(child, class_stack)
            return

        if isinstance(node, ast.ClassDef):
            new_stack = class_stack + [node.name]
            for child in ast.iter_child_nodes(node):
                visit(child, new_stack)
            return

        for child in ast.iter_child_nodes(node):
            visit(child, class_stack)

    visit(tree, [])
    return records


def audit_directory(root: Path) -> list[_FunctionRecord]:
    """Walk root/game/**/*.py and return all function records."""
    game_dir = root / "game"
    if not game_dir.is_dir():
        raise SystemExit(f"No game/ directory under {root}")

    records: list[_FunctionRecord] = []
    for py_file in sorted(game_dir.rglob("*.py")):
        # Skip pycache or any vendored/build trees if present.
        if "__pycache__" in py_file.parts:
            continue
        rel = py_file.relative_to(root).as_posix()
        try:
            source = py_file.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            print(f"WARN: skipping {rel} (encoding issue: {exc})", file=sys.stderr)
            continue
        try:
            tree = ast.parse(source, filename=str(py_file))
        except SyntaxError as exc:
            print(f"WARN: skipping {rel} (syntax error: {exc})", file=sys.stderr)
            continue
        records.extend(collect_functions(tree, rel))
    return records


def subsystem_for(rel_path: str) -> str:
    """Return one of SUBSYSTEMS or 'other' (for things like game/__init__.py, game/context.py, etc.)."""
    rel = rel_path.replace("\\", "/")
    for prefix in SUBSYSTEMS:
        if rel.startswith(prefix):
            return prefix
    return "other"


def write_csv(records: list[_FunctionRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["file", "function", "has_return_annotation", "is_dunder", "is_public"]
        )
        for r in records:
            writer.writerow(
                [
                    r.rel_path,
                    r.qualified_name,
                    "true" if r.has_return_annotation else "false",
                    "true" if r.is_dunder else "false",
                    "true" if r.is_public else "false",
                ]
            )


def write_unannotated_csv(records: list[_FunctionRecord], path: Path) -> None:
    """Same shape as write_csv but only the unannotated, non-dunder rows.

    These are the functions Phase 3 needs to backfill.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["file", "function", "has_return_annotation", "is_dunder", "is_public"]
        )
        for r in records:
            if r.is_dunder:
                continue
            if r.has_return_annotation:
                continue
            writer.writerow(
                [
                    r.rel_path,
                    r.qualified_name,
                    "false",
                    "false",
                    "true" if r.is_public else "false",
                ]
            )


def summarize(records: list[_FunctionRecord]) -> dict[str, object]:
    """Compute totals and per-subsystem stats. Non-dunder is the denominator for coverage."""
    total = len(records)
    dunders = sum(1 for r in records if r.is_dunder)
    non_dunder = total - dunders
    annotated_nd = sum(
        1 for r in records if r.has_return_annotation and not r.is_dunder
    )
    unannotated_nd = non_dunder - annotated_nd

    per_subsystem: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "total": 0,
            "dunder": 0,
            "non_dunder": 0,
            "annotated_nd": 0,
            "unannotated_nd": 0,
        }
    )
    for r in records:
        sub = subsystem_for(r.rel_path)
        bucket = per_subsystem[sub]
        bucket["total"] += 1
        if r.is_dunder:
            bucket["dunder"] += 1
        else:
            bucket["non_dunder"] += 1
            if r.has_return_annotation:
                bucket["annotated_nd"] += 1
            else:
                bucket["unannotated_nd"] += 1

    return {
        "total": total,
        "dunders": dunders,
        "non_dunder": non_dunder,
        "annotated_nd": annotated_nd,
        "unannotated_nd": unannotated_nd,
        "coverage_pct": (annotated_nd / non_dunder * 100.0) if non_dunder else 0.0,
        "per_subsystem": dict(per_subsystem),
    }


def print_summary(summary: dict[str, object]) -> None:
    print("=== Annotation Audit (game/) ===")
    print(f"  Total functions:          {summary['total']}")
    print(f"  Dunder methods:           {summary['dunders']}")
    print(f"  Non-dunder functions:     {summary['non_dunder']}")
    print(f"  Annotated (non-dunder):   {summary['annotated_nd']}")
    print(f"  Unannotated (non-dunder): {summary['unannotated_nd']}")
    print(f"  Coverage (non-dunder):    {summary['coverage_pct']:.2f}%")
    print()
    print("=== Per-subsystem breakdown ===")
    print(
        f"  {'subsystem':<22} {'total':>7} {'non-d':>7} {'annot':>7} {'unann':>7} {'cov%':>7}"
    )
    per = summary["per_subsystem"]
    assert isinstance(per, dict)
    # Stable ordering: known subsystems in declared order, then 'other'.
    ordered_keys = list(SUBSYSTEMS) + ["other"]
    for key in ordered_keys:
        if key not in per:
            continue
        b = per[key]
        nd = b["non_dunder"]
        cov = (b["annotated_nd"] / nd * 100.0) if nd else 0.0
        print(
            f"  {key:<22} {b['total']:>7} {nd:>7} {b['annotated_nd']:>7} {b['unannotated_nd']:>7} {cov:>6.2f}%"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repo root (defaults to auto-detected).",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=None,
        help="If given, write the full inventory CSV to this path.",
    )
    parser.add_argument(
        "--unannotated-csv",
        type=Path,
        default=None,
        help="If given, write only unannotated non-dunder rows to this path.",
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=None,
        help="Audit a single file instead of all of game/. Useful for self-test.",
    )
    args = parser.parse_args()

    if args.file is not None:
        single = args.file.resolve()
        if not single.is_file():
            raise SystemExit(f"--file path does not exist: {single}")
        # We still need a "root" so rel paths look sane.
        root = find_repo_root(single)
        rel = single.relative_to(root).as_posix()
        source = single.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(single))
        records = collect_functions(tree, rel)
    else:
        root = args.root.resolve() if args.root else find_repo_root(Path(__file__))
        records = audit_directory(root)

    if args.csv:
        write_csv(records, args.csv)
        print(f"Wrote full inventory CSV: {args.csv}")
    if args.unannotated_csv:
        write_unannotated_csv(records, args.unannotated_csv)
        print(f"Wrote unannotated CSV:    {args.unannotated_csv}")

    summary = summarize(records)
    print_summary(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

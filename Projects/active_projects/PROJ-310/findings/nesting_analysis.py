"""PROJ-310: AST-based deep-nesting analysis tool.

Walks game/**/*.py (skipping tests/), parses each file, and for every
FunctionDef / AsyncFunctionDef computes:
    max_depth        - deepest control-flow + def + class nesting depth
                       (counts If, For, While, Try, With, FunctionDef,
                       AsyncFunctionDef, ClassDef nodes on the deepest
                       path inside the function body)
    total_loc        - body line count (last_lineno - first_lineno + 1)
    longest_ladder   - kinds of nodes in the deepest chain joined by '->'

Outputs:
    findings/nesting_metrics.csv

Run as a module/script from repo root:
    python Projects/active_projects/PROJ-310/findings/nesting_analysis.py
"""
from __future__ import annotations

import ast
import csv
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, List, Tuple

# Node kinds counted as "one level deeper" relative to the function root.
# We deliberately count ClassDef + nested FunctionDef so that a method
# inside a class inside a function still scores correctly, but the per-
# *function* row reports the depth WITHIN the function body, treating
# any nested class/def as adding to the path. Top-level FunctionDef is
# the analysis root and is NOT counted as +1.
NESTING_KINDS = (
    ast.If,
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.Try,
    ast.With,
    ast.AsyncWith,
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.ClassDef,
)

# Short label used in the longest_ladder string.
def _kind_label(node: ast.AST) -> str:
    return {
        ast.If: "if",
        ast.For: "for",
        ast.AsyncFor: "afor",
        ast.While: "while",
        ast.Try: "try",
        ast.With: "with",
        ast.AsyncWith: "awith",
        ast.FunctionDef: "def",
        ast.AsyncFunctionDef: "adef",
        ast.ClassDef: "class",
    }.get(type(node), type(node).__name__)


def _deepest_path(stmts: Iterable[ast.AST]) -> List[ast.AST]:
    """Return the longest chain of nesting-kind nodes reachable from stmts.

    The chain represents one root-to-leaf path through nested control
    flow / definitions. Length of the returned list == max depth at this
    level.
    """
    best: List[ast.AST] = []
    for node in stmts:
        if not isinstance(node, NESTING_KINDS):
            # Walk into expression-level nodes? No -- only statements
            # contribute to nesting. But descend into compound stmts'
            # children when the parent itself wasn't a nesting kind
            # (e.g., ast.Module body holds these directly).
            continue
        # Collect the immediate child statement bodies.
        sub_chain = _walk_children(node)
        candidate = [node] + sub_chain
        if len(candidate) > len(best):
            best = candidate
    return best


def _walk_children(node: ast.AST) -> List[ast.AST]:
    """Inspect a nesting-kind node's child statement lists and recurse."""
    children: List[List[ast.AST]] = []

    if isinstance(node, ast.If):
        children.append(node.body)
        # NOTE: An `elif` is parsed as `If(orelse=[If(...)])`. We DO descend
        # into orelse so the metric reflects actual control-flow depth as
        # the AST sees it, but the elif-chain detector below distinguishes
        # this case from real visual nesting.
        children.append(node.orelse)
    elif isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
        children.append(node.body)
        children.append(node.orelse)
    elif isinstance(node, ast.Try):
        children.append(node.body)
        for handler in node.handlers:
            children.append(handler.body)
        children.append(node.orelse)
        children.append(node.finalbody)
    elif isinstance(node, (ast.With, ast.AsyncWith)):
        children.append(node.body)
    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        children.append(node.body)

    best: List[ast.AST] = []
    for branch in children:
        chain = _deepest_path(branch)
        if len(chain) > len(best):
            best = chain
    return best


def _visual_depth(stmts: Iterable[ast.AST], current: int = 0) -> int:
    """Return the deepest *visual* indent depth.

    Treats `elif` chains (an `If` whose orelse is a single `If`) as zero
    additional indent -- which is how Python actually renders them. This
    gives a metric that matches what a human reads.
    """
    best = current
    for node in stmts:
        if not isinstance(node, NESTING_KINDS):
            continue
        depth_here = current + 1
        # Recurse into bodies normally
        sub_branches: List[Iterable[ast.AST]] = []
        if isinstance(node, ast.If):
            sub_branches.append(node.body)
            # If orelse is exactly one If, treat as elif (no extra indent)
            if (
                len(node.orelse) == 1
                and isinstance(node.orelse[0], ast.If)
            ):
                # Walk the elif's body+orelse at the SAME depth_here
                elif_node = node.orelse[0]
                # Recurse manually keeping depth_here flat
                # (effectively unfolds the elif chain)
                # We synthesise a "virtual" branch that treats the elif's
                # body as a sibling.
                stack = [elif_node]
                while stack:
                    cur = stack.pop()
                    sub_branches.append(cur.body)
                    if (
                        len(cur.orelse) == 1
                        and isinstance(cur.orelse[0], ast.If)
                    ):
                        stack.append(cur.orelse[0])
                    else:
                        sub_branches.append(cur.orelse)
            else:
                sub_branches.append(node.orelse)
        elif isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
            sub_branches.append(node.body)
            sub_branches.append(node.orelse)
        elif isinstance(node, ast.Try):
            sub_branches.append(node.body)
            for h in node.handlers:
                sub_branches.append(h.body)
            sub_branches.append(node.orelse)
            sub_branches.append(node.finalbody)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            sub_branches.append(node.body)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            sub_branches.append(node.body)

        for branch in sub_branches:
            best = max(best, _visual_depth(branch, depth_here))
        if depth_here > best:
            best = depth_here
    return best


def _is_elif_chain(stmts: Iterable[ast.AST]) -> bool:
    """Return True if the deepest path is dominated by an elif chain.

    Heuristic: walk the deepest If chain through orelse links; if every
    link in the chain is `If(orelse=[If(...)])` for >=3 hops, it's an
    elif ladder.
    """
    # Find the longest elif run starting from any top-level If.
    max_run = 0
    for s in stmts:
        if isinstance(s, ast.If):
            run = 1
            cur = s
            while (
                len(cur.orelse) == 1
                and isinstance(cur.orelse[0], ast.If)
            ):
                run += 1
                cur = cur.orelse[0]
            max_run = max(max_run, run)
        # Also descend into other compound bodies in case the elif lives
        # inside them
        for child_attr in ("body", "orelse", "finalbody"):
            child = getattr(s, child_attr, None)
            if isinstance(child, list):
                max_run = max(max_run, _is_elif_chain_run(child))
    return max_run

def _is_elif_chain_run(stmts: Iterable[ast.AST]) -> int:
    max_run = 0
    for s in stmts:
        if isinstance(s, ast.If):
            run = 1
            cur = s
            while (
                len(cur.orelse) == 1
                and isinstance(cur.orelse[0], ast.If)
            ):
                run += 1
                cur = cur.orelse[0]
            max_run = max(max_run, run)
    return max_run


def analyze_function(func: ast.AST) -> Tuple[int, int, str, int, int]:
    """Return (max_depth, total_loc, longest_ladder_kind, visual_depth, elif_run).

    max_depth     - AST depth (counts every elif as +1; useful for raw signal)
    visual_depth  - depth as a human reads it (elif chain = same level)
    elif_run      - longest if/elif/elif/... run anywhere in the function
    """
    body = getattr(func, "body", []) or []
    deepest = _deepest_path(body)
    max_depth = len(deepest)
    vis_depth = _visual_depth(body, 0)
    elif_run = _is_elif_chain_run(body)
    # Also check elif runs nested inside other constructs
    for node in ast.walk(func):
        if isinstance(node, ast.If) and node is not func:
            run = 1
            cur = node
            while (
                len(cur.orelse) == 1
                and isinstance(cur.orelse[0], ast.If)
            ):
                run += 1
                cur = cur.orelse[0]
            if run > elif_run:
                elif_run = run

    first = getattr(func, "lineno", 0)
    last = getattr(func, "end_lineno", first)
    total_loc = (last - first + 1) if last and first else 0

    ladder = "->".join(_kind_label(n) for n in deepest)
    return max_depth, total_loc, ladder, vis_depth, elif_run


def analyze_file(path: Path, source_root: Path) -> List[dict]:
    """Return a list of per-function rows for a single .py file."""
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError:
        return []

    rel_path = path.relative_to(source_root).as_posix()
    rows: List[dict] = []

    # Walk module-level: each FunctionDef / AsyncFunctionDef / ClassDef
    # at any depth contributes one row per function. We use a dotted
    # qualified name (Class.method) for readability.
    for parent_qualname, node in _iter_functions(tree, prefix=""):
        max_depth, total_loc, ladder, vis_depth, elif_run = analyze_function(node)
        rows.append({
            "file": rel_path,
            "function": parent_qualname,
            "max_depth": max_depth,
            "visual_depth": vis_depth,
            "elif_run": elif_run,
            "total_loc": total_loc,
            "longest_ladder_kind": ladder,
        })
    return rows


def _iter_functions(node: ast.AST, prefix: str):
    """Yield (qualified_name, function_node) for every def in the tree."""
    body = getattr(node, "body", []) or []
    for child in body:
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            qname = f"{prefix}{child.name}" if prefix else child.name
            yield qname, child
            # Recurse into nested defs
            yield from _iter_functions(child, prefix=f"{qname}.")
        elif isinstance(child, ast.ClassDef):
            cls_prefix = f"{prefix}{child.name}." if prefix else f"{child.name}."
            yield from _iter_functions(child, prefix=cls_prefix)


def main(repo_root: Path, out_csv: Path) -> None:
    game_root = repo_root / "game"
    if not game_root.is_dir():
        sys.exit(f"game/ not found at {game_root}")

    all_rows: List[dict] = []
    for path in sorted(game_root.rglob("*.py")):
        # Skip any tests subtree under game/ (defensive; should be none)
        if "tests" in path.parts:
            continue
        all_rows.extend(analyze_file(path, repo_root))

    # Write CSV
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "file",
                "function",
                "max_depth",
                "visual_depth",
                "elif_run",
                "total_loc",
                "longest_ladder_kind",
            ],
        )
        writer.writeheader()
        for row in all_rows:
            writer.writerow(row)

    # Print summary
    total = len(all_rows)
    deep = [r for r in all_rows if r["max_depth"] >= 4]
    deep_visual = [r for r in all_rows if r["visual_depth"] >= 4]
    histogram = Counter(min(r["max_depth"], 9) for r in all_rows)
    vis_histogram = Counter(min(r["visual_depth"], 9) for r in all_rows)
    print(f"Total functions analyzed: {total}")
    print(f"Functions at AST depth >= 4: {len(deep)} ({100 * len(deep) / total:.1f}%)")
    print(f"Functions at VISUAL depth >= 4: {len(deep_visual)} ({100 * len(deep_visual) / total:.1f}%)")
    print("AST depth distribution (depth: count):")
    for depth in sorted(histogram):
        bucket = f">={depth}" if depth == 9 else str(depth)
        print(f"  {bucket}: {histogram[depth]}")
    print("VISUAL depth distribution (depth: count):")
    for depth in sorted(vis_histogram):
        bucket = f">={depth}" if depth == 9 else str(depth)
        print(f"  {bucket}: {vis_histogram[depth]}")

    # Files containing >=1 function at depth >= 4
    files_deep = {r["file"] for r in deep}
    files_total = {r["file"] for r in all_rows}
    print(f"Files with >=1 deep function: {len(files_deep)} of {len(files_total)} "
          f"({100 * len(files_deep) / len(files_total):.1f}%)")

    print(f"\nCSV written to: {out_csv}")


if __name__ == "__main__":
    # Find repo root: this script lives under
    # <repo>/Projects/active_projects/PROJ-310/findings/nesting_analysis.py
    here = Path(__file__).resolve()
    repo = here.parents[4]
    out = here.parent / "nesting_metrics.csv"
    main(repo, out)

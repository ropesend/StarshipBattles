"""Test coverage audit — Phase 1 deterministic scanner.

Scans every .py file under game/ to extract callable definitions, then
cross-references against tests/unit/ to build a coverage matrix. Assigns
coverage tiers and generates a shard manifest for Phase 2 agent distribution.

Outputs structured JSON to REVIEW_DIR/raw/:
  1. coverage_matrix.json  — production-file → test-files + symbol coverage
  2. layer_summary.json     — coverage statistics by architectural layer
  3. file_inventory.json    — full production file inventory
  4. manifest.json          — shard assignments for agent distribution

Usage:
    python Tools/testcoverage_audit/testcoverage_audit.py
    python Tools/testcoverage_audit/testcoverage_audit.py --output CUSTOM_DIR
    python Tools/testcoverage_audit/testcoverage_audit.py --max-loc-per-shard 8000
    python Tools/testcoverage_audit/testcoverage_audit.py --coverage-json PATH

When --coverage-json is provided, the tool reads authoritative line-coverage
data (either coverage.py's native JSON format or a simple
``{file: {line: hit_count}}`` dict) and cross-references it against each
symbol's line range. Each symbol entry in coverage_matrix.json gains a
``coverage_authoritative`` field (true / false), and the matrix top-level
``coverage_source`` field is set to ``"authoritative+heuristic"``. Without
the flag, ``coverage_authoritative`` is ``null`` and ``coverage_source`` is
``"heuristic"``.
"""

from __future__ import annotations

import ast
import json
import os
import random
import sys
from datetime import datetime
from pathlib import Path


def _find_project_root() -> str:
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "game").is_dir() and (current / "data").is_dir():
            return str(current)
        current = current.parent
    raise RuntimeError("Could not find project root")


PROJECT_ROOT = _find_project_root()
GAME_DIR = os.path.join(PROJECT_ROOT, "game")
TESTS_DIR = os.path.join(PROJECT_ROOT, "tests")
UNIT_TESTS_DIR = os.path.join(TESTS_DIR, "unit")
REVIEWS_DIR = os.path.join(PROJECT_ROOT, "Reviews", "results")

sys.path.insert(0, PROJECT_ROOT)


def _rel(path: str) -> str:
    return os.path.relpath(path, PROJECT_ROOT).replace("\\", "/")


def _read_file(path: str) -> str | None:
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def _discover_py_files(root: str) -> list[str]:
    results: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fname in filenames:
            if fname.endswith(".py"):
                results.append(os.path.join(dirpath, fname))
    return sorted(results)


def _estimate_loc(filepath: str) -> int:
    try:
        with open(filepath, encoding="utf-8") as f:
            return sum(1 for _ in f)
    except (OSError, UnicodeDecodeError):
        return 0


def _layer_for_file(filepath: str) -> str:
    rel = _rel(filepath)
    if rel.startswith("game/ui/"):
        return "ui"
    if rel.startswith("game/strategy/"):
        return "strategy"
    if rel.startswith("game/simulation/"):
        return "simulation"
    if rel.startswith("game/core/"):
        return "core"
    if rel.startswith("game/ai/"):
        return "ai"
    if rel.startswith("game/services/"):
        return "services"
    if rel.startswith("game/research/"):
        return "research"
    if rel.startswith("game/assets/"):
        return "assets"
    if rel.startswith("game/engine/"):
        return "engine"
    return "game_root"


# ---- AST Scanners ----


class _ProductionScanner(ast.NodeVisitor):
    """Extract callable definitions (functions, methods, classes) from production code."""

    def __init__(self) -> None:
        self.symbols: list[dict[str, object]] = []
        self._inside_class = False

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self._inside_class:
            return
        self.symbols.append({
            "name": node.name,
            "type": "function",
            "line": node.lineno,
            "end_line": getattr(node, "end_lineno", node.lineno) or node.lineno,
            "decorators": [
                self._decorator_name(d) for d in node.decorator_list
            ],
        })
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        if self._inside_class:
            return
        self.symbols.append({
            "name": node.name,
            "type": "async_function",
            "line": node.lineno,
            "end_line": getattr(node, "end_lineno", node.lineno) or node.lineno,
            "decorators": [
                self._decorator_name(d) for d in node.decorator_list
            ],
        })
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.symbols.append({
            "name": node.name,
            "type": "class",
            "line": node.lineno,
            "end_line": getattr(node, "end_lineno", node.lineno) or node.lineno,
            "decorators": [
                self._decorator_name(d) for d in node.decorator_list
            ],
        })
        for body_item in node.body:
            if isinstance(body_item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fq_name = f"{node.name}.{body_item.name}"
                self.symbols.append({
                    "name": fq_name,
                    "aliases": [body_item.name],
                    "type": "method",
                    "line": body_item.lineno,
                    "end_line": getattr(body_item, "end_lineno", body_item.lineno) or body_item.lineno,
                    "decorators": [
                        self._decorator_name(d)
                        for d in body_item.decorator_list
                    ],
                })
        was_inside = self._inside_class
        self._inside_class = True
        try:
            for body_item in node.body:
                if not isinstance(body_item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    self.visit(body_item)
        finally:
            self._inside_class = was_inside

    @staticmethod
    def _decorator_name(node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parts: list[str] = [node.attr]
            current: ast.expr = node.value
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            parts.reverse()
            return ".".join(parts)
        if isinstance(node, ast.Call):
            return _ProductionScanner._decorator_name(node.func)
        return "?"


class _TestImportScanner(ast.NodeVisitor):
    """Extract imports from game.* modules in test files."""

    def __init__(self) -> None:
        self.imported_modules: set[str] = set()
        self.imported_symbols: dict[str, str] = {}

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name.startswith("game."):
                self.imported_modules.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module is None:
            self.generic_visit(node)
            return
        if not node.module.startswith("game."):
            self.generic_visit(node)
            return
        self.imported_modules.add(node.module)
        for alias in node.names:
            name = alias.asname or alias.name
            if name != "*":
                fq = f"{node.module}.{name}" if name != alias.name else name
                self.imported_symbols[name] = node.module
        self.generic_visit(node)


def _scan_production_file(filepath: str) -> dict | None:
    source = _read_file(filepath)
    if source is None:
        return None
    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return None
    scanner = _ProductionScanner()
    scanner.visit(tree)
    return {
        "file": _rel(filepath),
        "loc": len(source.splitlines()),
        "layer": _layer_for_file(filepath),
        "symbols": scanner.symbols,
    }


def _scan_test_file(filepath: str) -> dict | None:
    source = _read_file(filepath)
    if source is None:
        return None
    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return None
    scanner = _TestImportScanner()
    scanner.visit(tree)
    return {
        "file": _rel(filepath),
        "loc": len(source.splitlines()),
        "imported_modules": sorted(scanner.imported_modules),
        "imported_symbols": scanner.imported_symbols,
    }


def _name_grep(source: str, symbol_name: str) -> bool:
    """Heuristic: does symbol_name appear as a standalone word in source?"""
    import re
    return bool(re.search(rf"\b{re.escape(symbol_name)}\b", source))


def _symbol_match_names(symbol: dict) -> list[str]:
    names: list[str] = []
    primary = symbol.get("name")
    if primary:
        names.append(str(primary))
    aliases = symbol.get("aliases", [])
    if isinstance(aliases, list):
        for alias in aliases:
            alias_name = str(alias)
            if alias_name and alias_name not in names:
                names.append(alias_name)
    return names


def _load_authoritative_coverage(
    coverage_json_path: str,
) -> dict[str, set[int]]:
    """Load authoritative line coverage from a JSON file.

    Accepts two formats permissively:
      1. coverage.py native: {"files": {file: {"executed_lines": [...]}}}
      2. Simple dict: {file: {line_number: hit_count}}  (line_number may be
         int or string; hit_count > 0 means hit)

    Returns mapping ``rel_file_path -> set of hit line numbers``. Paths
    are normalized to forward-slash repo-relative form when possible.
    """
    try:
        with open(coverage_json_path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"  WARNING: failed to read --coverage-json {coverage_json_path}: {exc}")
        return {}

    result: dict[str, set[int]] = {}

    def _normalize(p: str) -> str:
        norm = p.replace("\\", "/")
        # Strip absolute repo-root prefix if present
        root_norm = PROJECT_ROOT.replace("\\", "/").rstrip("/") + "/"
        if norm.startswith(root_norm):
            norm = norm[len(root_norm):]
        return norm

    if isinstance(data, dict) and isinstance(data.get("files"), dict):
        # coverage.py native format
        for fpath, finfo in data["files"].items():
            if not isinstance(finfo, dict):
                continue
            executed = finfo.get("executed_lines")
            if not isinstance(executed, list):
                # Fallback: support older variants storing per-line dicts
                executed = []
            hit_lines: set[int] = set()
            for ln in executed:
                try:
                    hit_lines.add(int(ln))
                except (TypeError, ValueError):
                    continue
            if hit_lines:
                result[_normalize(str(fpath))] = hit_lines
        return result

    # Generic {file: {line: hits}} format
    if isinstance(data, dict):
        for fpath, line_map in data.items():
            if not isinstance(line_map, dict):
                continue
            hit_lines = set()
            for ln, hits in line_map.items():
                try:
                    if int(hits) > 0:
                        hit_lines.add(int(ln))
                except (TypeError, ValueError):
                    continue
            if hit_lines:
                result[_normalize(str(fpath))] = hit_lines

    return result


def _build_coverage_matrix(
    prod_results: list[dict],
    test_results: list[dict],
    authoritative_coverage: dict[str, set[int]] | None = None,
) -> dict:
    module_to_tests: dict[str, set[str]] = {}
    for tr in test_results:
        for mod in tr.get("imported_modules", []):
            module_to_tests.setdefault(mod, set()).add(tr["file"])
        for sym_name, sym_module in tr.get("imported_symbols", {}).items():
            module_to_tests.setdefault(sym_module, set()).add(tr["file"])

    test_file_sources: dict[str, str | None] = {}
    for tr in test_results:
        fpath = os.path.join(PROJECT_ROOT, tr["file"])
        test_file_sources[tr["file"]] = _read_file(fpath)

    matrix: dict = {}
    for pr in prod_results:
        prod_rel = pr["file"]
        prod_module = os.path.splitext(prod_rel)[0].replace("/", ".").replace("\\", ".")
        if prod_module.endswith(".__init__"):
            prod_module = prod_module[: -len(".__init__")]

        related_test_files: list[str] = sorted(
            module_to_tests.get(prod_module, set())
        )

        # Lookup authoritative hit lines for this production file (if any)
        file_hit_lines: set[int] | None = None
        if authoritative_coverage is not None:
            file_hit_lines = authoritative_coverage.get(prod_rel)
            if file_hit_lines is None:
                # Try basename-suffix match as a fallback for path-shape mismatches
                for cov_path, lines in authoritative_coverage.items():
                    if cov_path.endswith(prod_rel) or prod_rel.endswith(cov_path):
                        file_hit_lines = lines
                        break

        symbol_coverage: dict = {}
        untested_symbols: list[dict] = []
        for sym in pr.get("symbols", []):
            sym_name: str = sym["name"]
            found_in: list[str] = []
            matched_names: list[str] = []
            match_names = _symbol_match_names(sym)
            for test_file in related_test_files:
                source = test_file_sources.get(test_file)
                matched_this_file = False
                for match_name in match_names:
                    if source and _name_grep(source, match_name):
                        matched_this_file = True
                        if match_name not in matched_names:
                            matched_names.append(match_name)
                if matched_this_file:
                    found_in.append(test_file)

            # Authoritative coverage cross-reference
            coverage_authoritative: bool | None
            if authoritative_coverage is None:
                coverage_authoritative = None
            elif file_hit_lines is None:
                coverage_authoritative = False
            else:
                start_line = int(sym.get("line", 0))
                end_line = int(sym.get("end_line", start_line) or start_line)
                if end_line < start_line:
                    end_line = start_line
                coverage_authoritative = any(
                    start_line <= ln <= end_line for ln in file_hit_lines
                )

            symbol_coverage[sym_name] = {
                "type": sym["type"],
                "line": sym["line"],
                "end_line": sym.get("end_line", sym["line"]),
                "aliases": sym.get("aliases", []),
                "matched_names": matched_names,
                "candidate_test_files": found_in,
                "heuristic_match": len(found_in) > 0,
                "coverage_authoritative": coverage_authoritative,
            }
            if not found_in:
                untested_symbols.append(sym)

        total_symbols = len(pr.get("symbols", []))
        tested_count = sum(
            1 for sc in symbol_coverage.values() if sc["heuristic_match"]
        )

        if not related_test_files:
            tier = 0
        elif tested_count == 0:
            tier = 1
        elif tested_count < total_symbols:
            tier = 2
        else:
            tier = 3

        matrix[prod_rel] = {
            "layer": pr["layer"],
            "loc": pr["loc"],
            "candidate_test_files": related_test_files,
            "total_symbols": total_symbols,
            "tested_symbols": tested_count,
            "untested_symbols": [s["name"] for s in untested_symbols],
            "coverage_tier": tier,
            "tier_label": {
                0: "TIER_0_NO_TESTS",
                1: "TIER_1_NO_SYMBOLS_TESTED",
                2: "TIER_2_PARTIAL",
                3: "TIER_3_APPARENTLY_COVERED",
            }[tier],
            "symbol_coverage": symbol_coverage,
        }

    return matrix


def _build_layer_summary(matrix: dict) -> dict:
    layers: dict[str, dict] = {}
    for filepath, info in matrix.items():
        layer = info["layer"]
        if layer not in layers:
            layers[layer] = {
                "layer": layer,
                "total_files": 0,
                "total_loc": 0,
                "total_symbols": 0,
                "tested_symbols": 0,
                "tier_counts": {"0": 0, "1": 0, "2": 0, "3": 0},
            }
        ls = layers[layer]
        ls["total_files"] += 1
        ls["total_loc"] += info["loc"]
        ls["total_symbols"] += info["total_symbols"]
        ls["tested_symbols"] += info["tested_symbols"]
        ls["tier_counts"][str(info["coverage_tier"])] += 1

    for ls in layers.values():
        total = ls["total_symbols"]
        ls["coverage_pct"] = round(
            (ls["tested_symbols"] / total * 100) if total > 0 else 0, 1
        )

    return {
        "layers": layers,
        "totals": {
            "total_files": sum(ls["total_files"] for ls in layers.values()),
            "total_loc": sum(ls["total_loc"] for ls in layers.values()),
            "total_symbols": sum(
                ls["total_symbols"] for ls in layers.values()
            ),
            "tested_symbols": sum(
                ls["tested_symbols"] for ls in layers.values()
            ),
            "overall_coverage_pct": round(
                sum(ls["tested_symbols"] for ls in layers.values())
                / max(sum(ls["total_symbols"] for ls in layers.values()), 1)
                * 100,
                1,
            ),
        },
    }


def greedy_balance(
    files: list[tuple[str, int]], shard_count: int
) -> list[list[tuple[str, int]]]:
    shards: list[list[tuple[str, int]]] = [[] for _ in range(shard_count)]
    totals = [0] * shard_count
    for filepath, loc in files:
        min_idx = min(range(shard_count), key=lambda i: totals[i])
        shards[min_idx].append((filepath, loc))
        totals[min_idx] += loc
    return shards


def _generate_manifest(
    prod_files: list[str],
    matrix: dict,
    seed: str,
    target_shards: int,
    max_loc_per_shard: int,
) -> dict:
    files = [
        (f, matrix[f]["loc"] if f in matrix else _estimate_loc(f))
        for f in prod_files
    ]

    rng = random.Random(seed)
    rng.shuffle(files)

    shard_count = target_shards

    if max_loc_per_shard and max_loc_per_shard > 0:
        max_file = max(loc for _, loc in files) if files else 0
        for _attempt in range(50):
            shards = greedy_balance(files, shard_count)
            max_shard = max(
                sum(loc for _, loc in s) for s in shards
            )
            if max_shard <= max_loc_per_shard:
                break
            if shard_count >= 40:
                break
            shard_count += 1

    shards = greedy_balance(files, shard_count)

    manifest: dict = {
        "seed": seed,
        "shard_count": shard_count,
        "target_shards": target_shards,
        "max_loc_per_shard": max_loc_per_shard,
        "total_files": len(files),
        "total_loc_estimate": sum(loc for _, loc in files),
        "shards": {},
    }

    for i, shard in enumerate(shards):
        sid = f"{i + 1:02d}"
        file_paths = sorted(path for path, _ in shard)
        tier_counts = {"0": 0, "1": 0, "2": 0, "3": 0}
        for fp in file_paths:
            if fp in matrix:
                tier_counts[str(matrix[fp]["coverage_tier"])] += 1
        manifest["shards"][sid] = {
            "label": f"Shard {sid}",
            "file_count": len(file_paths),
            "loc_estimate": sum(loc for _, loc in shard),
            "tier_counts": tier_counts,
            "files": file_paths,
        }

    return manifest


def run(
    force_output_dir: str | None = None,
    max_loc_per_shard: int = 8000,
    target_shards: int = 18,
    coverage_json: str | None = None,
) -> str:
    date_slug = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_dir = force_output_dir or os.path.join(
        REVIEWS_DIR, f"{date_slug}_testcoverage-audit"
    )
    raw_dir = os.path.join(output_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)

    print("=== Phase 1: Test Coverage Audit ===")
    print(f"Output: {output_dir}")
    print()

    print("Discovering production files...")
    prod_files = _discover_py_files(GAME_DIR)
    print(f"  Found {len(prod_files)} production files")

    print("Scanning production code for callable definitions...")
    prod_results: list[dict] = []
    for fp in prod_files:
        result = _scan_production_file(fp)
        if result is not None:
            prod_results.append(result)

    total_symbols = sum(len(r.get("symbols", [])) for r in prod_results)
    print(f"  Extracted {total_symbols} callable definitions "
          f"from {len(prod_results)} parseable files")

    print("Discovering unit test files...")
    test_files = _discover_py_files(UNIT_TESTS_DIR)
    print(f"  Found {len(test_files)} unit test files")

    print("Scanning test files for game.* imports...")
    test_results: list[dict] = []
    for fp in test_files:
        result = _scan_test_file(fp)
        if result is not None:
            test_results.append(result)

    total_imports = sum(
        len(r.get("imported_modules", [])) for r in test_results
    )
    print(f"  Found {total_imports} game-module imports "
          f"across {len(test_results)} parseable test files")

    authoritative_coverage: dict[str, set[int]] | None = None
    if coverage_json:
        print(f"Loading authoritative line coverage from {coverage_json}...")
        authoritative_coverage = _load_authoritative_coverage(coverage_json)
        print(
            f"  Loaded coverage for {len(authoritative_coverage)} files"
        )

    print("Building coverage matrix...")
    matrix = _build_coverage_matrix(
        prod_results, test_results, authoritative_coverage
    )
    coverage_source = (
        "authoritative+heuristic" if authoritative_coverage is not None
        else "heuristic"
    )

    tier_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    for info in matrix.values():
        tier_counts[info["coverage_tier"]] += 1
    print(f"  Tier 0 (no tests):        {tier_counts[0]}")
    print(f"  Tier 1 (no symbols):      {tier_counts[1]}")
    print(f"  Tier 2 (partial):         {tier_counts[2]}")
    print(f"  Tier 3 (appears covered): {tier_counts[3]}")

    print("Computing layer summary...")
    layer_summary = _build_layer_summary(matrix)
    for ls in layer_summary["layers"].values():
        print(
            f"  {ls['layer']:>12s}: {ls['coverage_pct']:5.1f}% "
            f"({ls['tested_symbols']}/{ls['total_symbols']} symbols)"
        )

    rel_files = [_rel(f) for f in prod_files]

    with open(os.path.join(raw_dir, "file_inventory.json"), "w",
              encoding="utf-8") as f:
        json.dump(
            {"total_files": len(prod_files), "files": sorted(rel_files)},
            f, indent=2,
        )

    with open(os.path.join(raw_dir, "coverage_matrix.json"), "w",
              encoding="utf-8") as f:
        json.dump(
            {
                "coverage_source": coverage_source,
                "files": matrix,
            },
            f, indent=2,
        )

    with open(os.path.join(raw_dir, "layer_summary.json"), "w",
              encoding="utf-8") as f:
        json.dump(layer_summary, f, indent=2)

    print("Generating shard manifest...")
    seed = f"testcoverage-{date_slug}"
    manifest = _generate_manifest(
        rel_files, matrix, seed, target_shards, max_loc_per_shard,
    )
    with open(os.path.join(raw_dir, "manifest.json"), "w",
              encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"  {manifest['shard_count']} shards "
          f"(target: {target_shards}, max LOC/shard: {max_loc_per_shard})")
    for sid, info in manifest["shards"].items():
        print(
            f"    {sid}: {info['file_count']:>4d} files, "
            f"~{info['loc_estimate']:>6d} LOC, "
            f"tiers={info['tier_counts']}"
        )

    print()
    print(f"Phase 1 complete. Raw results: {raw_dir}")
    print(f"Output directory: {output_dir}")
    return output_dir


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Test coverage audit — Phase 1 deterministic scanner"
    )
    parser.add_argument(
        "--output", default=None,
        help="Override output directory",
    )
    parser.add_argument(
        "--max-loc-per-shard", type=int, default=8000,
        help="Auto-increase shard count to keep per-shard LOC under this ceiling",
    )
    parser.add_argument(
        "--shards", type=int, default=18,
        help="Target number of shards (default: 18)",
    )
    parser.add_argument(
        "--coverage-json", default=None,
        help=(
            "Optional path to a JSON file containing authoritative line-"
            "coverage data (coverage.py native format or a simple "
            "{file: {line: hit_count}} dict). When provided, each symbol "
            "in coverage_matrix.json gains a 'coverage_authoritative' "
            "boolean and the matrix's top-level 'coverage_source' is set "
            "to 'authoritative+heuristic'. Without the flag, "
            "coverage_authoritative is null and coverage_source is "
            "'heuristic'."
        ),
    )
    args = parser.parse_args()
    run(
        force_output_dir=args.output,
        max_loc_per_shard=args.max_loc_per_shard,
        target_shards=args.shards,
        coverage_json=args.coverage_json,
    )

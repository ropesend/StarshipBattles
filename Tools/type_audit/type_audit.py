"""Type safety & annotation quality audit — Phase 1 deterministic scanner.

Two scanning passes:
  1. mypy strict-mode (generates temp config, runs mypy, captures output)
  2. AST annotation scanner (``-> Any`` density, missing returns, ``# type: ignore``,
     ``cast()`` usage, ``TYPE_CHECKING`` block hygiene)

Outputs structured JSON to REVIEW_DIR/raw/ and generates a shard manifest.

Usage::

    python Tools/type_audit/type_audit.py
    python Tools/type_audit/type_audit.py --skip-mypy
    python Tools/type_audit/type_audit.py --output CUSTOM_DIR
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
import tempfile
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
REVIEWS_DIR = os.path.join(PROJECT_ROOT, "Reviews", "results")

sys.path.insert(0, PROJECT_ROOT)


MYPIQ_CONFIG = """
[tool.mypy]
python_version = "3.14"
warn_return_any = true
warn_unused_ignores = true
show_error_codes = true

[[tool.mypy.overrides]]
module = "game.ui.*"
disallow_any_expr = false
disallow_untyped_defs = false
"""

LAYER_MAP = {
    "game/ui": "ui",
    "game/strategy": "strategy",
    "game/simulation": "simulation",
    "game/ai": "ai",
    "game/engine": "engine",
    "game/research": "research",
    "game/assets": "assets",
    "game/services": "services",
    "game/core": "core",
}


def _rel(path: str) -> str:
    return os.path.relpath(path, PROJECT_ROOT).replace("\\", "/")


def _file_layer(filepath: str) -> str:
    rel = _rel(filepath).replace("\\", "/")
    for prefix, layer in sorted(LAYER_MAP.items(), key=lambda x: -len(x[0])):
        if rel.startswith(prefix + "/") or rel == prefix:
            return layer
    return "unknown"


class _TypeScanner(ast.NodeVisitor):
    def __init__(self, source: str, filepath: str):
        self.source = source
        self.lines = source.splitlines()
        self.filepath = filepath
        self.layer = _file_layer(filepath)
        self.any_returns: list[dict] = []
        self.missing_returns: list[dict] = []
        self.type_ignores: list[dict] = []
        self.cast_usages: list[dict] = []
        self.type_checking_blocks: list[dict] = []
        self.any_annotations: list[dict] = []
        self._current_class: str | None = None
        self._in_type_checking = False

    def visit_If(self, node: ast.If) -> None:
        if self._is_type_checking_check(node.test):
            self._in_type_checking = True
            self.type_checking_blocks.append({
                "file": _rel(self.filepath),
                "line": node.lineno,
                "body_lines": len(node.body),
            })
            for stmt in ast.walk(node):
                if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                    pass
            self.generic_visit(node)
            self._in_type_checking = False
        else:
            self.generic_visit(node)

    def _is_type_checking_check(self, test: ast.expr) -> bool:
        if isinstance(test, ast.Name) and test.id == "TYPE_CHECKING":
            return True
        if isinstance(test, ast.Attribute):
            parts = []
            current = test
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            parts.reverse()
            return "TYPE_CHECKING" in parts
        return False

    def _is_any_type(self, node: ast.expr) -> bool:
        if isinstance(node, ast.Name) and node.id == "Any":
            return True
        if isinstance(node, ast.Attribute) and node.attr == "Any":
            return True
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) and node.value.id == "Any":
            return True
        return False

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        is_dunder = node.name.startswith("__") and node.name.endswith("__")

        if node.returns is None:
            if not is_dunder:
                self.missing_returns.append({
                    "file": _rel(self.filepath),
                    "line": node.lineno,
                    "function": node.name,
                    "class": self._current_class,
                    "layer": self.layer,
                })
        elif self._is_any_type(node.returns):
            self.any_returns.append({
                "file": _rel(self.filepath),
                "line": node.lineno,
                "function": node.name,
                "class": self._current_class,
                "layer": self.layer,
            })

        for arg in node.args.args:
            if arg.annotation and self._is_any_type(arg.annotation):
                self.any_annotations.append({
                    "file": _rel(self.filepath),
                    "line": node.lineno,
                    "function": node.name,
                    "parameter": arg.arg,
                    "type": "Any",
                })

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        prev = self._current_class
        self._current_class = node.name
        self.generic_visit(node)
        self._current_class = prev

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        if isinstance(func, ast.Name) and func.id == "cast":
            self.cast_usages.append({
                "file": _rel(self.filepath),
                "line": node.lineno,
            })
        self.generic_visit(node)


def scan_file(filepath: str) -> dict | None:
    source = None
    try:
        with open(filepath, encoding="utf-8", errors="replace") as f:
            source = f.read()
    except OSError:
        return None
    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return None
    scanner = _TypeScanner(source, filepath)
    scanner.visit(tree)

    for lineno, line in enumerate(scanner.lines, 1):
        stripped = line.strip()
        if "# type: ignore" in stripped:
            scanner.type_ignores.append({
                "file": _rel(filepath),
                "line": lineno,
                "content": stripped,
            })

    return {
        "file": _rel(filepath),
        "layer": scanner.layer,
        "any_returns": scanner.any_returns,
        "missing_returns": scanner.missing_returns,
        "type_ignores": scanner.type_ignores,
        "cast_usages": scanner.cast_usages,
        "type_checking_blocks": scanner.type_checking_blocks,
        "any_annotations": scanner.any_annotations,
    }


def run_mypy(output_dir: str) -> dict:
    config_text = MYPIQ_CONFIG.strip()

    config_path = os.path.join(output_dir, "_mypy_config.toml")
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config_text)

    try:
        result = subprocess.run(
            [sys.executable, "-m", "mypy", str(GAME_DIR),
             "--config-file", config_path,
             "--no-error-summary", "--no-pretty"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=PROJECT_ROOT,
        )
        lines = result.stdout.strip().splitlines() if result.stdout else []
        errors = result.stderr.strip().splitlines() if result.stderr else []

        error_list: list[dict] = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = line.split(":", 2)
            if len(parts) >= 2:
                error_list.append({
                    "raw": line,
                    "file": parts[0],
                    "line": parts[1] if len(parts) > 1 else "",
                })

        return {
            "status": "ok" if result.returncode == 0 else "errors_found",
            "error_count": len(error_list),
            "exit_code": result.returncode,
            "errors": error_list,
            "stderr_lines": errors[:20],
        }
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "error_count": 0, "errors": []}
    except FileNotFoundError:
        return {"status": "mypy_not_installed", "error_count": 0, "errors": []}
    finally:
        try:
            os.unlink(config_path)
        except OSError:
            pass


def _discover_py_files(root: str) -> list[str]:
    results: list[str] = []
    for dirpath, _, filenames in os.walk(root):
        if "__pycache__" in dirpath:
            continue
        for fname in filenames:
            if fname.endswith(".py"):
                results.append(os.path.join(dirpath, fname))
    return results


def _simple_balance(files: list[tuple[str, int]], shard_count: int) -> list[list[tuple[str, int]]]:
    shards: list[list[tuple[str, int]]] = [[] for _ in range(shard_count)]
    totals = [0] * shard_count
    for filepath, loc in files:
        min_idx = min(range(shard_count), key=lambda i: totals[i])
        shards[min_idx].append((filepath, loc))
        totals[min_idx] += loc
    return shards


def _generate_manifest(files: list[str], output_dir: str) -> dict:
    seed = f"type-{datetime.now().strftime('%Y-%m-%d')}"
    rng = __import__("random").Random(seed)
    shuffled = list(files)
    rng.shuffle(shuffled)

    loc_map = {}
    for f in shuffled:
        try:
            with open(os.path.join(PROJECT_ROOT, f), encoding="utf-8") as fp:
                loc_map[f] = sum(1 for _ in fp)
        except OSError:
            loc_map[f] = 0

    pairs = [(f, loc_map.get(f, 0)) for f in shuffled]
    shards = _simple_balance(pairs, 4)
    manifest = {
        "seed": seed,
        "shard_count": 4,
        "total_files": len(files),
        "shards": {},
    }
    for i, shard in enumerate(shards):
        sid = f"{i + 1:02d}"
        manifest["shards"][sid] = {
            "label": f"Shard {sid}",
            "files": [p for p, _ in shard],
            "file_count": len(shard),
            "loc_estimate": sum(loc for _, loc in shard),
        }
    return manifest


def _build_any_heatmap(results: list[dict]) -> dict:
    heatmap: dict[str, dict] = {}
    for r in results:
        layer = r.get("layer", "unknown")
        if layer not in heatmap:
            heatmap[layer] = {
                "any_returns": 0,
                "any_annotations": 0,
                "missing_returns": 0,
                "cast_usages": 0,
                "type_ignores": 0,
            }
        heatmap[layer]["any_returns"] += len(r.get("any_returns", []))
        heatmap[layer]["any_annotations"] += len(r.get("any_annotations", []))
        heatmap[layer]["missing_returns"] += len(r.get("missing_returns", []))
        heatmap[layer]["cast_usages"] += len(r.get("cast_usages", []))
        heatmap[layer]["type_ignores"] += len(r.get("type_ignores", []))
    return heatmap


def run(force_output_dir: str | None = None, skip_mypy: bool = False) -> str:
    date_slug = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_dir = force_output_dir or os.path.join(REVIEWS_DIR, f"{date_slug}_type-audit")
    raw_dir = os.path.join(output_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)

    print("=== Phase 1: Type Safety Audit ===")
    print(f"Output: {output_dir}")
    print()

    files = _discover_py_files(GAME_DIR)
    print(f"Scanning {len(files)} files...")

    results: list[dict] = []
    for filepath in files:
        result = scan_file(filepath)
        if result is not None:
            results.append(result)

    any_returns_flat: list[dict] = []
    all_missing: list[dict] = []
    all_ignores: list[dict] = []
    all_casts: list[dict] = []
    all_any_annotations: list[dict] = []

    for r in results:
        any_returns_flat.extend(r.get("any_returns", []))
        all_missing.extend(r.get("missing_returns", []))
        all_ignores.extend(r.get("type_ignores", []))
        all_casts.extend(r.get("cast_usages", []))
        all_any_annotations.extend(r.get("any_annotations", []))

    heatmap = _build_any_heatmap(results)

    with open(os.path.join(raw_dir, "any_heatmap.json"), "w", encoding="utf-8") as f:
        json.dump(heatmap, f, indent=2)
    with open(os.path.join(raw_dir, "any_returns.json"), "w", encoding="utf-8") as f:
        json.dump(any_returns_flat, f, indent=2)
    with open(os.path.join(raw_dir, "missing_returns.json"), "w", encoding="utf-8") as f:
        json.dump(all_missing, f, indent=2)
    with open(os.path.join(raw_dir, "type_ignore_sites.json"), "w", encoding="utf-8") as f:
        json.dump(all_ignores, f, indent=2)
    with open(os.path.join(raw_dir, "cast_usage.json"), "w", encoding="utf-8") as f:
        json.dump(all_casts, f, indent=2)

    rel_files = [_rel(f) for f in files]
    manifest = _generate_manifest(rel_files, output_dir)
    with open(os.path.join(raw_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Per-shard filtered copies of the AST scan outputs.
    # any_heatmap.json is global (not split). mypy is split below after it runs.
    for sid, shard_info in manifest["shards"].items():
        shard_files = set(shard_info["files"])

        def _filter(items: list[dict]) -> list[dict]:
            return [it for it in items if it.get("file") in shard_files]

        with open(os.path.join(raw_dir, f"any_returns_{sid}.json"), "w", encoding="utf-8") as f:
            json.dump(_filter(any_returns_flat), f, indent=2)
        with open(os.path.join(raw_dir, f"missing_returns_{sid}.json"), "w", encoding="utf-8") as f:
            json.dump(_filter(all_missing), f, indent=2)
        with open(os.path.join(raw_dir, f"type_ignore_sites_{sid}.json"), "w", encoding="utf-8") as f:
            json.dump(_filter(all_ignores), f, indent=2)
        with open(os.path.join(raw_dir, f"cast_usage_{sid}.json"), "w", encoding="utf-8") as f:
            json.dump(_filter(all_casts), f, indent=2)

    if not skip_mypy:
        print("Running mypy strict-mode...")
        mypy_result = run_mypy(raw_dir)
        with open(os.path.join(raw_dir, "mypy_report.json"), "w", encoding="utf-8") as f:
            json.dump(mypy_result, f, indent=2)
        print(f"  mypy: {mypy_result['status']} ({mypy_result['error_count']} errors)")

        # Per-shard mypy reports — filter errors by file membership.
        # mypy reports paths relative to cwd (PROJECT_ROOT) using OS separators; normalise to forward-slash.
        for sid, shard_info in manifest["shards"].items():
            shard_files = set(shard_info["files"])
            shard_errors = []
            for err in mypy_result.get("errors", []):
                err_file = err.get("file", "").replace("\\", "/")
                if err_file in shard_files:
                    shard_errors.append(err)
            shard_report = {
                "status": mypy_result.get("status"),
                "exit_code": mypy_result.get("exit_code"),
                "error_count": len(shard_errors),
                "errors": shard_errors,
            }
            with open(os.path.join(raw_dir, f"mypy_report_{sid}.json"), "w", encoding="utf-8") as f:
                json.dump(shard_report, f, indent=2)
    else:
        print("  mypy: SKIPPED (--skip-mypy)")
        with open(os.path.join(raw_dir, "mypy_report.json"), "w", encoding="utf-8") as f:
            json.dump({"status": "skipped"}, f)
        for sid in manifest["shards"]:
            with open(os.path.join(raw_dir, f"mypy_report_{sid}.json"), "w", encoding="utf-8") as f:
                json.dump({"status": "skipped"}, f)

    print(f"  -> Any returns:      {len(any_returns_flat)}")
    print(f"  Missing returns:     {len(all_missing)}")
    print(f"  # type: ignore:      {len(all_ignores)}")
    print(f"  cast() usages:       {len(all_casts)}")
    print(f"  :Any annotations:    {len(all_any_annotations)}")
    print()
    print(f"Phase 1 complete. Raw results: {raw_dir}")
    print(f"Output directory: {output_dir}")
    return output_dir


if __name__ == "__main__":
    skip_mypy_flag = "--skip-mypy" in sys.argv
    run(skip_mypy=skip_mypy_flag)

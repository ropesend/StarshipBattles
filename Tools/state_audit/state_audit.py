"""State management & mutability audit — Phase 1 deterministic scanner.

Scans every .py file under game/ and extracts:
  1. Module-level singleton patterns (``_default_*``, ``_instance``, ``_singleton``)
  2. Module-level mutable collections (dict, list, set at module scope)
  3. ``global`` keyword usages with context
  4. Class-level mutable parameter defaults
  5. ``random.seed()`` calls outside the per-battle RNG pattern
  6. ``get_default_xxx()`` call-site vs ``ctx.xxx`` access ratio per file

Outputs structured JSON to REVIEW_DIR/raw/ and generates a shard manifest.

Usage::

    python Tools/state_audit/state_audit.py
    python Tools/state_audit/state_audit.py --output CUSTOM_DIR
"""

from __future__ import annotations

import ast
import json
import os
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


class _StateScanner(ast.NodeVisitor):
    SINGLETON_PATTERNS = ("_default_", "_instance", "_singleton")

    def __init__(self, source: str, filepath: str):
        self.source = source
        self.lines = source.splitlines()
        self.filepath = filepath
        self.module_mutables: list[dict] = []
        self.singleton_defs: list[dict] = []
        self.global_usages: list[dict] = []
        self.class_mutable_defaults: list[dict] = []
        self.random_seed_sites: list[dict] = []
        self.ctx_accesses: list[dict] = []
        self.get_default_calls: list[dict] = []
        self._current_function: str | None = None
        self._in_class_body = False
        self._current_class: str | None = None

    def visit_Assign(self, node: ast.Assign) -> None:
        if self._current_function is None and not self._in_class_body:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    for pattern in self.SINGLETON_PATTERNS:
                        if target.id.startswith(pattern):
                            self.singleton_defs.append({
                                "file": _rel(self.filepath),
                                "line": node.lineno,
                                "variable": target.id,
                                "context": self.lines[node.lineno - 1].strip() if node.lineno <= len(self.lines) else "",
                            })
                            break
                    if target.id.isupper():
                        continue
                    if isinstance(node.value, (ast.Dict, ast.List, ast.Set, ast.ListComp, ast.DictComp, ast.SetComp)):
                        self.module_mutables.append({
                            "file": _rel(self.filepath),
                            "line": node.lineno,
                            "variable": target.id,
                            "type": node.value.__class__.__name__,
                            "context": self.lines[node.lineno - 1].strip() if node.lineno <= len(self.lines) else "",
                        })
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if self._current_function is None and not self._in_class_body:
            if isinstance(node.target, ast.Name):
                for pattern in self.SINGLETON_PATTERNS:
                    if node.target.id.startswith(pattern):
                        self.singleton_defs.append({
                            "file": _rel(self.filepath),
                            "line": node.lineno,
                            "variable": node.target.id,
                            "context": self.lines[node.lineno - 1].strip() if node.lineno <= len(self.lines) else "",
                        })
                        break
                if node.value and isinstance(node.value, (ast.Dict, ast.List, ast.Set, ast.ListComp, ast.DictComp, ast.SetComp)):
                    if node.target.id.isupper():
                        return
                    self.module_mutables.append({
                        "file": _rel(self.filepath),
                        "line": node.lineno,
                        "variable": node.target.id,
                        "type": node.value.__class__.__name__,
                        "context": self.lines[node.lineno - 1].strip() if node.lineno <= len(self.lines) else "",
                    })
        self.generic_visit(node)

    def visit_Global(self, node: ast.Global) -> None:
        for name in node.names:
            self.global_usages.append({
                "file": _rel(self.filepath),
                "line": node.lineno,
                "variable": name,
                "function": self._current_function or "<module>",
                "context": self.lines[node.lineno - 1].strip() if node.lineno <= len(self.lines) else "",
            })
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        prev = self._current_function
        self._current_function = node.name
        if self._in_class_body:
            for arg in node.args.defaults:
                if isinstance(arg, (ast.List, ast.Dict, ast.Set)):
                    self.class_mutable_defaults.append({
                        "file": _rel(self.filepath),
                        "line": node.lineno,
                        "method": node.name,
                        "class": self._current_class or "<unknown>",
                        "default_type": arg.__class__.__name__,
                    })
        self.generic_visit(node)
        self._current_function = prev

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        prev_class = self._current_class
        prev_in_class = self._in_class_body
        self._current_class = node.name
        self._in_class_body = True
        self.generic_visit(node)
        self._current_class = prev_class
        self._in_class_body = prev_in_class

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        call_name = self._resolve_call_name(func)
        if call_name and call_name.startswith("get_default_"):
            self.get_default_calls.append({
                "file": _rel(self.filepath),
                "line": node.lineno,
                "call": call_name,
            })
        elif call_name and call_name.startswith("set_default_"):
            self.get_default_calls.append({
                "file": _rel(self.filepath),
                "line": node.lineno,
                "call": call_name,
            })
        elif call_name and call_name.startswith("ctx."):
            self.ctx_accesses.append({
                "file": _rel(self.filepath),
                "line": node.lineno,
                "call": call_name,
            })
        elif call_name in ("random.seed",):
            import_parts = self.filepath.replace("\\", "/")
            if "battle_engine" not in import_parts and "damage_calculator" not in import_parts:
                self.random_seed_sites.append({
                    "file": _rel(self.filepath),
                    "line": node.lineno,
                    "call": call_name,
                })
        self.generic_visit(node)

    def _resolve_call_name(self, node: ast.expr) -> str | None:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parts: list[str] = [node.attr]
            current = node.value
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            parts.reverse()
            return ".".join(parts)
        return None


def scan_file(filepath: str) -> dict | None:
    source = _read_file(filepath)
    if source is None:
        return None
    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return None
    scanner = _StateScanner(source, filepath)
    scanner.visit(tree)
    return {
        "file": _rel(filepath),
        "singleton_defs": scanner.singleton_defs,
        "module_mutables": scanner.module_mutables,
        "global_usages": scanner.global_usages,
        "class_mutable_defaults": scanner.class_mutable_defaults,
        "random_seed_sites": scanner.random_seed_sites,
        "get_default_calls": scanner.get_default_calls,
        "ctx_accesses": scanner.ctx_accesses,
    }


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
    seed = f"state-{datetime.now().strftime('%Y-%m-%d')}"
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


def run(force_output_dir: str | None = None) -> str:
    date_slug = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_dir = force_output_dir or os.path.join(REVIEWS_DIR, f"{date_slug}_state-audit")
    raw_dir = os.path.join(output_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)

    print("=== Phase 1: State Management Audit ===")
    print(f"Output: {output_dir}")
    print()

    files = _discover_py_files(GAME_DIR)
    print(f"Scanning {len(files)} files...")

    all_singleton_defs: list[dict] = []
    all_module_mutables: list[dict] = []
    all_global_usages: list[dict] = []
    all_class_mutable_defaults: list[dict] = []
    all_random_seeds: list[dict] = []
    get_default_count = 0
    ctx_access_count = 0
    per_file_get_default: dict[str, int] = {}
    per_file_ctx: dict[str, int] = {}

    for filepath in files:
        result = scan_file(filepath)
        if result is None:
            continue
        all_singleton_defs.extend(result["singleton_defs"])
        all_module_mutables.extend(result["module_mutables"])
        all_global_usages.extend(result["global_usages"])
        all_class_mutable_defaults.extend(result["class_mutable_defaults"])
        all_random_seeds.extend(result["random_seed_sites"])
        get_default_count += len(result["get_default_calls"])
        ctx_access_count += len(result["ctx_accesses"])
        per_file_get_default[result["file"]] = len(result["get_default_calls"])
        per_file_ctx[result["file"]] = len(result["ctx_accesses"])

    with open(os.path.join(raw_dir, "singleton_sites.json"), "w", encoding="utf-8") as f:
        json.dump(all_singleton_defs, f, indent=2)
    with open(os.path.join(raw_dir, "module_mutables.json"), "w", encoding="utf-8") as f:
        json.dump(all_module_mutables, f, indent=2)
    with open(os.path.join(raw_dir, "global_usages.json"), "w", encoding="utf-8") as f:
        json.dump(all_global_usages, f, indent=2)
    with open(os.path.join(raw_dir, "class_mutable_defaults.json"), "w", encoding="utf-8") as f:
        json.dump(all_class_mutable_defaults, f, indent=2)
    with open(os.path.join(raw_dir, "random_seed_sites.json"), "w", encoding="utf-8") as f:
        json.dump(all_random_seeds, f, indent=2)

    ctx_ratio = {
        "get_default_calls": get_default_count,
        "ctx_accesses": ctx_access_count,
        "ratio_ctx_percent": round(ctx_access_count * 100 / max(get_default_count + ctx_access_count, 1), 1),
    }
    with open(os.path.join(raw_dir, "ctx_usage_ratio.json"), "w", encoding="utf-8") as f:
        json.dump(ctx_ratio, f, indent=2)

    rel_files = [_rel(f) for f in files]
    manifest = _generate_manifest(rel_files, output_dir)
    with open(os.path.join(raw_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Per-shard filtered copies (each shard's files determine which findings belong to it).
    for sid, shard_info in manifest["shards"].items():
        shard_files = set(shard_info["files"])

        def _filter(items: list[dict]) -> list[dict]:
            return [it for it in items if it.get("file") in shard_files]

        with open(os.path.join(raw_dir, f"singleton_sites_{sid}.json"), "w", encoding="utf-8") as f:
            json.dump(_filter(all_singleton_defs), f, indent=2)
        with open(os.path.join(raw_dir, f"module_mutables_{sid}.json"), "w", encoding="utf-8") as f:
            json.dump(_filter(all_module_mutables), f, indent=2)
        with open(os.path.join(raw_dir, f"global_usages_{sid}.json"), "w", encoding="utf-8") as f:
            json.dump(_filter(all_global_usages), f, indent=2)
        with open(os.path.join(raw_dir, f"class_mutable_defaults_{sid}.json"), "w", encoding="utf-8") as f:
            json.dump(_filter(all_class_mutable_defaults), f, indent=2)
        with open(os.path.join(raw_dir, f"random_seed_sites_{sid}.json"), "w", encoding="utf-8") as f:
            json.dump(_filter(all_random_seeds), f, indent=2)

        shard_get_default = sum(per_file_get_default.get(p, 0) for p in shard_files)
        shard_ctx = sum(per_file_ctx.get(p, 0) for p in shard_files)
        shard_ratio = {
            "get_default_calls": shard_get_default,
            "ctx_accesses": shard_ctx,
            "ratio_ctx_percent": round(shard_ctx * 100 / max(shard_get_default + shard_ctx, 1), 1),
        }
        with open(os.path.join(raw_dir, f"ctx_usage_ratio_{sid}.json"), "w", encoding="utf-8") as f:
            json.dump(shard_ratio, f, indent=2)

    print(f"  Singleton definitions:     {len(all_singleton_defs)}")
    print(f"  Module-level mutables:     {len(all_module_mutables)}")
    print(f"  global keyword usages:     {len(all_global_usages)}")
    print(f"  Class mutable defaults:    {len(all_class_mutable_defaults)}")
    print(f"  random.seed() outside RNG: {len(all_random_seeds)}")
    print(f"  get_default_xxx() calls:   {get_default_count}")
    print(f"  ctx.xxx accesses:          {ctx_access_count}")
    print(f"  ctx usage ratio:           {ctx_ratio['ratio_ctx_percent']}%")
    print()
    print(f"Phase 1 complete. Raw results: {raw_dir}")
    print(f"Output directory: {output_dir}")
    return output_dir


if __name__ == "__main__":
    run()

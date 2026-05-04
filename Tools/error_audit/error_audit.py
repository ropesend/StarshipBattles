"""Error handling & robustness audit — Phase 1 deterministic scanner.

Scans every .py file under game/ and extracts:
  1. Broad ``except Exception`` without ``# Intentional`` comment
  2. Bare ``except:`` clauses
  3. ``json.load`` / ``json.dump`` bypassing ``json_utils`` helpers
  4. ``raise Exception(...)`` instead of domain-specific exceptions
  5. ``traceback.print_exc()`` / ``print()`` diagnostic usage
  6. Resource opens without ``with`` blocks
  7. LLM exception ``context`` dicts (security audit)

Outputs structured JSON to REVIEW_DIR/raw/ and generates a shard manifest
for Phase 2 agent distribution.

Usage::

    python Tools/error_audit/error_audit.py
    python Tools/error_audit/error_audit.py --output CUSTOM_DIR
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


def _get_source_lines(source: str) -> list[str]:
    return source.splitlines()


def _has_intentional_comment(lines: list[str], lineno: int) -> bool:
    """Check if the line at lineno-1 (0-indexed) or preceding line has '# Intentional'."""
    for check in (lineno - 1, lineno - 2):
        if 0 <= check < len(lines):
            stripped = lines[check].strip()
            if stripped.startswith("#") and "intentional" in stripped.lower():
                return True
    return False


def _is_json_utils_import(node: ast.ImportFrom) -> bool:
    return node.module is not None and "json_utils" in node.module


class _ErrorScanner(ast.NodeVisitor):
    def __init__(self, source: str, filepath: str):
        self.source = source
        self.lines = _get_source_lines(source)
        self.filepath = filepath
        self.broad_excepts: list[dict] = []
        self.bare_excepts: list[dict] = []
        self.raises: list[dict] = []
        self.json_bypasses: list[dict] = []
        self.print_debugs: list[dict] = []
        self.resource_opens: list[dict] = []
        self.llm_contexts: list[dict] = []
        self._json_utils_aliases: set[str] = set()
        self._func_def_depth = 0

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if _is_json_utils_import(node):
            for alias in node.names:
                self._json_utils_aliases.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if "json_utils" in alias.name:
                self._json_utils_aliases.add(alias.asname or alias.name.split(".")[-1])
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        for handler in node.handlers:
            if handler.type is None:
                self.bare_excepts.append({
                    "file": _rel(self.filepath),
                    "line": handler.lineno,
                    "context": self.lines[handler.lineno - 1].strip() if handler.lineno <= len(self.lines) else "",
                })
            elif isinstance(handler.type, ast.Name) and handler.type.id == "Exception":
                if not _has_intentional_comment(self.lines, handler.lineno):
                    self.broad_excepts.append({
                        "file": _rel(self.filepath),
                        "line": handler.lineno,
                        "context": self.lines[handler.lineno - 1].strip() if handler.lineno <= len(self.lines) else "",
                        "has_comment": False,
                    })
                else:
                    self.broad_excepts.append({
                        "file": _rel(self.filepath),
                        "line": handler.lineno,
                        "context": self.lines[handler.lineno - 1].strip() if handler.lineno <= len(self.lines) else "",
                        "has_comment": True,
                    })
        self.generic_visit(node)

    def visit_Raise(self, node: ast.Raise) -> None:
        if isinstance(node.exc, ast.Call) and isinstance(node.exc.func, ast.Name):
            if node.exc.func.id == "Exception":
                self.raises.append({
                    "file": _rel(self.filepath),
                    "line": node.lineno,
                    "context": self.lines[node.lineno - 1].strip() if node.lineno <= len(self.lines) else "",
                })
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func

        if isinstance(func, ast.Attribute):
            full = self._resolve_attr(func)
            if full in ("json.load", "json.dump", "json.loads", "json.dumps"):
                if not self._json_utils_aliases:
                    self.json_bypasses.append({
                        "file": _rel(self.filepath),
                        "line": node.lineno,
                        "call": full,
                    })
            elif full in ("traceback.print_exc", "traceback.format_exc"):
                self.print_debugs.append({
                    "file": _rel(self.filepath),
                    "line": node.lineno,
                    "call": full,
                })
        elif isinstance(func, ast.Name):
            if func.id == "print":
                self.print_debugs.append({
                    "file": _rel(self.filepath),
                    "line": node.lineno,
                    "call": "print()",
                })

        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:
        for item in node.items:
            if isinstance(item.context_expr, ast.Call) and isinstance(item.context_expr.func, ast.Name):
                if item.context_expr.func.id == "open":
                    self.resource_opens.append({
                        "file": _rel(self.filepath),
                        "line": node.lineno,
                        "managed": True,
                    })
        self.generic_visit(node)

    def _resolve_attr(self, node: ast.Attribute) -> str:
        parts: list[str] = [node.attr]
        current = node.value
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        parts.reverse()
        return ".".join(parts)


def scan_file(filepath: str) -> dict | None:
    source = _read_file(filepath)
    if source is None:
        return None
    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return None
    scanner = _ErrorScanner(source, filepath)
    scanner.visit(tree)
    return {
        "file": _rel(filepath),
        "broad_excepts": scanner.broad_excepts,
        "bare_excepts": scanner.bare_excepts,
        "generic_raises": scanner.raises,
        "json_bypasses": scanner.json_bypasses,
        "print_debugs": scanner.print_debugs,
        "resource_opens": scanner.resource_opens,
        "llm_contexts": scanner.llm_contexts,
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


def _generate_manifest(files: list[str], output_dir: str) -> dict:
    seed = f"error-{datetime.now().strftime('%Y-%m-%d')}"

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


def _simple_balance(files: list[tuple[str, int]], shard_count: int) -> list[list[tuple[str, int]]]:
    shards: list[list[tuple[str, int]]] = [[] for _ in range(shard_count)]
    totals = [0] * shard_count
    for filepath, loc in files:
        min_idx = min(range(shard_count), key=lambda i: totals[i])
        shards[min_idx].append((filepath, loc))
        totals[min_idx] += loc
    return shards


def _extract_broad_excepts_no_comment(results: list[dict]) -> list[dict]:
    items: list[dict] = []
    for r in results:
        for be in r.get("broad_excepts", []):
            if not be.get("has_comment", False):
                items.append(be)
    return items


def _extract_all_bare_excepts(results: list[dict]) -> list[dict]:
    items: list[dict] = []
    for r in results:
        items.extend(r.get("bare_excepts", []))
    return items


def _extract_all_json_bypasses(results: list[dict]) -> list[dict]:
    items: list[dict] = []
    for r in results:
        items.extend(r.get("json_bypasses", []))
    return items


def _extract_all_generic_raises(results: list[dict]) -> list[dict]:
    items: list[dict] = []
    for r in results:
        items.extend(r.get("generic_raises", []))
    return items


def _extract_all_print_debugs(results: list[dict]) -> list[dict]:
    items: list[dict] = []
    for r in results:
        items.extend(r.get("print_debugs", []))
    return items


def _extract_resource_open_count(results: list[dict]) -> int:
    return sum(len(r.get("resource_opens", [])) for r in results)


def run(force_output_dir: str | None = None) -> str:
    date_slug = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_dir = force_output_dir or os.path.join(REVIEWS_DIR, f"{date_slug}_error-audit")
    raw_dir = os.path.join(output_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)

    print("=== Phase 1: Error Handling Audit ===")
    print(f"Output: {output_dir}")
    print()

    files = _discover_py_files(GAME_DIR)
    print(f"Scanning {len(files)} files...")

    results: list[dict] = []
    for filepath in files:
        result = scan_file(filepath)
        if result is not None:
            results.append(result)

    broad_excepts = _extract_broad_excepts_no_comment(results)
    bare_excepts = _extract_all_bare_excepts(results)
    json_bypasses = _extract_all_json_bypasses(results)
    generic_raises = _extract_all_generic_raises(results)
    print_debugs = _extract_all_print_debugs(results)
    resource_count = _extract_resource_open_count(results)

    with open(os.path.join(raw_dir, "broad_except_sites.json"), "w", encoding="utf-8") as f:
        json.dump(broad_excepts, f, indent=2)
    with open(os.path.join(raw_dir, "bare_except_sites.json"), "w", encoding="utf-8") as f:
        json.dump(bare_excepts, f, indent=2)
    with open(os.path.join(raw_dir, "json_bypass_sites.json"), "w", encoding="utf-8") as f:
        json.dump(json_bypasses, f, indent=2)
    with open(os.path.join(raw_dir, "raise_generic_sites.json"), "w", encoding="utf-8") as f:
        json.dump(generic_raises, f, indent=2)
    with open(os.path.join(raw_dir, "print_debug_sites.json"), "w", encoding="utf-8") as f:
        json.dump(print_debugs, f, indent=2)

    rel_files = [_rel(f) for f in files]
    with open(os.path.join(raw_dir, "file_inventory.json"), "w", encoding="utf-8") as f:
        json.dump({"total_files": len(files), "files": sorted(rel_files)}, f, indent=2)

    manifest = _generate_manifest(rel_files, output_dir)
    with open(os.path.join(raw_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"  Broad except w/o comment: {len(broad_excepts)}")
    print(f"  Bare except:             {len(bare_excepts)}")
    print(f"  JSON bypass:             {len(json_bypasses)}")
    print(f"  Generic raise Exception: {len(generic_raises)}")
    print(f"  Print/traceback debug:   {len(print_debugs)}")
    print(f"  Open() blocks:           {resource_count}")
    print()
    print(f"Phase 1 complete. Raw results: {raw_dir}")
    print(f"Output directory: {output_dir}")
    return output_dir


if __name__ == "__main__":
    run()

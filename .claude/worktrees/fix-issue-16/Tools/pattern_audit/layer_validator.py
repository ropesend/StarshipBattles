"""Layer dependency validator.

Parses import statements from all .py files under game/, maps each file to its
architectural layer, and checks imports against the dependency table defined in
docs/01_ARCHITECTURE.md.

Outputs layer_violations.json — every import that crosses a forbidden boundary.

Usage::

    python Tools/pattern_audit/layer_validator.py --output PATH/TO/raw/
"""

from __future__ import annotations

import ast
import json
import os
import sys
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

sys.path.insert(0, PROJECT_ROOT)

ALLOWED_DEPENDENCIES: dict[str, frozenset[str]] = {
    "core":       frozenset(),
    "services":   frozenset({"core"}),
    "assets":     frozenset({"core", "services"}),
    "engine":     frozenset({"core", "services"}),
    "research":   frozenset({"core", "services"}),
    "simulation": frozenset({"core", "services", "engine"}),
    "ai":         frozenset({"core", "services", "engine", "simulation"}),
    "strategy":   frozenset({"core", "services", "engine", "simulation"}),
    "ui":         frozenset({"core", "services", "assets", "engine", "research", "simulation", "ai", "strategy"}),
}

LAYER_PATH_PREFIXES: dict[str, str] = {
    "game/core": "core",
    "game/services": "services",
    "game/assets": "assets",
    "game/engine": "engine",
    "game/research": "research",
    "game/simulation": "simulation",
    "game/ai": "ai",
    "game/strategy": "strategy",
    "game/ui": "ui",
}


def _rel(path: str) -> str:
    return os.path.relpath(path, PROJECT_ROOT).replace("\\", "/")


def _file_layer(filepath: str) -> str:
    rel = _rel(filepath).replace("\\", "/")
    for prefix, layer in sorted(LAYER_PATH_PREFIXES.items(), key=lambda x: -len(x[0])):
        if rel.startswith(prefix + "/") or rel == prefix:
            return layer
    return "unknown"


def _import_layer(import_name: str) -> str | None:
    for prefix, layer in sorted(LAYER_PATH_PREFIXES.items(), key=lambda x: -len(x[0])):
        if import_name == prefix or import_name.startswith(prefix + "."):
            return layer
    return None


class _ImportExtractor(ast.NodeVisitor):
    def __init__(self, filepath: str, file_layer: str):
        self.filepath = filepath
        self.file_layer = file_layer
        self.imports: list[dict] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            target_layer = _import_layer(alias.name)
            if target_layer and target_layer not in ALLOWED_DEPENDENCIES.get(self.file_layer, frozenset()):
                self.imports.append({
                    "file": _rel(self.filepath),
                    "line": node.lineno,
                    "from_layer": self.file_layer,
                    "to_layer": target_layer,
                    "import": alias.name,
                    "type": "import",
                })
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module is None:
            return
        target_layer = _import_layer(node.module)
        if target_layer and target_layer not in ALLOWED_DEPENDENCIES.get(self.file_layer, frozenset()):
            self.imports.append({
                "file": _rel(self.filepath),
                "line": node.lineno,
                "from_layer": self.file_layer,
                "to_layer": target_layer,
                "import": node.module,
                "type": "import_from",
            })
        self.generic_visit(node)


def scan_file(filepath: str) -> list[dict]:
    try:
        with open(filepath, encoding="utf-8", errors="replace") as f:
            source = f.read()
    except OSError:
        return []

    layer = _file_layer(filepath)
    if layer == "unknown":
        return []

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return []

    extractor = _ImportExtractor(filepath, layer)
    extractor.visit(tree)
    return extractor.imports


def _discover_py_files(root: str) -> list[str]:
    results: list[str] = []
    for dirpath, _, filenames in os.walk(root):
        if "__pycache__" in dirpath:
            continue
        for fname in filenames:
            if fname.endswith(".py") and not fname.startswith("__"):
                results.append(os.path.join(dirpath, fname))
    return results


def run(raw_dir: str) -> dict:
    files = _discover_py_files(GAME_DIR)
    all_violations: list[dict] = []

    for filepath in files:
        violations = scan_file(filepath)
        all_violations.extend(violations)

    known_bridges = (
        ("game/simulation", "game/strategy"),
    )
    filtered: list[dict] = []
    false_positives: list[dict] = []

    for v in all_violations:
        pair = (v["from_layer"], v["to_layer"])
        if pair in known_bridges:
            false_positives.append(v)
        else:
            filtered.append(v)

    summary = {
        "total_files_scanned": len(files),
        "total_violations": len(all_violations),
        "filtered_violations": len(filtered),
        "known_intentional_bridges": len(false_positives),
        "violations": filtered,
        "intentional_bridges": false_positives,
    }

    output_path = os.path.join(raw_dir, "layer_violations.json")
    os.makedirs(raw_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary


if __name__ == "__main__":
    output = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        PROJECT_ROOT, "Reviews", "results", "_layer_out", "raw"
    )
    result = run(output)
    print(f"Files scanned:    {result['total_files_scanned']}")
    print(f"Violations:       {result['total_violations']} total")
    print(f"  Filtered:       {result['filtered_violations']}")
    print(f"  Intentional:    {result['known_intentional_bridges']}")
    print(f"Output: {os.path.join(output, 'layer_violations.json')}")

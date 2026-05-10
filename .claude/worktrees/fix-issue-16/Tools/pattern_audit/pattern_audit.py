"""Pattern conformance & architecture drift audit — Phase 1 orchestrator.

Runs:
  1. Layer validator (forbidden import detection)
  2. LOC baseline (via Tools/loc/loc.py)
  3. File size checker (500-LOC ceiling)
  4. Singleton site extractor (from state_audit, for context)
  5. Protocol registry scanner (Protocol classes + TypeGuard presence)
  6. Shard manifest generator

Outputs structured JSON to REVIEW_DIR/raw/.

Usage::

    python Tools/pattern_audit/pattern_audit.py
    python Tools/pattern_audit/pattern_audit.py --output CUSTOM_DIR
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
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
TOOLS_DIR = os.path.join(PROJECT_ROOT, "Tools")
PATTERN_DIR = os.path.join(TOOLS_DIR, "pattern_audit")

sys.path.insert(0, PROJECT_ROOT)


def _rel(path: str) -> str:
    return os.path.relpath(path, PROJECT_ROOT).replace("\\", "/")


def _run_tool(cmd: list[str], output_file: str | None, label: str) -> bool:
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60, cwd=PROJECT_ROOT,
        )
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result.stdout)
                if result.stderr:
                    f.write("\n\n--- STDERR ---\n")
                    f.write(result.stderr)
        status = "OK" if result.returncode == 0 else f"FAILED (exit {result.returncode})"
        print(f"  [{status}] {label}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"  [TIMEOUT] {label}")
        return False
    except OSError as e:
        print(f"  [MISSING] {label} — {e}")
        return False


def _scan_protocol_registry(raw_dir: str) -> dict:
    """Find Protocol classes and check for corresponding TypeGuard functions."""
    protocols: list[dict] = []
    files = []
    for dirpath, _, filenames in os.walk(GAME_DIR):
        if "__pycache__" in dirpath:
            continue
        for fname in filenames:
            if fname.endswith(".py"):
                files.append(os.path.join(dirpath, fname))

    for filepath in files:
        try:
            with open(filepath, encoding="utf-8", errors="replace") as f:
                source = f.read()
        except OSError:
            continue
        try:
            tree = ast.parse(source, filename=filepath)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == "Protocol":
                        protocols.append({
                            "class": node.name,
                            "file": _rel(filepath),
                            "line": node.lineno,
                        })

    typeguards: dict[str, list[str]] = {}
    for filepath in files:
        try:
            with open(filepath, encoding="utf-8", errors="replace") as f:
                source = f.read()
        except OSError:
            continue
        try:
            tree = ast.parse(source, filename=filepath)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith("is_") or node.name.endswith("_guard") or "TypeGuard" in str(ast.unparse(node.returns) if node.returns else ""):
                    if node.returns:
                        returns_str = ast.unparse(node.returns)
                        if "TypeGuard" in returns_str:
                            typeguards.setdefault(node.name, []).append(_rel(filepath))

    result = {
        "protocols_found": len(protocols),
        "protocols": protocols,
        "typeguards_found": len(typeguards),
    }
    out_path = os.path.join(raw_dir, "protocol_registry.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    return result


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
    seed = f"pattern-{datetime.now().strftime('%Y-%m-%d')}"
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
    output_dir = force_output_dir or os.path.join(REVIEWS_DIR, f"{date_slug}_pattern-audit")
    raw_dir = os.path.join(output_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)

    print("=== Phase 1: Pattern Conformance Audit ===")
    print(f"Output: {output_dir}")
    print()

    print("1. Layer dependency validator...")
    layer_path = os.path.join(PATTERN_DIR, "layer_validator.py")
    result = subprocess.run(
        [sys.executable, layer_path, "--output", raw_dir],
        capture_output=True, text=True, timeout=60, cwd=PROJECT_ROOT,
    )
    print(result.stdout.strip())

    print("2. LOC baseline...")
    _run_tool(
        [sys.executable, os.path.join(TOOLS_DIR, "loc", "loc.py"), "--detailed"],
        os.path.join(raw_dir, "loc_baseline.json"),
        "loc",
    )

    print("3. File size checker (500-LOC ceiling)...")
    size_tool = os.path.join(TOOLS_DIR, "check_file_size", "check_file_size.py")
    _run_tool(
        [sys.executable, size_tool],
        os.path.join(raw_dir, "file_size_violations.txt"),
        "check_file_size",
    )

    print("4. Protocol registry scanner...")
    proto_result = _scan_protocol_registry(raw_dir)
    print(f"  Protocols found: {proto_result['protocols_found']}")

    print("5. Manifest + shard assignments...")
    files = [os.path.join(dirpath, fname).replace("\\", "/")
             for dirpath, _, filenames in os.walk(GAME_DIR)
             for fname in filenames
             if fname.endswith(".py") and "__pycache__" not in dirpath]
    rel_files = [_rel(f) for f in files]
    manifest = _generate_manifest(rel_files, output_dir)
    with open(os.path.join(raw_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print()
    print(f"Phase 1 complete. Raw results: {raw_dir}")
    print(f"Output directory: {output_dir}")
    return output_dir


if __name__ == "__main__":
    force_dir = sys.argv[1] if len(sys.argv) > 1 else None
    run(force_dir)

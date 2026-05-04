"""Documentation freshness & accuracy audit — Phase 1 deterministic scanner.

Extracts and cross-references all references from docs/ against live code:
  1. ``game/*`` file references validated against filesystem
  2. PROJ references cross-referenced against projects_index.md
  3. Doc staleness scoring from "Last verified" timestamps
  4. Undocumented modules (production .py files > 50 LOC with no doc mention)
  5. Doc file inventory for Phase 2 agent sharding

Outputs structured JSON to REVIEW_DIR/raw/.

Usage::

    python Tools/docs_audit/docs_audit.py
    python Tools/docs_audit/docs_audit.py --output CUSTOM_DIR
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def _find_project_root() -> str:
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "game").is_dir() and (current / "data").is_dir():
            return str(current)
        current = current.parent
    raise RuntimeError("Could not find project root")


PROJECT_ROOT = _find_project_root()
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")
REVIEWS_DIR = os.path.join(PROJECT_ROOT, "Reviews", "results")
PROJECTS_INDEX = os.path.join(PROJECT_ROOT, "Projects", "projects_index.md")
GAME_DIR = os.path.join(PROJECT_ROOT, "game")

sys.path.insert(0, PROJECT_ROOT)

DOC_FILES = [
    "README.md", "01_ARCHITECTURE.md", "02_PATTERNS.md", "03_CONVENTIONS.md",
    "04_SERVICES.md", "05_ERROR_HANDLING.md", "06_UI_STYLE_GUIDE.md",
]
DOC_DIRS: list[tuple[str, str]] = [
    ("systems", "docs/systems"),
    ("guides", "docs/guides"),
]
EXTRA_DOCS = ["AGENTS.md", "CLAUDE.md", ".agents/CODEX.md"]


def _rel(path: str) -> str:
    return os.path.relpath(path, PROJECT_ROOT).replace("\\", "/")


def _read_file(path: str) -> str | None:
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def extract_file_references(doc_path: str) -> list[dict]:
    content = _read_file(doc_path)
    if content is None:
        return []

    refs: list[dict] = []
    pattern = re.compile(r'(game/[\w/]+(?:\.py|\w+/))')
    for match in pattern.finditer(content):
        ref_path = match.group(1)
        line_no = content[:match.start()].count("\n") + 1
        exists = os.path.exists(os.path.join(PROJECT_ROOT, ref_path))
        refs.append({
            "doc": _rel(doc_path),
            "line": line_no,
            "reference": ref_path,
            "exists": exists,
        })
    return refs


def extract_proj_references(doc_path: str) -> list[dict]:
    content = _read_file(doc_path)
    if content is None:
        return []

    project_statuses = _load_project_statuses()
    refs: list[dict] = []
    pattern = re.compile(r'\b(PROJ-\d{3})\b')
    for match in pattern.finditer(content):
        proj_id = match.group(1)
        line_no = content[:match.start()].count("\n") + 1
        status = project_statuses.get(proj_id, "unknown")
        refs.append({
            "doc": _rel(doc_path),
            "line": line_no,
            "proj": proj_id,
            "current_status": status,
        })
    return refs


def _load_project_statuses() -> dict[str, str]:
    content = _read_file(PROJECTS_INDEX)
    if content is None:
        return {}
    statuses: dict[str, str] = {}
    pattern = re.compile(r'\|\s*(PROJ-\d{3})\s*\|\s*([^|]+?)\s*\|')
    for match in pattern.finditer(content):
        statuses[match.group(1)] = match.group(2).strip()
    return statuses


def extract_staleness(doc_path: str) -> dict | None:
    content = _read_file(doc_path)
    if content is None:
        return None
    match = re.search(r'Last verified:\s*(\d{4}-\d{2}-\d{2})', content)
    if match:
        date_str = match.group(1)
        try:
            last_verified = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            days = (datetime.now(timezone.utc) - last_verified).days
            return {
                "doc": _rel(doc_path),
                "last_verified": date_str,
                "days_stale": days,
                "stale": days > 60,
            }
        except ValueError:
            return {"doc": _rel(doc_path), "last_verified": date_str, "days_stale": -1, "stale": False}
    return {"doc": _rel(doc_path), "last_verified": None, "days_stale": -1, "stale": False}


def find_undocumented_modules() -> list[dict]:
    all_doc_content = ""
    for root, _, filenames in os.walk(DOCS_DIR):
        if "_ignore" in Path(root).parts:
            continue
        for fname in filenames:
            if fname.endswith(".md"):
                content = _read_file(os.path.join(root, fname))
                if content:
                    all_doc_content += content
    for extra in EXTRA_DOCS:
        content = _read_file(os.path.join(PROJECT_ROOT, extra))
        if content:
            all_doc_content += content

    undocumented: list[dict] = []
    for dirpath, _, filenames in os.walk(GAME_DIR):
        if "__pycache__" in dirpath:
            continue
        for fname in filenames:
            if not fname.endswith(".py") or fname.startswith("__"):
                continue
            filepath = os.path.join(dirpath, fname)
            rel = _rel(filepath)
            try:
                loc = sum(1 for _ in open(filepath, encoding="utf-8", errors="replace"))
            except OSError:
                continue
            if loc <= 50:
                continue
            module_name = rel.replace("/", ".").replace(".py", "")
            module_short = os.path.splitext(fname)[0]
            if module_short not in all_doc_content and fname not in all_doc_content:
                undocumented.append({
                    "module": rel,
                    "loc": loc,
                    "dir": _rel(dirpath),
                })

    return undocumented


def build_doc_inventory() -> list[dict]:
    inventory: list[dict] = []
    for fname in DOC_FILES:
        path = os.path.join(DOCS_DIR, fname)
        content = _read_file(path)
        if content:
            headings = re.findall(r'^#{1,3}\s+(.+)$', content, re.MULTILINE)
            inventory.append({
                "doc": f"docs/{fname}",
                "group": "architecture",
                "headings": headings[:10],
                "loc": content.count("\n"),
            })

    for group, dir_rel in DOC_DIRS:
        dir_path = os.path.join(PROJECT_ROOT, dir_rel)
        if os.path.isdir(dir_path):
            for fname in sorted(os.listdir(dir_path)):
                if fname.endswith(".md"):
                    path = os.path.join(dir_path, fname)
                    content = _read_file(path)
                    if content:
                        headings = re.findall(r'^#{1,3}\s+(.+)$', content, re.MULTILINE)
                        inventory.append({
                            "doc": f"{dir_rel}/{fname}",
                            "group": group,
                            "headings": headings[:10],
                            "loc": content.count("\n"),
                        })

    for extra in EXTRA_DOCS:
        path = os.path.join(PROJECT_ROOT, extra)
        content = _read_file(path)
        if content:
            headings = re.findall(r'^#{1,3}\s+(.+)$', content, re.MULTILINE)
            inventory.append({
                "doc": extra,
                "group": "root",
                "headings": headings[:10],
                "loc": content.count("\n"),
            })

    return inventory


def run(force_output_dir: str | None = None) -> str:
    date_slug = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_dir = force_output_dir or os.path.join(REVIEWS_DIR, f"{date_slug}_docs-audit")
    raw_dir = os.path.join(output_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)

    print("=== Phase 1: Documentation Freshness Audit ===")
    print(f"Output: {output_dir}")
    print()

    all_refs: list[dict] = []
    all_proj_refs: list[dict] = []
    staleness: list[dict] = []

    all_doc_paths: list[str] = []
    for fname in DOC_FILES:
        all_doc_paths.append(os.path.join(DOCS_DIR, fname))
    for _, dir_rel in DOC_DIRS:
        dir_path = os.path.join(PROJECT_ROOT, dir_rel)
        if os.path.isdir(dir_path):
            for fname in os.listdir(dir_path):
                if fname.endswith(".md"):
                    all_doc_paths.append(os.path.join(dir_path, fname))
    for extra in EXTRA_DOCS:
        all_doc_paths.append(os.path.join(PROJECT_ROOT, extra))

    print(f"Scanning {len(all_doc_paths)} doc files...")
    for path in all_doc_paths:
        refs = extract_file_references(path)
        all_refs.extend(refs)
        proj_refs = extract_proj_references(path)
        all_proj_refs.extend(proj_refs)
        st = extract_staleness(path)
        if st:
            staleness.append(st)

    dead_refs = [r for r in all_refs if not r["exists"]]
    stale_proj_refs = [r for r in all_proj_refs if r["current_status"] in ("Complete", "Archived", "Abandoned")]

    print("Finding undocumented modules...")
    undocumented = find_undocumented_modules()

    print("Building doc inventory...")
    inventory = build_doc_inventory()

    with open(os.path.join(raw_dir, "doc_file_refs.json"), "w", encoding="utf-8") as f:
        json.dump({"total": len(all_refs), "dead_refs": dead_refs, "all_refs": all_refs}, f, indent=2)
    with open(os.path.join(raw_dir, "stale_proj_refs.json"), "w", encoding="utf-8") as f:
        json.dump({"total": len(all_proj_refs), "stale": stale_proj_refs, "all": all_proj_refs}, f, indent=2)
    with open(os.path.join(raw_dir, "doc_staleness.json"), "w", encoding="utf-8") as f:
        json.dump(staleness, f, indent=2)
    with open(os.path.join(raw_dir, "undocumented_modules.json"), "w", encoding="utf-8") as f:
        json.dump({"count": len(undocumented), "modules": undocumented}, f, indent=2)
    with open(os.path.join(raw_dir, "doc_inventory.json"), "w", encoding="utf-8") as f:
        json.dump({"total_docs": len(inventory), "docs": inventory}, f, indent=2)

    print(f"  File refs: {len(all_refs)} total, {len(dead_refs)} dead")
    print(f"  PROJ refs: {len(all_proj_refs)} total, {len(stale_proj_refs)} stale")
    print(f"  Stale docs: {sum(1 for s in staleness if s.get('stale', False))}")
    print(f"  Undocumented modules: {len(undocumented)}")
    print(f"  Doc inventory: {len(inventory)} files")
    print()
    print(f"Phase 1 complete. Raw results: {raw_dir}")
    print(f"Output directory: {output_dir}")
    return output_dir


if __name__ == "__main__":
    run()

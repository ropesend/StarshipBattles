"""Detect Python modules under game/ that are never imported by any other
game/ module.

Uses the AST so it correctly handles:
  - ``from game.X.Y import Z``       (absolute)
  - ``import game.X.Y``              (absolute)
  - ``from .X import Y``             (relative, same package)
  - ``from ..pkg import X``          (relative, parent package)

Recognized non-orphan exemptions:
  - Top-level entry points and bootstrap files in ``game/``
  - Package ``__init__`` modules (imported as the package, not by name)

Output: prints a count and the orphaned module names (relative to game/).
"""

from __future__ import annotations

import ast
import sys
from collections import defaultdict
from pathlib import Path


def _find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "game").is_dir() and (current / "data").is_dir():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")


_PROJECT_ROOT = _find_project_root()
sys.path.insert(0, str(_PROJECT_ROOT))

from game.core.paths import Paths  # noqa: E402

GAME_DIR = Path(Paths.GAME_DIR)


# Modules that are entry points or are loaded by the runtime via top-level
# import (game.app etc.) — they are imported but the importer is not under
# game/ so the cross-game scan misses them.
ENTRY_POINTS: set[str] = {
    "app",
    "app_bootstrap",
    "context",
    "exit_dialog",
    "run_loop",
    "screen_router",
    "__init__",
}


def _module_key(rel_path: Path) -> str:
    """Convert a path relative to game/ into a slash-separated module key.

    e.g. core/registry.py    -> "core/registry"
         core/__init__.py    -> "core/__init__"
         app.py              -> "app"
    """
    s = str(rel_path).replace("\\", "/")
    if s.endswith(".py"):
        s = s[:-3]
    return s


def _resolve_absolute(modname: str, all_modules: set[str]) -> list[str]:
    """``modname`` is a dotted absolute name like ``game.core.registry``.

    Returns the matching module keys (zero or more). Submodule package
    imports are matched too — ``game.core`` resolves to ``core/__init__``
    if present, plus we mark every direct child as imported via the package.
    """
    if not modname.startswith("game."):
        return []
    rel = modname[len("game."):].replace(".", "/")
    matches: list[str] = []
    if rel in all_modules:
        matches.append(rel)
    # If `game.core` is imported, treat its __init__ as imported.
    init_key = f"{rel}/__init__"
    if init_key in all_modules:
        matches.append(init_key)
    return matches


def _resolve_relative(level: int, modname: str | None, current_key: str, all_modules: set[str]) -> list[str]:
    """Resolve ``from .X import Y`` style imports.

    ``current_key`` is the slash-separated module key of the importing file.
    Walks ``level`` parent directories from the importer, then appends
    ``modname`` (if any). Returns matching module keys.
    """
    parts = current_key.split("/")
    # Drop the file part (importer is a file, not a package). For __init__
    # files, drop the __init__ leaf so `.X` resolves to siblings of the package.
    if parts[-1] == "__init__":
        parts = parts[:-1]
    else:
        parts = parts[:-1]
    # Each extra dot beyond level=1 means one more parent.
    for _ in range(level - 1):
        if not parts:
            return []
        parts = parts[:-1]
    base = "/".join(parts) if parts else ""
    if modname:
        target = f"{base}/{modname.replace('.', '/')}" if base else modname.replace(".", "/")
    else:
        target = base
    target = target.lstrip("/")
    matches: list[str] = []
    if target in all_modules:
        matches.append(target)
    init_key = f"{target}/__init__" if target else "__init__"
    if init_key in all_modules:
        matches.append(init_key)
    return matches


def _imports_from_file(py_file: Path, current_key: str, all_modules: set[str]) -> set[str]:
    """Return the set of module keys imported by ``py_file``."""
    try:
        source = py_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(py_file))
    except Exception:
        return set()

    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.update(_resolve_absolute(alias.name, all_modules))
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                base_keys = _resolve_relative(node.level, node.module, current_key, all_modules)
                found.update(base_keys)
                # Each name in the import list might itself be a submodule.
                if node.module is not None:
                    for alias in node.names:
                        if alias.name == "*":
                            continue
                        sub = (node.module + "." + alias.name)
                        found.update(_resolve_relative(node.level, sub, current_key, all_modules))
                else:
                    for alias in node.names:
                        if alias.name == "*":
                            continue
                        found.update(_resolve_relative(node.level, alias.name, current_key, all_modules))
            elif node.module:
                found.update(_resolve_absolute(node.module, all_modules))
                # `from game.pkg import submod` should also count submod as imported.
                for alias in node.names:
                    if alias.name == "*":
                        continue
                    found.update(_resolve_absolute(f"{node.module}.{alias.name}", all_modules))
    return found


def main() -> int:
    all_files: dict[str, Path] = {}
    for py_file in sorted(GAME_DIR.rglob("*.py")):
        rel = py_file.relative_to(GAME_DIR)
        all_files[_module_key(rel)] = py_file

    all_modules = set(all_files.keys())
    imported_by: dict[str, list[str]] = defaultdict(list)

    for module_key, py_file in all_files.items():
        for target in _imports_from_file(py_file, module_key, all_modules):
            imported_by[target].append(module_key)

    orphaned: list[str] = []
    for module_key in sorted(all_modules):
        # Strip __init__ — packages are imported as the package name.
        is_init = module_key.endswith("/__init__") or module_key == "__init__"
        if is_init:
            continue
        leaf = module_key.split("/")[-1]
        if leaf in ENTRY_POINTS:
            continue
        if module_key in imported_by:
            continue
        orphaned.append(module_key)

    print(f"Orphaned modules: {len(orphaned)}")
    for mod in orphaned[:50]:
        print(f"  {mod}")
    if len(orphaned) > 50:
        print(f"  ... and {len(orphaned) - 50} more")

    return 0


if __name__ == "__main__":
    sys.exit(main())

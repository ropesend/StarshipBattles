"""PROJ-372: AST guard preventing direct reads of Galaxy private indexes.

The five private indexes — `_global_hex_planets`, `_global_hex_zones`,
`_zone_to_system`, `_planet_to_system`, `_global_hex_warp_points` — are
legacy compatibility properties. All call sites must go through public
methods on Galaxy, the relevant service, or GalaxyState's non-underscore
indexes.

Phase 3 introduced `GalaxyState` and renamed the indexes (dropped the
leading underscore). This guard now pins the old underscore names as
compatibility-only surfaces that external callers must not read, except
for the explicit grandfathered sites tracked below.

The walker scans every `*.py` under `game/` and asserts no
`Attribute(value=Name|Attribute(...), attr='_global_hex_planets')` etc.
appears in disallowed files.
"""
from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
GAME_ROOT = REPO_ROOT / "game"

# These attrs must not be read outside the allow-listed files.
RESTRICTED_ATTRS = frozenset(
    {
        "_global_hex_planets",
        "_global_hex_zones",
        "_zone_to_system",
        "_planet_to_system",
        "_global_hex_warp_points",
    }
)

# No file should read the legacy underscore properties directly. Galaxy's
# compatibility property definitions are FunctionDef nodes, not Attribute reads,
# so they do not need an allowlist entry.
ALLOWED_FILES = frozenset()

# PROJ-372 Phase 0 discovery: five external read sites the architect's
# initial review missed. Captured here so today's baseline ships green;
# each tuple is precise so new reads still fail.
GRANDFATHERED_EXTERNAL_READS = frozenset(
    {
        ("game/strategy/engine/handlers/movement.py", "_global_hex_warp_points"),
        ("game/strategy/services/fleet_navigation_service.py", "_global_hex_warp_points"),
        ("game/ui/screens/strategy_render/hex_outlines.py", "_global_hex_warp_points"),
        ("game/ui/screens/strategy_render/hex_outlines.py", "_global_hex_planets"),
        ("game/ui/screens/strategy_render/hex_outlines.py", "_global_hex_zones"),
    }
)


def _iter_py_files(root: Path):
    for path in root.rglob("*.py"):
        # Skip __pycache__ etc.
        if "__pycache__" in path.parts:
            continue
        yield path


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _find_violations(path: Path) -> list[tuple[int, str]]:
    """Return (lineno, attr) tuples where the file reads a restricted attr."""
    src = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError:
        return []
    violations: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr in RESTRICTED_ATTRS:
            violations.append((node.lineno, node.attr))
    return violations


def test_no_external_reads_of_galaxy_private_indexes() -> None:
    bad: dict[str, list[tuple[int, str]]] = {}
    for path in _iter_py_files(GAME_ROOT):
        rel = _rel(path)
        if rel in ALLOWED_FILES:
            continue
        viols = _find_violations(path)
        # Filter out grandfathered (file, attr) pairs.
        non_grandfathered = [
            (lineno, attr) for lineno, attr in viols
            if (rel, attr) not in GRANDFATHERED_EXTERNAL_READS
        ]
        if non_grandfathered:
            bad[rel] = non_grandfathered

    if bad:
        lines = ["Disallowed reads of Galaxy private indexes:"]
        for fp, viols in sorted(bad.items()):
            for lineno, attr in viols:
                lines.append(f"  {fp}:{lineno} reads `.{attr}`")
        lines.append(
            "Allowed files: " + ", ".join(sorted(ALLOWED_FILES)) + ". "
            "Route through Galaxy public methods or the registry / spatial / "
            "warp-generator services. PROJ-372."
        )
        raise AssertionError("\n".join(lines))


def test_allowed_files_actually_use_at_least_one_index() -> None:
    """Sanity check the allow-list — every entry should reference at least
    one restricted attr (otherwise it's stale and should be pruned).

    Kept even though the current allow-list is empty, so future deliberate
    exceptions cannot silently go stale."""
    for rel in ALLOWED_FILES:
        path = REPO_ROOT / rel
        assert path.exists(), f"Stale allow-list entry: {rel}"
        viols = _find_violations(path)
        assert viols, (
            f"Allow-listed file {rel} does not actually read any restricted "
            "attr. Either remove it from ALLOWED_FILES or restore the usage."
        )

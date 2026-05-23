"""PROJ-372 / PROJ-387 / PROJ-394: AST guard against reintroducing
Galaxy private-index forwarders.

PROJ-372 Phase 3 extracted ``GalaxyState`` and renamed the five spatial
indexes — ``_global_hex_planets``, ``_global_hex_zones``,
``_zone_to_system``, ``_planet_to_system``, ``_global_hex_warp_points`` —
to their non-underscore counterparts on ``GalaxyState``. The original
underscore-prefixed names lived on as ``@property`` forwarders on
``Galaxy`` for the five grandfathered external read sites.

PROJ-387 deleted those five forwarders entirely after migrating every
caller to ``galaxy._state.<field>``. PROJ-394 then promoted access to a
public ``Galaxy.state`` property and migrated remaining callers to
``galaxy.state.<field>``.

This guard now defends against any reintroduction of the legacy
underscore names: the walker scans every ``*.py`` under ``game/`` and
asserts no ``Attribute(attr='_global_hex_planets')`` etc. appears
anywhere. ``GRANDFATHERED_EXTERNAL_READS`` is intentionally empty after
PROJ-394; it is preserved as the API for surfacing future grandfathered
reads if any are ever needed.
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

# PROJ-394 emptied this after PROJ-387 deleted the forwarders. Kept as
# the API for surfacing future grandfathered reads if any are ever needed.
GRANDFATHERED_EXTERNAL_READS: frozenset[tuple[str, str]] = frozenset()


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



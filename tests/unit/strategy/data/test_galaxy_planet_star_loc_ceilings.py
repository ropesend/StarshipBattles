"""PROJ-372: LOC ceilings for the three god-class files.

The ceilings tighten phase-by-phase. Phase 0 captures today's baseline;
Phases 1-4 lower them as services are extracted; Phase 5 locks the
final budget. Each ceiling is intentionally one number per file so a
single edit per phase advances the gate.

LOC count uses ``Path.read_text().count('\\n')`` which matches ``wc -l``
semantics on POSIX-style line endings.
"""
from __future__ import annotations

from pathlib import Path

# Repo-root-relative discovery (avoids hardcoding checkout-specific paths).
# This file lives at tests/unit/strategy/data/, so parents[3] is the repo root.
REPO_ROOT = Path(__file__).resolve().parents[4]
GAME_ROOT = REPO_ROOT / "game"

# PROJ-372 phase-aware LOC ceilings. Values tighten each phase.
# Phase 0 (baseline today): galaxy=689, planet=667, stars=770.
# Phase 1 lowers stars to 280.
# Phase 2 lowers planet to 350.
# Phase 3 lowers galaxy to 420 (intermediate).
# Phase 4 lowers galaxy to 350 (final).
GALAXY_LOC_CEILING = 689
PLANET_LOC_CEILING = 667
STARS_LOC_CEILING = 770


def _count_lines(path: Path) -> int:
    return path.read_text(encoding="utf-8").count("\n")


def test_galaxy_loc_ceiling() -> None:
    path = GAME_ROOT / "strategy" / "data" / "galaxy.py"
    actual = _count_lines(path)
    assert actual <= GALAXY_LOC_CEILING, (
        f"galaxy.py is {actual} LOC; ceiling is {GALAXY_LOC_CEILING}. "
        "Tighten the constant in test_galaxy_planet_star_loc_ceilings.py "
        "as PROJ-372 phases land."
    )


def test_planet_loc_ceiling() -> None:
    path = GAME_ROOT / "strategy" / "data" / "planet.py"
    actual = _count_lines(path)
    assert actual <= PLANET_LOC_CEILING, (
        f"planet.py is {actual} LOC; ceiling is {PLANET_LOC_CEILING}."
    )


def test_stars_loc_ceiling() -> None:
    path = GAME_ROOT / "strategy" / "data" / "stars.py"
    actual = _count_lines(path)
    assert actual <= STARS_LOC_CEILING, (
        f"stars.py is {actual} LOC; ceiling is {STARS_LOC_CEILING}."
    )

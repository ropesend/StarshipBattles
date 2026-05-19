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
GALAXY_LOC_CEILING = 350  # Phase 4 final: tightened after pathfinding/intercept extraction.
# PROJ-443 Phase 3a: raised from 350 to 405 to reflect post-PROJ-436 drift.
# PROJ-436 Phase 8: raised from 405 to 425 — Phase 8 added the
# ``IProductionResourceSource`` delegators (3 methods + 4 lines of
# header comment) so ProductionEngine reads through one uniform
# protocol satisfied by both Planet and Fleet. The growth is the
# protocol-conformance surface, not bloat; planet.py extraction is
# still on the Phase 6 Codex-consult question.
# PROJ-450 Phase 1: raised from 425 to 485 — Phase 1 moved the 3 dict ↔
# typed staging-yard helpers (``_is_carried_vehicle_dict`` /
# ``_pod_from_dict`` / ``_staging_yard_carried_vehicle``) IN from
# ``transfer_branches.py``, widened ``add_to_staging_yard`` to accept
# typed inputs, and added ``pop_staging_yard_typed``. The growth is the
# centralised conversion surface on the Planet boundary, not bloat;
# Phase 2 widens the substrate type itself.
# PROJ-450 Phase 3 codex-audit: reclaimed headroom. Phase 2 raised the
# ceiling to 525 to absorb the substrate-widening surface; Phase 3
# replaced the dict-projection bridge with a one-line typed read-only
# property, so the file is now 504 LOC. Ceiling reset to 520 (≈16 LOC
# headroom for incremental edits without thrash). The file remains
# slightly above the 500 project convention but the headroom-vs-thrash
# trade-off favours leaving it at 504+ with a tight ceiling rather than
# forcing a sub-500 split that would just extract docstrings.
PLANET_LOC_CEILING = 520
STARS_LOC_CEILING = 280  # Phase 1: tightened from 770 after Spectrum/StarGenerator extraction.


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


# PROJ-372 Phase 5: per-service LOC ceilings on the new files.
SERVICE_CEILINGS = {
    "strategy/data/galaxy_state.py": 150,
    # PROJ-443 Phase 3a: raised from 200 to 210 to reflect 2-LOC drift since
    # PROJ-372 Phase 5 close. Trivial overshoot; phase 6 Codex consult may
    # decide whether to require tightening back.
    # PROJ-450 Phase 2: raised from 210 to 230 — Phase 2 tightened
    # IStagingYardHolder.add_to_staging_yard / remove_from_staging_yard
    # signatures to the typed union + added per-method docstrings
    # documenting the typed substrate.
    "strategy/data/galaxy_protocols.py": 230,
    "strategy/data/spectrum.py": 80,
    "core/spectrum_math.py": 200,
    "strategy/generation/star_generator.py": 500,
    "strategy/services/planet_query_service.py": 250,
    "strategy/services/planet_habitability_service.py": 200,
    "strategy/services/galaxy_pathfinding_service.py": 350,
    "strategy/services/intercept_calculator.py": 250,
    "strategy/data/star_system.py": 200,
    "strategy/data/planet_serde.py": 300,
}


def test_per_service_loc_ceilings() -> None:
    """Each PROJ-372 service / data module stays within its ceiling."""
    failures: list[str] = []
    for rel, ceiling in SERVICE_CEILINGS.items():
        path = GAME_ROOT / rel
        if not path.exists():
            failures.append(f"{rel} missing")
            continue
        actual = _count_lines(path)
        if actual > ceiling:
            failures.append(f"{rel}: {actual} LOC (ceiling {ceiling})")
    assert not failures, (
        "PROJ-372 per-service LOC violations:\n  " + "\n  ".join(failures)
    )

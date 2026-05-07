"""PROJ-377 Phase 1: JSON capture for golden-save fixtures.

This script is **NOT a pytest test** — leading underscore prevents pytest
discovery (default `test_*.py` glob ignores it). Humans run it manually
to (re-)capture the two checked-in golden fixtures next to this file:

    python tests/fixtures/saves/_capture_baseline.py

The capture is *best-effort deterministic* — system placement, system
naming, planet body shapes, and per-planet intrinsic abilities are
seeded; planet `image_id` / `image_rotation` are normalized to
deterministic placeholders. Star-image selection, warp-point
`warp_type` rolls, and warp-point intrinsic abilities still consume an
unseeded `random.Random()` inside their generators (each re-run picks
different stable values). Re-running this script therefore overwrites
the fixtures with a new internally-consistent snapshot — the contract
CI checks is the round-trip identity assertion in
`tests/integration/strategy/test_save_round_trip.py`, NOT byte-equality
between successive captures.

Storms are stripped before `to_dict` because `Storm.to_dict()/from_dict()`
has pre-existing drift (PROJ-372 explicitly scoped it OUT — see
`tests/integration/strategy/test_save_round_trip.py:34-38`).
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from game.strategy.data.galaxy import Galaxy  # noqa: E402

_HERE = Path(__file__).resolve().parent


def _strip_storms(galaxy: Galaxy) -> None:
    for system in galaxy.systems.values():
        system.storms = []


def _normalize_image_fields(galaxy: Galaxy) -> None:
    """Replace `image_id` / `image_rotation` with deterministic placeholders.

    `PlanetImageRegistry.get_random_image` and `get_random_rotation` use an
    unseeded `random.Random()` when no `rng` is threaded through, so these
    two fields drift across capture runs even with a fixed seed. The
    fixture's job is to detect *structural* drift; normalizing these two
    cosmetic fields keeps the fixture deterministic without changing what
    the round-trip identity test catches.
    """
    for system in galaxy.systems.values():
        for planet in system.planets:
            planet.image_id = f"_fixture_planet_{planet.id}.png"
            planet.image_rotation = 0.0


def capture_baseline() -> dict:
    """5-system synthetic with warp lanes."""
    random.seed(2)  # NameRegistry / image-registry shuffles read global random.
    galaxy = Galaxy(radius=30)
    random.seed(2)  # Galaxy.__init__ may have consumed an indeterminate amount.
    galaxy.generate_systems(5, min_dist=5, rng=random.Random(2))
    _strip_storms(galaxy)
    _normalize_image_fields(galaxy)
    random.seed(2002)
    galaxy.generate_warp_lanes()
    return galaxy.to_dict()


def capture_populated() -> dict:
    """10-system with planets + warp lanes + one explicitly-decorated planet.

    The decorated planet exercises serialization fields that synthetic
    generation often leaves at default: ``owner_id``, custom ``atmosphere``,
    populated ``deposits``, ``stockpile`` / ``max_stockpile``,
    ``populations``, ``intrinsic_abilities``.
    """
    random.seed(100)
    galaxy = Galaxy(radius=50)
    random.seed(100)
    galaxy.generate_systems(10, min_dist=5, rng=random.Random(100))
    _strip_storms(galaxy)
    for i, system in enumerate(list(galaxy.systems.values())):
        random.seed(100_000 + i)
        try:
            galaxy.generate_planets(system)
        except Exception:  # Intentional broad catch: synthetic galaxies may produce systems with no eligible planet types; we still want a populated round-trip even if a few systems don't get planets.
            pass
    _normalize_image_fields(galaxy)
    random.seed(200_100)
    galaxy.generate_warp_lanes()

    # Decorate one planet with non-default fields so the round-trip
    # exercises the full Planet.to_dict surface for at least one entry.
    decorated = None
    for system in galaxy.systems.values():
        for planet in system.planets:
            decorated = planet
            break
        if decorated is not None:
            break

    if decorated is not None:
        from game.strategy.data.species_population import SpeciesPopulation

        decorated.owner_id = 0
        decorated.atmosphere = {"oxygen": 0.21, "nitrogen": 0.78, "argon": 0.01}
        decorated.atmosphere_target = {"oxygen": 0.25, "nitrogen": 0.74, "argon": 0.01}
        decorated.deposits = {
            "metals": {"surface": 100.0, "shallow": 50.0, "deep": 25.0},
            "organics": {"surface": 60.0, "shallow": 30.0, "deep": 0.0},
        }
        decorated.stockpile = {"metals": 250.0, "organics": 75.0}
        decorated.max_stockpile = {"metals": 1000.0, "organics": 500.0}
        decorated.populations = [
            SpeciesPopulation(race_id="human", count=1_000_000, happiness=0.6),
        ]
        decorated.intrinsic_abilities = {"ResearchBonus": 0.1}

    return galaxy.to_dict()


def main() -> None:
    baseline_path = _HERE / "galaxy_proj372_baseline.json"
    populated_path = _HERE / "galaxy_proj372_populated.json"

    baseline_path.write_text(
        json.dumps(capture_baseline(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    populated_path.write_text(
        json.dumps(capture_populated(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {baseline_path.relative_to(_REPO_ROOT)}")
    print(f"wrote {populated_path.relative_to(_REPO_ROOT)}")


if __name__ == "__main__":
    main()

"""PROJ-379 Phase 1: hand-built deterministic golden-save fixture builder.

This script is **NOT a pytest test** — leading underscore prevents pytest
discovery (default `test_*.py` glob ignores it). Humans run it manually
to (re-)generate the two checked-in golden fixtures next to this file:

    python tests/fixtures/saves/_build_galaxy_fixture.py

PROJ-379 closes PROJ-377 review MIN-002. The replaced ``_capture_baseline.py``
ran ``Galaxy.generate_systems()`` and post-processed the result, but
``StarGenerator`` / ``PlanetGenerator`` / ``NameRegistry`` / image registries
all consume unseeded ``random.Random()`` instances that fixed seeds cannot
control — so re-runs drifted across processes. This builder side-steps all of
that by constructing ``StarSystem`` / ``Planet`` / ``WarpPoint`` directly via
``__init__`` with explicit field values, then routing through the production
``Galaxy._registry.add_system()`` / ``register_planet()`` paths so ``from_dict``
sees the same registration shape ``to_dict`` writes.

Determinism contract (PROJ-379 G1): re-runs produce byte-identical JSON across
processes, including under random ``PYTHONHASHSEED``. Phase 2 enforces this
via subprocess tests in ``tests/integration/strategy/test_save_round_trip.py``.

Field-coverage contract (PROJ-379 G2): the populated fixture exercises every
key emitted by ``planet_to_dict`` (modulo ``image_id``/``image_rotation``
skiplist) with a non-default value somewhere in the planets. Asserted by
``tests/integration/strategy/test_golden_fixture_field_coverage.py``.

PYTHONHASHSEED rule: do NOT iterate any ``set`` to populate fixture lists. Use
explicit lists and tuples for warp-point sequences, planet sequences, etc.
``json.dumps(sort_keys=True)`` is a backstop on the final emit path.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from game.core.hex_math import HexCoord  # noqa: E402
from game.strategy.data.colony_species_config import ColonySpeciesConfig  # noqa: E402
from game.strategy.data.order_types import Order, OrderType  # noqa: E402
from game.strategy.data.planet import Planet, PlanetType  # noqa: E402
from game.strategy.data.planetary_facility import PlanetaryFacility  # noqa: E402
from game.strategy.data.species_population import SpeciesPopulation  # noqa: E402
from game.strategy.data.star_system import StarSystem, WarpPoint  # noqa: E402
from tests.fixtures.galaxy_fixtures import make_galaxy_stub  # noqa: E402

_HERE = Path(__file__).resolve().parent

# PROJ-379: image fields are intentionally normalized to deterministic
# placeholders. Field-coverage guard skiplist matches.
_PLACEHOLDER_IMAGE_ROTATION = 0.0


def _placeholder_image_id(planet_id: int) -> str:
    return f"_fixture_planet_{planet_id}.png"


def _build_minimal_planet(name: str, location: HexCoord, planet_type: PlanetType) -> Planet:
    """Construct a minimal Planet with required fields + deterministic image placeholder."""
    return Planet(
        name=name,
        location=location,
        orbit_distance=1,
        mass=5.97e24,
        radius=6.371e6,
        surface_area=5.1e14,
        density=5515.0,
        surface_gravity=9.81,
        surface_pressure=101325.0,
        surface_temperature=288.0,
        surface_water=0.5,
        tectonic_activity=0.5,
        magnetic_field=1.0,
        planet_type=planet_type,
    )


def _build_decorated_planet(name: str, location: HexCoord) -> Planet:
    """Construct a Planet with every ``planet_to_dict`` field at a non-default value.

    Skips ``image_id`` and ``image_rotation`` (set to deterministic placeholders
    by Phase 1 Task 1.5 — see PROJ-379 decisions.md "Field-coverage skiplist").
    """
    planet = Planet(
        name=name,
        location=location,
        orbit_distance=3,
        mass=4.87e24,
        radius=6.052e6,
        surface_area=4.6e14,
        density=5243.0,
        surface_gravity=8.87,
        surface_pressure=9.2e6,
        surface_temperature=737.0,
        surface_water=0.3,
        tectonic_activity=0.7,
        magnetic_field=0.4,
        planet_type=PlanetType.CONTINENTAL,
    )

    # Required for the field-coverage guard — every key in planet_to_dict
    # (modulo skiplist) gets a non-default value.
    planet.owner_id = 1
    planet.atmosphere = {"oxygen": 0.21, "nitrogen": 0.78, "argon": 0.01}
    planet.atmosphere_target = {"oxygen": 0.25, "nitrogen": 0.74, "argon": 0.01}
    planet.deposits = {
        "metals": {"surface": 100.0, "shallow": 50.0, "deep": 25.0},
        "organics": {"surface": 60.0, "shallow": 30.0, "deep": 0.0},
    }
    planet._stockpile = {"metals": 250.0, "organics": 75.0}
    planet._max_stockpile = {"metals": 1000.0, "organics": 500.0}
    planet.max_staging_mass = 500.0
    # PROJ-450 Phase 2: route through the public mutator so the entry
    # is promoted to a typed DropPod / CarriedVehicle on the way in.
    # Direct ``planet._staging_yard = [dict, ...]`` would skip the
    # typed-substrate invariant enforced by ``Planet.__post_init__``.
    planet.add_to_staging_yard(
        {"design_id": "test_ship", "ready_at_turn": 5, "mass": 100.0}
    )
    planet.facilities = [
        PlanetaryFacility(
            instance_id="fixture-facility-uuid-0001",
            design_id="test_complex",
            name="Test Complex",
            design_data={"layers": [], "category": "complex"},
            is_operational=True,
            construction_queue=[],
            construction_queue_paused=False,
            consumable_levels={"fuel": 50.0},
            component_states={},
        ),
    ]
    planet.populations = [
        SpeciesPopulation(race_id="human", count=1_000_000, happiness=0.6),
    ]
    planet.construction_queue = [
        {"design_id": "test_ship", "type": "ship", "turns_remaining": 5.0},
    ]
    planet.construction_queue_paused = True
    planet.radius_hexes = 2
    planet.energy = 50.0
    planet.energy_capacity = 200.0
    planet.energy_generation = 10.0
    planet.gravity_target = 9.81
    planet.gravity_original = 8.87
    planet.water_target = 0.5
    planet.radiation_shielding = 25.0
    planet.radiation_shielding_target = 50.0
    planet.orbit_parent_name = "Decorated Star"
    planet.orders = [
        Order(OrderType.ACTIVATE_ABILITY, target={"ability": "test_ability"}),
    ]
    planet.species_configs = {
        "human": ColonySpeciesConfig(food_allocation=1.5),
    }
    planet.intrinsic_abilities = {"ResearchBonus": 0.1}

    return planet


def _add_warp_link(
    sys_a: StarSystem,
    sys_b: StarSystem,
    a_local: HexCoord,
    b_local: HexCoord,
) -> None:
    """Add mutual warp points connecting two systems."""
    sys_a.warp_points.append(WarpPoint(sys_b.name, a_local, warp_type="stable"))
    sys_b.warp_points.append(WarpPoint(sys_a.name, b_local, warp_type="stable"))


def build_baseline() -> dict:
    """5-system fixture with warp lanes, no planets, no stars (round-trip-safe)."""
    galaxy = make_galaxy_stub(radius=30)

    # Hand-built systems at fixed coordinates. Names are explicit; no
    # NameRegistry consumption. No stars (the round-trip path serializes an
    # empty list when stars=[]).
    systems = [
        StarSystem("Alpha-1", HexCoord(0, 0)),
        StarSystem("Alpha-2", HexCoord(10, -5)),
        StarSystem("Alpha-3", HexCoord(-8, 6)),
        StarSystem("Alpha-4", HexCoord(15, 5)),
        StarSystem("Alpha-5", HexCoord(-12, -4)),
    ]

    # MST: Alpha-1 ↔ {2, 3}; Alpha-2 ↔ Alpha-4; Alpha-3 ↔ Alpha-5.
    _add_warp_link(systems[0], systems[1], HexCoord(2, 0), HexCoord(-2, 0))
    _add_warp_link(systems[0], systems[2], HexCoord(-2, 1), HexCoord(2, -1))
    _add_warp_link(systems[1], systems[3], HexCoord(2, 1), HexCoord(-2, -1))
    _add_warp_link(systems[2], systems[4], HexCoord(-1, -1), HexCoord(1, 1))

    for system in systems:
        galaxy._registry.add_system(system)

    return galaxy.to_dict()


def build_populated() -> dict:
    """10-system fixture with planets + warp lanes + one fully-decorated planet.

    The decorated planet exercises every key emitted by ``planet_to_dict``
    (modulo ``image_id`` / ``image_rotation`` skiplist) with a non-default
    value — asserted by ``test_golden_fixture_field_coverage.py``.
    """
    galaxy = make_galaxy_stub(radius=50)

    systems = [
        StarSystem("Beta-1", HexCoord(0, 0)),
        StarSystem("Beta-2", HexCoord(12, -6)),
        StarSystem("Beta-3", HexCoord(-10, 4)),
        StarSystem("Beta-4", HexCoord(20, 5)),
        StarSystem("Beta-5", HexCoord(-15, -8)),
        StarSystem("Beta-6", HexCoord(25, -10)),
        StarSystem("Beta-7", HexCoord(-20, 12)),
        StarSystem("Beta-8", HexCoord(8, 18)),
        StarSystem("Beta-9", HexCoord(-5, -20)),
        StarSystem("Beta-10", HexCoord(18, -18)),
    ]

    # Warp links: an MST + a few density edges. 9 links total.
    _add_warp_link(systems[0], systems[1], HexCoord(2, 0), HexCoord(-2, 0))
    _add_warp_link(systems[0], systems[2], HexCoord(-2, 1), HexCoord(2, -1))
    _add_warp_link(systems[1], systems[3], HexCoord(2, 1), HexCoord(-2, -1))
    _add_warp_link(systems[2], systems[4], HexCoord(-1, -2), HexCoord(1, 2))
    _add_warp_link(systems[3], systems[5], HexCoord(2, -1), HexCoord(-2, 1))
    _add_warp_link(systems[4], systems[6], HexCoord(-1, 2), HexCoord(1, -2))
    _add_warp_link(systems[0], systems[7], HexCoord(0, 2), HexCoord(0, -2))
    _add_warp_link(systems[4], systems[8], HexCoord(2, -1), HexCoord(-2, 1))
    _add_warp_link(systems[5], systems[9], HexCoord(-1, 1), HexCoord(1, -1))

    # Register systems first so register_planet has the system in the registry.
    for system in systems:
        galaxy._registry.add_system(system)

    # Hand-built planets — explicit list to avoid set iteration. Each planet
    # is appended to its system AND registered (PROJ-379 decisions.md row
    # "Phase 1 Task 1.4 makes the system.planets.append explicit alongside
    # register_planet"). Two planets per system for systems 0-7; system 8
    # carries the decorated planet (so total = 8*2 + 1 = 17 planets).
    plain_specs: list[tuple[StarSystem, str, HexCoord, PlanetType]] = [
        (systems[0], "Beta-1 I", HexCoord(2, 0), PlanetType.CONTINENTAL),
        (systems[0], "Beta-1 II", HexCoord(3, -1), PlanetType.BARREN),
        (systems[1], "Beta-2 I", HexCoord(1, 1), PlanetType.PELAGIC),
        (systems[1], "Beta-2 II", HexCoord(-1, 2), PlanetType.JOVIAN),
        (systems[2], "Beta-3 I", HexCoord(2, 0), PlanetType.ARID),
        (systems[2], "Beta-3 II", HexCoord(-2, 1), PlanetType.CRYOPLANET),
        (systems[3], "Beta-4 I", HexCoord(1, -1), PlanetType.CONTINENTAL),
        (systems[3], "Beta-4 II", HexCoord(2, 1), PlanetType.MAGMA),
        (systems[4], "Beta-5 I", HexCoord(-2, 0), PlanetType.BARREN),
        (systems[4], "Beta-5 II", HexCoord(0, -2), PlanetType.ICE_GIANT),
        (systems[5], "Beta-6 I", HexCoord(2, 0), PlanetType.PELAGIC),
        (systems[5], "Beta-6 II", HexCoord(-1, 1), PlanetType.ARID),
        (systems[6], "Beta-7 I", HexCoord(1, 0), PlanetType.CRYOPLANET),
        (systems[6], "Beta-7 II", HexCoord(-1, -1), PlanetType.PLANETOID),
        (systems[7], "Beta-8 I", HexCoord(2, -1), PlanetType.CONTINENTAL),
        (systems[7], "Beta-8 II", HexCoord(-2, 2), PlanetType.JOVIAN),
    ]
    for system, name, location, ptype in plain_specs:
        planet = _build_minimal_planet(name, location, ptype)
        # PROJ-379 Codex review P2 #2: register_planet assigns ID + indexes
        # but does NOT append to system.planets. Both steps required for
        # round-trip-safe serialization (StarSystem.to_dict serializes
        # self.planets at star_system.py:99-107).
        system.planets.append(planet)
        galaxy._registry.register_planet(system, planet)

    # Decorated planet on system 8 (Beta-9) — exercises every Planet field.
    decorated = _build_decorated_planet("Beta-9 I (decorated)", HexCoord(1, 0))
    systems[8].planets.append(decorated)
    galaxy._registry.register_planet(systems[8], decorated)

    # Apply image-field placeholders deterministically AFTER registration so
    # planet IDs are assigned. This matches PROJ-377's _normalize_image_fields
    # contract — these two fields are intentionally cosmetic placeholders.
    for system in systems:
        for planet in system.planets:
            planet.image_id = _placeholder_image_id(planet.id)
            planet.image_rotation = _PLACEHOLDER_IMAGE_ROTATION

    return galaxy.to_dict()


def main() -> None:
    baseline_path = _HERE / "galaxy_proj372_baseline.json"
    populated_path = _HERE / "galaxy_proj372_populated.json"

    baseline_path.write_text(
        json.dumps(build_baseline(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    populated_path.write_text(
        json.dumps(build_populated(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {baseline_path.relative_to(_REPO_ROOT)}")
    print(f"wrote {populated_path.relative_to(_REPO_ROOT)}")


if __name__ == "__main__":
    main()

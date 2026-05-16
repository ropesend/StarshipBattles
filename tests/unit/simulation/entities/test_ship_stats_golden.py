"""
PROJ-360 Phase 1: Golden output tests for ShipStatsCalculator.

Locks the full observable output of `ShipStatsCalculator.calculate(ship)` for a
representative cross-section of quickstart ship designs *before* the
decomposition refactor begins. Tests must PASS bit-for-bit on current `main`
and continue to PASS bit-for-bit through Phases 2-3 of PROJ-360.

The golden snapshot is stored as a sibling JSON file
(`test_ship_stats_golden_snapshot.json`) generated once via
`generate_snapshot()` and committed to source control. The test compares the
calculator's output against that snapshot using a stable canonicalization of
floats so the bit-equality goal is robust to platform float-formatting noise.

Design selection (covers diverse contributor domains):
- ``qs_escort``         small/light, no armor pool, warp drive, no weapons
- ``qs_general_purpose`` light cruiser, colony pod bay (passenger), warp drive
- ``qs_frigate_gc``     frigate w/ many components (broad cross-section)
- ``qs_heavy_cruiser``  full 4-layer ship w/ shields + armor + weapons
- ``qs_battleship``     full capital w/ shields, armor, weapons, PDC
- ``qs_missile_cruiser`` cruiser exercising capital-missile path
- ``qs_warp_gate_opener`` superweapon-class with warp drive
- ``qs_carrier``         PROJ-367 Phase 1: VehicleLaunchAbility + VehicleStorageAbility coverage
                          (also closes PROJ-360 review FIND-001 / FIND-005)
- ``qs_recon_picket``    PROJ-367 Phase 1: MultiplexTrackingAbility coverage
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from game.core.constants import LayerType
from game.core.json_utils import load_json
from game.core.paths import Paths
from game.simulation.entities.ship import Ship


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


SNAPSHOT_PATH = Path(__file__).parent / "test_ship_stats_golden_snapshot.json"

# Ship designs that exercise the breadth of contributor domains.
GOLDEN_DESIGNS: list[str] = [
    "qs_escort",
    "qs_general_purpose",
    "qs_frigate_gc",
    "qs_heavy_cruiser",
    "qs_battleship",
    "qs_missile_cruiser",
    "qs_warp_gate_opener",
    # PROJ-367 Phase 1: typed-ability coverage (closes EXT-07 + PROJ-360 FIND-001/005).
    "qs_carrier",
    "qs_recon_picket",
]

# Float comparison tolerance — tests are intended to be bit-identical across
# the refactor, but JSON round-tripping introduces tiny representational noise.
# 1e-9 is well below any meaningful semantic shift in any of the snapshotted
# fields (all are accumulations of finite-component data).
FLOAT_TOL = 1e-9


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_design(name: str) -> dict:
    designs_dir = Paths.get_starter_designs_dir()
    return load_json(str(designs_dir / f"{name}.json"))


def _round_for_snapshot(value):
    """Recursively normalize floats to a stable representation for JSON.

    NaN/Inf are not expected in the calculator's output; if they ever appear
    we surface that as a serialization failure.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            raise ValueError(f"Non-finite float in snapshot: {value!r}")
        # 12 significant decimal digits is more than enough for double-precision
        # round-trip without leaking representation-specific noise.
        return round(value, 12)
    if isinstance(value, dict):
        return {str(k): _round_for_snapshot(v) for k, v in sorted(value.items())}
    if isinstance(value, (list, tuple)):
        return [_round_for_snapshot(v) for v in value]
    return value


def _normalize_infinity(value):
    """Convert `float('inf')` to a JSON-safe sentinel for snapshot storage.

    `combat_endurance` writes `float('inf')` for endurance fields when the
    relevant resource has zero consumption. JSON cannot encode `inf`; we
    normalize to the string "inf" so the snapshot round-trips losslessly.
    """
    if isinstance(value, float) and math.isinf(value):
        return "inf"
    return value


def _normalize_summary(summary):
    """Pass through the cached_summary dict, normalizing inf values."""
    if not isinstance(summary, dict):
        return summary
    return {k: _normalize_infinity(v) for k, v in summary.items()}


def _capture_stats(ship: "Ship") -> dict:
    """Snapshot every calculator-written field on the ship.

    Mirrors every assignment the calculator performs against `ship` plus the
    layer/resource side-channels it mutates. New fields added by the
    calculator must be added here.
    """
    snap: dict = {
        # Mass / HP
        "mass": ship.mass,
        "current_mass": ship.current_mass,
        "max_hp": ship.max_hp,
        "hp": ship.hp,
        # Movement
        "total_thrust": ship.total_thrust,
        "total_strategic_movement": ship.total_strategic_movement,
        "turn_speed": ship.turn_speed,
        "max_speed": ship.max_speed,
        "acceleration_rate": ship.acceleration_rate,
        "drag": ship.drag,
        "total_maneuver_points": ship.total_maneuver_points,
        # Defense
        "max_shields": ship.max_shields,
        "shield_regen_rate": ship.shield_regen_rate,
        "shield_regen_cost": ship.shield_regen_cost,
        "current_shields": ship.current_shields,
        "repair_rate": ship.repair_rate,
        "emissive_armor": ship.emissive_armor,
        "shield_regenerating_armor": ship.shield_regenerating_armor,
        # Hangar / Launch
        "fighter_capacity": ship.fighter_capacity,
        "fighters_per_wave": ship.fighters_per_wave,
        "fighter_size_cap": ship.fighter_size_cap,
        "launch_cycle": ship.launch_cycle,
        # Command / multiplex
        "max_targets": ship.max_targets,
        "crew_onboard": ship.crew_onboard,
        "crew_required": ship.crew_required,
        # Mass budget
        "max_mass_budget": ship.max_mass_budget,
        "mass_limits_ok": ship.mass_limits_ok,
        # Geometry
        "radius": ship.radius,
        # Targeting / EW
        "total_defense_score": ship.total_defense_score,
        "baseline_to_hit_offense": ship.baseline_to_hit_offense,
        # Resources / costs
        "construction_cost": dict(ship.construction_cost),
        "warp_max_tonnage": ship.warp_max_tonnage,
        "warp_energy_cost": ship.warp_energy_cost,
        "warp_resource_costs": dict(ship.warp_resource_costs),
        "cargo_storage": dict(ship.cargo_storage),
        "pod_storage_mass": ship.pod_storage_mass,
        "ammo_gen_rate": ship.ammo_gen_rate,
        # Combat endurance (PROJ-360 audit FIND-002).
        # These 12 fields are written by `combat_endurance.calculate_combat_endurance`
        # and complete the calculator's observable surface. `float('inf')`
        # is normalized to the JSON-safe sentinel string "inf" — endurance
        # values are unbounded when consumption is zero.
        "fuel_consumption": ship.fuel_consumption,
        "ammo_consumption": ship.ammo_consumption,
        "energy_consumption": ship.energy_consumption,
        "potential_fuel_consumption": ship.potential_fuel_consumption,
        "potential_ammo_consumption": ship.potential_ammo_consumption,
        "potential_energy_consumption": ship.potential_energy_consumption,
        "fuel_endurance": _normalize_infinity(ship.fuel_endurance),
        "ammo_endurance": _normalize_infinity(ship.ammo_endurance),
        "energy_endurance": _normalize_infinity(ship.energy_endurance),
        "energy_recharge": _normalize_infinity(ship.energy_recharge),
        "energy_net": ship.energy_net,
        "cached_summary": _normalize_summary(ship._cached_summary),
    }

    # Layer status (ship.layer_status is keyed by LayerType enum)
    layer_status_snap: dict = {}
    for layer_key, layer_info in ship.layer_status.items():
        # LayerType enum -> name for stable JSON key
        key = layer_key.name if isinstance(layer_key, LayerType) else str(layer_key)
        layer_status_snap[key] = dict(layer_info)
    snap["layer_status"] = layer_status_snap

    # Armor pool side-channel
    if LayerType.ARMOR in ship.layers:
        armor = ship.layers[LayerType.ARMOR]
        snap["armor_max_hp_pool"] = armor.max_hp_pool
        snap["armor_hp_pool"] = armor.hp_pool

    # Resource registry contents (max + regen for every registered resource)
    resource_snap: dict = {}
    for res_name in sorted(ship.resources.get_resource_names()):
        res = ship.resources.get_resource(res_name)
        if res is None:
            continue
        resource_snap[res_name] = {
            "max": ship.resources.get_max_value(res_name),
            "value": ship.resources.get_value(res_name),
            "regen_rate": getattr(res, "regen_rate", 0.0),
        }
    snap["resources"] = resource_snap

    return _round_for_snapshot(snap)


def _build_and_calculate(design_name: str, fresh_registries) -> "Ship":
    design = _load_design(design_name)
    ship = Ship.from_dict(design, registries=fresh_registries)
    ship.recalculate_stats()
    return ship


# ---------------------------------------------------------------------------
# Snapshot generation helper (used to produce the initial JSON file)
# ---------------------------------------------------------------------------


def generate_snapshot(fresh_registries) -> dict:
    """Produce a fresh snapshot dict for ALL designs.

    Invoked once by the bootstrap test below when the snapshot file does not
    yet exist. Subsequent runs compare against the committed snapshot.
    """
    snapshot: dict = {}
    for design_name in GOLDEN_DESIGNS:
        ship = _build_and_calculate(design_name, fresh_registries)
        snapshot[design_name] = _capture_stats(ship)
    return snapshot


def _load_snapshot() -> dict:
    if not SNAPSHOT_PATH.exists():
        return {}
    with SNAPSHOT_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Deep equality with float tolerance
# ---------------------------------------------------------------------------


def _assert_equal(got, want, path: str = "") -> None:
    """Recursive equality with FLOAT_TOL on floats, exact on ints/strings/bools."""
    if isinstance(want, dict):
        assert isinstance(got, dict), f"{path}: type mismatch dict vs {type(got).__name__}"
        assert set(got.keys()) == set(want.keys()), (
            f"{path}: key mismatch — extra={set(got.keys()) - set(want.keys())}, "
            f"missing={set(want.keys()) - set(got.keys())}"
        )
        for k in sorted(want.keys()):
            _assert_equal(got[k], want[k], f"{path}.{k}" if path else str(k))
        return
    if isinstance(want, list):
        assert isinstance(got, list), f"{path}: type mismatch list vs {type(got).__name__}"
        assert len(got) == len(want), f"{path}: length mismatch {len(got)} != {len(want)}"
        for i, (g, w) in enumerate(zip(got, want)):
            _assert_equal(g, w, f"{path}[{i}]")
        return
    if isinstance(want, bool) or isinstance(got, bool):
        # bool is a subtype of int — guard before float compare
        assert got == want, f"{path}: {got!r} != {want!r}"
        return
    if isinstance(want, (int, float)) and isinstance(got, (int, float)):
        if math.isclose(float(got), float(want), abs_tol=FLOAT_TOL, rel_tol=1e-12):
            return
        raise AssertionError(f"{path}: {got!r} != {want!r} (numeric tol {FLOAT_TOL})")
    assert got == want, f"{path}: {got!r} != {want!r}"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def golden_snapshot() -> dict:
    snap = _load_snapshot()
    if not snap:
        pytest.fail(
            f"Golden snapshot missing at {SNAPSHOT_PATH}. "
            f"Run the bootstrap script with REGENERATE_SHIP_STATS_GOLDEN=1 "
            f"or invoke generate_snapshot() manually."
        )
    return snap


@pytest.mark.parametrize("design_name", GOLDEN_DESIGNS)
def test_design_in_snapshot(golden_snapshot, design_name):
    """Every parametrized design must have a baked snapshot entry."""
    assert design_name in golden_snapshot, (
        f"Design {design_name!r} missing from snapshot {SNAPSHOT_PATH}. "
        f"Regenerate the snapshot file."
    )


@pytest.mark.parametrize("design_name", GOLDEN_DESIGNS)
def test_ship_stats_match_golden(design_name, fresh_registries, golden_snapshot):
    """Calculator output for ``design_name`` matches the locked snapshot.

    This is the bit-for-bit baseline that PROJ-360 Phase 2-3 must preserve.
    A single deviation in any captured field constitutes a regression.
    """
    ship = _build_and_calculate(design_name, fresh_registries)
    got = _capture_stats(ship)
    want = golden_snapshot[design_name]
    _assert_equal(got, want, path=design_name)


def test_carrier_design_exercises_typed_vehicle_abilities(fresh_registries):
    """PROJ-FMS-C audit Fix 1: ``qs_carrier`` exercises the new launch surface.

    The carrier now mounts :class:`TacticalFighterLaunchAbility` and
    :class:`VehicleBayAbility` (PROJ-FMS-A Phase 5) in place of the
    legacy :class:`VehicleLaunchAbility` / :class:`VehicleStorageAbility`
    pair. The stat aggregator's ``contribute_vehicle_launch`` reads
    ``capacity_per_action`` / ``cycle_time`` into ``fighters_per_wave`` /
    ``launch_cycle`` and the ``contribute_vehicle_bay`` aggregator sums
    ``capacity_mass`` into ``bay_capacity_mass``. The non-zero checks
    pin the typed-ability access path.
    """
    ship = _build_and_calculate("qs_carrier", fresh_registries)
    assert ship.fighters_per_wave > 0
    assert ship.launch_cycle > 0
    assert ship.bay_capacity_mass > 0


def test_recon_picket_design_exercises_typed_multiplex(fresh_registries):
    """PROJ-367 Phase 1: ``qs_recon_picket`` exercises MultiplexTrackingAbility
    (closes EXT-07 + PROJ-360 FIND-005).

    If the typed-ability access broke, ``max_targets`` would stay at the
    ``CombatConstants.DEFAULT_MAX_TARGETS`` value (1). The strict-greater
    check pins the typed-ability path.
    """
    ship = _build_and_calculate("qs_recon_picket", fresh_registries)
    assert ship.max_targets > 1


def test_construction_cost_is_deterministic(fresh_registries):
    """Calling ``recalculate_stats`` twice yields identical construction_cost.

    The calculator zero-fills planetary-resource costs and accumulates per
    component; this check guards against any future drift toward
    nondeterministic dict ordering or accumulator carry-over.
    """
    ship = _build_and_calculate("qs_battleship", fresh_registries)
    first = dict(ship.construction_cost)
    ship.recalculate_stats()
    second = dict(ship.construction_cost)
    assert first == second, (
        f"construction_cost differs across recalculations: "
        f"first={first}, second={second}"
    )

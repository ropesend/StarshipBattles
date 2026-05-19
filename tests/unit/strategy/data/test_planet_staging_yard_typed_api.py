"""PROJ-450 Phase 1: typed-API contract tests for the planet staging yard.

These tests pin the new typed surface widened in Phase 1:

* ``Planet.add_to_staging_yard(item)`` accepts ``Dict`` |
  :class:`CarriedVehicle` | :class:`DropPod` and normalises to the
  legacy dict substrate internally (Phase 1 keeps the substrate as
  ``List[Dict[str, Any]]`` for save-format compatibility — Phase 2
  widens the type).
* ``Planet.pop_staging_yard_typed(index)`` pops via the existing
  ``remove_from_staging_yard`` and promotes the result to a typed
  :class:`CarriedVehicle` or :class:`DropPod`.

The 3 helpers that previously lived as module-level privates in
``transfer_branches.py`` move into ``planet.py`` so the dict ↔ typed
promotion logic is centralised on the Planet boundary.
"""
from __future__ import annotations

from game.strategy.data.bay_inventory import DropPod
from game.strategy.data.carried_vehicle import CarriedVehicle
from tests.fixtures.strategy_entities import create_test_planet


def _empty_planet():
    """Return a Planet with no facilities/pop and uncapped staging yard."""
    p = create_test_planet(has_facilities=False, has_population=False)
    # Default ``max_staging_mass`` is 0.0 which means "uncapped" per
    # ``add_to_staging_yard`` (condition guards on ``> 0``).
    return p


# ---------------------------------------------------------------------------
# add_to_staging_yard typed accept
# ---------------------------------------------------------------------------


def test_add_to_staging_yard_accepts_typed_carried_vehicle():
    """Passing a typed CarriedVehicle lands in the staging yard.

    The substrate is still dict-shaped in Phase 1, so the assert
    projects through the dict view rather than expecting the typed
    instance to round-trip identity.
    """
    planet = _empty_planet()
    cv = CarriedVehicle(
        design_id="fighter_alpha",
        design_data={"name": "fighter_alpha"},
        vehicle_type="fighter",
        mass=20.0,
        current_hp=80,
    )
    assert planet.add_to_staging_yard(cv) is True
    assert len(planet.staging_yard) == 1
    stored = planet.staging_yard[0]
    # Substrate stays dict-shaped in Phase 1 — Phase 2 widens it.
    assert isinstance(stored, dict)
    assert stored["design_id"] == "fighter_alpha"
    assert stored["vehicle_type"] == "fighter"
    assert stored["mass"] == 20.0


def test_add_to_staging_yard_accepts_typed_drop_pod():
    """Passing a typed DropPod lands in the staging yard."""
    planet = _empty_planet()
    pod = DropPod(
        design_id="drop_pod_basic",
        design_data={"name": "drop_pod_basic"},
        mass=100.0,
        payload={"name": "PodAlpha", "colonists": 1000},
    )
    assert planet.add_to_staging_yard(pod) is True
    assert len(planet.staging_yard) == 1
    stored = planet.staging_yard[0]
    assert isinstance(stored, dict)
    assert stored["design_id"] == "drop_pod_basic"
    assert stored["mass"] == 100.0


def test_add_to_staging_yard_accepts_dict_backward_compat():
    """Legacy dict callers (rollback paths, save-load) still work."""
    planet = _empty_planet()
    legacy = {
        "design_id": "drop_pod_basic",
        "mass": 50.0,
        "name": "LegacyPod",
    }
    assert planet.add_to_staging_yard(legacy) is True
    assert len(planet.staging_yard) == 1
    assert planet.staging_yard[0]["design_id"] == "drop_pod_basic"


# ---------------------------------------------------------------------------
# pop_staging_yard_typed
# ---------------------------------------------------------------------------


def test_pop_staging_yard_typed_returns_carried_vehicle():
    """Adding a typed CV and popping via the typed API returns a CV."""
    planet = _empty_planet()
    cv = CarriedVehicle(
        design_id="mine_alpha",
        design_data={"name": "mine_alpha"},
        vehicle_type="mine",
        mass=10.0,
        current_hp=5,
    )
    assert planet.add_to_staging_yard(cv) is True
    popped = planet.pop_staging_yard_typed(0)
    assert isinstance(popped, CarriedVehicle)
    assert popped.design_id == "mine_alpha"
    assert popped.vehicle_type == "mine"
    assert popped.mass == 10.0
    assert len(planet.staging_yard) == 0


def test_pop_staging_yard_typed_returns_drop_pod():
    """Adding a typed DropPod and popping returns a DropPod."""
    planet = _empty_planet()
    pod = DropPod(
        design_id="drop_pod_basic",
        design_data={"name": "drop_pod_basic"},
        mass=100.0,
        payload={"name": "PodAlpha", "colonists": 1000},
    )
    assert planet.add_to_staging_yard(pod) is True
    popped = planet.pop_staging_yard_typed(0)
    assert isinstance(popped, DropPod)
    assert popped.design_id == "drop_pod_basic"
    assert popped.mass == 100.0
    # Payload preserved through the dict round-trip.
    assert popped.payload.get("name") == "PodAlpha"
    assert popped.payload.get("colonists") == 1000


def test_pop_staging_yard_typed_handles_dict_storage():
    """Direct dict-shaped entry (vehicle_type discriminator) promotes
    to a typed CarriedVehicle via the typed pop."""
    planet = _empty_planet()
    legacy_cv = {
        "design_id": "fighter_legacy",
        "design_data": {"name": "fighter_legacy"},
        "vehicle_type": "fighter",
        "mass": 25.0,
        "current_hp": 90,
    }
    assert planet.add_to_staging_yard(legacy_cv) is True
    popped = planet.pop_staging_yard_typed(0)
    assert isinstance(popped, CarriedVehicle)
    assert popped.design_id == "fighter_legacy"
    assert popped.vehicle_type == "fighter"


def test_pop_staging_yard_typed_returns_drop_pod_fallback_on_unknown_vehicle_type():
    """A dict without a recognised ``vehicle_type`` falls back to
    DropPod promotion (mirrors the legacy ``_pod_from_dict`` behaviour
    used by ``_dispatch_drop_pod_load``)."""
    planet = _empty_planet()
    legacy_pod = {
        "design_id": "drop_pod_basic",
        "mass": 100.0,
        "name": "PodAlpha",
        "colonists": 1000,
    }
    assert planet.add_to_staging_yard(legacy_pod) is True
    popped = planet.pop_staging_yard_typed(0)
    assert isinstance(popped, DropPod)
    assert popped.design_id == "drop_pod_basic"
    assert popped.mass == 100.0


def test_pop_staging_yard_typed_returns_none_on_out_of_range():
    """Invalid index returns None (mirrors remove_from_staging_yard)."""
    planet = _empty_planet()
    assert planet.pop_staging_yard_typed(0) is None
    assert planet.pop_staging_yard_typed(5) is None
    assert planet.pop_staging_yard_typed(-1) is None

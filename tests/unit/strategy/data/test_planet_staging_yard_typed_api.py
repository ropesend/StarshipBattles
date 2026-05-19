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

    PROJ-450 Phase 3: the public ``staging_yard`` property is a typed
    read-only tuple of ``CarriedVehicle | DropPod``; readers use
    attribute access (no dict subscripting).
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
    assert isinstance(stored, CarriedVehicle)
    assert stored.design_id == "fighter_alpha"
    assert stored.vehicle_type == "fighter"
    assert stored.mass == 20.0


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
    assert isinstance(stored, DropPod)
    assert stored.design_id == "drop_pod_basic"
    assert stored.mass == 100.0


def test_add_to_staging_yard_accepts_dict_backward_compat():
    """Legacy dict callers (rollback paths, save-load) still work.

    PROJ-450 Phase 3: dict input is promoted to a typed entry on the way
    in; the public property hands back the typed object.
    """
    planet = _empty_planet()
    legacy = {
        "design_id": "drop_pod_basic",
        "mass": 50.0,
        "name": "LegacyPod",
    }
    assert planet.add_to_staging_yard(legacy) is True
    assert len(planet.staging_yard) == 1
    stored = planet.staging_yard[0]
    assert isinstance(stored, (CarriedVehicle, DropPod))
    assert stored.design_id == "drop_pod_basic"


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


# ---------------------------------------------------------------------------
# PROJ-450 Phase 2: typed substrate contract
# ---------------------------------------------------------------------------


def test_staging_yard_internal_storage_is_typed():
    """After ``add_to_staging_yard``, the private ``_staging_yard``
    list holds typed :class:`CarriedVehicle` / :class:`DropPod` entries
    rather than dicts.

    PROJ-450 Phase 2 contract: the substrate is widened to
    ``List[CarriedVehicle | DropPod]``. Dict inputs are promoted to
    typed entries before append.
    """
    planet = _empty_planet()
    cv = CarriedVehicle(
        design_id="fighter_alpha",
        design_data={"name": "fighter_alpha"},
        vehicle_type="fighter",
        mass=20.0,
        current_hp=80,
    )
    pod = DropPod(
        design_id="drop_pod_basic",
        design_data={"name": "drop_pod_basic"},
        mass=100.0,
        payload={"name": "PodAlpha"},
    )
    legacy_pod = {
        "design_id": "drop_pod_legacy",
        "mass": 50.0,
        "name": "LegacyPod",
    }
    assert planet.add_to_staging_yard(cv) is True
    assert planet.add_to_staging_yard(pod) is True
    assert planet.add_to_staging_yard(legacy_pod) is True
    for stored in planet._staging_yard:
        assert isinstance(stored, (CarriedVehicle, DropPod)), (
            f"_staging_yard entry is {type(stored).__name__}, expected "
            f"CarriedVehicle | DropPod (PROJ-450 Phase 2)"
        )


def test_save_round_trip_preserves_typed_substrate():
    """A save -> load round-trip leaves ``_staging_yard`` typed.

    The save format on-disk is dict-shaped (per the
    :meth:`CarriedVehicle.to_dict` / :meth:`DropPod.to_dict`
    serialisation), but the loaded Planet's substrate is typed again
    via ``planet_serde._normalize_to_typed``.
    """
    from game.strategy.data.planet import Planet

    planet = _empty_planet()
    cv = CarriedVehicle(
        design_id="fighter_alpha",
        design_data={"name": "fighter_alpha"},
        vehicle_type="fighter",
        mass=20.0,
        current_hp=80,
    )
    pod = DropPod(
        design_id="drop_pod_basic",
        design_data={"name": "drop_pod_basic"},
        mass=100.0,
        payload={"name": "PodAlpha"},
    )
    assert planet.add_to_staging_yard(cv) is True
    assert planet.add_to_staging_yard(pod) is True

    saved = planet.to_dict()
    loaded = Planet.from_dict(saved)

    assert len(loaded._staging_yard) == 2
    for stored in loaded._staging_yard:
        assert isinstance(stored, (CarriedVehicle, DropPod)), (
            f"After round-trip, _staging_yard entry is "
            f"{type(stored).__name__}, expected typed"
        )


def test_save_format_remains_dict_shape():
    """``planet.to_dict()['staging_yard']`` is still
    ``List[Dict[str, Any]]`` — typed entries flatten back to dicts at
    the save boundary."""
    planet = _empty_planet()
    cv = CarriedVehicle(
        design_id="fighter_alpha",
        design_data={"name": "fighter_alpha"},
        vehicle_type="fighter",
        mass=20.0,
        current_hp=80,
    )
    pod = DropPod(
        design_id="drop_pod_basic",
        design_data={"name": "drop_pod_basic"},
        mass=100.0,
        payload={"name": "PodAlpha"},
    )
    assert planet.add_to_staging_yard(cv) is True
    assert planet.add_to_staging_yard(pod) is True

    saved = planet.to_dict()
    yard = saved["staging_yard"]
    assert isinstance(yard, list)
    for entry in yard:
        assert isinstance(entry, dict), (
            f"save-shape staging_yard entry is {type(entry).__name__}, "
            f"expected dict"
        )

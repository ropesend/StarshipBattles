"""Tests for the Phase 1a Container-snapshot substrate (PROJ-437).

Pins the additive ``ContainerSnapshotInfo`` DTO + the
``facade.fleets.get_containers(id)`` / ``facade.planets.get_containers(id)``
accessors that PROJ-437 Phase 1b's transfer-dialog rework consumes. No
caller migration in 1a — these tests lock in the projection shape only.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from game.strategy.data.bay_inventory import BayInventory
from game.strategy.data.containable import ContainableKind
from game.strategy.facade.dto import ContainerSnapshotInfo
from game.strategy.facade.grouped_namespaces import (
    FacadeFleetQueries,
    FacadePlanetQueries,
)
from game.strategy.facade.slices.fleet_slice import FleetSlice
from game.strategy.facade.slices.planet_slice import PlanetSlice


# ---------------------------------------------------------------------------
# DTO
# ---------------------------------------------------------------------------


class TestContainerSnapshotInfo:
    def test_mass_remaining_is_capacity_minus_used(self) -> None:
        snap = ContainerSnapshotInfo(
            container_id="ship:abc:bay",
            owner_kind="fleet",
            owner_id=1,
            label="Ship A — Bay",
            capacity_mass=100.0,
            mass_used=40.0,
            allowed_kinds=frozenset({ContainableKind.RESOURCE}),
            entries=(),
        )

        assert snap.mass_remaining == pytest.approx(60.0)

    def test_is_hashable_and_immutable(self) -> None:
        snap = ContainerSnapshotInfo(
            container_id="ship:abc:bay",
            owner_kind="fleet",
            owner_id=1,
            label="A",
            capacity_mass=1.0,
            mass_used=0.0,
            allowed_kinds=frozenset({ContainableKind.RESOURCE}),
            entries=(),
        )

        with pytest.raises((AttributeError, Exception)):
            snap.label = "mutated"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# FleetSlice.get_fleet_containers
# ---------------------------------------------------------------------------


def _ship_with_bay(
    *,
    instance_id: str,
    name: str,
    bay_capacity_max: float,
    resources: dict[str, float] | None = None,
    population: dict[str, int] | None = None,
) -> SimpleNamespace:
    inventory = BayInventory(
        bay=[],
        pods=[],
        resources=dict(resources or {}),
        population=dict(population or {}),
    )
    cargo_mgr = SimpleNamespace(
        get_vehicle_bay_capacity=lambda: (0.0, bay_capacity_max),
    )
    return SimpleNamespace(
        instance_id=instance_id,
        name=name,
        bay_inventory=inventory,
        _cargo_mgr=cargo_mgr,
    )


def test_get_fleet_containers_returns_empty_for_unknown_fleet_id() -> None:
    state = SimpleNamespace(get_fleet_by_id=lambda _id: None)
    slice_ = FleetSlice(state)

    assert slice_.get_fleet_containers(404) == ()


def test_get_fleet_containers_emits_one_snapshot_per_ship() -> None:
    ship_a = _ship_with_bay(
        instance_id="alpha",
        name="Alpha",
        bay_capacity_max=100.0,
        resources={"metals": 10.0},
    )
    ship_b = _ship_with_bay(
        instance_id="beta",
        name="Beta",
        bay_capacity_max=50.0,
    )
    fleet = SimpleNamespace(id=7, ships=[ship_a, ship_b])
    state = SimpleNamespace(
        get_fleet_by_id=lambda fid: fleet if fid == 7 else None,
    )

    snapshots = FleetSlice(state).get_fleet_containers(7)

    assert isinstance(snapshots, tuple)
    assert len(snapshots) == 2
    a_snap, b_snap = snapshots

    assert a_snap.container_id == "ship:alpha:bay_inventory"
    assert a_snap.owner_kind == "fleet"
    assert a_snap.owner_id == 7
    assert a_snap.label == "Alpha"
    assert a_snap.capacity_mass == 100.0
    assert ContainableKind.RESOURCE in a_snap.allowed_kinds
    assert ContainableKind.ITEM in a_snap.allowed_kinds
    assert ContainableKind.POPULATION in a_snap.allowed_kinds
    # Resources slice projected into entries.
    resource_entries = [
        e for e in a_snap.entries if e.kind is ContainableKind.RESOURCE
    ]
    assert len(resource_entries) == 1
    assert resource_entries[0].type_id == "metals"
    assert resource_entries[0].quantity == pytest.approx(10.0)

    assert b_snap.container_id == "ship:beta:bay_inventory"
    assert b_snap.capacity_mass == 50.0
    assert b_snap.entries == ()


def test_ship_container_snapshot_capacity_matches_bay_inventory() -> None:
    """F-A-013: snapshot's capacity_mass mirrors the real bay cap.

    A ship with a 50-mass bay holding 10 mass of resources reports
    ``mass_used == 10`` and ``capacity_mass == 50`` (not ``inf``).
    """
    # 1 "vapors" unit is 0.001 mass; 10000 units = 10.0 mass — well
    # under the 50-mass bay cap.
    ship = _ship_with_bay(
        instance_id="cap-test",
        name="Cap Test",
        bay_capacity_max=50.0,
        resources={"vapors": 10000.0},
    )
    fleet = SimpleNamespace(id=11, ships=[ship])
    state = SimpleNamespace(get_fleet_by_id=lambda fid: fleet)

    (snap,) = FleetSlice(state).get_fleet_containers(11)

    assert snap.capacity_mass == 50.0
    assert snap.mass_used == pytest.approx(10.0)
    assert snap.capacity_mass != float("inf")


def test_get_fleet_containers_capacity_falls_back_to_infinity_when_unreadable() -> None:
    """If the ship's cargo manager cannot supply bay capacity, the
    snapshot reports inf — the projection stays usable and Phase 2
    validation can decide how to handle uncapped containers."""

    def raise_(*_a, **_kw) -> tuple[float, float]:
        raise RuntimeError("no cargo manager wired")

    inventory = BayInventory(bay=[], pods=[], resources={}, population={})
    ship = SimpleNamespace(
        instance_id="zeta",
        name="Zeta",
        bay_inventory=inventory,
        _cargo_mgr=SimpleNamespace(get_vehicle_bay_capacity=raise_),
    )
    fleet = SimpleNamespace(id=3, ships=[ship])
    state = SimpleNamespace(get_fleet_by_id=lambda fid: fleet)

    (snap,) = FleetSlice(state).get_fleet_containers(3)

    assert snap.capacity_mass == float("inf")


# ---------------------------------------------------------------------------
# PlanetSlice.get_planet_containers
# ---------------------------------------------------------------------------


def test_get_planet_containers_returns_empty_for_unknown_planet_id() -> None:
    state = SimpleNamespace(get_planet_by_id=lambda _id: None)
    slice_ = PlanetSlice(state)

    assert slice_.get_planet_containers(404) == ()


def test_get_planet_containers_emits_stockpile_and_staging_yard_snapshots() -> None:
    planet = SimpleNamespace(
        id=12,
        name="Alpha Colony",
        stockpile={"metals": 50.0, "fuel": 12.0},
        max_stockpile={"metals": 100.0, "fuel": 100.0},
        staging_yard=[
            {"name": "Drop Pod A", "vehicle_type": "Ship", "mass": 8.0,
             "design_id": "pod_a", "instance_id": "py-1"},
            {"name": "Drop Pod A", "vehicle_type": "Ship", "mass": 8.0,
             "design_id": "pod_a", "instance_id": "py-2"},
        ],
        max_staging_mass=500.0,
    )
    state = SimpleNamespace(
        get_planet_by_id=lambda pid: planet if pid == 12 else None,
    )

    snaps = PlanetSlice(state).get_planet_containers(12)

    by_id = {s.container_id: s for s in snaps}
    stockpile = by_id["planet:12:stockpile"]
    staging = by_id["planet:12:staging_yard"]

    assert stockpile.owner_kind == "planet"
    assert stockpile.owner_id == 12
    assert stockpile.label == "Alpha Colony — Stockpile"
    assert stockpile.allowed_kinds == frozenset({ContainableKind.RESOURCE})
    # F-A-014: caps are resource units, converted to mass per-resource.
    from game.core.resources import ResourceCatalog
    _catalog = ResourceCatalog.from_json()
    expected_cap = (
        100.0 * _catalog.get_mass_per_unit("metals")
        + 100.0 * _catalog.get_mass_per_unit("fuel")
    )
    assert stockpile.capacity_mass == pytest.approx(expected_cap)
    by_resource = {e.type_id: e for e in stockpile.entries}
    assert by_resource["metals"].quantity == pytest.approx(50.0)
    assert by_resource["fuel"].quantity == pytest.approx(12.0)

    assert staging.label == "Alpha Colony — Staging Yard"
    assert staging.allowed_kinds == frozenset({ContainableKind.ITEM})
    assert staging.capacity_mass == pytest.approx(500.0)
    item_entries = [
        e for e in staging.entries if e.kind is ContainableKind.ITEM
    ]
    assert len(item_entries) == 2
    assert all(e.type_id == "pod_a" for e in item_entries)


def test_get_planet_containers_handles_missing_optional_fields() -> None:
    """Planet without ``staging_yard`` data still yields the stockpile
    snapshot — empty staging_yard does not break the projection."""
    planet = SimpleNamespace(
        id=14,
        name="Bare Colony",
        stockpile={"metals": 1.0},
        max_stockpile={"metals": 5.0},
        staging_yard=[],
        max_staging_mass=0.0,
    )
    state = SimpleNamespace(get_planet_by_id=lambda pid: planet)

    snaps = PlanetSlice(state).get_planet_containers(14)

    assert {s.container_id for s in snaps} == {
        "planet:14:stockpile",
        "planet:14:staging_yard",
    }


# ---------------------------------------------------------------------------
# Grouped-namespace proxies
# ---------------------------------------------------------------------------


def test_facade_fleets_get_containers_proxies_to_slice() -> None:
    slice_mock = MagicMock(spec=FleetSlice)
    sentinel = ()  # tuple instance for identity check
    slice_mock.get_fleet_containers.return_value = sentinel

    result = FacadeFleetQueries(slice_mock).get_containers(99)

    assert result is sentinel
    slice_mock.get_fleet_containers.assert_called_once_with(99)


def test_facade_planets_get_containers_proxies_to_slice() -> None:
    slice_mock = MagicMock(spec=PlanetSlice)
    sentinel = ()
    slice_mock.get_planet_containers.return_value = sentinel

    result = FacadePlanetQueries(slice_mock).get_containers(99)

    assert result is sentinel
    slice_mock.get_planet_containers.assert_called_once_with(99)

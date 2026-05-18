"""Phase 1b cutover tests (PROJ-437) — container-aware browse path.

Locks the additive Container-snapshot plumbing in the transfer
controller and view model:

* ``TransferController.collect_sources_and_targets`` attaches a
  ``containers`` tuple per entry, sourced from
  ``facade.fleets.get_containers(id)`` /
  ``facade.planets.get_containers(id)`` (Phase 1a substrate).
* ``TransferViewModel.get_amounts_from_containers(snapshots)`` returns
  the same ``cargo_key → amount`` shape the legacy
  ``get_amounts(info_obj)`` produces for FleetInfo / PlanetInfo, but
  reads from container snapshots — the projection consumers will
  switch to in Phase 3.

Phase 1b stays browse-only: existing dropdown labels, selection flow,
and row-data construction are untouched. Tests for the legacy DTO
path live in [test_transfer_controller.py](test_transfer_controller.py)
and [test_transfer_view_model.py](test_transfer_view_model.py) and
remain authoritative for Phase 1.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from game.strategy.data.containable import ContainableKind
from game.strategy.data.container import ContainerEntry
from game.strategy.facade.dto import ContainerSnapshotInfo
from game.ui.screens.transfer_controller import TransferController
from game.ui.screens.transfer_view_model import TransferViewModel


# ---------------------------------------------------------------------------
# Snapshot builders
# ---------------------------------------------------------------------------


def _snap(
    container_id: str,
    *,
    owner_kind: str = "fleet",
    owner_id: int = 1,
    label: str = "snap",
    entries: tuple[ContainerEntry, ...] = (),
    capacity_mass: float = 100.0,
    mass_used: float = 0.0,
    allowed_kinds: frozenset[ContainableKind] | None = None,
) -> ContainerSnapshotInfo:
    return ContainerSnapshotInfo(
        container_id=container_id,
        owner_kind=owner_kind,
        owner_id=owner_id,
        label=label,
        capacity_mass=capacity_mass,
        mass_used=mass_used,
        allowed_kinds=allowed_kinds or frozenset({
            ContainableKind.RESOURCE,
            ContainableKind.ITEM,
            ContainableKind.POPULATION,
        }),
        entries=entries,
    )


# ---------------------------------------------------------------------------
# Controller — collect_sources_and_targets attaches per-entry containers
# ---------------------------------------------------------------------------


def _make_controller() -> tuple[TransferController, MagicMock]:
    facade = MagicMock()
    vm = TransferViewModel()
    return TransferController(facade, vm), facade


def test_collect_sources_attaches_containers_to_fleet_and_planet_entries() -> None:
    controller, facade = _make_controller()
    fleet = SimpleNamespace(fleet_id=10, name="Alpha Fleet")
    colony = SimpleNamespace(planet_id=20, name="Alpha Colony", owner_id=1)
    facade.fleets.at_hex.return_value = [fleet]
    facade.planets.at_hex.return_value = [colony]

    fleet_snap = _snap("ship:s1:bay_inventory", owner_kind="fleet", owner_id=10)
    planet_snap = _snap(
        "planet:20:stockpile", owner_kind="planet", owner_id=20,
        label="Alpha Colony — Stockpile",
        allowed_kinds=frozenset({ContainableKind.RESOURCE}),
    )
    facade.fleets.get_containers.return_value = (fleet_snap,)
    facade.planets.get_containers.return_value = (planet_snap,)

    sources = controller.collect_sources_and_targets(
        source_fleet=None, hex_coord=(0, 0),
    )

    fleet_entry = next(s for s in sources if s["type"] == "fleet")
    colony_entry = next(s for s in sources if s["type"] == "colony")

    assert fleet_entry["containers"] == (fleet_snap,)
    facade.fleets.get_containers.assert_any_call(10)

    assert colony_entry["containers"] == (planet_snap,)
    facade.planets.get_containers.assert_any_call(20)


def test_collect_sources_attaches_containers_to_source_fleet_fallback() -> None:
    """When the facade doesn't list the source fleet at the hex, the
    controller injects it. The injected entry must still carry its
    container snapshots so downstream phases can reach them uniformly."""
    controller, facade = _make_controller()
    # Match `location` to `hex_coord` so the fallback `at_hex(projected)`
    # branch in `collect_sources_and_targets` is not exercised here —
    # this test is specifically about the source-fleet injection path.
    source_fleet = SimpleNamespace(
        id=7, name="Detached Fleet", location=(0, 0), orders=[],
    )
    facade.fleets.at_hex.return_value = []
    facade.planets.at_hex.return_value = []
    snap = _snap("ship:detached:bay_inventory", owner_kind="fleet", owner_id=7)
    facade.fleets.get_containers.return_value = (snap,)

    sources = controller.collect_sources_and_targets(
        source_fleet=source_fleet, hex_coord=(0, 0),
    )

    assert len(sources) == 1
    assert sources[0]["type"] == "fleet"
    assert sources[0]["id"] == 7
    assert sources[0]["containers"] == (snap,)
    facade.fleets.get_containers.assert_called_once_with(7)


def test_collect_sources_for_planet_entry_uses_planets_get_containers() -> None:
    controller, facade = _make_controller()
    planet = SimpleNamespace(planet_id=30, name="Wild Planet", owner_id=None)
    facade.fleets.at_hex.return_value = []
    facade.planets.at_hex.return_value = [planet]
    snap = _snap(
        "planet:30:stockpile", owner_kind="planet", owner_id=30,
        label="Wild Planet — Stockpile",
        allowed_kinds=frozenset({ContainableKind.RESOURCE}),
    )
    facade.planets.get_containers.return_value = (snap,)

    sources = controller.collect_sources_and_targets(
        source_fleet=None, hex_coord=(0, 0),
    )

    (entry,) = sources
    assert entry["type"] == "planet"
    assert entry["label"] == "Planet: Wild Planet"
    assert entry["containers"] == (snap,)


# ---------------------------------------------------------------------------
# ViewModel — get_amounts_from_containers reader
# ---------------------------------------------------------------------------


class TestGetAmountsFromContainers:
    def test_empty_snapshot_list_returns_empty_dict(self) -> None:
        assert TransferViewModel.get_amounts_from_containers(()) == {}

    def test_resource_entries_aggregate_across_snapshots(self) -> None:
        snap_a = _snap(
            "ship:a:bay_inventory",
            entries=(
                ContainerEntry(
                    kind=ContainableKind.RESOURCE,
                    type_id="metals",
                    quantity=10.0,
                    mass_total=10.0,
                ),
                ContainerEntry(
                    kind=ContainableKind.RESOURCE,
                    type_id="fuel",
                    quantity=2.5,
                    mass_total=2.5,
                ),
            ),
        )
        snap_b = _snap(
            "ship:b:bay_inventory",
            entries=(
                ContainerEntry(
                    kind=ContainableKind.RESOURCE,
                    type_id="metals",
                    quantity=4.0,
                    mass_total=4.0,
                ),
            ),
        )

        amounts = TransferViewModel.get_amounts_from_containers((snap_a, snap_b))

        # Resources aggregate, integer-coerced to match legacy
        # `get_amounts(info_obj)` int conventions.
        assert amounts == {"metals": 14, "fuel": 2}

    def test_population_entries_become_passengers_keys(self) -> None:
        snap = _snap(
            "planet:1:stockpile",
            owner_kind="planet",
            entries=(
                ContainerEntry(
                    kind=ContainableKind.POPULATION,
                    type_id="alpha",
                    quantity=7.0,
                    mass_total=0.7,
                ),
                ContainerEntry(
                    kind=ContainableKind.POPULATION,
                    type_id="zeta",
                    quantity=3.0,
                    mass_total=0.3,
                ),
            ),
        )

        amounts = TransferViewModel.get_amounts_from_containers((snap,))

        assert amounts == {"passengers_alpha": 7, "passengers_zeta": 3}

    def test_item_entries_are_ignored_in_phase_1_amounts(self) -> None:
        """Phase 1's amounts dict only covers resources + population (the
        legacy `get_amounts` shape). Items render through the existing
        `_build_pod_rows` path until Phase 3's mixed-content cutover."""
        snap = _snap(
            "planet:1:staging_yard",
            owner_kind="planet",
            entries=(
                ContainerEntry(
                    kind=ContainableKind.ITEM,
                    type_id="drop_pod_a",
                    quantity=1.0,
                    mass_total=10.0,
                ),
                ContainerEntry(
                    kind=ContainableKind.RESOURCE,
                    type_id="metals",
                    quantity=5.0,
                    mass_total=5.0,
                ),
            ),
        )

        amounts = TransferViewModel.get_amounts_from_containers((snap,))

        assert amounts == {"metals": 5}

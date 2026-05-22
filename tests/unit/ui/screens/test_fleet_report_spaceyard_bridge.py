"""PROJ-475 Phase 2 Task 2.6 — fleet-report spaceyard reads via the facade bridge.

The fleet report runs on raw ``ShipInstance`` lists, so a per-ship
``has_spaceyard`` lookup (``instance_id -> bool``), projected by the facade
(``ShipInfo.has_spaceyard``, Phase 1 Task 1.4), is threaded through the report
path. The spaceyard column / filter / sort consult that lookup instead of
calling ``FleetCapabilityCalculator.ship_has_spaceyard`` in the UI.
"""

from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace

from game.ui.filters.filter_state import FilterState
from game.ui.screens.fleet_data_source import FleetDataSource
from game.ui.screens.fleet_report_filters import filter_ships, sort_ships
from game.ui.screens.fleet_report_view_model import FleetListViewModel

_REPO_ROOT = Path(__file__).resolve().parents[4]


def _ship(instance_id: str, name: str = "S"):
    return SimpleNamespace(
        instance_id=instance_id,
        name=name,
        serial=1,
        design_data={"name": name},
        # Status-filter attributes (default: healthy + alive so the default
        # status filter does not exclude the ship).
        is_alive=True,
        is_derelict=False,
        is_damaged=lambda: False,
    )


class TestFilterSortUseLookup:
    def test_filter_excludes_by_lookup_not_calculator(self) -> None:
        yard = _ship("y1", "Carrier")
        no_yard = _ship("n1", "Destroyer")
        lookup = {"y1": True, "n1": False}

        # Keep only spaceyard ships.
        result = filter_ships(
            [yard, no_yard],
            {"has_spaceyard": FilterState.YES},
            spaceyard_lookup=lookup,
        )
        assert [s.instance_id for s in result] == ["y1"]

        # Keep only non-spaceyard ships.
        result = filter_ships(
            [yard, no_yard],
            {"has_spaceyard": FilterState.NO},
            spaceyard_lookup=lookup,
        )
        assert [s.instance_id for s in result] == ["n1"]

    def test_sort_by_spaceyard_uses_lookup(self) -> None:
        yard = _ship("y1")
        no_yard = _ship("n1")
        lookup = {"y1": True, "n1": False}

        result = sort_ships(
            [no_yard, yard], "spaceyard", descending=True, spaceyard_lookup=lookup
        )
        assert result[0].instance_id == "y1"


class TestViewModelHoldsLookup:
    def test_view_model_exposes_has_spaceyard(self) -> None:
        vm = FleetListViewModel([_ship("y1"), _ship("n1")])
        vm.set_spaceyard_lookup({"y1": True, "n1": False})

        assert vm.has_spaceyard("y1") is True
        assert vm.has_spaceyard("n1") is False
        # Unknown id defaults to False.
        assert vm.has_spaceyard("zzz") is False

    def test_filtered_ships_respect_lookup(self) -> None:
        vm = FleetListViewModel([_ship("y1"), _ship("n1")])
        vm.set_spaceyard_lookup({"y1": True, "n1": False})
        vm.set_filter_state("has_spaceyard", FilterState.YES)

        assert [s.instance_id for s in vm.get_filtered_ships()] == ["y1"]


class TestDataSourceFormatsFromLookup:
    def test_format_spaceyard_reads_lookup(self) -> None:
        vm = FleetListViewModel([_ship("y1"), _ship("n1")])
        vm.set_spaceyard_lookup({"y1": True, "n1": False})
        ds = FleetDataSource(vm)

        assert ds._format_spaceyard(_ship("y1")) == "Yes"
        assert ds._format_spaceyard(_ship("n1")) == "No"


def test_fleet_report_files_do_not_import_fleet_capability_calculator() -> None:
    """The three migrated readers must no longer import the calculator."""
    for rel in (
        "game/ui/screens/fleet_data_source.py",
        "game/ui/screens/fleet_report_filters.py",
    ):
        src = (_REPO_ROOT / rel).read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert "fleet_capability_calculator" not in node.module, (
                    f"{rel} still imports FleetCapabilityCalculator"
                )

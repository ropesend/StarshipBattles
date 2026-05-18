from __future__ import annotations

import pytest

from game.core.hex_math import HexCoord
from game.strategy.facade.dto.fleet_dto import FleetInfo
from game.strategy.facade.dto.planet_dto import PlanetInfo
from game.core.resources import ResourceCatalog
from game.ui.screens.transfer_view_model import TransferViewModel


# PROJ-436 Phase 7: the deleted ``RESOURCE_TYPES`` hardcoded list is
# replaced by ``ResourceCatalog.all_ids()`` ordering. The test layer
# resolves the canonical list once at import.
_CANONICAL_RESOURCE_IDS = ResourceCatalog.from_json().all_ids()


class TestTransferViewModelPendingMath:
    @pytest.mark.parametrize(
        ("sentinel", "delta", "expected"),
        [
            pytest.param(TransferViewModel.MAX_LOAD, 25, 25, id="load"),
            pytest.param(TransferViewModel.MAX_DROP, -10, -10, id="drop"),
        ],
    )
    def test_worker_i_transfer_vm_sentinel_reset(
        self,
        sentinel: float,
        delta: int,
        expected: int,
    ) -> None:
        vm = TransferViewModel()
        vm.pending_transfers["metals"] = sentinel

        result = vm.apply_arrow("metals", delta)

        assert result == expected
        assert vm.pending_transfers["metals"] == expected

    def test_worker_i_transfer_vm_apply_max_direction(self) -> None:
        vm = TransferViewModel()

        assert vm.apply_max("fuel", "load") == TransferViewModel.MAX_LOAD
        assert vm.pending_transfers["fuel"] == TransferViewModel.MAX_LOAD

        assert vm.apply_max("fuel", "drop") == TransferViewModel.MAX_DROP
        assert vm.pending_transfers["fuel"] == TransferViewModel.MAX_DROP

    def test_pending_reset_helpers_clear_specific_or_all_entries(self) -> None:
        vm = TransferViewModel()
        vm.pending_transfers = {"metals": 50, "fuel": -5}

        vm.set_pending_zero("metals")
        assert vm.pending_transfers == {"metals": 0, "fuel": -5}

        vm.clear_all_pending()
        assert vm.pending_transfers == {"metals": 0, "fuel": 0}

        vm.reset_pending()
        assert vm.pending_transfers == {}


class TestTransferViewModelRows:
    def test_worker_i_transfer_vm_species_key_ordering(self) -> None:
        vm = TransferViewModel(all_pod_names=["Empty Pod"])
        planet = PlanetInfo(
            planet_id=1,
            name="Colony",
            planet_type="CONTINENTAL",
            location=HexCoord(0, 0),
            orbit_distance=2,
            stockpile=(("metals", 50),),
            population_details=(
                ("zeta", 7, 0.7),
                ("alpha", 3, 0.9),
            ),
            staging_yard_summary=(("Drop Pod B", "Ship", 10.0, 1),),
        )
        fleet = FleetInfo(
            fleet_id=2,
            owner_id=1,
            name="Lift Fleet",
            composition_summary="1 transport",
            location=HexCoord(1, 0),
            speed=1.0,
            ship_count=1,
            passengers_current=5,
            cargo_resources=(("fuel", 12),),
            carried_items_summary=(("Drop Pod A", "Ship", 8.0, 2),),
        )

        rows = vm.build_row_data(planet, fleet)

        assert [row["cargo_key"] for row in rows[:len(_CANONICAL_RESOURCE_IDS)]] == _CANONICAL_RESOURCE_IDS

        species_start = len(_CANONICAL_RESOURCE_IDS)
        assert [row["cargo_key"] for row in rows[species_start:species_start + 3]] == [
            "passengers",
            "passengers_alpha",
            "passengers_zeta",
        ]
        assert [row["display_name"] for row in rows[species_start:species_start + 3]] == [
            "Population",
            "alpha",
            "zeta",
        ]
        assert [row["cargo_key"] for row in rows[-3:]] == [
            "drop_pod:Drop Pod A",
            "drop_pod:Drop Pod B",
            "drop_pod:Empty Pod",
        ]

    def test_filter_empty_limits_visible_rows_to_rows_with_amounts(self) -> None:
        vm = TransferViewModel()
        vm.row_data = [
            {"cargo_key": "metals", "source_amt": 0, "target_amt": 0},
            {"cargo_key": "fuel", "source_amt": 1, "target_amt": 0},
            {"cargo_key": "ammo", "source_amt": 0, "target_amt": 2},
        ]

        assert vm.visible_rows() == vm.row_data
        assert vm.toggle_filter_empty() is True
        assert [row["cargo_key"] for row in vm.visible_rows()] == ["fuel", "ammo"]

    def test_source_and_target_selection_updates_labels_and_defaults(self) -> None:
        vm = TransferViewModel()
        vm.set_sources([
            {"label": "Fleet A", "type": "fleet", "id": 1},
            {"label": "Colony B", "type": "colony", "id": 2},
            {"label": "Fleet C", "type": "fleet", "id": 3},
        ])

        selected = vm.select_source("Fleet A")

        assert selected == {"label": "Fleet A", "type": "fleet", "id": 1}
        assert vm.source_labels() == ["Fleet A", "Colony B", "Fleet C"]
        assert vm.target_labels() == ["Colony B", "Fleet C"]
        assert vm.current_target == {"label": "Colony B", "type": "colony", "id": 2}

        assert vm.select_target("Fleet C") == {"label": "Fleet C", "type": "fleet", "id": 3}
        assert vm.select_source("Missing") is None
        assert vm.select_target("Missing") is None

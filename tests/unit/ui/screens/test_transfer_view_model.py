from __future__ import annotations

import pytest

from game.core.hex_math import HexCoord
from game.strategy.facade.dto.fleet_dto import FleetInfo
from game.strategy.facade.dto.planet_dto import PlanetInfo
from game.ui.screens.transfer_view_model import RESOURCE_TYPES, TransferViewModel


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

        assert [row["cargo_key"] for row in rows[:len(RESOURCE_TYPES)]] == RESOURCE_TYPES

        species_start = len(RESOURCE_TYPES)
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

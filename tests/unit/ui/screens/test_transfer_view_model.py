from __future__ import annotations

import pytest

from game.ui.screens.transfer_view_model import TransferViewModel


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
    # PROJ-437 Phase 4: legacy DTO row-builder retired
    # (`build_row_data`, `get_amounts`, `_build_pod_rows`,
    # `all_pod_names`). The container-driven builder is covered at
    # tests/unit/ui/screens/test_transfer_mixed_content.py — equivalent
    # row-ordering pins live there.

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

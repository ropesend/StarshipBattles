"""Characterization tests for TransferDialog (PROJ-328 Phase C).

Pin down current behaviour BEFORE the deep MVVM split so the refactor
has a safety net. These tests are intentionally written against the
*pre-refactor* class shape — methods like ``_on_arrow_click``,
``_on_max_click``, ``_format_pending``, ``_on_confirm``,
``_get_amounts``, ``_add_pod_rows``, ``_on_source_changed`` — and
exercise the actual production logic, not mocks of it.

Per the consensus refactor plan
(``Projects/active_projects/PROJ-325/findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md``)
TransferDialog is "command-heavy. Add focused tests around
pending-transfer math and IssueTransferCommand emission BEFORE moving
UI code." This file is that safety net.

Areas covered:

* Pending-transfer math: arrow-button increments, sentinel resets
  (Max → specific amount), max set, clear-all, format strings.
* ``_on_confirm`` command emission: fleet→colony, colony→fleet,
  fleet→fleet, both-non-fleet abort, no-source/no-target abort,
  zero-amount skipping, Max-sentinel translation to amount=0,
  cargo_key parsing (passengers / passengers_<species> / drop_pod:<name>
  / plain resource), direction inference per source/target type.
* ``_get_amounts`` extraction from FleetInfo + PlanetInfo DTOs.
* ``_add_pod_rows`` merging of known pod designs with actual pod
  counts on either side.
* ``_on_source_changed`` target-list filtering (selected source not in
  targets) + ``_current_source``/``_current_target`` updates.

After the Phase C refactor lands, these tests must still pass — the
math/emission logic moves into ``TransferViewModel`` /
``TransferController`` but the observable behaviour driven through the
dialog's existing surface is unchanged.
"""
from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import pygame
import pygame_gui

from game.strategy.engine.commands import IssueTransferCommand
from game.strategy.facade.dto import FleetInfo, PlanetInfo
from game.ui.screens.transfer_dialog import (
    ARROW_INCREMENTS_DROP,
    ARROW_INCREMENTS_LOAD,
    RESOURCE_TYPES,
    TransferDialog,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_manager():
    return pygame_gui.UIManager((800, 600))


@pytest.fixture
def mock_scene():
    scene = MagicMock()
    scene._facade = MagicMock()
    scene.facade = scene._facade
    return scene


@pytest.fixture
def mock_fleet():
    fleet = MagicMock()
    fleet.id = 1
    fleet.fleet_id = 1
    fleet.configure_mock(name="Fleet 1")
    fleet.location = (0, 0)
    return fleet


def _empty_fleet_info() -> Any:
    info = MagicMock(spec=FleetInfo)
    info.passengers_current = 0
    info.cargo_resources = ()
    info.cargo_capacities = ()
    info.carried_items_summary = ()
    return info


def _empty_planet_info() -> Any:
    info = MagicMock(spec=PlanetInfo)
    info.population_details = ()
    info.stockpile = ()
    info.max_stockpile = ()
    info.staging_yard_summary = ()
    return info


def _make_dialog(mock_manager, mock_scene, mock_fleet,
                 *, fleets=None, planets=None,
                 fleet_info=None, planet_info=None) -> TransferDialog:
    """Build a TransferDialog through the real ``__init__``.

    The dialog needs a real pygame_gui shell because it constructs
    ``UIDropDownMenu`` etc. inside ``_setup_ui`` — that's the very
    coupling Phase C refactors away. For characterization we accept
    the cost (these tests still complete in well under a second each).
    """
    mock_scene._facade.fleets.at_hex.return_value = list(fleets or [])
    mock_scene._facade.planets.at_hex.return_value = list(planets or [])
    mock_scene._facade.fleets.get.return_value = fleet_info or _empty_fleet_info()
    mock_scene._facade.planets.get.return_value = planet_info or _empty_planet_info()

    rect = pygame.Rect(0, 0, 900, 700)
    return TransferDialog(
        rect, mock_manager, mock_fleet, (0, 0), mock_scene, window_manager=None,
    )


# ---------------------------------------------------------------------------
# Pending-transfer math — _on_arrow_click / _on_max_click / _format_pending
# ---------------------------------------------------------------------------


class TestPendingTransferMath:
    def test_arrow_click_adds_delta_from_zero(self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        dialog._pending_labels["metals"] = MagicMock()
        dialog._on_arrow_click("metals", 1000)
        assert dialog.pending_transfers["metals"] == 1000

    def test_arrow_click_negative_delta_sets_drop(self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        dialog._pending_labels["fuel"] = MagicMock()
        dialog._on_arrow_click("fuel", -10)
        assert dialog.pending_transfers["fuel"] == -10

    def test_arrow_click_accumulates_deltas(self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        dialog._pending_labels["metals"] = MagicMock()
        dialog._on_arrow_click("metals", 100)
        dialog._on_arrow_click("metals", 1000)
        dialog._on_arrow_click("metals", 1)
        assert dialog.pending_transfers["metals"] == 1101

    def test_arrow_click_resets_max_load_sentinel_to_zero_first(
            self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        dialog._pending_labels["metals"] = MagicMock()
        dialog.pending_transfers["metals"] = TransferDialog.MAX_LOAD
        dialog._on_arrow_click("metals", 50)
        # Was Max; reset to 0 then add 50.
        assert dialog.pending_transfers["metals"] == 50

    def test_arrow_click_resets_max_drop_sentinel_to_zero_first(
            self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        dialog._pending_labels["metals"] = MagicMock()
        dialog.pending_transfers["metals"] = TransferDialog.MAX_DROP
        dialog._on_arrow_click("metals", -50)
        assert dialog.pending_transfers["metals"] == -50

    def test_max_click_load_sets_max_load_sentinel(self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        dialog._pending_labels["organics"] = MagicMock()
        dialog._on_max_click("organics", "load")
        assert dialog.pending_transfers["organics"] == TransferDialog.MAX_LOAD

    def test_max_click_drop_sets_max_drop_sentinel(self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        dialog._pending_labels["organics"] = MagicMock()
        dialog._on_max_click("organics", "drop")
        assert dialog.pending_transfers["organics"] == TransferDialog.MAX_DROP

    def test_format_pending_zero_returns_zero_string(self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        assert dialog._format_pending(0) == "0"

    def test_format_pending_positive_says_load(self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        assert dialog._format_pending(123) == "Load 123"

    def test_format_pending_negative_says_drop_with_abs(
            self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        assert dialog._format_pending(-456) == "Drop 456"

    def test_format_pending_max_load_returns_load_max(
            self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        assert dialog._format_pending(TransferDialog.MAX_LOAD) == "Load Max"

    def test_format_pending_max_drop_returns_drop_max(
            self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        assert dialog._format_pending(TransferDialog.MAX_DROP) == "Drop Max"

    def test_clear_all_zeros_existing_keys(self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        dialog._pending_labels["metals"] = MagicMock()
        dialog._pending_labels["fuel"] = MagicMock()
        dialog.pending_transfers["metals"] = 100
        dialog.pending_transfers["fuel"] = TransferDialog.MAX_LOAD
        dialog._on_clear_all()
        assert dialog.pending_transfers["metals"] == 0
        assert dialog.pending_transfers["fuel"] == 0

    def test_arrow_increments_constants_are_5_each(self):
        # Pin: 5 gradations per direction. Refactor must preserve.
        assert len(ARROW_INCREMENTS_LOAD) == 5
        assert len(ARROW_INCREMENTS_DROP) == 5

    def test_arrow_increments_load_descending(self):
        # Load buttons go largest→smallest left-to-right.
        assert ARROW_INCREMENTS_LOAD == sorted(ARROW_INCREMENTS_LOAD, reverse=True)

    def test_arrow_increments_drop_ascending(self):
        # Drop buttons go smallest→largest left-to-right.
        assert ARROW_INCREMENTS_DROP == sorted(ARROW_INCREMENTS_DROP)


# ---------------------------------------------------------------------------
# _get_amounts extraction
# ---------------------------------------------------------------------------


class TestGetAmounts:
    def test_get_amounts_none_returns_empty(self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        assert dialog._get_amounts(None) == {}

    def test_get_amounts_fleet_includes_resources_and_passengers(
            self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        info = MagicMock(spec=FleetInfo)
        info.cargo_resources = (("metals", 100), ("fuel", 50.0))
        info.passengers_current = 7
        amounts = dialog._get_amounts(info)
        assert amounts["metals"] == 100
        assert amounts["fuel"] == 50  # Coerced to int.
        assert amounts["passengers"] == 7

    def test_get_amounts_planet_includes_stockpile_and_population(
            self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        info = MagicMock(spec=PlanetInfo)
        info.stockpile = (("metals", 1234.5),)
        # population_details: (race_id, count, _)
        info.population_details = [("humans", 100, None), ("elves", 25, None)]
        amounts = dialog._get_amounts(info)
        assert amounts["metals"] == 1234  # int-coerced.
        assert amounts["passengers_humans"] == 100
        assert amounts["passengers_elves"] == 25


# ---------------------------------------------------------------------------
# _on_source_changed target filtering
# ---------------------------------------------------------------------------


class TestSourceChange:
    def test_on_source_changed_excludes_selected_source_from_targets(
            self, mock_manager, mock_scene, mock_fleet):
        f1 = MagicMock(fleet_id=1, owner_id=0)
        f1.configure_mock(name="Fleet 1")
        f2 = MagicMock(fleet_id=2, owner_id=0)
        f2.configure_mock(name="Fleet 2")
        dialog = _make_dialog(
            mock_manager, mock_scene, mock_fleet, fleets=[f1, f2],
        )
        dialog._on_source_changed("Fleet 1")
        target_labels = [t["label"] for t in dialog.available_targets]
        assert "Fleet 1" not in target_labels
        assert "Fleet 2" in target_labels
        assert dialog._current_source["label"] == "Fleet 1"

    def test_on_source_changed_unknown_label_is_noop(
            self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        before = dialog._current_source
        dialog._on_source_changed("Nonexistent Label")
        # _current_source not changed when label not found.
        assert dialog._current_source is before


# ---------------------------------------------------------------------------
# _add_pod_rows merging
# ---------------------------------------------------------------------------


class TestAddPodRows:
    def test_pod_rows_merge_known_designs_with_present_pods(
            self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        # Reset to known-pod-design list.
        dialog._all_pod_names = ["MarinePod"]
        dialog._row_data = []

        source = MagicMock(spec=PlanetInfo)
        source.staging_yard_summary = (("MarinePod", "Drop Pod", 5, 3),)
        target = MagicMock(spec=FleetInfo)
        target.carried_items_summary = (("HazmatPod", "Drop Pod", 5, 1),)

        dialog._add_pod_rows(source, target)

        keys = [r["cargo_key"] for r in dialog._row_data]
        assert "drop_pod:MarinePod" in keys
        assert "drop_pod:HazmatPod" in keys
        # source carries 3 MarinePods; target carries 1 HazmatPod.
        marine_row = next(r for r in dialog._row_data
                          if r["cargo_key"] == "drop_pod:MarinePod")
        hazmat_row = next(r for r in dialog._row_data
                          if r["cargo_key"] == "drop_pod:HazmatPod")
        assert marine_row["source_amt"] == 3
        assert marine_row["target_amt"] == 0
        assert hazmat_row["source_amt"] == 0
        assert hazmat_row["target_amt"] == 1


# ---------------------------------------------------------------------------
# _on_confirm command emission
# ---------------------------------------------------------------------------


class TestConfirmCommandEmission:
    def test_confirm_aborts_when_no_source(self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        dialog._current_source = None
        dialog._current_target = {"type": "fleet", "id": 2, "label": "x"}
        dialog.pending_transfers = {"metals": 100}
        with patch.object(dialog, "kill"):
            dialog._on_confirm()
        mock_scene._facade.handle_command.assert_not_called()

    def test_confirm_aborts_when_no_target(self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        dialog._current_source = {"type": "fleet", "id": 1, "label": "x"}
        dialog._current_target = None
        dialog.pending_transfers = {"metals": 100}
        with patch.object(dialog, "kill"):
            dialog._on_confirm()
        mock_scene._facade.handle_command.assert_not_called()

    def test_confirm_skips_zero_pending(self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        dialog._current_source = {"type": "fleet", "id": 1, "label": "F1"}
        dialog._current_target = {"type": "colony", "id": 10, "label": "Alpha"}
        dialog.pending_transfers = {"metals": 0, "fuel": 0}
        mock_scene._facade.handle_command.return_value = MagicMock(is_valid=True)
        with patch.object(dialog, "kill"):
            dialog._on_confirm()
        mock_scene._facade.handle_command.assert_not_called()

    def test_confirm_aborts_when_both_non_fleet(self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        dialog._current_source = {"type": "colony", "id": 10, "label": "Alpha"}
        dialog._current_target = {"type": "planet", "id": 11, "label": "Beta"}
        dialog.pending_transfers = {"metals": 100}
        mock_scene._facade.handle_command.return_value = MagicMock(is_valid=True)
        with patch.object(dialog, "kill"):
            dialog._on_confirm()
        mock_scene._facade.handle_command.assert_not_called()

    def test_confirm_fleet_to_colony_load_direction(
            self, mock_manager, mock_scene, mock_fleet):
        # Fleet → colony, positive amount = load (target → fleet).
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        dialog._current_source = {"type": "fleet", "id": 1, "label": "F1"}
        dialog._current_target = {"type": "colony", "id": 10, "label": "Alpha"}
        dialog.pending_transfers = {"metals": 50}
        mock_scene._facade.handle_command.return_value = MagicMock(is_valid=True)
        with patch.object(dialog, "kill"):
            dialog._on_confirm()
        mock_scene._facade.handle_command.assert_called_once()
        cmd = mock_scene._facade.handle_command.call_args[0][0]
        assert isinstance(cmd, IssueTransferCommand)
        assert cmd.fleet_id == 1
        assert cmd.planet_id == 10
        assert cmd.cargo_type == "metals"
        assert cmd.direction == "load"
        assert cmd.amount == 50
        assert cmd.species_id is None
        assert cmd.target_fleet_id is None

    def test_confirm_fleet_to_colony_drop_direction(
            self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        dialog._current_source = {"type": "fleet", "id": 1, "label": "F1"}
        dialog._current_target = {"type": "colony", "id": 10, "label": "Alpha"}
        dialog.pending_transfers = {"fuel": -100}
        mock_scene._facade.handle_command.return_value = MagicMock(is_valid=True)
        with patch.object(dialog, "kill"):
            dialog._on_confirm()
        cmd = mock_scene._facade.handle_command.call_args[0][0]
        assert cmd.direction == "unload"
        assert cmd.amount == 100  # abs of -100

    def test_confirm_colony_to_fleet_swaps_direction(
            self, mock_manager, mock_scene, mock_fleet):
        # Source is colony, target is fleet. Positive amount = "load" from
        # the user's perspective (load into fleet) but command direction
        # is "unload" because the colony is the planet side.
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        dialog._current_source = {"type": "colony", "id": 10, "label": "Alpha"}
        dialog._current_target = {"type": "fleet", "id": 1, "label": "F1"}
        dialog.pending_transfers = {"metals": 50}
        mock_scene._facade.handle_command.return_value = MagicMock(is_valid=True)
        with patch.object(dialog, "kill"):
            dialog._on_confirm()
        cmd = mock_scene._facade.handle_command.call_args[0][0]
        assert cmd.fleet_id == 1
        assert cmd.planet_id == 10
        assert cmd.direction == "unload"  # colony→fleet positive flips.
        assert cmd.amount == 50

    def test_confirm_fleet_to_fleet_uses_target_fleet_id(
            self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        dialog._current_source = {"type": "fleet", "id": 1, "label": "F1"}
        dialog._current_target = {"type": "fleet", "id": 2, "label": "F2"}
        dialog.pending_transfers = {"passengers": -20}
        mock_scene._facade.handle_command.return_value = MagicMock(is_valid=True)
        with patch.object(dialog, "kill"):
            dialog._on_confirm()
        cmd = mock_scene._facade.handle_command.call_args[0][0]
        assert cmd.fleet_id == 1
        assert cmd.target_fleet_id == 2
        assert cmd.planet_id is None
        assert cmd.direction == "unload"
        assert cmd.amount == 20

    def test_confirm_max_load_sentinel_translates_to_amount_zero(
            self, mock_manager, mock_scene, mock_fleet):
        # MAX_LOAD/MAX_DROP signal "transfer all"; engine convention is
        # amount=0 means all-available.
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        dialog._current_source = {"type": "fleet", "id": 1, "label": "F1"}
        dialog._current_target = {"type": "colony", "id": 10, "label": "Alpha"}
        dialog.pending_transfers = {"metals": TransferDialog.MAX_LOAD}
        mock_scene._facade.handle_command.return_value = MagicMock(is_valid=True)
        with patch.object(dialog, "kill"):
            dialog._on_confirm()
        cmd = mock_scene._facade.handle_command.call_args[0][0]
        assert cmd.amount == 0
        assert cmd.direction == "load"

    def test_confirm_max_drop_sentinel_translates_to_amount_zero_unload(
            self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        dialog._current_source = {"type": "fleet", "id": 1, "label": "F1"}
        dialog._current_target = {"type": "colony", "id": 10, "label": "Alpha"}
        dialog.pending_transfers = {"metals": TransferDialog.MAX_DROP}
        mock_scene._facade.handle_command.return_value = MagicMock(is_valid=True)
        with patch.object(dialog, "kill"):
            dialog._on_confirm()
        cmd = mock_scene._facade.handle_command.call_args[0][0]
        assert cmd.amount == 0
        assert cmd.direction == "unload"

    def test_confirm_passengers_no_species(self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        dialog._current_source = {"type": "fleet", "id": 1, "label": "F1"}
        dialog._current_target = {"type": "colony", "id": 10, "label": "Alpha"}
        dialog.pending_transfers = {"passengers": 10}
        mock_scene._facade.handle_command.return_value = MagicMock(is_valid=True)
        with patch.object(dialog, "kill"):
            dialog._on_confirm()
        cmd = mock_scene._facade.handle_command.call_args[0][0]
        assert cmd.cargo_type == "passengers"
        assert cmd.species_id is None

    def test_confirm_passengers_with_species(self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        dialog._current_source = {"type": "fleet", "id": 1, "label": "F1"}
        dialog._current_target = {"type": "colony", "id": 10, "label": "Alpha"}
        dialog.pending_transfers = {"passengers_humans": 10}
        mock_scene._facade.handle_command.return_value = MagicMock(is_valid=True)
        with patch.object(dialog, "kill"):
            dialog._on_confirm()
        cmd = mock_scene._facade.handle_command.call_args[0][0]
        assert cmd.cargo_type == "passengers"
        assert cmd.species_id == "humans"

    def test_confirm_drop_pod_parses_pod_name(self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        dialog._current_source = {"type": "fleet", "id": 1, "label": "F1"}
        dialog._current_target = {"type": "colony", "id": 10, "label": "Alpha"}
        dialog.pending_transfers = {"drop_pod:MarinePod": -2}
        mock_scene._facade.handle_command.return_value = MagicMock(is_valid=True)
        with patch.object(dialog, "kill"):
            dialog._on_confirm()
        cmd = mock_scene._facade.handle_command.call_args[0][0]
        assert cmd.cargo_type == "drop_pod"
        assert cmd.species_id == "MarinePod"
        assert cmd.amount == 2
        assert cmd.direction == "unload"

    def test_confirm_emits_one_command_per_nonzero_pending(
            self, mock_manager, mock_scene, mock_fleet):
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        dialog._current_source = {"type": "fleet", "id": 1, "label": "F1"}
        dialog._current_target = {"type": "colony", "id": 10, "label": "Alpha"}
        dialog.pending_transfers = {
            "metals": 100, "fuel": -50, "energy": 0, "ammo": 25,
        }
        mock_scene._facade.handle_command.return_value = MagicMock(is_valid=True)
        with patch.object(dialog, "kill"):
            dialog._on_confirm()
        assert mock_scene._facade.handle_command.call_count == 3

    def test_confirm_kills_dialog_even_when_controller_raises(
            self, mock_manager, mock_scene, mock_fleet):
        # Regression (PROJ-321..328 audit, S1.2): if confirm_pending raises
        # — command dispatch failure, validation error, etc. — the dialog
        # MUST still be torn down via self.kill() so we don't leave an
        # orphaned window the user can re-click. The original exception
        # MUST propagate; we only guarantee cleanup, never swallow.
        dialog = _make_dialog(mock_manager, mock_scene, mock_fleet)
        dialog._controller = MagicMock()
        dialog._controller.confirm_pending = MagicMock(
            side_effect=RuntimeError("dispatch boom")
        )
        with patch.object(dialog, "kill") as mock_kill:
            with pytest.raises(RuntimeError, match="dispatch boom"):
                dialog._on_confirm()
            mock_kill.assert_called_once()


# ---------------------------------------------------------------------------
# RESOURCE_TYPES constant pin
# ---------------------------------------------------------------------------


class TestResourceTypesConstant:
    def test_8_resource_types_in_canonical_order(self):
        assert RESOURCE_TYPES == [
            "metals", "organics", "vapors", "radioactives", "exotics",
            "fuel", "energy", "ammo",
        ]


# ---------------------------------------------------------------------------
# Two-stage construction (PROJ-328 Phase C) — bypass + Mock builder.
# These exercise the new fixtures at tests/fixtures/transfer_ui_builder.py.
# ---------------------------------------------------------------------------


class TestTwoStageConstruction:
    """Verify Stage-1 cheap state survives ``bypass_init`` and the
    Mock builder populates widget slots without a live display."""

    def _build(self, *, ui_builder=None, scene=None, source_fleet=None):
        from tests.fixtures.ui_widget_factory import bypass_init

        scene = scene or _make_scene()
        source_fleet = source_fleet or _make_source_fleet()

        with bypass_init(TransferDialog):
            return TransferDialog(
                pygame.Rect(0, 0, 900, 700),
                MagicMock(name="ui_manager"),
                source_fleet,
                (0, 0),
                scene,
                window_manager=None,
                ui_builder=ui_builder,
            )

    def test_bypass_with_null_builder_leaves_widget_slots_empty(self):
        from tests.fixtures.transfer_ui_builder import NullTransferUiBuilder

        dialog = self._build(ui_builder=NullTransferUiBuilder())
        # Cheap state is present.
        assert dialog.view_model is not None
        assert dialog._controller is not None
        assert dialog._renderer is not None
        # Widget slots are placeholders.
        assert dialog.drop_source is None
        assert dialog.btn_confirm is None
        assert dialog.grid_container is None
        assert dialog._arrow_buttons == {}

    def test_bypass_without_builder_leaves_widget_slots_empty(self):
        # No ui_builder supplied → bypass branch returns without
        # invoking any builder (production builder would crash on a
        # mock manager).
        dialog = self._build(ui_builder=None)
        assert dialog.drop_source is None
        assert dialog.btn_confirm is None

    def test_bypass_with_mock_builder_populates_widgets(self):
        from tests.fixtures.transfer_ui_builder import MockTransferUiBuilder

        scene = _make_scene()
        # Seed the facade so populate_initial_data finds a fleet at
        # the hex.
        f1 = MagicMock(fleet_id=1, owner_id=0)
        f1.configure_mock(name="Fleet 1")
        scene.facade.fleets.at_hex.return_value = [f1]
        scene.facade.planets.at_hex.return_value = []
        scene.facade.fleets.get.return_value = _empty_fleet_info()
        scene.facade.planets.get.return_value = _empty_planet_info()

        dialog = self._build(
            ui_builder=MockTransferUiBuilder(),
            scene=scene,
        )

        assert dialog.drop_source is not None
        assert dialog.drop_target is not None
        assert dialog.btn_confirm is not None
        assert dialog.btn_cancel is not None
        assert dialog.btn_clear_all is not None
        assert dialog.btn_filter is not None
        assert dialog.grid_container is not None
        # populate_initial_data ran → row_data has the canonical
        # 8 resource rows.
        resource_keys = [r["cargo_key"] for r in dialog._row_data
                         if r["cargo_key"] in RESOURCE_TYPES]
        assert len(resource_keys) == 8

    def test_bypassed_dialog_pending_math_works_end_to_end(self):
        """ViewModel-driven math + label refresh works under bypass
        with the Mock builder (renderer's update_pending_label path
        does not crash on Mock labels)."""
        from tests.fixtures.transfer_ui_builder import MockTransferUiBuilder

        scene = _make_scene()
        f1 = MagicMock(fleet_id=1, owner_id=0)
        f1.configure_mock(name="Fleet 1")
        p1 = MagicMock(planet_id=10, owner_id=0)
        p1.name = "Alpha"
        scene.facade.fleets.at_hex.return_value = [f1]
        scene.facade.planets.at_hex.return_value = [p1]
        scene.facade.fleets.get.return_value = _empty_fleet_info()
        scene.facade.planets.get.return_value = _empty_planet_info()

        dialog = self._build(
            ui_builder=MockTransferUiBuilder(),
            scene=scene,
        )

        # Manually wire a pending label for "metals" (the Mock
        # builder skipped the per-row construction).
        dialog._pending_labels["metals"] = MagicMock(name="metals_label")

        dialog._on_arrow_click("metals", 100)
        dialog._on_arrow_click("metals", 1000)
        assert dialog.pending_transfers["metals"] == 1100
        # Label.set_text was called twice (once per arrow click).
        assert dialog._pending_labels["metals"].set_text.call_count == 2


def _make_scene() -> Any:
    scene = MagicMock()
    scene._facade = MagicMock()
    scene.facade = scene._facade
    return scene


def _make_source_fleet() -> Any:
    fleet = MagicMock()
    fleet.id = 1
    fleet.fleet_id = 1
    fleet.configure_mock(name="Fleet 1")
    fleet.location = (0, 0)
    return fleet

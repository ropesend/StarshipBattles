"""Pure tests for workshop data reload orchestration."""
from __future__ import annotations

from contextlib import nullcontext
import os
from types import SimpleNamespace
from unittest.mock import MagicMock

from game.core.paths import Paths
from game.ui.screens.builder_utils import BuilderEvents
from game.ui.screens.workshop_data_loader import LoadResult
from game.ui.screens.workshop_data_reloader import WorkshopDataReloader


def _disable_profiling(monkeypatch) -> None:
    monkeypatch.setattr(
        "game.ui.screens.workshop_data_reloader.profile_block",
        lambda _label: nullcontext(),
    )


def _make_reloader() -> tuple[WorkshopDataReloader, SimpleNamespace]:
    context = SimpleNamespace(registries=object())
    ship = SimpleNamespace(name="New Ship")
    viewmodel = SimpleNamespace(
        refresh_available_components=MagicMock(),
        create_default_ship=MagicMock(return_value=ship),
        clear_selection=MagicMock(),
        ship=SimpleNamespace(name="Old Ship"),
    )
    right_panel = MagicMock()
    left_panel = MagicMock()
    view = SimpleNamespace(selected_component="old")
    controller = SimpleNamespace(selected_component="old")
    callbacks = SimpleNamespace(
        context=context,
        ship_io_adapter=MagicMock(),
        viewmodel=viewmodel,
        show_error=MagicMock(),
        classes={"Cruiser": {"type": "Ship"}},
        event_bus=MagicMock(),
        right_panel=right_panel,
        left_panel=left_panel,
        view=view,
        controller=controller,
        rebuild_modifier_ui=MagicMock(),
        update_stats=MagicMock(),
        new_ship=ship,
    )
    reloader = WorkshopDataReloader(
        context=context,
        ship_io_adapter=callbacks.ship_io_adapter,
        viewmodel=viewmodel,
        show_error_callback=callbacks.show_error,
        get_vehicle_classes_callback=lambda: callbacks.classes,
        event_bus=callbacks.event_bus,
        right_panel_ref=lambda: right_panel,
        left_panel_ref=lambda: left_panel,
        view_ref=lambda: view,
        controller_ref=lambda: controller,
        rebuild_modifier_ui_callback=callbacks.rebuild_modifier_ui,
        update_stats_callback=callbacks.update_stats,
    )
    return reloader, callbacks


def _patch_loader(monkeypatch, load_result: LoadResult) -> list[object]:
    created = []

    class FakeLoader:
        def __init__(self, directory: str, *, registries: object) -> None:
            self.directory = directory
            self.registries = registries
            created.append(self)

        def load_all(self) -> LoadResult:
            return load_result

    monkeypatch.setattr(
        "game.ui.screens.workshop_data_reloader.WorkshopDataLoader",
        FakeLoader,
    )
    return created


def test_reload_data_success_refreshes_ui_and_emits_registry_reloaded(monkeypatch) -> None:
    reloader, callbacks = _make_reloader()
    directory = os.path.join("tmp", "custom_data")
    created = _patch_loader(monkeypatch, LoadResult(default_class="Cruiser"))

    reloader.reload_data(directory)

    assert created[0].directory == directory
    assert created[0].registries is callbacks.context.registries
    callbacks.right_panel.refresh_controls.assert_called_once_with()
    assert callbacks.left_panel.update_component_list.call_count == 2
    assert callbacks.rebuild_modifier_ui.call_count == 2
    callbacks.viewmodel.refresh_available_components.assert_called_once_with()
    callbacks.viewmodel.create_default_ship.assert_called_once_with(ship_class="Cruiser")
    assert callbacks.viewmodel.ship is callbacks.new_ship
    assert callbacks.view.selected_component is None
    assert callbacks.controller.selected_component is None
    callbacks.viewmodel.clear_selection.assert_called_once_with()
    callbacks.right_panel.update_dropdowns_for_data_reload.assert_called_once_with(
        "Cruiser",
        callbacks.classes,
    )
    callbacks.update_stats.assert_called_once_with()
    callbacks.event_bus.emit.assert_called_once_with(
        BuilderEvents.REGISTRY_RELOADED,
        None,
    )
    callbacks.show_error.assert_called_once_with("Reloaded data from custom_data")


def test_reload_data_failure_reports_first_error_without_refresh(monkeypatch) -> None:
    reloader, callbacks = _make_reloader()
    _patch_loader(
        monkeypatch,
        LoadResult(success=False, errors=["bad component", "bad class"]),
    )

    reloader.reload_data("broken_data")

    callbacks.show_error.assert_called_once_with(
        "Data loading failed: bad component"
    )
    callbacks.right_panel.refresh_controls.assert_not_called()
    callbacks.viewmodel.refresh_available_components.assert_not_called()
    callbacks.event_bus.emit.assert_not_called()


def test_reload_data_failure_without_errors_reports_unknown(monkeypatch) -> None:
    reloader, callbacks = _make_reloader()
    _patch_loader(monkeypatch, LoadResult(success=False))

    reloader.reload_data("broken_data")

    callbacks.show_error.assert_called_once_with(
        "Data loading failed: Unknown error"
    )
    callbacks.right_panel.refresh_controls.assert_not_called()


def test_reload_data_catches_expected_loader_errors(monkeypatch) -> None:
    reloader, callbacks = _make_reloader()

    class RaisingLoader:
        def __init__(self, _directory: str, *, registries: object) -> None:
            self.registries = registries

        def load_all(self) -> LoadResult:
            raise ValueError("bad payload")

    monkeypatch.setattr(
        "game.ui.screens.workshop_data_reloader.WorkshopDataLoader",
        RaisingLoader,
    )

    reloader.reload_data("broken_data")

    callbacks.show_error.assert_called_once_with(
        "Error reloading data: bad payload"
    )
    callbacks.right_panel.refresh_controls.assert_not_called()
    callbacks.event_bus.emit.assert_not_called()


def test_on_select_data_pressed_reports_when_tk_root_is_missing(monkeypatch) -> None:
    reloader, callbacks = _make_reloader()
    monkeypatch.setattr("game.ui.screens.workshop_data_reloader.tk_root", None)

    reloader.on_select_data_pressed()

    callbacks.show_error.assert_called_once_with(
        "Tkinter not initialized, cannot open dialog"
    )


def test_on_select_data_pressed_reloads_chosen_directory(monkeypatch) -> None:
    _disable_profiling(monkeypatch)
    reloader, _callbacks = _make_reloader()
    directory = os.path.join("tmp", "chosen")
    reload_data = MagicMock()
    reloader.reload_data = reload_data
    askdirectory = MagicMock(return_value=directory)
    monkeypatch.setattr("game.ui.screens.workshop_data_reloader.tk_root", object())
    monkeypatch.setattr(
        "game.ui.screens.workshop_data_reloader.filedialog.askdirectory",
        askdirectory,
    )

    reloader.on_select_data_pressed()

    askdirectory.assert_called_once_with(
        initialdir=Paths.DATA_DIR,
        title="Select Data Directory",
    )
    reload_data.assert_called_once_with(directory)


def test_load_standard_data_sets_standard_ship_folder_and_status(monkeypatch) -> None:
    _disable_profiling(monkeypatch)
    reloader, callbacks = _make_reloader()
    reloader.reload_data = MagicMock()

    reloader.load_standard_data()

    reloader.reload_data.assert_called_once_with(Paths.DATA_DIR)
    callbacks.ship_io_adapter.set_ships_folder.assert_called_once_with(Paths.SHIPS_DIR)
    callbacks.show_error.assert_called_once_with(
        f"Loaded Standard Data \u2022 Ships: {Paths.SHIPS_DIR}"
    )


def test_load_test_data_sets_test_ship_folder_and_status(monkeypatch) -> None:
    _disable_profiling(monkeypatch)
    reloader, callbacks = _make_reloader()
    reloader.reload_data = MagicMock()

    reloader.load_test_data()

    reloader.reload_data.assert_called_once_with(os.path.join(os.getcwd(), "tests", "data"))
    callbacks.ship_io_adapter.set_ships_folder.assert_called_once_with(
        os.path.join("tests", "data", "ships")
    )
    callbacks.show_error.assert_called_once_with(
        "Loaded Test Data \u2022 Ships: tests/data/ships/"
    )

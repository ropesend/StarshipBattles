from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from game.strategy.engine.commands import IssueTransferCommand
from game.ui.screens.transfer_controller import ConfirmResult, TransferController
from game.ui.screens.transfer_view_model import TransferViewModel


def _controller() -> tuple[TransferController, MagicMock, TransferViewModel]:
    facade = MagicMock()
    view_model = TransferViewModel()
    return TransferController(facade, view_model), facade, view_model


def test_collect_sources_includes_source_fleet_when_facade_omits_it() -> None:
    controller, facade, _view_model = _controller()
    source_fleet = SimpleNamespace(
        id=7,
        name="Detached Fleet",
        location=(1, 2),
        orders=[],
    )
    facade.get_fleets_at_hex.return_value = []
    facade.get_planets_at_hex.return_value = []

    sources = controller.collect_sources_and_targets(source_fleet, (1, 2))

    assert sources == [{"label": "Detached Fleet", "type": "fleet", "id": 7}]


def test_collect_sources_checks_projected_position_when_primary_hex_has_no_planets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    controller, facade, _view_model = _controller()
    source_fleet = SimpleNamespace(id=7, name="Transport")
    colony = SimpleNamespace(planet_id=3, name="Alpha", owner_id=1)
    facade.get_fleets_at_hex.return_value = []
    facade.get_planets_at_hex.side_effect = [[], [colony]]
    monkeypatch.setattr(
        "game.strategy.services.cargo_transfer_service.project_fleet_position",
        lambda fleet: (9, 9),
    )

    sources = controller.collect_sources_and_targets(source_fleet, (1, 2))

    assert sources[-1] == {"label": "Colony: Alpha", "type": "colony", "id": 3}
    assert facade.get_planets_at_hex.call_args_list[1].args == ((9, 9),)


def test_discover_pod_designs_returns_sorted_unique_drop_pod_names(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    controller, _facade, _view_model = _controller()
    scene = SimpleNamespace(
        session=SimpleNamespace(save_path="save-a", active_empire=SimpleNamespace(id=4))
    )

    class _Library:
        def __init__(self, save_path: str, empire_id: int) -> None:
            assert save_path == "save-a"
            assert empire_id == 4

        def filter_designs(self, *, vehicle_type: str) -> list[SimpleNamespace]:
            assert vehicle_type == "Drop Pod"
            return [
                SimpleNamespace(name="Zulu Pod"),
                SimpleNamespace(name="Alpha Pod"),
                SimpleNamespace(name="Alpha Pod"),
            ]

    monkeypatch.setattr("game.strategy.systems.design_library.DesignLibrary", _Library)

    assert controller.discover_pod_designs(scene) == ["Alpha Pod", "Zulu Pod"]


def test_discover_pod_designs_falls_back_to_empty_list_on_library_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    controller, _facade, _view_model = _controller()
    scene = SimpleNamespace(session=SimpleNamespace(save_path="save-a", active_empire=None))

    class _BrokenLibrary:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            raise OSError("missing designs")

    monkeypatch.setattr(
        "game.strategy.systems.design_library.DesignLibrary",
        _BrokenLibrary,
    )

    assert controller.discover_pod_designs(scene) == []


@pytest.mark.parametrize(
    ("cargo_key", "expected"),
    [
        ("drop_pod:Marine Pod", ("drop_pod", "Marine Pod")),
        ("passengers", ("passengers", None)),
        ("passengers_human", ("passengers", "human")),
        ("metals", ("metals", None)),
        # QA Obs 5 (2026-05-16): vehicle:<design_id> rows emitted by
        # TransferViewModel._build_pod_rows must split into the bare
        # "vehicle" cargo_type the order-handler dispatch and validator
        # recognise, with the design_id surfaced as species_id.
        ("vehicle:qs_mine", ("vehicle", "qs_mine")),
        ("vehicle:qs_fighter", ("vehicle", "qs_fighter")),
        ("vehicle:qs_satellite", ("vehicle", "qs_satellite")),
    ],
)
def test_parse_cargo_key(cargo_key: str, expected: tuple[str, str | None]) -> None:
    assert TransferController._parse_cargo_key(cargo_key) == expected


def test_fetch_dto_routes_fleet_and_planet_entries() -> None:
    controller, facade, _view_model = _controller()
    fleet = object()
    planet = object()
    facade.get_fleet.return_value = fleet
    facade.get_planet.return_value = planet

    assert controller.fetch_dto({"type": "fleet", "id": 5}) is fleet
    assert controller.fetch_dto({"type": "colony", "id": 6}) is planet
    assert controller.fetch_dto(None) is None


def test_confirm_pending_aborts_when_endpoints_are_not_fleet_backed() -> None:
    controller, facade, view_model = _controller()
    view_model.current_source = {"type": "colony", "id": 1}
    view_model.current_target = {"type": "planet", "id": 2}
    view_model.pending_transfers = {"metals": 50}

    result = controller.confirm_pending()

    assert result == ConfirmResult(orders_issued=0, aborted_for_correction=True)
    facade.handle_command.assert_not_called()


def test_confirm_pending_carries_rejection_message_when_all_rejected() -> None:
    """QA Obs 5 follow-up (2026-05-16): when every IssueTransferCommand
    is rejected by the facade (e.g. INVALID_CARGO_TYPE for a missing
    parse branch), the dialog needs to surface the rejection so the user
    sees why "Confirm All" appeared to do nothing. The controller
    forwards the first rejection's message on the ConfirmResult."""
    controller, facade, view_model = _controller()
    view_model.current_source = {"type": "fleet", "id": 10}
    view_model.current_target = {"type": "colony", "id": 2}
    view_model.pending_transfers = {"vehicle:qs_mine": TransferViewModel.MAX_LOAD}
    facade.handle_command.return_value = SimpleNamespace(
        is_valid=False,
        message="Invalid cargo type 'vehicle:qs_mine'.",
    )

    result = controller.confirm_pending()

    assert result.orders_issued == 0
    assert result.aborted_for_correction is True
    assert result.rejection_message == "Invalid cargo type 'vehicle:qs_mine'."


def test_confirm_pending_no_rejection_message_when_some_accepted() -> None:
    """Mixed-accept case: rejection_message stays None when at least
    one order was accepted — the user got partial success and doesn't
    need the failure popup."""
    controller, facade, view_model = _controller()
    view_model.current_source = {"type": "fleet", "id": 10}
    view_model.current_target = {"type": "fleet", "id": 20}
    view_model.pending_transfers = {
        "metals": 25,
        "vehicle:qs_mine": TransferViewModel.MAX_LOAD,
    }
    facade.handle_command.side_effect = [
        SimpleNamespace(is_valid=True),
        SimpleNamespace(is_valid=False, message="rejected"),
    ]

    result = controller.confirm_pending()

    assert result.orders_issued == 1
    assert result.aborted_for_correction is False
    assert result.rejection_message is None


def test_confirm_pending_emits_commands_and_counts_only_accepted_results() -> None:
    controller, facade, view_model = _controller()
    view_model.current_source = {"type": "fleet", "id": 10}
    view_model.current_target = {"type": "fleet", "id": 20}
    view_model.pending_transfers = {
        "metals": 25,
        "drop_pod:Marine Pod": TransferViewModel.MAX_DROP,
        "fuel": 0,
    }
    facade.handle_command.side_effect = [
        SimpleNamespace(is_valid=True),
        SimpleNamespace(is_valid=False, message="rejected"),
    ]

    result = controller.confirm_pending()

    assert result == ConfirmResult(orders_issued=1, aborted_for_correction=False)
    assert facade.handle_command.call_count == 2

    first_command = facade.handle_command.call_args_list[0].args[0]
    assert isinstance(first_command, IssueTransferCommand)
    assert first_command.fleet_id == 10
    assert first_command.planet_id is None
    assert first_command.target_fleet_id == 20
    assert first_command.cargo_type == "metals"
    assert first_command.direction == "load"
    assert first_command.amount == 25

    second_command = facade.handle_command.call_args_list[1].args[0]
    assert second_command.cargo_type == "drop_pod"
    assert second_command.species_id == "Marine Pod"
    assert second_command.direction == "unload"
    assert second_command.amount == 0

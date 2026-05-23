from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from game.core.input_actions import InputAction
from game.ui.screens import strategy_fleet_command_router as router_module
from game.ui.screens.strategy_fleet_command_router import FleetCommandRouter


class _PressedKeys:
    def __init__(self, pressed: set[int] | None = None) -> None:
        self._pressed = pressed or set()

    def __getitem__(self, key: int) -> bool:
        return key in self._pressed


class _WarpCapabilities:
    def __init__(self, can_warp: bool) -> None:
        self._can_warp = can_warp

    def can_use_warp(self) -> bool:
        return self._can_warp


def _make_scene(
    *,
    selected_fleet: object | None = None,
    current_selection: object | None = None,
) -> SimpleNamespace:
    ui = MagicMock()
    ui.current_selection = current_selection
    return SimpleNamespace(
        selected_fleet=selected_fleet,
        ui=ui,
        facade=MagicMock(),
        on_colonize_click=MagicMock(),
        on_fleet_build_click=MagicMock(),
        on_ui_selection=MagicMock(),
        _superweapons=MagicMock(),
        _edit_move_ghost_hex="ghost",
        _edit_move_order_index=2,
        _edit_move_fleet=selected_fleet,
    )


def _make_router(
    *,
    selected_fleet: object | None = None,
    current_selection: object | None = None,
    input_mode: str = "SELECT",
) -> tuple[FleetCommandRouter, SimpleNamespace, SimpleNamespace]:
    scene = _make_scene(
        selected_fleet=selected_fleet,
        current_selection=current_selection,
    )
    handler = SimpleNamespace(scene=scene, input_mode=input_mode)
    return FleetCommandRouter(handler), handler, scene


@pytest.mark.parametrize(
    ("action", "expected_mode"),
    [
        (InputAction.FLEET_MOVE, "MOVE"),
        (InputAction.FLEET_JOIN, "JOIN"),
        (InputAction.FLEET_COLONIZE, "COLONIZE_TARGET"),
        (InputAction.FLEET_TRANSFER, "TRANSFER"),
        (InputAction.FLEET_DROP_CARGO, "DROP_CARGO"),
        (InputAction.FLEET_LOAD_CARGO, "LOAD_CARGO"),
        (InputAction.FLEET_WARP, "WARP_TARGET"),
    ],
)
def test_fleet_action_enters_target_mode_when_fleet_selected(
    action: InputAction,
    expected_mode: str,
) -> None:
    router, handler, scene = _make_router(selected_fleet=object())

    handled = router.handle_fleet_action(action)

    assert handled is True
    assert handler.input_mode == expected_mode
    if action == InputAction.FLEET_COLONIZE:
        scene.on_colonize_click.assert_called_once_with()
    else:
        scene.on_colonize_click.assert_not_called()


@pytest.mark.parametrize(
    "action",
    [
        InputAction.FLEET_MOVE,
        InputAction.FLEET_JOIN,
        InputAction.FLEET_COLONIZE,
        InputAction.FLEET_TRANSFER,
        InputAction.FLEET_DROP_CARGO,
        InputAction.FLEET_LOAD_CARGO,
        InputAction.FLEET_WARP,
    ],
)
def test_fleet_action_without_selected_fleet_is_handled_without_mode_change(
    action: InputAction,
) -> None:
    router, handler, scene = _make_router(input_mode="SELECT")

    handled = router.handle_fleet_action(action)

    assert handled is True
    assert handler.input_mode == "SELECT"
    scene.on_colonize_click.assert_not_called()


def test_fleet_warp_action_with_non_warp_fleet_stays_in_select_mode() -> None:
    fleet = SimpleNamespace(capabilities=_WarpCapabilities(can_warp=False))
    router, handler, _scene = _make_router(selected_fleet=fleet)

    handled = router.handle_fleet_action(InputAction.FLEET_WARP)

    assert handled is True
    assert handler.input_mode == "SELECT"


def test_fleet_cancel_from_edit_move_clears_edit_ghost_state() -> None:
    fleet = object()
    router, handler, scene = _make_router(
        selected_fleet=fleet,
        input_mode="EDIT_MOVE",
    )

    handled = router.handle_fleet_action(InputAction.FLEET_CANCEL_MODE)

    assert handled is True
    assert handler.input_mode == "SELECT"
    assert scene._edit_move_ghost_hex is None
    assert scene._edit_move_order_index is None
    assert scene._edit_move_fleet is None


@pytest.mark.parametrize(
    "mode",
    [
        "MOVE",
        "COLONIZE_TARGET",
        "JOIN",
        "TRANSFER",
        "DROP_CARGO",
        "LOAD_CARGO",
        "WARP_TARGET",
        "IMPLODE_PLANET_TARGET",
        "STELLERATE_STAR_TARGET",
        "OPEN_WARP_TARGET",
        "CLOSE_WARP_TARGET",
        "DYSON_SPHERE_TARGET",
    ],
)
def test_fleet_cancel_from_target_mode_returns_to_select(mode: str) -> None:
    router, handler, _scene = _make_router(input_mode=mode)

    handled = router.handle_fleet_action(InputAction.FLEET_CANCEL_MODE)

    assert handled is True
    assert handler.input_mode == "SELECT"


def test_non_fleet_action_returns_false() -> None:
    router, _handler, scene = _make_router(selected_fleet=object())

    handled = router.handle_fleet_action(InputAction.STRATEGY_NEXT_TURN)

    assert handled is False
    scene.on_colonize_click.assert_not_called()


@pytest.mark.parametrize(
    ("action", "expected_mode"),
    [
        (InputAction.FLEET_IMPLODE_PLANET, "IMPLODE_PLANET_TARGET"),
        (InputAction.FLEET_STELLERATE_STAR, "STELLERATE_STAR_TARGET"),
        (InputAction.FLEET_OPEN_WARP_POINT, "OPEN_WARP_TARGET"),
        (InputAction.FLEET_CLOSE_WARP_POINT, "CLOSE_WARP_TARGET"),
        (InputAction.FLEET_CREATE_DYSON_SPHERE, "DYSON_SPHERE_TARGET"),
    ],
)
def test_superweapon_target_action_enters_target_mode_when_fleet_selected(
    action: InputAction,
    expected_mode: str,
) -> None:
    router, handler, _scene = _make_router(selected_fleet=object())

    handled = router.handle_superweapon_action(action)

    assert handled is True
    assert handler.input_mode == expected_mode


@pytest.mark.parametrize(
    "action",
    [
        InputAction.FLEET_IMPLODE_PLANET,
        InputAction.FLEET_STELLERATE_STAR,
        InputAction.FLEET_OPEN_WARP_POINT,
        InputAction.FLEET_CLOSE_WARP_POINT,
        InputAction.FLEET_CREATE_DYSON_SPHERE,
        InputAction.FLEET_SELF_DESTRUCT,
    ],
)
def test_superweapon_action_without_selected_fleet_is_no_op(action: InputAction) -> None:
    router, handler, scene = _make_router(input_mode="SELECT")

    handled = router.handle_superweapon_action(action)

    assert handled is True
    assert handler.input_mode == "SELECT"
    scene._superweapons.handle_self_destruct.assert_not_called()


def test_superweapon_self_destruct_delegates_to_superweapon_handler() -> None:
    fleet = object()
    router, handler, scene = _make_router(selected_fleet=fleet, input_mode="SELECT")

    handled = router.handle_superweapon_action(InputAction.FLEET_SELF_DESTRUCT)

    assert handled is True
    assert handler.input_mode == "SELECT"
    scene._superweapons.handle_self_destruct.assert_called_once_with(fleet)


def test_non_superweapon_action_returns_false() -> None:
    router, _handler, scene = _make_router(selected_fleet=object())

    handled = router.handle_superweapon_action(InputAction.STRATEGY_NEXT_TURN)

    assert handled is False
    scene._superweapons.handle_self_destruct.assert_not_called()


def test_detail_orders_action_opens_fleet_orders_when_fleet_selected() -> None:
    fleet = object()
    router, _handler, scene = _make_router(selected_fleet=fleet)

    handled = router.handle_detail_action(InputAction.DETAIL_PANEL_ORDERS)

    assert handled is True
    scene.ui.open_orders_window.assert_called_once_with(fleet)


def test_detail_orders_action_opens_planet_orders_when_planet_selected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    planet = object()
    monkeypatch.setattr(router_module, "is_planet", lambda value: value is planet)
    router, _handler, scene = _make_router(current_selection=planet)

    handled = router.handle_detail_action(InputAction.DETAIL_PANEL_ORDERS)

    assert handled is True
    scene.ui.open_orders_window.assert_called_once_with(planet, entity_type="planet")


@pytest.mark.parametrize(
    "action",
    [
        InputAction.DETAIL_PANEL_PLANET_ORDERS,
        InputAction.PLANET_ABILITIES_WINDOW,
    ],
)
def test_planet_detail_actions_ignore_non_planet_selection(
    action: InputAction,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    selected = object()
    monkeypatch.setattr(router_module, "is_planet", lambda value: False)
    router, _handler, scene = _make_router(current_selection=selected)

    handled = router.handle_detail_action(action)

    assert handled is True
    scene.ui.open_orders_window.assert_not_called()
    scene.ui.open_planet_abilities_window.assert_not_called()


def test_dedicated_planet_orders_action_opens_planet_orders(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    planet = object()
    monkeypatch.setattr(router_module, "is_planet", lambda value: value is planet)
    router, _handler, scene = _make_router(current_selection=planet)

    handled = router.handle_detail_action(InputAction.DETAIL_PANEL_PLANET_ORDERS)

    assert handled is True
    scene.ui.open_orders_window.assert_called_once_with(planet, entity_type="planet")


def test_planet_abilities_action_opens_planet_abilities_window(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    planet = object()
    monkeypatch.setattr(router_module, "is_planet", lambda value: value is planet)
    router, _handler, scene = _make_router(current_selection=planet)

    handled = router.handle_detail_action(InputAction.PLANET_ABILITIES_WINDOW)

    assert handled is True
    scene.ui.open_planet_abilities_window.assert_called_once_with(planet)


def test_detail_fleet_report_action_opens_fleet_report_when_fleet_selected() -> None:
    fleet = object()
    router, _handler, scene = _make_router(selected_fleet=fleet)

    handled = router.handle_detail_action(InputAction.DETAIL_PANEL_FLEET_REPORT)

    assert handled is True
    scene.ui.open_fleet_report_window.assert_called_once_with(fleet)


def test_detail_build_action_delegates_to_scene_when_fleet_selected() -> None:
    router, _handler, scene = _make_router(selected_fleet=object())

    handled = router.handle_detail_action(InputAction.DETAIL_PANEL_BUILD)

    assert handled is True
    scene.on_fleet_build_click.assert_called_once_with()


@pytest.mark.parametrize(
    ("action", "ability_name"),
    [
        (InputAction.PLANET_SHIELD_TOGGLE, "PlanetaryShield"),
        (InputAction.PLANET_GEOLOGIC_TOGGLE, "GeologicStabilizer"),
        (InputAction.PLANET_STELLAR_TOGGLE, "StellarStabilizer"),
        (InputAction.PLANET_WARP_TOGGLE, "WarpFieldStabilizer"),
    ],
)
def test_planet_toggle_detail_actions_delegate_to_ability_toggle(
    action: InputAction,
    ability_name: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    router, _handler, _scene = _make_router()
    toggle = MagicMock()
    monkeypatch.setattr(router, "_handle_ability_toggle", toggle)

    handled = router.handle_detail_action(action)

    assert handled is True
    toggle.assert_called_once_with(ability_name)


def test_non_detail_action_returns_false() -> None:
    router, _handler, scene = _make_router(selected_fleet=object())

    handled = router.handle_detail_action(InputAction.STRATEGY_NEXT_TURN)

    assert handled is False
    scene.ui.open_orders_window.assert_not_called()
    scene.ui.open_fleet_report_window.assert_not_called()
    scene.on_fleet_build_click.assert_not_called()


def test_ability_toggle_returns_without_planet_selection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    selected = object()
    monkeypatch.setattr(router_module, "is_planet", lambda value: False)
    router, _handler, scene = _make_router(current_selection=selected)

    router._handle_ability_toggle("PlanetaryShield")

    scene.facade.handle_command.assert_not_called()


@pytest.mark.parametrize(
    ("phase", "expected_cmd_class"),
    [
        # PROJ-479 Task 3.26: import real command classes and assert via
        # isinstance instead of comparing `type(command).__name__` (which
        # silently passes on shadowed classes or string typos).
        pytest.param(
            "active",
            "DeactivatePlanetAbilityCommand",
            id="active->deactivate",
        ),
        pytest.param(
            "inactive",
            "ActivatePlanetAbilityCommand",
            id="inactive->activate",
        ),
    ],
)
def test_ability_toggle_issues_order_for_first_operational_facility_component(  # noqa: E501
    phase: str,
    expected_cmd_class: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """PROJ-438 Phase 5: typed planet-ability commands replace the stringly
    ``IssuePlanetOrderCommand(order_type=...)`` path. The router now picks
    ``ActivatePlanetAbilityCommand`` or ``DeactivatePlanetAbilityCommand``
    based on current activation phase."""
    facility = SimpleNamespace(
        instance_id="facility-1",
        is_operational=True,
        design_data={"layers": []},
    )
    facility.get_activation_state = MagicMock(return_value=SimpleNamespace(phase=phase))
    planet = SimpleNamespace(id=42, facilities=[facility])

    class _ActivationPhase:
        ACTIVE = "active"
        ACTIVATING = "activating"

    monkeypatch.setattr(router_module, "is_planet", lambda value: value is planet)
    monkeypatch.setattr(
        "game.core.registry.get_default_registry_provider",
        lambda: SimpleNamespace(get_components=lambda: {"shield": {}}),
    )
    monkeypatch.setattr(
        "game.core.patterns.layer_iterator.iter_keyed_components",
        lambda design_data: iter([("CORE:0", "CORE", {"id": "shield"})]),
    )
    monkeypatch.setattr(
        "game.strategy.services.component_abilities.extract_abilities_from_component",
        lambda comp, registry: {"PlanetaryShield": {"activation_time": 1}},
    )
    monkeypatch.setattr(
        "game.strategy.data.component_activation_state.ActivationPhase",
        _ActivationPhase,
    )

    router, _handler, scene = _make_router(current_selection=planet)
    scene.facade.handle_command.return_value = SimpleNamespace(is_valid=True)

    router._handle_ability_toggle("PlanetaryShield")

    scene.facade.handle_command.assert_called_once()
    command = scene.facade.handle_command.call_args.args[0]
    # PROJ-479 Task 3.26: real class import for isinstance check
    from game.strategy.engine import commands as _cmd_mod
    expected_cls = getattr(_cmd_mod, expected_cmd_class)
    assert isinstance(command, expected_cls)
    assert command.planet_id == 42
    assert command.facility_instance_id == "facility-1"
    assert command.ability_name == "PlanetaryShield"
    assert command.component_key == "CORE:0"
    facility.get_activation_state.assert_called_once_with("CORE:0")


def test_ability_toggle_skips_missing_toggleable_ability(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facility = SimpleNamespace(
        instance_id="facility-1",
        is_operational=True,
        design_data={"layers": []},
    )
    planet = SimpleNamespace(id=42, facilities=[facility])

    monkeypatch.setattr(router_module, "is_planet", lambda value: value is planet)
    monkeypatch.setattr(
        "game.core.registry.get_default_registry_provider",
        lambda: SimpleNamespace(get_components=lambda: {"shield": {}}),
    )
    monkeypatch.setattr(
        "game.core.patterns.layer_iterator.iter_keyed_components",
        lambda design_data: iter([("CORE:0", "CORE", {"id": "shield"})]),
    )
    monkeypatch.setattr(
        "game.strategy.services.component_abilities.extract_abilities_from_component",
        lambda comp, registry: {"PlanetaryShield": True},
    )

    router, _handler, scene = _make_router(current_selection=planet)

    router._handle_ability_toggle("PlanetaryShield")

    scene.facade.handle_command.assert_not_called()


def test_finish_move_action_clears_mode_when_shift_not_pressed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fleet = object()
    router, handler, scene = _make_router(selected_fleet=fleet, input_mode="MOVE")
    monkeypatch.setattr(
        router_module.pygame.key,
        "get_pressed",
        lambda: _PressedKeys(),
    )

    router.finish_move_action(fleet)

    assert handler.input_mode == "SELECT"
    scene.on_ui_selection.assert_called_once_with(fleet)


def test_finish_move_action_keeps_mode_when_shift_pressed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fleet = object()
    router, handler, scene = _make_router(selected_fleet=fleet, input_mode="MOVE")
    monkeypatch.setattr(
        router_module.pygame.key,
        "get_pressed",
        lambda: _PressedKeys({router_module.pygame.K_LSHIFT}),
    )

    router.finish_move_action(fleet)

    assert handler.input_mode == "MOVE"
    scene.on_ui_selection.assert_called_once_with(fleet)

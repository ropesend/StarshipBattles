"""Contract test for StrategyWindowManager public API (PROJ-309 sub-phase 3.10).

Locks the public surface of `game.ui.screens.strategy_window_manager` so the
decomposition into the `strategy_windows/` subpackage cannot accidentally drop
a method or slot that production code depends on.

Pinned contract:

1. The class `StrategyWindowManager` is importable from
   `game.ui.screens.strategy_window_manager`.

2. Every public `open_*` / `prompt_*` / `close_*` / `show_*` /
   `handle_*` / `process_*` method that callers use today is callable on
   the instance, with the documented signature.

3. The 14 window-slot attributes that `StrategyEventRouter.has_modal_open()`
   reads are present on the instance and initialized to `None` —
   PLUS `planet_abilities_window` (PROJ-309 sub-phase 3.10 latent-bug fix:
   originally created on first open without a `None`-init and absent from
   `has_modal_open`'s 14-slot scan; the decomposition initializes it like
   the others, raising the slot count to 15).

4. The `ui_callbacks` dict and the two confirmation-dialog cache attributes
   are initialized as documented.
"""
from __future__ import annotations

import inspect
from unittest.mock import Mock

import pytest


# ---------------------------------------------------------------------------
# Constants — the locked-in public contract
# ---------------------------------------------------------------------------

# Window-slot attributes read by StrategyEventRouter.has_modal_open() and
# StrategyEventRouter._is_blocking_ui_element_at(). The original 14 plus
# `planet_abilities_window` (latent-bug fix — see module docstring).
EXPECTED_WINDOW_SLOTS: frozenset[str] = frozenset({
    "planet_list_window",
    "star_list_window",
    "build_queue_list_window",
    "empire_build_queue_window",
    "event_log_window",
    "fleet_orders_window",
    "fleet_report_window",
    "transfer_dialog",
    "empire_panel_window",
    "settings_window",
    "move_choice_window",
    "cargo_quick_dialog",
    "planet_selection_window",
    "system_selection_window",
    "fleet_selection_window",
    "planet_abilities_window",  # PROJ-309 3.10: now None-initialized
})

# Public methods the production code calls on StrategyWindowManager.
EXPECTED_PUBLIC_METHODS: frozenset[str] = frozenset({
    "handle_resize",
    "open_planet_list",
    "open_star_list",
    "open_build_queue_list",
    "open_empire_build_queue_window",
    "close_empire_build_queue_window",
    "open_event_log",
    "open_event_log_with_events",
    "open_empire_panel",
    "open_settings",
    "open_orders_window",
    "open_fleet_report_window",
    "open_transfer_dialog",
    "open_cargo_quick_dialog",
    "prompt_planet_selection",
    "open_planet_abilities_window",
    "open_system_selection",
    "prompt_fleet_selection",
    "prompt_move_choice",
    "process_ui_callbacks",
    "show_confirmation_dialog",
    "process_confirmation_event",
    "show_ship_picker",
})


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_scene():
    scene = Mock()
    scene.current_empire = Mock()
    scene.galaxy = Mock()
    scene.facade = Mock()
    scene.facade.get_all_events = Mock(return_value=[])
    scene.session = Mock()
    scene.session.empires = []
    scene.session.registries = Mock()
    scene.on_navigate_to_hex_build = Mock()
    return scene


@pytest.fixture
def mock_manager():
    return Mock()


@pytest.fixture
def window_manager(mock_scene, mock_manager):
    from game.ui.screens.strategy_window_manager import StrategyWindowManager
    return StrategyWindowManager(
        scene=mock_scene,
        manager=mock_manager,
        width=2560,
        height=1600,
        input_mapper=None,
        asset_resolver=None,
    )


# ---------------------------------------------------------------------------
# Contract tests
# ---------------------------------------------------------------------------

class TestImportPath:
    """The class must remain importable from its current module path."""

    def test_class_importable_from_strategy_window_manager(self) -> None:
        from game.ui.screens.strategy_window_manager import StrategyWindowManager
        assert inspect.isclass(StrategyWindowManager)
        assert StrategyWindowManager.__name__ == "StrategyWindowManager"


class TestWindowSlots:
    """The 15 window-slot attributes must exist and be `None` after __init__."""

    def test_all_slots_present(self, window_manager) -> None:
        for slot in EXPECTED_WINDOW_SLOTS:
            assert hasattr(window_manager, slot), (
                f"Missing window slot: {slot}"
            )

    def test_all_slots_initialized_to_none(self, window_manager) -> None:
        for slot in EXPECTED_WINDOW_SLOTS:
            assert getattr(window_manager, slot) is None, (
                f"Window slot {slot} should be None after __init__, "
                f"got {getattr(window_manager, slot)!r}"
            )

    def test_slots_are_writable(self, window_manager) -> None:
        """Each slot must accept assignment — registrars set them post-construction."""
        sentinel = object()
        for slot in EXPECTED_WINDOW_SLOTS:
            setattr(window_manager, slot, sentinel)
            assert getattr(window_manager, slot) is sentinel
            setattr(window_manager, slot, None)


class TestPublicMethods:
    """Every public method callers use must remain on the class."""

    def test_methods_present_and_callable(self, window_manager) -> None:
        for name in EXPECTED_PUBLIC_METHODS:
            method = getattr(window_manager, name, None)
            assert method is not None, f"Missing public method: {name}"
            assert callable(method), f"Attribute {name} is not callable"


class TestUICallbackState:
    """ui_callbacks dict and confirmation-dialog cache initial state."""

    def test_ui_callbacks_is_empty_dict(self, window_manager) -> None:
        assert window_manager.ui_callbacks == {}

    def test_confirmation_dialog_state_initialized(self, window_manager) -> None:
        assert window_manager._pending_confirmation_dialog is None
        assert window_manager._pending_confirmation_callback is None


class TestConstructorSignature:
    """The __init__ signature must accept the documented arguments."""

    def test_can_construct_with_minimal_args(self, mock_scene, mock_manager) -> None:
        from game.ui.screens.strategy_window_manager import StrategyWindowManager
        wm = StrategyWindowManager(mock_scene, mock_manager, 1920, 1080)
        assert wm.scene is mock_scene
        assert wm.manager is mock_manager
        assert wm.width == 1920
        assert wm.height == 1080

    def test_can_construct_with_input_mapper_and_asset_resolver(
        self, mock_scene, mock_manager
    ) -> None:
        from game.ui.screens.strategy_window_manager import StrategyWindowManager
        mapper = Mock()
        resolver = Mock()
        wm = StrategyWindowManager(
            scene=mock_scene,
            manager=mock_manager,
            width=2560,
            height=1600,
            input_mapper=mapper,
            asset_resolver=resolver,
        )
        # Internal storage names are documented by the existing
        # test_strategy_window_manager.py fixture's keyword usage; the
        # behavioral guarantee is that input_mapper threads to OrdersWindow
        # and asset_resolver threads to PlanetListWindow. This is exercised
        # in test_sub_window_hotkeys.py and the existing module tests; we
        # only assert here that the constructor accepts both kwargs.
        assert wm is not None


class TestEventRouterContract:
    """`StrategyEventRouter.has_modal_open()` reads the slots directly.

    This test guards the read-side contract: each slot it reads must be
    declared by the composer. If a slot is renamed or removed, this test
    fails before integration.
    """

    def test_has_modal_open_finds_no_modals_when_all_slots_none(
        self, window_manager, mock_scene, mock_manager
    ) -> None:
        from game.ui.screens.strategy_event_router import StrategyEventRouter

        ui = Mock()
        ui.window_manager = window_manager
        ui.menu_panel = None
        ui.scene = mock_scene
        ui.scene.build_queue_screen = None

        router = StrategyEventRouter(ui)
        assert router.has_modal_open() is False

    @pytest.mark.parametrize(
        "slot",
        sorted(EXPECTED_WINDOW_SLOTS - {"settings_window"}),
        # `settings_window` is intentionally NOT scanned by has_modal_open
        # today (the SettingsWindow has its own modal-blocking via the
        # settings flow). All other slots flip has_modal_open to True.
    )
    def test_has_modal_open_returns_true_when_slot_set(
        self, window_manager, mock_scene, slot
    ) -> None:
        from game.ui.screens.strategy_event_router import StrategyEventRouter

        ui = Mock()
        ui.window_manager = window_manager
        ui.menu_panel = None
        ui.scene = mock_scene
        ui.scene.build_queue_screen = None

        setattr(window_manager, slot, Mock())

        router = StrategyEventRouter(ui)
        assert router.has_modal_open() is True, (
            f"has_modal_open() did not return True with {slot} set; "
            f"the slot may have been dropped from the modal-detection scan."
        )

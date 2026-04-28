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


# Slots that StrategyEventRouter._handle_window_close clears directly when
# pygame_gui dispatches UI_WINDOW_CLOSE. Any other slot must clear via a
# registrar-registered on_close_callback fired from the window's kill().
SLOTS_CLEARED_BY_HANDLE_WINDOW_CLOSE: frozenset[str] = frozenset({
    "fleet_orders_window",
    "star_list_window",
    "fleet_report_window",
    "transfer_dialog",
    "build_queue_list_window",
    "empire_build_queue_window",
    "event_log_window",
    "empire_panel_window",
    "move_choice_window",
    "cargo_quick_dialog",
    "planet_selection_window",
    "system_selection_window",
    "fleet_selection_window",
})


class TestModalSlotCleanupContract:
    """Every slot scanned by has_modal_open() must clear to None on close.

    Regression guard for BUG-121 — `planet_abilities_window` was added to
    has_modal_open()'s scan in PROJ-309 sub-phase 3.10 but the close-side
    cleanup was never wired up, so the slot pointed at a dead UIWindow
    forever after the user closed it once. has_modal_open() returned True
    permanently and strategy mouse-wheel zoom died for the rest of the
    session.

    For every modal-tracked slot (the 15 slots minus settings_window which
    is intentionally exempt), confirm there is SOME cleanup path that
    returns the slot to None when the underlying window closes.
    """

    @pytest.mark.parametrize(
        "slot",
        sorted(EXPECTED_WINDOW_SLOTS - {"settings_window"}),
    )
    def test_modal_slot_clears_after_window_kill(
        self, window_manager, slot, mock_scene
    ) -> None:
        """For each modal-tracked slot, simulate close and assert slot is None.

        Two cleanup pathways are recognized:
        1. ``StrategyEventRouter._handle_window_close`` reset
           (the elif chain) — used by 13 of 15 slots.
        2. Registrar ``on_close_callback`` fired from the window's
           ``kill()`` override — used by ``planet_list_window``
           (post-fix: also ``planet_abilities_window``).

        If neither pathway clears the slot, the slot will leak forever
        once the user closes the corresponding window.
        """
        import pygame_gui
        from game.ui.screens.strategy_event_router import StrategyEventRouter

        # Place a sentinel window in the slot.
        sentinel_window = Mock()
        setattr(window_manager, slot, sentinel_window)

        # Path 1: try _handle_window_close.
        if slot in SLOTS_CLEARED_BY_HANDLE_WINDOW_CLOSE:
            ui = Mock()
            ui.window_manager = window_manager
            ui.scene = mock_scene
            router = StrategyEventRouter(ui)
            event = Mock()
            event.type = pygame_gui.UI_WINDOW_CLOSE
            event.ui_element = sentinel_window
            router._handle_window_close(event)
            assert getattr(window_manager, slot) is None, (
                f"Slot {slot} should clear via _handle_window_close but did not."
            )
            return

        # Path 2: this slot must rely on a registrar-registered
        # on_close_callback. The contract: the registrar's open() call
        # must pass `on_close_callback=...` so the window's kill() can
        # reset the slot. Inspect each registrar to find the slot it
        # owns.
        registrar_slot_map = {
            "planet_list_window": (
                "game.ui.screens.strategy_windows.list_windows",
                "PlanetListRegistrar",
            ),
            "planet_abilities_window": (
                "game.ui.screens.strategy_windows.planet_abilities_ctrl",
                "PlanetAbilitiesRegistrar",
            ),
        }
        assert slot in registrar_slot_map, (
            f"Slot {slot} is not cleared by _handle_window_close AND has no "
            f"registered registrar in this guard test. Either add a "
            f"_handle_window_close branch (and update "
            f"SLOTS_CLEARED_BY_HANDLE_WINDOW_CLOSE) OR add a registrar "
            f"on_close_callback (and add the registrar to this map). "
            f"Without a cleanup path, the slot will leak — see BUG-121."
        )

        from importlib import import_module
        import inspect as _inspect
        module_name, registrar_cls_name = registrar_slot_map[slot]
        module = import_module(module_name)
        registrar_cls = getattr(module, registrar_cls_name)

        # The registrar must define an `_on_closed` method that resets the
        # slot to None on the composer it holds. This is the contract that
        # PlanetListRegistrar follows; the same contract is what BUG-121's
        # fix establishes for PlanetAbilitiesRegistrar.
        assert hasattr(registrar_cls, "_on_closed"), (
            f"{registrar_cls_name} must define _on_closed() to clear "
            f"composer.{slot} (BUG-121 cleanup contract)."
        )

        # Verify the registrar's open() call wires the callback. We can't
        # call open() without a real pygame display, but we CAN inspect
        # the source for the on_close_callback kwarg.
        open_src = _inspect.getsource(registrar_cls.open)
        assert "on_close_callback" in open_src, (
            f"{registrar_cls_name}.open() must pass `on_close_callback=...` "
            f"to the window constructor so the slot can clear on kill "
            f"(BUG-121)."
        )

        # Verify _on_closed actually resets the slot.
        composer = Mock()
        setattr(composer, slot, sentinel_window)
        registrar = registrar_cls(composer)
        registrar._on_closed()
        assert getattr(composer, slot) is None, (
            f"{registrar_cls_name}._on_closed() must reset composer.{slot} "
            f"to None (BUG-121)."
        )

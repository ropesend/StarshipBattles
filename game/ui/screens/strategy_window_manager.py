"""Window-lifecycle composition root for the StrategyUI (PROJ-86 / PROJ-309).

This module hosts ``StrategyWindowManager``, the orchestrator that owns the
window-slot attributes and delegates each ``open_*`` call to a registrar in
``game.ui.screens.strategy_windows``. Production code imports the class
from this module path; that import path MUST stay stable.

PROJ-309 sub-phase 3.10: split into a 13-module subpackage. Public API and
all 15 window-slot attributes (the original 14 plus ``planet_abilities_window``
— see latent-bug fix below) remain on this composer.

**Latent-bug fix (PROJ-309 3.10):** ``planet_abilities_window`` was
historically created on first open without a ``None``-init in ``__init__``,
and ``StrategyEventRouter.has_modal_open()`` did not include it in the
modal-detection scan. The decomposition initializes the slot here AND
``StrategyEventRouter.has_modal_open()`` / ``_is_blocking_ui_element_at`` now
scan it like the other modals.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Iterator, List, Optional

import pygame_gui

from pygame_gui.elements import UIWindow

from game.ui.screens.strategy_windows.build_queue_windows import (
    BuildQueueListRegistrar,
    EmpireBuildQueueRegistrar,
)
from game.ui.screens.strategy_windows.dispatch import (
    ConfirmationDialogController,
    UICallbackDispatcher,
)
from game.ui.screens.strategy_windows.empire_panel_ctrl import (
    EmpirePanelRegistrar,
    SettingsRegistrar,
)
from game.ui.screens.strategy_windows.event_log_window_ctrl import (
    EventLogRegistrar,
)
from game.ui.screens.strategy_windows.fleet_report_ctrl import (
    FleetReportRegistrar,
)
from game.ui.screens.strategy_windows.list_windows import (
    PlanetListRegistrar,
    StarListRegistrar,
)
from game.ui.screens.strategy_windows.move_choice_dialog import MoveChoiceDialog
from game.ui.screens.strategy_windows.orders_window_ctrl import OrdersRegistrar
from game.ui.screens.strategy_windows.planet_abilities_ctrl import (
    PlanetAbilitiesRegistrar,
)
from game.ui.screens.strategy_windows.selection_prompts import (
    SelectionPromptRegistrar,
)
from game.ui.screens.strategy_windows.ship_picker import ShipPickerStub
from game.ui.screens.strategy_windows.transfer_dialogs import (
    TransferDialogRegistrar,
)

if TYPE_CHECKING:
    from game.ui.services.input_mapper import InputMapper


class StrategyWindowManager:
    """Manages modal window lifecycle for the strategy screen.

    Composition root for the per-window-family registrars. Owns the 15
    window-slot attributes that ``StrategyEventRouter`` reads directly for
    modal detection and click-blocking.

    Attributes:
        planet_list_window: Active planet list window or None.
        star_list_window: Active star list window (PROJ-231) or None.
        build_queue_list_window: Active build queue list window or None.
        empire_build_queue_window: Active empire build queue window or None.
        event_log_window: Active event log window or None.
        fleet_orders_window: Active fleet/planet orders window or None.
        fleet_report_window: Active fleet report window or None.
        transfer_dialog: Active transfer dialog or None.
        empire_panel_window: Active empire panel window or None.
        settings_window: Active settings window or None.
        move_choice_window: Active move-choice dialog or None.
        cargo_quick_dialog: Active cargo quick dialog or None.
        planet_selection_window: Active planet selection prompt or None.
        system_selection_window: Active system selection prompt or None.
        fleet_selection_window: Active fleet selection prompt or None.
        planet_abilities_window: Active planet abilities window or None
            (PROJ-309 3.10: now ``None``-initialized; previously created on
            first open without a slot init).
        ui_callbacks: Dict mapping buttons to callbacks for prompt dialogs.
    """

    def __init__(
        self,
        scene,
        manager: pygame_gui.UIManager,
        width: int,
        height: int,
        input_mapper: Optional["InputMapper"] = None,
        asset_resolver: Optional[Callable] = None,
    ):
        """Initialize the window manager.

        Args:
            scene: Reference to StrategyScreen for current_empire, galaxy,
                _facade access.
            manager: The pygame_gui UIManager.
            width: Screen width.
            height: Screen height.
            input_mapper: Optional InputMapper for hotkey tooltips.
            asset_resolver: Optional callable for resolving object portraits.
        """
        self.scene = scene
        self.manager = manager
        self.width = width
        self.height = height
        self._mapper = input_mapper
        self._asset_resolver = asset_resolver

        # Window-slot references — all None until the matching registrar
        # opens the window. Read directly by StrategyEventRouter for modal
        # detection (`has_modal_open`) and click blocking
        # (`_is_blocking_ui_element_at`).
        self.planet_list_window = None
        self.star_list_window = None
        self.build_queue_list_window = None
        self.empire_build_queue_window = None
        self.event_log_window = None
        self.fleet_orders_window = None
        self.fleet_report_window = None
        self.transfer_dialog = None
        self.empire_panel_window = None
        self.settings_window = None
        self.move_choice_window = None
        self.cargo_quick_dialog = None
        self.planet_selection_window = None
        self.system_selection_window = None
        self.fleet_selection_window = None
        # PROJ-309 3.10 latent-bug fix: was previously created on first
        # open without a slot init, and missing from has_modal_open's scan.
        self.planet_abilities_window = None

        # PROJ-313: Modal-window live list. Subclasses of
        # ``StrategyModalWindow`` auto-register on ``__init__`` and
        # auto-deregister on ``kill()``. The slot fields above are being
        # phased out; the dual-track router OR-bridges this list with the
        # remaining slot scans during migration.
        self._modals: List[UIWindow] = []

        # Callback map for dynamic prompt buttons. Owned here so registrars
        # can register entries via composer.ui_callbacks[btn] = cb without
        # needing a back-reference to the dispatcher.
        self.ui_callbacks: dict = {}

        # Confirmation dialog state (PROJ-198) — owned here so
        # StrategyEventRouter._is_blocking_ui_element_at can read the
        # dialog directly via getattr(wm, '_pending_confirmation_dialog').
        self._pending_confirmation_dialog = None
        self._pending_confirmation_callback = None

        # Per-window-family registrars + the two small dispatch helpers.
        self._planet_list = PlanetListRegistrar(self)
        self._star_list = StarListRegistrar(self)
        self._build_queue_list = BuildQueueListRegistrar(self)
        self._empire_build_queue = EmpireBuildQueueRegistrar(self)
        self._event_log = EventLogRegistrar(self)
        self._empire_panel = EmpirePanelRegistrar(self)
        self._settings = SettingsRegistrar(self)
        self._orders = OrdersRegistrar(self)
        self._fleet_report = FleetReportRegistrar(self)
        self._transfer = TransferDialogRegistrar(self)
        self._selection = SelectionPromptRegistrar(self)
        self._planet_abilities = PlanetAbilitiesRegistrar(self)
        self._move_choice = MoveChoiceDialog(self)
        self._ui_dispatch = UICallbackDispatcher(self)
        self._confirmation = ConfirmationDialogController(self)
        self._ship_picker = ShipPickerStub()

    def handle_resize(self, width: int, height: int) -> None:
        """Update stored dimensions on resize.

        Args:
            width: New screen width.
            height: New screen height.
        """
        self.width = width
        self.height = height

    # ----------------------------------------------------- PROJ-313 modal API

    def register_modal(self, w: UIWindow) -> None:
        """Register a modal window. Called from ``StrategyModalWindow.__init__``.

        Args:
            w: The modal window instance registering itself.
        """
        self._modals.append(w)

    def unregister_modal(self, w: UIWindow) -> None:
        """Deregister a modal window. Called from ``StrategyModalWindow.kill()``.

        Idempotent — safe to call when the window is not currently
        registered (e.g., after parent-kill cascade orphan reaping).

        Args:
            w: The modal window instance deregistering itself.
        """
        try:
            self._modals.remove(w)
        except ValueError:
            pass

    def iter_live_modals(self) -> Iterator[UIWindow]:
        """Yield every currently-alive modal window.

        Performs an in-place GC walk that drops any dead references
        (e.g., orphans from parent-kill cascades that didn't route
        through ``StrategyModalWindow.kill()``). The list is rewritten
        to contain only live windows; dead refs are reaped before
        yielding.

        Yields:
            Each :class:`UIWindow` that is currently alive in
            ``self._modals``.
        """
        self._modals = [w for w in self._modals if w.alive()]
        yield from self._modals

    # ---------------------------------------------------------------- windows

    def open_planet_list(self) -> None:
        """Open the Planet List Window."""
        self._planet_list.open()

    def open_star_list(self) -> None:
        """Open the Star List Window (PROJ-231)."""
        self._star_list.open()

    def open_build_queue_list(self) -> None:
        """Open the Build Queue List Window (BUG-67)."""
        self._build_queue_list.open()

    def open_empire_build_queue_window(self) -> None:
        """Open the Empire-Wide Build Queue Window (PROJ-76)."""
        self._empire_build_queue.open()

    def close_empire_build_queue_window(self) -> None:
        """Close the empire build queue window if open."""
        self._empire_build_queue.close()

    def open_event_log(self) -> None:
        """Open the Event Log Window showing all events (PROJ-77)."""
        self._event_log.open_all()

    def open_event_log_with_events(self, events: list) -> None:
        """Open the Event Log Window with a specific event list."""
        self._event_log.open_with_events(events)

    def open_empire_panel(self) -> None:
        """Open the Empire Panel Window."""
        self._empire_panel.open()

    def open_settings(self) -> None:
        """Open the Settings Window."""
        self._settings.open()

    def open_orders_window(self, entity, entity_type: str = "fleet") -> None:
        """Open the Orders Window for a fleet or planet (PROJ-238)."""
        self._orders.open(entity, entity_type=entity_type)

    def open_fleet_report_window(self, fleet) -> None:
        """Open the Fleet Report Window."""
        self._fleet_report.open(fleet)

    def open_transfer_dialog(self, source_fleet, hex_coord) -> None:
        """Open the cargo/population transfer dialog (PROJ-68)."""
        self._transfer.open(source_fleet, hex_coord)

    def open_cargo_quick_dialog(self, fleet, hex_coord, direction: str) -> None:
        """Open the quick cargo drop/load dialog (PROJ-100)."""
        self._transfer.open_quick(fleet, hex_coord, direction)

    def prompt_planet_selection(self, planets, on_select: Callable) -> None:
        """Open a modal window to select a planet."""
        self._selection.prompt_planet(planets, on_select)

    def open_planet_abilities_window(self, planet) -> None:
        """Open the planet abilities management window."""
        self._planet_abilities.open(planet)

    def _open_planet_editor(self, editor_type: str, planet) -> None:
        """Dispatch a planet-environment editor request to the event router.

        Retained on the composer for symmetry with the rest of the public
        surface; delegates straight through to the registrar.
        """
        self._planet_abilities.open_editor(editor_type, planet)

    def open_system_selection(
        self, systems, current_system, on_selected: Callable
    ) -> None:
        """Open a modal window to select a star system (PROJ-138)."""
        self._selection.open_system(systems, current_system, on_selected)

    def prompt_fleet_selection(self, fleets, on_select: Callable) -> None:
        """Open a modal window to select a fleet to join (FEAT-08)."""
        self._selection.prompt_fleet(fleets, on_select)

    def prompt_move_choice(
        self,
        fleet,
        target_hex,
        on_move_sector: Callable,
        on_intercept_fleet: Callable,
    ) -> None:
        """Dialog to choose between moving to the sector or intercepting the fleet."""
        self._move_choice.show(fleet, target_hex, on_move_sector, on_intercept_fleet)

    # ------------------------------------------------------------- dispatch

    def process_ui_callbacks(self, event) -> bool:
        """Process button press events for prompt dialogs.

        Returns:
            True if a callback was executed, False otherwise.
        """
        return self._ui_dispatch.process(event)

    def show_confirmation_dialog(
        self, title: str, message: str, on_confirm, is_warning: bool = False
    ) -> None:
        """Show a confirmation dialog for dangerous actions (PROJ-198)."""
        self._confirmation.show(title, message, on_confirm, is_warning=is_warning)

    def process_confirmation_event(self, event) -> bool:
        """Process UI_CONFIRMATION_DIALOG_CONFIRMED events.

        Returns:
            True if a confirmation callback was executed, False otherwise.
        """
        return self._confirmation.process_event(event)

    def show_ship_picker(self, ships, ability_name: str, on_selected) -> None:
        """Show ship picker dialog for multi-select (PROJ-198)."""
        self._ship_picker.show(ships, ability_name, on_selected)

    # ----------------------------------------------------- legacy callbacks
    # The private ``_on_*_closed`` / ``_on_event_log_navigate`` callbacks
    # below preserve the pre-PROJ-309 internal API. ``StrategyEventRouter``
    # invokes ``_on_star_list_closed`` / ``_on_empire_build_queue_closed``
    # / ``_on_event_log_closed`` / ``_on_empire_panel_closed`` from
    # ``_handle_window_close``; the existing direct unit tests also call
    # them. Each forwards to the matching registrar so behavior stays in
    # one place.

    def _on_planet_list_closed(self) -> None:
        self._planet_list._on_closed()

    def _on_star_list_closed(self) -> None:
        self._star_list._on_closed()

    def _on_build_queue_list_closed(self) -> None:
        self._build_queue_list._on_closed()

    def _on_empire_build_queue_closed(self) -> None:
        self._empire_build_queue._on_closed()

    def _on_event_log_closed(self) -> None:
        self._event_log._on_closed()

    def _on_event_log_navigate(self, location_hex: list) -> None:
        self._event_log._on_navigate(location_hex)

    def _on_empire_panel_closed(self) -> None:
        self._empire_panel._on_closed()

    def _on_settings_closed(self) -> None:
        self._settings._on_closed()

    def _on_fleet_report_closed(self) -> None:
        self._fleet_report._on_closed()

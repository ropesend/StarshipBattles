"""
StrategyScreen - Main coordinator for strategy layer.

This is the central hub that manages the strategy game state and delegates
to specialized modules for rendering, input handling, and game operations.

Refactored from 1,568 lines to ~350 lines by extracting:
- StrategyRenderer: All drawing logic (~580 lines)
- InputHandler: Event and click routing (~180 lines)
- CameraNavigator: Camera focus and zoom (~90 lines)
- FleetOperations: Fleet movement commands (~130 lines)
- ColonizationSystem: Colonization workflow (~175 lines)

PROJ-40: Use protocol type guards instead of isinstance for cross-layer checks.
"""
from __future__ import annotations

import logging
from typing import Any

from game.ui.config import UIConfig
from game.ui.renderer.camera import Camera
from game.ui.screens.strategy_ui import StrategyUI

logger = logging.getLogger(__name__)

# Extracted modules
from game.strategy.facade.strategy_session_facade import StrategySessionFacade
from game.ui.screens.race_asset_loader import RaceAssetLoader
from game.ui.screens.strategy_screen_composition import (
    StrategyScreenComposition,
    StrategyScreenCompositionFactory,
)
from game.ui.colors import BG_BATTLE


class StrategyScreen:
    """Manages strategy layer simulation, rendering, and UI.

    Implements IScene protocol for standardized scene handling.
    """

    TOP_BAR_HEIGHT = 50

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        session=None,
        scene_callback=None,
        input_mapper=None,
        *,
        composition: StrategyScreenComposition | None = None,
    ):
        """Initialize strategy screen.

        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
            session: Optional GameSession to use (creates new if None)
            scene_callback: Callback function for scene transitions.
                           Called with (action, **kwargs) where action is:
                           - "open_builder": Open design workshop with context kwarg
            input_mapper: Optional InputMapper for centralized keybinding resolution.
            composition: PROJ-327 Phase 4 — Compositional Construction seam.
                Defaults to ``StrategyScreenCompositionFactory()`` (production
                wiring). Tests pass ``MockStrategyScreenComposition`` from
                ``tests/fixtures/strategy_screen_composition.py`` to substitute
                any sub-object without bypass-init monkey-patching. See
                ``docs/02_PATTERNS.md`` § "Compositional Construction".
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scene_callback = scene_callback
        self.input_mapper = input_mapper

        # Session Management
        # PROJ-382 Phase 1: ``self._session`` is the private composition-root
        # handle. External callers should use ``self.facade`` instead. The
        # public ``session`` property (below) is retained as an audit-residue
        # delegate while deferred U1/U2/U3 cover the broader UI surface that
        # still reads ``c.scene.session.<x>``; the AST static-guard at
        # ``tests/static_guards/test_facade_bypass_guard.py`` blocks the
        # facade-bypass dispatch path from re-growing.
        if session:
            self._session = session
        else:
            from game.strategy.engine.game_session import GameSession
            from game.ai.ai_factory import AIControllerFactory
            self._session = GameSession(ai_factory=AIControllerFactory())

        # Create facade for UI-to-engine communication
        self._facade = StrategySessionFacade(self._session)

        # Camera
        self.camera = Camera(
            screen_width - UIConfig.STRATEGY_SIDEBAR_WIDTH,
            screen_height - self.TOP_BAR_HEIGHT,
            offset_x=0,
            offset_y=self.TOP_BAR_HEIGHT
        )
        self.camera.max_zoom = 25.0
        self.camera.zoom = 2.0  # Start Zoomed In

        # Focus on Player Home
        self._focus_on_player_home()

        # UI
        self.ui = StrategyUI(self, screen_width, screen_height, input_mapper=input_mapper)

        # State
        self.hover_hex = None
        self.hex_size = 10
        self.detail_zoom_level = 3.0

        self.selected_fleet = None
        self.selected_object = None
        self.last_selected_system = None

        self.turn_processing = False
        self.current_player_index = 0
        self._quit_confirm_dialog = None
        self.build_queue_screen = None

        # FEAT-20: Dev "Run 10 Turns" cancel flag — set by Esc-pump during loop
        self.dev_run_cancel_requested = False
        # FEAT-20: progress text shown by the "PROCESSING TURN..." overlay
        # during dev `run_n_turns`. None means default message.
        self.turn_processing_message: str | None = None
        # Issue #7: per-tick progress (1..TICKS_PER_TURN) shown as a smaller
        # secondary line below the main "PROCESSING TURN..." label. Set by
        # the StrategyGameStateManager callback every tick; None outside the
        # turn-processing window so the secondary line is hidden.
        self.current_tick: int | None = None
        self.total_ticks: int | None = None

        # Assets
        self.empire_assets = {}
        self._race_loader = RaceAssetLoader()
        self._load_assets()

        # Initialize sub-modules via Composition factory (PROJ-327 Phase 4).
        # Default factory constructs the production graph verbatim; tests
        # substitute via MockStrategyScreenComposition.
        comp = composition or StrategyScreenCompositionFactory()
        self._renderer = comp.make_renderer(self)
        self._camera_nav = comp.make_camera_navigator(self)
        self._fleet_ops = comp.make_fleet_ops(self)
        self._colonization = comp.make_colonization(self)
        self._superweapons = comp.make_superweapons(self)
        self._build_queue = comp.make_build_queue_manager(self)
        self._game_state = comp.make_game_state_manager(self)
        self._input = comp.make_input_handler(self)

    # =========================================================================
    # Properties (delegate to session for internal convenience)
    # External callers should use the facade for cross-layer communication.
    # =========================================================================

    @property
    def galaxy(self) -> Any:
        return self._session.galaxy

    @property
    def empires(self) -> Any:
        return self._session.empires

    @property
    def systems(self) -> Any:
        return self._session.systems

    @property
    def active_empire(self) -> Any:
        """The empire whose turn it currently is.

        BUG-125: renamed from `player_empire` (which never rotated and
        silently broke authorization in hot-seat). Delegates to
        `session.active_empire`, which is rotated by
        `StrategyGameStateManager.advance_turn`.
        """
        return self._session.active_empire

    @property
    def enemy_empire(self) -> Any:
        return self._session.enemy_empire

    @property
    def human_player_ids(self) -> Any:
        return self._session.human_player_ids

    @property
    def current_empire(self) -> Any:
        """Get the empire for the current player (supports N players).

        This is the *viewing* human — the player whose turn-order index
        is at ``current_player_index``. Prefer the explicit
        ``viewing_empire_id`` accessor (below) when only the id is
        needed; reserve ``active_empire`` for turn-gated authorization
        decisions (command handlers, end-turn).
        """
        empires = self.empires
        if not empires:
            return self.active_empire

        human_player_ids = self.human_player_ids
        if not human_player_ids:
            return self.active_empire or empires[0]

        current_player_id = human_player_ids[self.current_player_index]
        return next((e for e in empires if e.id == current_player_id), empires[0])

    @property
    def viewing_empire_id(self) -> int | None:
        """Canonical anchor for 'whose data should this UI show'.

        Returns ``current_empire.id`` (the human at the keyboard), not
        ``active_empire.id`` (the empire whose turn it is). The two
        diverge in hot-seat play — e.g. when a save is loaded mid-turn,
        or when ``advance_turn`` has rotated ``active_empire`` but the
        UI is rendering for the previous viewer.

        New UI surfaces that fetch empire-scoped data (designs,
        planets, fleets, build queues, deployments, etc.) should
        anchor here. Turn-gated actions (move orders, end-turn) still
        authorize against ``active_empire``.

        See ``feedback_viewing_empire_anchor`` memory and QA Obs 1
        (post-PROJ-FMS, 2026-05-16).
        """
        empire = self.current_empire
        return empire.id if empire is not None else None

    @property
    def facade(self) -> Any:
        """Public accessor for the strategy session facade.

        Used by dialogs and child components that need to issue commands
        or query game state through the facade pattern.
        """
        return self._facade

    @property
    def session(self) -> Any:
        """Audit-residue delegate for legacy ``c.scene.session.<x>`` reads.

        PROJ-382 Phase 1: ``self._session`` is the private composition-root
        handle. The facade is the canonical UI-to-engine boundary; the AST
        guard at ``tests/static_guards/test_facade_bypass_guard.py`` blocks
        any new ``<expr>.session.handle_command(...)`` regression. Existing
        registries / galaxy / active_empire reads still resolve through this
        delegate while deferred PROJs (U1/U2/U3) cover the broader migration.

        The setter exists solely so tests may swap in a mock session via
        ``screen.session = ...``; production code never reassigns the
        session post-init.
        """
        return self._session

    @session.setter
    def session(self, value: Any) -> None:
        """Write-through setter for test session swap.

        PROJ-382 Phase 1 introduced this setter so tests can swap in a mock
        session via ``screen.session = ...``.

        PROJ-396 MAJ-001: writing ``_session`` alone left ``self._facade``
        pointing at the original session — every subsequent
        ``screen.facade.handle_command(...)`` then dispatched through the
        stale session while ``screen.galaxy`` / ``empires`` / ``active_empire``
        read from the new one (split-brain). The setter now rebuilds the
        facade in lockstep so both halves of the screen stay coherent
        regardless of whether tests swap via ``screen.session = ...`` or
        production constructs the screen normally.
        """
        self._session = value
        self._facade = StrategySessionFacade(value)

    @property
    def input_mode(self) -> Any:
        return self._input.input_mode

    @input_mode.setter
    def input_mode(self, value) -> None:
        self._input.input_mode = value

    # =========================================================================
    # Lifecycle Methods
    # =========================================================================

    def update(self, dt) -> None:
        """Update scene state."""
        self.camera.update(dt)
        self._renderer.update(dt)
        self.ui.update(dt)

    def draw(self, screen) -> None:
        """Render the scene."""
        # Always fill entire screen first to prevent remnants from other screens
        screen.fill(BG_BATTLE)

        self._renderer.draw(screen)

        if self.turn_processing:
            # FEAT-20: dev `run_n_turns` overrides the message with progress text.
            message = getattr(self, 'turn_processing_message', None) or "PROCESSING TURN..."
            # Issue #7: getattr defaults match the FEAT-20 idiom — keeps the
            # call site safe under partial-construction in tests.
            self._renderer.draw_processing_overlay(
                screen, message,
                current_tick=getattr(self, 'current_tick', None),
                total_ticks=getattr(self, 'total_ticks', None),
            )

        self.ui.draw(screen)

        # Draw build queue screen overlay (including drag preview).
        # PROJ-376 Phase 2: gate on is_visible() — the cached screen
        # persists across opens and must not draw while hidden.
        if (
            self.build_queue_screen is not None
            and self.build_queue_screen.is_visible()
        ):
            self.build_queue_screen.draw(screen)

    def handle_resize(self, width, height) -> None:
        """Handle window resize."""
        self.screen_width = width
        self.screen_height = height
        self.camera.width = width - UIConfig.STRATEGY_SIDEBAR_WIDTH
        self.camera.height = height - self.TOP_BAR_HEIGHT
        self.camera.offset_y = self.TOP_BAR_HEIGHT
        self.ui.handle_resize(width, height)

    # =========================================================================
    # Event Handling (delegates to InputHandler)
    # =========================================================================

    def handle_event(self, event) -> None:
        """Process pygame events."""
        self._input.handle_event(event)

    def handle_click(self, mx, my, button) -> Any:
        """Handle mouse clicks."""
        return self._input.handle_click(mx, my, button)

    def update_input(self, dt, events) -> None:
        """Update input state."""
        self._input.update_input(dt, events)

    # =========================================================================
    # Navigation (delegates to CameraNavigator)
    # =========================================================================

    def center_camera_on(self, obj) -> None:
        """Center camera on a game object."""
        self._camera_nav.center_on(obj)

    def cycle_selection(self, obj_type, direction) -> None:
        """Cycle selection through colonies or fleets."""
        new_obj = self._camera_nav.cycle_selection(obj_type, direction)
        if new_obj:
            self.on_ui_selection(new_obj)
            self.center_camera_on(new_obj)

    # =========================================================================
    # Colonization (delegates to ColonizationSystem)
    # =========================================================================

    def on_colonize_click(self) -> None:
        """Handle colonize action — opens load transfer dialog first."""
        from game.ui.screens import strategy_screen_selection as _sel
        _sel.on_colonize_click(self)

    def _on_colonize_planet_selected(self, planet) -> None:
        """Handle planet selection — issue colonize command, then open drop dialog."""
        from game.ui.screens import strategy_screen_selection as _sel
        _sel.on_colonize_planet_selected(self, planet)

    def request_colonize_order(self, fleet, planet=None) -> None:
        """Handle colonize request from UI."""
        from game.ui.screens import strategy_screen_selection as _sel
        _sel.request_colonize_order(self, fleet, planet)

    # =========================================================================
    # Order Editing
    # =========================================================================

    # State for EDIT_MOVE mode: ghost hex of old destination
    _edit_move_ghost_hex = None
    _edit_move_order_index = None
    _edit_move_fleet = None

    def on_edit_order(self, entity, order_index, order) -> None:
        """Handle edit request for an order in the queue."""
        from game.ui.screens import strategy_screen_order_editing as _order_edit
        _order_edit.on_edit_order(self, entity, order_index, order)

    def _start_edit_move(self, fleet, order_index, order) -> None:
        """Enter EDIT_MOVE mode."""
        from game.ui.screens import strategy_screen_order_editing as _order_edit
        _order_edit.start_edit_move(self, fleet, order_index, order)

    def complete_edit_move(self, new_hex) -> None:
        """Finalize MOVE order edit: update the order target in-place."""
        from game.ui.screens import strategy_screen_order_editing as _order_edit
        _order_edit.complete_edit_move(self, new_hex)

    def _start_edit_transfer(self, fleet, order_index, order) -> None:
        """Re-open transfer dialog pre-populated with current order amounts."""
        from game.ui.screens import strategy_screen_order_editing as _order_edit
        _order_edit.start_edit_transfer(self, fleet, order_index, order)

    # =========================================================================
    # Turn Management (delegates to GameStateManager)
    # =========================================================================

    def advance_turn(self) -> None:
        """End current player's order phase. Process turn when all humans ready."""
        self._game_state.advance_turn()

    def run_n_turns(self, n: int = 10) -> int:
        """Dev-mode: run N full game turns sequentially (FEAT-20).

        Each iteration runs the full end-turn flow for every player. Esc cancels
        between iterations (never mid-turn — auto-save runs at the end of each
        turn). Per-turn event-log popups are suppressed during the loop and a
        single combined log is surfaced at the end.

        Args:
            n: Number of full turns to run.

        Returns:
            Number of turns actually completed (may be < n if cancelled).
        """
        return self._game_state.run_n_turns(n)

    # =========================================================================
    # Selection
    # =========================================================================

    def on_ui_selection(self, obj) -> None:
        """Called when user selects an item in the UI list."""
        from game.ui.screens import strategy_screen_selection as _sel
        _sel.on_ui_selection(self, obj)

    # =========================================================================
    # Actions
    # =========================================================================

    def on_build_yard_click(self) -> None:
        """Open build queue screen for selected planet."""
        self._build_queue.on_build_yard_click()

    def on_navigate_to_hex_build(self, hex_coord, source) -> None:
        """Navigate to the build queue screen for a specific hex and source."""
        self._build_queue.on_navigate_to_hex_build(hex_coord, source)

    def on_fleet_build_click(self) -> None:
        """Open build queue screen for selected fleet (PROJ-67: Fleet Space Yards)."""
        self._build_queue.on_fleet_build_click()

    def on_design_click(self) -> None:
        """Handle 'Design' button click - opens Design Workshop."""
        from game.ui.screens import strategy_screen_lifecycle as _lifecycle
        _lifecycle.on_design_click(self)

    def on_menu_option(self, option: str) -> None:
        """Dispatch menu option from the strategy menu panel.

        Args:
            option: Option identifier string from StrategyMenuPanel.
        """
        from game.ui.screens import strategy_screen_lifecycle as _lifecycle
        _lifecycle.on_menu_option(self, option)

    def _show_load_game_dialog(self) -> None:
        """Open the save selection window for loading a game."""
        from game.ui.screens import strategy_screen_lifecycle as _lifecycle
        _lifecycle.show_load_game_dialog(self)

    def _on_load_selected(self, save_path, turn_number=None) -> None:
        """Handle save selection from load dialog."""
        from game.ui.screens import strategy_screen_lifecycle as _lifecycle
        _lifecycle.on_load_selected(self, save_path, turn_number)

    def _confirm_quit_to_menu(self) -> None:
        """Show confirmation dialog before quitting to main menu."""
        from game.ui.screens import strategy_screen_lifecycle as _lifecycle
        _lifecycle.confirm_quit_to_menu(self)

    def _handle_quit_confirmed(self) -> None:
        """Handle quit-to-menu confirmation dialog result."""
        from game.ui.screens import strategy_screen_lifecycle as _lifecycle
        _lifecycle.handle_quit_confirmed(self)

    def _show_coming_soon(self, feature_name: str) -> None:
        """Show a 'Coming Soon' placeholder dialog."""
        from game.ui.screens import strategy_screen_lifecycle as _lifecycle
        _lifecycle.show_coming_soon(self, feature_name)

    def on_save_game_click(self) -> None:
        """Handle 'Save Game' button click."""
        from game.ui.screens import strategy_screen_lifecycle as _lifecycle
        _lifecycle.on_save_game_click(self)

    # =========================================================================
    # Pathfinding (for external access)
    # =========================================================================

    def calculate_hybrid_path(self, start_hex, end_hex) -> Any:
        """Calculate path combining local hex movement and warp jumps."""
        return self.galaxy._pathfinder.find_hybrid_path(start_hex, end_hex)

    def _get_system_at_hex(self, hex_c) -> Any:
        """Find which system owns this hex."""
        return self.galaxy._pathfinder.get_system_at_hex(hex_c)

    def _find_nearest_system(self, hex_c) -> Any:
        """Find the nearest system to a hex coordinate."""
        return self.galaxy._pathfinder.find_nearest_system(hex_c)

    # =========================================================================
    # Private Helpers
    # =========================================================================

    def _focus_on_player_home(self) -> None:
        """Focus camera on player's home colony at startup."""
        from game.ui.screens import strategy_screen_assets as _assets
        _assets.focus_on_player_home(self)

    def _load_assets(self) -> None:
        """Load visual assets using AssetManager and RaceAssetLoader."""
        from game.ui.screens import strategy_screen_assets as _assets
        _assets.load_assets(self)

    def _get_object_asset(self, obj) -> Any:
        """Resolve the visual asset for a data object."""
        from game.ui.screens import strategy_screen_assets as _assets
        return _assets.get_object_asset(self, obj)

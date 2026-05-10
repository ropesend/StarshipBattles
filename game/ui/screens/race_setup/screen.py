"""PROJ-309 Sub-phase 3.1 — RaceSetupScreen orchestrator.

Thin orchestrator for the race setup wizard. Constructs the seven tab
panels (via `panel_factory.py`), holds delegate references (Controller /
Renderer / ViewModel / InputHandler / LLMDialogService), and forwards
`update()` / `process_event()` / `kill()` to them.

All business logic lives on the delegates per `docs/03_CONVENTIONS.md
§1.6` (MVVM) and the design at
`Projects/active_projects/PROJ-309/findings/race_setup_screen_decomposition.md`.

Public API stability: `from game.ui.screens.race_setup_screen import
RaceSetupScreen` keeps working via a 4-line shim at the legacy path
(Option A). The constructor signature is unchanged so `app.py:522` and
`new_game_setup_screen.py:433` continue to construct it the same way.
"""
from __future__ import annotations

import logging
from typing import Callable, List, Optional, TYPE_CHECKING

import pygame
import pygame_gui

from game.strategy.data.race_config import RaceConfig
from game.strategy.systems.race_library import RaceLibrary
# Re-exported for the FEAT-12 tests that patch
# `game.ui.screens.race_setup_screen.RaceRandomizer` — the legacy shim
# at `race_setup_screen.py` re-exports this name from the package.
from game.strategy.systems.race_randomizer import RaceRandomizer  # noqa: F401

# PROJ-12 Phase 4: extracted siblings.
from game.ui.screens.race_browser_dialog import RaceBrowserDialog  # noqa: F401
from game.ui.screens.race_validator import RaceValidator  # noqa: F401
from game.ui.screens.race_asset_loader import RaceAssetLoader

from game.ui.screens.race_setup import panel_factory
from game.ui.screens.race_setup.controller import RaceSetupController  # noqa: F401  (re-export for tests)
from game.ui.screens.race_setup.delegate_factory import (
    DefaultRaceSetupDelegateFactory,
    RaceSetupDelegates,
)
from game.ui.screens.race_setup.input_handler import RaceSetupInputHandler  # noqa: F401  (re-export for tests)
from game.ui.screens.race_setup.llm_dialog_service import LLMDialogService  # noqa: F401  (re-export for tests)
from game.ui.screens.race_setup.renderer import RaceSetupRenderer  # noqa: F401  (re-export for tests)
from game.ui.screens.race_setup.ui_builder import RaceSetupUiBuilder
from game.ui.screens.race_setup.view_model import (
    TAB_APTITUDES,
    TAB_DESCRIPTIONS,
    TAB_ENVIRONMENT,
    TAB_IDENTITY,
    TAB_NAMES,
    TAB_SHIPS,
    TAB_SUMMARY,
    TAB_VISUALS,
    RaceSetupViewModel,
)

if TYPE_CHECKING:
    from game.core.protocols import IRaceRegistry

logger = logging.getLogger(__name__)


class RaceSetupScreen(pygame_gui.elements.UIWindow):
    """Tab-based window for race configuration."""

    # Tab constants — re-exported as class attrs for backwards-compat
    # with existing tests that read `RaceSetupScreen.TAB_*`.
    TAB_SUMMARY = TAB_SUMMARY
    TAB_IDENTITY = TAB_IDENTITY
    TAB_VISUALS = TAB_VISUALS
    TAB_SHIPS = TAB_SHIPS
    TAB_ENVIRONMENT = TAB_ENVIRONMENT
    TAB_APTITUDES = TAB_APTITUDES
    TAB_DESCRIPTIONS = TAB_DESCRIPTIONS
    TAB_NAMES = TAB_NAMES

    def __init__(
        self,
        rect: pygame.Rect,
        manager: pygame_gui.UIManager,
        on_complete_callback: Callable[[RaceConfig], None],
        on_cancel_callback: Callable[[], None],
        race_to_edit: Optional[RaceConfig] = None,
        race_registry: Optional["IRaceRegistry"] = None,
        *,
        ui_builder: Optional[RaceSetupUiBuilder] = None,
        delegate_factory: Optional[DefaultRaceSetupDelegateFactory] = None,
    ):
        """Create race setup wizard window.

        Args:
            rect: Window rectangle.
            manager: pygame_gui UIManager.
            on_complete_callback: Callback(RaceConfig) when user saves race.
            on_cancel_callback: Callback() when user cancels.
            race_to_edit: Optional existing race to edit.
            race_registry: Optional session-scoped IRaceRegistry (PROJ-287).
                When supplied, a successful save invalidates the cached
                entry for the saved race so the next ``get_race`` call
                re-reads from disk. Pre-game launches pass None.
            ui_builder: PROJ-325 Phase 3 — UI builder seam. Defaults to
                ``RaceSetupUiBuilder`` (production widget construction).
                Tests can pass ``NullRaceSetupUiBuilder`` /
                ``MockRaceSetupUiBuilder`` from
                ``tests/fixtures/race_setup_ui_builders.py``.
            delegate_factory: PROJ-325 Phase 3 — delegate-factory seam.
                Defaults to ``DefaultRaceSetupDelegateFactory`` (the
                production MVVM wiring). Tests can pass a custom factory
                to substitute any delegate.

        Two-stage construction (PROJ-325 Phase 3):

        1. Cheap state + delegate construction runs *before* the
           ``bypass_init`` guard, so test instances built under
           ``with bypass_init(RaceSetupScreen):`` still have real
           delegates (``_view_model``, ``_controller``, etc.) populated.
        2. The ``UIWindow`` shell + widget tree run *after* the guard.
           Bypassed instances skip the heavy ``pygame_gui`` calls.

        See ``Projects/active_projects/PROJ-325/findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md``
        for the full rationale.
        """
        # ---- Stage 1: cheap state + widget-ref placeholders + delegates ----
        self._init_state(
            rect=rect,
            on_complete_callback=on_complete_callback,
            on_cancel_callback=on_cancel_callback,
            race_to_edit=race_to_edit,
            race_registry=race_registry,
        )
        self._init_widget_refs()
        self._delegates: RaceSetupDelegates = (
            delegate_factory or DefaultRaceSetupDelegateFactory()
        ).build(self)
        # Mirror delegate refs to the legacy attribute names so callers
        # / tests that read ``screen._view_model`` etc. keep working.
        self._view_model = self._delegates.view_model
        self._renderer = self._delegates.renderer
        self._controller = self._delegates.controller
        self._input_handler = self._delegates.input_handler
        self._llm_service = self._delegates.llm_service

        # ---- Stage 2: UIWindow shell (skipped under bypass_init) ----
        # PROJ-324 Phase 1: opt-in test escape hatch — see
        # StrategyModalWindow.__init__ for full rationale. PROJ-325
        # Phase 3 moved the guard from the first executable statement to
        # *after* cheap state + delegate setup so bypassed instances are
        # useful (not bare).
        if getattr(type(self), 'bypass_init', False):
            self.ui_manager = manager
            self._window_init_bypassed = True
            # Stage 3 (test branch): give the (test-supplied) builder a
            # chance to populate widget slots without a real UIWindow
            # shell. Production builds would not pass a ``ui_builder``;
            # tests pass ``NullRaceSetupUiBuilder`` (no-op) or
            # ``MockRaceSetupUiBuilder`` (MagicMock-populated slots).
            # When no builder is supplied under bypass, leave slots at
            # their ``_init_widget_refs`` placeholders.
            if ui_builder is not None:
                ui_builder.build(self)
            return

        super().__init__(
            rect,
            manager,
            window_display_title="Species Setup",
            object_id="#race_setup_window",
            resizable=False,
        )
        # PROJ-347 T4.6: mirror StrategyModalWindow base — production
        # paths set ``_window_init_bypassed = False`` so the flag is
        # always defined (tests and call sites can rely on it without
        # ``getattr(..., False)`` everywhere).
        self._window_init_bypassed = False

        # ---- Stage 3 (production): widget tree ----
        (ui_builder or RaceSetupUiBuilder()).build(self)
        self._show_step(self._view_model.current_step)

    # ------------------------------------------------------------------
    # PROJ-325 Phase 3 — two-stage construction helpers
    # ------------------------------------------------------------------

    def _init_state(
        self,
        *,
        rect: pygame.Rect,
        on_complete_callback: Callable[[RaceConfig], None],
        on_cancel_callback: Callable[[], None],
        race_to_edit: Optional[RaceConfig],
        race_registry: Optional["IRaceRegistry"],
    ) -> None:
        """Assign cheap state — no pygame_gui widget construction.

        Called from ``__init__`` *before* the ``bypass_init`` guard so
        test-mode instances see the same race_config / library / asset
        loader / callback wiring as production. Stays cheap: only Python
        object construction (no live pygame display required).

        Note: ``rect`` is intentionally NOT assigned to ``self.rect``
        here. ``pygame_gui``'s ``GUISprite`` base class implements
        ``rect`` as a descriptor that mutates ``self.blit_data`` on
        write — and ``blit_data`` is initialized by the
        ``pygame.sprite.Sprite.__init__`` chain that ``bypass_init``
        skips. In production, ``super().__init__`` (called by Stage 2
        of ``__init__``) assigns ``self.rect`` for us. Tests still
        pass ``rect`` for parity with the production constructor.
        Pattern-discovery flagged for PROJ-328: the consensus plan's
        headline sketch wrote ``self.rect = rect`` in the bypass branch,
        but that fails for ``UIWindow`` subclasses; sibling refactors
        will need to either drop the assignment (as here) or use
        ``object.__setattr__`` / a direct ``self._rect`` write.
        """
        del rect  # see docstring — not assignable on a bypassed UIWindow
        # Working race configuration. Controller is the writeable owner;
        # the screen mirrors for backwards-compat with tests/callers that
        # read ``screen.race_config`` / ``screen.is_editing``.
        if race_to_edit:
            self.race_config = race_to_edit
            self.is_editing = True
        else:
            self.race_config = RaceConfig()
            self.is_editing = False

        self.race_library = RaceLibrary()
        self.race_registry = race_registry
        self._asset_loader = RaceAssetLoader()

        # Backwards-compat: existing tests / code read these directly.
        self.on_complete_callback = on_complete_callback
        self.on_cancel_callback = on_cancel_callback

    def _init_widget_refs(self) -> None:
        """Assign every widget slot to ``None`` / empty container.

        Per the consensus refactor plan: prefer explicit placeholder
        initialization over lazy properties. Bypassed instances are then
        honest — widget tree absent, cheap delegates present.
        """
        # Panel references — populated by the production UI builder.
        self._summary_panel = None
        self._identity_panel = None
        self._environment_panel = None
        self._aptitudes_panel = None
        self._description_panel = None
        self._flag_gallery = None
        self._portrait_gallery = None
        self._theme_gallery = None

        # UI element references built in ``_create_ui()`` / by the builder.
        self.step_panels: List = []
        self.tab_buttons: List = []
        # Issue #11: {tab_index: factory} for deferred panel construction.
        self._deferred_panel_factories: dict = {}
        self.btn_cancel: Optional[pygame_gui.elements.UIButton] = None
        self.btn_save: Optional[pygame_gui.elements.UIButton] = None
        self.btn_load: Optional[pygame_gui.elements.UIButton] = None
        self.btn_randomize: Optional[pygame_gui.elements.UIButton] = None
        self.btn_randomize_all: Optional[pygame_gui.elements.UIButton] = None
        self.error_label: Optional[pygame_gui.elements.UILabel] = None
        self.ship_preview_scroll: Optional[
            pygame_gui.elements.UIScrollingContainer
        ] = None

    # ------------------------------------------------------------------
    # Backwards-compat property shims
    # ------------------------------------------------------------------

    @property
    def current_step(self) -> int:
        return self._view_model.current_step

    @current_step.setter
    def current_step(self, value: int) -> None:
        self._view_model.current_step = value

    @property
    def _description_controller(self):
        # Tests + legacy code read `screen._description_controller`.
        return self._controller.description_controller

    @_description_controller.setter
    def _description_controller(self, value) -> None:
        # Used by the descriptions-tab factory + tests' bypass-init helpers.
        self._controller.attach_description_controller(value)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _create_ui(self) -> None:
        """Create all UI elements."""
        container = self.get_container()
        content_width = container.get_size()[0] - 20
        content_height = container.get_size()[1]

        self._create_tab_buttons(container, content_width)

        # Content area for tab panels (below tabs, above bottom buttons).
        panel_top = 55
        panel_height = content_height - 130
        self._create_step_panels(container, content_width, panel_top, panel_height)

        self._create_navigation_buttons(container, content_width, content_height)

        self.error_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, content_height - 90, content_width, 25),
            text="",
            manager=self.ui_manager,
            container=container,
        )

    def _create_tab_buttons(self, container, content_width: int) -> None:
        tab_y = 5
        num_tabs = len(self.TAB_NAMES)
        tab_width = (content_width - 10) // num_tabs
        tab_height = 40

        for i, name in enumerate(self.TAB_NAMES):
            btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(10 + i * tab_width, tab_y, tab_width - 5, tab_height),
                text=name,
                manager=self.ui_manager,
                container=container,
                object_id=f"#tab_{name.lower()}",
            )
            btn.tab_index = i
            self.tab_buttons.append(btn)

    def _create_step_panels(self, container, width: int, top: int, height: int) -> None:
        """Create one UIPanel per tab. Issue #11: only Summary runs eagerly;
        other factories are deferred to first ``_show_step`` (or to
        ``ensure_panel_built`` when the controller needs gallery contents
        before the user has visited the tab)."""
        panel_rect = pygame.Rect(10, top, width, height)
        factories = (
            ("#panel_summary", panel_factory.create_summary_panel),
            ("#panel_identity", panel_factory.create_identity_panel),
            ("#panel_visuals", panel_factory.create_visuals_panel),
            ("#panel_ships", panel_factory.create_ships_panel),
            ("#panel_environment", panel_factory.create_environment_panel),
            ("#panel_aptitudes", panel_factory.create_aptitudes_panel),
            ("#panel_descriptions", panel_factory.create_descriptions_panel),
        )
        self._deferred_panel_factories = {}
        for tab_index, (object_id, factory) in enumerate(factories):
            panel = pygame_gui.elements.UIPanel(
                relative_rect=panel_rect,
                manager=self.ui_manager,
                container=container,
                object_id=object_id,
            )
            if tab_index == TAB_SUMMARY:
                factory(self, panel)
            else:
                self._deferred_panel_factories[tab_index] = factory
            self.step_panels.append(panel)

    def ensure_panel_built(self, tab_index: int) -> None:
        """Materialise a deferred tab panel if not yet built (Issue #11)."""
        factory = self._deferred_panel_factories.pop(tab_index, None)
        if factory is None:
            return
        factory(self, self.step_panels[tab_index])

    def _create_navigation_buttons(self, container, content_width: int, content_height: int) -> None:
        """Bottom action buttons."""
        button_y = content_height - 60
        button_width = 120
        button_height = 40

        self.btn_cancel = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, button_y, button_width, button_height),
            text="Cancel",
            manager=self.ui_manager,
            container=container,
        )

        randomize_width = 160
        self.btn_randomize = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10 + button_width + 10, button_y, randomize_width, button_height),
            text="Generate Random",
            manager=self.ui_manager,
            container=container,
        )
        self.btn_randomize.hide()

        self.btn_save = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(content_width - button_width + 10, button_y, button_width, button_height),
            text="Save" if not self.is_editing else "Update",
            manager=self.ui_manager,
            container=container,
        )

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _show_step(self, step_num: int) -> None:
        """Show the specified tab panel and refresh content as needed."""
        step_num = self._view_model.clamp_step(step_num)
        self._view_model.current_step = step_num

        logger.debug(f"Showing race setup tab {step_num}: {self.TAB_NAMES[step_num]}")

        self.ensure_panel_built(step_num)  # Issue #11: lazy tab build

        for i, panel in enumerate(self.step_panels):
            if i == step_num:
                panel.show()
            else:
                panel.hide()

        self._update_tab_highlighting()
        self._update_navigation_buttons()

        if self.error_label:
            self.error_label.set_text("")

        # Refresh content when showing specific tabs.
        if step_num == self.TAB_SUMMARY:
            self._refresh_summary()
        elif step_num == self.TAB_SHIPS:
            if self.race_config.theme_id:
                self._renderer.refresh_ship_preview(self.race_config.theme_id)
        elif step_num == self.TAB_APTITUDES:
            if self._aptitudes_panel:
                self._aptitudes_panel.update_budget_display()

    def _update_navigation_buttons(self) -> None:
        """Update navigation button visibility based on current tab."""
        step = self.current_step
        if self._view_model.show_save_button_on(step):
            self.btn_save.show()
        else:
            self.btn_save.hide()

        if self._view_model.show_randomize_button_on(step):
            self.btn_randomize.show()
        else:
            self.btn_randomize.hide()

    def _update_tab_highlighting(self) -> None:
        """Update tab button visual states to show the current tab."""
        for i, btn in enumerate(self.tab_buttons):
            if i == self.current_step:
                btn.select()
            else:
                btn.unselect()

    def _refresh_summary(self) -> None:
        """Refresh summary panel with current race_config data."""
        logger.debug("Refreshing race summary")
        self._controller.update_descriptions_from_text()
        if self._summary_panel:
            self._summary_panel.refresh()

    # ------------------------------------------------------------------
    # Per-frame update + lifecycle + event dispatch
    # ------------------------------------------------------------------

    def update(self, time_delta: float) -> None:
        """Per-frame update.

        PROJ-299: polls the description LLM controller so its background
        worker results land in the UI on the same frame they complete.
        Also drives the 30s/90s "still working" dialog and error popups.

        Issue #6: also pumps `RaceDescriptionPanel.update(time_delta)`
        so its elapsed-seconds status label can tick while the LLM call
        is RUNNING. Without this call the timer freezes at the value it
        had at the IDLE→RUNNING transition.
        """
        super().update(time_delta)
        controller = self._controller.description_controller
        if controller is not None:
            controller.update()
            self._llm_service.check_dialog_thresholds(controller)
            self._llm_service.check_error_popups(controller)
        if self._description_panel is not None:
            self._description_panel.update(time_delta)

    def kill(self) -> None:
        """PROJ-299: cancel any in-flight LLM calls so worker threads
        don't try to populate dead text-box widgets after teardown."""
        controller = self._controller.description_controller
        if controller is not None:
            controller.cancel_all()
        super().kill()

    def on_close_window_button_pressed(self) -> None:
        """BUG-115: Route the title-bar [X]-close through the same path
        as the in-window Cancel button. Default ``UIWindow`` behaviour
        only calls ``self.kill()``, which leaves callers' modal-tracking
        state stale (e.g., ``NewGameSetupScreen.active_race_modal``).
        Delegating to ``controller.on_cancel`` fires ``on_cancel_callback``
        and then ``kill()`` — single canonical cancel path."""
        self._controller.on_cancel()

    def process_event(self, event: pygame.event.Event) -> bool:
        """Delegate event dispatch to the input handler."""
        super_handled = super().process_event(event)
        return self._input_handler.handle(event, super_handled=super_handled)

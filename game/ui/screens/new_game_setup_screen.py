"""New Game Setup Screen - UI for configuring a new game.

Allows users to:

* Enter a save name.
* Select number of players (1-4).
* Select or create races for each player.
* Start the game with race-based themes and visuals.

PROJ-40: Moved RaceConfig to TYPE_CHECKING (type-hints only).
PROJ-328 Phase B: Real MVVM split.

* ``NewGameSetupViewModel`` (``new_game_setup_view_model.py``) owns
  the user-input state — player count, galaxy type, system count,
  per-player race selections, modal state. Pure Python; no
  ``pygame_gui`` imports.
* ``NewGameSetupController`` (``new_game_setup_controller.py``) owns
  the mutations + lifecycle — save-name validation, ``GameConfig``
  building, race-modal callbacks, start/cancel.
* ``NewGameSetupUiBuilder`` (``new_game_setup_ui_builder.py``) is a
  Pattern §33 (``docs/02_PATTERNS.md``) test-substitution seam. The
  production builder's ``build()`` is currently a one-line passthrough
  that delegates to ``screen._create_ui()``; the actual ``pygame_gui``
  widget construction still lives on the screen because it reaches
  into a number of screen helpers (``_create_empire_inputs`` /
  ``_update_empire_visibility``) and reads ``self.get_container()``
  on the live ``UIWindow``. Tests swap in
  ``MockNewGameSetupUiBuilder`` / ``NullNewGameSetupUiBuilder`` from
  ``tests/fixtures/new_game_setup_ui_builder.py`` to bypass widget
  construction under ``bypass_init``. Incrementally moving widget
  construction into the builder is a low-priority follow-up and is
  explicitly out of scope here.

The screen itself composes the three delegates, forwards events to
the controller, owns the widget refs populated by ``_create_ui()``,
and keeps property shims so existing tests / callers that read
``screen.player_count``, ``screen.player_races``, etc. keep working.

Two-stage ``__init__`` per PROJ-325 PoC + PROJ-328 Phase A:

1. Cheap state + delegate construction runs *before* the
   ``bypass_init`` guard, so test instances built under
   ``with bypass_init(NewGameSetupScreen):`` still have real
   delegates (``_view_model``, ``_controller``) populated.
2. The ``UIWindow`` shell + widget tree run *after* the guard.
   Bypassed instances skip the heavy ``pygame_gui`` calls.
"""
from __future__ import annotations

import logging
from typing import Callable, List, Optional, TYPE_CHECKING

import pygame
import pygame_gui

from game.ui.colors import TEXT_ERROR
from game.strategy.engine.game_config import (
    GameConfig,
    THEME_DEFAULTS,
    VALID_GALAXY_TYPES,
    DEFAULT_SYSTEM_COUNT,
    MIN_SYSTEM_COUNT,
    MAX_SYSTEM_COUNT,
)
from game.strategy.systems.race_library import RaceLibrary
from game.ui.screens.new_game_setup_controller import NewGameSetupController
from game.ui.screens.new_game_setup_ui_builder import NewGameSetupUiBuilder
from game.ui.screens.new_game_setup_view_model import (
    DEFAULT_GALAXY_TYPE,
    DEFAULT_PLAYER_COUNT,
    MAX_PLAYER_SLOTS,
    NewGameSetupViewModel,
)

if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig


logger = logging.getLogger(__name__)


# FEAT-27: the underlying pygame_gui slider runs over an integer
# 0..SLIDER_T_MAX range. The visible system_count is derived from the
# slider position via a quadratic curve so dragging is fine-grained at
# the low end (1->2->3 selectable) and coarser at the high end.
SLIDER_T_MAX: int = 1000


def system_count_slider_curve(t: int) -> int:
    """Map an internal slider position ``t`` (0..SLIDER_T_MAX) to a
    galaxy ``system_count`` in the closed range
    ``[MIN_SYSTEM_COUNT, MAX_SYSTEM_COUNT]`` using a quadratic curve.

    ``value = MIN + (MAX - MIN) * (t/T_MAX)**2``, clamped on both ends.

    The quadratic is concave-up, so equal slider increments at the low
    end yield small system_count changes (fine-grained) while equal
    increments at the high end yield larger changes (coarse).
    """
    if t <= 0:
        return MIN_SYSTEM_COUNT
    if t >= SLIDER_T_MAX:
        return MAX_SYSTEM_COUNT
    span = MAX_SYSTEM_COUNT - MIN_SYSTEM_COUNT
    normalized = t / SLIDER_T_MAX
    raw = MIN_SYSTEM_COUNT + span * (normalized ** 2)
    return max(MIN_SYSTEM_COUNT, min(MAX_SYSTEM_COUNT, int(round(raw))))


def system_count_slider_inverse(value: int) -> int:
    """Inverse of ``system_count_slider_curve`` — used to position the
    slider thumb when initialising the UI from a default ``system_count``.
    """
    if value <= MIN_SYSTEM_COUNT:
        return 0
    if value >= MAX_SYSTEM_COUNT:
        return SLIDER_T_MAX
    span = MAX_SYSTEM_COUNT - MIN_SYSTEM_COUNT
    normalized = ((value - MIN_SYSTEM_COUNT) / span) ** 0.5
    return int(round(normalized * SLIDER_T_MAX))


class NewGameSetupScreen(pygame_gui.elements.UIWindow):
    """Window for configuring a new game.

    Thin shell over a view model + controller + UI builder; see module
    docstring for the MVVM split rationale.
    """

    def __init__(
        self,
        rect,
        manager,
        on_start_callback: Callable[[GameConfig], None],
        on_cancel_callback: Callable[[], None],
        *,
        ui_builder: Optional[NewGameSetupUiBuilder] = None,
        view_model: Optional[NewGameSetupViewModel] = None,
        controller: Optional[NewGameSetupController] = None,
    ):
        """Create new game setup window.

        Args:
            rect: Window rectangle.
            manager: ``pygame_gui`` UIManager.
            on_start_callback: Callback(``GameConfig``) when user
                starts game.
            on_cancel_callback: Callback() when user cancels.
            ui_builder: PROJ-328 Phase B — UI builder seam. Defaults to
                ``NewGameSetupUiBuilder`` (production widget
                construction). Tests can pass
                ``NullNewGameSetupUiBuilder`` /
                ``MockNewGameSetupUiBuilder`` from
                ``tests/fixtures/new_game_setup_ui_builder.py``.
            view_model: PROJ-328 Phase B — view-model seam. Defaults to
                ``NewGameSetupViewModel(...)`` with the current
                defaults. Tests typically let the screen build its own
                and then mutate it.
            controller: PROJ-328 Phase B — controller seam. Defaults to
                ``NewGameSetupController(...)`` wired against the
                view model + race library + the supplied callbacks.
        """
        # ---- Stage 1: cheap state + widget-ref placeholders + delegates ----
        self._init_state(
            on_start_callback=on_start_callback,
            on_cancel_callback=on_cancel_callback,
        )
        self._init_widget_refs()

        self._view_model = view_model or NewGameSetupViewModel()
        self._controller = controller or NewGameSetupController(
            screen=self,
            view_model=self._view_model,
            race_library=self.race_library,
            on_start_callback=on_start_callback,
            on_cancel_callback=on_cancel_callback,
        )

        # ---- Stage 2: UIWindow shell (skipped under bypass_init) ----
        # PROJ-324 Phase 1 / PROJ-328 Phase B: opt-in test escape
        # hatch. When a test sets ``Cls.bypass_init = True`` (preferably
        # via ``tests.fixtures.ui_widget_factory.bypass_init``), skip
        # the heavy ``UIWindow.__init__`` chain.
        if getattr(type(self), 'bypass_init', False):
            self.ui_manager = manager
            self._window_init_bypassed = True
            # Stage 3 (test branch): give the (test-supplied) builder a
            # chance to populate widget slots without a real UIWindow
            # shell. PROJ-325 PoC finding 2 — Mock builders are useless
            # without this hook.
            # NOTE: do not assign ``self.rect``. ``pygame_gui``'s
            # ``GUISprite`` base class makes ``rect`` a descriptor that
            # mutates ``self.blit_data`` on write, and ``blit_data``
            # is initialized only by the ``pygame.sprite.Sprite.__init__``
            # chain that ``bypass_init`` skips. (PROJ-325 PoC finding 1.)
            if ui_builder is not None:
                ui_builder.build(self)
            return

        super().__init__(
            rect,
            manager,
            window_display_title="New Game Setup",
            object_id="#new_game_setup_window",
            resizable=False,
        )
        # PROJ-347 T4.6: mirror StrategyModalWindow base — production
        # paths set ``_window_init_bypassed = False`` so the flag is
        # always defined (tests and call sites can rely on it without
        # ``getattr(..., False)`` everywhere).
        self._window_init_bypassed = False

        # ---- Stage 3 (production): widget tree ----
        (ui_builder or NewGameSetupUiBuilder()).build(self)

    # ------------------------------------------------------------------
    # Stage 1 helpers — cheap state
    # ------------------------------------------------------------------

    def _init_state(
        self,
        *,
        on_start_callback: Callable[[GameConfig], None],
        on_cancel_callback: Callable[[], None],
    ) -> None:
        """Assign cheap state — no ``pygame_gui`` widget construction.

        Called from ``__init__`` *before* the ``bypass_init`` guard so
        test-mode instances see the same race_library / callback wiring
        as production.
        """
        # Race library is cheap (no pygame imports / file IO at
        # construction time per PROJ-287; loads lazily on first read).
        self.race_library = RaceLibrary()

        # Backwards-compat: existing tests / code read these directly.
        self.on_start_callback = on_start_callback
        self.on_cancel_callback = on_cancel_callback

    def _init_widget_refs(self) -> None:
        """Assign every widget slot to ``None`` / empty container.

        Per the consensus refactor plan: prefer explicit placeholder
        initialization over lazy properties. Bypassed instances are
        then honest — widget tree absent, cheap delegates present.
        """
        # Top-level widgets — populated by the production UI builder.
        self.save_name_input: Optional[pygame_gui.elements.UITextEntryLine] = None
        self.player_count_dropdown: Optional[pygame_gui.elements.UIDropDownMenu] = None
        self.galaxy_type_dropdown: Optional[pygame_gui.elements.UIDropDownMenu] = None
        self.system_count_slider: Optional[pygame_gui.elements.UIHorizontalSlider] = None
        self.system_count_label: Optional[pygame_gui.elements.UILabel] = None
        self.btn_start: Optional[pygame_gui.elements.UIButton] = None
        self.btn_cancel: Optional[pygame_gui.elements.UIButton] = None
        self.error_label: Optional[pygame_gui.elements.UILabel] = None

        # Per-player row widgets — always allocate ``MAX_PLAYER_SLOTS``,
        # toggle visibility via ``_update_empire_visibility``.
        self.empire_name_inputs: List = []
        self.theme_labels: List = []
        self.num_labels: List = []
        self.race_preview_labels: List = []
        self.load_race_buttons: List = []
        self.setup_race_buttons: List = []

        # ``empire_inputs_start_y`` is a layout-state int set by the
        # production ``_create_ui`` and read by ``_create_empire_inputs``.
        # Keep a placeholder here for parity with the bypass branch.
        self.empire_inputs_start_y: int = 0

    # ------------------------------------------------------------------
    # UI construction — invoked by ``NewGameSetupUiBuilder.build``.
    # ------------------------------------------------------------------

    def _create_ui(self) -> None:
        """Create UI elements."""
        container = self.get_container()
        content_width = container.get_size()[0] - 20
        y_offset = 10

        # Save name label and input.
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_offset, 150, 25),
            text="Save Name:",
            manager=self.ui_manager,
            container=container,
        )
        y_offset += 25

        self.save_name_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(10, y_offset, content_width, 35),
            manager=self.ui_manager,
            container=container,
            placeholder_text="Enter save name...",
        )
        self.save_name_input.set_text(
            NewGameSetupController.generate_default_save_name()
        )
        y_offset += 45

        # Player count label and dropdown.
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_offset, 150, 25),
            text="Number of Players:",
            manager=self.ui_manager,
            container=container,
        )
        y_offset += 25

        self.player_count_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=[str(n) for n in self.get_player_count_options()],
            starting_option=str(DEFAULT_PLAYER_COUNT),
            relative_rect=pygame.Rect(10, y_offset, 100, 35),
            manager=self.ui_manager,
            container=container,
        )
        y_offset += 50

        # Galaxy type label and dropdown.
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_offset, 150, 25),
            text="Galaxy Type:",
            manager=self.ui_manager,
            container=container,
        )
        y_offset += 25

        # Sort galaxy types for consistent display.
        galaxy_types = sorted(list(VALID_GALAXY_TYPES))
        self.galaxy_type_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=galaxy_types,
            starting_option=self._view_model.galaxy_type,
            relative_rect=pygame.Rect(10, y_offset, 150, 35),
            manager=self.ui_manager,
            container=container,
        )
        y_offset += 50

        # Star system count label, slider, and value display.
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_offset, 150, 25),
            text="Star Systems:",
            manager=self.ui_manager,
            container=container,
        )
        y_offset += 25

        # FEAT-27: source the default from GameConfig (single source of
        # truth) and drive the slider over an internal 0..SLIDER_T_MAX
        # range. The visible system_count is derived via the quadratic
        # ``system_count_slider_curve``.
        self._view_model.system_count = DEFAULT_SYSTEM_COUNT
        self.system_count_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(10, y_offset, content_width - 60, 30),
            start_value=system_count_slider_inverse(self._view_model.system_count),
            value_range=(0, SLIDER_T_MAX),
            manager=self.ui_manager,
            container=container,
            click_increment=1,
        )
        self.system_count_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(content_width - 40, y_offset, 50, 30),
            text=str(self._view_model.system_count),
            manager=self.ui_manager,
            container=container,
        )
        y_offset += 45

        # Empire/Race section header.
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_offset, content_width, 25),
            text="Player Species:",
            manager=self.ui_manager,
            container=container,
        )
        y_offset += 30

        # Create empire name inputs with race selection.
        self.empire_inputs_start_y = y_offset
        self._create_empire_inputs()

        # Calculate button position at bottom.
        button_y = container.get_size()[1] - 60
        button_width = 120

        self.btn_start = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, button_y, button_width, 40),
            text="Start Game",
            manager=self.ui_manager,
            container=container,
        )

        self.btn_cancel = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                content_width - button_width + 10, button_y, button_width, 40
            ),
            text="Cancel",
            manager=self.ui_manager,
            container=container,
        )

        # Error label (hidden by default).
        self.error_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, button_y - 30, content_width, 25),
            text="",
            manager=self.ui_manager,
            container=container,
        )
        self.error_label.text_colour = pygame.Color(*TEXT_ERROR)

    def _create_empire_inputs(self) -> None:
        """Create empire name input fields with race selection for each
        player slot."""
        container = self.get_container()
        y_offset = self.empire_inputs_start_y

        # Clear existing elements.
        for inp in self.empire_name_inputs:
            inp.kill()
        for lbl in self.theme_labels:
            lbl.kill()
        for lbl in self.num_labels:
            lbl.kill()
        for lbl in self.race_preview_labels:
            lbl.kill()
        for btn in self.load_race_buttons:
            btn.kill()
        for btn in self.setup_race_buttons:
            btn.kill()

        self.empire_name_inputs = []
        self.theme_labels = []
        self.num_labels = []
        self.race_preview_labels = []
        self.load_race_buttons = []
        self.setup_race_buttons = []

        # Row height for each player (name row + race row + spacing).
        row_height = 95

        for i in range(MAX_PLAYER_SLOTS):
            row_y = y_offset + (i * row_height)

            num_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, row_y, 80, 30),
                text=f"Player {i + 1}:",
                manager=self.ui_manager,
                container=container,
            )
            self.num_labels.append(num_label)

            # Name input (hidden when race selected — race name becomes
            # empire name).
            name_input = pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect(90, row_y, 200, 30),
                manager=self.ui_manager,
                container=container,
                placeholder_text=f"Empire {i + 1}",
            )
            self.empire_name_inputs.append(name_input)

            # Theme label (auto-assigned, shows race theme when selected).
            theme_name = THEME_DEFAULTS[i][0]
            theme_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(300, row_y, 200, 30),
                text=f"Theme: {theme_name}",
                manager=self.ui_manager,
                container=container,
            )
            self.theme_labels.append(theme_label)

            # Race selection row (below name row).
            race_row_y = row_y + 35

            # Race preview label.
            race_preview = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(90, race_row_y, 280, 30),
                text="No species selected (using defaults)",
                manager=self.ui_manager,
                container=container,
            )
            self.race_preview_labels.append(race_preview)

            # Load Race button.
            load_btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(380, race_row_y, 100, 30),
                text="Load Species",
                manager=self.ui_manager,
                container=container,
            )
            self.load_race_buttons.append(load_btn)

            # Setup Race button.
            setup_btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(490, race_row_y, 110, 30),
                text="Setup Species",
                manager=self.ui_manager,
                container=container,
            )
            self.setup_race_buttons.append(setup_btn)

        # Update visibility based on current player count.
        self._update_empire_visibility()

    def _update_empire_visibility(self) -> None:
        """Show/hide empire inputs based on player count."""
        for i in range(MAX_PLAYER_SLOTS):
            visible = i < self._view_model.player_count
            elements = [
                self.empire_name_inputs[i],
                self.theme_labels[i],
                self.num_labels[i],
                self.race_preview_labels[i],
                self.load_race_buttons[i],
                self.setup_race_buttons[i],
            ]
            for elem in elements:
                if visible:
                    elem.show()
                else:
                    elem.hide()

            # Clear race selection for hidden players.
            if not visible and self._view_model.get_race(i) is not None:
                self._view_model.clear_race(i)
                self._update_race_display(i)

    def _update_race_display(self, player_index: int) -> None:
        """Update the race preview display for a player."""
        race = self._view_model.get_race(player_index)

        if race:
            # Race selected — show faction name (or race name fallback).
            display_name = race.faction_name if race.faction_name else race.name
            self.race_preview_labels[player_index].set_text(
                f"Species: {display_name}"
            )
            details = []
            if race.government_type:
                details.append(race.government_type)
            if race.society_type:
                details.append(race.society_type)
            if details:
                self.theme_labels[player_index].set_text(" • ".join(details))
            else:
                self.theme_labels[player_index].set_text(f"Theme: {race.theme_id}")
            # Hide name input — race name will be used.
            self.empire_name_inputs[player_index].hide()
        else:
            # No race — show default state.
            self.race_preview_labels[player_index].set_text(
                "No species selected (using defaults)"
            )
            default_theme = THEME_DEFAULTS[player_index][0]
            self.theme_labels[player_index].set_text(f"Theme: {default_theme}")
            # Show name input for manual entry.
            if player_index < self._view_model.player_count:
                self.empire_name_inputs[player_index].show()

    # ------------------------------------------------------------------
    # Event dispatch
    # ------------------------------------------------------------------

    def process_event(self, event: pygame.event.Event) -> bool:
        """Process pygame events.

        BUG-115: No modal-active early-return guard. ``pygame_gui``
        z-orders child windows above the parent and dispatches to them
        first, so the modal already gets first crack at events. The
        previous guard silently swallowed all parent button events
        whenever ``active_race_modal`` was stale (e.g., the modal was
        killed via title-bar [X] without invoking its cancel callback),
        making Cancel / Start permanently dead.
        """
        handled = super().process_event(event)

        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.player_count_dropdown:
                self._view_model.set_player_count(int(event.text))
                self._update_empire_visibility()
                handled = True
            elif event.ui_element == self.galaxy_type_dropdown:
                self._view_model.galaxy_type = event.text
                handled = True

        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.system_count_slider:
                # FEAT-27: slider runs over 0..SLIDER_T_MAX; convert to
                # a real galaxy size via the quadratic curve.
                self._view_model.system_count = system_count_slider_curve(
                    int(event.value)
                )
                self.system_count_label.set_text(
                    str(self._view_model.system_count)
                )
                handled = True

        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_start:
                self._on_start_clicked()
                handled = True
            elif event.ui_element == self.btn_cancel:
                self._on_cancel_clicked()
                handled = True
            else:
                for i, btn in enumerate(self.load_race_buttons):
                    if event.ui_element == btn:
                        self._on_load_race_clicked(i)
                        handled = True
                        break

                for i, btn in enumerate(self.setup_race_buttons):
                    if event.ui_element == btn:
                        self._on_setup_race_clicked(i)
                        handled = True
                        break

        return handled

    # ------------------------------------------------------------------
    # Backwards-compat thin wrappers — delegate to the controller.
    # Existing tests reach into these private methods directly; keep
    # them as one-liners on the screen so test reach-throughs survive.
    # ------------------------------------------------------------------

    def _on_load_race_clicked(self, player_index: int) -> None:
        self._controller.on_load_race_clicked(player_index)

    def _on_setup_race_clicked(self, player_index: int) -> None:
        self._controller.on_setup_race_clicked(player_index)

    def _on_race_selected(
        self, player_index: int, race_config: "RaceConfig"
    ) -> None:
        self._controller.on_race_selected(player_index, race_config)

    def _on_race_created(
        self, player_index: int, race_config: "RaceConfig"
    ) -> None:
        self._controller.on_race_created(player_index, race_config)

    def _on_race_dialog_cancelled(self) -> None:
        self._controller.on_race_dialog_cancelled()

    def _on_start_clicked(self) -> None:
        self._controller.on_start_clicked()

    def _on_cancel_clicked(self) -> None:
        self._controller.on_cancel_clicked()

    # ------------------------------------------------------------------
    # Static methods — back-compat surface for existing callers / tests.
    # PROJ-392 dropped the ``validate_save_name`` /
    # ``generate_default_save_name`` shims; call
    # ``NewGameSetupController.validate_save_name(...)`` /
    # ``NewGameSetupController.generate_default_save_name(...)`` directly.
    # ------------------------------------------------------------------

    @staticmethod
    def get_player_count_options() -> List[int]:
        """Get available player count options."""
        return [1, 2, 3, 4]

    @staticmethod
    def build_game_config(
        save_name: str,
        player_count: int,
        empire_names: List[str],
        race_configs: Optional[List[Optional["RaceConfig"]]] = None,
        galaxy_type: str = DEFAULT_GALAXY_TYPE,
        system_count: int = DEFAULT_SYSTEM_COUNT,
    ) -> GameConfig:
        """Build a ``GameConfig`` from setup-screen values. See
        ``NewGameSetupController.build_game_config``."""
        return NewGameSetupController.build_game_config(
            save_name=save_name,
            player_count=player_count,
            empire_names=empire_names,
            race_configs=race_configs,
            galaxy_type=galaxy_type,
            system_count=system_count,
        )

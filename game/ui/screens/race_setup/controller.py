"""PROJ-309 Sub-phase 3.1 — RaceSetupController.

Owns every mutation that flows into `race_config` and every call into
the race library or registry. Handles the FEAT-05 save flow
(overwrite-vs-new), the load flow, validation, and the per-tab + master
randomization dispatch.

Per `docs/03_CONVENTIONS.md §2.4`, this controller's concentrated
mutation surface (~17 mutation methods + save/load + validation) is a
legitimate justification for >300 LOC; the strict cap remains 500 LOC.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional, Tuple

import pygame

from game.strategy.data.race_config import RaceConfig
from game.strategy.systems.race_library import RaceLibrary
from game.strategy.systems.race_randomizer import RaceRandomizer
from game.ui.screens.race_browser_dialog import RaceBrowserDialog
from game.ui.screens.race_validator import RaceValidator

if TYPE_CHECKING:
    from game.core.protocols import IRaceRegistry
    from game.ui.screens.race_setup.renderer import RaceSetupRenderer
    from game.ui.screens.race_setup.screen import RaceSetupScreen
    from game.ui.screens.race_setup.view_model import RaceSetupViewModel
    from game.strategy.services.race_description_llm_controller import (
        RaceDescriptionLLMController,
    )

logger = logging.getLogger(__name__)


class RaceSetupController:
    """Race setup mutation surface + lifecycle."""

    def __init__(
        self,
        *,
        screen: "RaceSetupScreen",
        view_model: "RaceSetupViewModel",
        renderer: "RaceSetupRenderer",
        race_config: RaceConfig,
        race_library: RaceLibrary,
        race_registry: Optional["IRaceRegistry"] = None,
        on_complete_callback=None,
        on_cancel_callback=None,
    ) -> None:
        self._screen = screen
        self._vm = view_model
        self._renderer = renderer

        self.race_config = race_config
        self.race_library = race_library
        # PROJ-287: optional session-scoped registry; do_save() invalidates
        # the cached entry after a successful save.
        self.race_registry = race_registry

        self.on_complete_callback = on_complete_callback
        self.on_cancel_callback = on_cancel_callback

        # PROJ-299 LLM description controller (assigned by Screen during
        # descriptions-tab construction).
        self._description_controller: Optional[
            "RaceDescriptionLLMController"
        ] = None

    # ------------------------------------------------------------------
    # PROJ-299 description controller wiring
    # ------------------------------------------------------------------

    def attach_description_controller(
        self, controller: "RaceDescriptionLLMController"
    ) -> None:
        self._description_controller = controller

    @property
    def description_controller(
        self,
    ) -> Optional["RaceDescriptionLLMController"]:
        return self._description_controller

    def on_description_controller_change(self) -> None:
        """PROJ-299 state-transition callback. Worker-thread safe; only
        mutates the description panel widgets."""
        screen = self._screen
        if screen._description_panel is not None and self._description_controller is not None:
            screen._description_panel.set_state(self._description_controller)

    def update_description_char_counts(self) -> None:
        if self._screen._description_panel:
            self._screen._description_panel.update_char_counts()

    def update_descriptions_from_text(self) -> None:
        if self._screen._description_panel:
            self._screen._description_panel.update_config()

    # ------------------------------------------------------------------
    # Theme selection
    # ------------------------------------------------------------------

    def on_theme_selected(self, theme_id: str) -> None:
        self.race_config.theme_id = theme_id
        logger.debug(f"Theme selected: {theme_id}")
        self._renderer.refresh_ship_preview(theme_id)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_for_save(self) -> Tuple[bool, str]:
        """Validate identity / aptitudes panels into config, then check
        point budget and run RaceValidator.

        PROJ-12 Phase 4: delegates to RaceValidator.
        PROJ-66 Phase 6: identity sync + budget check first."""
        screen = self._screen

        if screen._identity_panel:
            screen._identity_panel.update_config()
            if self.race_config.race_name:
                self.race_config.name = self.race_config.race_name

        if screen._aptitudes_panel:
            screen._aptitudes_panel.update_config()
            from game.strategy.data.race_point_budget import RacePointBudget
            budget = RacePointBudget()
            if not budget.is_within_budget(self.race_config):
                remaining = budget.get_remaining_points(self.race_config)
                return False, f"Over budget by {-remaining} points (Aptitudes tab)"

        validator = RaceValidator()
        result = validator.validate(self.race_config)
        return result.is_valid, result.message

    # ------------------------------------------------------------------
    # Race load flow
    # ------------------------------------------------------------------

    def on_load_race(self) -> None:
        """Open the in-game race browser dialog."""
        logger.debug("Opening race browser dialog")
        screen = self._screen
        window_rect = screen.get_abs_rect()
        dialog_width, dialog_height = 600, 500
        dialog_x = window_rect.centerx - dialog_width // 2
        dialog_y = window_rect.centery - dialog_height // 2
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)

        screen.race_browser = RaceBrowserDialog(
            rect=dialog_rect,
            manager=screen.ui_manager,
            race_library=self.race_library,
            on_select_callback=self.on_race_selected,
            on_cancel_callback=self.on_race_browser_cancelled,
        )

    def on_race_selected(self, loaded_config: RaceConfig) -> None:
        """Replace race_config with a loaded one and resync every panel."""
        logger.info(f"Loaded race: {loaded_config.name}")
        self.race_config = loaded_config
        self._vm.is_editing = True
        # Mirror onto the screen for backwards-compat with tests that
        # read `screen.is_editing` / `screen.race_config`.
        self._screen.is_editing = True
        self._screen.race_config = loaded_config

        self.populate_ui_from_config()

        if self._screen.btn_save:
            self._screen.btn_save.set_text("Update")

    def on_race_browser_cancelled(self) -> None:
        logger.debug("Race browser cancelled")

    def populate_ui_from_config(self) -> None:
        """Refresh every panel from the current race_config.

        PROJ-66 Phase 6: identity + aptitudes panels added.
        BUG-81: update panel `race_config` references first.
        PROJ-299: keep the LLM controller's `race_config` reference in
        sync — without this, the controller writes generated text into
        the orphaned old config (silent data loss)."""
        screen = self._screen
        for panel in [
            screen._identity_panel,
            screen._flag_gallery,
            screen._portrait_gallery,
            screen._theme_gallery,
            screen._environment_panel,
            screen._aptitudes_panel,
            screen._description_panel,
            screen._summary_panel,
        ]:
            if panel is not None:
                panel.race_config = self.race_config

        controller = self._description_controller
        if controller is not None:
            controller.set_race_config(self.race_config)

        if screen._identity_panel:
            screen._identity_panel.set_from_config()
        if screen._flag_gallery:
            screen._flag_gallery.set_from_config()
        if screen._portrait_gallery:
            screen._portrait_gallery.set_from_config()
        if screen._theme_gallery:
            screen._theme_gallery.set_from_config()
        if screen._environment_panel:
            screen._environment_panel.set_from_config()
        if screen._aptitudes_panel:
            screen._aptitudes_panel.set_from_config()
        if screen._description_panel:
            screen._description_panel.set_from_config()
        # BUG-118: the summary panel uses `refresh()`, not
        # `set_from_config()`, so it must be invoked explicitly here.
        # Without this, bulk-update entry points (Randomize All, race
        # load) leave the Summary tab's left-column labels stale until
        # the next tab switch triggers `_refresh_summary()`.
        if screen._summary_panel:
            screen._summary_panel.refresh()

    # ------------------------------------------------------------------
    # Per-tab randomization
    # ------------------------------------------------------------------

    def on_randomize(self) -> None:
        """Generate Random button — dispatches by current tab."""
        from game.ui.screens.race_setup.view_model import (
            TAB_APTITUDES,
            TAB_ENVIRONMENT,
            TAB_IDENTITY,
            TAB_SHIPS,
            TAB_VISUALS,
        )

        step = self._vm.current_step
        if step == TAB_IDENTITY:
            self.randomize_identity()
        elif step == TAB_VISUALS:
            self.randomize_visuals()
        elif step == TAB_SHIPS:
            self.randomize_ships()
        elif step == TAB_ENVIRONMENT:
            self.randomize_environment()
        elif step == TAB_APTITUDES:
            self.randomize_aptitudes()

    def randomize_identity(self) -> None:
        portrait_id = self.race_config.portrait_id or None
        result = RaceRandomizer.randomize_identity(portrait_id=portrait_id)

        self.race_config.race_name = result["race_name"]
        self.race_config.race_name_plural = result["race_name_plural"]
        self.race_config.leader_name = result["leader_name"]
        self.race_config.physical_type = result["physical_type"]
        self.race_config.government_type = result["government_type"]
        self.race_config.government_organization = result["government_organization"]
        self.race_config.leader_title = result["leader_title"]
        self.race_config.society_type = result["society_type"]
        self.race_config.faction_name = result["faction_name"]

        if self._screen._identity_panel:
            self._screen._identity_panel.set_from_config()

        logger.info(f"Randomized identity: {result['race_name']}")

    def randomize_visuals(self) -> None:
        screen = self._screen
        if screen._flag_gallery:
            flag_ids = [a[0] for a in screen._flag_gallery._discover_assets()]
            new_flag = RaceRandomizer.randomize_flag(flag_ids)
            if new_flag:
                self.race_config.flag_id = new_flag
                screen._flag_gallery.set_from_config()

        if screen._portrait_gallery:
            portrait_ids = [a[0] for a in screen._portrait_gallery._discover_assets()]
            new_portrait = RaceRandomizer.randomize_portrait(portrait_ids)
            if new_portrait:
                self.race_config.portrait_id = new_portrait
                screen._portrait_gallery.set_from_config()

        logger.info(
            f"Randomized visuals: flag={self.race_config.flag_id}, "
            f"portrait={self.race_config.portrait_id}"
        )

    def randomize_ships(self) -> None:
        screen = self._screen
        if screen._theme_gallery:
            theme_ids = [a[0] for a in screen._theme_gallery._discover_assets()]
            new_theme = RaceRandomizer.randomize_theme(theme_ids)
            if new_theme:
                self.race_config.theme_id = new_theme
                screen._theme_gallery.set_from_config()
                self._renderer.refresh_ship_preview(new_theme)

        logger.info(f"Randomized ships: theme={self.race_config.theme_id}")

    def randomize_environment(self) -> None:
        """Randomize env preferences within the available budget.

        Available budget = 100 - cost(other categories). If aptitudes /
        reproduction already consume the budget, the randomizer
        rebalances toward registry defaults."""
        from game.strategy.data.race_point_budget import RacePointBudget

        budget_calc = RacePointBudget()
        env_budget = (
            budget_calc.total_budget
            - budget_calc.calculate_aptitude_cost(self.race_config)
        )
        env_budget = max(0, env_budget)

        result = RaceRandomizer.randomize_environment(budget=env_budget)
        self.race_config.preferences = dict(result["preferences"])
        self.race_config.homeworld_type = result["homeworld_type"]
        self.race_config.base_reproduction_rate = result["base_reproduction_rate"]
        self.race_config.base_happiness = result["base_happiness"]

        screen = self._screen
        if screen._environment_panel is not None:
            screen._environment_panel.set_from_config()
        # Aptitudes panel reads preferences-cost via RacePointBudget — refresh
        # its budget display so the user sees the new total cost immediately.
        if screen._aptitudes_panel is not None:
            screen._aptitudes_panel.update_budget_display()

        logger.info(
            f"Randomized environment: homeworld={result['homeworld_type']} "
            f"repro={result['base_reproduction_rate']:.4f} "
            f"happiness={result['base_happiness']:.2f}"
        )

    def randomize_aptitudes(self) -> None:
        """Randomize the 7 paid aptitudes within the available budget."""
        from game.strategy.data.race_point_budget import RacePointBudget

        budget_calc = RacePointBudget()
        apt_budget = (
            budget_calc.total_budget
            - budget_calc.calculate_preferences_cost(self.race_config)
            - budget_calc.calculate_reproduction_cost(
                self.race_config.base_reproduction_rate
            )
        )
        apt_budget = max(0, apt_budget)

        aptitudes = RaceRandomizer.randomize_aptitudes(budget=apt_budget)
        for name, value in aptitudes.items():
            setattr(self.race_config, f"aptitude_{name}", value)

        if self._screen._aptitudes_panel is not None:
            self._screen._aptitudes_panel.set_from_config()

        logger.info(f"Randomized aptitudes: {aptitudes}")

    def randomize_all(self) -> None:
        """Master "Randomize All" — every category except Description."""
        screen = self._screen
        flag_ids = (
            [a[0] for a in screen._flag_gallery._discover_assets()]
            if screen._flag_gallery
            else []
        )
        portrait_ids = (
            [a[0] for a in screen._portrait_gallery._discover_assets()]
            if screen._portrait_gallery
            else []
        )
        theme_ids = (
            [a[0] for a in screen._theme_gallery._discover_assets()]
            if screen._theme_gallery
            else []
        )

        result = RaceRandomizer.randomize_all(
            available_flags=flag_ids,
            available_portraits=portrait_ids,
            available_themes=theme_ids,
        )

        # Identity
        self.race_config.race_name = result["race_name"]
        self.race_config.race_name_plural = result["race_name_plural"]
        self.race_config.leader_name = result["leader_name"]
        self.race_config.physical_type = result["physical_type"]
        self.race_config.government_type = result["government_type"]
        self.race_config.government_organization = result["government_organization"]
        self.race_config.leader_title = result["leader_title"]
        self.race_config.society_type = result["society_type"]
        self.race_config.faction_name = result["faction_name"]
        # `name` mirrors race_name (matches validate_for_save contract).
        self.race_config.name = result["race_name"]

        # Visuals
        self.race_config.flag_id = result["flag_id"]
        self.race_config.portrait_id = result["portrait_id"]
        self.race_config.theme_id = result["theme_id"]

        # Environment
        self.race_config.preferences = dict(result["preferences"])
        self.race_config.homeworld_type = result["homeworld_type"]
        self.race_config.base_reproduction_rate = result["base_reproduction_rate"]
        self.race_config.base_happiness = result["base_happiness"]

        # Aptitudes
        for name, value in result["aptitudes"].items():
            setattr(self.race_config, f"aptitude_{name}", value)

        self.populate_ui_from_config()
        if self.race_config.theme_id:
            self._renderer.refresh_ship_preview(self.race_config.theme_id)

        logger.info(
            f"Randomized all: {result['race_name']} on {result['homeworld_type']}"
        )

    # ------------------------------------------------------------------
    # Cancel + save flow
    # ------------------------------------------------------------------

    def on_cancel(self) -> None:
        logger.debug("Race setup cancelled")
        if self.on_cancel_callback is not None:
            self.on_cancel_callback()
        self._screen.kill()

    def on_save(self) -> None:
        """FEAT-05: when editing a loaded species, prompt overwrite-vs-new."""
        screen = self._screen

        is_valid, error = self.validate_for_save()
        if not is_valid:
            screen.error_label.set_text(error)
            return

        validation_result = self.race_config.validate()
        if not validation_result.is_valid:
            logger.warning(
                f"Saving race with validation warnings: {validation_result.message}"
            )

        if self._vm.is_editing and self.race_config.race_id:
            self._renderer.show_save_update_dialog()
            return

        self.do_save()

    def do_save(self) -> None:
        """Execute the actual save to library."""
        screen = self._screen
        success, message = self.race_library.save_race(self.race_config)
        if success:
            logger.info(f"Race saved: {self.race_config.name}")
            if self.race_registry is not None:
                self.race_registry.invalidate(self.race_config.race_id)
            if self.on_complete_callback is not None:
                self.on_complete_callback(self.race_config)
            screen.kill()
        else:
            screen.error_label.set_text(message)

    def on_overwrite_save(self) -> None:
        """FEAT-05: Overwrite existing species (keep race_id)."""
        self._renderer.close_save_update_dialog()
        self.do_save()

    def on_save_as_new(self) -> None:
        """FEAT-05: Save as new species (clear race_id)."""
        self._renderer.close_save_update_dialog()
        self.race_config.race_id = None
        self._vm.is_editing = False
        self._screen.is_editing = False
        if self._screen.btn_save:
            self._screen.btn_save.set_text("Save")
        self.do_save()

    def on_save_dialog_cancel(self) -> None:
        """FEAT-05: Cancel save dialog — return to editing."""
        self._renderer.close_save_update_dialog()

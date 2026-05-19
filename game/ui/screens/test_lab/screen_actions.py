"""Test-lab screen actions: battle launch + execution + result viewers.

PROJ-457 Phase 3: extracted from `test_lab/screen.py` to bring the
screen back under the 500-LOC ceiling. Contains:

* Battle execution helpers: `_render_progress`, `_draw_and_flip`,
  `_require_display_surface`, `_get_engine`, `_ensure_engine`.
* Battle launch: `_switch_to_battle`.
* Run callbacks: `_on_run`, `_on_run_visual_baseline`,
  `_on_run_headless`, `_on_run_all_tests`, `_continue_batch_test`.
* Result viewers: `_on_view_battle_states`, `_on_use_seed_from_run`,
  `_on_copy_results`, `_prompt_for_custom_seed`, `_show_ships_json`,
  `_show_components_json`.

The class holds a reference back to the screen and reads/writes screen
state through it. The screen wires the `_executor` and `_input_handler`
callbacks to methods on this class.
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

import pygame

from combat_lab.logging_config import get_logger
from game.core.config import DisplayConfig
from game.core.json_utils import load_json
from game.core.string_utils import display_name
from game.ui.fonts import FONT_MONO, get_font
from game.ui.screens.test_lab import theme
from game.ui.screens.test_lab.data_extractor import get_test_data_dir
from game.ui.screens.test_lab.dialogs import JSONPopup

if TYPE_CHECKING:
    from game.ui.screens.test_lab.screen import TestLabScreen


WIDTH, HEIGHT = DisplayConfig.DEFAULT_WIDTH, DisplayConfig.DEFAULT_HEIGHT


logger = get_logger(__name__)


class TestLabScreenActions:
    """Owns test execution + result viewing for `TestLabScreen`."""

    def __init__(self, screen: "TestLabScreen") -> None:
        self._s = screen

    # ─────────────────────────────────────────────────────────────────
    # Executor callback helpers
    # ─────────────────────────────────────────────────────────────────

    def _render_progress(self, title, subtitle, detail) -> None:
        """Render a progress overlay for headless test execution."""
        s = self._s
        overlay = pygame.Surface((600, 200))
        overlay.fill(theme.BG_OVERLAY)
        pygame.draw.rect(overlay, theme.BORDER_ACTIVE, overlay.get_rect(), 3)

        header_font = get_font(24, FONT_MONO)
        body_font = get_font(18, FONT_MONO)
        small_font = get_font(14, FONT_MONO)

        title_text = header_font.render(title, True, theme.TEXT_WHITE)
        sub_text = body_font.render(subtitle, True, theme.TEXT_MUTED)
        detail_text = small_font.render(detail, True, theme.TEXT_DIM)

        overlay.blit(title_text, (300 - title_text.get_width()//2, 50))
        overlay.blit(sub_text, (300 - sub_text.get_width()//2, 90))
        overlay.blit(detail_text, (300 - detail_text.get_width()//2, 130))

        surface = self._require_display_surface()
        screen_center_x = s.screen_width // 2
        screen_center_y = s.screen_height // 2
        surface.blit(overlay, (screen_center_x - 300, screen_center_y - 100))

    def _draw_and_flip(self) -> None:
        """Draw current screen state with progress overlay and flip display."""
        surface = self._require_display_surface()
        surface.fill(theme.BG_PRIMARY)
        self._s.draw(surface)
        pygame.display.flip()

    def _require_display_surface(self) -> pygame.Surface:
        """Return the active pygame display surface or raise.

        `pygame.display.get_surface()` returns None if `set_mode` has not
        been called. In production this never happens (bootstrap creates
        the display before scenes exist); the explicit check exists so a
        misconfigured unit test surfaces a clear error instead of an opaque
        AttributeError downstream.
        """
        surface = pygame.display.get_surface()
        if surface is None:
            raise RuntimeError(
                "Display surface not initialized; "
                "TestLabScreen progress rendering requires "
                "pygame.display.set_mode() to have been called."
            )
        return surface

    def _get_engine(self) -> Any:
        """Get the battle engine from battle scene."""
        return self._s.battle_scene.engine

    def _ensure_engine(self) -> None:
        """Ensure battle engine exists (create if needed)."""
        s = self._s
        if s.battle_scene.engine is None:
            from game.ai.ai_factory import AIControllerFactory
            s.battle_scene._battle_service.create_battle(
                ai_factory=AIControllerFactory()
            )

    def _switch_to_battle(self, scenario) -> None:
        """Configure a visual-mode battle via the spec compiler + controller.

        PROJ-269 Phase 6 Task 6.9/6.10: the legacy `scenario.setup(engine)`
        path (which force-started the engine and required a
        `_is_started=True` hack) is gone. The flow is now:

          1. `scenario.to_spec()` → BattleSpec.
          2. `scenario.before_run_battle(spec)` (ComparisonScenario baseline).
          3. Materialize ships via `materialize_spec_ships` + scenario's
             `_load_ship` as the ship_builder.
          4. Thread `spec.boundary` + `spec.modifier_stack` onto the engine.
          5. `controller.add_ships` + `controller.start()` — proper
             lifecycle, no hack.
          6. `scenario.wire_ships` + `scenario.custom_setup` post-start.
          7. Hand the started controller to `BattleScreen`.
        """
        from combat_lab.runner import _snapshot_ship_state
        from game.ai.ai_factory import AIControllerFactory
        from combat_lab.spec_compiler import build_test_battle_spec
        from game.simulation.battle_config import BattleConfig
        from game.core.return_destination import ReturnDestination
        from game.simulation.battle_controller import BattleController

        s = self._s

        # 1. Compile + pre-run hook. PROJ-279: explicit composition.
        spec = build_test_battle_spec(scenario, registries=None)
        scenario.before_run_battle(spec)

        # 2. Operational config (spec-driven fields auto-filled by
        # start_from_spec when not overridden here).
        config = BattleConfig(
            start_paused=True,
            return_destination=ReturnDestination.TEST_LAB,
            show_results=True,
            seed=spec.seed,
            end_condition=spec.end_condition,
            absolute_max_ticks=spec.absolute_max_ticks,
        )

        # 3. Pre-snapshot ship state — need ships materialized BEFORE
        # start_from_spec drives start_teams (for role-keyed initial state).
        # PROJ-274: use the context materializer (DesignOnlyMaterializer
        # installed by Combat Lab's TestRunner) instead of a per-call
        # closure.
        # PROJ-306: pass `registry_provider` explicitly — UI is outside
        # the Simulation layer and is allowed to call
        # `get_default_registry_provider()`.
        from game.core.registry import get_default_registry_provider
        from game.simulation.battle_runner import (
            build_context_ship_builder,
            materialize_spec_ships,
        )
        registry_provider = get_default_registry_provider()
        _pre_teams, pre_ships_by_role = materialize_spec_ships(
            spec,
            ship_builder=build_context_ship_builder(
                registry_provider=registry_provider,
            ),
        )
        initial_state = {
            role: _snapshot_ship_state(ship)
            for role, ship in pre_ships_by_role.items()
        }

        # 4. PROJ-270 Phase 10 + PROJ-274: start via unified spec-in path
        # with context materializer. `start_from_spec` calls
        # `materialize_spec_ships` again internally; the DesignOnlyMaterializer
        # loads ships deterministically per design_id so this is safe.
        controller = BattleController()
        _result, ships_by_role = controller.start_from_spec(
            spec,
            ai_factory=AIControllerFactory(),
            registry_provider=registry_provider,
            config=config,
        )
        engine = controller.service.get_engine()

        # 5. Wire ships + run scenario-specific custom setup post-start.
        scenario._effective_seed = spec.seed
        scenario.wire_ships(
            ships_by_role, engine=engine, initial_state=initial_state,
        )
        scenario.custom_setup(engine)

        # 7. Hand to BattleScreen for per-frame ticking.
        s.battle_scene.start_battle(controller)

        if s.scene_callback:
            s.scene_callback("start_test_battle", scenario=scenario)

    def _on_view_battle_states(self, run_record, run_number) -> None:
        """Open the battle state viewer for a test run."""
        from combat_lab.battle_state_capture import load_battle_state_json

        s = self._s
        initial_json = None
        final_json = None

        if run_record.initial_state_file:
            initial_json = load_battle_state_json(run_record.initial_state_file)
        if run_record.final_state_file:
            final_json = load_battle_state_json(run_record.final_state_file)

        if initial_json or final_json:
            s.battle_state_viewer.show(
                initial_json=initial_json,
                final_json=final_json,
                test_id=s.selected_test_id,
                run_number=run_number
            )
        else:
            s.output_log.append("ERROR: Could not load battle state files")

    def _on_use_seed_from_run(self, seed) -> None:
        """Copy the seed from a test run to the custom seed control."""
        s = self._s
        s.controller.ui_state.set_custom_seed(seed)
        s.output_log.append(f"Seed set to: {seed}")

    def _on_copy_results(self, run_record, run_number) -> None:
        """Copy test results to clipboard."""
        s = self._s
        lines = []
        lines.append(f"Test: {s.selected_test_id}")
        lines.append(f"Run #{run_number} - {run_record.get_formatted_timestamp()}")
        lines.append(f"Status: {'PASSED' if run_record.passed else 'FAILED'}")
        if run_record.seed is not None:
            lines.append(f"Seed: {run_record.seed}")
        lines.append("")

        lines.append("=== Test Metrics ===")
        for key, value in run_record.metrics.items():
            if key not in ['validation_results', 'validation_summary']:
                if isinstance(value, float):
                    value_str = f"{value:.4f}"
                else:
                    value_str = str(value)
                display_key = display_name(key)
                lines.append(f"  {display_key}: {value_str}")
        lines.append("")

        if run_record.validation_results:
            lines.append("=== Validation Results ===")
            for vr in run_record.validation_results:
                status = vr['status']
                name = vr['name']
                symbol = "V" if status == 'PASS' else "X"
                lines.append(f"{symbol} {name}: {status}")

        try:
            result_text = "\n".join(lines)
            pygame.scrap.init()
            pygame.scrap.put(pygame.SCRAP_TEXT, result_text.encode('utf-8'))
            s.output_log.append("Test results copied to clipboard")
        except pygame.error as e:
            s.output_log.append(f"Failed to copy to clipboard: {e}")

    def _on_run(self) -> None:
        """Run the selected test scenario visually in Combat Lab."""
        s = self._s
        s._executor.run_visual(s.selected_test_id)

    def _on_run_visual_baseline(self) -> None:
        """Run the baseline battle of a ComparisonScenario visually."""
        s = self._s
        s._executor.run_visual_baseline(s.selected_test_id)

    def _on_run_headless(self) -> None:
        """Run the selected test scenario in headless mode (fast, no visuals)."""
        s = self._s
        s.headless_running = True
        s._executor.run_headless(s.selected_test_id)
        s.headless_running = False
        # Refresh results panel if it exists
        if s._viewmodel.results_panel:
            s._viewmodel.results_panel.set_test(s.selected_test_id)

    def _on_run_all_tests(self) -> None:
        """Run all visible tests headlessly in sequence."""
        s = self._s
        s._executor.run_all(s._get_filtered_scenarios())

    def _continue_batch_test(self) -> None:
        """Continue batch execution (called from event handler)."""
        self._s._executor.continue_batch()

    def _prompt_for_custom_seed(self) -> None:
        """Prompt user to enter a custom seed value."""
        import tkinter as tk
        from tkinter import simpledialog

        s = self._s

        # Create a hidden root window
        root = tk.Tk()
        root.withdraw()

        # Get current custom seed for default value
        current_seed = s.controller.ui_state.get_custom_seed()
        default_val = str(current_seed) if current_seed is not None else ""

        # Show input dialog
        result = simpledialog.askstring(
            "Custom Seed",
            "Enter seed value (integer):",
            initialvalue=default_val,
            parent=root
        )

        root.destroy()

        # Process result
        if result is not None:
            try:
                seed_value = int(result.strip())
                s.controller.ui_state.set_custom_seed(seed_value)
                s.output_log.append(f"Custom seed set to: {seed_value}")
            except ValueError:
                s.output_log.append(f"Invalid seed value: {result}")

    def _show_ships_json(self, test_id) -> None:
        """Show JSON for all ships used in the test."""
        s = self._s
        if test_id is None:
            return

        scenario_info = s.registry.get_by_id(test_id)
        if not scenario_info:
            return

        ships_data = {}
        metadata = scenario_info['metadata']

        ship_files = []
        for condition in metadata.conditions:
            if '.json' in condition and ('Attacker:' in condition or 'Target:' in condition):
                parts = condition.split(':')
                if len(parts) > 1:
                    filename = parts[1].strip()
                    ship_files.append(filename)

        data_dir = os.path.join(get_test_data_dir(), 'ships')

        for ship_file in ship_files:
            ship_path = os.path.join(data_dir, ship_file)
            ship_data = load_json(ship_path)
            if ship_data is not None:
                ships_data[ship_file] = ship_data
            elif os.path.exists(ship_path):
                ships_data[ship_file] = "Error loading ship file"

        if not ships_data:
            ships_data = {"error": "No ship files found for this test"}

        popup = JSONPopup(f"Ships JSON - {test_id}", ships_data, WIDTH, HEIGHT, s.ui_manager)
        s._viewmodel.open_json_popup(popup)

    def _show_components_json(self) -> None:
        """Show JSON for all components in the test data."""
        s = self._s
        components_path = os.path.join(get_test_data_dir(), 'components.json')

        components_data = load_json(components_path)
        if components_data is not None:
            popup = JSONPopup("Components JSON", components_data, WIDTH, HEIGHT, s.ui_manager)
        else:
            popup = JSONPopup(
                "Components JSON",
                {"error": "components.json not found or invalid"},
                WIDTH, HEIGHT, s.ui_manager
            )
        s._viewmodel.open_json_popup(popup)

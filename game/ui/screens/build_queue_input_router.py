"""BuildQueueInputRouter — input handling + command dispatch + refresh
delegate for `BuildQueueScreen`.

PROJ-457 Phase 1: extracted from `BuildQueueScreen` to bring the screen
back under the 500-LOC ceiling. The router owns event handling
(`handle_event` + `_handle_*` family), command dispatch
(`_dispatch_*` family), refresh helpers (`_refresh_*`), queue-selection
helpers (`_get_active_queue`, `_on_queue_selection_changed`), modal
helpers (`_apply_tooltips`, `_prompt_target_planet`, `_request_close`),
and the active-player-change flush hook.

The router holds a reference to the screen and reads/writes screen-level
state (panels, controller, renderer, queue_sources, etc.) through that
reference. The screen retains lifecycle methods (`__init__`,
`_validate_params`, `_construct_collaborators`, `_rebuild_panels`,
`open_for_yard`, `hide`, `show`, `is_visible`, `update`, `draw`) plus
the public `handle_event` entry point which delegates to this router.

Construction: `BuildQueueScreen.__init__` instantiates the router
immediately after the shell-state block so the router is ready when
`_construct_collaborators` wires callbacks pointing at the router's
methods.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, List, Optional, Set

import pygame
import pygame_gui

from game.core.input_actions import InputAction
from game.strategy.data.build_queue_source import (
    BuildQueueSource,
    collect_build_queues_at_hex,
)
from game.ui.screens.planet_selection_window import PlanetSelectionWindow

if TYPE_CHECKING:
    from game.ui.screens.build_queue_screen import BuildQueueScreen


logger = logging.getLogger(__name__)


class BuildQueueInputRouter:
    """Owns user input + command dispatch + refresh for `BuildQueueScreen`."""

    def __init__(self, screen: "BuildQueueScreen") -> None:
        self._screen = screen

    # -----------------------------------------------------------------------
    # Queue Selection
    # -----------------------------------------------------------------------

    def _on_queue_selection_changed(
        self,
        active_source: Optional[BuildQueueSource],
        selected_indices: Set[int],
    ) -> None:
        """Handle selection change from BuildQueueSelector."""
        s = self._screen
        s.active_queue_source = active_source
        s.selected_queue_indices = selected_indices

        if active_source is not None:
            s.controller.set_active_queue(active_source)
        else:
            selected_sources = [
                s.queue_sources[i] for i in sorted(selected_indices)
            ]
            s.controller.set_selected_queues(selected_sources)

        self._refresh_queue_display()
        s.renderer.update_queue_header(active_source)
        # FEAT-17: keep the pause-toggle label in sync with the new selection
        s.renderer.refresh_pause_button(active_source)

    def _get_active_queue(self) -> list:
        """Return the active construction queue list."""
        s = self._screen
        if s.active_queue_source is not None:
            return s.active_queue_source.construction_queue
        return s.build_context.construction_queue

    # -----------------------------------------------------------------------
    # Command Dispatch (PROJ-208)
    # -----------------------------------------------------------------------

    def _dispatch_add_to_queue_command(
        self,
        entity_id: int,
        entity_type: str,
        design_id: str,
        category: str,
        index: Optional[int],
        target_planet_id: Optional[int],
        queue_id: Optional[str],
    ) -> None:
        """Dispatch AddToConstructionQueueCommand through command pipeline."""
        from game.strategy.engine.commands import AddToConstructionQueueCommand
        cmd = AddToConstructionQueueCommand(
            entity_id=entity_id,
            entity_type=entity_type,
            design_id=design_id,
            category=category,
            index=index,
            target_planet_id=target_planet_id,
            queue_id=queue_id,
        )
        # PROJ-382 Phase 1: facade is required; no session fallback.
        self._screen.facade.handle_command(cmd)

    def _dispatch_remove_from_queue_command(self, item_index: int) -> None:
        """Dispatch RemoveFromConstructionQueueCommand through command pipeline."""
        from game.strategy.engine.commands import (
            BuildEntityType,
            RemoveFromConstructionQueueCommand,
        )

        s = self._screen
        # Determine entity from active queue source
        source = s.active_queue_source
        if source is None:
            # Fallback to build_context
            entity = s.build_context
        else:
            entity = source.owner_entity

        entity_type = (
            BuildEntityType.PLANET if hasattr(entity, 'planet_type')
            else BuildEntityType.FLEET
        )
        entity_id = getattr(entity, 'id', 0)
        queue_id = getattr(source, 'queue_id', None) if source is not None else None

        cmd = RemoveFromConstructionQueueCommand(
            entity_id=entity_id,
            entity_type=entity_type,
            item_index=item_index,
            queue_id=queue_id,
        )
        # PROJ-382 Phase 1: facade is required; no session fallback.
        s.facade.handle_command(cmd)

    def _dispatch_toggle_pause_command(self) -> None:
        """FEAT-17 — flip the active queue source's paused flag.

        Resolves the active queue source's owner entity (Planet or Fleet)
        and the optional facility queue_id, then dispatches
        SetBuildQueuePausedCommand with the inverted current state.
        """
        from game.strategy.engine.commands import (
            BuildEntityType,
            SetBuildQueuePausedCommand,
        )

        s = self._screen
        source = s.active_queue_source
        if source is None:
            logger.warning("Pause toggle ignored — no active queue source")
            return

        entity = source.owner_entity
        entity_type = (
            BuildEntityType.PLANET if hasattr(entity, 'planet_type')
            else BuildEntityType.FLEET
        )
        entity_id = getattr(entity, 'id', 0)

        cmd = SetBuildQueuePausedCommand(
            entity_id=entity_id,
            entity_type=entity_type,
            paused=not source.is_paused,
            queue_id=source.queue_id,
        )
        # PROJ-382 Phase 1: facade is required; no session fallback.
        s.facade.handle_command(cmd)

        # Re-collect sources so the active source's `is_paused` reflects the
        # new state, then refresh the button label + queue display.
        # PROJ-382 Phase 1: registries pulled through facade rather than session.
        s.queue_sources = collect_build_queues_at_hex(
            s.hex_coord, s.galaxy, s.empire,
            registries=s.facade.session_meta.registries(),
        )
        # Re-bind the active source by queue_id (same reference may not exist
        # after re-collection — match by identifier).
        for candidate in s.queue_sources:
            if candidate.queue_id == source.queue_id:
                s.active_queue_source = candidate
                s.controller.set_active_queue(candidate)
                break
        self._refresh_queue_display()

    # -----------------------------------------------------------------------
    # Refresh Methods (delegate to renderer)
    # -----------------------------------------------------------------------

    def _refresh_items_list(self) -> None:
        """Refresh the items list based on selected category."""
        s = self._screen
        designs, roles_list = s.controller.load_designs_by_category(
            s.controller.selected_category
        )
        s.renderer.refresh_items_list(designs, s.controller.selected_category)
        if hasattr(s.renderer, 'refresh_roles_list'):
            s.renderer.refresh_roles_list(
                roles_list, getattr(s.controller, 'selected_role', 'Any'),
            )

    def _refresh_queue_display(self) -> None:
        """Refresh the build queue display via VirtualTable."""
        s = self._screen
        is_multi = len(s.selected_queue_indices) > 1
        queue = self._get_active_queue() if not is_multi else []

        # Get build rate from active queue source
        build_rate = {}
        if s.active_queue_source is not None:
            build_rate = s.active_queue_source.build_rate or {}

        s.renderer.refresh_queue_display(
            queue=queue,
            build_rate=build_rate,
            on_queue_selector_refresh=self._refresh_queue_selector,
        )
        # FEAT-17: re-sync pause button label after each refresh (covers
        # toggle commands that mutate the active source's `is_paused`).
        s.renderer.refresh_pause_button(s.active_queue_source)

    def _refresh_queue_selector(self) -> None:
        """Rebuild queue selector UI elements."""
        if self._screen._queue_selector:
            self._screen._queue_selector.refresh()

    # -----------------------------------------------------------------------
    # Event Handling
    # -----------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle UI events for the build queue screen."""
        s = self._screen
        # PROJ-376 Phase 1: defensive visibility gate. Pre-Phase-2 the manager
        # still constructs and shows the screen synchronously, so this is a
        # no-op for legacy callers; it guards against post-Phase-2 paths
        # where a hidden screen might still receive events.
        if not s.is_visible():
            return
        if event.type == pygame.KEYDOWN:
            logger.debug(f"BuildQueueScreen.handle_event: KEYDOWN key={event.key}")

        s.manager.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            self._handle_button_press(event)

        self._handle_drag_operations(event)

        if event.type == pygame.KEYDOWN:
            self._handle_keyboard_input(event)

    def _handle_button_press(self, event: pygame.event.Event) -> None:
        """Handle all UI_BUTTON_PRESSED events."""
        s = self._screen
        panels = s.panels

        # Category buttons
        if event.ui_element == panels.btn_category_complex:
            s.controller.set_category("complex")
            self._refresh_items_list()
        elif event.ui_element == panels.btn_category_ship:
            s.controller.set_category("ship")
            self._refresh_items_list()
        elif event.ui_element == panels.btn_category_satellite:
            s.controller.set_category("satellite")
            self._refresh_items_list()
        elif event.ui_element == panels.btn_category_fighter:
            s.controller.set_category("fighter")
            self._refresh_items_list()
        elif event.ui_element == panels.btn_category_drop_pod:
            s.controller.set_category("drop_pod")
            self._refresh_items_list()
        elif event.ui_element == panels.btn_category_mine:
            s.controller.set_category("mine")
            self._refresh_items_list()

        # Close button
        elif event.ui_element == panels.btn_close:
            self._request_close()

        # FEAT-17: Pause/Unpause toggle for the active queue source
        elif event.ui_element == panels.btn_pause_queue:
            self._dispatch_toggle_pause_command()

        # Check action column in virtual table
        action_match = panels.virtual_table.check_action_button_press(
            event.ui_element
        )
        if action_match:
            action, row_idx = action_match
            self._handle_virtual_table_action(action, row_idx)
            return

        # Check role filter buttons
        if hasattr(event.ui_element, 'role_filter'):
            s.controller.set_role(event.ui_element.role_filter)
            self._refresh_items_list()
            return

        # Check Add to Queue in available designs
        if hasattr(event.ui_element, 'is_add_to_queue_btn') and event.ui_element.is_add_to_queue_btn:
            s.controller.add_to_queue(event.ui_element.design_id)
            return

        # Queue selector button clicks
        elif s._queue_selector and s._queue_selector.handle_button_click(
            event.ui_element, bool(pygame.key.get_mods() & pygame.KMOD_CTRL)
        ):
            pass  # Handled by selector

    def _handle_virtual_table_action(self, action: str, row_idx: int) -> None:
        """Handle virtual table action button press."""
        s = self._screen
        if len(s.selected_queue_indices) > 1:
            return

        active_queue = self._get_active_queue()
        if row_idx < 0 or row_idx >= len(active_queue):
            return

        item = active_queue[row_idx]
        design_id = item.get('design_id')
        turns = item.get('turns_remaining', 1.0)
        category = item.get('type', 'ship')

        if not design_id:
            return

        if action == "remove":
            self._dispatch_remove_from_queue_command(row_idx)
            self._refresh_queue_display()
        elif action == "add":
            s.controller.add_to_queue(design_id, 1.0, category)
        elif action == "up":
            if row_idx > 0:
                self._dispatch_remove_from_queue_command(row_idx)
                s.controller.add_to_queue(design_id, turns, category, row_idx - 1)
        elif action == "down":
            if row_idx < len(active_queue) - 1:
                self._dispatch_remove_from_queue_command(row_idx)
                s.controller.add_to_queue(design_id, turns, category, row_idx + 1)

    def _handle_remove(self) -> None:
        """Handle remove from queue action.

        PROJ-208: Routes removal through RemoveFromConstructionQueueCommand.
        """
        s = self._screen
        if len(s.selected_queue_indices) > 1:
            logger.warning("Cannot remove items in multi-select mode")
            return

        remove_queue = self._get_active_queue()
        if s.selected_queue_index is not None and s.selected_queue_index < len(remove_queue):
            design_id = remove_queue[s.selected_queue_index].get('design_id', 'Unknown')
            self._dispatch_remove_from_queue_command(s.selected_queue_index)
            logger.info(
                f"Removed {design_id} from queue at index {s.selected_queue_index}"
            )
            s.selected_queue_index = None
            self._refresh_queue_display()
        else:
            logger.warning("No queue item selected to remove")

    def _handle_drag_operations(self, event: pygame.event.Event) -> None:
        """Handle mouse events for drag-and-drop.

        PROJ-221 Phase 4: Adapted to work with VirtualTable. Queue item
        click detection now uses VirtualTable.handle_click() for row
        identification, with the drag handler still managing drag state.
        """
        s = self._screen
        multi_select = len(s.selected_queue_indices) > 1
        active_queue = self._get_active_queue()
        virtual_table = s.panels.virtual_table

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            s.drag_handler.handle_mouse_down(
                event, s.panels.items_scrollable,
                virtual_table, active_queue,
                s.controller.selected_category,
                multi_select_active=multi_select,
            )

        if event.type == pygame.MOUSEMOTION and event.buttons[0]:
            s.drag_handler.handle_mouse_motion(
                event, active_queue, multi_select_active=multi_select,
            )

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            result = s.drag_handler.handle_mouse_up(
                event, s.panels.build_queue_panel,
                virtual_table, active_queue,
                multi_select_active=multi_select,
            )
            if result is not None:
                s.selected_queue_index = result
                if result < len(active_queue):
                    design_id = active_queue[result].get('design_id')
                    if design_id:
                        s.controller.refresh_design_report(design_id)

    def _handle_keyboard_input(self, event: pygame.event.Event) -> None:
        """Handle keyboard events."""
        self._handle_keydown(event)

    def _handle_keydown(self, event: pygame.event.Event) -> bool:
        """Dispatch keyboard events via InputMapper."""
        s = self._screen
        if not s._mapper:
            return False
        action = s._mapper.resolve(event, contexts=["build_queue"])
        if action == InputAction.BUILD_QUEUE_CLOSE:
            self._request_close()
            return True
        if action == InputAction.BUILD_QUEUE_ADD:
            if s.drag_handler.selected_design:
                s.controller.add_to_queue(s.drag_handler.selected_design)
            return True
        if action == InputAction.BUILD_QUEUE_REMOVE:
            self._handle_remove()
            return True
        if action == InputAction.BUILD_QUEUE_CAT_COMPLEXES:
            s.controller.set_category("complex")
            self._refresh_items_list()
            return True
        if action == InputAction.BUILD_QUEUE_CAT_SHIPS:
            s.controller.set_category("ship")
            self._refresh_items_list()
            return True
        if action == InputAction.BUILD_QUEUE_CAT_SATELLITES:
            s.controller.set_category("satellite")
            self._refresh_items_list()
            return True
        if action == InputAction.BUILD_QUEUE_CAT_FIGHTERS:
            s.controller.set_category("fighter")
            self._refresh_items_list()
            return True
        return False

    # -----------------------------------------------------------------------
    # Tooltips
    # -----------------------------------------------------------------------

    def _apply_tooltips(self) -> None:
        """Enrich buttons with hotkey hint tooltips from InputMapper."""
        s = self._screen
        if not s._mapper:
            return
        _hint = s._mapper.get_display_text
        panels = s.panels

        hints = [
            (panels.btn_close, InputAction.BUILD_QUEUE_CLOSE, "Close"),
            (panels.btn_add_to_queue, InputAction.BUILD_QUEUE_ADD, "Add to Queue"),
            (panels.btn_remove_from_queue, InputAction.BUILD_QUEUE_REMOVE, "Remove Selected"),
            (panels.btn_category_complex, InputAction.BUILD_QUEUE_CAT_COMPLEXES, "Complexes"),
            (panels.btn_category_ship, InputAction.BUILD_QUEUE_CAT_SHIPS, "Ships"),
            (panels.btn_category_satellite, InputAction.BUILD_QUEUE_CAT_SATELLITES, "Satellites"),
            (panels.btn_category_fighter, InputAction.BUILD_QUEUE_CAT_FIGHTERS, "Fighters"),
        ]
        for btn, action, label in hints:
            if btn is None:
                continue
            hint = _hint(action)
            if hint:
                btn.set_tooltip(f"{label} ({hint})")

    # -----------------------------------------------------------------------
    # Planet Selection
    # -----------------------------------------------------------------------

    def _prompt_target_planet(self, planets, on_selected) -> None:
        """Open planet selection window for complex target planet."""
        s = self._screen
        rect = pygame.Rect(200, 100, 950, 650)
        # PROJ-397 Phase 3 Task 3.2: pass the strategy facade so colonized
        # planets render the PROJ-289 per-species sub-block.
        s.planet_selection_window = PlanetSelectionWindow(
            rect,
            s.manager,
            planets,
            on_selected,
            window_manager=None,  # PROJ-313: build queue screen has its own modal lifecycle
            window_title="Select Target Planet",
            list_label="Colonies in sector:",
            show_any_button=False,
            facade=s.facade,
        )
        logger.info(
            f"BuildQueue: Opened planet selection for {len(planets)} colonies"
        )

    # -----------------------------------------------------------------------
    # Lifecycle
    # -----------------------------------------------------------------------

    def _request_close(self) -> None:
        """Hide the build queue screen and notify the close callback.

        PROJ-376 Phase 2: replaces ``_close()`` (which destroyed the panel
        tree). Single source of truth for "user closed the screen": calls
        ``hide()`` (panels survive across opens) then invokes ``on_close``
        so the manager can run side-effect cleanup (FEAT-17 fleet BUILD
        order auto-issue, restoring the galaxy UI).

        Per decisions.md row 2026-05-07, ``hide()`` does NOT invoke
        ``on_close``; the close-button / Esc handler is the only place
        that pairs them.
        """
        s = self._screen
        s.hide()
        if s.on_close:
            s.on_close()

    def on_active_player_changed(self) -> None:
        """PROJ-410 Phase 4 Task 4.1: flush cached UI state on player change.

        Called by ``StrategyBuildQueueManager._open_build_queue`` (Task 4.2)
        when the active empire id has changed since the last open. Hides
        the screen, invalidates the VirtualTable widget caches, and clears
        the cached queue-source refs that were collected for the prior
        empire. The screen-side rebind of ``self.empire`` / ``self.galaxy``
        / ``self.facade`` happens in the **manager** (Task 4.2), not here —
        this hook only does the *flush* half.

        Idempotent: safe to call on a hidden screen or one without panels
        (e.g. shell-only construction).
        """
        s = self._screen
        if s.is_visible():
            s.hide()
        if s.panels is not None:
            s.panels.virtual_table.invalidate_widget_caches()
        s.queue_sources = []
        s.active_queue_source = None
        s.selected_queue_indices = set()

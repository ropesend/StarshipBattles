"""
Build Queue Screen - Full-screen interface for managing build queues.

Supports both Planet and Fleet build contexts (PROJ-67 Phase 4).
Updated in PROJ-69 Phase 3 to support multiple queue sources at a hex.
Refactored in PROJ-172 Phase 4 to MVVM architecture.
"""
from __future__ import annotations

import logging
import pygame
import pygame_gui
from typing import TYPE_CHECKING, List, Optional, Callable, Set

from game.core.input_actions import InputAction
from game.ui.services.screenshot_manager import ScreenshotManager
from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode

logger = logging.getLogger(__name__)
from game.ui.panels.build_queue_portraits import BuildQueuePortraitLoader
from game.ui.panels.build_queue_drag_handler import BuildQueueDragHandler
from game.ui.panels.build_queue_controller import BuildQueueController
from game.strategy.data.build_queue_source import BuildQueueSource, collect_build_queues_at_hex
from game.ui.screens.planet_selection_window import PlanetSelectionWindow
from game.ui.screens.build_queue_helpers import format_empire_resources
from game.ui.screens.build_queue_panel_factory import BuildQueuePanelFactory
from game.ui.screens.build_queue_renderer import BuildQueueRenderer

if TYPE_CHECKING:
    from game.ui.services.input_mapper import InputMapper
    from game.core.hex_math import HexCoord
    from game.strategy.data.galaxy import Galaxy
    from game.strategy.data.empire import Empire
    from game.strategy.systems.design_library import DesignLibrary
    from game.ui.services.design_loader_adapter import DesignLoaderAdapter


class BuildQueueScreen:
    """Full-screen modal interface for managing build queues on planets or fleets.

    PROJ-172 Phase 4: Refactored to MVVM architecture with:
    - BuildQueuePanelFactory: Creates all UI panels
    - BuildQueueRenderer: Handles display refresh
    - BuildQueueController: Business logic
    - BuildQueueDragHandler: Drag-drop handling
    """

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        build_context,  # Planet, Fleet, or BuildContext
        session,
        on_close_callback: Callable,
        portrait_surface: Optional[pygame.Surface] = None,
        design_library: 'DesignLibrary' = None,
        design_loader: 'DesignLoaderAdapter' = None,
        hex_coord: 'HexCoord' = None,
        galaxy: 'Galaxy' = None,
        empire: 'Empire' = None,
        input_mapper: Optional['InputMapper'] = None
    ):
        """Initialize the build queue screen."""
        # Validate required parameters
        self._validate_params(hex_coord, galaxy, empire, build_context)

        self.manager = manager
        self.build_context = build_context
        self.session = session
        self.on_close = on_close_callback
        self.portrait_surface = portrait_surface
        self._mapper = input_mapper
        self.selected_queue_index = None  # Currently selected item in queue

        # Dependencies
        self.design_library = design_library
        self.design_loader = design_loader
        self.hex_coord = hex_coord
        self.galaxy = galaxy
        self.empire = empire
        self.planet_selection_window = None

        # Portrait loading
        self.portrait_loader = BuildQueuePortraitLoader(design_library, session)

        # Populate queue sources from hex context
        self.queue_sources: List[BuildQueueSource] = collect_build_queues_at_hex(
            hex_coord, galaxy, empire
        )

        # Queue selection state
        self.selected_queue_indices: Set[int] = {0} if self.queue_sources else set()
        self.active_queue_source: Optional[BuildQueueSource] = (
            self.queue_sources[0] if self.queue_sources else None
        )

        logger.info(f"BuildQueue: Initialized for {build_context.context_type} '{build_context.name}'")
        logger.info(f"BuildQueue: {len(self.queue_sources)} queue source(s) discovered")

        # Get screen dimensions
        screen_size = manager.get_root_container().get_container().get_size()
        self.screen_width = screen_size[0]
        self.screen_height = screen_size[1]

        # Create UI panels via factory
        factory = BuildQueuePanelFactory(
            manager=manager,
            build_context=build_context,
            session=session,
            queue_sources=self.queue_sources,
            portrait_loader=self.portrait_loader,
            on_queue_selection_changed=self._on_queue_selection_changed,
        )
        self.panels = factory.create_all_panels(format_empire_resources)
        self._queue_selector = self.panels.queue_selector

        # Create renderer
        self.renderer = BuildQueueRenderer(
            manager=manager,
            panels=self.panels,
            portrait_loader=self.portrait_loader,
        )

        # Controller for queue business logic
        # PROJ-208: Create callback for AddToConstructionQueueCommand dispatch
        self.controller = BuildQueueController(
            build_context=self.build_context,
            design_library=self.design_library,
            design_loader=self.design_loader,
            design_report=self.panels.design_report,
            on_queue_changed=self._refresh_queue_display,
            hex_coord=self.hex_coord,
            galaxy=self.galaxy,
            empire=self.empire,
            on_planet_selection_needed=self._prompt_target_planet,
            add_to_queue_callback=self._dispatch_add_to_queue_command,
        )

        # Sync controller with initial queue selection
        if self.active_queue_source is not None:
            self.controller.set_active_queue(self.active_queue_source)

        # Drag-drop handling
        self.drag_handler = BuildQueueDragHandler(
            portrait_loader=self.portrait_loader,
            design_library=self.design_library,
            on_add_to_queue=self.controller.add_to_queue,
            on_refresh_queue=self._refresh_queue_display,
            on_refresh_design_report=self.controller.refresh_design_report
        )

        # Apply hotkey tooltips
        self._apply_tooltips()

        # Load initial designs
        self._refresh_items_list()
        self._refresh_queue_display()

    def _validate_params(self, hex_coord, galaxy, empire, build_context):
        """Validate required constructor parameters."""
        if hex_coord is None:
            raise ValidationException(
                "BuildQueueScreen requires hex_coord parameter",
                code=ErrorCode.MISSING_DEPENDENCY.value,
                context={"screen": "BuildQueueScreen", "missing_param": "hex_coord"}
            )
        if galaxy is None:
            raise ValidationException(
                "BuildQueueScreen requires galaxy parameter",
                code=ErrorCode.MISSING_DEPENDENCY.value,
                context={"screen": "BuildQueueScreen", "missing_param": "galaxy"}
            )
        if empire is None:
            raise ValidationException(
                "BuildQueueScreen requires empire parameter",
                code=ErrorCode.MISSING_DEPENDENCY.value,
                context={"screen": "BuildQueueScreen", "missing_param": "empire"}
            )
        if not hasattr(build_context, 'owner_id'):
            raise ValidationException(
                f"build_context '{getattr(build_context, 'name', 'unknown')}' missing 'owner_id' attribute",
                code=ErrorCode.SCHEMA_VALIDATION_ERROR.value,
                context={"screen": "BuildQueueScreen", "missing_attr": "owner_id"}
            )
        if not hasattr(build_context, 'name'):
            logger.warning("BuildQueueScreen: build_context missing 'name' attribute")

    # -----------------------------------------------------------------------
    # Queue Selection
    # -----------------------------------------------------------------------

    def _on_queue_selection_changed(
        self, active_source: Optional[BuildQueueSource], selected_indices: Set[int]
    ) -> None:
        """Handle selection change from BuildQueueSelector."""
        self.active_queue_source = active_source
        self.selected_queue_indices = selected_indices

        if active_source is not None:
            self.controller.set_active_queue(active_source)
        else:
            selected_sources = [
                self.queue_sources[i] for i in sorted(selected_indices)
            ]
            self.controller.set_selected_queues(selected_sources)

        self._refresh_queue_display()
        self.renderer.update_queue_header(active_source)

    def _get_active_queue(self) -> list:
        """Return the active construction queue list."""
        if self.active_queue_source is not None:
            return self.active_queue_source.construction_queue
        return self.build_context.construction_queue

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
        """Dispatch AddToConstructionQueueCommand through command pipeline.

        PROJ-208: Routes build queue additions through CQRS command system.

        Args:
            entity_id: Planet or fleet ID.
            entity_type: "planet" or "fleet".
            design_id: ID of the design to build.
            category: Design category ("complex", "ship", "satellite", "fighter").
            index: Optional insertion index. None = append.
            target_planet_id: For complexes built at fleet yards, the target planet.
            queue_id: Optional queue identifier for multi-queue entities (e.g., shipyard facility ID).
        """
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
        self.session.handle_command(cmd)

    # -----------------------------------------------------------------------
    # Refresh Methods (delegate to renderer)
    # -----------------------------------------------------------------------

    def _refresh_items_list(self):
        """Refresh the items list based on selected category."""
        designs = self.controller.load_designs_by_category(self.controller.selected_category)
        self.renderer.refresh_items_list(designs, self.controller.selected_category)

    def _refresh_queue_display(self):
        """Refresh the build queue display."""
        is_multi = len(self.selected_queue_indices) > 1
        selected_sources = [
            self.queue_sources[i] for i in sorted(self.selected_queue_indices)
        ] if is_multi else None

        queue = self._get_active_queue() if not is_multi else []

        self.renderer.queue_items = self.renderer.refresh_queue_display(
            queue=queue,
            selected_queue_index=self.selected_queue_index,
            is_multi_select=is_multi,
            selected_sources=selected_sources,
            on_queue_selector_refresh=self._refresh_queue_selector,
        )

    def _refresh_queue_selector(self):
        """Rebuild queue selector UI elements."""
        if self._queue_selector:
            self._queue_selector.refresh()

    # -----------------------------------------------------------------------
    # Event Handling
    # -----------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event):
        """Handle UI events for the build queue screen."""
        if event.type == pygame.KEYDOWN:
            logger.debug(f"BuildQueueScreen.handle_event: KEYDOWN key={event.key}")

        self.manager.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            self._handle_button_press(event)

        self._handle_drag_operations(event)

        if event.type == pygame.KEYDOWN:
            self._handle_keyboard_input(event)

    def _handle_button_press(self, event: pygame.event.Event) -> None:
        """Handle all UI_BUTTON_PRESSED events."""
        panels = self.panels

        # Category buttons
        if event.ui_element == panels.btn_category_complex:
            self.controller.set_category("complex")
            self._refresh_items_list()
        elif event.ui_element == panels.btn_category_ship:
            self.controller.set_category("ship")
            self._refresh_items_list()
        elif event.ui_element == panels.btn_category_satellite:
            self.controller.set_category("satellite")
            self._refresh_items_list()
        elif event.ui_element == panels.btn_category_fighter:
            self.controller.set_category("fighter")
            self._refresh_items_list()

        # Close button
        elif event.ui_element == panels.btn_close:
            self._close()

        # Add to queue button
        elif event.ui_element == panels.btn_add_to_queue:
            if self.drag_handler.selected_design:
                self.controller.add_to_queue(self.drag_handler.selected_design)

        # Remove selected from queue button
        elif event.ui_element == panels.btn_remove_from_queue:
            self._handle_remove()

        # Queue selector button clicks
        elif self._queue_selector and self._queue_selector.handle_button_click(
            event.ui_element, bool(pygame.key.get_mods() & pygame.KMOD_CTRL)
        ):
            pass  # Handled by selector

    def _handle_remove(self):
        """Handle remove from queue action."""
        if len(self.selected_queue_indices) > 1:
            logger.warning("Cannot remove items in multi-select mode")
            return

        remove_queue = self._get_active_queue()
        if self.selected_queue_index is not None and self.selected_queue_index < len(remove_queue):
            removed_item = remove_queue.pop(self.selected_queue_index)
            design_id = removed_item.get('design_id', 'Unknown')
            logger.info(f"Removed {design_id} from queue at index {self.selected_queue_index}")
            self.selected_queue_index = None
            self._refresh_queue_display()
        else:
            logger.warning("No queue item selected to remove")

    def _handle_drag_operations(self, event: pygame.event.Event) -> None:
        """Handle mouse events for drag-and-drop."""
        multi_select = len(self.selected_queue_indices) > 1
        active_queue = self._get_active_queue()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.drag_handler.handle_mouse_down(
                event, self.panels.items_scrollable, self.renderer.queue_items,
                active_queue, self.controller.selected_category,
                multi_select_active=multi_select
            )

        if event.type == pygame.MOUSEMOTION and event.buttons[0]:
            self.drag_handler.handle_mouse_motion(
                event, active_queue, multi_select_active=multi_select
            )

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            result = self.drag_handler.handle_mouse_up(
                event, self.panels.build_queue_panel, self.panels.queue_scrollable,
                active_queue, multi_select_active=multi_select
            )
            if result is not None:
                self.selected_queue_index = result
                if result < len(active_queue):
                    design_id = active_queue[result].get('design_id')
                    if design_id:
                        self.controller.refresh_design_report(design_id)

    def _handle_keyboard_input(self, event: pygame.event.Event) -> None:
        """Handle keyboard events."""
        if self._handle_keydown(event):
            return
        if event.key in (pygame.K_F11, pygame.K_F12):
            self._take_screenshot()

    def _handle_keydown(self, event: pygame.event.Event) -> bool:
        """Dispatch keyboard events via InputMapper."""
        if not self._mapper:
            return False
        action = self._mapper.resolve(event, contexts=["build_queue"])
        if action == InputAction.BUILD_QUEUE_CLOSE:
            self._close()
            return True
        if action == InputAction.BUILD_QUEUE_ADD:
            if self.drag_handler.selected_design:
                self.controller.add_to_queue(self.drag_handler.selected_design)
            return True
        if action == InputAction.BUILD_QUEUE_REMOVE:
            self._handle_remove()
            return True
        if action == InputAction.BUILD_QUEUE_CAT_COMPLEXES:
            self.controller.set_category("complex")
            self._refresh_items_list()
            return True
        if action == InputAction.BUILD_QUEUE_CAT_SHIPS:
            self.controller.set_category("ship")
            self._refresh_items_list()
            return True
        if action == InputAction.BUILD_QUEUE_CAT_SATELLITES:
            self.controller.set_category("satellite")
            self._refresh_items_list()
            return True
        if action == InputAction.BUILD_QUEUE_CAT_FIGHTERS:
            self.controller.set_category("fighter")
            self._refresh_items_list()
            return True
        return False

    # -----------------------------------------------------------------------
    # Tooltips
    # -----------------------------------------------------------------------

    def _apply_tooltips(self) -> None:
        """Enrich buttons with hotkey hint tooltips from InputMapper."""
        if not self._mapper:
            return
        _hint = self._mapper.get_display_text
        panels = self.panels

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
            hint = _hint(action)
            if hint:
                btn.set_tooltip(f"{label} ({hint})")

    # -----------------------------------------------------------------------
    # Planet Selection
    # -----------------------------------------------------------------------

    def _prompt_target_planet(self, planets, on_selected):
        """Open planet selection window for complex target planet."""
        rect = pygame.Rect(200, 100, 950, 650)
        self.planet_selection_window = PlanetSelectionWindow(
            rect,
            self.manager,
            planets,
            on_selected,
            window_title="Select Target Planet",
            list_label="Colonies in sector:",
            show_any_button=False
        )
        logger.info(f"BuildQueue: Opened planet selection for {len(planets)} colonies")

    # -----------------------------------------------------------------------
    # Screenshot
    # -----------------------------------------------------------------------

    def _take_screenshot(self):
        """Take a screenshot of the current screen."""
        sm = ScreenshotManager.instance()
        sm.capture(label="build_queue")
        sm.show_toast(self.manager, self.screen_width)

    # -----------------------------------------------------------------------
    # Lifecycle
    # -----------------------------------------------------------------------

    def _close(self):
        """Close the build queue screen."""
        if self.planet_selection_window:
            self.planet_selection_window.kill()
            self.planet_selection_window = None

        self.panels.background.kill()
        self.manager.update(0)

        if self.on_close:
            self.on_close()

    def update(self, time_delta: float):
        """Update the UI manager."""
        self.manager.update(time_delta)

    def draw(self, screen: pygame.Surface):
        """Draw the UI."""
        self.manager.draw_ui(screen)
        self.renderer.draw_selection_highlight(screen, self.selected_queue_index)
        self.drag_handler.draw_drag_preview(screen)

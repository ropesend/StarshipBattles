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
from typing import TYPE_CHECKING, List, Optional, Callable, Set, Union

from game.core.input_actions import InputAction
from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode
from game.core.profiling import profile_action

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
        build_context=None,  # Planet, Fleet, or BuildContext (legacy positional yard)
        on_close_callback: Optional[Callable] = None,
        portrait_surface: Optional[pygame.Surface] = None,
        design_library: 'DesignLibrary' = None,
        design_loader: 'DesignLoaderAdapter' = None,
        hex_coord: 'HexCoord' = None,
        galaxy: 'Galaxy' = None,
        empire: 'Empire' = None,
        input_mapper: Optional['InputMapper'] = None,
        *,
        facade,
        theme_id_supplier: Optional[Callable[[], str]] = None,
        initial_yard: Optional[Union['object', None]] = None,
    ):
        """Initialize the build queue screen.

        PROJ-208 Phase 3: Added facade parameter for CQRS-compliant command dispatch.
        PROJ-382 Phase 1: ``facade`` is required (keyword-only); the legacy
        ``session=`` kwarg is gone.
        PROJ-396 MAJ-002: ``portrait_session`` (a renamed full-session
        backdoor) replaced by ``theme_id_supplier`` — a zero-arg callable
        returning the active empire's ``empire_theme_id`` string.  The
        screen no longer holds a reference to anything session-shaped
        outside the facade.

        PROJ-376 Phase 1: Split into "UI shell" (always runs) + "yard population"
        (only when ``initial_yard`` is provided, or legacy ``build_context`` is
        non-None). When neither is provided, the screen constructs in shell-only
        mode — no panels, controller, or drag handler — and waits for
        ``open_for_yard()`` to populate the panel tree on first open.

        ``initial_yard`` (keyword-only) is the new explicit kwarg. The legacy
        ``build_context`` positional/keyword arg is preserved for back-compat:
        when ``initial_yard is None`` and ``build_context is not None``,
        ``build_context`` is treated as the initial yard.
        """
        # PROJ-376: Resolve the effective initial yard from new + legacy kwargs.
        effective_initial_yard = initial_yard if initial_yard is not None else build_context

        # Validate required parameters (relaxed when no yard is provided).
        self._validate_params(hex_coord, galaxy, empire, effective_initial_yard)

        # ---- Shell block: DI / always-present state. ----------------------
        self.manager = manager
        self.facade = facade  # PROJ-208/382: required for command dispatch
        # PROJ-396 MAJ-002: replaced ``portrait_session`` (a renamed
        # full-session backdoor) with a narrow zero-arg callable returning
        # the active empire's ``empire_theme_id`` string.  Falls back to a
        # constant supplier when omitted.
        self._theme_id_supplier: Callable[[], str] = (
            theme_id_supplier
            if theme_id_supplier is not None
            else lambda: "Federation"
        )
        self.on_close = on_close_callback
        self.portrait_surface = portrait_surface
        self._mapper = input_mapper

        # Dependencies (some yard-specific defaults are seeded here so shell-
        # only construction has a defined attribute surface).
        self.design_library = design_library
        self.design_loader = design_loader
        self.galaxy = galaxy
        self.empire = empire

        # Yard-specific state (initialized to "no yard" defaults; ``open_for_yard``
        # mutates these when a yard arrives).
        self.build_context = None
        self.hex_coord = None
        self.selected_queue_index = None
        self.planet_selection_window = None
        self.queue_sources: List[BuildQueueSource] = []
        self.selected_queue_indices: Set[int] = set()
        self.active_queue_source: Optional[BuildQueueSource] = None

        # Portrait loading — needs design_library + a narrow theme-id
        # supplier for empire-theme lookup (PROJ-396 MAJ-002).
        self.portrait_loader = BuildQueuePortraitLoader(
            design_library, self._theme_id_supplier
        )

        # Get screen dimensions (stable across yards; cheap and idempotent).
        screen_size = manager.get_root_container().get_container().get_size()
        self.screen_width = screen_size[0]
        self.screen_height = screen_size[1]

        # Panel-dependent collaborators stay None until a yard arrives. When
        # ``initial_yard is not None`` we delegate to ``open_for_yard`` below.
        self.panels = None
        self._queue_selector = None
        self.renderer = None
        self.controller = None
        self.drag_handler = None

        # ---- Yard population block (delegate to open_for_yard). -----------
        if effective_initial_yard is not None:
            self.open_for_yard(
                effective_initial_yard,
                hex_coord=hex_coord,
                portrait_surface=portrait_surface,
            )

    def _validate_params(self, hex_coord, galaxy, empire, build_context) -> None:
        """Validate required constructor parameters.

        PROJ-376: When ``build_context`` is None (shell-only construction),
        ``hex_coord`` may also be None. ``galaxy`` and ``empire`` remain
        required because they're shell-level dependencies (the screen routes
        commands through them regardless of the active yard).
        """
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
        if build_context is None:
            # Shell-only construction: hex_coord may also be None.
            return
        if hex_coord is None:
            raise ValidationException(
                "BuildQueueScreen requires hex_coord parameter when a yard is provided",
                code=ErrorCode.MISSING_DEPENDENCY.value,
                context={"screen": "BuildQueueScreen", "missing_param": "hex_coord"}
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
    # Lifecycle (PROJ-376 Phase 1)
    # -----------------------------------------------------------------------

    def _construct_collaborators(self, yard, hex_coord, portrait_surface) -> None:
        """Build the panel tree + collaborators for ``yard``.

        Called from ``open_for_yard`` when no panels exist yet (shell-only
        first-open) and from ``_rebuild_panels`` on a context-type transition.
        Collaborators (renderer, controller, drag handler) hold references
        INTO ``panels``, so they're reseated together.
        """
        # PROJ-382 Phase 1: registries pulled from facade.
        # PROJ-396 MAJ-003: ``session`` parameter dropped; the factory now
        # routes registries / turn through the facade and reads the empire
        # from the explicit ``empire`` kwarg.
        factory = BuildQueuePanelFactory(
            manager=self.manager,
            build_context=yard,
            queue_sources=collect_build_queues_at_hex(
                hex_coord, self.galaxy, self.empire,
                registries=self.facade.get_registries(),
            ),
            portrait_loader=self.portrait_loader,
            on_queue_selection_changed=self._on_queue_selection_changed,
            portrait_surface=portrait_surface,
            facade=self.facade,  # PROJ-292 H1: enables per-species sub-block
            empire=self.empire,
        )
        self.panels = factory.create_all_panels(format_empire_resources)
        self._queue_selector = self.panels.queue_selector
        self.renderer = BuildQueueRenderer(
            manager=self.manager,
            panels=self.panels,
            portrait_loader=self.portrait_loader,
        )
        self.controller = BuildQueueController(
            build_context=yard,
            design_library=self.design_library,
            design_loader=self.design_loader,
            design_report=self.panels.design_report,
            on_queue_changed=self._refresh_queue_display,
            hex_coord=hex_coord,
            galaxy=self.galaxy,
            empire=self.empire,
            on_planet_selection_needed=self._prompt_target_planet,
            add_to_queue_callback=self._dispatch_add_to_queue_command,
            registries=self.facade.get_registries(),
        )
        # PROJ-208: drag handler wires through controller's add/refresh.
        self.drag_handler = BuildQueueDragHandler(
            portrait_loader=self.portrait_loader,
            design_library=self.design_library,
            on_add_to_queue=self.controller.add_to_queue,
            on_refresh_queue=self._refresh_queue_display,
            on_refresh_design_report=self.controller.refresh_design_report,
            on_remove_from_queue=self._dispatch_remove_from_queue_command,
        )
        self._apply_tooltips()

    def _rebuild_panels(self, yard, hex_coord, portrait_surface) -> None:
        """Tear down + reconstruct the panel tree for a context-type transition.

        Called from ``open_for_yard`` when ``build_context.context_type`` changes
        (planet ↔ fleet). The panel factory dispatches different concrete panels
        based on context type (``PlanetReportPanel`` vs fleet info panel), so the
        whole tree must be rebuilt. Collaborators are reseated alongside.
        """
        if self.panels is not None:
            self.panels.background.kill()
            self.manager.update(0)
        self._construct_collaborators(yard, hex_coord, portrait_surface)

    # PROJ-411 Task 1.10: full-open span. ``open_for_yard`` is the
    # production entry point for the Build Queue panel — covers panel
    # rebuild (cross-type opens), controller reset, queue refresh, and
    # virtual-table widget invalidation.
    @profile_action("Panel: BuildQueue.open_for_yard")
    def open_for_yard(
        self,
        yard,
        *,
        hex_coord: 'HexCoord',
        portrait_surface: Optional[pygame.Surface] = None,
    ) -> None:
        """Populate yard-specific state and show the screen.

        PROJ-376 Phase 1: split out from ``__init__`` so the manager can reuse
        a single ``BuildQueueScreen`` instance across opens (Phase 2). Behavior
        parity with today is the contract — the post-call observable state must
        match what ``__init__(initial_yard=yard, hex_coord=hex_coord)`` produced.
        """
        prev_type = self.build_context.context_type if self.build_context is not None else None
        new_type = yard.context_type

        # Decide whether to rebuild panels.
        if self.panels is None:
            # Shell-only first open — construct the collaborators.
            self._construct_collaborators(yard, hex_coord, portrait_surface)
        elif prev_type is not None and prev_type != new_type:
            # Cross-context-type transition (planet ↔ fleet) — rebuild.
            self._rebuild_panels(yard, hex_coord, portrait_surface)

        # Update yard-specific state.
        self.build_context = yard
        self.hex_coord = hex_coord
        if portrait_surface is not None:
            self.portrait_surface = portrait_surface
        self.queue_sources = collect_build_queues_at_hex(
            hex_coord, self.galaxy, self.empire,
            registries=self.facade.get_registries(),
        )
        self.selected_queue_indices = {0} if self.queue_sources else set()
        self.active_queue_source = (
            self.queue_sources[0] if self.queue_sources else None
        )
        self.selected_queue_index = None
        # PROJ-376 review LS-04: kill any orphan PlanetSelectionWindow before
        # clearing the slot. Mirrors hide()'s pattern for the case where
        # open_for_yard is invoked while the screen is still visible (rapid
        # yard switch); production paths today always call hide() first, but
        # this is defense-in-depth so the slot can never leak a live window.
        if self.planet_selection_window is not None:
            self.planet_selection_window.kill()
        self.planet_selection_window = None

        logger.info(
            f"BuildQueue: open_for_yard {new_type} '{getattr(yard, 'name', 'unknown')}' "
            f"({len(self.queue_sources)} queue source(s))"
        )

        # Update controller for the new yard.
        self.controller.build_context = yard
        self.controller.hex_coord = hex_coord
        self.controller.galaxy = self.galaxy
        self.controller.empire = self.empire
        if self.active_queue_source is not None:
            self.controller.set_active_queue(self.active_queue_source)
        else:
            # PROJ-410 Task 3.6: zero-source yard. set_active_queue() is the
            # only path that clears controller.active_queue_source /
            # selected_queue_sources, and we just skipped it. set_selected_queues([])
            # explicitly clears both via the existing controller API
            # (build_queue_controller.py:132-143) so the controller does not
            # leak the prior yard's source refs into a planet with no yards.
            self.controller.set_selected_queues([])
        self.controller.reset_filters()

        # Reset drag handler transient state.
        self.drag_handler.reset_state()
        # PROJ-376: design_library may differ between Planet and Fleet manager
        # call sites (each constructs a fresh DesignLibrary). Rebind so the
        # drag handler always reflects the current manager's library.
        self.drag_handler.design_library = self.design_library

        # Refresh queue selector against the new sources.
        self._queue_selector.queue_sources = self.queue_sources
        self._queue_selector.selected_indices = self.selected_queue_indices
        self._queue_selector.active_source = self.active_queue_source
        self._queue_selector.refresh()

        # Issue #17: header text is bound to the active queue source, but
        # ``update_queue_header`` is otherwise only invoked from
        # ``_on_queue_selection_changed``. Without this call the title
        # remains pointed at the previously-active yard on re-open /
        # player-turn change, even though the selector cursor and
        # rendered rows correctly reflect the reset active source.
        self.renderer.update_queue_header(self.active_queue_source)

        # Initial render — also resyncs the FEAT-17 pause-button label via
        # ``renderer.refresh_pause_button(...)``.
        self._refresh_items_list()
        self._refresh_queue_display()

        self.show()

    def hide(self) -> None:
        """Hide the build-queue overlay without destroying widgets.

        PROJ-376: replaces destroy-then-reconstruct close path. Kills any
        transient ``PlanetSelectionWindow`` that's still open (matching
        today's ``_close()`` cleanup) and toggles panel visibility off.
        Panels remain alive across calls so subsequent ``show()`` is cheap.

        Decision: ``hide()`` does NOT invoke ``on_close``. Only the close-
        button / Esc handler invokes ``hide()`` then ``on_close()`` in
        sequence (decisions.md row 2026-05-07).
        """
        if self.planet_selection_window is not None:
            self.planet_selection_window.kill()
            self.planet_selection_window = None
        if self.panels is not None:
            # pygame_gui.UIPanel exposes hide()/show() methods + a `visible`
            # attribute (no `set_visible`). hide() recursively toggles
            # visibility of children and stops event delivery.
            self.panels.background.hide()
            # Provisional: mirror today's _close() flush. See decisions.md.
            self.manager.update(0)

    def show(self) -> None:
        """Reveal the build-queue overlay (panels must already exist).

        Issue #17 follow-up: pygame_gui's
        ``UIPanel.show(show_contents=True)`` calls
        ``panel_container.show(True)``, and ``UIContainer.show(True)``
        iterates ``self.elements`` and calls ``element.show()`` on every
        descendant regardless of each descendant's prior individual
        ``visible`` state (verified against pygame-ce 2.5.7:
        ``ui_panel.py:468-476`` + ``ui_container.py:380-394``). So any
        pool row that ``invalidate_widget_caches()`` or
        ``update_visible_rows()`` individually hid because
        ``data_idx >= current_count`` is re-exposed by the call below.

        Re-run the virtual table's visibility pass AFTER the recursive
        un-hide so rows beyond ``row_count`` stay hidden.
        ``force_update()`` resets the ``(scroll_pct, row_count)`` early
        return so ``update_visible_rows()`` cannot short-circuit on the
        unchanged tuple. PROJ-373 perf-lock (no ``.kill()``), PROJ-410
        ephemeral ``_data_identity_dirty``, and PROJ-376 repeat-open
        budget are preserved (``force_update()`` only mutates
        dirty-tracking scalars; ``update_visible_rows()`` uses
        hide/show/set_text/set_image, not ``.kill()``).
        """
        if self.panels is not None:
            self.panels.background.show()
            # Issue #17 follow-up: re-assert per-row visibility after the
            # recursive un-hide. Guarded against shell-only construction
            # where panels exist but virtual_table may not (defensive).
            virtual_table = getattr(self.panels, "virtual_table", None)
            if virtual_table is not None:
                virtual_table.force_update()
                virtual_table.update_visible_rows()
            self.manager.update(0)

    def is_visible(self) -> bool:
        """Return True iff panels exist AND their root is currently visible."""
        return self.panels is not None and bool(self.panels.background.visible)

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
        # FEAT-17: keep the pause-toggle label in sync with the new selection
        self.renderer.refresh_pause_button(active_source)

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
        PROJ-208 Phase 3: Route through facade for CQRS consistency.

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
        # PROJ-382 Phase 1: facade is required; no session fallback.
        self.facade.handle_command(cmd)

    def _dispatch_remove_from_queue_command(self, item_index: int) -> None:
        """Dispatch RemoveFromConstructionQueueCommand through command pipeline.

        PROJ-208: Routes build queue removals (drag-from-queue) through CQRS command system.
        PROJ-208 Phase 3: Route through facade for CQRS consistency.
        BUG-103: Pass queue_id for multi-queue entities (facility queues).

        Args:
            item_index: Index of the item to remove from the active queue.
        """
        from game.strategy.engine.commands import RemoveFromConstructionQueueCommand

        # Determine entity from active queue source
        source = self.active_queue_source
        if source is None:
            # Fallback to build_context
            entity = self.build_context
        else:
            entity = source.owner_entity

        from game.strategy.engine.commands import BuildEntityType
        entity_type = BuildEntityType.PLANET if hasattr(entity, 'planet_type') else BuildEntityType.FLEET
        entity_id = getattr(entity, 'id', 0)
        queue_id = getattr(source, 'queue_id', None) if source is not None else None

        cmd = RemoveFromConstructionQueueCommand(
            entity_id=entity_id,
            entity_type=entity_type,
            item_index=item_index,
            queue_id=queue_id,
        )
        # PROJ-382 Phase 1: facade is required; no session fallback.
        self.facade.handle_command(cmd)

    def _dispatch_toggle_pause_command(self) -> None:
        """FEAT-17 — flip the active queue source's paused flag.

        Resolves the active queue source's owner entity (Planet or Fleet) and
        the optional facility queue_id, then dispatches
        SetBuildQueuePausedCommand with the inverted current state.
        """
        from game.strategy.engine.commands import (
            SetBuildQueuePausedCommand,
            BuildEntityType,
        )

        source = self.active_queue_source
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
        self.facade.handle_command(cmd)

        # Re-collect sources so the active source's `is_paused` reflects the
        # new state, then refresh the button label + queue display.
        # PROJ-382 Phase 1: registries pulled through facade rather than session.
        self.queue_sources = collect_build_queues_at_hex(
            self.hex_coord, self.galaxy, self.empire,
            registries=self.facade.get_registries(),
        )
        # Re-bind the active source by queue_id (same reference may not exist
        # after re-collection — match by identifier).
        for s in self.queue_sources:
            if s.queue_id == source.queue_id:
                self.active_queue_source = s
                self.controller.set_active_queue(s)
                break
        self._refresh_queue_display()

    # -----------------------------------------------------------------------
    # Refresh Methods (delegate to renderer)
    # -----------------------------------------------------------------------

    def _refresh_items_list(self) -> None:
        """Refresh the items list based on selected category."""
        designs, roles_list = self.controller.load_designs_by_category(self.controller.selected_category)
        self.renderer.refresh_items_list(designs, self.controller.selected_category)
        if hasattr(self.renderer, 'refresh_roles_list'):
            self.renderer.refresh_roles_list(roles_list, getattr(self.controller, 'selected_role', 'Any'))

    def _refresh_queue_display(self) -> None:
        """Refresh the build queue display via VirtualTable."""
        is_multi = len(self.selected_queue_indices) > 1
        queue = self._get_active_queue() if not is_multi else []

        # Get build rate from active queue source
        build_rate = {}
        if self.active_queue_source is not None:
            build_rate = self.active_queue_source.build_rate or {}

        self.renderer.refresh_queue_display(
            queue=queue,
            build_rate=build_rate,
            on_queue_selector_refresh=self._refresh_queue_selector,
        )
        # FEAT-17: re-sync pause button label after each refresh (covers
        # toggle commands that mutate the active source's `is_paused`).
        self.renderer.refresh_pause_button(self.active_queue_source)

    def _refresh_queue_selector(self) -> None:
        """Rebuild queue selector UI elements."""
        if self._queue_selector:
            self._queue_selector.refresh()

    # -----------------------------------------------------------------------
    # Event Handling
    # -----------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle UI events for the build queue screen."""
        # PROJ-376 Phase 1: defensive visibility gate. Pre-Phase-2 the manager
        # still constructs and shows the screen synchronously, so this is a
        # no-op for legacy callers; it guards against post-Phase-2 paths where
        # a hidden screen might still receive events.
        if not self.is_visible():
            return
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
        elif event.ui_element == panels.btn_category_drop_pod:
            self.controller.set_category("drop_pod")
            self._refresh_items_list()
        elif event.ui_element == panels.btn_category_mine:
            self.controller.set_category("mine")
            self._refresh_items_list()

        # Close button
        elif event.ui_element == panels.btn_close:
            self._request_close()

        # FEAT-17: Pause/Unpause toggle for the active queue source
        elif event.ui_element == panels.btn_pause_queue:
            self._dispatch_toggle_pause_command()

        # Check action column in virtual table
        action_match = panels.virtual_table.check_action_button_press(event.ui_element)
        if action_match:
            action, row_idx = action_match
            self._handle_virtual_table_action(action, row_idx)
            return

        # Check role filter buttons
        if hasattr(event.ui_element, 'role_filter'):
            self.controller.set_role(event.ui_element.role_filter)
            self._refresh_items_list()
            return

        # Check Add to Queue in available designs
        if hasattr(event.ui_element, 'is_add_to_queue_btn') and event.ui_element.is_add_to_queue_btn:
            self.controller.add_to_queue(event.ui_element.design_id)
            return

        # Queue selector button clicks
        elif self._queue_selector and self._queue_selector.handle_button_click(
            event.ui_element, bool(pygame.key.get_mods() & pygame.KMOD_CTRL)
        ):
            pass  # Handled by selector

    def _handle_virtual_table_action(self, action: str, row_idx: int) -> None:
        """Handle virtual table action button press."""
        if len(self.selected_queue_indices) > 1:
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
            self.controller.add_to_queue(design_id, 1.0, category)
        elif action == "up":
            if row_idx > 0:
                self._dispatch_remove_from_queue_command(row_idx)
                self.controller.add_to_queue(design_id, turns, category, row_idx - 1)
        elif action == "down":
            if row_idx < len(active_queue) - 1:
                self._dispatch_remove_from_queue_command(row_idx)
                self.controller.add_to_queue(design_id, turns, category, row_idx + 1)

    def _handle_remove(self) -> None:
        """Handle remove from queue action.

        PROJ-208: Routes removal through RemoveFromConstructionQueueCommand.
        """
        if len(self.selected_queue_indices) > 1:
            logger.warning("Cannot remove items in multi-select mode")
            return

        remove_queue = self._get_active_queue()
        if self.selected_queue_index is not None and self.selected_queue_index < len(remove_queue):
            design_id = remove_queue[self.selected_queue_index].get('design_id', 'Unknown')
            self._dispatch_remove_from_queue_command(self.selected_queue_index)
            logger.info(f"Removed {design_id} from queue at index {self.selected_queue_index}")
            self.selected_queue_index = None
            self._refresh_queue_display()
        else:
            logger.warning("No queue item selected to remove")

    def _handle_drag_operations(self, event: pygame.event.Event) -> None:
        """Handle mouse events for drag-and-drop.

        PROJ-221 Phase 4: Adapted to work with VirtualTable. Queue item
        click detection now uses VirtualTable.handle_click() for row
        identification, with the drag handler still managing drag state.
        """
        multi_select = len(self.selected_queue_indices) > 1
        active_queue = self._get_active_queue()
        virtual_table = self.panels.virtual_table

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.drag_handler.handle_mouse_down(
                event, self.panels.items_scrollable,
                virtual_table, active_queue,
                self.controller.selected_category,
                multi_select_active=multi_select
            )

        if event.type == pygame.MOUSEMOTION and event.buttons[0]:
            self.drag_handler.handle_mouse_motion(
                event, active_queue, multi_select_active=multi_select
            )

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            result = self.drag_handler.handle_mouse_up(
                event, self.panels.build_queue_panel,
                virtual_table, active_queue,
                multi_select_active=multi_select
            )
            if result is not None:
                self.selected_queue_index = result
                if result < len(active_queue):
                    design_id = active_queue[result].get('design_id')
                    if design_id:
                        self.controller.refresh_design_report(design_id)

    def _handle_keyboard_input(self, event: pygame.event.Event) -> None:
        """Handle keyboard events."""
        self._handle_keydown(event)

    def _handle_keydown(self, event: pygame.event.Event) -> bool:
        """Dispatch keyboard events via InputMapper."""
        if not self._mapper:
            return False
        action = self._mapper.resolve(event, contexts=["build_queue"])
        if action == InputAction.BUILD_QUEUE_CLOSE:
            self._request_close()
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
        rect = pygame.Rect(200, 100, 950, 650)
        # PROJ-397 Phase 3 Task 3.2: pass the strategy facade so colonized
        # planets render the PROJ-289 per-species sub-block.
        self.planet_selection_window = PlanetSelectionWindow(
            rect,
            self.manager,
            planets,
            on_selected,
            window_manager=None,  # PROJ-313: build queue screen has its own modal lifecycle
            window_title="Select Target Planet",
            list_label="Colonies in sector:",
            show_any_button=False,
            facade=self.facade,
        )
        logger.info(f"BuildQueue: Opened planet selection for {len(planets)} colonies")

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
        self.hide()
        if self.on_close:
            self.on_close()

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
        if self.is_visible():
            self.hide()
        if self.panels is not None:
            self.panels.virtual_table.invalidate_widget_caches()
        self.queue_sources = []
        self.active_queue_source = None
        self.selected_queue_indices = set()

    def update(self, time_delta: float) -> None:
        """Update the UI manager."""
        self.manager.update(time_delta)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the UI."""
        self.manager.draw_ui(screen)
        self.drag_handler.draw_drag_preview(screen)

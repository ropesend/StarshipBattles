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

from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode
from game.core.profiling import profile_action

logger = logging.getLogger(__name__)
from game.ui.panels.build_queue_portraits import BuildQueuePortraitLoader
from game.ui.panels.build_queue_drag_handler import BuildQueueDragHandler
from game.ui.panels.build_queue_controller import BuildQueueController
from game.strategy.data.build_queue_source import BuildQueueSource, collect_build_queues_at_hex
from game.ui.screens.build_queue_helpers import format_empire_resources
from game.ui.screens.build_queue_input_router import BuildQueueInputRouter
from game.ui.screens.build_queue_panel_factory import BuildQueuePanelFactory
from game.ui.screens.build_queue_renderer import BuildQueueRenderer
from game.strategy.services.planet_economy_projector import compute_planet_production

if TYPE_CHECKING:
    from game.ui.services.input_mapper import InputMapper
    from game.core.hex_math import HexCoord
    from game.strategy.data.galaxy import Galaxy
    from game.strategy.data.empire import Empire
    from game.strategy.systems.design_catalog import DesignCatalog
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
        on_close_callback: Optional[Callable] = None,
        portrait_surface: Optional[pygame.Surface] = None,
        design_catalog: 'DesignCatalog' = None,
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
        (only when ``initial_yard`` is provided). When ``initial_yard is None``
        the screen constructs in shell-only mode — no panels, controller, or
        drag handler — and waits for ``open_for_yard()`` to populate the
        panel tree on first open.

        PROJ-456 Phase 2: the legacy ``build_context`` positional/keyword
        constructor arg was retired; ``initial_yard`` (keyword-only) is the
        canonical entry point for an eager-population first yard.
        """
        effective_initial_yard = initial_yard

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
        self.design_catalog = design_catalog
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

        # Portrait loading — needs design_catalog + a narrow theme-id
        # supplier for empire-theme lookup (PROJ-396 MAJ-002).
        self.portrait_loader = BuildQueuePortraitLoader(
            design_catalog, self._theme_id_supplier
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

        # PROJ-457 Phase 1: input routing + command dispatch + refresh
        # helpers extracted to a sibling module. Constructed here so it is
        # available when ``_construct_collaborators`` wires callbacks
        # pointing at the router's methods.
        self._input_router = BuildQueueInputRouter(self)

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
                registries=self.facade.session_meta.registries(),
            ),
            portrait_loader=self.portrait_loader,
            on_queue_selection_changed=self._input_router._on_queue_selection_changed,
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
            design_catalog=self.design_catalog,
            design_loader=self.design_loader,
            design_report=self.panels.design_report,
            on_queue_changed=self._input_router._refresh_queue_display,
            hex_coord=hex_coord,
            galaxy=self.galaxy,
            empire=self.empire,
            on_planet_selection_needed=self._input_router._prompt_target_planet,
            add_to_queue_callback=self._input_router._dispatch_add_to_queue_command,
            registries=self.facade.session_meta.registries(),
        )
        # PROJ-208: drag handler wires through controller's add/refresh.
        self.drag_handler = BuildQueueDragHandler(
            portrait_loader=self.portrait_loader,
            design_catalog=self.design_catalog,
            on_add_to_queue=self.controller.add_to_queue,
            on_refresh_queue=self._input_router._refresh_queue_display,
            on_refresh_design_report=self.controller.refresh_design_report,
            on_remove_from_queue=self._input_router._dispatch_remove_from_queue_command,
        )
        self._input_router._apply_tooltips()

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
        prev_yard = self.build_context

        # Decide whether to rebuild panels.
        if self.panels is None:
            # Shell-only first open — construct the collaborators.
            self._construct_collaborators(yard, hex_coord, portrait_surface)
        elif prev_type is not None and prev_type != new_type:
            # Cross-context-type transition (planet ↔ fleet) — rebuild.
            self._rebuild_panels(yard, hex_coord, portrait_surface)
        elif new_type == "fleet" and prev_yard is not yard:
            # Obs 2: fleet info panel has no refresh_fleet() API.
            # When swapping between two distinct fleets on the same screen
            # the cheapest correct path is a panel rebuild — the fleet
            # info panel is small (a single UITextBox), so the rebuild
            # cost is negligible. Same-yard re-opens skip this and reuse.
            self._rebuild_panels(yard, hex_coord, portrait_surface)
        elif (
            new_type == "planet"
            and self.panels.planet_report is not None
            and prev_yard is not yard
        ):
            # Obs 2: planet→planet on a cached screen — refresh the
            # PlanetReportPanel in place. Mirrors the arg shape used by
            # ``BuildQueuePanelFactory._create_context_report_panel`` at
            # construction time so the post-refresh state matches a
            # fresh open. ``update_planet`` is the existing in-place
            # refresh primitive (planet_report_panel.py:320-385).
            view = None
            if yard.owner_id is not None:
                view = self.facade.economy.colony_demographic_view(yard.id)
            self.panels.planet_report.update_planet(
                planet=yard,
                portrait_surface=portrait_surface,
                production_rates=compute_planet_production(
                    yard, self.facade.session_meta.registries()
                ),
                view=view,
            )

        # Update yard-specific state.
        self.build_context = yard
        self.hex_coord = hex_coord
        if portrait_surface is not None:
            self.portrait_surface = portrait_surface
        self.queue_sources = collect_build_queues_at_hex(
            hex_coord, self.galaxy, self.empire,
            registries=self.facade.session_meta.registries(),
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
        # PROJ-376: design_catalog may differ between Planet and Fleet manager
        # call sites (each constructs a fresh DesignCatalog). Rebind so the
        # drag handler always reflects the current manager's library.
        self.drag_handler.design_catalog = self.design_catalog
        # QA Obs 2 (2026-05-16): same rebind for the controller. PROJ-410
        # Phase 4 Task 4.2 covers screen.design_catalog + drag_handler but
        # missed the controller's own reference set in _rebuild_panels
        # (~line 229). Without this, controller.scan_designs() reads from
        # the previous empire's designs folder after a hot-seat swap.
        self.controller.design_catalog = self.design_catalog
        self.controller.design_loader = self.design_loader

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
        self._input_router._refresh_items_list()
        self._input_router._refresh_queue_display()

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

    # PROJ-457 Phase 1: input routing, command dispatch, refresh helpers,
    # and modal helpers were extracted to BuildQueueInputRouter (sibling
    # module). Tests reaching through retired-shape methods (e.g.
    # screen._request_close) now call them on screen._input_router.

    def handle_event(self, event: pygame.event.Event) -> None:
        """IScene event entry — delegates to the input router."""
        self._input_router.handle_event(event)

    def on_active_player_changed(self) -> None:
        """PROJ-410 Phase 4 Task 4.1: flush cached UI state on player change."""
        self._input_router.on_active_player_changed()

    def update(self, time_delta: float) -> None:
        """Update the UI manager."""
        self.manager.update(time_delta)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the UI."""
        self.manager.draw_ui(screen)
        self.drag_handler.draw_drag_preview(screen)

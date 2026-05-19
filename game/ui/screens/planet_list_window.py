"""
Planet List Window - Displays a filterable, sortable list of planets.

Provides comprehensive planet management with filtering, sorting, and presets.

PROJ-188 Phase 3: Migrated to VirtualTable + PlanetDataSource + SingleSelect.
PROJ-329C Phase 3: two-stage construction with ``ui_builder`` test seam
+ ``PlanetListController`` for facade-coupled queries.
PROJ-457 Phase 2: helpers + production builder extracted to
``planet_list_helpers``; event dispatch + selection coordination
extracted to ``planet_list_event_router.PlanetListEventRouter``.
"""
from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING
import pygame

from game.core.profiling import profile_action
from game.ui.screens.planet_list_controller import PlanetListController
from game.ui.screens.strategy_modal_window import StrategyModalWindow
from game.ui.screens.data_list_window_mixin import DataListWindowMixin
from game.ui.screens.planet_list_event_router import PlanetListEventRouter
from game.ui.screens.planet_list_helpers import (
    PlanetListUiBuilder,
    _format_population,
    _get_planetary_ids,
    build_effect_columns,
)

if TYPE_CHECKING:
    from game.ui.screens.strategy_window_manager import StrategyWindowManager


from game.ui.config import UIConfig
import logging

logger = logging.getLogger(__name__)
from game.ui.screens.planet_list_filters import (
    gather_planets, filter_planets, sort_planets,
    compute_planet_ranges, get_system_name, get_owner_name, get_mass_earth, get_resource_str,
    compute_planet_effect_keys,
)
from game.ui.screens.planet_list_presets import PresetManager, capture_planet_list_state, apply_planet_list_state
from game.ui.filters.filter_state import FilterState
from game.ui.screens.planet_list_filter_manager import PlanetListFilterManager
from game.ui.components.table import TableColumnManager


class PlanetListWindow(DataListWindowMixin, StrategyModalWindow):
    # Issue #28: opts into the per-player UI view-state container.
    # ``StrategyGameStateManager`` reads this attribute when iterating
    # snapshot windows.
    SNAPSHOT_SLOT: str = "planet_list"

    @profile_action("Panel: PlanetRegistry.window_init")
    def __init__(self, rect, manager, galaxy, empire, *,
                 window_manager: "StrategyWindowManager",
                 on_close_callback=None, asset_resolver=None, empires=None,
                 registries=None, on_navigate_callback=None,
                 race_registry=None, facade=None,
                 ui_builder: Optional[PlanetListUiBuilder] = None,
                 controller: Optional[PlanetListController] = None):
        # ---- Stage 1: cheap state + delegates (no facade I/O) ----
        # State that set_dimensions() may depend on must exist before the
        # super().__init__() call, since UIWindow.__init__ can trigger
        # rebuild() -> set_dimensions().
        self.selected_planet = None
        self.planet_detail_panel = None
        self.btn_build_queue = None
        self.btn_navigate = None
        self.last_preset_selection = None  # PROJ-199: lazy init elimination

        # PROJ-347 T4.1b (Pattern §33 widget-ref placeholders): set widget
        # slots populated by the production builder to None up front, so a
        # NullPlanetListWindowUiBuilder test can safely call kill() without
        # AttributeError on `self.virtual_table.kill()`. The production
        # builder overwrites these in Stage 3.
        self.virtual_table = None
        self.sidebar_panel = None
        self.main_panel = None
        self.data_source = None
        self.column_manager = None
        self.selection = None
        self._registries = registries  # PROJ-211: injected registries (DI)
        self._race_registry = race_registry  # PROJ-290
        # PROJ-292 H1: facade enables per-species sub-block rendering on
        # colonized planets via ``get_colony_demographic_view(planet.id)``.
        self._facade = facade

        self.galaxy = galaxy
        self.empire = empire  # Current player empire
        self.empires = empires or []  # PROJ-198: all empires for owner lookup
        self.on_close_callback = on_close_callback
        # PROJ-348 T5.3: navigate dispatch routes through controller (line ~321);
        # window no longer caches the callback. Parameter still threads to the
        # controller via the constructor passthrough below.
        self.asset_resolver = asset_resolver

        # Layout constants
        self.sidebar_width = UIConfig.REGISTRY_SIDEBAR_WIDTH
        self.header_height = UIConfig.HEADER_HEIGHT
        self.row_height = UIConfig.ROW_HEIGHT_LARGE
        self.detail_panel_width = 580
        self.panel_margin = 20

        # Filter / preset state
        # PROJ-411 Phase 1: pass facade_state when available so the
        # per-turn cache short-circuits the galaxy walk on re-opens.
        # Use getattr to tolerate test stubs that lack `facade_state`.
        _proj411_state = getattr(facade, "facade_state", None) if facade is not None else None
        self.all_planets = gather_planets(galaxy, empire, facade_state=_proj411_state)
        self.filtered_planets: list = []
        self.preset_manager = PresetManager()
        self._filter_mgr = PlanetListFilterManager()
        # Issue #28: per-empire view-state is now centrally orchestrated
        # via ``StrategyGameStateManager._per_player_ui_state``. The
        # window opts in by exposing ``SNAPSHOT_SLOT``,
        # ``capture_view_state`` and ``apply_view_state``. The pristine
        # post-Stage-3 snapshot below is the "fresh empire" default
        # applied when the central container returns None.
        self._default_filter_snapshot: dict | None = None

        # Compute dynamic filter ranges from actual planet data
        self._planet_ranges = compute_planet_ranges(self.all_planets)
        self._filter_mgr.filter_ranges = {
            'gravity': [self._planet_ranges['gravity'][0], self._planet_ranges['gravity'][1]],
            'temp': [self._planet_ranges['temp'][0], self._planet_ranges['temp'][1]],
            'mass': [self._planet_ranges['mass'][0], self._planet_ranges['mass'][1]],
        }

        self.ui_filters: dict = {}

        # Default columns (owner column captures self.galaxy/empire references)
        self.columns = [
            {'id': 'icon', 'width': 50, 'title': '', 'type': 'image', 'visible': True},
            {'id': 'name', 'width': 150, 'title': 'Name', 'attr': 'name', 'visible': True},
            {'id': 'type', 'width': 100, 'title': 'Type', 'attr': 'planet_type.name', 'visible': True},
            {'id': 'system', 'width': 120, 'title': 'System', 'func': get_system_name, 'visible': True},
            {'id': 'owner', 'width': 140, 'title': 'Owner', 'func': lambda p: get_owner_name(p, self.empires, self.empire), 'visible': True},
            {'id': 'mass', 'width': 100, 'title': 'Mass (M_E)', 'func': get_mass_earth, 'visible': True},
            {'id': 'grav', 'width': 90, 'title': 'Grav (g)', 'func': lambda p: f"{p.surface_gravity/9.81:.2f}", 'visible': True},
            {'id': 'temp', 'width': 90, 'title': 'Temp (K)', 'attr': 'surface_temperature', 'fmt': "{:.0f}", 'visible': True},
            {'id': 'water', 'width': 90, 'title': 'Water %', 'attr': 'surface_water', 'fmt': "{:.0%}", 'visible': False},
            {'id': 'pressure', 'width': 100, 'title': 'Press (atm)', 'attr': 'total_pressure_atm', 'fmt': "{:.2f}", 'visible': False},
            {'id': 'population', 'width': 120, 'title': 'Population', 'func': lambda p: _format_population(p), 'visible': False},
        ]
        for res in _get_planetary_ids():
            self.columns.append({
                'id': f'res_{res}',
                'width': 110,
                'title': res,
                'func': lambda p, r=res: get_resource_str(p, r),
                'visible': False,
            })

        # FEAT-16: per-effect columns (one per intrinsic-ability group-key
        # present in the loaded galaxy). Hidden by default. Empty galaxy →
        # zero columns added.
        self._effect_keys = compute_planet_effect_keys(self.all_planets)
        self.columns.extend(build_effect_columns(self._effect_keys))

        # FEAT-25: seed manager filter_effects with FilterState.IGNORE per
        # discovered effect group-key (no-op default).
        self._filter_mgr.filter_effects = {
            k: FilterState.IGNORE for k in self._effect_keys
        }

        # PROJ-329C controller — wraps the facade's
        # ``get_colony_demographic_view`` plus the navigate callback.
        self.controller = controller or PlanetListController(
            facade=facade,
            on_navigate_callback=on_navigate_callback,
        )

        # PROJ-457 Phase 2: event dispatch + selection coordination
        # extracted to PlanetListEventRouter. Instantiated here so the
        # router is ready when Stage 3 builder finishes (and for tests
        # that exercise event handling via the router directly).
        self._event_router = PlanetListEventRouter(self)

        # ---- Stage 2: shell ----
        super().__init__(
            rect, manager,
            window_display_title="Galactic Planet Registry",
            resizable=True,
            window_manager=window_manager,
        )

        # ---- Stage 3: widgets ----
        if getattr(self, '_window_init_bypassed', False):
            if ui_builder is not None:
                ui_builder.build(self)
            return

        (ui_builder or PlanetListUiBuilder()).build(self)
        # PROJ-411 Task 2.10: snapshot the pristine post-build filter
        # state so empire switches that see a new empire for the first
        # time apply defaults instead of inheriting the prior empire's
        # filters.
        self._default_filter_snapshot = capture_planet_list_state(
            self.columns, self.txt_name_filter, self.filter_types,
            self.filter_owner, self.ui_filters,
            filter_effects=self.filter_effects,
        )

    # -----------------------------------------------------------------------
    # Filter state properties (delegate to PlanetListFilterManager)
    # -----------------------------------------------------------------------

    @property
    def filter_types(self) -> Any:
        """Planet type filter dict (mutable reference)."""
        return self._filter_mgr.filter_types

    @filter_types.setter
    def filter_types(self, value) -> None:
        """Set planet type filter dict."""
        self._filter_mgr.filter_types = value

    @property
    def filter_owner(self) -> Any:
        """Owner category filter dict (mutable reference)."""
        return self._filter_mgr.filter_owner

    @filter_owner.setter
    def filter_owner(self, value) -> None:
        """Set owner category filter dict."""
        self._filter_mgr.filter_owner = value

    @property
    def filter_effects(self) -> Any:
        """FEAT-16: Effects filter dict (mutable reference)."""
        return self._filter_mgr.filter_effects

    @filter_effects.setter
    def filter_effects(self, value) -> None:
        """Set Effects filter dict."""
        self._filter_mgr.filter_effects = value

    @property
    def filter_ranges(self) -> Any:
        """Range filter dict (mutable reference)."""
        return self._filter_mgr.filter_ranges

    @filter_ranges.setter
    def filter_ranges(self, value) -> None:
        """Set range filter dict."""
        self._filter_mgr.filter_ranges = value

    def refresh_list(self) -> None:
        """Filter and update scrollbar."""
        # 1. Update Filter State from UI (lazy sync)
        search = self.txt_name_filter.get_text()
        if search == "Search Name...":
            search = ""
        search_lower = search.lower() if search else ""

        min_g = self.ui_filters['gravity']['min'].get_current_value()
        max_g = self.ui_filters['gravity']['max'].get_current_value()
        min_t = self.ui_filters['temp']['min'].get_current_value()
        max_t = self.ui_filters['temp']['max'].get_current_value()
        min_m = self.ui_filters['mass']['min'].get_current_value()
        max_m = self.ui_filters['mass']['max'].get_current_value()

        # Use extracted filter function (BUG-27: added owner filter; FEAT-16: Effects)
        self.filtered_planets = filter_planets(
            self.all_planets, search_lower, self.filter_types,
            min_g, max_g, min_t, max_t, min_m, max_m,
            filter_owner=self.filter_owner, empire=self.empire,
            filter_effects=self.filter_effects,
        )

        # 1b. Sort using extracted function (use TableColumnManager state)
        sort_planets(
            self.filtered_planets,
            self.column_manager.sort_column_id,
            self.column_manager.sort_descending,
            self.columns,
        )

        # 2. Update DataSource with filtered planets
        self.data_source.update_data(self.filtered_planets)

        # 3. Update scrollbar and visible rows
        self.virtual_table.update_scroll_bar()
        self.virtual_table.force_update()
        self.virtual_table.update_visible_rows()
    def update(self, time_delta) -> None:
        super().update(time_delta)
        # PROJ-375 Task 3.2: shared scroll/slider/header/preset polling.
        self._run_update_template(['gravity', 'temp', 'mass'])
    def _capture_current_state(self) -> Any:
        """Serialize current filters and column config."""
        return capture_planet_list_state(
            self.columns, self.txt_name_filter, self.filter_types,
            self.filter_owner, self.ui_filters,
            filter_effects=self.filter_effects,
        )

    def _apply_state(self, state) -> None:
        """Restore state."""
        self.columns = apply_planet_list_state(
            state, self.columns, self.txt_name_filter,
            self.filter_types, self.ui_filters,
            filter_owner=self.filter_owner,
            filter_effects=self.filter_effects,
        )
        self.column_manager = TableColumnManager(self.columns)
        self.data_source._columns = self.columns
        self.virtual_table._column_manager = self.column_manager
        self.virtual_table.rebuild_headers()
        self.virtual_table.rebuild_row_pool()
        self.refresh_list()
    def process_event(self, event) -> bool:
        """Delegate event dispatch to PlanetListEventRouter (PROJ-457 Phase 2)."""
        return self._event_router.process_event(event)

    def _super_process_event(self, event) -> bool:
        """Internal hook used by PlanetListEventRouter to call the base-class
        ``process_event`` without re-entering this class's override."""
        return super().process_event(event)

    def set_dimensions(self, dimensions, clamp_to_container=False) -> None:
        """Handle window resize - reposition detail panel."""
        super().set_dimensions(dimensions, clamp_to_container)
        # Recreate the detail panel at new position if one is showing
        if self.selected_planet is not None:
            self._event_router._on_planet_selected(self.selected_planet)

    # ---- PROJ-411 Task 2.1: Window reuse (Track A) ----
    #
    # PROJ-376 BuildQueueScreen template. The X-button close path now
    # hides the window instead of killing it; the registrar keeps the
    # slot populated across user-close/re-open cycles. ``open_for_galaxy``
    # rebinds context and resets per-open state. Esc-close still calls
    # ``kill()`` for parity with the existing event-router contract.

    def on_close_window_button_pressed(self) -> None:
        """Override pygame_gui default kill() — hide for reuse instead."""
        self.hide()

    def request_close(self) -> None:
        """PROJ-411 Task 2.5: Esc close path uses hide() for reuse."""
        self.hide()

    # ``hide()`` / ``show()`` inherited from StrategyModalWindow base
    # (PROJ-411 Task 2.8 consolidated the reuse-hide/show logic there).

    def _post_show_hook(self) -> None:
        """Obs 3: re-assert row-pool visibility after the show cascade.

        pygame_gui's ``UIWindow.show()`` -> ``UIContainer.show(True)``
        recursively un-hides every descendant, re-exposing the
        out-of-range row-pool entries that ``update_visible_rows()``
        hid individually. Re-run the virtual table's visibility pass
        AFTER the cascade. Mirrors ``BuildQueueScreen.show()``.
        """
        vt = getattr(self, "virtual_table", None)
        if vt is not None:
            vt.force_update()
            vt.update_visible_rows()

    def open_for_galaxy(
        self,
        galaxy,
        empire,
        *,
        facade=None,
    ) -> None:
        """Rebind context + reset per-open state + show the window.

        Called by ``PlanetListRegistrar.open()`` when reusing an already-
        constructed instance instead of constructing a fresh one. Net
        cost should be <500 ms vs ~4.4 s for fresh construction.

        Issue #28: per-empire view-state save/restore on empire switch
        was removed from this method. It is now handled centrally by
        ``StrategyGameStateManager`` at turn rotation
        (``advance_turn`` captures, ``_apply_turn_start_state``
        restores). Same-turn re-opens preserve in-place state because
        the central swap only runs at turn boundaries.
        """
        self.galaxy = galaxy
        self.empire = empire
        self._facade = facade
        self.selected_planet = None

        self.show()
        self.refresh_list()

    def capture_view_state(self) -> dict:
        """Issue #28: snapshot current columns + filters + ranges.

        Called by ``StrategyGameStateManager._capture_outgoing_player_state``
        at turn-end. Delegates to the existing preset capture so the
        serialised shape matches preset save/load.
        """
        return capture_planet_list_state(
            self.columns, self.txt_name_filter, self.filter_types,
            self.filter_owner, self.ui_filters,
            filter_effects=self.filter_effects,
        )

    def apply_view_state(self, state: dict | None) -> None:
        """Issue #28: restore a previously-captured snapshot, or reset to defaults.

        ``state is None`` means the incoming empire has no saved
        snapshot (their first turn after this window opened). We apply
        the pristine ``_default_filter_snapshot`` captured at the end
        of Stage 3 so the new player starts from a fresh view rather
        than inheriting the outgoing player's filters.
        """
        target = state if state is not None else self._default_filter_snapshot
        if target is None:
            # Stage 3 was bypassed (test stub) and no default was
            # captured. Nothing to apply.
            return
        self.columns = apply_planet_list_state(
            target, self.columns, self.txt_name_filter,
            self.filter_types, self.ui_filters,
            filter_owner=self.filter_owner,
            filter_effects=self.filter_effects,
        )

    # ---- end PROJ-411 Task 2.1 ----

    def kill(self) -> None:
        # Clean up VirtualTable
        if self.virtual_table:
            self.virtual_table.kill()

        if self.planet_detail_panel:
            self.planet_detail_panel.kill()
            self.planet_detail_panel = None

        if self.btn_build_queue:
            self.btn_build_queue.kill()
            self.btn_build_queue = None

        if self.btn_navigate:
            self.btn_navigate.kill()
            self.btn_navigate = None

        if self.on_close_callback:
            self.on_close_callback()
        super().kill()


__all__ = [
    "PlanetListWindow",
    "PlanetListUiBuilder",
    "build_effect_columns",
]

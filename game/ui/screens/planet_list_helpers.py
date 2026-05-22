"""Planet-list helper functions + production UI builder.

PROJ-457 Phase 2: extracted from ``planet_list_window.py`` to bring the
window under the 500-LOC ceiling. Contains:

* ``_get_planetary_ids()`` — cached lookup of planetary-display-group
  resource IDs from the canonical ``ResourceCatalog``.
* ``_format_population(planet)`` — total-population cell renderer.
* ``_render_effect_cell(planet, group_key)`` — per-effect cell renderer
  (FEAT-16, with damage-type / resource-type discrimination).
* ``build_effect_columns(effect_keys)`` — per-effect column definitions
  (FEAT-16).
* ``PlanetListUiBuilder`` — production widget builder (Pattern §33
  two-stage construction; ``build(screen)`` populates the panel tree).
"""
from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

import pygame
from pygame_gui.elements import UIButton, UIPanel

from game.core.profiling import profile_action
from game.core.resources import ResourceCatalog
from game.strategy.services.system_effects_collector import (
    format_intrinsic_ability_magnitude,
    make_display_name as _effect_display_name,
)
from game.ui.components.table import (
    SingleSelect,
    TableColumnManager,
    VirtualTable,
)
from game.ui.screens.planet_data_source import PlanetDataSource
from game.ui.screens.planet_list_sidebar import build_sidebar
from game.ui.panels.planet_report_panel import format_compact_number

if TYPE_CHECKING:
    from game.ui.screens.planet_list_window import PlanetListWindow


@lru_cache(maxsize=1)
def _get_planetary_ids() -> tuple[str, ...]:
    """PROJ-397 F-07: lazy-load planetary resource IDs (was module-level)."""
    return tuple(
        d.id for d in ResourceCatalog.from_json().by_display_group("planetary")
    )


def _format_population(planet) -> str:
    """Format total planet population for the list column."""
    pops = getattr(planet, 'populations', [])
    if not pops:
        return "—"
    total = sum(getattr(p, 'count', 0) for p in pops)
    return format_compact_number(total) if total > 0 else "—"


def _render_effect_cell(planet, group_key: str) -> str:
    """Render a planet's magnitude for one effect group-key, or '—' if absent.

    FEAT-16: used as the `func` for per-effect columns. Discriminates by
    damage_type for EnvironmentalDamage so a thermal-damage planet renders
    blank in the :radiation column and vice versa.
    """
    abilities = getattr(planet, 'intrinsic_abilities', None) or {}
    if ':' in group_key:
        ability_name, _discriminator = group_key.split(':', 1)
    else:
        ability_name = group_key
    data = abilities.get(ability_name)
    if data is None:
        return "—"
    # Confirm the planet's instance matches the same group-key (so a
    # radiation-damage planet doesn't render in the thermal-damage column).
    from game.strategy.services.system_effects_collector import make_group_key
    if make_group_key(ability_name, data) != group_key:
        return "—"
    rendered = format_intrinsic_ability_magnitude(ability_name, data)
    return rendered if rendered else "—"


@profile_action("Panel: PlanetRegistry.build_effect_columns")
def build_effect_columns(effect_keys: list[str]) -> list[dict]:
    """Build per-effect column definitions for the Planet List (FEAT-16).

    Args:
        effect_keys: Sorted group-keys produced by `compute_planet_effect_keys`.

    Returns:
        List of column dicts (id='effect_<group_key>', title=display name,
        func=cell renderer, visible=False). One column per key. When the
        list is empty (no planet has any effect) the result is empty.
    """
    columns: list[dict] = []
    for group_key in effect_keys:
        if ':' in group_key:
            ability_name, discriminator = group_key.split(':', 1)
            data = {'damage_type': discriminator, 'resource_type': discriminator}
        else:
            ability_name = group_key
            data = {}
        title = _effect_display_name(ability_name, data)
        columns.append({
            'id': f'effect_{group_key}',
            'width': 130,
            'title': title,
            'func': lambda p, gk=group_key: _render_effect_cell(p, gk),
            'visible': False,
        })
    return columns


class PlanetListUiBuilder:
    """Production widget builder for ``PlanetListWindow``.

    Builds the column list (default + per-resource + per-effect),
    sidebar widgets via ``build_sidebar``, the main panel + virtual
    table, the navigate button, and runs the initial ``refresh_list()``.

    The builder reads cheap-state attrs the screen pre-populated in
    Stage 1 (``galaxy``, ``empire``, ``all_planets``, ``preset_manager``,
    ``_filter_mgr``, ``_planet_ranges``, ``sidebar_width``,
    ``header_height``, ``row_height``, ``detail_panel_width``,
    ``panel_margin``, ``columns``, ``_effect_keys``) and writes the
    widget references the rest of the class operates on (sidebar
    references, ``main_panel``, ``column_manager``, ``data_source``,
    ``selection``, ``virtual_table``, ``btn_navigate``).
    """

    def build(self, screen: "PlanetListWindow") -> None:
        rect = screen.rect
        manager = screen.ui_manager

        # --- Sidebar ---
        screen.sidebar_panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, screen.sidebar_width, rect.height - 50),
            manager=manager,
            container=screen,
            anchors={'left': 'left', 'top': 'top', 'bottom': 'bottom'}
        )

        sidebar_widgets = build_sidebar(
            manager=manager,
            sidebar_panel=screen.sidebar_panel,
            sidebar_width=screen.sidebar_width,
            rect_height=rect.height,
            planet_ranges=screen._planet_ranges,
            columns=screen.columns,
            preset_manager=screen.preset_manager,
            effect_keys=screen._effect_keys,
        )
        screen.sidebar_scroller = sidebar_widgets['sidebar_scroller']
        screen.txt_name_filter = sidebar_widgets['txt_name_filter']
        screen.btn_all_types = sidebar_widgets['btn_all_types']
        screen.btn_none_types = sidebar_widgets['btn_none_types']
        screen.btn_all_owners = sidebar_widgets['btn_all_owners']
        screen.btn_none_owners = sidebar_widgets['btn_none_owners']
        screen.btn_all_effects = sidebar_widgets['btn_all_effects']
        screen.btn_none_effects = sidebar_widgets['btn_none_effects']
        screen.btn_apply = sidebar_widgets['btn_apply']
        screen.btn_save_preset = sidebar_widgets['btn_save_preset']
        screen.txt_preset_name = sidebar_widgets['txt_preset_name']
        screen.dd_presets = sidebar_widgets['dd_presets']
        screen.ui_filters = sidebar_widgets['ui_filters']

        # --- Main content area ---
        main_w = (
            rect.width - screen.sidebar_width - screen.detail_panel_width
            - screen.panel_margin - 10
        )
        screen.main_panel = UIPanel(
            relative_rect=pygame.Rect(
                screen.sidebar_width, 0, main_w, rect.height - 90
            ),
            manager=manager, container=screen,
            anchors={'left': 'left', 'right': 'right',
                     'top': 'top', 'bottom': 'bottom'},
        )

        # PROJ-188: virtual table infrastructure
        screen.column_manager = TableColumnManager(screen.columns)
        # BUG-23: default sort by owner ascending
        screen.column_manager.sort_column_id = 'owner'
        screen.column_manager.sort_descending = False

        # PROJ-477 Phase 4: PlanetDataSource takes the scene.world seam for
        # context (the stored handle is unused for traversal; owner lookup uses
        # the precomputed empires list on the columns).
        screen.data_source = PlanetDataSource(
            screen.columns, screen.world, screen.empire
        )
        screen.selection = SingleSelect()

        screen.virtual_table = VirtualTable(
            panel=screen.main_panel,
            manager=manager,
            data_source=screen.data_source,
            column_manager=screen.column_manager,
            selection_strategy=screen.selection,
            row_height=screen.row_height,
            header_height=screen.header_height,
        )

        # Navigate button (bottom of main area)
        nav_y = rect.height - 80
        screen.btn_navigate = UIButton(
            relative_rect=pygame.Rect(
                screen.sidebar_width + 10, nav_y, 180, 30
            ),
            text="Navigate to Planet",
            manager=manager,
            container=screen,
        )

        # Initial population
        screen.refresh_list()

"""
Planet Report Panel - Reusable widget for displaying planet information.

This widget encapsulates the planet detail display from the strategy screen,
showing planet portrait, comprehensive stats, and atmosphere composition graph.
"""
from __future__ import annotations


import os
from typing import Dict, List, Optional

import pygame
import pygame_gui
from pygame_gui.elements import UIImage, UITextBox, UIPanel, UIScrollingContainer, UILabel
from game.core.paths import Paths
from game.ui.screens.strategy_detail_fmt import format_planet_info
from game.ui.fonts import get_font
from game.ui.utils.formatters import format_compact_number, format_signed_float

from game.ui.panels.strategy_widgets import AtmosphereGraph
from game.ui.panels.build_queue_portraits import RESOURCE_PORTRAIT_FILES, RESOURCE_FALLBACK_COLORS
from game.ui.utils.resource_display import (
    get_displayed_resource_ids,
    get_resource_abbreviation,
)
from game.ui.colors import (
    PLANET_TERRESTRIAL, PLANET_GAS_GIANT, PLANET_ICE, PLANET_ROCKY, PLANET_OCEANIC,
    TEXT_DIM, WHITE, TEXT_LIGHT, HP_HEALTHY, HP_CRITICAL,
)
from collections import Counter


# Catalog-driven resource list. Adding a resource to data/resources.json
# (with a `display_group` of "planetary" or "operational") adds a column
# to this grid with no code change.
_DISPLAYED_RESOURCES: List[str] = get_displayed_resource_ids()


# Row labels for the transposed grid, in render order. The header row is
# index 0 (icons + abbreviations) and is constructed by the build method;
# only the data-row labels appear in this list.
_DATA_ROW_LABELS = ("Qty", "Qual", "Harvest", "Upkeep", "Yard", "Net", "Stored", "Cap")


def _projection_grid_rows(planet, view, displayed_ids: List[str]) -> List[tuple]:
    """Return the header + per-metric cell-text rows for the transposed
    icon-column grid.

    Pure data-shape function — no UI side effects, testable without pygame.

    Layout: each row is ``(row_label, *resource_cells)``. The header row's
    label is `""` and the per-resource cells are the resource ids (the
    build method renders them as icon + abbreviation). The 8 data rows
    are Qty, Qual, Harvest, Upkeep, Yard, Net, Stored, Cap.

    Cell rules:
      * Qty / Qual — from ``planet.deposits[res]``; ``"-"`` if absent.
      * Harvest / Upkeep / Yard / Net — from ``view.resource_projections``
        keyed by ``resource_id``. Sign convention: harvest as-is, upkeep
        and yard rendered as drains (negated), net as-is. Resources
        missing from projections (or ``view is None``) render ``"-"``.
      * Stored / Cap — from ``planet.stockpile`` / ``planet.max_stockpile``;
        ``"-"`` if the key is absent.
    """
    deposits = getattr(planet, "deposits", None) or {}
    stockpile = getattr(planet, "stockpile", None) or {}
    max_stockpile = getattr(planet, "max_stockpile", None) or {}

    proj_by_id = {}
    if view is not None:
        proj_by_id = {p.resource_id: p for p in view.resource_projections}

    rows: List[tuple] = [("",) + tuple(displayed_ids)]

    qty_cells = [_qty_cell(deposits.get(rid)) for rid in displayed_ids]
    qual_cells = [_qual_cell(deposits.get(rid)) for rid in displayed_ids]
    harvest_cells = [_flow_cell(proj_by_id.get(rid), "harvest") for rid in displayed_ids]
    upkeep_cells = [_flow_cell(proj_by_id.get(rid), "upkeep") for rid in displayed_ids]
    yard_cells = [_flow_cell(proj_by_id.get(rid), "yard") for rid in displayed_ids]
    net_cells = [_flow_cell(proj_by_id.get(rid), "net") for rid in displayed_ids]
    stored_cells = [_stockpile_cell(stockpile, rid) for rid in displayed_ids]
    cap_cells = [_stockpile_cell(max_stockpile, rid) for rid in displayed_ids]

    rows.append(("Qty", *qty_cells))
    rows.append(("Qual", *qual_cells))
    rows.append(("Harvest", *harvest_cells))
    rows.append(("Upkeep", *upkeep_cells))
    rows.append(("Yard", *yard_cells))
    rows.append(("Net", *net_cells))
    rows.append(("Stored", *stored_cells))
    rows.append(("Cap", *cap_cells))

    return rows


def _qty_cell(deposit) -> str:
    if not isinstance(deposit, dict):
        return "-"
    quantity = deposit.get("quantity", 0)
    if not quantity:
        return "-"
    return format_compact_number(quantity)


def _qual_cell(deposit) -> str:
    if not isinstance(deposit, dict):
        return "-"
    quality = deposit.get("quality", 0)
    if not quality:
        return "-"
    return f"{quality:.1f}"


def _flow_cell(proj, field: str) -> str:
    """One Harvest/Upkeep/Yard/Net cell. ``proj`` is None when the
    resource has no projection signal (operational resources, unowned
    planets) — render `-` so the column reads as "no data" rather than
    a misleading projected zero."""
    if proj is None:
        return "-"
    if field == "upkeep":
        return format_signed_float(-proj.upkeep, decimals=1)
    if field == "yard":
        return format_signed_float(-proj.yard, decimals=1)
    return format_signed_float(getattr(proj, field), decimals=1)


def _stockpile_cell(store: dict, rid: str) -> str:
    if rid not in store:
        return "-"
    return format_compact_number(store[rid])


def _net_cell_color(net: float) -> tuple[int, int, int]:
    """Colour for a Net cell — green positive, red negative, default zero.
    Reuses the existing HP colour constants (`HP_HEALTHY` / `HP_CRITICAL`)
    so the palette stays consistent with other "good vs bad" indicators."""
    if net > 0:
        return HP_HEALTHY
    if net < 0:
        return HP_CRITICAL
    return TEXT_LIGHT


# Height reserved for resource grid at bottom of panel. Sized so the
# default 8-data-row grid (header + 8 × row_h=20) fits without a vertical
# scrollbar at default screen sizes; the hosting UIScrollingContainer
# adds scrollbars only when the panel is shrunk or the catalog grows.
RESOURCE_PANEL_HEIGHT = 220


class PlanetReportPanel:
    """
    Reusable panel that displays comprehensive planet information.

    Components:
    - Portrait (150x150 at 10, 10)
    - Info text (UITextBox with HTML in middle — includes inline
      Staged Units block when the planet has staging-yard contents,
      QA-OBS-A)
    - Atmosphere graph (150px wide at 10, 170)
    - Complexes list (scrollable, right side)
    """

    def __init__(
        self,
        manager,
        rect,
        planet,
        container=None,
        portrait_surface=None,
        show_complexes=True,
        production_rates: Optional[Dict[str, float]] = None,
        view=None,
        empire=None,
        race_registry=None,
    ):
        """
        Initialize planet report panel.

        Args:
            manager: pygame_gui UIManager
            rect: pygame.Rect for panel dimensions
            planet: Planet object to display
            container: Optional parent container
            portrait_surface (pygame.Surface, optional): Pre-loaded portrait image.
                If provided, will be used instead of generating placeholder.
            show_complexes (bool, optional): Whether to show the complexes list.
                Defaults to True. Set to False for contexts like Strategy UI.
            production_rates (Dict[str, float], optional): Per-resource production rates.
                Used for the resource grid. Defaults to empty dict.
            view: Optional ``ColonyDemographicView`` (PROJ-289). Threaded through
                to ``format_planet_info`` so the per-species text is rendered
                as the indented sub-block (habitability / happiness / growth /
                food ratio / allocation). ``None`` keeps the legacy single-line
                fallback for callers without facade access.
            empire: PROJ-290 — optional viewing empire used to render the
                uncolonized-planet habitability section. Combined with
                `race_registry` below; either missing → section omitted.
            race_registry: PROJ-290 — optional `IRaceRegistry`. Required
                alongside `empire` to render the uncolonized habitability
                section. None preserves the pre-PROJ-290 rendering.
        """
        self.manager = manager
        self.rect = rect
        self.planet = planet
        self.container = container
        self._init_portrait_surface = portrait_surface
        self.production_rates = production_rates or {}
        self.view = view
        self._resource_icons: Dict[str, pygame.Surface] = {}
        self._resource_grid_items: List = []
        # Catalog-driven column set for the resource grid. Stored on the
        # instance so tests can pin it explicitly.
        self._displayed_resources: List[str] = list(_DISPLAYED_RESOURCES)
        # PROJ-290 — stored so `update_planet` can default to the
        # construction-time values when it's called without new deps.
        self._empire = empire
        self._race_registry = race_registry

        # Load resource icons
        self._load_resource_icons(icon_size=20)

        # Create panel container
        self.panel = UIPanel(
            relative_rect=rect,
            manager=manager,
            container=container
        )

        # Portrait (10, 10, 150, 150)
        self.portrait_image = UIImage(
            relative_rect=pygame.Rect(10, 10, 150, 150),
            image_surface=pygame.Surface((150, 150)),
            manager=manager,
            container=self.panel
        )

        # Reserve space for the right-side complexes column (200px wide)
        # when show_complexes=True. Staged-yard contents are rendered
        # inline within the detail_text by `format_planet_info` (QA-OBS-A),
        # so there is no separate staged-units column.
        complexes_width = 200
        complexes_gap = 10

        # Info text (170, 10, text_w, text_h) - width depends on whether
        # the complexes column is shown.
        # Height reduced to make room for resource panel at bottom
        if show_complexes:
            text_w = rect.width - 180 - complexes_width - complexes_gap
        else:
            text_w = rect.width - 180  # Only leave room for portrait and graph
        text_h = rect.height - 20 - RESOURCE_PANEL_HEIGHT
        self.detail_text = UITextBox(
            html_text=format_planet_info(
                planet, view=view, empire=empire, race_registry=race_registry,
            ),
            relative_rect=pygame.Rect(170, 10, text_w, text_h),
            manager=manager,
            container=self.panel
        )

        # Right-side complexes column (full height when shown).
        column_x = rect.width - complexes_width - 10
        complexes_h = rect.height - 20 - RESOURCE_PANEL_HEIGHT

        if show_complexes:
            self.complexes_container = UIScrollingContainer(
                relative_rect=pygame.Rect(column_x, 10, complexes_width, complexes_h),
                manager=manager,
                container=self.panel
            )
            UILabel(
                relative_rect=pygame.Rect(5, 5, complexes_width - 10, 25),
                text="Built Complexes",
                manager=manager,
                container=self.complexes_container
            )
            self.complex_items = []
        else:
            self.complexes_container = None
            self.complex_items = []

        # Atmosphere graph (10, 170, 150, graph_h)
        # Height reduced to make room for resource panel at bottom
        graph_y = 170
        graph_h = rect.height - 180 - RESOURCE_PANEL_HEIGHT
        if graph_h < 50:
            graph_h = 50

        self.graph_rect = pygame.Rect(10, graph_y, 150, graph_h)
        self.graph_image = UIImage(
            relative_rect=self.graph_rect,
            image_surface=pygame.Surface((150, graph_h)),
            manager=manager,
            container=self.panel
        )

        # Create atmosphere graph renderer with SWAPPED dimensions for rotation
        # Strategy screen uses AtmosphereGraph(height, width) then rotates -90 degrees
        self.graph = AtmosphereGraph(int(graph_h), 150)

        # Resource grid panel at bottom (PROJ-82). Hosted in a
        # UIScrollingContainer so horizontal/vertical scrollbars appear
        # automatically when the resource catalog or grid height grows
        # past the viewport (the same idiom used by EmpireTreasuryPanel).
        resource_y = rect.height - RESOURCE_PANEL_HEIGHT - 10
        self.resource_panel = UIScrollingContainer(
            relative_rect=pygame.Rect(10, resource_y, rect.width - 20, RESOURCE_PANEL_HEIGHT),
            manager=manager,
            container=self.panel
        )

        # Initial render
        self._update_portrait(portrait_surface)
        self._update_graph()
        self._update_complexes_list()
        self._build_resource_grid()

    def update_planet(
        self,
        planet,
        portrait_surface=None,
        production_rates: Optional[Dict[str, float]] = None,
        view=None,
        empire=None,
        race_registry=None,
    ) -> None:
        """
        Update display for a new planet.

        Args:
            planet: Planet object to display
            portrait_surface: Optional pygame Surface for planet portrait
            production_rates: Optional per-resource production rates for the grid
            view: Optional ``ColonyDemographicView`` (PROJ-289). When supplied,
                the planet info panel renders the per-species sub-block with
                habitability / happiness / growth / food ratio / allocation
                instead of the legacy single-line fallback. Resolved upstream
                via ``facade.get_colony_demographic_view(planet.id)`` —
                ``None`` for uncolonized planets or when the caller doesn't
                have facade access. Overwrites the construction-time view
                every call (explicit per-refresh policy from PROJ-289).
            empire: PROJ-290 — override the construction-time empire.
                When None, the panel reuses whatever was passed to
                `__init__` (both default to None → no habitability section).
            race_registry: PROJ-290 — override the construction-time
                `IRaceRegistry`. Same fallback contract as `empire`.

        PROJ-292 m1 — kwarg-fallback asymmetry:
            `view` is overwritten unconditionally on every call (PROJ-289
            policy). `empire` and `race_registry` use None-sentinel fallback
            (PROJ-290 policy) — passing None preserves the previous values
            from construction time. The asymmetry is intentional: `view`
            is per-planet (changes every selection), while empire +
            registry are per-session (constant across planet switches).
            Callers switching planets without changing session pass only
            `view`; callers rebinding session context pass both.
        """
        self.planet = planet
        self.production_rates = production_rates or {}
        # PROJ-289: overwrite unconditionally so callers can explicitly
        # pass view=None to revert to the legacy layout.
        self.view = view
        # PROJ-290: keyword-sentinel fallback — pass None to reuse the
        # construction-time values rather than clearing them.
        if empire is not None:
            self._empire = empire
        if race_registry is not None:
            self._race_registry = race_registry

        # Update info text
        self.detail_text.html_text = format_planet_info(
            planet,
            view=view,
            empire=self._empire,
            race_registry=self._race_registry,
        )
        self.detail_text.rebuild()

        # Update portrait, graph, complexes list, and resource grid
        self._update_portrait(portrait_surface)
        self._update_graph()
        self._update_complexes_list()
        self._update_resource_grid()

    def _update_portrait(self, portrait_surface=None) -> None:
        """Update planet portrait image."""
        if portrait_surface:
            # Use provided portrait surface (from strategy scene asset system)
            scaled = pygame.transform.smoothscale(portrait_surface, (150, 150))
            self.portrait_image.set_image(scaled)
        else:
            # Create placeholder portrait (gradient based on planet type)
            portrait_surf = pygame.Surface((150, 150))

            # Color based on planet type (planet_type always present via IPlanet)
            type_colors = {
                'TERRESTRIAL': PLANET_TERRESTRIAL,
                'GAS_GIANT': PLANET_GAS_GIANT,
                'ICE_GIANT': PLANET_ICE,
                'ROCKY': PLANET_ROCKY,
                'OCEANIC': PLANET_OCEANIC
            }
            base_color = type_colors.get(
                self.planet.planet_type.name,
                TEXT_DIM
            )

            # Simple gradient fill
            for y in range(150):
                fade = 1.0 - (y / 150.0) * 0.3
                color = tuple(int(c * fade) for c in base_color)
                pygame.draw.line(portrait_surf, color, (0, y), (150, y))

            # Add planet name text
            font = get_font(16, bold=True)
            text = font.render(self.planet.name[:20], True, WHITE)
            text_rect = text.get_rect(center=(75, 75))

            # Add shadow for readability
            from game.ui.colors import BLACK
            shadow = font.render(self.planet.name[:20], True, BLACK)
            shadow_rect = shadow.get_rect(center=(76, 76))
            portrait_surf.blit(shadow, shadow_rect)
            portrait_surf.blit(text, text_rect)

            # Add border
            pygame.draw.rect(portrait_surf, TEXT_LIGHT, (0, 0, 150, 150), 2)

            # Update UIImage
            self.portrait_image.set_image(portrait_surf)

    def _update_graph(self) -> None:
        """Update atmosphere graph visualization."""
        # Render atmosphere graph vertically then rotate -90 degrees (matches strategy screen)
        graph_surface = self.graph.render(self.planet, vertical=True)
        graph_surface = pygame.transform.rotate(graph_surface, -90)

        # Update UIImage
        self.graph_image.set_image(graph_surface)

    def _update_complexes_list(self) -> None:
        """Update the list of built complexes on the planet."""
        # Check if complexes list is enabled
        if not self.complexes_container:
            return  # Complexes list disabled, nothing to update

        # Clear existing items - copy list to avoid mutation during iteration (BUG-26)
        items_to_kill = list(self.complex_items)
        for item in items_to_kill:
            item.kill()
        self.complex_items = []

        # Check if planet has facilities (facilities always present via IPlanet)
        if not self.planet.facilities:
            # Show "None" message
            no_complexes_label = UILabel(
                relative_rect=pygame.Rect(5, 35, 190, 25),
                text="None",
                manager=self.manager,
                container=self.complexes_container
            )
            self.complex_items.append(no_complexes_label)
            return

        # Count complexes by design_id
        complex_counts = Counter(facility.design_id for facility in self.planet.facilities)

        # Create list items
        y_offset = 35  # Start below header
        for design_id, count in sorted(complex_counts.items()):
            # Get name from first facility with this design_id
            facility_name = next(
                (f.name for f in self.planet.facilities if f.design_id == design_id),
                design_id  # Fallback to design_id if name not found
            )

            # Format display text
            if count > 1:
                display_text = f"{facility_name} x{count}"
            else:
                display_text = facility_name

            # Create label
            complex_label = UILabel(
                relative_rect=pygame.Rect(5, y_offset, 350, 25),
                text=display_text,
                manager=self.manager,
                container=self.complexes_container
            )
            self.complex_items.append(complex_label)

            y_offset += 30  # Gap between items

    # Net row index within the 8 data rows returned by `_projection_grid_rows`
    # (Qty, Qual, Harvest, Upkeep, Yard, Net, Stored, Cap). Used to scope
    # the green/red sign-tint to the Net row only.
    _NET_DATA_ROW_INDEX = 5

    def _build_resource_grid(self) -> None:
        """Render the transposed icon-column resource grid into
        ``self.resource_panel``.

        Layout:
          * Header row — per resource, an icon (UIImage) above a 3-letter
            abbreviation (UILabel). Resource set comes from
            ``self._displayed_resources`` (catalog-driven).
          * 8 data rows — Qty / Qual / Harvest / Upkeep / Yard / Net /
            Stored / Cap, each row with a row-label cell on the left
            followed by one value cell per resource.

        Cell text is computed by the pure helper
        ``_projection_grid_rows(planet, view, displayed_ids)`` so the
        cell-text contract is testable without pygame. This method only
        wires those tuples into UI widgets and applies the Net row's
        green/red sign tint.
        """
        # Clear any existing grid items (refresh path).
        for item in self._resource_grid_items:
            item.kill()
        self._resource_grid_items = []

        rows = _projection_grid_rows(self.planet, self.view, self._displayed_resources)
        proj_by_id = {}
        if self.view is not None:
            proj_by_id = {p.resource_id: p for p in self.view.resource_projections}

        # Fixed cell dimensions sized for the default theme font
        # (arial-14, ~20px line height). The hosting UIScrollingContainer
        # supplies horizontal/vertical scrollbars when content exceeds
        # the viewport, so cells no longer need to be compressed to fit.
        n = len(self._displayed_resources)
        label_col_w = 80
        col_w = 75

        icon_size = 20
        abbrev_h = 20
        row_h = 20
        header_y = 4
        data_start_y = header_y + icon_size + abbrev_h + 2

        # Header row: per-resource icon + abbreviation column header.
        for col_idx, rid in enumerate(self._displayed_resources):
            x = label_col_w + 5 + col_idx * col_w
            icon_surf = self._resource_icons.get(rid)
            if icon_surf is not None:
                icon_x = x + (col_w - icon_size) // 2
                icon_image = UIImage(
                    relative_rect=pygame.Rect(icon_x, header_y, icon_size, icon_size),
                    image_surface=icon_surf,
                    manager=self.manager,
                    container=self.resource_panel,
                )
                self._resource_grid_items.append(icon_image)
            abbrev_label = UILabel(
                relative_rect=pygame.Rect(x, header_y + icon_size, col_w, abbrev_h),
                text=get_resource_abbreviation(rid),
                manager=self.manager,
                container=self.resource_panel,
            )
            self._resource_grid_items.append(abbrev_label)

        # Data rows: rows[1:] are the 8 metric rows from the helper.
        for data_idx, row_cells in enumerate(rows[1:]):
            y = data_start_y + data_idx * row_h
            row_label = UILabel(
                relative_rect=pygame.Rect(5, y, label_col_w, row_h),
                text=row_cells[0],
                manager=self.manager,
                container=self.resource_panel,
            )
            self._resource_grid_items.append(row_label)

            for col_idx, rid in enumerate(self._displayed_resources):
                x = label_col_w + 5 + col_idx * col_w
                cell = UILabel(
                    relative_rect=pygame.Rect(x, y, col_w, row_h),
                    text=row_cells[1 + col_idx],
                    manager=self.manager,
                    container=self.resource_panel,
                )
                # Sign-tint the Net row cells where a real projection exists.
                if data_idx == self._NET_DATA_ROW_INDEX:
                    proj = proj_by_id.get(rid)
                    if proj is not None:
                        color = _net_cell_color(proj.net)
                        try:
                            cell.text_colour = color
                            cell.rebuild()
                        except AttributeError:
                            # pygame_gui versions vary on `text_colour`
                            # setter support; the colour is non-essential
                            # to correctness, so silently skip the missing
                            # setter. Other exceptions propagate so real
                            # bugs surface instead of being swallowed.
                            pass
                self._resource_grid_items.append(cell)

        # Tell the scrolling container how large the rendered grid is so
        # horizontal/vertical scrollbars appear when content overflows.
        # Inputs reuse the cell-layout constants above so this stays
        # consistent if they change.
        n_data_rows = len(rows) - 1  # rows[0] is the header tuple
        content_w = label_col_w + 5 + n * col_w + 10
        content_h = data_start_y + n_data_rows * row_h + 6
        self.resource_panel.set_scrollable_area_dimensions((content_w, content_h))

    def _update_resource_grid(self) -> None:
        """Refresh resource grid values when planet changes."""
        self._build_resource_grid()

    def _load_resource_icons(self, icon_size: int = 24) -> None:
        """
        Load resource portrait icons for the resource grid.

        Args:
            icon_size: Size of the square icons in pixels (default 24).
        """
        base_path = Paths.RESOURCE_PORTRAITS_DIR

        for resource in self._displayed_resources:
            filename = RESOURCE_PORTRAIT_FILES.get(resource)
            if filename:
                path = os.path.join(base_path, filename)
                try:
                    img = pygame.image.load(path)
                    self._resource_icons[resource] = pygame.transform.smoothscale(
                        img, (icon_size, icon_size)
                    )
                except (FileNotFoundError, pygame.error):
                    # Create fallback colored square
                    surf = pygame.Surface((icon_size, icon_size))
                    color = RESOURCE_FALLBACK_COLORS.get(resource, TEXT_DIM)
                    surf.fill(color)
                    pygame.draw.rect(surf, WHITE, surf.get_rect(), 1)
                    self._resource_icons[resource] = surf
            else:
                # No filename mapped, create gray placeholder
                surf = pygame.Surface((icon_size, icon_size))
                surf.fill(TEXT_DIM)
                pygame.draw.rect(surf, WHITE, surf.get_rect(), 1)
                self._resource_icons[resource] = surf

    def get_height_required(self) -> int:
        """
        Get minimum height required for this panel.

        Returns:
            int: Minimum height in pixels (350 + RESOURCE_PANEL_HEIGHT)
        """
        return 350 + RESOURCE_PANEL_HEIGHT

    def kill(self) -> None:
        """Clean up all UI elements."""
        # Clean up resource grid items
        for item in self._resource_grid_items:
            item.kill()
        self._resource_grid_items = []

        # Clean up resource panel
        if self.resource_panel:
            self.resource_panel.kill()

        # Clean up main panel (contains all other elements)
        if self.panel:
            self.panel.kill()


# PROJ-288 Task 2.3: `compute_planet_production` (and its `_get_harvester_info`
# helper) moved to `game/strategy/services/planet_economy_projector.py` to fix
# the previous strategy-math-living-in-UI layer violation. Importers updated
# to pull directly from the new location.

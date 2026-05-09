"""
EmpireTreasuryPanel - Displays empire economy overview with production, expenses, and treasury.

PROJ-99 Phase 2: Treasury tab panel for the Empire Panel Window.
Shows per-turn production and expenses broken down by category,
plus current treasury and storage capacity.
"""
from __future__ import annotations

import os
from typing import Dict, List, Tuple, Optional

import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UIImage, UIScrollingContainer

from functools import lru_cache

from game.core.resources import ResourceCatalog
from game.core.paths import Paths


@lru_cache(maxsize=1)
def _get_planetary_ids() -> tuple[str, ...]:
    """PROJ-397 F-07: lazy-load planetary resource IDs.

    Was a module-level ``ResourceCatalog.from_json()`` call that ran at
    import time, breaking the docs/02_PATTERNS.md Pattern 12 contract
    (no I/O at import). Tests can call ``_get_planetary_ids.cache_clear()``.
    """
    return tuple(d.id for d in ResourceCatalog.from_json().by_display_group("planetary"))
from game.strategy.services.empire_economy_service import EmpireEconomySnapshot  # PROJ-292 M1
from game.ui.utils import create_section_header
from game.ui.utils.resource_display import get_resource_abbreviation


# Layout constants
LABEL_COL_WIDTH = 240
RESOURCE_COL_WIDTH = 100
ICON_SIZE = 20
ROW_HEIGHT = 28
SECTION_GAP = 15
HEADER_HEIGHT = 35
LEFT_MARGIN = 10
TOP_MARGIN = 10


class EmpireTreasuryPanel:
    """
    Panel displaying empire-wide economy data.

    Shows three sections:
    - Resource Production Per Turn: colony, ship, trade, tribute, mining sources
    - Resource Expenses Per Turn: tributes, construction
    - Treasury: net resources, current storage, max storage

    Each section shows values for all 5 resource types in columns.
    """

    def __init__(
        self,
        panel: UIPanel,
        manager: pygame_gui.UIManager,
        snapshot: EmpireEconomySnapshot,
        resource_icons: Dict[str, pygame.Surface]
    ):
        """
        Create treasury panel content.

        Args:
            panel: Parent UIPanel to add controls to
            manager: pygame_gui UIManager
            snapshot: EmpireEconomySnapshot with economy data
            resource_icons: Dict mapping resource type to pre-loaded 20x20 icon Surface
        """
        self.panel = panel
        self.ui_manager = manager
        self.snapshot = snapshot
        self.resource_icons = resource_icons

        # UI element references for refresh
        self._scroll_container: Optional[UIScrollingContainer] = None
        self._elements: List[pygame_gui.core.UIElement] = []

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the complete treasury panel UI."""
        # Get panel dimensions
        panel_rect = self.panel.get_relative_rect()
        container_width = panel_rect.width - 20
        container_height = panel_rect.height - 20

        # Create scrolling container
        self._scroll_container = UIScrollingContainer(
            relative_rect=pygame.Rect(LEFT_MARGIN, TOP_MARGIN, container_width, container_height),
            manager=self.ui_manager,
            container=self.panel
        )

        y_offset = TOP_MARGIN

        # Resource column headers
        y_offset = self._build_resource_header(y_offset)

        # Production section
        production_rows = self._get_production_rows()
        y_offset = self._build_section("Resource Production Per Turn", production_rows, y_offset)

        # Expense section
        expense_rows = self._get_expense_rows()
        y_offset = self._build_section("Resource Expenses Per Turn", expense_rows, y_offset)

        # Treasury section
        treasury_rows = self._get_treasury_rows()
        y_offset = self._build_section("Treasury", treasury_rows, y_offset)

        # Set scrollable area height
        self._scroll_container.set_scrollable_area_dimensions(
            (container_width - 20, y_offset + 20)
        )

    def _build_resource_header(self, y: int) -> int:
        """
        Build resource icon and label column headers.

        Args:
            y: Starting y offset

        Returns:
            New y offset after header
        """
        for i, resource in enumerate(_get_planetary_ids()):
            x = LABEL_COL_WIDTH + i * RESOURCE_COL_WIDTH

            # Resource icon
            if resource in self.resource_icons:
                icon_surface = self.resource_icons[resource]
                icon_img = UIImage(
                    relative_rect=pygame.Rect(x + (RESOURCE_COL_WIDTH - ICON_SIZE) // 2, y, ICON_SIZE, ICON_SIZE),
                    image_surface=icon_surface,
                    manager=self.ui_manager,
                    container=self._scroll_container
                )
                self._elements.append(icon_img)

            # Abbreviated label
            abbrev = get_resource_abbreviation(resource)
            label = UILabel(
                relative_rect=pygame.Rect(x, y + ICON_SIZE + 2, RESOURCE_COL_WIDTH, 22),
                text=abbrev,
                manager=self.ui_manager,
                container=self._scroll_container
            )
            self._elements.append(label)

        return y + HEADER_HEIGHT

    def _build_section(
        self,
        title: str,
        rows: List[Tuple[str, Dict[str, float], bool]],
        y: int
    ) -> int:
        """
        Build a section with title and data rows.

        Args:
            title: Section title
            rows: List of (label, values_dict, is_total) tuples
            y: Starting y offset

        Returns:
            New y offset after section
        """
        # Section title
        title_label = create_section_header(
            title, y,
            LABEL_COL_WIDTH + len(_get_planetary_ids()) * RESOURCE_COL_WIDTH,
            self.ui_manager, self._scroll_container,
            x=LEFT_MARGIN, height=ROW_HEIGHT
        )
        self._elements.append(title_label)
        y += ROW_HEIGHT

        # Data rows
        for label_text, values, is_total in rows:
            y = self._build_row(label_text, values, is_total, y)

        # Section gap
        return y + SECTION_GAP

    def _build_row(
        self,
        label_text: str,
        values: Dict[str, float],
        is_total: bool,
        y: int
    ) -> int:
        """
        Build a single data row.

        Args:
            label_text: Row label
            values: Dict mapping resource type to value
            is_total: If True, render with total row styling
            y: Current y offset

        Returns:
            New y offset after row
        """
        # Row label
        object_id = "#total_row" if is_total else None
        label = UILabel(
            relative_rect=pygame.Rect(LEFT_MARGIN + 10, y, LABEL_COL_WIDTH - 10, ROW_HEIGHT),
            text=label_text,
            manager=self.ui_manager,
            container=self._scroll_container,
            object_id=object_id
        )
        self._elements.append(label)

        # Resource values
        for i, resource in enumerate(_get_planetary_ids()):
            x = LABEL_COL_WIDTH + i * RESOURCE_COL_WIDTH
            value = values.get(resource, 0.0)
            formatted = self._format_value(value)

            value_label = UILabel(
                relative_rect=pygame.Rect(x, y, RESOURCE_COL_WIDTH, ROW_HEIGHT),
                text=formatted,
                manager=self.ui_manager,
                container=self._scroll_container,
                object_id=object_id
            )
            self._elements.append(value_label)

        return y + ROW_HEIGHT

    def _format_value(self, value: float) -> str:
        """
        Format a numeric value for display.

        Args:
            value: Numeric value to format

        Returns:
            Formatted string with comma separators
        """
        if value == 0:
            return "0"
        # Round to integer and format with commas
        int_value = int(round(value))
        return f"{int_value:,}"

    def _get_production_rows(self) -> List[Tuple[str, Dict[str, float], bool]]:
        """Get production section row data."""
        return [
            ("From Colonies", self.snapshot.colony_production, False),
            ("From Ships", self.snapshot.ship_production, False),
            ("From Trade", self.snapshot.trade_production, False),
            ("From Tribute", self.snapshot.tribute_production, False),
            ("From Remote Mining", self.snapshot.mining_production, False),
            ("Total", self.snapshot.total_production, True),
        ]

    def _get_expense_rows(self) -> List[Tuple[str, Dict[str, float], bool]]:
        """Get expense section row data.

        PROJ-290: inserts a "Population Upkeep" row (signed-negative
        cells) before the Total row when
        `snapshot.total_population_upkeep` contains at least one
        non-zero value. Hidden in fresh-game / no-pop state.
        """
        rows: List[Tuple[str, Dict[str, float], bool]] = [
            ("Tributes", self.snapshot.tribute_expenses, False),
            ("Construction Queues (Ships)", self.snapshot.construction_expenses_ships, False),
            ("Construction Queues (Complexes)", self.snapshot.construction_expenses_complexes, False),
        ]

        upkeep = self.snapshot.total_population_upkeep
        if upkeep and any(v > 0 for v in upkeep.values()):
            # Render as drain — cells are signed-negative floats so the
            # visual language matches the other "Construction Queues"
            # drain rows.
            negated = {res: -value for res, value in upkeep.items() if value > 0}
            rows.append(("Population Upkeep", negated, False))

        rows.append(("Total", self.snapshot.total_expenses, True))
        return rows

    def _get_treasury_rows(self) -> List[Tuple[str, Dict[str, float], bool]]:
        """Get treasury section row data."""
        return [
            ("Net Resources", self.snapshot.net_resources, False),
            ("Total In Storage", self.snapshot.current_storage, False),
            ("Maximum Storage", self.snapshot.max_storage, False),
        ]

    def refresh(self, snapshot: EmpireEconomySnapshot) -> None:
        """
        Refresh panel with new snapshot data.

        Args:
            snapshot: New EmpireEconomySnapshot to display
        """
        self.snapshot = snapshot

        # Clear existing elements
        for element in self._elements:
            element.kill()
        self._elements.clear()

        if self._scroll_container:
            self._scroll_container.kill()
            self._scroll_container = None

        # Rebuild UI
        self._build_ui()


def load_resource_icons() -> Dict[str, pygame.Surface]:
    """
    Load and scale resource icons for the treasury panel.

    Returns:
        Dict mapping resource type to 20x20 pygame Surface.
    """
    icons = {}
    resource_icons_dir = os.path.join(Paths.ASSET_DIR, "Images", "Resource Icons")

    for resource in _get_planetary_ids():
        filename = f"resource_{resource.lower()}_icon.png"
        filepath = os.path.join(resource_icons_dir, filename)

        if os.path.exists(filepath):
            try:
                surface = pygame.image.load(filepath).convert_alpha()
                scaled = pygame.transform.smoothscale(surface, (ICON_SIZE, ICON_SIZE))
                icons[resource] = scaled
            except pygame.error:
                pass  # Skip icons that fail to load

    return icons

"""Fleet data source for VirtualTable.

PROJ-188 Phase 2: FleetDataSource provides ship data for the fleet report table.
"""

from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

import pygame

from game.ui.components.table.data_source import ITableDataSource
from game.ui.config import UIConfig
from game.ui.utils import scale_image_by_visible_portion, scale_image_to_fit
from game.ui.colors import GRID_BG, BORDER_LIGHT

if TYPE_CHECKING:
    from game.ui.screens.fleet_report_view_model import FleetListViewModel
    from game.strategy.data.ship_instance import ShipInstance


# Default column configuration for fleet reports
DEFAULT_FLEET_COLUMNS = [
    {"id": "portrait", "width": 44, "title": "", "type": "image", "visible": True},
    {"id": "topdown", "width": 60, "title": "", "type": "image", "visible": True},
    {"id": "serial", "width": 130, "title": "Serial ID", "visible": True},
    {"id": "design", "width": 100, "title": "Design", "visible": True},
    {"id": "name", "width": 120, "title": "Name", "visible": True},
    {"id": "hp_pct", "width": 80, "title": "HP %", "visible": True},
    {"id": "status", "width": 100, "title": "Status", "visible": True},
    {"id": "speed", "width": 70, "title": "Spd", "visible": False},
    {"id": "tonnage", "width": 80, "title": "Tons", "visible": False},
    {"id": "warp", "width": 55, "title": "Warp", "visible": False},
    {"id": "spaceyard", "width": 60, "title": "Yard", "visible": False},
    {"id": "transport", "width": 65, "title": "Pax", "visible": False},
    {"id": "resources", "width": 130, "title": "Resources", "visible": False},
    {"id": "cargo", "width": 65, "title": "Cargo", "visible": False},
    {"id": "can_destroy_planet", "width": 75, "title": "DestrPlanet", "visible": False},
    {"id": "can_open_warp", "width": 75, "title": "OpenWarp", "visible": False},
    {"id": "can_close_warp", "width": 75, "title": "CloseWarp", "visible": False},
    {"id": "can_destroy_star", "width": 75, "title": "DestrStar", "visible": False},
    {"id": "can_create_sphere", "width": 75, "title": "Sphere", "visible": False},
]


# Special capability columns and their corresponding ability names
SPECIAL_CAPABILITY_COLUMNS = {
    "can_destroy_planet": "DestroyPlanet",
    "can_open_warp": "OpenWarpPoint",
    "can_close_warp": "CloseWarpPoint",
    "can_destroy_star": "DestroyStar",
    "can_create_sphere": "CreateSphereWorld",
}


class FleetDataSource(ITableDataSource):
    """Data source providing ship data for VirtualTable.

    Wraps FleetListViewModel and provides cell values, images, and column config.
    """

    def __init__(self, view_model: "FleetListViewModel") -> None:
        """Initialize with a view model.

        Args:
            view_model: FleetListViewModel for filtered/sorted ship access.
        """
        self._view_model = view_model
        self._image_cache: Dict[tuple, pygame.Surface] = {}
        self._row_height = UIConfig.ROW_HEIGHT_LARGE

    def get_row_count(self) -> int:
        """Return number of filtered ships."""
        return len(self._view_model.get_filtered_ships())

    def get_columns(self) -> List[Dict[str, Any]]:
        """Return column definitions."""
        return DEFAULT_FLEET_COLUMNS

    def get_cell_value(self, row_index: int, column_id: str) -> str:
        """Return string value for a cell.

        Args:
            row_index: Zero-based row index.
            column_id: Column identifier.

        Returns:
            String representation of cell value.
        """
        ship = self.get_ship_at_index(row_index)
        if ship is None:
            return ""

        return self._get_column_value(ship, column_id)

    def get_cell_image(
        self, row_index: int, column_id: str
    ) -> Optional[pygame.Surface]:
        """Return image surface for image columns.

        Args:
            row_index: Zero-based row index.
            column_id: Column identifier.

        Returns:
            Pygame surface or None.
        """
        if column_id not in ("portrait", "topdown"):
            return None

        ship = self.get_ship_at_index(row_index)
        if ship is None:
            return None

        return self._get_ship_image(ship, column_id)

    def get_ship_at_index(self, row_index: int) -> Optional["ShipInstance"]:
        """Get ship at given row index.

        Args:
            row_index: Zero-based row index.

        Returns:
            ShipInstance or None if out of bounds.
        """
        ships = self._view_model.get_filtered_ships()
        if 0 <= row_index < len(ships):
            return ships[row_index]
        return None

    def _get_column_handlers(self) -> Dict[str, Callable[["ShipInstance"], str]]:
        """Return mapping of column IDs to handler methods.

        Returns:
            Dict mapping column ID to handler function.
        """
        return {
            "serial": self._format_serial,
            "design": self._format_design,
            "name": self._format_name,
            "hp_pct": self._format_hp_pct,
            "status": self._format_status,
            "speed": self._format_speed,
            "tonnage": self._format_tonnage,
            "warp": self._format_warp,
            "spaceyard": self._format_spaceyard,
            "transport": self._format_transport,
            "resources": self._format_resources,
            "cargo": self._format_cargo,
        }

    def _get_column_value(self, ship: "ShipInstance", col_id: str) -> str:
        """Get display value for a column.

        Args:
            ship: Ship instance.
            col_id: Column identifier.

        Returns:
            String value to display.
        """
        # Image columns handled separately
        if col_id in ("portrait", "topdown"):
            return ""

        # Special capability columns need col_id parameter
        if col_id in SPECIAL_CAPABILITY_COLUMNS:
            return self._format_capability(ship, col_id)

        # Dispatch to handler
        handlers = self._get_column_handlers()
        handler = handlers.get(col_id)
        if handler:
            return handler(ship)

        # Unknown column
        return ""

    def _format_status(self, ship: "ShipInstance") -> str:
        """Format ship status for display."""
        if not ship.is_alive:
            return "DESTROYED"
        elif ship.is_derelict:
            return "DERELICT"
        elif ship.is_damaged():
            return "DAMAGED"
        else:
            return "OK"

    def _format_resources(self, ship: "ShipInstance") -> str:
        """Format resource percentages for display."""
        parts = []
        resource_abbrevs = [
            ("energy", "E"),
            ("fuel", "F"),
            ("ammo", "A"),
        ]
        for res_type, abbrev in resource_abbrevs:
            pct = ship.get_resource_percentage(res_type)
            if pct is not None and pct >= 0:
                parts.append(f"{abbrev}:{int(pct * 100)}")
        return " ".join(parts) if parts else "--"

    def _format_serial(self, ship: "ShipInstance") -> str:
        """Format ship serial ID for display."""
        display_id = ship._display_fmt.get_display_id()
        return display_id if display_id else ship.instance_id[:8]

    def _format_design(self, ship: "ShipInstance") -> str:
        """Format ship design name for display."""
        return ship.design_data.get("name", ship.design_id)

    def _format_name(self, ship: "ShipInstance") -> str:
        """Format ship name for display."""
        return ship.name

    def _format_hp_pct(self, ship: "ShipInstance") -> str:
        """Format HP percentage for display."""
        return f"{ship.get_hp_percentage() * 100:.0f}%"

    def _format_tonnage(self, ship: "ShipInstance") -> str:
        """Format ship tonnage for display."""
        mass = ship.get_calculated_stats().get("mass", 0)
        return f"{mass:,.0f}"

    def _format_speed(self, ship: "ShipInstance") -> str:
        """Format ship speed for display."""
        # INTENTIONAL LATE IMPORT: Avoid circular import
        from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator

        speed = FleetSpeedCalculator.calculate_ship_speed(ship)
        return str(speed)

    def _format_warp(self, ship: "ShipInstance") -> str:
        """Format warp capability for display."""
        from game.strategy.services.component_inspector import has_warp_capability

        return "Yes" if has_warp_capability(ship) else "No"

    def _format_spaceyard(self, ship: "ShipInstance") -> str:
        """Format spaceyard capability for display."""
        # INTENTIONAL LATE IMPORT: Avoid circular import
        from game.strategy.data.fleet_capability_calculator import (
            FleetCapabilityCalculator,
        )

        return "Yes" if FleetCapabilityCalculator.ship_has_spaceyard(ship) else "No"

    def _format_transport(self, ship: "ShipInstance") -> str:
        """Format passenger transport capacity for display."""
        capacity = ship.get_cargo_capacity("passengers")
        current = ship.get_current_cargo("passengers")
        return f"{current}/{capacity}" if capacity > 0 else "--"

    def _format_cargo(self, ship: "ShipInstance") -> str:
        """Format total cargo for display."""
        total = sum(ship.cargo_contents.values()) if ship.cargo_contents else 0
        return str(total) if total > 0 else "--"

    def _format_capability(self, ship: "ShipInstance", col_id: str) -> str:
        """Format special capability for display."""
        # INTENTIONAL LATE IMPORT: Avoid circular import
        from game.strategy.services.component_inspector import ship_has_ability

        ability_name = SPECIAL_CAPABILITY_COLUMNS[col_id]
        registry = ship._registries.components if ship._registries else {}
        return "Yes" if ship_has_ability(ship, ability_name, registry) else "No"

    def _get_ship_image(
        self, ship: "ShipInstance", image_type: str
    ) -> pygame.Surface:
        """Get a ship image (portrait or topdown) scaled for display.

        Args:
            ship: Ship instance.
            image_type: 'portrait' or 'topdown'.

        Returns:
            Scaled pygame surface.
        """
        from game.ui.assets import get_default_ship_theme_manager

        # Get theme and ship class from design_data
        theme_id = ship.design_data.get("theme_id", "Federation")
        ship_class = ship.design_data.get("ship_class", "Unknown")

        # Check cache
        cache_key = (ship.instance_id, image_type)
        if cache_key in self._image_cache:
            return self._image_cache[cache_key]

        # Get image from theme manager
        theme_mgr = get_default_ship_theme_manager()
        target_height = self._row_height - 4

        if image_type == "portrait":
            target_size = (40, target_height)
            raw_surf = theme_mgr.get_portrait_image(theme_id, ship_class)
            if raw_surf:
                result = scale_image_to_fit(raw_surf, target_size)
            else:
                result = self._create_placeholder(target_size)
        elif image_type == "topdown":
            raw_surf = theme_mgr.load_image(theme_id, ship_class)
            target_width = 56  # topdown column width (60) minus padding
            if raw_surf:
                result = scale_image_by_visible_portion(raw_surf, target_height, max_width=target_width)
            else:
                result = self._create_placeholder((target_width, target_height))
        else:
            result = self._create_placeholder((40, target_height))

        # Cache the result
        self._image_cache[cache_key] = result
        return result

    def _create_placeholder(self, size: tuple) -> pygame.Surface:
        """Create a placeholder surface for missing images.

        Args:
            size: (width, height) tuple.

        Returns:
            Placeholder pygame surface.
        """
        result = pygame.Surface(size)
        result.fill(GRID_BG)
        pygame.draw.rect(result, BORDER_LIGHT, (5, 10, 30, 20), 1)
        return result

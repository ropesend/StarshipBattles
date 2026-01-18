"""
Design Library - Manages ship designs for an empire/savegame

This module provides the DesignLibrary class for managing ship designs in
integrated mode, including saving, loading, filtering, and marking designs
as obsolete. Designs are stored in the savegame's designs folder.
"""
import os
import glob
from typing import List, Optional, Tuple, Set
from datetime import datetime
from game.strategy.data.design_metadata import DesignMetadata
from game.core.json_utils import load_json_required, save_json
from game.simulation.entities.ship import Ship


class DesignLibrary:
    """Manages ship designs for a specific empire/savegame"""

    def __init__(self, savegame_path: str, empire_id: int):
        """
        Initialize design library.

        Args:
            savegame_path: Path to the savegame directory
            empire_id: ID of the empire this library belongs to
        """
        self.savegame_path = savegame_path
        self.empire_id = empire_id
        self.designs_folder = os.path.join(savegame_path, "designs")

        # Ensure designs folder exists
        os.makedirs(self.designs_folder, exist_ok=True)

    def scan_designs(self) -> List[DesignMetadata]:
        """
        Scan designs folder and build metadata list.

        Returns:
            List of DesignMetadata objects for all designs in the library
        """
        designs = []
        pattern = os.path.join(self.designs_folder, "*.json")

        for filepath in glob.glob(pattern):
            try:
                design_id = os.path.splitext(os.path.basename(filepath))[0]
                metadata = DesignMetadata.from_design_file(filepath, design_id)
                designs.append(metadata)
            except Exception as e:
                # Log error but continue scanning
                print(f"Warning: Failed to load design metadata from {filepath}: {e}")
                continue

        return designs

    def save_design(self, ship, design_name: str, built_designs: Set[str]) -> Tuple[bool, str]:
        """
        Save design to empire's designs folder.

        Args:
            ship: Ship object to save
            design_name: Name for the design
            built_designs: Set of design IDs that have been built (prevents overwriting)

        Returns:
            Tuple of (success: bool, message: str)
        """
        design_id = self._sanitize_design_id(design_name)
        filepath = os.path.join(self.designs_folder, f"{design_id}.json")

        # Check if design exists and was ever built
        if os.path.exists(filepath) and design_id in built_designs:
            return False, f"Cannot overwrite '{design_name}' - this design has been built in-game"

        try:
            # Create metadata
            metadata = DesignMetadata.from_ship(ship, design_id)

            # If updating existing design, preserve created_date and times_built
            if os.path.exists(filepath):
                old_data = load_json_required(filepath)
                old_metadata = old_data.get("_metadata", {})
                metadata.created_date = old_metadata.get("created_date", metadata.created_date)
                metadata.times_built = old_metadata.get("times_built", 0)
                metadata.is_obsolete = old_metadata.get("is_obsolete", False)

            metadata.last_modified = datetime.now().isoformat()

            # Get ship data and embed metadata
            ship_data = ship.to_dict()
            ship_data = metadata.embed_in_ship_data(ship_data)

            # Save to file
            save_json(filepath, ship_data, indent=4)

            return True, f"Saved design: {design_name}"

        except Exception as e:
            return False, f"Failed to save design: {str(e)}"

    def load_design(self, design_id: str, width: int = 1920, height: int = 1080) -> Tuple[Optional[Ship], str]:
        """
        Load design by ID.

        Args:
            design_id: Design ID to load
            width: Screen width for positioning
            height: Screen height for positioning

        Returns:
            Tuple of (Ship object or None, message: str)
        """
        filepath = os.path.join(self.designs_folder, f"{design_id}.json")

        if not os.path.exists(filepath):
            return None, f"Design not found: {design_id}"

        try:
            data = load_json_required(filepath)
            ship = Ship.from_dict(data)

            # Position ship at screen center
            import pygame
            ship.position = pygame.math.Vector2(width // 2, height // 2)

            # Recalculate stats
            ship.recalculate_stats()

            return ship, f"Loaded design: {ship.name}"

        except Exception as e:
            return None, f"Failed to load design: {str(e)}"

    def load_design_data(self, design_id: str) -> Optional[dict]:
        """
        Load raw design data without creating Ship instance.

        Useful for strategy layer when creating ShipInstances.

        Args:
            design_id: Design ID to load

        Returns:
            Design data dict or None if not found
        """
        filepath = os.path.join(self.designs_folder, f"{design_id}.json")

        if not os.path.exists(filepath):
            return None

        try:
            return load_json_required(filepath)
        except Exception:
            return None

    def mark_obsolete(self, design_id: str, is_obsolete: bool) -> Tuple[bool, str]:
        """
        Toggle obsolete flag on design metadata.

        Args:
            design_id: Design ID to update
            is_obsolete: New obsolete status

        Returns:
            Tuple of (success: bool, message: str)
        """
        filepath = os.path.join(self.designs_folder, f"{design_id}.json")

        if not os.path.exists(filepath):
            return False, f"Design not found: {design_id}"

        try:
            # Load design data
            data = load_json_required(filepath)

            # Update metadata
            metadata_dict = data.get("_metadata", {})
            metadata_dict["is_obsolete"] = is_obsolete
            data["_metadata"] = metadata_dict

            # Save back
            save_json(filepath, data, indent=4)

            status = "obsolete" if is_obsolete else "active"
            return True, f"Marked design as {status}"

        except Exception as e:
            return False, f"Failed to update design: {str(e)}"

    def increment_built_count(self, design_id: str) -> bool:
        """
        Increment the times_built counter for a design.

        Called when a ship is built from this design.

        Args:
            design_id: Design ID to update

        Returns:
            True if successful, False otherwise
        """
        filepath = os.path.join(self.designs_folder, f"{design_id}.json")

        if not os.path.exists(filepath):
            return False

        try:
            # Load design data
            data = load_json_required(filepath)

            # Update metadata
            metadata_dict = data.get("_metadata", {})
            metadata_dict["times_built"] = metadata_dict.get("times_built", 0) + 1
            data["_metadata"] = metadata_dict

            # Save back
            save_json(filepath, data, indent=4)

            return True

        except Exception:
            return False

    def filter_designs(self,
                      ship_class: Optional[str] = None,
                      vehicle_type: Optional[str] = None,
                      show_obsolete: bool = False) -> List[DesignMetadata]:
        """
        Filter designs by criteria.

        Args:
            ship_class: Filter by ship class (None = no filter)
            vehicle_type: Filter by vehicle type (None = no filter)
            show_obsolete: Whether to include obsolete designs

        Returns:
            List of filtered DesignMetadata objects
        """
        designs = self.scan_designs()

        # Apply filters
        if ship_class:
            designs = [d for d in designs if d.ship_class == ship_class]

        if vehicle_type:
            designs = [d for d in designs if d.vehicle_type == vehicle_type]

        if not show_obsolete:
            designs = [d for d in designs if not d.is_obsolete]

        return designs

    def search_designs(self, name_query: str, filters: Optional[dict] = None) -> List[DesignMetadata]:
        """
        Search designs by name and optional filters.

        Args:
            name_query: Text to search for in design names
            filters: Optional dict with 'ship_class', 'vehicle_type', 'show_obsolete' keys

        Returns:
            List of matching DesignMetadata objects
        """
        filters = filters or {}

        # Get filtered designs
        designs = self.filter_designs(
            ship_class=filters.get('ship_class'),
            vehicle_type=filters.get('vehicle_type'),
            show_obsolete=filters.get('show_obsolete', False)
        )

        # Apply name search
        if name_query:
            search_lower = name_query.lower()
            designs = [d for d in designs if search_lower in d.name.lower()]

        return designs

    def delete_design(self, design_id: str, built_designs: Set[str]) -> Tuple[bool, str]:
        """
        Delete a design from the library.

        Args:
            design_id: Design ID to delete
            built_designs: Set of design IDs that have been built (prevents deletion)

        Returns:
            Tuple of (success: bool, message: str)
        """
        filepath = os.path.join(self.designs_folder, f"{design_id}.json")

        if not os.path.exists(filepath):
            return False, f"Design not found: {design_id}"

        # Check if design was built
        if design_id in built_designs:
            return False, f"Cannot delete design that has been built. Mark as obsolete instead."

        try:
            os.remove(filepath)
            return True, f"Deleted design: {design_id}"
        except Exception as e:
            return False, f"Failed to delete design: {str(e)}"

    @staticmethod
    def _sanitize_design_id(name: str) -> str:
        """
        Convert design name to safe filename.

        Args:
            name: Design name to sanitize

        Returns:
            Safe filename string
        """
        # Keep only alphanumeric, space, hyphen, underscore
        safe = "".join([c for c in name if c.isalnum() or c in (' ', '-', '_')]).strip()

        # Replace spaces with underscores
        safe = safe.replace(' ', '_')

        # Default if empty
        return safe if safe else "unnamed_design"

    def get_design_path(self, design_id: str) -> str:
        """
        Get full filepath for a design ID.

        Args:
            design_id: Design ID

        Returns:
            Full path to design file
        """
        return os.path.join(self.designs_folder, f"{design_id}.json")

    def design_exists(self, design_id: str) -> bool:
        """
        Check if a design exists.

        Args:
            design_id: Design ID to check

        Returns:
            True if design exists, False otherwise
        """
        return os.path.exists(self.get_design_path(design_id))

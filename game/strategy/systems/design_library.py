"""
Design Library - Manages ship designs for an empire/savegame

This module provides the DesignLibrary class for managing ship designs in
integrated mode, including saving, loading, filtering, and marking designs
as obsolete. Designs are stored in the savegame's designs folder.
"""
import logging
from dataclasses import dataclass
from json import JSONDecodeError
import os
import glob
from typing import List, Optional, Tuple, Set
from datetime import datetime
from game.strategy.data.design_metadata import DesignMetadata
from game.core.json_utils import load_json_required, save_json
from game.core.string_utils import slugify
from game.core.exceptions import ValidationException

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DesignLoadResult:
    """Result of attempting to load a ship design.

    PROJ-251: Replaces bare Optional[dict] return so callers can distinguish
    between not-found, corrupt JSON, invalid schema, and permission errors.

    Usage:
        result = library.load_design_data(design_id)
        if result.success:
            data = result.data
        else:
            if result.error_type == "not_found":
                pass  # Normal — design hasn't been saved yet
            else:
                logger.warning(f"Design load failed: {result.error}")
    """
    data: Optional[dict] = None
    error: Optional[str] = None
    error_type: Optional[str] = None

    @property
    def success(self) -> bool:
        """True if design was loaded successfully."""
        return self.data is not None

    @staticmethod
    def ok(data: dict) -> 'DesignLoadResult':
        """Create a successful result."""
        return DesignLoadResult(data=data)

    @staticmethod
    def not_found(design_id: str) -> 'DesignLoadResult':
        """Design file does not exist."""
        return DesignLoadResult(
            error=f"Design '{design_id}' not found",
            error_type="not_found"
        )

    @staticmethod
    def corrupt(design_id: str, detail: str) -> 'DesignLoadResult':
        """Design file exists but contains invalid JSON."""
        return DesignLoadResult(
            error=f"Design '{design_id}' has corrupt JSON: {detail}",
            error_type="corrupt_json"
        )

    @staticmethod
    def invalid_schema(design_id: str, detail: str) -> 'DesignLoadResult':
        """Design file has valid JSON but missing/invalid schema."""
        return DesignLoadResult(
            error=f"Design '{design_id}' has invalid schema: {detail}",
            error_type="invalid_schema"
        )

    @staticmethod
    def permission_denied(design_id: str, detail: str) -> 'DesignLoadResult':
        """Cannot read design file due to permissions."""
        return DesignLoadResult(
            error=f"Design '{design_id}' permission denied: {detail}",
            error_type="permission_denied"
        )

    @staticmethod
    def io_error(design_id: str, detail: str) -> 'DesignLoadResult':
        """Cannot read design file due to OS/IO error."""
        return DesignLoadResult(
            error=f"Design '{design_id}' IO error: {detail}",
            error_type="io_error"
        )


class DesignLibrary:
    """Manages ship designs for a specific empire/savegame"""

    def __init__(self, savegame_path: Optional[str], empire_id: int):
        """
        Initialize design library.

        Args:
            savegame_path: Path to the savegame directory (None if no savegame)
            empire_id: ID of the empire this library belongs to
        """
        self.savegame_path = savegame_path
        self.empire_id = empire_id

        logger.debug(f"DesignLibrary.__init__ called:")
        logger.debug(f"  savegame_path: {savegame_path}")
        logger.debug(f"  empire_id: {empire_id}")

        # Determine designs folder location
        if isinstance(savegame_path, str) and savegame_path != "":
            # Use per-empire subfolder: designs/empire_N/
            self.designs_folder = os.path.join(savegame_path, "designs", f"empire_{empire_id}")
            logger.info(f"DesignLibrary: Using savegame designs folder: {self.designs_folder}")
        else:
            # Use temp folder for designs when no savegame exists (standalone Workshop mode)
            import tempfile
            temp_base = os.path.join(tempfile.gettempdir(), "starship_battles_temp_designs")
            self.designs_folder = os.path.join(temp_base, f"empire_{empire_id}")
            logger.info(f"DesignLibrary: No savegame path - using temp folder: {self.designs_folder}")

        # Ensure designs folder exists
        try:
            os.makedirs(self.designs_folder, exist_ok=True)
            logger.debug(f"DesignLibrary: Ensured designs folder exists: {self.designs_folder}")
        except PermissionError as e:
            logger.error(f"Permission denied creating designs folder '{self.designs_folder}' for empire_{empire_id}: {e}")
        except OSError as e:
            logger.error(f"OS error creating designs folder '{self.designs_folder}' for empire_{empire_id}: {e}")
            # Fallback to temp directory
            import tempfile
            temp_base = os.path.join(tempfile.gettempdir(), "starship_battles_temp_designs")
            self.designs_folder = os.path.join(temp_base, f"empire_{empire_id}")
            os.makedirs(self.designs_folder, exist_ok=True)
            logger.error(f"DesignLibrary: Using fallback temp folder: {self.designs_folder}")

    def scan_designs(self) -> List[DesignMetadata]:
        """
        Scan designs folder and build metadata list.

        Returns:
            List of DesignMetadata objects for all designs in the library
            (empty list if no savegame path)
        """
        # Return empty list if no designs folder
        if self.designs_folder is None:
            logger.warning("scan_designs: designs_folder is None, returning empty list")
            return []

        designs = []
        pattern = os.path.join(self.designs_folder, "*.json")
        logger.debug(f"scan_designs: Scanning pattern: {pattern}")

        matching_files = list(glob.glob(pattern))
        logger.debug(f"scan_designs: Found {len(matching_files)} JSON files")

        for filepath in matching_files:
            try:
                logger.debug(f"scan_designs: Loading {filepath}")
                design_id = os.path.splitext(os.path.basename(filepath))[0]
                metadata = DesignMetadata.from_design_file(filepath, design_id)
                logger.debug(f"scan_designs: Loaded design '{metadata.name}' (vehicle_type={metadata.vehicle_type}, design_id={design_id})")
                designs.append(metadata)
            except JSONDecodeError as e:
                logger.error(f"scan_designs: Corrupt JSON in design file {filepath}: {e}")
                continue
            except KeyError as e:
                logger.error(f"scan_designs: Missing required field in design {filepath}: {e}")
                continue
            except (PermissionError, OSError) as e:
                logger.error(f"scan_designs: Cannot read design file {filepath}: {e}")
                continue
            except ValidationException as e:
                # Log validation errors but continue scanning
                logger.exception(f"scan_designs: Validation error loading design from {filepath}: {e}")
                continue

        logger.debug(f"scan_designs: Successfully loaded {len(designs)} designs")
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
        logger.info(f"DesignLibrary.save_design called for '{design_name}'")
        logger.debug(f"  designs_folder: {self.designs_folder}")
        logger.debug(f"  empire_id: {self.empire_id}")
        logger.debug(f"  savegame_path: {self.savegame_path}")

        # Safety check
        if self.designs_folder is None:
            logger.error("Design library not properly initialized - designs_folder is None")
            return False, "Design library not properly initialized"

        design_id = self._sanitize_design_id(design_name)
        filepath = os.path.join(self.designs_folder, f"{design_id}.json")
        logger.debug(f"  design_id: {design_id}")
        logger.debug(f"  filepath: {filepath}")

        # Check if design exists and was ever built
        if os.path.exists(filepath) and design_id in built_designs:
            logger.debug(f"Cannot overwrite '{design_name}' - already built")
            return False, f"Cannot overwrite '{design_name}' - this design has been built in-game"

        try:
            logger.debug("Creating metadata from ship...")
            # Create metadata
            metadata = DesignMetadata.from_ship(ship, design_id)
            logger.debug("Metadata created successfully")

            # If updating existing design, preserve created_date and times_built
            if os.path.exists(filepath):
                logger.debug("Design exists, loading old metadata...")
                old_data = load_json_required(filepath)
                old_metadata = old_data.get("_metadata", {})
                metadata.created_date = old_metadata.get("created_date", metadata.created_date)
                metadata.times_built = old_metadata.get("times_built", 0)
                metadata.is_obsolete = old_metadata.get("is_obsolete", False)
                logger.debug("Old metadata loaded successfully")

            metadata.last_modified = datetime.now().isoformat()

            logger.debug("Calling ship.to_dict()...")
            # Get ship data and embed metadata
            ship_data = ship.to_dict()
            logger.debug(f"ship.to_dict() completed. Data type: {type(ship_data)}")
            logger.debug(f"ship_data keys: {ship_data.keys() if isinstance(ship_data, dict) else 'NOT A DICT!'}")

            logger.debug("Embedding metadata in ship data...")
            ship_data = metadata.embed_in_ship_data(ship_data)
            logger.debug("Metadata embedded successfully")

            logger.debug(f"Saving to file: {filepath}")
            # Save to file
            save_json(filepath, ship_data, indent=4)
            logger.info(f"Design saved successfully: {design_name}")

            return True, f"Saved design: {design_name}"

        except PermissionError as e:
            logger.error(f"Permission denied saving design '{design_name}' to {filepath}")
            return False, f"Failed to save design: Permission denied"
        except OSError as e:
            logger.error(f"OS error saving design '{design_name}' to {filepath}: {e}")
            return False, f"Failed to save design: {str(e)}"
        except ValidationException as e:
            logger.exception(f"Serialization error saving design '{design_name}': {e}")
            return False, f"Failed to save design: Invalid design data"
        except (AttributeError, KeyError) as e:
            logger.exception(f"Unexpected error saving design '{design_name}': {e}")
            return False, f"Failed to save design: {str(e)}"

    def load_design_data(self, design_id: str) -> DesignLoadResult:
        """
        Load raw design data without creating Ship instance.

        PROJ-251: Returns DesignLoadResult instead of Optional[dict] so callers
        can distinguish failure modes.

        Args:
            design_id: Design ID to load

        Returns:
            DesignLoadResult with data on success, or error info on failure.
        """
        if self.designs_folder is None:
            return DesignLoadResult.not_found(design_id)

        filepath = os.path.join(self.designs_folder, f"{design_id}.json")

        if not os.path.exists(filepath):
            return DesignLoadResult.not_found(design_id)

        try:
            data = load_json_required(filepath)
            return DesignLoadResult.ok(data)
        except JSONDecodeError as e:
            logger.warning(f"DesignLibrary: Corrupt JSON in design '{design_id}' at '{filepath}': {e}")
            return DesignLoadResult.corrupt(design_id, str(e))
        except PermissionError as e:
            logger.error(f"DesignLibrary: Permission denied reading design '{design_id}' from '{filepath}': {e}")
            return DesignLoadResult.permission_denied(design_id, str(e))
        except OSError as e:
            logger.error(f"DesignLibrary: IO error reading design '{design_id}' from '{filepath}': {e}")
            return DesignLoadResult.io_error(design_id, str(e))

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

        except JSONDecodeError as e:
            return False, f"Design file is corrupted"
        except (PermissionError, OSError) as e:
            return False, f"Failed to update design: {str(e)}"
        except (KeyError, TypeError, ValueError, AttributeError) as e:
            logger.error(f"DesignLibrary: Unexpected error marking design '{design_id}' obsolete: {e}")
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

        except JSONDecodeError as e:
            logger.warning(f"DesignLibrary: Corrupt JSON in design '{design_id}': {e}")
            return False
        except (PermissionError, OSError) as e:
            logger.warning(f"DesignLibrary: Cannot update design '{design_id}': {e}")
            return False
        except (KeyError, TypeError, ValueError, AttributeError) as e:
            logger.warning(f"DesignLibrary: Unexpected error incrementing built count for '{design_id}': {e}")
            return False

    def filter_designs(self,
                      ship_class: Optional[str] = None,
                      vehicle_type: Optional[str] = None,
                      design_role: Optional[str] = None,
                      show_obsolete: bool = False) -> List[DesignMetadata]:
        """
        Filter designs by criteria.

        Args:
            ship_class: Filter by ship class (None = no filter)
            vehicle_type: Filter by vehicle type (None = no filter)
            design_role: Filter by design role (None = no filter)
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

        if design_role:
            designs = [d for d in designs if d.design_role == design_role]

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
            design_role=filters.get('design_role'),
            show_obsolete=filters.get('show_obsolete', False)
        )

        # Apply name search
        if name_query:
            search_lower = name_query.lower()
            designs = [d for d in designs if search_lower in d.name.lower()]

        return designs

    @staticmethod
    def _sanitize_design_id(name: str) -> str:
        """
        Convert design name to safe filename.

        Args:
            name: Design name to sanitize

        Returns:
            Safe filename string
        """
        result = slugify(name)
        return result if result else "unnamed_design"

    def get_design_path(self, design_id: str) -> str:
        """
        Get full filepath for a design ID.

        Args:
            design_id: Design ID

        Returns:
            Full path to design file
        """
        return os.path.join(self.designs_folder, f"{design_id}.json")

    def has_design(self, design_id: str) -> bool:
        """
        Check if a design exists.

        Args:
            design_id: Design ID to check

        Returns:
            True if design exists, False otherwise
        """
        return os.path.exists(self.get_design_path(design_id))

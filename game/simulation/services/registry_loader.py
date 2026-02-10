"""
Registry Loader - Simulation layer module for loading registry data from disk.

PROJ-90 Phase 2: This module was extracted from RegistryManager.reload_all_from_directory()
to fix the Core -> Simulation layer violation. The Core layer (registry.py) should not
import from Simulation layer. This free function lives in the Simulation layer where
the simulation-specific loader imports are legal.

Usage:
    from game.simulation.services.registry_loader import reload_registries_from_directory
    from game.core.registry import RegistryManager

    manager = RegistryManager.instance()
    success = reload_registries_from_directory(manager, "data/")
"""
import json
import logging
import os
from pathlib import Path
from typing import Union, TYPE_CHECKING

# These imports are legal here - Simulation layer can import its own modules
from game.simulation.components.component import load_modifiers, load_components
from game.simulation.entities.ship_loader import load_vehicle_classes

if TYPE_CHECKING:
    from game.core.registry import RegistryManager


def reload_registries_from_directory(
    registry_manager: "RegistryManager",
    data_dir: Union[str, Path]
) -> bool:
    """
    Reload all registry data from a directory.

    Clears all existing registry data and reloads components, modifiers,
    and vehicle classes from JSON files in the specified directory.

    PROJ-44: Centralizes registry reload logic previously scattered across
    BuilderScreen and other locations.

    PROJ-90: Extracted from RegistryManager to Simulation layer to fix
    the Core -> Simulation layer violation.

    Args:
        registry_manager: The RegistryManager instance to populate.
        data_dir: Path to directory containing data files (string or Path).
                 Looks for: components.json, modifiers.json, vehicleclasses.json
                 Also checks for test_* prefixed versions.

    Returns:
        True if directory exists (even if some files missing), False if directory invalid.

    Raises:
        FrozenStateException: If the registry is frozen.
    """
    registry_manager._check_frozen()

    logger = logging.getLogger("StarshipBattles")

    # Normalize path
    if isinstance(data_dir, str):
        data_dir = Path(data_dir)

    if not data_dir.exists() or not data_dir.is_dir():
        logger.warning(f"RegistryLoader: Directory does not exist: {data_dir}")
        return False

    # Clear all registries first (preserves dict identity)
    registry_manager.components.clear()
    registry_manager.modifiers.clear()
    registry_manager.vehicle_classes.clear()
    registry_manager.resources.clear()
    registry_manager._validator = None

    # Helper to find file with test_ prefix fallback
    def find_file(*names):
        """Find first existing file from names, checking test_ prefix first."""
        for name in names:
            # Check test_ prefix first (for test data directories)
            test_path = data_dir / f"test_{name}"
            if test_path.exists():
                return test_path
            # Then standard name
            std_path = data_dir / name
            if std_path.exists():
                return std_path
        return None

    # Load modifiers first (components may depend on them)
    mod_path = find_file("modifiers.json")
    if mod_path:
        try:
            load_modifiers(str(mod_path))
            logger.info(f"RegistryLoader: Loaded modifiers from {mod_path}")
        except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            logger.error(f"RegistryLoader: Failed to load modifiers: {e}")

    # Load components
    comp_path = find_file("components.json")
    if comp_path:
        try:
            load_components(str(comp_path))
            logger.info(f"RegistryLoader: Loaded components from {comp_path}")
        except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            logger.error(f"RegistryLoader: Failed to load components: {e}")

    # Load vehicle classes (check multiple possible names)
    vclass_path = find_file("vehicleclasses.json", "classes.json")
    vlayer_path = find_file("vehiclelayers.json", "layers.json")
    if vclass_path:
        try:
            if vlayer_path:
                load_vehicle_classes(str(vclass_path), layers_file_path=str(vlayer_path))
                logger.info(f"RegistryLoader: Loaded classes from {vclass_path} with layers from {vlayer_path}")
            else:
                load_vehicle_classes(str(vclass_path))
                logger.info(f"RegistryLoader: Loaded classes from {vclass_path}")
        except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            logger.error(f"RegistryLoader: Failed to load vehicle classes: {e}")

    return True

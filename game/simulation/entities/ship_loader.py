"""
Ship Loader - Functions for loading vehicle class data and initializing ship data.

PROJ-174: Migrated to IRegistryProvider pattern for registry access.
"""
import logging
import os
from typing import Optional

from game.core.exceptions import MissingResourceException
from game.core.error_codes import ErrorCode
from game.core.json_utils import load_json, load_json_required

logger = logging.getLogger(__name__)
from game.core.registry import set_validator, get_default_registry_provider, get_validator
from game.simulation.validation.ship_validator import ShipDesignValidator
from game.core.paths import Paths


def get_or_create_validator(registry_provider=None):
    """Get the ship design validator, creating it if necessary.

    PROJ-174: Uses IRegistryProvider pattern for registry access.
    Validator storage remains on RegistryManager (lifecycle concern).

    Args:
        registry_provider: Optional IRegistryProvider. If None, uses default.

    Returns:
        ShipDesignValidator instance.
    """
    # Validator storage is on RegistryManager (singleton lifecycle)
    # PROJ-195: Use module-level wrapper instead of direct singleton access
    val = get_validator()
    if not val:
        if registry_provider is None:
            registry_provider = get_default_registry_provider()
        from game.core.registry import GameRegistries
        registries = GameRegistries(
            components=registry_provider.get_components(),
            modifiers=registry_provider.get_modifiers(),
            vehicle_classes=registry_provider.get_vehicle_classes(),
            resources=registry_provider.get_resources()
        )
        val = ShipDesignValidator(registries=registries)
        set_validator(val)
    return val


def load_vehicle_classes_data(
    file_path: str = None,
    layers_file_path: Optional[str] = None
) -> dict:
    """
    Pure function to load vehicle class definitions from JSON.

    PROJ-38: Returns a dictionary of vehicle class definitions without
    modifying any global state. Use this for DI patterns.

    Args:
        file_path: Path to the vehicle classes JSON file
        layers_file_path: Optional path to the layer definitions JSON file

    Returns:
        Dict[str, dict]: Vehicle class definitions keyed by class name
    """
    import copy

    if file_path is None:
        file_path = Paths.VEHICLE_CLASSES_FILE

    # Check if we need to resolve path relative to this file
    if not os.path.exists(file_path):
        # Try finding it relative to module
        base_dir = os.path.dirname(os.path.abspath(__file__))
        abs_path = os.path.join(base_dir, file_path)
        if os.path.exists(abs_path):
            file_path = abs_path

    # Try to load layer definitions (optional)
    layer_definitions = {}

    if layers_file_path:
        layers_path = layers_file_path
    else:
        layers_path = os.path.join(os.path.dirname(file_path), "vehiclelayers.json")

    layer_data = load_json(layers_path, default={})
    if layer_data:
        layer_definitions = layer_data.get('definitions', {})

    # Load vehicle classes (required)
    try:
        data = load_json_required(file_path)
    except FileNotFoundError as e:
        raise MissingResourceException(
            f"Vehicle class data file not found: {file_path}",
            code=ErrorCode.RESOURCE_NOT_FOUND.value,
            context={"file_path": str(file_path), "severity": "critical"}
        ) from e

    raw_classes = data.get('classes', {})

    # Deep copy to ensure independence
    result = copy.deepcopy(raw_classes)

    # Post-process to resolve layer configurations
    for cls_name, cls_def in result.items():
        if 'layer_config' in cls_def:
            config_id = cls_def['layer_config']
            if config_id in layer_definitions:
                cls_def['layers'] = copy.deepcopy(layer_definitions[config_id])

    return result


def load_vehicle_classes(
    file_path: str = None,
    layers_file_path: Optional[str] = None,
    registry_provider=None
) -> None:
    """
    Load vehicle class definitions from JSON and populate the global registry.

    Wrapper around load_vehicle_classes_data() that also populates the registry.

    PROJ-174: Uses IRegistryProvider pattern for registry access.

    Args:
        file_path: Path to vehicle classes JSON. Defaults to Paths.VEHICLE_CLASSES_FILE.
        layers_file_path: Optional path to layer definitions JSON.
        registry_provider: Optional IRegistryProvider. If None, uses default.
    """
    if file_path is None:
        file_path = Paths.VEHICLE_CLASSES_FILE

    # Load data using pure function
    result = load_vehicle_classes_data(file_path, layers_file_path)

    # Log layer info (we need to check the layers file to get the count)
    if layers_file_path:
        layers_path = layers_file_path
    else:
        layers_path = os.path.join(os.path.dirname(file_path), "vehiclelayers.json")

    layer_data = load_json(layers_path, default={})
    if layer_data:
        layer_definitions = layer_data.get('definitions', {})
        logger.info(f"Loaded {len(layer_definitions)} layer configurations from {os.path.basename(layers_path)}.")

    # PROJ-174: Use provider pattern for registry access
    if registry_provider is None:
        registry_provider = get_default_registry_provider()
    classes = registry_provider.get_vehicle_classes()
    classes.clear()
    classes.update(result)

    logger.info(f"Loaded {len(classes)} vehicle classes.")


def initialize_ship_data(base_path: Optional[str] = None) -> None:
    """Facade for initializing all ship-related data."""
    if base_path:
        path = os.path.join(base_path, "data", "vehicleclasses.json")
        load_vehicle_classes(path)
    else:
        load_vehicle_classes()

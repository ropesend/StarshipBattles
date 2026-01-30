"""
Ship Loader - Functions for loading vehicle class data and initializing ship data.

PROJ-50: Removed get_default_registry_provider import - use RegistryManager instead.
"""

import os
from typing import Optional

from game.core.logger import log_info, log_warning
from game.core.json_utils import load_json, load_json_required
from game.core.registry import RegistryManager, set_validator
from game.simulation.ship_validator import ShipDesignValidator
from game.core.paths import Paths


def get_or_create_validator():
    """Get the ship design validator, creating it if necessary.

    PROJ-50: Creates validator with GameRegistries from RegistryManager.
    """
    val = RegistryManager.instance().get_validator()
    if not val:
        from game.core.registry import GameRegistries
        mgr = RegistryManager.instance()
        registries = GameRegistries(
            components=mgr.components,
            modifiers=mgr.modifiers,
            vehicle_classes=mgr.vehicle_classes,
            resources=mgr.resources
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
    except FileNotFoundError:
        raise RuntimeError(f"Critical Error: {file_path} not found. Vehicle class data is required for game operation.")

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


def load_vehicle_classes(file_path: str = None, layers_file_path: Optional[str] = None) -> None:
    """
    Load vehicle class definitions from JSON and populate the global registry.

    This is a thin wrapper around load_vehicle_classes_data() for backward
    compatibility. New code should prefer DI via load_vehicle_classes_data().
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
        log_info(f"Loaded {len(layer_definitions)} layer configurations from {os.path.basename(layers_path)}.")

    # PROJ-50: Update registry in place using RegistryManager (not provider)
    classes = RegistryManager.instance().vehicle_classes
    classes.clear()
    classes.update(result)

    log_info(f"Loaded {len(classes)} vehicle classes.")


def initialize_ship_data(base_path: Optional[str] = None) -> None:
    """Facade for initializing all ship-related data."""
    if base_path:
        path = os.path.join(base_path, "data", "vehicleclasses.json")
        load_vehicle_classes(path)
    else:
        load_vehicle_classes()

"""
Ship Loader - Functions for loading vehicle class data and initializing ship data.
"""

import os
from typing import Optional

from game.core.logger import log_info, log_warning
from game.core.json_utils import load_json, load_json_required
from game.core.registry import get_vehicle_classes, get_validator, set_validator
from game.simulation.ship_validator import ShipDesignValidator
from game.core.paths import Paths


def get_or_create_validator():
    """Get the ship design validator, creating it if necessary."""
    val = get_validator()
    if not val:
        val = ShipDesignValidator()
        set_validator(val)
    return val


def load_vehicle_classes_data(
    filepath: str = None,
    layers_filepath: Optional[str] = None
) -> dict:
    """
    Pure function to load vehicle class definitions from JSON.

    PROJ-38: Returns a dictionary of vehicle class definitions without
    modifying any global state. Use this for DI patterns.

    Args:
        filepath: Path to the vehicle classes JSON file
        layers_filepath: Optional path to the layer definitions JSON file

    Returns:
        Dict[str, dict]: Vehicle class definitions keyed by class name
    """
    import copy

    if filepath is None:
        filepath = Paths.VEHICLE_CLASSES_FILE

    # Check if we need to resolve path relative to this file
    if not os.path.exists(filepath):
        # Try finding it relative to module
        base_dir = os.path.dirname(os.path.abspath(__file__))
        abs_path = os.path.join(base_dir, filepath)
        if os.path.exists(abs_path):
            filepath = abs_path

    # Try to load layer definitions (optional)
    layer_definitions = {}

    if layers_filepath:
        layers_path = layers_filepath
    else:
        layers_path = os.path.join(os.path.dirname(filepath), "vehiclelayers.json")

    layer_data = load_json(layers_path, default={})
    if layer_data:
        layer_definitions = layer_data.get('definitions', {})

    # Load vehicle classes (required)
    try:
        data = load_json_required(filepath)
    except FileNotFoundError:
        raise RuntimeError(f"Critical Error: {filepath} not found. Vehicle class data is required for game operation.")

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


def load_vehicle_classes(filepath: str = None, layers_filepath: Optional[str] = None) -> None:
    """
    Load vehicle class definitions from JSON and populate the global registry.

    This is a thin wrapper around load_vehicle_classes_data() for backward
    compatibility. New code should prefer DI via load_vehicle_classes_data().
    """
    if filepath is None:
        filepath = Paths.VEHICLE_CLASSES_FILE

    # Load data using pure function
    result = load_vehicle_classes_data(filepath, layers_filepath)

    # Log layer info (we need to check the layers file to get the count)
    if layers_filepath:
        layers_path = layers_filepath
    else:
        layers_path = os.path.join(os.path.dirname(filepath), "vehiclelayers.json")

    layer_data = load_json(layers_path, default={})
    if layer_data:
        layer_definitions = layer_data.get('definitions', {})
        log_info(f"Loaded {len(layer_definitions)} layer configurations from {os.path.basename(layers_path)}.")

    # Update registry in place to preserve references
    classes = get_vehicle_classes()
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

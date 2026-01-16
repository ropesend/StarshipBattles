"""
Ship Loader - Functions for loading vehicle class data and initializing ship data.
"""

import os
from typing import Optional

from game.core.logger import log_info, log_warning
from game.core.json_utils import load_json, load_json_required
from game.core.registry import RegistryManager, get_vehicle_classes, get_validator
from game.simulation.ship_validator import ShipDesignValidator


def get_or_create_validator():
    """Get the ship design validator, creating it if necessary."""
    val = get_validator()
    if not val:
        val = ShipDesignValidator()
        RegistryManager.instance().set_validator(val)
    return val


def load_vehicle_classes(filepath: str = "data/vehicleclasses.json", layers_filepath: Optional[str] = None) -> None:
    """
    Load vehicle class definitions from JSON.
    This should be called explicitly during game initialization.
    """

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
        log_info(f"Loaded {len(layer_definitions)} layer configurations from {os.path.basename(layers_path)}.")

    # Load vehicle classes (required)
    try:
        data = load_json_required(filepath)
    except FileNotFoundError:
        raise RuntimeError(f"Critical Error: {filepath} not found. Vehicle class data is required for game operation.")

    # Update in place to preserve references
    classes = get_vehicle_classes()
    classes.clear()

    raw_classes = data.get('classes', {})

    # Post-process to resolve layer configurations
    for cls_name, cls_def in raw_classes.items():
        if 'layer_config' in cls_def:
            config_id = cls_def['layer_config']
            if config_id in layer_definitions:
                cls_def['layers'] = layer_definitions[config_id]
            else:
                log_warning(f"Class {cls_name} references unknown layer config {config_id}")

    classes.update(raw_classes)
    log_info(f"Loaded {len(classes)} vehicle classes.")


def initialize_ship_data(base_path: Optional[str] = None) -> None:
    """Facade for initializing all ship-related data."""
    if base_path:
        path = os.path.join(base_path, "data", "vehicleclasses.json")
        load_vehicle_classes(path)
    else:
        load_vehicle_classes()

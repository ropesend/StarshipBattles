"""
Homeworld Presets - Environmental defaults for each planet type.

This module provides functions to load and apply homeworld presets,
which define the environmental preferences for races based on their
homeworld planet type.
"""
from typing import Dict, List, Optional

from game.core.json_utils import load_json
from game.core.paths import Paths
from game.strategy.data.race_config import RaceConfig


# Cache for loaded presets
_presets_cache: Optional[Dict[str, dict]] = None


def _get_presets_path() -> str:
    """Get the path to the homeworld_presets.json file."""
    return Paths.HOMEWORLD_PRESETS_FILE


def load_homeworld_presets() -> Dict[str, dict]:
    """
    Load homeworld presets from JSON file.

    Returns:
        Dictionary mapping planet type ID to preset data.
        Example: {"CONTINENTAL": {...}, "JOVIAN": {...}}
    """
    global _presets_cache

    if _presets_cache is not None:
        return _presets_cache

    data = load_json(_get_presets_path())
    if data is None or "presets" not in data:
        return {}

    # Convert list to dict keyed by ID
    _presets_cache = {
        preset["id"]: preset for preset in data["presets"]
    }

    return _presets_cache


def get_preset_for_planet_type(planet_type_name: str) -> Optional[dict]:
    """
    Get the homeworld preset for a specific planet type.

    Args:
        planet_type_name: The planet type ID (e.g., "CONTINENTAL", "JOVIAN")

    Returns:
        Preset dictionary or None if not found
    """
    presets = load_homeworld_presets()
    return presets.get(planet_type_name)


def apply_preset_to_config(preset: dict, race_config: RaceConfig) -> None:
    """
    Apply a homeworld preset to a RaceConfig, setting all environment fields.

    Args:
        preset: The preset dictionary from get_preset_for_planet_type()
        race_config: The RaceConfig to update
    """
    if preset is None:
        return

    # Set homeworld type
    race_config.homeworld_type = preset["id"]

    # Set gravity
    race_config.gravity_ideal = preset["gravity_ideal"]
    race_config.gravity_tolerance = preset["gravity_tolerance"]

    # Set temperature
    race_config.temperature_ideal = preset["temperature_ideal"]
    race_config.temperature_tolerance = preset["temperature_tolerance"]

    # Set water
    race_config.water_ideal = preset["water_ideal"]
    race_config.water_tolerance = preset["water_tolerance"]

    # Set radiation
    race_config.radiation_tolerance = preset["radiation_tolerance"]

    # Set atmosphere preferences
    for gas, value in preset["atmosphere_preferences"].items():
        if gas in race_config.atmosphere_preferences:
            race_config.atmosphere_preferences[gas] = value


def get_available_homeworld_names() -> List[str]:
    """
    Get list of homeworld display names for UI dropdowns.

    Returns:
        List of human-readable homeworld type names
    """
    presets = load_homeworld_presets()
    return [preset["name"] for preset in presets.values()]


def get_preset_id_from_name(display_name: str) -> Optional[str]:
    """
    Convert a display name back to preset ID.

    Args:
        display_name: Human-readable name (e.g., "Ice Giant")

    Returns:
        Preset ID (e.g., "ICE_GIANT") or None if not found
    """
    presets = load_homeworld_presets()
    for preset_id, preset in presets.items():
        if preset["name"] == display_name:
            return preset_id
    return None


def clear_cache() -> None:
    """Clear the presets cache. Useful for testing."""
    global _presets_cache
    _presets_cache = None

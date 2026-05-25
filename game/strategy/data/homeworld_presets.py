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


def reset_homeworld_presets_cache() -> None:
    """Drop the cached homeworld presets.

    Wired into `game.data_loader` so a mod that ships its own
    homeworld_presets.json takes effect after a data-set switch.
    """
    global _presets_cache
    _presets_cache = None


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
    """Apply a homeworld preset to a RaceConfig.

    PROJ-283 Phase 5: presets now declare partial `preferences` keyed by
    `FACTOR_REGISTRY` ids — see `data/homeworld_presets.json` `_schema`.
    For each factor listed in the preset, build a fresh
    `EnvironmentalPreference` (filling unspecified setpoint/tolerance
    from registry defaults). Factors not listed in the preset are NOT
    touched — the race keeps whatever value it already had.

    Args:
        preset: The preset dictionary from `get_preset_for_planet_type`,
            or None (no-op).
        race_config: The RaceConfig to mutate in place.
    """
    if preset is None:
        return

    from game.strategy.data.environmental_preference import EnvironmentalPreference
    from game.strategy.data.habitability_factors import get_factor

    race_config.homeworld_type = preset["id"]

    for factor_id, override in preset.get("preferences", {}).items():
        factor = get_factor(factor_id)
        # Default to registry values when the preset omits a field; this
        # lets a preset say `{"setpoint": 0}` without restating tolerance.
        setpoint = float(override.get("setpoint", factor.default_setpoint))
        tolerance = float(override.get("tolerance", factor.default_tolerance))
        race_config.preferences[factor_id] = EnvironmentalPreference(
            setpoint=setpoint,
            # `EnvironmentalPreference.validate` requires tolerance >= 0;
            # `step` is the cost-curve unit, not a hard floor on tolerance.
            tolerance=max(tolerance, 0.0),
            min_value=factor.min_value,
            max_value=factor.max_value,
            step=factor.step,
        )

    if "base_reproduction_rate" in preset:
        race_config.base_reproduction_rate = float(preset["base_reproduction_rate"])


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
    reset_homeworld_presets_cache()


# Self-register the cache reset with the data lifecycle.
from game.data_loader import register_data_cache_invalidator as _register_data_cache_invalidator
_register_data_cache_invalidator(reset_homeworld_presets_cache)

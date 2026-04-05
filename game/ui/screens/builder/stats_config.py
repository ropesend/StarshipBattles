"""Stats configuration loader for the ship builder.

Loads stat layout from data/stats_layout.json and provides module-level
constants for each stat group. Sub-modules handle definitions, getters,
and dynamic row generation.

Public API (all re-exported for backward compatibility):
- StatDefinition: Stat row definition class
- STATS_CONFIG, STATS_MAIN, etc.: Loaded stat groups
- get_logistics_rows, get_construction_rows: Dynamic row generators
- get_strategic_rows, has_strategic_abilities: Strategic section
- get_crew_required: Crew requirement getter
"""
import logging
from game.core.json_utils import load_json

logger = logging.getLogger(__name__)

# Re-export public API from sub-modules
from .stat_definitions import StatDefinition  # noqa: F401
from .stat_getters import (  # noqa: F401
    GETTERS, FORMATTERS, VALIDATORS, UNITS,
    get_crew_required, get_resource_consumption, get_resource_storage,
    get_resource_generation, get_resource_endurance, get_resource_replenish,
    get_resource_max_usage,
    fmt_time, fmt_multiply, fmt_decimal, fmt_score, fmt_targeting,
    mass_validator, crew_validator, life_support_validator,
    get_mass_display, get_crew_capacity, get_life_support, get_max_targets,
    get_armor_hp, get_maneuver_points, get_strategic_speed,
    get_fuel_consumption, get_ammo_consumption, get_energy_consumption,
)
from .stat_rows_dynamic import (  # noqa: F401
    get_logistics_rows, get_construction_rows,
    get_strategic_rows, has_strategic_abilities,
)


def load_stats_config():
    """Load stats configuration from data/stats_layout.json."""
    import os

    path = os.path.join(os.getcwd(), 'data', 'stats_layout.json')
    data = load_json(path, default={})
    if not data:
        logger.warning(f"Stats config not found or empty: {path}")
        return {}

    loaded_groups = {}

    if 'groups' not in data:
        return {}

    for group_key, group_data in data['groups'].items():
        items = []
        for item_data in group_data.get('items', []):
            raw_getter = GETTERS.get(item_data.get('getter')) if item_data.get('getter') else None

            getter = raw_getter
            if raw_getter and item_data.get('getter_args'):
                args = item_data['getter_args']
                getter = lambda s, g=raw_getter, a=args: g(s, *a)

            fmt_val = item_data.get('formatter', "{:.0f}")
            formatter = FORMATTERS.get(fmt_val, fmt_val)

            unit_val = item_data.get('unit', "")
            unit = UNITS.get(unit_val, unit_val)

            validator = VALIDATORS.get(item_data.get('validator')) if item_data.get('validator') else None

            stat_def = StatDefinition(
                id=item_data['id'],
                label=item_data['label'],
                key=item_data.get('key'),
                getter=getter,
                formatter=formatter,
                unit=unit,
                validator=validator
            )
            items.append(stat_def)
        loaded_groups[group_key] = items

    return loaded_groups


# Load on module import
STATS_CONFIG = load_stats_config()

STATS_MAIN = STATS_CONFIG.get('main', [])
STATS_MANEUVERING = STATS_CONFIG.get('maneuvering', [])
STATS_SHIELDS = STATS_CONFIG.get('shields', [])
STATS_ARMOR = STATS_CONFIG.get('armor', [])
STATS_TARGETING = STATS_CONFIG.get('targeting', [])
STATS_LOGISTICS = STATS_CONFIG.get('logistics', [])
STATS_CREW_LOGISTICS = STATS_CONFIG.get('crewlogistics', [])
STATS_FIGHTER_SUPPORT = STATS_CONFIG.get('fightersupport', [])

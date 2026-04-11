"""Stats configuration loader for the ship builder.

Loads stat layout from data/stats_layout.json and data/stats_sections.json.
Provides module-level constants for stat groups and section visibility resolution.

Public API (all re-exported for backward compatibility):
- StatDefinition, SectionDefinition: Definition classes
- STATS_CONFIG, STATS_MAIN, etc.: Loaded stat groups (legacy)
- SECTIONS_CONFIG, ALWAYS_VISIBLE: Section-based config (new)
- resolve_section_visibility: Visibility resolver
- get_logistics_rows, get_construction_rows: Dynamic row generators
- get_strategic_rows, has_strategic_abilities: Strategic section
- get_crew_required: Crew requirement getter
"""
import logging
from typing import Dict, List, Optional
from game.core.json_utils import load_json

logger = logging.getLogger(__name__)

# Re-export public API from sub-modules
from .stat_definitions import StatDefinition, SectionDefinition  # noqa: F401
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
    from game.core.paths import Paths

    path = Paths.STATS_LAYOUT_FILE
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


# ─────────────────────────────────────────────────────────────────
# Section-based configuration (new visibility engine)
# ─────────────────────────────────────────────────────────────────

# Dynamic section generators — maps generator name to callable(ship) -> List[StatDefinition]
SECTION_GENERATORS: Dict[str, callable] = {
    'logistics': get_logistics_rows,
    'construction': get_construction_rows,
    'strategic': get_strategic_rows,
}


def load_sections_config() -> Dict[str, SectionDefinition]:
    """Load section-based stats configuration from data/stats_sections.json."""
    from game.core.paths import Paths

    path = Paths.STATS_SECTIONS_FILE
    data = load_json(path, default={})
    if not data or 'sections' not in data:
        logger.warning("Sections config not found or empty: %s", path)
        return {}, {}

    sections = {}
    for sec_key, sec_data in data['sections'].items():
        items = []
        for item_data in sec_data.get('items', []):
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

            items.append(StatDefinition(
                id=item_data['id'],
                label=item_data['label'],
                key=item_data.get('key'),
                getter=getter,
                formatter=formatter,
                unit=unit,
                validator=validator,
            ))

        sections[sec_key] = SectionDefinition(
            key=sec_key,
            title=sec_data.get('title', sec_key),
            column=sec_data.get('column', 1),
            order=sec_data.get('order', 100),
            visibility=sec_data.get('visibility', 'always'),
            items=items,
            generator=sec_data.get('generator'),
        )

    always_visible = data.get('always_visible', {})
    return sections, always_visible


def resolve_section_visibility(
    section: SectionDefinition,
    ship,
    vehicle_type: str,
    always_visible: Dict[str, List[str]],
    generators: Optional[Dict[str, callable]] = None,
) -> bool:
    """Determine whether a section should be visible for the current design.

    Resolution order:
    1. visibility == "always" → True
    2. Section key in always_visible[vehicle_type] → True
    3. ability_present → True if ship has any listed ability
    4. dynamic → True if generator returns non-empty rows
    5. Otherwise → False

    Args:
        section: The section to check.
        ship: Ship object to inspect for abilities.
        vehicle_type: Current vehicle type string.
        always_visible: Per-vehicle-type always-visible section lists.
        generators: Optional generator registry (defaults to SECTION_GENERATORS).

    Returns:
        True if the section should be displayed.
    """
    vis = section.visibility

    # Rule 1: Always visible
    if vis == "always":
        return True

    # Rule 2: Always-visible override per vehicle type
    type_overrides = always_visible.get(vehicle_type, [])
    if section.key in type_overrides:
        return True

    # Rules 3-4 require a dict visibility
    if not isinstance(vis, dict):
        return False

    vis_type = vis.get('type', '')

    # Rule 3: Ability present on any component
    if vis_type == 'ability_present':
        required_abilities = vis.get('abilities', [])
        for comp in ship.get_all_components():
            for ab_name in required_abilities:
                if comp.has_ability(ab_name):
                    return True
        return False

    # Rule 4: Dynamic generator returns rows
    if vis_type == 'dynamic':
        gen_name = vis.get('generator', section.generator)
        gen_registry = generators if generators is not None else SECTION_GENERATORS
        gen_func = gen_registry.get(gen_name)
        if gen_func:
            return len(gen_func(ship)) > 0
        return False

    return False


# Load sections config on module import
try:
    SECTIONS_CONFIG, ALWAYS_VISIBLE = load_sections_config()
except Exception:
    logger.warning("Failed to load stats_sections.json, using empty config")
    SECTIONS_CONFIG, ALWAYS_VISIBLE = {}, {}

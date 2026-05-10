"""Dynamic stat row generators for resource, construction, and strategic sections.

These functions inspect a ship's actual state to generate stat rows on the fly,
rather than using the static JSON-defined layout. This allows the UI to adapt
to different ship configurations (e.g., only showing fuel rows if fuel exists).
"""
from __future__ import annotations

from typing import Any
from .stat_definitions import StatDefinition
from .stat_getters import (
    fmt_time,
    get_resource_storage, get_resource_generation, get_resource_max_usage,
    get_resource_endurance, get_resource_replenish,
)


def _get_constant_consumption(ship, res_name) -> Any:
    """Get constant consumption rate for a resource (excludes activation-based)."""
    from game.simulation.components.abilities.resources import ResourceConsumption
    total = 0
    try:
        for layer in ship.layers.values():
            for comp in layer.components:
                for ability in comp.ability_instances:
                    if isinstance(ability, ResourceConsumption):
                        if ability.resource_type == res_name and ability.trigger == 'constant':
                            total += ability.amount
    except (TypeError, AttributeError):
        pass
    return total


def _get_max_endurance(ship, res_name) -> Any:
    """Calculate endurance at max usage rate (constant + all weapons firing)."""
    try:
        capacity = get_resource_storage(ship, res_name)
        max_usage = get_resource_max_usage(ship, res_name)
        if not isinstance(max_usage, (int, float)) or max_usage <= 0:
            return float('inf')
        if not isinstance(capacity, (int, float)):
            return float('inf')
        return capacity / max_usage
    except (TypeError, AttributeError):
        return float('inf')


def _discover_resources(ship) -> Any:
    """Discover all resource names present on a ship and return sorted.

    Sources: resource registry, consumption attributes, generation attributes.
    Returns sorted list: fuel, energy, ammo first, then others alphabetically.
    """
    resource_order = ["fuel", "energy", "ammo"]
    try:
        res_names = set(ship.resources.get_resource_names())
    except (TypeError, AttributeError):
        res_names = set()

    for stat_type in ['consumption', 'generation']:
        for res in resource_order:
            try:
                val = ship.get_resource_stat(res, stat_type)
            except (TypeError, AttributeError):
                val = 0
            if isinstance(val, (int, float)) and val > 0:
                res_names.add(res)

    res_names = list(res_names)

    def sort_key(name) -> Any:
        if name in resource_order:
            return resource_order.index(name)
        return 999

    res_names.sort(key=sort_key)
    return res_names


def _build_resource_rows(ship, resource_name) -> Any:
    """Build conditional stat rows (1-7) for a single resource."""
    try:
        r = ship.resources.get_resource(resource_name)
        max_value = r.max_value if r else 0
        if not isinstance(max_value, (int, float)):
            max_value = 0

        const_consumption = _get_constant_consumption(ship, resource_name)
        if not isinstance(const_consumption, (int, float)):
            const_consumption = 0
        max_usage = get_resource_max_usage(ship, resource_name)
        if not isinstance(max_usage, (int, float)):
            max_usage = 0
        generation = get_resource_generation(ship, resource_name)
        if not isinstance(generation, (int, float)):
            generation = 0

        if max_value <= 0 and const_consumption <= 0 and max_usage <= 0 and generation <= 0:
            return []
    except (TypeError, AttributeError):
        return []

    rows = []
    label_base = resource_name.title()

    if max_value > 0:
        rows.append(StatDefinition(
            id=f"max_{resource_name}", label=f"{label_base} Capacity",
            getter=lambda s, n=resource_name: get_resource_storage(s, n),
            formatter="{:.0f}", unit=""
        ))

    if generation > 0:
        rows.append(StatDefinition(
            id=f"{resource_name}_gen", label=f"{label_base} Generation",
            getter=lambda s, n=resource_name: get_resource_generation(s, n),
            formatter="{:.1f}", unit="/s"
        ))

    if const_consumption > 0:
        rows.append(StatDefinition(
            id=f"{resource_name}_constant", label=f"{label_base} Constant Use",
            getter=lambda s, n=resource_name: _get_constant_consumption(s, n),
            formatter="{:.1f}", unit="/s"
        ))

    if max_usage > 0:
        rows.append(StatDefinition(
            id=f"{resource_name}_max_usage", label=f"{label_base} Max Usage",
            getter=lambda s, n=resource_name: get_resource_max_usage(s, n),
            formatter="{:.1f}", unit="/s"
        ))

    if max_value > 0 and const_consumption > 0:
        rows.append(StatDefinition(
            id=f"{resource_name}_endurance", label=f"{label_base} Endurance",
            getter=lambda s, n=resource_name: get_resource_endurance(s, n),
            formatter=fmt_time, unit=""
        ))
    elif max_usage > 0:
        rows.append(StatDefinition(
            id=f"{resource_name}_endurance", label=f"{label_base} Endurance",
            getter=lambda s, n=resource_name: _get_max_endurance(s, n),
            formatter=fmt_time, unit=""
        ))

    if max_value > 0 and max_usage > const_consumption and const_consumption > 0:
        rows.append(StatDefinition(
            id=f"{resource_name}_max_endurance", label=f"{label_base} Max Endurance",
            getter=lambda s, n=resource_name: _get_max_endurance(s, n),
            formatter=fmt_time, unit=""
        ))

    if generation > 0 and const_consumption <= 0 and max_usage <= 0 and max_value > 0:
        rows.append(StatDefinition(
            id=f"{resource_name}_recharge", label=f"{label_base} Recharge",
            getter=lambda s, n=resource_name: get_resource_replenish(s, n),
            formatter=fmt_time, unit=""
        ))

    return rows


def get_logistics_rows(ship) -> Any:
    """Generate stat rows for the Logistics section (dynamic resource rows)."""
    res_names = _discover_resources(ship)
    dynamic_rows = []
    for r_name in res_names:
        dynamic_rows.extend(_build_resource_rows(ship, r_name))
    return dynamic_rows


def get_construction_rows(ship) -> Any:
    """Generate stat rows for the Construction section."""
    from game.core.resources import ResourceCatalog

    PLANET_RESOURCE_NAMES = [d.id for d in ResourceCatalog.from_json().by_display_group("planetary")]
    LABEL_ABBREV = {
        "metals": "Metals", "organics": "Organics", "vapors": "Vapors",
        "radioactives": "Radact", "exotics": "Exotics",
    }

    rows = []
    for res in PLANET_RESOURCE_NAMES:
        def res_getter(ship, r=res) -> Any:
            return ship.construction_cost.get(r, 0)

        rows.append(StatDefinition(
            id=f"cost_{res.lower()}", label=LABEL_ABBREV.get(res, res),
            getter=res_getter, formatter="{:.0f}", unit=""
        ))
    return rows


# --- Strategic Ability Helpers ---

def _get_strategic_abilities(ship) -> dict:
    """Collect strategic ability data from all components on a ship."""
    harvesters = {}
    storage = {}
    has_planetary_yard = False
    has_space_shipyard = False
    shipyard_info = {}
    staging_capacity = 0.0

    try:
        layers = ship.layers
        layer_items = layers.values()
    except (TypeError, AttributeError):
        layer_items = []

    for layer in layer_items:
        for comp in getattr(layer, 'components', []):
            for ability in getattr(comp, 'ability_instances', []):
                cls_name = type(ability).__name__

                if cls_name == 'ResourceHarvesterAbility':
                    res = ability.resource_type
                    rate = ability.base_harvest_rate
                    harvesters[res] = harvesters.get(res, 0.0) + rate
                elif cls_name == 'LocalStorageAbility':
                    res = ability.resource_type
                    cap = ability.capacity
                    storage[res] = storage.get(res, 0.0) + cap
                elif cls_name == 'PlanetaryYardAbility':
                    has_planetary_yard = True
                elif cls_name == 'SpaceShipyardAbility':
                    has_space_shipyard = True
                    shipyard_info = {
                        'bonus': ability.construction_speed_bonus,
                        'max_mass': ability.max_ship_mass,
                        'rates': ability.production_rates,
                    }
                elif cls_name == 'StagingYardAbility':
                    staging_capacity += ability.capacity_mass

    return {
        'harvesters': harvesters, 'storage': storage,
        'has_planetary_yard': has_planetary_yard,
        'has_space_shipyard': has_space_shipyard,
        'shipyard_info': shipyard_info,
        'staging_capacity': staging_capacity,
    }


def get_strategic_rows(ship) -> Any:
    """Generate stat rows for the Strategic/Colony section."""
    info = _get_strategic_abilities(ship)
    rows = []

    LABEL_ABBREV = {
        "metals": "Metals", "organics": "Organics", "vapors": "Vapors",
        "radioactives": "Radact", "exotics": "Exotics",
    }

    if info['harvesters']:
        for res, rate in sorted(info['harvesters'].items()):
            def rate_getter(ship, r=res) -> Any:
                data = _get_strategic_abilities(ship)
                return data['harvesters'].get(r, 0.0)
            rows.append(StatDefinition(
                id=f"harvest_{res}", label=f"Harv {LABEL_ABBREV.get(res, res)}",
                getter=rate_getter, formatter="{:.1f}", unit="/turn"
            ))

    if info['storage']:
        for res, cap in sorted(info['storage'].items()):
            def cap_getter(ship, r=res) -> Any:
                data = _get_strategic_abilities(ship)
                return data['storage'].get(r, 0.0)
            rows.append(StatDefinition(
                id=f"storage_{res}", label=f"Stor {LABEL_ABBREV.get(res, res)}",
                getter=cap_getter, formatter="{:,.0f}", unit=""
            ))

    if info['has_planetary_yard']:
        def yard_getter(ship) -> Any:
            data = _get_strategic_abilities(ship)
            return 1.0 if data['has_planetary_yard'] else 0.0
        rows.append(StatDefinition(
            id="planetary_yard", label="Planet Yard",
            getter=yard_getter, formatter=lambda v: "Yes" if v > 0 else "No", unit=""
        ))

    if info['has_space_shipyard']:
        def shipyard_getter(ship) -> Any:
            data = _get_strategic_abilities(ship)
            si = data['shipyard_info']
            return si.get('bonus', 1.0) if si else 0.0
        rows.append(StatDefinition(
            id="space_shipyard", label="Shipyard",
            getter=shipyard_getter, formatter=lambda v: f"{v:.1f}x" if v > 0 else "No", unit=""
        ))

        def max_mass_getter(ship) -> Any:
            data = _get_strategic_abilities(ship)
            si = data['shipyard_info']
            return si.get('max_mass', 0) if si else 0
        rows.append(StatDefinition(
            id="shipyard_max_mass", label="Max Build Mass",
            getter=max_mass_getter, formatter="{:,.0f}", unit="kg"
        ))

    if info['staging_capacity'] > 0:
        def staging_getter(ship) -> Any:
            data = _get_strategic_abilities(ship)
            return data['staging_capacity']
        rows.append(StatDefinition(
            id="staging_capacity", label="Staging Cap",
            getter=staging_getter, formatter="{:,.0f}", unit="mass"
        ))

    return rows


def has_strategic_abilities(ship) -> bool:
    """Check if a ship has any strategic abilities worth displaying."""
    info = _get_strategic_abilities(ship)
    return bool(
        info['harvesters'] or info['storage'] or
        info['has_planetary_yard'] or info['has_space_shipyard'] or
        info['staging_capacity'] > 0
    )


# --- Cargo & Transport Dynamic Rows ---

def get_cargo_rows(ship) -> Any:
    """Generate stat rows for cargo, pod storage, and colonization."""
    rows = []

    # Cargo by type
    for cargo_type, capacity in sorted(ship.cargo_storage.items()):
        if capacity > 0:
            def cap_getter(s, ct=cargo_type) -> Any:
                return s.cargo_storage.get(ct, 0)
            label = cargo_type.replace('_', ' ').title()
            rows.append(StatDefinition(
                id=f"cargo_{cargo_type}", label=f"{label} Cap",
                getter=cap_getter, formatter="{:,.0f}", unit=""
            ))

    # Pod storage
    if ship.pod_storage_mass > 0:
        rows.append(StatDefinition(
            id="pod_storage", label="Pod Storage",
            getter=lambda s: s.pod_storage_mass, formatter="{:,.0f}", unit=" mass"
        ))

    # Colony capability
    from .stat_getters import get_colony_types
    colony_str = get_colony_types(ship)
    if colony_str != 'None':
        rows.append(StatDefinition(
            id="colony_types", label="Colonizes",
            getter=get_colony_types, formatter=lambda v: str(v), unit=""
        ))

    return rows


def has_cargo_abilities(ship) -> bool:
    """Check if ship has any cargo/transport/colony abilities."""
    if ship.cargo_storage:
        return True
    if ship.pod_storage_mass > 0:
        return True
    for comp in ship.get_all_components():
        if comp.has_ability('ColonizePlanet'):
            return True
    return False


# --- Planetary Engineering Dynamic Rows ---

_PLANETARY_ABILITIES = {
    'AtmosphereModifier': ('Atmo Rate', 'modification_rate', '/turn'),
    'WaterModifier': ('Water Rate', 'modification_rate', '/turn'),
}

_ACTIVATABLE_ABILITIES = {
    'GravityModifier': 'Gravity Mod',
    'RadiationShield': 'Rad Shield',
    'PlanetaryShield': 'Planet Shield',
    'GeologicStabilizer': 'Geo Stabilizer',
    'StellarStabilizer': 'Star Stabilizer',
    'WarpFieldStabilizer': 'Warp Stabilizer',
}

def get_planetary_engineering_rows(ship) -> Any:
    """Generate rows for planetary modification abilities."""
    rows = []

    for ab_name, (label, rate_attr, unit) in _PLANETARY_ABILITIES.items():
        for comp in ship.get_all_components():
            if comp.has_ability(ab_name):
                ab = comp.get_ability(ab_name)
                rate = getattr(ab, rate_attr, 0)
                if rate != 0:
                    def rate_getter(s, an=ab_name, ra=rate_attr) -> Any:
                        total = 0
                        for c in s.get_all_components():
                            if c.has_ability(an):
                                a = c.get_ability(an)
                                total += getattr(a, ra, 0)
                        return total
                    rows.append(StatDefinition(
                        id=f"planetary_{ab_name.lower()}", label=label,
                        getter=rate_getter, formatter="{:.2f}", unit=unit
                    ))
                    break

    return rows


def get_planetary_defense_rows(ship) -> Any:
    """Generate rows for planetary defense/stabilizer abilities."""
    rows = []

    for ab_name, label in _ACTIVATABLE_ABILITIES.items():
        for comp in ship.get_all_components():
            if comp.has_ability(ab_name):
                ab = comp.get_ability(ab_name)
                activation = getattr(ab, 'activation_time', 0)
                scope = getattr(ab, 'scope', 'self')
                scope_text = f" ({scope})" if scope != 'self' else ""

                def drain_getter(s, an=ab_name) -> Any:
                    total = 0
                    for c in s.get_all_components():
                        if c.has_ability(an):
                            a = c.get_ability(an)
                            total += getattr(a, 'energy_drain_rate', 0)
                    return total

                rows.append(StatDefinition(
                    id=f"defense_{ab_name.lower()}", label=f"{label}{scope_text}",
                    getter=drain_getter, formatter="{:.1f}", unit=" E/s"
                ))

                if activation > 0:
                    rows.append(StatDefinition(
                        id=f"defense_{ab_name.lower()}_time", label=f"  Activation",
                        getter=lambda s, at=activation: at,
                        formatter="{:.0f}", unit="s"
                    ))
                break

    return rows


# --- Strategic Modifiers Dynamic Rows ---

def get_strategic_modifier_rows(ship) -> Any:
    """Generate rows for shield/damage modifiers with scope."""
    rows = []

    modifier_abilities = {
        'ShieldModifier': ('Shield Mult', 'multiplier'),
        'DamageModifier': ('Damage Mult', 'multiplier'),
        'BuildRateBooster': ('Build Rate', 'multiplier'),
        'ResourceHarvestBooster': ('Harvest Boost', 'multiplier'),
    }

    for ab_name, (label, mult_attr) in modifier_abilities.items():
        for comp in ship.get_all_components():
            if comp.has_ability(ab_name):
                ab = comp.get_ability(ab_name)
                scope = getattr(ab, 'scope', 'self')
                scope_text = f" ({scope})" if scope != 'self' else ""

                def mult_getter(s, an=ab_name, ma=mult_attr) -> Any:
                    # Aggregate: multiply across components
                    total = 1.0
                    for c in s.get_all_components():
                        if c.has_ability(an):
                            a = c.get_ability(an)
                            total *= getattr(a, ma, 1.0)
                    return total

                rows.append(StatDefinition(
                    id=f"modifier_{ab_name.lower()}", label=f"{label}{scope_text}",
                    getter=mult_getter, formatter="{:.2f}x", unit=""
                ))
                break

    return rows


# --- Superweapon Dynamic Rows ---

def get_superweapon_rows(ship) -> Any:
    """Generate rows for each superweapon type with activation count."""
    from .stat_getters import _superweapon_ability_names, _SUPERWEAPON_LABELS
    rows = []

    for ab_name in _superweapon_ability_names():
        count = 0
        for comp in ship.get_all_components():
            if comp.has_ability(ab_name):
                count += 1
        if count > 0:
            label = _SUPERWEAPON_LABELS.get(ab_name, ab_name)
            def count_getter(s, an=ab_name) -> Any:
                c = 0
                for comp in s.get_all_components():
                    if comp.has_ability(an):
                        c += 1
                return c
            rows.append(StatDefinition(
                id=f"superweapon_{ab_name.lower()}", label=label,
                getter=count_getter, formatter=lambda v: f"x{int(v)}", unit=" uses"
            ))

    return rows

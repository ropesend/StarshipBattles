"""Protocol definitions for type-safe duck typing replacement.

This package provides @runtime_checkable Protocol classes and TypeGuard
functions to replace hasattr/getattr patterns with proper type checking.

Decomposed from a single 1087-line module in PROJ-309 (Phase 3.4 / 2026-04-27)
to keep each sub-module under the 500-LOC ceiling. The package's `__init__.py`
re-exports every public symbol so `from game.core.protocols import X` continues
to work for the 132 import sites across 80 files.

Sub-module layout:
    common              — _has_attrs, ILocatable, INamed, IOwnable
    registry            — IRegistryProvider
    strategy_entities   — concrete galaxy-map types (stars, planets, fleets, ...)
    strategy_domain     — organisational types (empires, facilities, races, ship instances)
    combat              — combat-side ship/entity protocols
    boundary            — strategy↔simulation seam contracts (PROJ-90)
    ui                  — IScene, ICamera
    persistence         — ISerializable

Usage:
    from game.core.protocols import is_fleet, is_planet, is_scene, IFleet, IScene

    if is_fleet(obj):
        # obj is now typed as IFleet
        print(obj.ships)
    elif is_planet(obj):
        # obj is now typed as IPlanet
        print(obj.name)
    elif is_scene(obj):
        # obj is now typed as IScene
        obj.handle_event(event)
"""

from game.core.protocols.boundary import (
    IPostBattleShip,
    IResourceHolder,
    IResourceReader,
    is_post_battle_ship,
    is_resource_holder,
    is_resource_reader,
)
from game.core.protocols.combat import (
    ICombatant,
    ICombatShip,
    IDamageable,
    is_combat_ship,
    is_combatant,
)
from game.core.protocols.common import (
    ILocatable,
    INamed,
    IOwnable,
    _has_attrs,
)
from game.core.protocols.persistence import ISerializable
from game.core.protocols.registry import IRegistryProvider
from game.core.protocols.strategy_domain import (
    IEmpire,
    IFacility,
    IRaceRegistry,
    IShipInstance,
    is_empire,
    is_facility,
    is_ship_instance,
)
from game.core.protocols.strategy_entities import (
    IAbilitySource,
    IFleet,
    IOrderable,
    IPlanet,
    ISectorEnvironment,
    IStar,
    IStarSystem,
    IStorm,
    IWarpPoint,
    IZoneOccupant,
    is_ability_source,
    is_fleet,
    is_planet,
    is_sector_environment,
    is_star,
    is_star_system,
    is_storm,
    is_warp_point,
    is_zone_occupant,
)
from game.core.protocols.ui import ICamera, IScene, is_camera


__all__ = [
    # Registry
    "IRegistryProvider",
    # Common base mixins
    "ILocatable",
    "INamed",
    "IOwnable",
    # Strategy entities — protocol classes
    "IStarSystem",
    "IStar",
    "IPlanet",
    "IOrderable",
    "IZoneOccupant",
    "IFleet",
    "IWarpPoint",
    "ISectorEnvironment",
    "IStorm",
    "IAbilitySource",
    # Strategy entities — TypeGuards
    "is_star_system",
    "is_star",
    "is_planet",
    "is_fleet",
    "is_warp_point",
    "is_sector_environment",
    "is_storm",
    "is_zone_occupant",
    "is_ability_source",
    # Strategy domain — protocol classes
    "IEmpire",
    "IFacility",
    "IRaceRegistry",
    "IShipInstance",
    # Strategy domain — TypeGuards
    "is_empire",
    "is_facility",
    "is_ship_instance",
    # Combat — protocol classes
    "ICombatant",
    "IDamageable",
    "ICombatShip",
    # Combat — TypeGuards
    "is_combatant",
    "is_combat_ship",
    # UI — protocol classes
    "IScene",
    "ICamera",
    # UI — TypeGuards
    "is_camera",
    # Strategy↔Simulation boundary
    "IResourceReader",
    "IPostBattleShip",
    "IResourceHolder",
    "is_post_battle_ship",
    "is_resource_reader",
    "is_resource_holder",
    # Persistence
    "ISerializable",
    # Private-but-publicly-imported helper
    "_has_attrs",
]

"""StabilizerRegistry — data-driven stabilizer-blocks-superweapon lookup.

Each `StabilizerSpec` declares an ability (e.g. `GeologicStabilizer`), the
scopes across which it protects (planet / sector / system), and the set of
`OrderType`s it blocks. `find_blocking_stabilizer(...)` scans all empires'
colonies for any ACTIVE instance of a stabilizer whose `blocks` set contains
the given order type and returns the first match (or None).

Extensibility contract (per docs/systems/strategy_layer.md):
    Adding a new stabilizer is a single edit to `STABILIZERS`. Authoring a
    new superweapon that an existing stabilizer should block is a single
    edit to that `StabilizerSpec.blocks` tuple. No code changes are needed
    in `SuperweaponOrderProcessor`.

Why this exists (PROJ-277): previously each superweapon handler hand-rolled
its own `_is_*_stabilized` wrapper that named the ability and scopes inline
and called `find_abilities_in_scope` without threading the component
registry. Real facility `design_data` uses `{"id": "stellar_stabilizer"}`
with no inline abilities dict — abilities live in the component registry.
Without a registry the scanner returned nothing and every stabilizer was
silently ineffective.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Tuple, TYPE_CHECKING

from game.strategy.data.order_types import OrderType

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.galaxy import Galaxy
    from game.strategy.data.planet import Planet


@dataclass(frozen=True)
class StabilizerSpec:
    """Declarative spec for a stabilizer ability.

    Attributes:
        ability_name: Registry key of the ability class
            (e.g. ``"GeologicStabilizer"``).
        scopes: Ordered tuple of scopes to scan, from narrow to wide.
            Stops at the first hit.
        blocks: Tuple of `OrderType` values this stabilizer protects against.
    """
    ability_name: str
    scopes: Tuple[str, ...]
    blocks: Tuple[OrderType, ...]


# Authoritative mapping. Order of entries does not matter; order of scopes
# within a spec matters only for logging (first hit wins regardless).
STABILIZERS: Tuple[StabilizerSpec, ...] = (
    StabilizerSpec(
        ability_name="GeologicStabilizer",
        scopes=("planet", "sector", "system"),
        blocks=(OrderType.IMPLODE_PLANET,),
    ),
    StabilizerSpec(
        ability_name="StellarStabilizer",
        scopes=("sector", "system"),
        blocks=(OrderType.STELLERATE_STAR, OrderType.CREATE_DYSON_SPHERE),
    ),
    StabilizerSpec(
        ability_name="WarpFieldStabilizer",
        scopes=("sector", "system"),
        blocks=(OrderType.OPEN_WARP_POINT, OrderType.CLOSE_WARP_POINT),
    ),
)


def find_blocking_stabilizer(
    order_type: OrderType,
    reference_planet: Optional["Planet"],
    galaxy: "Galaxy",
    empires,
    component_registry: Any = None,
) -> Optional[StabilizerSpec]:
    """Return the first active stabilizer spec blocking this order, or None.

    Args:
        order_type: The superweapon order being executed.
        reference_planet: Any planet in the affected system, used for spatial
            scope resolution. For IMPLODE_PLANET this is the target planet
            itself; for system-scope superweapons it is any planet in the
            target system. If None, no block is possible (defensive default).
        galaxy: Galaxy for spatial queries.
        empires: All empires to scan for stabilizers (friend or foe).
        component_registry: `GameRegistries` instance OR the plain components
            dict (``registries.components``). Required — the ability data for
            most facilities lives in the registry, not inline on the design.

    Returns:
        The first matching `StabilizerSpec` with an ACTIVE instance in scope,
        or None if the order is not blocked.
    """
    if reference_planet is None:
        return None

    from game.strategy.services.strategic_ability_scanner import find_abilities_in_scope

    for spec in STABILIZERS:
        if order_type not in spec.blocks:
            continue
        for empire in empires:
            for scope in spec.scopes:
                found = find_abilities_in_scope(
                    spec.ability_name,
                    reference_planet,
                    galaxy,
                    empire,
                    scope,
                    registries=component_registry,
                    require_active=True,
                )
                if found:
                    return spec
    return None

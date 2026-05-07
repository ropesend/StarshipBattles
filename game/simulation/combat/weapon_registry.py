"""PROJ-359: Weapon family registry and dispatch.

Routes `AttackRequest` instances to the registered `WeaponHandler` for the
request's family. Mirrors the shape of `ABILITY_STAT_REGISTRY` (PROJ-273):
one mapping per family, lookup at the dispatch site.

## Family detection
`detect_family(component)` is the single point that owns the legacy
`comp.has_ability(...)` string lookup. Once the migration is complete, this
function is the *only* place those strings appear in dispatch code; family
handlers themselves should consume metadata, not strings.

The PDC role is detected before BEAM because a PDC weapon is a Beam weapon
with the 'pdc' tag — order matters.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional

from game.simulation.combat.attack_contract import (
    AttackRequest,
    AttackResolution,
    UnregisteredWeaponFamilyError,
    WeaponFamily,
    WeaponHandler,
)

if TYPE_CHECKING:
    from game.simulation.components.component import Component


class WeaponRegistry:
    """Process-local registry. Tests reset via `reset()`.

    Keeping this as a class rather than a module-level dict allows tests to
    register fake families without leaking state across tests. The default
    process-wide instance is `WEAPON_REGISTRY`.
    """

    def __init__(self) -> None:
        self._handlers: Dict[WeaponFamily, WeaponHandler] = {}

    def register(self, family: WeaponFamily, handler: WeaponHandler) -> None:
        """Register a handler for a weapon family. Re-registration overwrites
        the previous handler (intentional — supports test fakes and runtime
        replacement)."""
        self._handlers[family] = handler

    def unregister(self, family: WeaponFamily) -> None:
        self._handlers.pop(family, None)

    def reset(self) -> None:
        self._handlers.clear()

    def has(self, family: WeaponFamily) -> bool:
        return family in self._handlers

    def dispatch(self, request: AttackRequest) -> AttackResolution:
        """Route a request to its family handler.

        Raises `UnregisteredWeaponFamilyError` if no handler is registered for
        `request.family`. Don't swallow this — it indicates a missing
        registration, not a runtime condition.
        """
        handler = self._handlers.get(request.family)
        if handler is None:
            raise UnregisteredWeaponFamilyError(
                f"No handler registered for weapon family {request.family.name}"
            )
        return handler.fire(request)


# Process-wide singleton. Family modules register on import; the firing
# system imports those modules to trigger registration.
WEAPON_REGISTRY = WeaponRegistry()


def detect_family(component: "Component") -> Optional[WeaponFamily]:
    """Resolve a weapon component to its family.

    This is the single point that owns the legacy string-class lookup.
    PDC is checked first because a PDC weapon has both `has_pdc_ability()`
    (tag-based) AND `has_ability('BeamWeaponAbility')`; without the
    PDC-first check the dispatch would route PDC weapons through the Beam
    family.
    """
    if component.has_pdc_ability():
        return WeaponFamily.PDC
    if component.has_ability('BeamWeaponAbility'):
        return WeaponFamily.BEAM
    if component.has_ability('SeekerWeaponAbility'):
        return WeaponFamily.SEEKER
    if component.has_ability('ProjectileWeaponAbility'):
        return WeaponFamily.PROJECTILE
    return None

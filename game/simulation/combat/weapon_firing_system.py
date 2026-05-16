"""
WeaponFiringSystem - Extracted weapon firing logic from ShipCombatEngine.

This class handles all weapon firing operations:
- Processing weapon components for firing
- Family-routed weapon dispatch (Beam, PDC, Projectile, Seeker via
  WEAPON_REGISTRY)

Part of PROJ-44 Phase 5: ShipCombatEngine Decomposition. Refactored under
PROJ-359 to delegate per-family construction to WeaponHandler instances
(see game/simulation/combat/families/).

PROJ-FMS-C audit Fix 1: the legacy ``VehicleLaunch`` hangar auto-launch
path was removed; tactical fighter launches now go through
:meth:`BattleEngine.launch_fighters_in_battle` driven by
:class:`game.ai.carrier_controller.CarrierAIController` or a player UI
action.
"""
from typing import TYPE_CHECKING, List, Optional, Any

from game.core.constants import AttackType, CombatConstants

# PROJ-359 Phase 3: importing `families` triggers WEAPON_REGISTRY registrations
from game.simulation.combat import families  # noqa: F401
from game.simulation.combat.attack_contract import (
    FAMILY_METADATA,
    AttackRequest,
    BeamResolution,
    ProjectileResolution,
)
from game.simulation.combat.weapon_registry import WEAPON_REGISTRY, detect_family

if TYPE_CHECKING:
    from game.core.event_logging import EventBus
    from game.simulation.entities.ship import Ship
    from game.simulation.components.component import Component
    from game.simulation.combat.targeting_system import TargetingSystem


class WeaponFiringSystem:
    """
    Handles all weapon firing logic for combat.

    Extracted from ShipCombatEngine to focus on single responsibility:
    firing weapons and creating attack objects.
    """

    def __init__(
        self,
        targeting_system: 'TargetingSystem',
        event_bus: 'EventBus | None' = None,
    ):
        """
        Initialize weapon firing system.

        Args:
            targeting_system: The targeting system to use for aim calculations
            event_bus: Optional session ``EventBus`` (PROJ-405).  When set, it
                is forwarded on every ``AttackRequest`` so weapon-family
                handlers can wire ``Projectile.event_logger`` to
                ``bus.log_event``.  ``None`` means tests/replay paths that
                don't need lifecycle telemetry.
        """
        self._targeting = targeting_system
        self._event_bus: "EventBus | None" = event_bus

    def set_event_bus(self, event_bus: 'EventBus | None') -> None:
        """Replace the session ``EventBus`` (PROJ-405).

        ``ShipCombatEngine`` shares one ``WeaponFiringSystem`` instance across
        all ships in the process; ``BattleEngine`` calls this in ``start()``
        so the running battle's session bus is the one that gets threaded
        into newly-spawned projectiles.
        """
        self._event_bus = event_bus

    def fire_weapons(
        self,
        ship: 'Ship',
        context: Optional[dict] = None
    ) -> List[Any]:
        """
        Fire all ready weapons at available targets.

        Iterates through all weapon components, checks firing conditions,
        and creates projectiles or beam attacks as appropriate.

        Args:
            ship: The ship firing weapons
            context: Optional context dict with projectiles list for PDC targeting

        Returns:
            List of attack objects (Projectiles or beam attack dicts)
        """
        attacks = []

        if not ship.is_alive or ship.is_derelict:
            return attacks

        for layer_type, comp in ship.iter_components():
            # PROJ-FMS-C audit Fix 1: the legacy ``VehicleLaunch`` weapon-
            # firing auto-launch path has been removed. Tactical fighter
            # launches now go through :meth:`BattleEngine.launch_fighters_in_battle`
            # driven by :class:`CarrierAIController` (or a player UI action),
            # not as a side-effect of the weapon-firing loop. The new path
            # spawns design-instance fighters with full components / weapons /
            # HP rather than class-string shells.

            # Handle Weapons (is_operational checks both is_active AND
            # requirement satisfaction like RequiresCommandAndControl)
            if comp.has_ability('WeaponAbility') and comp.is_operational:
                attack_result = self._process_weapon_fire(ship, comp, context)
                if attack_result:
                    if isinstance(attack_result, list):
                        attacks.extend(attack_result)
                    else:
                        attacks.append(attack_result)

        return attacks

    def _process_weapon_fire(
        self,
        ship: 'Ship',
        comp: 'Component',
        context: Optional[dict] = None
    ) -> Optional[List[Any]]:
        """
        Process firing for a weapon component.

        Validates target, checks firing conditions, and creates attack.

        Args:
            ship: The ship firing
            comp: Weapon component
            context: Optional context dict

        Returns:
            List of attacks or None
        """
        weapon_ab = comp.get_ability('WeaponAbility')

        if not comp.can_afford_activation():
            return None

        if not weapon_ab.can_fire():
            return None

        # Find valid target (pass context for PDC missile targeting)
        target = self._find_valid_target(ship, comp, weapon_ab, context)
        if not target:
            return None

        # Fire the weapon
        if not weapon_ab.fire(target):
            return None

        # Update stats (both fields initialized in __init__)
        ship.total_shots_fired += 1
        comp.shots_fired += 1

        # Create attack based on weapon type
        return self._create_attack(ship, comp, weapon_ab, target)

    def _find_valid_target(
        self,
        ship: 'Ship',
        comp: 'Component',
        weapon_ab: Any,
        context: Optional[dict] = None
    ) -> Optional[Any]:
        """
        Find a valid target for the weapon.

        For PDC weapons, includes enemy missiles from context as candidates.

        Args:
            ship: The ship targeting
            comp: Weapon component
            weapon_ab: Weapon ability instance
            context: Optional context dict with projectiles list

        Returns:
            Valid target or None
        """
        # Build secondary targets list
        secondary_targets = []
        if ship.max_targets > CombatConstants.DEFAULT_MAX_TARGETS:
            secondary_targets = list(ship.secondary_targets)

        # PROJ-359 Phase 3.4: Family-metadata-driven missile injection.
        # Previously: `if comp.has_pdc_ability() and context:` — string lookup.
        # Now: family metadata declares whether this family consumes the
        # PDC missile context. Adding a new family with this behavior is a
        # FAMILY_METADATA edit, not a firing-system edit.
        family = detect_family(comp)
        meta = FAMILY_METADATA.get(family) if family else None
        if meta is not None and meta.consumes_pdc_missile_context and context:
            projectiles = context.get('projectiles', [])
            for p in projectiles:
                if p.is_alive and p.team_id != ship.team_id and p.type == AttackType.MISSILE:
                    secondary_targets.append(p)

        return self._targeting.find_valid_target(
            ship,
            ship.current_target,
            secondary_targets,
            comp,
            weapon_ab
        )

    def _create_attack(
        self,
        ship: 'Ship',
        comp: 'Component',
        weapon_ab: Any,
        target: Any
    ) -> List[Any]:
        """Create attack object(s) for a successful weapon fire.

        PROJ-359 Phase 4: thin family-dispatcher. The four legacy string
        branches (`comp.has_ability('BeamWeaponAbility')` etc.) collapsed into
        a single `detect_family` call. Adding a new weapon family does not
        require any change to this method.
        """
        family = detect_family(comp)
        if family is None:
            return []

        aim_pos, aim_vec = self._targeting.calculate_firing_solution(ship, comp, target)
        request = AttackRequest(
            source=ship,
            component=comp,
            weapon_ability=weapon_ab,
            target=target,
            aim_pos=aim_pos,
            aim_vec=aim_vec,
            family=family,
            # PROJ-405: forward the session EventBus so seeker/projectile
            # handlers can wire `Projectile.event_logger=bus.log_event`.
            event_bus=self._event_bus,
        )
        resolution = WEAPON_REGISTRY.dispatch(request)

        if isinstance(resolution, BeamResolution):
            return [resolution]
        if isinstance(resolution, ProjectileResolution):
            return [resolution.projectile]
        return []  # NoAttack — handler chose not to fire

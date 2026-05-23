"""PlanetModifierEffectEngine — Apply/revert instant planet modifier effects.

Handles the gravity modifier and radiation shield effects that activate
instantly (like stabilizers) rather than gradually (like atmosphere/water).
Runs once per tick after ComponentActivationEngine to detect state transitions
and apply or revert planet property changes.

Gravity: When ACTIVE, overrides surface_gravity with gravity_target. Stores
    original value in gravity_original. Reverts when INACTIVE or facility destroyed.

Radiation: When ACTIVE, sets radiation_shielding to radiation_shielding_target.
    Reverts to 0.0 when INACTIVE or facility destroyed.
"""
import logging
from typing import List, TYPE_CHECKING

from game.strategy.data.component_activation_state import (
    ComponentActivationState, ActivationPhase,
)

if TYPE_CHECKING:
    from game.core.protocols.strategy_mutators import IPlanetMutator
    from game.strategy.data.empire import Empire

logger = logging.getLogger(__name__)


class PlanetModifierEffectEngine:
    """Engine for applying/reverting instant planet modifier effects."""

    def __init__(self, registries=None, planet_mutator=None):
        self._registries = registries
        self._planet_mutator = planet_mutator

    def _get_planet_mutator(self) -> "IPlanetMutator":
        if self._planet_mutator is None:
            from game.strategy.services.planet_write_service import (
                PlanetWriteService,
            )
            self._planet_mutator = PlanetWriteService()
        return self._planet_mutator

    def process_modifier_effects_tick(self, tick: int, empires: List) -> None:
        """Process modifier effects for all empires.

        Called once per tick after ComponentActivationEngine.
        """
        for empire in empires:
            for colony in empire.colonies:
                self._process_planet(colony)

    def _process_planet(self, planet) -> None:
        """Process modifier effects for a single planet."""
        self._process_gravity(planet)
        self._process_radiation(planet)

    def _process_gravity(self, planet) -> None:
        """Apply or revert gravity modifier effect."""
        gravity_target = getattr(planet, 'gravity_target', None)
        gravity_original = getattr(planet, 'gravity_original', None)
        # Guard against MagicMock objects in tests
        if not isinstance(gravity_target, (int, float, type(None))):
            return
        if not isinstance(gravity_original, (int, float, type(None))):
            return

        # Check if any active GravityModifier exists
        has_active = self._has_active_ability(planet, 'GravityModifier')

        if has_active and gravity_target is not None:
            # Apply: store original if not already stored, then set target
            if gravity_original is None:
                planet.gravity_original = planet.surface_gravity
            planet.surface_gravity = gravity_target
        elif gravity_original is not None and not has_active:
            # Revert: no active modifier but original is stored
            planet.surface_gravity = gravity_original
            planet.gravity_original = None

    def _process_radiation(self, planet) -> None:
        """Apply or revert radiation shield effect."""
        shielding_target = getattr(planet, 'radiation_shielding_target', None)

        # Check if any active RadiationShield exists
        has_active = self._has_active_ability(planet, 'RadiationShield')

        # PROJ-370 Phase 3: route radiation_shielding writes through IPlanetMutator.
        if has_active and shielding_target is not None:
            self._get_planet_mutator().set_radiation_shielding(
                planet, shielding_target,
            )
        elif not has_active:
            # Revert: no active shield means no artificial shielding
            current = getattr(planet, 'radiation_shielding', 0.0)
            if isinstance(current, (int, float)) and current > 0:
                self._get_planet_mutator().set_radiation_shielding(planet, 0.0)

    def _has_active_ability(self, planet, ability_name: str) -> bool:
        """Check if any facility has an active component with the given ability."""
        for facility in getattr(planet, 'facilities', []):
            if not getattr(facility, 'is_operational', True):
                continue
            for _key, state in getattr(facility, 'component_states', {}).items():
                if isinstance(state, dict):
                    state = ComponentActivationState.from_dict(state)
                if (state.ability_name == ability_name
                        and state.phase == ActivationPhase.ACTIVE):
                    return True
        return False

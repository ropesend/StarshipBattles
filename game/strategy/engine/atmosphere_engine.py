"""AtmosphereEngine — Per-turn atmosphere modification toward target composition.

Scans colonies for AtmosphereModifier abilities and gradually changes the
planet's atmosphere toward the target gas composition. The rate of change
is based on the mass of atmosphere that can be processed per turn, which
translates to different pressure changes depending on planet properties.

Atmosphere mass formula: mass_kg = pressure_Pa * surface_area_m2 / gravity_ms2
"""
import logging
from typing import Dict, List, TYPE_CHECKING

from game.core.patterns.layer_iterator import iter_components

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire

logger = logging.getLogger(__name__)


class AtmosphereEngine:
    """Engine for processing per-turn atmosphere modification."""

    def process_atmosphere(self, empires: List) -> None:
        """Process atmosphere modification for all empires.

        Called once per turn (not per tick) by TurnEngine.

        Args:
            empires: List of Empire objects to process.
        """
        for empire in empires:
            for colony in empire.colonies:
                self._process_colony(colony)

    def _process_colony(self, colony) -> None:
        """Process atmosphere modification for a single colony."""
        target = getattr(colony, 'atmosphere_target', {})
        if not target or not isinstance(target, dict):
            return

        atmosphere = getattr(colony, 'atmosphere', {})
        if not isinstance(atmosphere, dict):
            return

        # Sum modification rate from all operational facilities
        total_rate_kg = 0.0
        for facility in getattr(colony, 'facilities', []):
            if not getattr(facility, 'is_operational', True):
                continue
            for comp in iter_components(facility.design_data):
                am_data = self._extract_atmo_modifier(comp)
                if am_data is None:
                    continue
                if isinstance(am_data, list):
                    for entry in am_data:
                        total_rate_kg += entry.get('modification_rate', 0.0)
                else:
                    total_rate_kg += am_data.get('modification_rate', 0.0)

        if total_rate_kg <= 0:
            return

        # Get planet physical properties for Pa-to-mass conversion
        surface_area = getattr(colony, 'surface_area', 0.0)
        gravity = getattr(colony, 'surface_gravity', 0.0)

        if surface_area <= 0 or gravity <= 0:
            return

        # Conversion factor: 1 Pa of gas = (surface_area / gravity) kg
        pa_per_kg = gravity / surface_area  # Pa per kg of atmosphere
        # So total_rate_kg can change total_rate_kg * pa_per_kg Pascals

        # Calculate deltas needed for each gas
        all_gases = set(list(target.keys()) + list(atmosphere.keys()))
        deltas = {}  # gas -> Pa delta needed
        total_delta_mass = 0.0

        for gas in all_gases:
            current_pa = atmosphere.get(gas, 0.0)
            target_pa = target.get(gas, current_pa)  # If not in target, keep current
            delta_pa = target_pa - current_pa

            if abs(delta_pa) < 0.001:
                continue

            # Convert Pa delta to mass delta
            delta_mass_kg = abs(delta_pa) * surface_area / gravity
            deltas[gas] = (delta_pa, delta_mass_kg)
            total_delta_mass += delta_mass_kg

        if total_delta_mass <= 0 or not deltas:
            return

        # Distribute available modification rate proportionally
        for gas, (delta_pa, delta_mass_kg) in deltas.items():
            # Fraction of total work allocated to this gas
            fraction = delta_mass_kg / total_delta_mass
            allocated_mass_kg = total_rate_kg * fraction

            # Convert allocated mass back to Pa
            allocated_pa = allocated_mass_kg * pa_per_kg

            # Don't overshoot
            if abs(delta_pa) < allocated_pa:
                actual_pa_change = delta_pa
            else:
                actual_pa_change = allocated_pa if delta_pa > 0 else -allocated_pa

            # Apply
            current_pa = atmosphere.get(gas, 0.0)
            new_pa = max(0.0, current_pa + actual_pa_change)
            atmosphere[gas] = new_pa

        # Update planet atmosphere reference (in case it was empty)
        colony.atmosphere = atmosphere

        # Update surface_pressure as sum of all partial pressures
        total_pressure = sum(atmosphere.values())
        colony.surface_pressure = total_pressure

    def _extract_atmo_modifier(self, comp):
        """Extract AtmosphereModifier ability data from a component entry."""
        from game.strategy.services.component_inspector import extract_abilities_from_component
        abilities = extract_abilities_from_component(comp)
        data = abilities.get('AtmosphereModifier')
        if isinstance(data, (dict, list)):
            return data
        return None

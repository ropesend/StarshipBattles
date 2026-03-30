"""ShipStatQuerier - Extracted ship stat aggregation logic.

PROJ-88 Phase 2: Moved from Ship class to reduce god class complexity.
Ship retains facade methods that delegate to this querier.
"""

from typing import Any, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship

__all__ = ['ShipStatQuerier']


class ShipStatQuerier:
    """
    Handles stat aggregation queries for a Ship.

    Extracted from Ship to reduce god class complexity.
    Ship retains facade methods that delegate here.

    Args:
        ship: The Ship instance to query stats from.
    """

    def __init__(self, ship: 'Ship') -> None:
        """Initialize querier with ship reference."""
        self._ship = ship

    def get_ability_total(self, ability_name: str) -> Union[float, int, bool]:
        """
        Get total value of a specific ability across all components.

        Uses ShipStatsCalculator.calculate_ability_totals() which applies
        stack_group rules (MAX within group, MULTIPLY across groups).

        Args:
            ability_name: The ability name to aggregate (e.g., 'ToHitAttackModifier').

        Returns:
            Total ability value, or 0 if ability not present.
        """
        all_components = self._ship.get_all_components()

        if not self._ship.stats_calculator:
            # Lazy create stats calculator if needed
            from game.simulation.entities.ship_stats import ShipStatsCalculator
            self._ship.stats_calculator = ShipStatsCalculator(
                self._ship._registries.vehicle_classes
            )

        totals = self._ship.stats_calculator.calculate_ability_totals(all_components)
        return totals.get(ability_name, 0)

    def get_total_ability_value(
        self,
        ability_name: str,
        operational_only: bool = True
    ) -> float:
        """
        Sum values from all matching abilities across all components.

        Uses polymorphic get_primary_value() interface for extensibility.

        Args:
            ability_name: Name of ability class to sum (e.g., 'CombatPropulsion').
            operational_only: If True, only count abilities from operational components.

        Returns:
            Sum of primary value attribute from all matching abilities.
        """
        total = 0.0
        for comp in self._ship.get_all_components():
            if operational_only and not comp.is_operational:
                continue
            for ab in comp.get_abilities(ability_name):
                total += ab.get_primary_value()
        return total

    def get_total_sensor_score(self) -> float:
        """
        Calculate total Targeting Score from all active sensors.

        Uses stack_group rules:
        - Same stack_group: MAX (redundancy)
        - Different stack_groups: SUM (stacking)

        Returns:
            Total sensor/targeting score as float.
        """
        result = self.get_ability_total('ToHitAttackModifier')
        return float(result) if isinstance(result, (int, float)) else 0.0

    def get_total_ecm_score(self) -> float:
        """
        Calculate total Evasion/Defense Score from all active ECM/Electronics.

        Uses stack_group rules:
        - Same stack_group: MAX (redundancy)
        - Different stack_groups: SUM (stacking)

        Returns:
            Total ECM/defense score as float.
        """
        result = self.get_ability_total('ToHitDefenseModifier')
        return float(result) if isinstance(result, (int, float)) else 0.0

    @property
    def max_weapon_range(self) -> float:
        """
        Calculate maximum range of all equipped weapons.

        For SeekerWeaponAbility, calculates range from projectile_speed * endurance
        if range is not explicitly set.

        Returns:
            Maximum weapon range, or 0.0 if no weapons equipped.
        """
        # INTENTIONAL LATE IMPORT: Avoid circular dependency with abilities module
        # See docs/ARCHITECTURE.md "Intentional Late Imports" section
        from game.simulation.components.abilities import SeekerWeaponAbility, WeaponAbility

        max_rng = 0.0
        for comp in self._ship.get_all_components():
            for ab in comp.ability_instances:
                # Polymorphic check using isinstance
                if not isinstance(ab, WeaponAbility):
                    continue

                # WeaponAbility.range is always initialized
                rng = ab.range
                # For SeekerWeapons, calculate range from endurance if not set
                # SeekerWeaponAbility always has projectile_speed and endurance
                if isinstance(ab, SeekerWeaponAbility):
                    if rng <= 0:
                        rng = ab.projectile_speed * ab.endurance

                if rng > max_rng:
                    max_rng = rng

        return max_rng if max_rng > 0 else 0.0

    # PROJ-225: Removed redundant cached_summary property (DUP-SIM-007).
    # Use Ship.cached_summary instead.

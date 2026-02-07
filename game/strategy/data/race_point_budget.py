"""
Race Point Budget - Point-buy system for race configuration.

PROJ-66 Phase 5: Implements cost calculations for aptitudes and environmental
tolerances. Uses linear costs for aptitudes and exponential (2^n) costs for
tolerances to encourage specialization.
"""
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig


class RacePointBudget:
    """
    Calculates and tracks point costs for race configuration.

    Aptitude costs are linear: each point above/below base 5 costs/refunds 1 point.
    Tolerance costs are exponential: each step costs 2^(step-1), so 1, 2, 4, 8, 16...

    This makes broad environmental tolerance extremely expensive, forcing races
    to specialize in their preferred environments.
    """

    # Default budget total
    DEFAULT_BUDGET = 100

    # Base aptitude value (costs nothing at this level)
    APTITUDE_BASE = 5

    # Tolerance step sizes for cost calculation
    GRAVITY_STEP = 0.1      # per 0.1g tolerance
    TEMPERATURE_STEP = 10   # per 10K tolerance
    WATER_STEP = 0.1        # per 0.1 (10%) tolerance
    RADIATION_STEP = 10     # per 10 radiation tolerance
    ATMOSPHERE_STEP = 10    # per 10 atmosphere preference

    def __init__(self, total_budget: int = DEFAULT_BUDGET):
        """
        Initialize point budget calculator.

        Args:
            total_budget: Total points available for customization
        """
        self.total_budget = total_budget

    def calculate_aptitude_cost(self, race_config: 'RaceConfig') -> int:
        """
        Calculate total cost of aptitude selections.

        Each point above base costs 1 point.
        Each point below base refunds 1 point (negative cost).

        Args:
            race_config: Race configuration to calculate costs for

        Returns:
            Net aptitude cost (can be negative if stats are lowered)
        """
        total = 0
        aptitudes = [
            race_config.aptitude_strength,
            race_config.aptitude_intelligence,
            race_config.aptitude_constitution,
            race_config.aptitude_dexterity,
            race_config.aptitude_tolerance_other_species,
            race_config.aptitude_cooperation,
            race_config.aptitude_happiness,
            race_config.aptitude_population_growth,
            race_config.aptitude_conflict_tolerance,
        ]
        for value in aptitudes:
            total += (value - self.APTITUDE_BASE)
        return total

    def calculate_tolerance_cost(self, race_config: 'RaceConfig') -> int:
        """
        Calculate total cost of environmental tolerance selections.

        Uses exponential 2^n cost: first step costs 1, second costs 2,
        third costs 4, etc. Total for n steps = 2^n - 1.

        Args:
            race_config: Race configuration to calculate costs for

        Returns:
            Total tolerance cost (always non-negative)
        """
        total = 0

        # Gravity tolerance
        gravity_steps = int(race_config.gravity_tolerance / self.GRAVITY_STEP + 0.5)
        total += self._exponential_cost(gravity_steps)

        # Temperature tolerance
        temp_steps = int(race_config.temperature_tolerance / self.TEMPERATURE_STEP + 0.5)
        total += self._exponential_cost(temp_steps)

        # Water tolerance
        water_steps = int(race_config.water_tolerance / self.WATER_STEP + 0.5)
        total += self._exponential_cost(water_steps)

        # Radiation tolerance (absolute value - both sensitive and resistant cost)
        radiation_steps = int(abs(race_config.radiation_tolerance) / self.RADIATION_STEP + 0.5)
        total += self._exponential_cost(radiation_steps)

        # Atmosphere preferences (absolute value for each gas)
        for gas, value in race_config.atmosphere_preferences.items():
            atmo_steps = int(abs(value) / self.ATMOSPHERE_STEP + 0.5)
            total += self._exponential_cost(atmo_steps)

        return total

    def _exponential_cost(self, steps: int) -> int:
        """
        Calculate exponential cost for a number of steps.

        Cost = sum of 2^i for i in 0..steps-1 = 2^steps - 1

        Args:
            steps: Number of steps of tolerance

        Returns:
            Total cost for that many steps
        """
        if steps <= 0:
            return 0
        return (1 << steps) - 1  # 2^steps - 1

    def calculate_total_cost(self, race_config: 'RaceConfig') -> int:
        """
        Calculate total cost of all selections.

        Args:
            race_config: Race configuration to calculate costs for

        Returns:
            Total cost (aptitudes + tolerances)
        """
        return self.calculate_aptitude_cost(race_config) + self.calculate_tolerance_cost(race_config)

    def get_remaining_points(self, race_config: 'RaceConfig') -> int:
        """
        Calculate remaining points in budget.

        Args:
            race_config: Race configuration to calculate for

        Returns:
            Remaining points (can be negative if over budget)
        """
        return self.total_budget - self.calculate_total_cost(race_config)

    def is_within_budget(self, race_config: 'RaceConfig') -> bool:
        """
        Check if configuration is within budget.

        Args:
            race_config: Race configuration to check

        Returns:
            True if remaining points >= 0
        """
        return self.get_remaining_points(race_config) >= 0

    def get_aptitude_breakdown(self, race_config: 'RaceConfig') -> Dict[str, int]:
        """
        Get per-aptitude cost breakdown.

        Args:
            race_config: Race configuration to analyze

        Returns:
            Dictionary mapping aptitude name to its cost
        """
        return {
            "strength": race_config.aptitude_strength - self.APTITUDE_BASE,
            "intelligence": race_config.aptitude_intelligence - self.APTITUDE_BASE,
            "constitution": race_config.aptitude_constitution - self.APTITUDE_BASE,
            "dexterity": race_config.aptitude_dexterity - self.APTITUDE_BASE,
            "tolerance_other_species": race_config.aptitude_tolerance_other_species - self.APTITUDE_BASE,
            "cooperation": race_config.aptitude_cooperation - self.APTITUDE_BASE,
            "happiness": race_config.aptitude_happiness - self.APTITUDE_BASE,
            "population_growth": race_config.aptitude_population_growth - self.APTITUDE_BASE,
            "conflict_tolerance": race_config.aptitude_conflict_tolerance - self.APTITUDE_BASE,
        }

    def get_tolerance_breakdown(self, race_config: 'RaceConfig') -> Dict[str, int]:
        """
        Get per-tolerance cost breakdown.

        Args:
            race_config: Race configuration to analyze

        Returns:
            Dictionary mapping tolerance name to its cost
        """
        breakdown = {}

        # Gravity
        gravity_steps = int(race_config.gravity_tolerance / self.GRAVITY_STEP + 0.5)
        breakdown["gravity"] = self._exponential_cost(gravity_steps)

        # Temperature
        temp_steps = int(race_config.temperature_tolerance / self.TEMPERATURE_STEP + 0.5)
        breakdown["temperature"] = self._exponential_cost(temp_steps)

        # Water
        water_steps = int(race_config.water_tolerance / self.WATER_STEP + 0.5)
        breakdown["water"] = self._exponential_cost(water_steps)

        # Radiation
        radiation_steps = int(abs(race_config.radiation_tolerance) / self.RADIATION_STEP + 0.5)
        breakdown["radiation"] = self._exponential_cost(radiation_steps)

        # Atmosphere (sum all gases)
        atmo_total = 0
        for gas, value in race_config.atmosphere_preferences.items():
            atmo_steps = int(abs(value) / self.ATMOSPHERE_STEP + 0.5)
            atmo_total += self._exponential_cost(atmo_steps)
        breakdown["atmosphere"] = atmo_total

        return breakdown

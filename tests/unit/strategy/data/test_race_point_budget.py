"""
Tests for RacePointBudget - Point-buy budget system for race configuration.

PROJ-66 Phase 5: Tests for aptitude and tolerance cost calculations.
"""
import pytest

from game.strategy.data.race_config import RaceConfig
from game.strategy.data.race_point_budget import RacePointBudget


class TestRacePointBudget:
    """Test RacePointBudget class."""

    @pytest.fixture
    def budget(self):
        """Create default point budget."""
        return RacePointBudget()

    @pytest.fixture
    def default_config(self):
        """Create default race config (all aptitudes at 50, minimal tolerance)."""
        return RaceConfig()

    # === Aptitude Cost Tests ===

    def test_default_aptitudes_cost_zero(self, budget, default_config):
        """All aptitudes at base (50) should cost 0 points."""
        cost = budget.calculate_aptitude_cost(default_config)
        assert cost == 0

    def test_aptitude_cost_one_above_base(self, budget, default_config):
        """One aptitude at 51 (1 above base) should cost 1 point."""
        default_config.aptitude_strength = 51
        cost = budget.calculate_aptitude_cost(default_config)
        assert cost == 1

    def test_aptitude_cost_one_below_base(self, budget, default_config):
        """One aptitude at 49 (1 below base) should REFUND 1 point (negative cost)."""
        default_config.aptitude_strength = 49
        cost = budget.calculate_aptitude_cost(default_config)
        assert cost == -1

    def test_aptitude_cost_multiple_stats_above(self, budget, default_config):
        """Three stats at 53 (3 above base each) should cost 9 points."""
        default_config.aptitude_strength = 53
        default_config.aptitude_intelligence = 53
        default_config.aptitude_dexterity = 53
        cost = budget.calculate_aptitude_cost(default_config)
        assert cost == 9  # 3 + 3 + 3

    def test_aptitude_cost_mixed_above_and_below(self, budget, default_config):
        """Stats above and below base should net out."""
        default_config.aptitude_strength = 53  # +3
        default_config.aptitude_intelligence = 47  # -3
        cost = budget.calculate_aptitude_cost(default_config)
        assert cost == 0  # Nets to 0

    def test_aptitude_cost_max_single_stat(self, budget, default_config):
        """One stat at max (100) should cost 440 points (exponential above 50)."""
        default_config.aptitude_strength = 100
        cost = budget.calculate_aptitude_cost(default_config)
        assert cost == 440

    def test_aptitude_cost_min_single_stat(self, budget, default_config):
        """One stat at min (1) should refund 49 points."""
        default_config.aptitude_strength = 1
        cost = budget.calculate_aptitude_cost(default_config)
        assert cost == -49

    # === Tolerance Cost Tests ===

    def test_tolerance_cost_zero_tolerance(self, budget, default_config):
        """All tolerances at 0 should cost 0 points."""
        default_config.gravity_tolerance = 0.0
        default_config.temperature_tolerance = 0.0
        default_config.water_tolerance = 0.0
        default_config.radiation_tolerance = 0.0
        for gas in default_config.atmosphere_preferences:
            default_config.atmosphere_preferences[gas] = 0.0
        cost = budget.calculate_tolerance_cost(default_config)
        assert cost == 0

    def test_tolerance_cost_one_step_gravity(self, budget, default_config):
        """Gravity tolerance of 0.1 (1 step) should cost 1 point."""
        default_config.gravity_tolerance = 0.1
        default_config.temperature_tolerance = 0.0
        default_config.water_tolerance = 0.0
        default_config.radiation_tolerance = 0.0
        for gas in default_config.atmosphere_preferences:
            default_config.atmosphere_preferences[gas] = 0.0
        cost = budget.calculate_tolerance_cost(default_config)
        assert cost == 1

    def test_tolerance_cost_two_steps_gravity(self, budget, default_config):
        """Gravity tolerance of 0.2 (2 steps) should cost 1+2=3 points."""
        default_config.gravity_tolerance = 0.2
        default_config.temperature_tolerance = 0.0
        default_config.water_tolerance = 0.0
        default_config.radiation_tolerance = 0.0
        for gas in default_config.atmosphere_preferences:
            default_config.atmosphere_preferences[gas] = 0.0
        cost = budget.calculate_tolerance_cost(default_config)
        assert cost == 3  # 1 + 2

    def test_tolerance_cost_three_steps_gravity(self, budget, default_config):
        """Gravity tolerance of 0.3 (3 steps) should cost 1+2+4=7 points."""
        default_config.gravity_tolerance = 0.3
        default_config.temperature_tolerance = 0.0
        default_config.water_tolerance = 0.0
        default_config.radiation_tolerance = 0.0
        for gas in default_config.atmosphere_preferences:
            default_config.atmosphere_preferences[gas] = 0.0
        cost = budget.calculate_tolerance_cost(default_config)
        assert cost == 7  # 1 + 2 + 4

    def test_tolerance_cost_exponential_growth(self, budget, default_config):
        """Verify 2^n pattern: steps 1-5 should cost 1, 3, 7, 15, 31."""
        default_config.temperature_tolerance = 0.0
        default_config.water_tolerance = 0.0
        default_config.radiation_tolerance = 0.0
        for gas in default_config.atmosphere_preferences:
            default_config.atmosphere_preferences[gas] = 0.0

        # Test progressive costs
        expected_costs = [
            (0.1, 1),    # 2^0 = 1
            (0.2, 3),    # 1 + 2
            (0.3, 7),    # 1 + 2 + 4
            (0.4, 15),   # 1 + 2 + 4 + 8
            (0.5, 31),   # 1 + 2 + 4 + 8 + 16
        ]
        for tolerance, expected in expected_costs:
            default_config.gravity_tolerance = tolerance
            cost = budget.calculate_tolerance_cost(default_config)
            assert cost == expected, f"Tolerance {tolerance} should cost {expected}, got {cost}"

    def test_tolerance_cost_temperature(self, budget, default_config):
        """Temperature tolerance of 20K (2 steps at 10K/step) should cost 3 points."""
        default_config.gravity_tolerance = 0.0
        default_config.temperature_tolerance = 20.0
        default_config.water_tolerance = 0.0
        default_config.radiation_tolerance = 0.0
        for gas in default_config.atmosphere_preferences:
            default_config.atmosphere_preferences[gas] = 0.0
        cost = budget.calculate_tolerance_cost(default_config)
        assert cost == 3  # 1 + 2

    def test_tolerance_cost_water(self, budget, default_config):
        """Water tolerance of 0.2 (2 steps at 0.1/step) should cost 3 points."""
        default_config.gravity_tolerance = 0.0
        default_config.temperature_tolerance = 0.0
        default_config.water_tolerance = 0.2
        default_config.radiation_tolerance = 0.0
        for gas in default_config.atmosphere_preferences:
            default_config.atmosphere_preferences[gas] = 0.0
        cost = budget.calculate_tolerance_cost(default_config)
        assert cost == 3  # 1 + 2

    def test_tolerance_cost_radiation_positive(self, budget, default_config):
        """Radiation tolerance of +20 (2 steps at 10/step) should cost 3 points."""
        default_config.gravity_tolerance = 0.0
        default_config.temperature_tolerance = 0.0
        default_config.water_tolerance = 0.0
        default_config.radiation_tolerance = 20.0
        for gas in default_config.atmosphere_preferences:
            default_config.atmosphere_preferences[gas] = 0.0
        cost = budget.calculate_tolerance_cost(default_config)
        assert cost == 3

    def test_tolerance_cost_radiation_negative(self, budget, default_config):
        """Radiation tolerance of -20 (sensitive) should also cost points."""
        default_config.gravity_tolerance = 0.0
        default_config.temperature_tolerance = 0.0
        default_config.water_tolerance = 0.0
        default_config.radiation_tolerance = -20.0
        for gas in default_config.atmosphere_preferences:
            default_config.atmosphere_preferences[gas] = 0.0
        cost = budget.calculate_tolerance_cost(default_config)
        assert cost == 3  # abs(-20) = 20, 2 steps

    def test_tolerance_cost_atmosphere(self, budget, default_config):
        """Atmosphere preference of +20 (2 steps) should cost 3 points."""
        default_config.gravity_tolerance = 0.0
        default_config.temperature_tolerance = 0.0
        default_config.water_tolerance = 0.0
        default_config.radiation_tolerance = 0.0
        for gas in default_config.atmosphere_preferences:
            default_config.atmosphere_preferences[gas] = 0.0
        default_config.atmosphere_preferences["Oxygen"] = 20.0
        cost = budget.calculate_tolerance_cost(default_config)
        assert cost == 3

    # === Total Cost Tests ===

    def test_total_cost_combines_aptitudes_and_tolerance(self, budget, default_config):
        """Total cost should sum aptitude and tolerance costs."""
        # Aptitude: strength 53 = +3
        default_config.aptitude_strength = 53

        # Tolerance: gravity 0.2 = 3 points
        default_config.gravity_tolerance = 0.2
        default_config.temperature_tolerance = 0.0
        default_config.water_tolerance = 0.0
        default_config.radiation_tolerance = 0.0
        for gas in default_config.atmosphere_preferences:
            default_config.atmosphere_preferences[gas] = 0.0

        aptitude_cost = budget.calculate_aptitude_cost(default_config)
        tolerance_cost = budget.calculate_tolerance_cost(default_config)
        total_cost = budget.calculate_total_cost(default_config)

        assert aptitude_cost == 3
        assert tolerance_cost == 3
        assert total_cost == 6

    def test_within_budget_default_config(self, budget, default_config):
        """Default config with minimal tolerance should be within budget."""
        default_config.gravity_tolerance = 0.0
        default_config.temperature_tolerance = 0.0
        default_config.water_tolerance = 0.0
        default_config.radiation_tolerance = 0.0
        for gas in default_config.atmosphere_preferences:
            default_config.atmosphere_preferences[gas] = 0.0
        assert budget.is_within_budget(default_config) is True

    def test_over_budget_detection(self, budget, default_config):
        """Config with max everything should be over budget."""
        # Max all aptitudes
        default_config.aptitude_strength = 100
        default_config.aptitude_intelligence = 100
        default_config.aptitude_constitution = 100
        default_config.aptitude_dexterity = 100
        default_config.aptitude_tolerance_other_species = 100
        default_config.aptitude_cooperation = 100
        default_config.aptitude_happiness = 100
        default_config.aptitude_population_growth = 100
        default_config.aptitude_conflict_tolerance = 100

        # Max all tolerances
        default_config.gravity_tolerance = 1.0
        default_config.temperature_tolerance = 100.0
        default_config.water_tolerance = 1.0
        default_config.radiation_tolerance = 100.0
        for gas in default_config.atmosphere_preferences:
            default_config.atmosphere_preferences[gas] = 100.0

        assert budget.is_within_budget(default_config) is False

    def test_remaining_points_calculation(self, budget, default_config):
        """Remaining points should be budget minus cost."""
        default_config.aptitude_strength = 53  # +3 cost
        default_config.gravity_tolerance = 0.0
        default_config.temperature_tolerance = 0.0
        default_config.water_tolerance = 0.0
        default_config.radiation_tolerance = 0.0
        for gas in default_config.atmosphere_preferences:
            default_config.atmosphere_preferences[gas] = 0.0

        remaining = budget.get_remaining_points(default_config)
        assert remaining == 97  # 100 - 3

    def test_remaining_points_can_be_negative(self, budget, default_config):
        """Remaining points can be negative when over budget."""
        default_config.aptitude_strength = 100  # +440
        default_config.gravity_tolerance = 1.0  # 10 steps = 1023 points
        default_config.temperature_tolerance = 0.0
        default_config.water_tolerance = 0.0
        default_config.radiation_tolerance = 0.0
        for gas in default_config.atmosphere_preferences:
            default_config.atmosphere_preferences[gas] = 0.0

        remaining = budget.get_remaining_points(default_config)
        assert remaining < 0

    def test_custom_budget_total(self):
        """Custom budget total should be respected."""
        budget = RacePointBudget(total_budget=50)
        config = RaceConfig()
        config.gravity_tolerance = 0.0
        config.temperature_tolerance = 0.0
        config.water_tolerance = 0.0
        config.radiation_tolerance = 0.0
        for gas in config.atmosphere_preferences:
            config.atmosphere_preferences[gas] = 0.0

        remaining = budget.get_remaining_points(config)
        assert remaining == 50


class TestRacePointBudgetCostBreakdown:
    """Tests for detailed cost breakdown."""

    @pytest.fixture
    def budget(self):
        return RacePointBudget()

    def test_get_aptitude_breakdown(self, budget):
        """Should return per-aptitude costs."""
        config = RaceConfig()
        config.aptitude_strength = 53  # +3
        config.aptitude_intelligence = 48  # -2

        breakdown = budget.get_aptitude_breakdown(config)

        assert breakdown["strength"] == 3
        assert breakdown["intelligence"] == -2
        assert breakdown["constitution"] == 0  # at base

    def test_get_tolerance_breakdown(self, budget):
        """Should return per-tolerance costs."""
        config = RaceConfig()
        config.gravity_tolerance = 0.2  # 3 points
        config.temperature_tolerance = 10.0  # 1 point
        config.water_tolerance = 0.0
        config.radiation_tolerance = 0.0
        for gas in config.atmosphere_preferences:
            config.atmosphere_preferences[gas] = 0.0

        breakdown = budget.get_tolerance_breakdown(config)

        assert breakdown["gravity"] == 3
        assert breakdown["temperature"] == 1
        assert breakdown["water"] == 0
        assert breakdown["radiation"] == 0

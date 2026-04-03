"""
Tests for TestMetadata end condition options.

TDD tests for TestMetadata supporting:
- absolute_max_ticks parameter
- escape_radius, escape_team, escape_all_ships parameters
- _create_end_condition() helper updates
"""
import pytest

from simulation_tests.scenarios.base import TestMetadata, TestScenario
from game.simulation.systems.battle_end_conditions import TickLimitCondition
from game.core.constants import SimulationConstants


class TestTestMetadataDefaults:
    """Tests for TestMetadata default values."""

    def test_existing_defaults_unchanged(self):
        """Existing defaults should remain unchanged."""
        metadata = TestMetadata(
            test_id="TEST-001",
            category="Test",
            subcategory="Unit",
            name="Test scenario",
            summary="A test",
            conditions=[],
            edge_cases=[],
            expected_outcome="Pass",
            pass_criteria="True"
        )

        assert metadata.max_ticks == 1000
        assert metadata.seed == 42
        assert metadata.battle_end_mode == "time_based"
        assert metadata.battle_end_check_derelict is False

    def test_absolute_max_ticks_default(self):
        """absolute_max_ticks should default to SimulationConstants value."""
        metadata = TestMetadata(
            test_id="TEST-001",
            category="Test",
            subcategory="Unit",
            name="Test scenario",
            summary="A test",
            conditions=[],
            edge_cases=[],
            expected_outcome="Pass",
            pass_criteria="True"
        )

        assert hasattr(metadata, 'absolute_max_ticks')
        assert metadata.absolute_max_ticks == SimulationConstants.ABSOLUTE_MAX_TICKS

    def test_escape_parameters_default_none(self):
        """Escape parameters should default appropriately."""
        metadata = TestMetadata(
            test_id="TEST-001",
            category="Test",
            subcategory="Unit",
            name="Test scenario",
            summary="A test",
            conditions=[],
            edge_cases=[],
            expected_outcome="Pass",
            pass_criteria="True"
        )

        assert hasattr(metadata, 'escape_radius')
        assert metadata.escape_radius is None
        assert hasattr(metadata, 'escape_team')
        assert metadata.escape_team is None
        assert hasattr(metadata, 'escape_all_ships')
        assert metadata.escape_all_ships is False


class TestTestMetadataCustomValues:
    """Tests for TestMetadata with custom end condition values."""

    def test_custom_absolute_max_ticks(self):
        """TestMetadata should accept custom absolute_max_ticks."""
        metadata = TestMetadata(
            test_id="TEST-001",
            category="Test",
            subcategory="Unit",
            name="Test scenario",
            summary="A test",
            conditions=[],
            edge_cases=[],
            expected_outcome="Pass",
            pass_criteria="True",
            absolute_max_ticks=100_000
        )

        assert metadata.absolute_max_ticks == 100_000

    def test_escape_mode_parameters(self):
        """TestMetadata should accept escape mode parameters."""
        metadata = TestMetadata(
            test_id="TEST-001",
            category="Test",
            subcategory="Unit",
            name="Test scenario",
            summary="A test",
            conditions=[],
            edge_cases=[],
            expected_outcome="Pass",
            pass_criteria="True",
            battle_end_mode="escape",
            escape_radius=5000.0,
            escape_team=1,
            escape_all_ships=True
        )

        assert metadata.battle_end_mode == "escape"
        assert metadata.escape_radius == 5000.0
        assert metadata.escape_team == 1
        assert metadata.escape_all_ships is True


class TestTestMetadataToDict:
    """Tests for TestMetadata.to_dict() with new fields."""

    def test_to_dict_includes_new_fields(self):
        """to_dict should include new end condition fields."""
        metadata = TestMetadata(
            test_id="TEST-001",
            category="Test",
            subcategory="Unit",
            name="Test scenario",
            summary="A test",
            conditions=[],
            edge_cases=[],
            expected_outcome="Pass",
            pass_criteria="True",
            absolute_max_ticks=500_000,
            escape_radius=3000.0,
            escape_team=0,
            escape_all_ships=True
        )

        data = metadata.to_dict()

        assert data['absolute_max_ticks'] == 500_000
        assert data['escape_radius'] == 3000.0
        assert data['escape_team'] == 0
        assert data['escape_all_ships'] is True


class MockScenario(TestScenario):
    """Mock scenario for testing _create_end_condition()."""

    metadata = TestMetadata(
        test_id="MOCK-001",
        category="Mock",
        subcategory="Test",
        name="Mock scenario",
        summary="A mock test scenario",
        conditions=[],
        edge_cases=[],
        expected_outcome="Pass",
        pass_criteria="True"
    )

    def setup(self, battle_engine):
        pass

    def verify(self, battle_engine):
        return True


class TestCreateEndCondition:
    """Tests for TestScenario._create_end_condition() helper."""

    def test_creates_time_based_condition(self):
        """_create_end_condition should create TickLimitCondition."""
        scenario = MockScenario()
        scenario.metadata = TestMetadata(
            test_id="TEST-001",
            category="Test",
            subcategory="Unit",
            name="Test",
            summary="Test",
            conditions=[],
            edge_cases=[],
            expected_outcome="Pass",
            pass_criteria="True",
            battle_end_mode="time_based",
            max_ticks=500
        )

        condition = scenario._create_end_condition()

        assert isinstance(condition, TickLimitCondition)
        assert condition.max_ticks == 500

    def test_creates_default_tick_limit_condition(self):
        """_create_end_condition should create TickLimitCondition with default max_ticks."""
        scenario = MockScenario()
        scenario.metadata = TestMetadata(
            test_id="TEST-001",
            category="Test",
            subcategory="Unit",
            name="Test",
            summary="Test",
            conditions=[],
            edge_cases=[],
            expected_outcome="Pass",
            pass_criteria="True",
        )

        condition = scenario._create_end_condition()

        assert isinstance(condition, TickLimitCondition)
        assert condition.max_ticks == 1000  # Default from TestMetadata

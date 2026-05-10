"""
Tests for TestScenario._create_end_condition().

``TestScenario._create_end_condition()`` is the single source of scenario end
conditions — it builds a ``TickLimitCondition(max_ticks=metadata.max_ticks)``
by default. The returned condition is carried on ``BattleSpec.end_condition``
(via ``scenario.to_spec()``) and consumed by ``run_battle(spec)``. Scenarios
needing a different condition override ``_create_end_condition()``.
"""
from combat_lab.scenarios.base import TestMetadata, TestScenario
from game.simulation.systems.battle_end_conditions import TickLimitCondition


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
        pass_criteria="True",
    )

    def setup(self, battle_engine):
        pass

    def validate(self, engine):
        return []


class TestCreateEndCondition:
    """Tests for TestScenario._create_end_condition() helper."""

    def test_creates_tick_limit_condition_with_metadata_max_ticks(self):
        """_create_end_condition builds TickLimitCondition(max_ticks=metadata.max_ticks)."""
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
            max_ticks=500,
        )

        condition = scenario._create_end_condition()

        assert isinstance(condition, TickLimitCondition)
        assert condition.max_ticks == 500

    def test_creates_default_tick_limit_condition(self):
        """Default max_ticks (1000) flows through to the TickLimitCondition."""
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

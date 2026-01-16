"""
Test scenario fixtures for Combat Lab service tests.

This module provides helper functions and fixtures for testing code that
interacts with TestScenario and TestMetadata from the simulation_tests framework.

Usage:
    from tests.fixtures.test_scenarios import create_test_metadata, create_mock_test_scenario

    def test_something():
        metadata = create_test_metadata(test_id="MY-001", name="My Test")
        scenario = create_mock_test_scenario(metadata=metadata)
"""
import pytest
from unittest.mock import Mock
from typing import Dict, Any, List, Optional


def create_test_metadata(
    test_id: str = "TEST-001",
    name: str = "Sample Test",
    category: str = "Test",
    subcategory: str = "Test Subcategory",
    summary: str = "A sample test",
    conditions: Optional[List[str]] = None,
    edge_cases: Optional[List[str]] = None,
    expected_outcome: str = "Expected outcome",
    pass_criteria: str = "Pass criteria",
    validation_rules: Optional[List] = None,
    max_ticks: int = 500,
    seed: int = 42,
    battle_end_mode: str = "time_based",
    ui_priority: int = 0,
    tags: Optional[List[str]] = None,
):
    """
    Helper to create TestMetadata with sensible defaults.

    Args:
        test_id: Unique test identifier (e.g., "BEAM-001")
        name: Short descriptive name
        category: Major category (e.g., "Weapons")
        subcategory: Specific area (e.g., "Beam Accuracy")
        summary: Brief description of the test
        conditions: List of test conditions
        edge_cases: Edge cases being tested
        expected_outcome: What should happen
        pass_criteria: How we verify success
        validation_rules: List of ValidationRule instances
        max_ticks: Maximum simulation ticks
        seed: Random seed for reproducibility
        battle_end_mode: Battle end condition mode
        ui_priority: Display priority in Combat Lab
        tags: Optional tags for filtering

    Returns:
        TestMetadata instance

    Example:
        metadata = create_test_metadata(
            test_id="BEAM-001",
            name="Point-blank accuracy",
            category="Weapons",
            conditions=["Distance: 50px", "Stationary target"]
        )
    """
    from simulation_tests.scenarios.base import TestMetadata

    return TestMetadata(
        test_id=test_id,
        name=name,
        category=category,
        subcategory=subcategory,
        summary=summary,
        conditions=conditions or [],
        edge_cases=edge_cases or [],
        expected_outcome=expected_outcome,
        pass_criteria=pass_criteria,
        validation_rules=validation_rules or [],
        max_ticks=max_ticks,
        seed=seed,
        battle_end_mode=battle_end_mode,
        ui_priority=ui_priority,
        tags=tags or [],
    )


def create_mock_test_scenario(
    name: str = "Test Scenario",
    test_id: str = "TEST-001",
    max_ticks: int = 500,
    passed: bool = False,
    results: Optional[Dict[str, Any]] = None,
    metadata: Optional[Any] = None,
) -> Mock:
    """
    Create a mock test scenario for unit tests.

    Args:
        name: Scenario name
        test_id: Test identifier
        max_ticks: Maximum ticks for the test
        passed: Whether the test passed
        results: Results dictionary
        metadata: Optional TestMetadata (creates mock if None)

    Returns:
        Mock object mimicking TestScenario interface
    """
    scenario = Mock()
    scenario.name = name
    scenario.max_ticks = max_ticks
    scenario.passed = passed
    scenario.results = results or {}

    if metadata is None:
        scenario.metadata = Mock()
        scenario.metadata.test_id = test_id
        scenario.metadata.max_ticks = max_ticks
        scenario.metadata.name = name
        scenario.metadata.category = "Test"
        scenario.metadata.subcategory = "Test Subcategory"
        scenario.metadata.summary = "A sample test"
        scenario.metadata.conditions = []
        scenario.metadata.edge_cases = []
        scenario.metadata.expected_outcome = "Expected outcome"
        scenario.metadata.pass_criteria = "Pass criteria"
        scenario.metadata.validation_rules = []
        scenario.metadata.tags = []
        scenario.metadata.to_dict = Mock(return_value={
            'test_id': test_id,
            'name': name,
            'category': 'Test',
            'subcategory': 'Test Subcategory',
            'max_ticks': max_ticks,
        })
    else:
        scenario.metadata = metadata

    scenario.setup = Mock()
    scenario.update = Mock()
    scenario.verify = Mock(return_value=True)
    scenario.get_data_paths = Mock(return_value={
        'components': 'data/components.json',
        'modifiers': 'data/modifiers.json',
        'vehicle_classes': 'data/vehicleclasses.json',
    })

    return scenario


def create_mock_test_registry(scenarios: Optional[Dict[str, Dict[str, Any]]] = None) -> Mock:
    """
    Create a mock test registry for unit tests.

    Args:
        scenarios: Optional dict of scenario info dicts to pre-populate

    Returns:
        Mock object mimicking TestRegistry interface
    """
    registry = Mock()
    registry.scenarios = scenarios or {}

    registry.get_all_scenarios = Mock(return_value=registry.scenarios)
    registry.get_by_id = Mock(side_effect=lambda x: registry.scenarios.get(x))
    registry.get_by_category = Mock(return_value={})
    registry.get_categories = Mock(return_value=[])
    registry.refresh = Mock()
    registry.clear = Mock()
    registry.update_last_run_results = Mock()

    return registry


def create_mock_test_runner() -> Mock:
    """
    Create a mock test runner for unit tests.

    Returns:
        Mock object mimicking TestRunner interface
    """
    runner = Mock()
    runner.current_scenario = None
    runner.test_log = []
    runner.engine = Mock()
    runner.load_data_for_scenario = Mock()
    runner.run_scenario = Mock()
    runner._log_test_execution = Mock()

    return runner


def create_mock_test_history() -> Mock:
    """
    Create a mock test history for unit tests.

    Returns:
        Mock object mimicking TestHistory interface
    """
    history = Mock()
    history.runs = []
    history.add_run = Mock()
    history.get_latest_run = Mock(return_value=None)
    history.get_runs_for_test = Mock(return_value=[])
    history.clear = Mock()

    return history


def create_scenario_info(
    test_id: str = "TEST-001",
    metadata: Optional[Any] = None,
    scenario_class: Optional[type] = None,
    file_path: str = "simulation_tests/scenarios/test_scenarios.py",
    last_run_results: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a scenario info dict as returned by TestRegistry.

    Args:
        test_id: Test identifier
        metadata: TestMetadata or mock (creates default if None)
        scenario_class: Scenario class or Mock
        file_path: Path to scenario file
        last_run_results: Results from last test run

    Returns:
        Dict matching TestRegistry scenario info format
    """
    if metadata is None:
        metadata = create_test_metadata(test_id=test_id)

    return {
        'test_id': test_id,
        'metadata': metadata,
        'class': scenario_class or Mock(),
        'module': f"simulation_tests.scenarios.{test_id.lower().replace('-', '_')}",
        'file': file_path,
        'last_run_results': last_run_results,
    }


# =============================================================================
# Sample Data Fixtures
# =============================================================================

def create_sample_ship_data(
    name: str = "Test Ship",
    ship_class: str = "TestS_2L",
    hp: int = 1000,
    mass: float = 400.0,
) -> Dict[str, Any]:
    """
    Create sample ship JSON data for testing.

    Args:
        name: Ship name
        ship_class: Vehicle class
        hp: Hit points
        mass: Ship mass

    Returns:
        Dict matching ship JSON format
    """
    return {
        "name": name,
        "vehicle_class": ship_class,
        "hp": hp,
        "mass": mass,
        "angle": 0,
        "ai_enabled": False,
        "layers": {
            "CORE": [
                {"id": "test_bridge", "component_id": "test_bridge", "x": 0, "y": 0}
            ]
        },
        "expected_stats": {
            "mass": mass
        }
    }


def create_sample_component_data(
    component_id: str = "test_beam",
    name: str = "Test Beam Weapon",
    component_type: str = "weapon",
    damage: int = 10,
    weapon_range: int = 500,
    base_accuracy: float = 0.8,
) -> Dict[str, Any]:
    """
    Create sample component JSON data for testing.

    Args:
        component_id: Component ID
        name: Display name
        component_type: Type string
        damage: Weapon damage
        weapon_range: Weapon range
        base_accuracy: Base accuracy value

    Returns:
        Dict matching component JSON format
    """
    return {
        "id": component_id,
        "name": name,
        "type": component_type,
        "abilities": {
            "BeamWeaponAbility": {
                "damage": damage,
                "range": weapon_range,
                "base_accuracy": base_accuracy,
                "accuracy_falloff": 0.002,
                "reload": 60,
                "firing_arc": 360
            }
        }
    }


# =============================================================================
# Pytest Fixtures
# =============================================================================

@pytest.fixture
def sample_test_metadata():
    """Sample test metadata object."""
    return create_test_metadata()


@pytest.fixture
def mock_test_scenario():
    """Mock test scenario instance."""
    return create_mock_test_scenario()


@pytest.fixture
def mock_test_registry():
    """Mock test registry instance."""
    return create_mock_test_registry()


@pytest.fixture
def mock_test_runner():
    """Mock test runner instance."""
    return create_mock_test_runner()


@pytest.fixture
def mock_test_history():
    """Mock test history instance."""
    return create_mock_test_history()


@pytest.fixture
def sample_scenario_info(sample_test_metadata):
    """Sample scenario info dict from registry."""
    return create_scenario_info(metadata=sample_test_metadata)


@pytest.fixture
def sample_ship_data():
    """Sample ship JSON data."""
    return create_sample_ship_data()


@pytest.fixture
def sample_component_data():
    """Sample component JSON data."""
    return create_sample_component_data()

"""
Pytest fixtures for Phase 3 service tests.

Provides mock objects, sample data, and test utilities for testing
the Combat Lab service layer.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any


# =============================================================================
# Helper Functions
# =============================================================================

def create_test_metadata(
    test_id="TEST-001",
    name="Sample Test",
    category="Test",
    subcategory="Test Subcategory",
    summary="A sample test",
    conditions=None,
    edge_cases=None,
    expected_outcome="Expected outcome",
    pass_criteria="Pass criteria",
    validation_rules=None,
    max_ticks=500,
    seed=42
):
    """Helper to create TestMetadata with sensible defaults."""
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
        seed=seed
    )


# =============================================================================
# Test Data Fixtures
# =============================================================================

@pytest.fixture
def sample_ship_data() -> Dict[str, Any]:
    """Sample ship JSON data."""
    return {
        "name": "Test Attacker",
        "vehicle_class": "Cruiser",
        "hp": 1000,
        "mass": 400.0,
        "angle": 0,
        "ai_enabled": False,
        "layers": {
            "CORE": [
                {"id": "test_beam_low_acc_1dmg", "component_id": "test_beam_low_acc_1dmg", "x": 0, "y": 0}
            ]
        },
        "expected_stats": {
            "mass": 400.0
        }
    }


@pytest.fixture
def sample_target_data() -> Dict[str, Any]:
    """Sample target ship JSON data."""
    return {
        "name": "Test Target",
        "vehicle_class": "Cruiser",
        "hp": 1000,
        "mass": 400.0,
        "angle": 0,
        "ai_enabled": False,
        "layers": {
            "CORE": [
                {"id": "hull_base", "component_id": "Hull_Base", "x": 0, "y": 0}
            ]
        },
        "expected_stats": {
            "mass": 400.0
        }
    }


@pytest.fixture
def sample_component_data() -> Dict[str, Any]:
    """Sample component JSON data."""
    return {
        "id": "test_beam_low_acc_1dmg",
        "name": "Test Beam Weapon",
        "type": "weapon",
        "abilities": {
            "BeamWeaponAbility": {
                "damage": 1,
                "range": 1000,
                "base_accuracy": 0.5,
                "accuracy_falloff": 0.002,
                "reload": 60,
                "firing_arc": 360
            }
        }
    }


@pytest.fixture
def sample_components_file() -> Dict[str, Any]:
    """Sample components.json structure."""
    return {
        "_metadata": {
            "_schema_version": "1.0",
            "_data_version": "1.0"
        },
        "components": [
            {
                "id": "test_beam_low_acc_1dmg",
                "name": "Test Beam Weapon",
                "type": "weapon",
                "abilities": {
                    "BeamWeaponAbility": {
                        "damage": 1,
                        "range": 1000,
                        "base_accuracy": 0.5,
                        "accuracy_falloff": 0.002,
                        "reload": 60,
                        "firing_arc": 360
                    }
                }
            },
            {
                "id": "Hull_Base",
                "name": "Base Hull",
                "type": "hull",
                "abilities": {}
            }
        ]
    }


@pytest.fixture
def sample_test_metadata():
    """Sample test metadata object."""
    from simulation_tests.scenarios.base import TestMetadata

    return TestMetadata(
        test_id="TEST-001",
        name="Sample Test",
        category="Test Category",
        subcategory="Test Subcategory",
        summary="A sample test for unit testing",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Low.json",
            "Target: Test_Target_Stationary.json (mass=400)"
        ],
        edge_cases=["Sample edge case"],
        expected_outcome="Expected outcome description",
        pass_criteria="Pass criteria description",
        validation_rules=[],
        max_ticks=500,
        seed=42
    )


@pytest.fixture
def sample_scenario_info(sample_test_metadata):
    """Sample scenario info dict from registry."""
    return {
        'test_id': 'TEST-001',
        'metadata': sample_test_metadata,
        'class': Mock(),
        'file': 'simulation_tests/scenarios/test_scenarios.py',
        'last_run_results': None
    }


# =============================================================================
# Mock Object Fixtures
# =============================================================================

@pytest.fixture
def mock_battle_engine():
    """Mock battle engine."""
    engine = Mock()
    engine.tick_counter = 0
    engine.ships = []
    engine.update = Mock()
    engine.is_battle_over = Mock(return_value=False)
    engine.start = Mock()
    return engine


@pytest.fixture
def mock_battle_scene(mock_battle_engine):
    """Mock battle scene with engine."""
    scene = Mock()
    scene.engine = mock_battle_engine
    scene.headless_mode = False
    scene.sim_paused = True
    scene.test_mode = False
    scene.test_scenario = None
    scene.test_tick_count = 0
    scene.test_completed = False
    scene.action_return_to_test_lab = False
    scene.camera = Mock()
    scene.camera.fit_objects = Mock()
    return scene


@pytest.fixture
def mock_game(mock_battle_scene):
    """Mock game object."""
    game = Mock()
    game.battle_scene = mock_battle_scene
    game.state = None
    return game


@pytest.fixture
def mock_test_scenario():
    """Mock test scenario instance."""
    scenario = Mock()
    scenario.name = "Test Scenario"
    scenario.metadata = Mock()
    scenario.metadata.test_id = "TEST-001"
    scenario.metadata.max_ticks = 500
    scenario.max_ticks = 500
    scenario.passed = False
    scenario.results = {}
    scenario.setup = Mock()
    scenario.update = Mock()
    scenario.verify = Mock(return_value=True)
    return scenario


@pytest.fixture
def mock_test_runner():
    """Mock test runner."""
    runner = Mock()
    runner.load_data_for_scenario = Mock()
    runner._log_test_execution = Mock()
    return runner


@pytest.fixture
def mock_test_registry():
    """Mock test registry."""
    registry = Mock()
    registry.get_all_scenarios = Mock(return_value={})
    registry.get_by_id = Mock(return_value=None)
    registry.refresh = Mock()
    return registry


@pytest.fixture
def mock_test_history():
    """Mock test history."""
    history = Mock()
    history.add_run = Mock()
    history.get_latest_run = Mock(return_value=None)
    return history


# =============================================================================
# Temporary Directory Fixtures
# =============================================================================

@pytest.fixture
def temp_data_dir(tmp_path, sample_ship_data, sample_target_data, sample_components_file):
    """Create temporary data directory with sample files."""
    data_dir = tmp_path / "data"
    ships_dir = data_dir / "ships"
    ships_dir.mkdir(parents=True)

    # Write ship files
    with open(ships_dir / "Test_Attacker_Beam360_Low.json", 'w') as f:
        json.dump(sample_ship_data, f)

    with open(ships_dir / "Test_Target_Stationary.json", 'w') as f:
        json.dump(sample_target_data, f)

    # Write components file
    with open(data_dir / "components.json", 'w') as f:
        json.dump(sample_components_file, f)

    return data_dir


# =============================================================================
# Observer Pattern Test Utilities
# =============================================================================

@pytest.fixture
def observer_spy():
    """Create a spy function that tracks calls."""
    call_count = {'count': 0}

    def spy():
        call_count['count'] += 1

    spy.call_count = call_count
    return spy


# =============================================================================
# Validation Test Fixtures
# =============================================================================

@pytest.fixture
def sample_validation_rule():
    """Sample ExactMatchRule."""
    from simulation_tests.scenarios.validation import ExactMatchRule
    return ExactMatchRule(
        name="Beam Weapon Damage",
        path="attacker.weapon.damage",
        expected=1
    )


@pytest.fixture
def sample_validation_context():
    """Sample validation context."""
    return {
        'attacker': {
            'mass': 400.0,
            'weapon': {
                'damage': 1,
                'range': 1000,
                'base_accuracy': 0.5,
                'accuracy_falloff': 0.002
            }
        },
        'target': {
            'mass': 400.0
        }
    }


@pytest.fixture
def sample_validation_results():
    """Sample validation results list."""
    from simulation_tests.scenarios.validation import ValidationResult

    return [
        ValidationResult(
            name="Test Rule 1",
            status="PASS",
            message="Value matches expected",
            expected=1,
            actual=1
        ),
        ValidationResult(
            name="Test Rule 2",
            status="FAIL",
            message="Value mismatch",
            expected=2,
            actual=3
        )
    ]

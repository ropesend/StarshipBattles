"""
Pytest fixtures for Combat Lab service tests.

This module imports shared fixtures from tests/fixtures/ and provides
any service-specific fixtures needed for testing the Combat Lab service layer.
"""

import pytest
import json
from typing import Dict, Any

# Import shared fixtures from consolidated location
from tests.fixtures.battle import (
    create_mock_battle_engine,
    create_mock_battle_scene,
)
from tests.fixtures.test_scenarios import (
    create_test_metadata,
    create_mock_test_scenario,
    create_mock_test_registry,
    create_mock_test_runner,
    create_mock_test_history,
    create_scenario_info,
)


# =============================================================================
# Re-export fixtures for pytest discovery
# =============================================================================

@pytest.fixture
def mock_battle_engine():
    """Mock battle engine."""
    return create_mock_battle_engine()


@pytest.fixture
def mock_battle_scene(mock_battle_engine):
    """Mock battle scene with engine."""
    return create_mock_battle_scene(engine=mock_battle_engine)


@pytest.fixture
def mock_game(mock_battle_scene):
    """Mock game object."""
    from unittest.mock import Mock
    game = Mock()
    game.battle_scene = mock_battle_scene
    game.state = None
    return game


@pytest.fixture
def mock_test_scenario():
    """Mock test scenario instance."""
    return create_mock_test_scenario()


@pytest.fixture
def mock_test_runner():
    """Mock test runner."""
    return create_mock_test_runner()


@pytest.fixture
def mock_test_registry():
    """Mock test registry."""
    return create_mock_test_registry()


@pytest.fixture
def mock_test_history():
    """Mock test history."""
    return create_mock_test_history()


@pytest.fixture
def sample_test_metadata():
    """Sample test metadata object with ship conditions for service tests."""
    return create_test_metadata(
        conditions=[
            "Attacker: Test_Attacker_Beam360_Low.json",
            "Target: Test_Target_Stationary.json (mass=400)"
        ],
        edge_cases=["Sample edge case"],
    )


@pytest.fixture
def sample_scenario_info(sample_test_metadata):
    """Sample scenario info dict from registry."""
    return create_scenario_info(metadata=sample_test_metadata)


@pytest.fixture
def sample_ship_data() -> Dict[str, Any]:
    """Sample ship JSON data matching Test_Attacker_Beam360_Low.json."""
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
    """Sample target ship JSON data matching Test_Target_Stationary.json."""
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
    """Sample component JSON data matching test_beam_low_acc_1dmg."""
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
def sample_components_file(sample_component_data) -> Dict[str, Any]:
    """Sample components.json structure."""
    return {
        "_metadata": {
            "_schema_version": "1.0",
            "_data_version": "1.0"
        },
        "components": [
            sample_component_data,
            {
                "id": "Hull_Base",
                "name": "Base Hull",
                "type": "hull",
                "abilities": {}
            }
        ]
    }


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

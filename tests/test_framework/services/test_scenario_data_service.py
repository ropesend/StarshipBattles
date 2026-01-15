"""
Unit tests for ScenarioDataService.

Tests data loading, ship extraction, component lookup, and validation context building.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from test_framework.services.scenario_data_service import ScenarioDataService
from tests.test_framework.services.conftest import create_test_metadata


class TestScenarioDataServiceInit:
    """Test ScenarioDataService initialization."""

    def test_init_with_default_data_dir(self):
        """Test initialization with default data directory."""
        service = ScenarioDataService()

        assert service.data_dir.name == 'data'
        assert 'simulation_tests' in str(service.data_dir)
        assert service.ships_dir == service.data_dir / 'ships'
        assert service.components_file == service.data_dir / 'components.json'
        assert service._components_cache is None

    def test_init_with_custom_data_dir(self, tmp_path):
        """Test initialization with custom data directory."""
        custom_dir = tmp_path / "custom_data"
        service = ScenarioDataService(data_dir=custom_dir)

        assert service.data_dir == custom_dir
        assert service.ships_dir == custom_dir / 'ships'
        assert service.components_file == custom_dir / 'components.json'


class TestExtractShipsFromScenario:
    """Test ship extraction from scenario metadata."""

    def test_extract_ships_basic(self, temp_data_dir, sample_test_metadata):
        """Test basic ship extraction."""
        service = ScenarioDataService(data_dir=temp_data_dir)
        ships = service.extract_ships_from_scenario(sample_test_metadata)

        assert len(ships) == 2
        assert ships[0]['role'] == 'Attacker'
        assert ships[0]['filename'] == 'Test_Attacker_Beam360_Low.json'
        assert ships[0]['ship_data']['name'] == 'Test Attacker'
        assert ships[1]['role'] == 'Target'
        assert ships[1]['filename'] == 'Test_Target_Stationary.json'

    def test_extract_ships_with_component_ids(self, temp_data_dir, sample_test_metadata):
        """Test that component IDs are extracted from layers."""
        service = ScenarioDataService(data_dir=temp_data_dir)
        ships = service.extract_ships_from_scenario(sample_test_metadata)

        attacker = ships[0]
        assert 'test_beam_low_acc_1dmg' in attacker['component_ids']

    def test_extract_ships_with_mass_annotation(self, temp_data_dir):
        """Test extraction with mass annotation in condition string."""
        metadata = create_test_metadata(
            test_id="TEST-002",
            name="Test with Mass",
            conditions=[
                "Attacker: Test_Attacker_Beam360_Low.json",
                "Target: Test_Target_Stationary.json (mass=400)"
            ]
        )

        service = ScenarioDataService(data_dir=temp_data_dir)
        ships = service.extract_ships_from_scenario(metadata)

        assert len(ships) == 2
        assert ships[1]['filename'] == 'Test_Target_Stationary.json'

    def test_extract_ships_missing_file(self, temp_data_dir, sample_test_metadata):
        """Test extraction with missing ship file."""
        metadata = create_test_metadata(
            test_id="TEST-003",
            name="Test Missing File",
            conditions=["Attacker: NonExistent.json"]
        )

        service = ScenarioDataService(data_dir=temp_data_dir)
        ships = service.extract_ships_from_scenario(metadata)

        # Should return empty list if file not found
        assert len(ships) == 0

    def test_extract_ships_no_ship_conditions(self):
        """Test extraction when metadata has no ship conditions."""
        metadata = create_test_metadata(
            test_id="TEST-004",
            name="Test No Ships",
            conditions=["Some other condition"]
        )

        service = ScenarioDataService()
        ships = service.extract_ships_from_scenario(metadata)

        assert len(ships) == 0


class TestLoadComponentData:
    """Test component data loading."""

    def test_load_component_data_first_call(self, temp_data_dir):
        """Test loading component data on first call (cache miss)."""
        service = ScenarioDataService(data_dir=temp_data_dir)

        component = service.load_component_data("test_beam_low_acc_1dmg")

        assert component is not None
        assert component['id'] == "test_beam_low_acc_1dmg"
        assert 'BeamWeaponAbility' in component['abilities']
        assert component['abilities']['BeamWeaponAbility']['damage'] == 1

    def test_load_component_data_cached(self, temp_data_dir):
        """Test that subsequent calls use cache."""
        service = ScenarioDataService(data_dir=temp_data_dir)

        # First call
        component1 = service.load_component_data("test_beam_low_acc_1dmg")
        # Second call (should use cache)
        component2 = service.load_component_data("test_beam_low_acc_1dmg")

        assert component1 is component2  # Same object reference

    def test_load_component_data_not_found(self, temp_data_dir):
        """Test loading non-existent component."""
        service = ScenarioDataService(data_dir=temp_data_dir)

        component = service.load_component_data("non_existent_component")

        assert component is None

    def test_load_component_data_missing_file(self, tmp_path):
        """Test loading when components.json doesn't exist."""
        service = ScenarioDataService(data_dir=tmp_path)

        component = service.load_component_data("test_beam_low_acc_1dmg")

        assert component is None
        assert service._components_cache == {}

    def test_load_component_data_invalid_json(self, tmp_path):
        """Test loading with invalid JSON file."""
        components_file = tmp_path / "components.json"
        components_file.write_text("{ invalid json")

        service = ScenarioDataService(data_dir=tmp_path)
        component = service.load_component_data("test_beam_low_acc_1dmg")

        assert component is None
        assert service._components_cache == {}


class TestGetComponentsCache:
    """Test components cache retrieval."""

    def test_get_components_cache_loaded(self, temp_data_dir):
        """Test getting cache when already loaded."""
        service = ScenarioDataService(data_dir=temp_data_dir)
        service.load_component_data("test_beam_low_acc_1dmg")  # Load cache

        cache = service.get_components_cache()

        assert len(cache) == 2
        assert "test_beam_low_acc_1dmg" in cache
        assert "Hull_Base" in cache

    def test_get_components_cache_not_loaded(self, temp_data_dir):
        """Test getting cache triggers loading if not loaded."""
        service = ScenarioDataService(data_dir=temp_data_dir)

        cache = service.get_components_cache()

        assert len(cache) == 2
        assert service._components_cache is not None


class TestBuildValidationContext:
    """Test validation context building."""

    def test_build_validation_context_basic(self, temp_data_dir, sample_test_metadata):
        """Test building basic validation context."""
        service = ScenarioDataService(data_dir=temp_data_dir)

        context = service.build_validation_context(sample_test_metadata)

        assert 'attacker' in context
        assert 'target' in context
        assert context['attacker']['mass'] == 400.0
        assert context['target']['mass'] == 400.0

    def test_build_validation_context_with_weapon(self, temp_data_dir, sample_test_metadata):
        """Test that weapon data is extracted into context."""
        service = ScenarioDataService(data_dir=temp_data_dir)

        context = service.build_validation_context(sample_test_metadata)

        assert 'weapon' in context['attacker']
        weapon = context['attacker']['weapon']
        assert weapon['damage'] == 1
        assert weapon['range'] == 1000
        assert weapon['base_accuracy'] == 0.5
        assert weapon['accuracy_falloff'] == 0.002
        assert weapon['reload'] == 60
        assert weapon['firing_arc'] == 360

    def test_build_validation_context_no_weapon(self, temp_data_dir, sample_test_metadata):
        """Test context building for ship without weapons."""
        service = ScenarioDataService(data_dir=temp_data_dir)

        context = service.build_validation_context(sample_test_metadata)

        # Target has no weapon
        assert 'weapon' not in context['target']

    def test_build_validation_context_empty_ships(self):
        """Test context building when no ships extracted."""
        metadata = create_test_metadata(
            test_id="TEST-005",
            name="Test No Ships",
            conditions=[]
        )

        service = ScenarioDataService()
        context = service.build_validation_context(metadata)

        assert context == {}

    def test_build_validation_context_projectile_weapon(self, temp_data_dir):
        """Test context with ProjectileWeaponAbility."""
        # Create ship with projectile weapon
        ship_data = {
            "name": "Projectile Attacker",
            "layers": {
                "CORE": [
                    {"id": "test_projectile", "component_id": "test_projectile", "x": 0, "y": 0}
                ]
            },
            "expected_stats": {"mass": 400.0}
        }

        components_data = {
            "components": [
                {
                    "id": "test_projectile",
                    "abilities": {
                        "ProjectileWeaponAbility": {
                            "damage": 10,
                            "range": 800,
                            "projectile_speed": 300,
                            "reload": 30
                        }
                    }
                }
            ]
        }

        # Setup temp files
        ships_dir = temp_data_dir / "ships"
        with open(ships_dir / "Test_Projectile.json", 'w') as f:
            json.dump(ship_data, f)

        with open(temp_data_dir / "components.json", 'w') as f:
            json.dump(components_data, f)

        metadata = create_test_metadata(
            test_id="PROJ-001",
            name="Projectile Test",
            category="Projectile",
            conditions=["Attacker: Test_Projectile.json"]
        )

        service = ScenarioDataService(data_dir=temp_data_dir)
        service.clear_cache()  # Clear cache to load new components
        context = service.build_validation_context(metadata)

        assert 'weapon' in context['attacker']
        weapon = context['attacker']['weapon']
        assert weapon['damage'] == 10
        assert weapon['range'] == 800
        assert weapon['projectile_speed'] == 300

    def test_build_validation_context_seeker_weapon(self, temp_data_dir):
        """Test context with SeekerWeaponAbility."""
        # Create ship with seeker weapon
        ship_data = {
            "name": "Seeker Attacker",
            "layers": {
                "CORE": [
                    {"id": "test_seeker", "component_id": "test_seeker", "x": 0, "y": 0}
                ]
            },
            "expected_stats": {"mass": 400.0}
        }

        components_data = {
            "components": [
                {
                    "id": "test_seeker",
                    "abilities": {
                        "SeekerWeaponAbility": {
                            "damage": 50,
                            "range": 2000,
                            "projectile_speed": 200,
                            "turning_rate": 5.0,
                            "reload": 120
                        }
                    }
                }
            ]
        }

        # Setup temp files
        ships_dir = temp_data_dir / "ships"
        with open(ships_dir / "Test_Seeker.json", 'w') as f:
            json.dump(ship_data, f)

        with open(temp_data_dir / "components.json", 'w') as f:
            json.dump(components_data, f)

        metadata = create_test_metadata(
            test_id="SEEK-001",
            name="Seeker Test",
            category="Seeker",
            conditions=["Attacker: Test_Seeker.json"]
        )

        service = ScenarioDataService(data_dir=temp_data_dir)
        service.clear_cache()
        context = service.build_validation_context(metadata)

        assert 'weapon' in context['attacker']
        weapon = context['attacker']['weapon']
        assert weapon['damage'] == 50
        assert weapon['range'] == 2000
        assert weapon['turning_rate'] == 5.0


class TestClearCache:
    """Test cache clearing."""

    def test_clear_cache(self, temp_data_dir):
        """Test that clear_cache resets the components cache."""
        service = ScenarioDataService(data_dir=temp_data_dir)

        # Load cache
        service.load_component_data("test_beam_low_acc_1dmg")
        assert service._components_cache is not None

        # Clear cache
        service.clear_cache()
        assert service._components_cache is None

        # Next load should reload from file
        component = service.load_component_data("test_beam_low_acc_1dmg")
        assert component is not None
        assert service._components_cache is not None

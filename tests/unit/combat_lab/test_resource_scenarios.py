"""
Unit tests for Resource System test scenarios.

Tests that each resource scenario:
- Has correct metadata
- Stores proper results during verification
- Uses ResourceScenario template correctly
- Has appropriate pass criteria
"""
import pytest
from unittest.mock import Mock
import pygame

from combat_lab.scenarios.resource_scenarios import (
    EngineFuelConsumptionScenario,
    EngineFuelDepletionScenario,
    EngineFuelRegenerationScenario,
    BeamEnergyConsumptionScenario,
    BeamEnergyDepletionScenario,
    BeamEnergyRegenerationScenario,
    ProjectileAmmoConsumptionScenario,
    ProjectileAmmoDepletionScenario,
    SeekerAmmoConsumptionScenario
)
from combat_lab.scenarios.templates import ResourceScenario


class TestResourceScenarioMetadata:
    """Tests for resource scenario metadata."""

    def test_fuel_consumption_has_correct_test_id(self):
        """EngineFuelConsumptionScenario should have test_id RESOURCE-001."""
        scenario = EngineFuelConsumptionScenario()
        assert scenario.metadata.test_id == "RESOURCE-001"

    def test_fuel_depletion_has_correct_test_id(self):
        """EngineFuelDepletionScenario should have test_id RESOURCE-002."""
        scenario = EngineFuelDepletionScenario()
        assert scenario.metadata.test_id == "RESOURCE-002"

    def test_fuel_regeneration_has_correct_test_id(self):
        """EngineFuelRegenerationScenario should have test_id RESOURCE-003."""
        scenario = EngineFuelRegenerationScenario()
        assert scenario.metadata.test_id == "RESOURCE-003"

    def test_beam_energy_consumption_has_correct_test_id(self):
        """BeamEnergyConsumptionScenario should have test_id RESOURCE-004."""
        scenario = BeamEnergyConsumptionScenario()
        assert scenario.metadata.test_id == "RESOURCE-004"

    def test_beam_energy_depletion_has_correct_test_id(self):
        """BeamEnergyDepletionScenario should have test_id RESOURCE-005."""
        scenario = BeamEnergyDepletionScenario()
        assert scenario.metadata.test_id == "RESOURCE-005"

    def test_beam_energy_regeneration_has_correct_test_id(self):
        """BeamEnergyRegenerationScenario should have test_id RESOURCE-005a."""
        scenario = BeamEnergyRegenerationScenario()
        assert scenario.metadata.test_id == "RESOURCE-005a"

    def test_projectile_ammo_consumption_has_correct_test_id(self):
        """ProjectileAmmoConsumptionScenario should have test_id RESOURCE-006."""
        scenario = ProjectileAmmoConsumptionScenario()
        assert scenario.metadata.test_id == "RESOURCE-006"

    def test_projectile_ammo_depletion_has_correct_test_id(self):
        """ProjectileAmmoDepletionScenario should have test_id RESOURCE-007."""
        scenario = ProjectileAmmoDepletionScenario()
        assert scenario.metadata.test_id == "RESOURCE-007"

    def test_seeker_ammo_consumption_has_correct_test_id(self):
        """SeekerAmmoConsumptionScenario should have test_id RESOURCE-008."""
        scenario = SeekerAmmoConsumptionScenario()
        assert scenario.metadata.test_id == "RESOURCE-008"


class TestResourceScenarioCategories:
    """Tests for resource scenario categories."""

    def test_fuel_tests_have_fuel_subcategory(self):
        """Fuel tests should have subcategory 'Fuel'."""
        for ScenarioClass in [EngineFuelConsumptionScenario,
                              EngineFuelDepletionScenario,
                              EngineFuelRegenerationScenario]:
            scenario = ScenarioClass()
            assert scenario.metadata.subcategory == "Fuel"
            assert scenario.metadata.category == "Resource System"

    def test_energy_tests_have_energy_subcategory(self):
        """Energy tests should have subcategory 'Energy'."""
        for ScenarioClass in [BeamEnergyConsumptionScenario,
                              BeamEnergyDepletionScenario,
                              BeamEnergyRegenerationScenario]:
            scenario = ScenarioClass()
            assert scenario.metadata.subcategory == "Energy"
            assert scenario.metadata.category == "Resource System"

    def test_ammo_tests_have_ammo_subcategory(self):
        """Ammo tests should have subcategory 'Ammo'."""
        for ScenarioClass in [ProjectileAmmoConsumptionScenario,
                              ProjectileAmmoDepletionScenario,
                              SeekerAmmoConsumptionScenario]:
            scenario = ScenarioClass()
            assert scenario.metadata.subcategory == "Ammo"
            assert scenario.metadata.category == "Resource System"


class TestResourceScenarioMaxTicks:
    """Tests for resource scenario tick limits."""

    def test_fuel_tests_run_for_500_ticks(self):
        """Fuel tests should run for 500 ticks."""
        for ScenarioClass in [EngineFuelConsumptionScenario,
                              EngineFuelDepletionScenario,
                              EngineFuelRegenerationScenario]:
            scenario = ScenarioClass()
            assert scenario.metadata.max_ticks == 500

    def test_energy_tests_run_for_100_ticks(self):
        """Energy tests should run for 100 ticks."""
        for ScenarioClass in [BeamEnergyConsumptionScenario,
                              BeamEnergyDepletionScenario,
                              BeamEnergyRegenerationScenario]:
            scenario = ScenarioClass()
            assert scenario.metadata.max_ticks == 100

    def test_ammo_tests_run_for_100_ticks(self):
        """Ammo tests should run for 100 ticks."""
        for ScenarioClass in [ProjectileAmmoConsumptionScenario,
                              ProjectileAmmoDepletionScenario,
                              SeekerAmmoConsumptionScenario]:
            scenario = ScenarioClass()
            assert scenario.metadata.max_ticks == 100


class TestResourceScenarioTemplateConfig:
    """Tests that scenarios have correct template configuration."""

    def test_fuel_scenarios_use_resource_template(self):
        """Fuel scenarios should extend ResourceScenario."""
        for ScenarioClass in [EngineFuelConsumptionScenario,
                              EngineFuelDepletionScenario,
                              EngineFuelRegenerationScenario]:
            assert issubclass(ScenarioClass, ResourceScenario)

    def test_energy_scenarios_use_resource_template(self):
        """Energy scenarios should extend ResourceScenario."""
        for ScenarioClass in [BeamEnergyConsumptionScenario,
                              BeamEnergyDepletionScenario,
                              BeamEnergyRegenerationScenario]:
            assert issubclass(ScenarioClass, ResourceScenario)

    def test_ammo_scenarios_use_resource_template(self):
        """Ammo scenarios should extend ResourceScenario."""
        for ScenarioClass in [ProjectileAmmoConsumptionScenario,
                              ProjectileAmmoDepletionScenario,
                              SeekerAmmoConsumptionScenario]:
            assert issubclass(ScenarioClass, ResourceScenario)

    def test_fuel_scenarios_track_fuel(self):
        """Fuel scenarios should have resource_type='fuel'."""
        for ScenarioClass in [EngineFuelConsumptionScenario,
                              EngineFuelDepletionScenario,
                              EngineFuelRegenerationScenario]:
            scenario = ScenarioClass()
            assert scenario.resource_type == "fuel"
            assert scenario.thrust_forward is True

    def test_energy_scenarios_track_energy(self):
        """Energy scenarios should have resource_type='energy'."""
        for ScenarioClass in [BeamEnergyConsumptionScenario,
                              BeamEnergyDepletionScenario,
                              BeamEnergyRegenerationScenario]:
            scenario = ScenarioClass()
            assert scenario.resource_type == "energy"
            assert scenario.force_fire is True
            assert scenario.target_ship_file is not None

    def test_ammo_scenarios_track_ammo(self):
        """Ammo scenarios should have resource_type='ammo'."""
        for ScenarioClass in [ProjectileAmmoConsumptionScenario,
                              ProjectileAmmoDepletionScenario,
                              SeekerAmmoConsumptionScenario]:
            scenario = ScenarioClass()
            assert scenario.resource_type == "ammo"
            assert scenario.force_fire is True
            assert scenario.target_ship_file is not None


class TestFuelScenarioResults:
    """Tests for fuel scenario result storage."""

    @pytest.fixture
    def mock_resources(self):
        """Create mock resources object."""
        resources = Mock()
        resources.get_value = Mock(return_value=1000.0)
        return resources

    @pytest.fixture
    def mock_ship(self, mock_resources):
        """Create mock ship with fuel."""
        ship = Mock()
        ship.resources = mock_resources
        ship.position = pygame.math.Vector2(0, 0)
        ship.velocity = pygame.math.Vector2(10, 0)
        ship.current_speed = 10.0
        ship.angle = 0
        ship.is_alive = True
        ship.engine_throttle = 1.0
        ship.layers = {}
        ship.mass = 400.0
        ship.hp = 100
        ship.max_hp = 100
        return ship

    @pytest.fixture
    def mock_battle_engine(self):
        """Create mock battle engine."""
        engine = Mock()
        engine.tick_counter = 500
        return engine

    def test_fuel_consumption_stores_initial_value(self, mock_ship, mock_battle_engine):
        """EngineFuelConsumptionScenario should store initial_value."""
        scenario = EngineFuelConsumptionScenario()
        scenario.ship = mock_ship
        scenario.initial_value = 1000.0
        scenario.start_position = pygame.math.Vector2(0, 0)
        scenario.target = None
        scenario.results = {}

        mock_ship.resources.get_value.return_value = 995.0

        scenario.collect_results(mock_battle_engine)

        assert 'initial_value' in scenario.results
        assert scenario.results['initial_value'] == 1000.0

    def test_fuel_consumption_stores_final_value(self, mock_ship, mock_battle_engine):
        """EngineFuelConsumptionScenario should store final_value."""
        scenario = EngineFuelConsumptionScenario()
        scenario.ship = mock_ship
        scenario.initial_value = 1000.0
        scenario.start_position = pygame.math.Vector2(0, 0)
        scenario.target = None
        scenario.results = {}

        mock_ship.resources.get_value.return_value = 995.0

        scenario.collect_results(mock_battle_engine)

        assert 'final_value' in scenario.results
        assert scenario.results['final_value'] == 995.0

    def test_fuel_consumption_stores_test_id(self):
        """EngineFuelConsumptionScenario stores test_id on init."""
        scenario = EngineFuelConsumptionScenario()
        assert scenario.results['test_id'] == 'RESOURCE-001'


class TestEnergyScenarioResults:
    """Tests for energy scenario result storage."""

    @pytest.fixture
    def mock_resources(self):
        """Create mock resources object."""
        resources = Mock()
        resources.get_value = Mock(return_value=100.0)
        return resources

    @pytest.fixture
    def mock_target(self):
        """Create mock target ship."""
        target = Mock()
        target.position = pygame.math.Vector2(10, 0)
        target.is_alive = True
        target.hp = 100
        target.max_hp = 200
        target.layers = {}
        target.mass = 400.0
        return target

    @pytest.fixture
    def mock_ship(self, mock_resources):
        """Create mock attacker ship."""
        ship = Mock()
        ship.resources = mock_resources
        ship.position = pygame.math.Vector2(0, 0)
        ship.current_speed = 0.0
        ship.angle = 0
        ship.is_alive = True
        ship.layers = {}
        ship.mass = 400.0
        ship.hp = 100
        ship.max_hp = 100
        return ship

    @pytest.fixture
    def mock_battle_engine(self):
        """Create mock battle engine."""
        engine = Mock()
        engine.tick_counter = 100
        return engine

    def test_energy_consumption_stores_shots_fired(self, mock_ship, mock_target, mock_battle_engine):
        """BeamEnergyConsumptionScenario should store shots_fired."""
        scenario = BeamEnergyConsumptionScenario()
        scenario.ship = mock_ship
        scenario.target = mock_target
        scenario.initial_value = 100.0
        scenario.initial_hp = 200
        scenario.start_position = pygame.math.Vector2(0, 0)
        scenario.results = {}

        mock_ship.resources.get_value.return_value = 0.0
        mock_target.hp = 102  # 200 - 98 = 102 (took 98 damage)

        scenario.collect_results(mock_battle_engine)

        assert 'shots_fired' in scenario.results
        assert scenario.results['shots_fired'] == 100

    def test_energy_consumption_stores_damage_dealt(self, mock_ship, mock_target, mock_battle_engine):
        """BeamEnergyConsumptionScenario should store damage_dealt."""
        scenario = BeamEnergyConsumptionScenario()
        scenario.ship = mock_ship
        scenario.target = mock_target
        scenario.initial_value = 100.0
        scenario.initial_hp = 200
        scenario.start_position = pygame.math.Vector2(0, 0)
        scenario.results = {}

        mock_ship.resources.get_value.return_value = 0.0
        mock_target.hp = 102  # 200 - 98 = 102 (took 98 damage)

        scenario.collect_results(mock_battle_engine)

        assert 'damage_dealt' in scenario.results
        assert scenario.results['damage_dealt'] == 98


class TestAmmoScenarioResults:
    """Tests for ammo scenario result storage."""

    @pytest.fixture
    def mock_resources(self):
        """Create mock resources object."""
        resources = Mock()
        resources.get_value = Mock(return_value=100.0)
        return resources

    @pytest.fixture
    def mock_target(self):
        """Create mock target ship."""
        target = Mock()
        target.position = pygame.math.Vector2(100, 0)
        target.is_alive = True
        target.hp = 100
        target.max_hp = 200
        target.layers = {}
        target.mass = 400.0
        return target

    @pytest.fixture
    def mock_ship(self, mock_resources):
        """Create mock attacker ship."""
        ship = Mock()
        ship.resources = mock_resources
        ship.position = pygame.math.Vector2(0, 0)
        ship.current_speed = 0.0
        ship.angle = 0
        ship.is_alive = True
        ship.layers = {}
        ship.mass = 400.0
        ship.hp = 100
        ship.max_hp = 100
        return ship

    @pytest.fixture
    def mock_battle_engine(self):
        """Create mock battle engine."""
        engine = Mock()
        engine.tick_counter = 100
        return engine

    def test_projectile_consumption_stores_initial_value(self, mock_ship, mock_target, mock_battle_engine):
        """ProjectileAmmoConsumptionScenario should store initial_value."""
        scenario = ProjectileAmmoConsumptionScenario()
        scenario.ship = mock_ship
        scenario.target = mock_target
        scenario.initial_value = 100.0
        scenario.initial_hp = 200
        scenario.start_position = pygame.math.Vector2(0, 0)
        scenario.results = {}

        mock_ship.resources.get_value.return_value = 0.0
        mock_target.hp = 105  # 200 - 95 = 105 (took 95 damage)

        scenario.collect_results(mock_battle_engine)

        assert 'initial_value' in scenario.results
        assert scenario.results['initial_value'] == 100.0

    def test_seeker_consumption_stores_launches(self, mock_ship, mock_target, mock_battle_engine):
        """SeekerAmmoConsumptionScenario should store launches."""
        scenario = SeekerAmmoConsumptionScenario()
        scenario.ship = mock_ship
        scenario.target = mock_target
        scenario.initial_value = 100.0
        scenario.initial_hp = 200
        scenario.start_position = pygame.math.Vector2(0, 0)
        scenario.results = {}

        mock_ship.resources.get_value.return_value = 0.0

        scenario.collect_results(mock_battle_engine)

        assert 'launches' in scenario.results
        assert scenario.results['launches'] == 100


class TestResourceScenarioPassCriteria:
    """Tests that scenarios have pass criteria defined."""

    def test_all_scenarios_have_pass_criteria(self):
        """All resource scenarios should have pass_criteria in metadata."""
        scenarios = [
            EngineFuelConsumptionScenario(),
            EngineFuelDepletionScenario(),
            EngineFuelRegenerationScenario(),
            BeamEnergyConsumptionScenario(),
            BeamEnergyDepletionScenario(),
            BeamEnergyRegenerationScenario(),
            ProjectileAmmoConsumptionScenario(),
            ProjectileAmmoDepletionScenario(),
            SeekerAmmoConsumptionScenario()
        ]

        for scenario in scenarios:
            assert scenario.metadata.pass_criteria, (
                f"{scenario.__class__.__name__} missing pass_criteria"
            )

    def test_all_scenarios_have_expected_outcome(self):
        """All resource scenarios should have expected_outcome in metadata."""
        scenarios = [
            EngineFuelConsumptionScenario(),
            EngineFuelDepletionScenario(),
            EngineFuelRegenerationScenario(),
            BeamEnergyConsumptionScenario(),
            BeamEnergyDepletionScenario(),
            BeamEnergyRegenerationScenario(),
            ProjectileAmmoConsumptionScenario(),
            ProjectileAmmoDepletionScenario(),
            SeekerAmmoConsumptionScenario()
        ]

        for scenario in scenarios:
            assert scenario.metadata.expected_outcome, (
                f"{scenario.__class__.__name__} missing expected_outcome"
            )


class TestResourceScenarioTags:
    """Tests that scenarios have appropriate tags."""

    def test_fuel_scenarios_have_fuel_tag(self):
        """Fuel scenarios should have 'fuel' in tags."""
        scenarios = [
            EngineFuelConsumptionScenario(),
            EngineFuelDepletionScenario(),
            EngineFuelRegenerationScenario()
        ]

        for scenario in scenarios:
            assert 'fuel' in scenario.metadata.tags

    def test_energy_scenarios_have_energy_tag(self):
        """Energy scenarios should have 'energy' in tags."""
        scenarios = [
            BeamEnergyConsumptionScenario(),
            BeamEnergyDepletionScenario(),
            BeamEnergyRegenerationScenario()
        ]

        for scenario in scenarios:
            assert 'energy' in scenario.metadata.tags

    def test_ammo_scenarios_have_ammo_tag(self):
        """Ammo scenarios should have 'ammo' in tags."""
        scenarios = [
            ProjectileAmmoConsumptionScenario(),
            ProjectileAmmoDepletionScenario(),
            SeekerAmmoConsumptionScenario()
        ]

        for scenario in scenarios:
            assert 'ammo' in scenario.metadata.tags

"""
Unit tests for Resource System test scenarios.

Tests that each resource scenario:
- Has correct metadata
- Stores proper results during verification
- Uses _load_ship() for ship loading
- Has appropriate pass criteria
"""
import pytest
from unittest.mock import Mock
import pygame

from simulation_tests.scenarios.resource_scenarios import (
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
        ship.layers = {}  # Empty layers dict for validation
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

    def test_fuel_consumption_stores_initial_fuel(self, mock_ship, mock_battle_engine):
        """EngineFuelConsumptionScenario should store initial_fuel."""
        scenario = EngineFuelConsumptionScenario()
        scenario.ship = mock_ship
        scenario.initial_fuel = 1000.0
        scenario.initial_velocity = 0.0
        scenario.start_position = pygame.math.Vector2(0, 0)
        scenario.results = {}

        # Mock get_value to return final fuel
        mock_ship.resources.get_value.return_value = 995.0

        scenario.verify(mock_battle_engine)

        assert 'initial_fuel' in scenario.results
        assert scenario.results['initial_fuel'] == 1000.0

    def test_fuel_consumption_stores_final_fuel(self, mock_ship, mock_battle_engine):
        """EngineFuelConsumptionScenario should store final_fuel."""
        scenario = EngineFuelConsumptionScenario()
        scenario.ship = mock_ship
        scenario.initial_fuel = 1000.0
        scenario.initial_velocity = 0.0
        scenario.start_position = pygame.math.Vector2(0, 0)
        scenario.results = {}

        mock_ship.resources.get_value.return_value = 995.0

        scenario.verify(mock_battle_engine)

        assert 'final_fuel' in scenario.results
        assert scenario.results['final_fuel'] == 995.0

    def test_fuel_consumption_stores_test_id(self, mock_ship, mock_battle_engine):
        """EngineFuelConsumptionScenario should store test_id."""
        scenario = EngineFuelConsumptionScenario()
        scenario.ship = mock_ship
        scenario.initial_fuel = 1000.0
        scenario.initial_velocity = 0.0
        scenario.start_position = pygame.math.Vector2(0, 0)
        scenario.results = {}

        mock_ship.resources.get_value.return_value = 995.0

        scenario.verify(mock_battle_engine)

        assert 'test_id' in scenario.results
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
        target.layers = {}  # Empty layers dict for validation
        target.mass = 400.0
        return target

    @pytest.fixture
    def mock_ship(self, mock_resources):
        """Create mock attacker ship."""
        ship = Mock()
        ship.resources = mock_resources
        ship.position = pygame.math.Vector2(0, 0)
        ship.angle = 0
        ship.is_alive = True
        ship.weapon_systems = Mock()
        ship.weapon_systems.fire_counts = {'test_beam_rapid_1dmg': 100}
        ship.weapon_systems.hit_counts = {'test_beam_rapid_1dmg': 98}
        ship.weapon_systems.total_damage_dealt = 98
        ship.layers = {}  # Empty layers dict for validation
        ship.mass = 400.0
        ship.hp = 100
        ship.max_hp = 100
        return ship

    @pytest.fixture
    def mock_battle_engine(self, mock_target):
        """Create mock battle engine."""
        engine = Mock()
        engine.tick_counter = 100
        return engine

    def test_energy_consumption_stores_shots_fired(self, mock_ship, mock_target, mock_battle_engine):
        """BeamEnergyConsumptionScenario should store shots_fired."""
        scenario = BeamEnergyConsumptionScenario()
        scenario.attacker = mock_ship
        scenario.target = mock_target
        scenario.initial_energy = 100.0
        scenario.initial_hp = 200  # Target's initial HP
        scenario.results = {}

        mock_ship.resources.get_value.return_value = 0.0
        mock_target.hp = 102  # 200 - 98 = 102 (took 98 damage)

        scenario.verify(mock_battle_engine)

        assert 'shots_fired' in scenario.results
        assert scenario.results['shots_fired'] == 100

    def test_energy_consumption_stores_damage_dealt(self, mock_ship, mock_target, mock_battle_engine):
        """BeamEnergyConsumptionScenario should store damage_dealt."""
        scenario = BeamEnergyConsumptionScenario()
        scenario.attacker = mock_ship
        scenario.target = mock_target
        scenario.initial_energy = 100.0
        scenario.initial_hp = 200  # Target's initial HP
        scenario.results = {}

        mock_ship.resources.get_value.return_value = 0.0
        mock_target.hp = 102  # 200 - 98 = 102 (took 98 damage)

        scenario.verify(mock_battle_engine)

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
        target.layers = {}  # Empty layers dict for validation
        target.mass = 400.0
        return target

    @pytest.fixture
    def mock_ship(self, mock_resources):
        """Create mock attacker ship."""
        ship = Mock()
        ship.resources = mock_resources
        ship.position = pygame.math.Vector2(0, 0)
        ship.angle = 0
        ship.is_alive = True
        ship.weapon_systems = Mock()
        ship.weapon_systems.fire_counts = {'test_proj_rapid': 100}
        ship.weapon_systems.hit_counts = {'test_proj_rapid': 95}
        ship.weapon_systems.total_damage_dealt = 95
        ship.layers = {}  # Empty layers dict for validation
        ship.mass = 400.0
        ship.hp = 100
        ship.max_hp = 100
        return ship

    @pytest.fixture
    def mock_battle_engine(self, mock_target):
        """Create mock battle engine."""
        engine = Mock()
        engine.tick_counter = 100
        return engine

    def test_projectile_consumption_stores_initial_ammo(self, mock_ship, mock_target, mock_battle_engine):
        """ProjectileAmmoConsumptionScenario should store initial_ammo."""
        scenario = ProjectileAmmoConsumptionScenario()
        scenario.attacker = mock_ship
        scenario.target = mock_target
        scenario.initial_ammo = 100.0
        scenario.initial_hp = 200  # Target's initial HP
        scenario.results = {}

        mock_ship.resources.get_value.return_value = 0.0
        mock_target.hp = 105  # 200 - 95 = 105 (took 95 damage)

        scenario.verify(mock_battle_engine)

        assert 'initial_ammo' in scenario.results
        assert scenario.results['initial_ammo'] == 100.0

    def test_seeker_consumption_stores_launches(self, mock_ship, mock_target, mock_battle_engine):
        """SeekerAmmoConsumptionScenario should store launches."""
        scenario = SeekerAmmoConsumptionScenario()
        scenario.attacker = mock_ship
        scenario.target = mock_target
        scenario.initial_ammo = 100.0
        scenario.results = {}

        # Mock seeker fire counts
        mock_ship.weapon_systems.fire_counts = {'test_seeker_rapid': 100}
        mock_ship.resources.get_value.return_value = 0.0

        scenario.verify(mock_battle_engine)

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

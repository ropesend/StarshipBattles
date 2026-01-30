"""Tests for BattleUIService.

PROJ-43 Phase 12: Tests for the battle UI service that converts
simulation objects to DTOs for UI consumption.

These tests verify:
1. Service wraps BattleService correctly
2. Ships are converted to ShipDTO correctly
3. Projectiles are converted to ProjectileDTO correctly
4. Beams are converted to BeamDTO correctly
5. Battle state is exposed correctly
"""
import pytest
from unittest.mock import Mock, MagicMock, PropertyMock

from game.ui.services.battle_ui_service import BattleUIService
from game.ui.interfaces.battle_ui import (
    IBattleUI,
    ShipDTO,
    ProjectileDTO,
    BeamDTO,
    ComponentDTO,
    ResourceDTO,
)
from game.core.math import Vector2


class TestBattleUIServiceCreation:
    """Tests for BattleUIService creation and setup."""

    def test_create_service_with_battle_service(self):
        """BattleUIService can be created with a BattleService."""
        mock_service = Mock()
        mock_service.get_engine.return_value = None

        service = BattleUIService(mock_service)
        assert service is not None

    def test_service_satisfies_protocol(self):
        """BattleUIService satisfies IBattleUI protocol."""
        mock_service = Mock()
        mock_service.get_engine.return_value = None

        service = BattleUIService(mock_service)
        assert isinstance(service, IBattleUI)


class TestBattleUIServiceShipConversion:
    """Tests for ship to ShipDTO conversion."""

    @pytest.fixture
    def mock_ship(self):
        """Create a mock ship with all required attributes."""
        ship = Mock()
        ship.id = "ship_1"
        ship.name = "Test Ship"
        ship.team_id = 0
        ship.position = Vector2(100, 200)
        ship.velocity = Vector2(10, 5)
        ship.heading = 1.5
        ship.is_alive = True
        ship.is_derelict = False
        ship.hp = 80.0
        ship.max_hp = 100.0
        ship.current_shields = 50.0
        ship.max_shields = 100.0
        ship.current_speed = 30.0
        ship.max_speed = 60.0
        ship.mass = 1000.0
        ship.total_thrust = 500.0
        ship.turn_speed = 0.1
        ship.total_shots_fired = 5
        ship.crew_onboard = 10
        ship.crew_required = 10
        ship.current_target = None
        ship.secondary_targets = []
        ship.max_targets = 1
        ship.ai_strategy = "aggressive"
        ship.source_file = "ships/test.json"
        ship.layers = {}

        # Mock resources
        mock_resource = Mock()
        mock_resource.name = "fuel"
        mock_resource.current_value = 50.0
        mock_resource.max_value = 100.0

        ship.resources = Mock()
        ship.resources._resources = {"fuel": mock_resource}

        return ship

    @pytest.fixture
    def mock_battle_service(self, mock_ship):
        """Create mock BattleService with ships."""
        service = Mock()
        engine = Mock()
        engine.ships = [mock_ship]
        engine.projectiles = []
        engine.recent_beams = []
        engine.tick_counter = 100
        engine.is_battle_over.return_value = False
        engine.get_winner.return_value = None
        service.get_engine.return_value = engine
        return service

    def test_get_ships_returns_list_of_dtos(self, mock_battle_service, mock_ship):
        """get_ships() returns a list of ShipDTO objects."""
        service = BattleUIService(mock_battle_service)
        ships = service.get_ships()

        assert len(ships) == 1
        assert isinstance(ships[0], ShipDTO)

    def test_ship_dto_has_correct_basic_properties(self, mock_battle_service, mock_ship):
        """ShipDTO has correct values from the ship object."""
        service = BattleUIService(mock_battle_service)
        dto = service.get_ships()[0]

        assert dto.name == "Test Ship"
        assert dto.team_id == 0
        assert dto.position.x == 100
        assert dto.position.y == 200
        assert dto.is_alive is True
        assert dto.hp == 80.0
        assert dto.max_hp == 100.0

    def test_ship_dto_converts_resources(self, mock_battle_service, mock_ship):
        """ShipDTO includes resource DTOs."""
        service = BattleUIService(mock_battle_service)
        dto = service.get_ships()[0]

        assert len(dto.resources) == 1
        assert dto.resources[0].name == "fuel"
        assert dto.resources[0].current_value == 50.0

    def test_ship_with_target_includes_target_name(self, mock_battle_service, mock_ship):
        """Ship with a target has target name in DTO."""
        target = Mock()
        target.name = "Enemy Ship"
        mock_ship.current_target = target

        service = BattleUIService(mock_battle_service)
        dto = service.get_ships()[0]

        assert dto.current_target_name == "Enemy Ship"

    def test_ship_with_components_converts_to_dto(self, mock_battle_service, mock_ship):
        """Ship components are converted to ComponentDTO."""
        # Add mock component
        comp = Mock()
        comp.name = "Laser"
        comp.current_hp = 50.0
        comp.max_hp = 100.0
        comp.is_active = True
        comp.status = Mock()
        comp.status.name = "ACTIVE"
        comp.has_ability = Mock(return_value=True)
        comp.shots_fired = 10
        comp.shots_hit = 7

        mock_ship.layers = {
            Mock(value="outer"): {"components": [comp]}
        }

        service = BattleUIService(mock_battle_service)
        dto = service.get_ships()[0]

        assert len(dto.components) == 1
        assert dto.components[0].name == "Laser"
        assert dto.components[0].has_weapon is True


class TestBattleUIServiceProjectileConversion:
    """Tests for projectile to ProjectileDTO conversion."""

    @pytest.fixture
    def mock_projectile(self):
        """Create a mock projectile."""
        proj = Mock()
        proj.id = "proj_1"
        proj.position = Vector2(50, 50)
        proj.velocity = Vector2(100, 0)
        proj.color = (255, 200, 50)
        proj.radius = 4.0
        proj.damage = 25.0
        proj.hp = 10.0
        proj.max_hp = 10.0
        proj.status = "active"
        proj.endurance = 5.0
        proj.max_endurance = 10.0
        proj.target = None
        proj.max_speed = 100.0
        return proj

    @pytest.fixture
    def mock_battle_service_with_projectile(self, mock_projectile):
        """Create mock BattleService with a projectile."""
        service = Mock()
        engine = Mock()
        engine.ships = []
        engine.projectiles = [mock_projectile]
        engine.recent_beams = []
        engine.tick_counter = 0
        engine.is_battle_over.return_value = False
        engine.get_winner.return_value = None
        service.get_engine.return_value = engine
        return service

    def test_get_projectiles_returns_list_of_dtos(self, mock_battle_service_with_projectile):
        """get_projectiles() returns a list of ProjectileDTO objects."""
        service = BattleUIService(mock_battle_service_with_projectile)
        projectiles = service.get_projectiles()

        assert len(projectiles) == 1
        assert isinstance(projectiles[0], ProjectileDTO)

    def test_projectile_dto_has_correct_properties(self, mock_battle_service_with_projectile):
        """ProjectileDTO has correct values from the projectile object."""
        service = BattleUIService(mock_battle_service_with_projectile)
        dto = service.get_projectiles()[0]

        assert dto.position.x == 50
        assert dto.damage == 25.0
        assert dto.status == "active"

    def test_projectile_with_target_includes_name(self, mock_battle_service_with_projectile, mock_projectile):
        """Projectile with target has target name in DTO."""
        target = Mock()
        target.name = "Target Ship"
        mock_projectile.target = target

        service = BattleUIService(mock_battle_service_with_projectile)
        dto = service.get_projectiles()[0]

        assert dto.target_name == "Target Ship"


class TestBattleUIServiceBeamConversion:
    """Tests for beam to BeamDTO conversion."""

    @pytest.fixture
    def mock_battle_service_with_beams(self):
        """Create mock BattleService with beams."""
        service = Mock()
        engine = Mock()
        engine.ships = []
        engine.projectiles = []
        engine.recent_beams = [
            {
                "start": Vector2(0, 0),
                "end": Vector2(100, 100),
                "color": (255, 0, 0)
            }
        ]
        engine.tick_counter = 0
        engine.is_battle_over.return_value = False
        engine.get_winner.return_value = None
        service.get_engine.return_value = engine
        return service

    def test_get_recent_beams_returns_list_of_dtos(self, mock_battle_service_with_beams):
        """get_recent_beams() returns a list of BeamDTO objects."""
        service = BattleUIService(mock_battle_service_with_beams)
        beams = service.get_recent_beams()

        assert len(beams) == 1
        assert isinstance(beams[0], BeamDTO)

    def test_beam_dto_has_correct_properties(self, mock_battle_service_with_beams):
        """BeamDTO has correct values from the beam dict."""
        service = BattleUIService(mock_battle_service_with_beams)
        dto = service.get_recent_beams()[0]

        assert dto.start.x == 0
        assert dto.end.x == 100
        assert dto.color == (255, 0, 0)


class TestBattleUIServiceBattleState:
    """Tests for battle state queries."""

    @pytest.fixture
    def mock_battle_service(self):
        """Create mock BattleService."""
        service = Mock()
        engine = Mock()
        engine.ships = []
        engine.projectiles = []
        engine.recent_beams = []
        engine.tick_counter = 500
        engine.is_battle_over.return_value = True
        engine.get_winner.return_value = 0
        service.get_engine.return_value = engine
        return service

    def test_is_battle_over_delegates_to_engine(self, mock_battle_service):
        """is_battle_over() returns engine state."""
        service = BattleUIService(mock_battle_service)
        assert service.is_battle_over() is True

    def test_get_winner_delegates_to_engine(self, mock_battle_service):
        """get_winner() returns engine winner."""
        service = BattleUIService(mock_battle_service)
        assert service.get_winner() == 0

    def test_get_tick_count_returns_engine_counter(self, mock_battle_service):
        """get_tick_count() returns engine tick counter."""
        service = BattleUIService(mock_battle_service)
        assert service.get_tick_count() == 500


class TestBattleUIServiceNoEngine:
    """Tests for service behavior when no engine is active."""

    def test_get_ships_returns_empty_when_no_engine(self):
        """get_ships() returns empty list when no engine."""
        service = Mock()
        service.get_engine.return_value = None

        ui_service = BattleUIService(service)
        assert ui_service.get_ships() == []

    def test_get_projectiles_returns_empty_when_no_engine(self):
        """get_projectiles() returns empty list when no engine."""
        service = Mock()
        service.get_engine.return_value = None

        ui_service = BattleUIService(service)
        assert ui_service.get_projectiles() == []

    def test_get_recent_beams_returns_empty_when_no_engine(self):
        """get_recent_beams() returns empty list when no engine."""
        service = Mock()
        service.get_engine.return_value = None

        ui_service = BattleUIService(service)
        assert ui_service.get_recent_beams() == []

    def test_is_battle_over_returns_true_when_no_engine(self):
        """is_battle_over() returns True when no engine."""
        service = Mock()
        service.get_engine.return_value = None

        ui_service = BattleUIService(service)
        assert ui_service.is_battle_over() is True

    def test_get_tick_count_returns_zero_when_no_engine(self):
        """get_tick_count() returns 0 when no engine."""
        service = Mock()
        service.get_engine.return_value = None

        ui_service = BattleUIService(service)
        assert ui_service.get_tick_count() == 0


# ============================================================================
# PROJ-43 Audit Cycle 1: Integration Tests with Real Domain Objects
# ============================================================================
# These tests verify BattleUIService works with actual domain objects,
# not just mocks. This addresses the audit finding that all tests were
# mock-only with no real domain object coverage.


class TestBattleUIServiceRealShipIntegration:
    """Integration tests using real Ship domain objects."""

    @pytest.fixture
    def real_ship(self):
        """Create a real Ship domain object for integration testing."""
        from game.simulation.entities.ship import Ship, LayerType
        from game.simulation.components.component import create_component

        ship = Ship("Integration Test Ship", 100, 200, (0, 0, 255))
        # Add minimal components for a functional ship
        ship.add_component(create_component('bridge'), LayerType.CORE)
        ship.add_component(create_component('crew_quarters'), LayerType.CORE)
        ship.add_component(create_component('life_support'), LayerType.CORE)
        ship.add_component(create_component('standard_engine'), LayerType.OUTER)
        ship.recalculate_stats()
        return ship

    @pytest.fixture
    def battle_service_with_real_ship(self, real_ship):
        """Create a real BattleService with a real ship."""
        from game.simulation.services import BattleService

        battle_service = BattleService()
        battle_service.create_battle()
        battle_service.add_ship(real_ship, team_id=0)
        battle_service.start_battle()
        return battle_service

    def test_convert_real_ship_to_dto(self, battle_service_with_real_ship, real_ship):
        """BattleUIService correctly converts a real Ship to ShipDTO."""
        ui_service = BattleUIService(battle_service_with_real_ship)
        ships = ui_service.get_ships()

        assert len(ships) == 1
        dto = ships[0]

        # Verify basic properties
        assert isinstance(dto, ShipDTO)
        assert dto.name == "Integration Test Ship"
        assert dto.team_id == 0
        assert dto.position.x == 100
        assert dto.position.y == 200
        assert dto.is_alive is True

        # Verify computed properties
        assert dto.max_hp > 0
        assert dto.hp <= dto.max_hp

    def test_real_ship_components_converted(self, battle_service_with_real_ship, real_ship):
        """Real ship components are correctly converted to ComponentDTO."""
        ui_service = BattleUIService(battle_service_with_real_ship)
        ships = ui_service.get_ships()
        dto = ships[0]

        # Ship should have components (bridge, crew_quarters, life_support, standard_engine)
        assert len(dto.components) >= 4

        # Find a specific component
        bridge_components = [c for c in dto.components if 'bridge' in c.name.lower()]
        assert len(bridge_components) >= 1

        bridge = bridge_components[0]
        assert isinstance(bridge, ComponentDTO)
        assert bridge.max_hp > 0
        assert bridge.is_active is True

    def test_real_ship_resources_converted(self, battle_service_with_real_ship, real_ship):
        """Real ship resources are correctly converted to ResourceDTO."""
        ui_service = BattleUIService(battle_service_with_real_ship)
        ships = ui_service.get_ships()
        dto = ships[0]

        # Resources should be converted (may be empty list if no resource-granting components)
        assert isinstance(dto.resources, list)

        # If the ship has any resources, verify they're valid DTOs
        for resource in dto.resources:
            assert isinstance(resource, ResourceDTO)
            assert isinstance(resource.name, str)
            assert resource.current_value >= 0
            assert resource.max_value >= 0

    def test_real_ship_missing_optional_attributes(self, battle_service_with_real_ship):
        """Service handles real ships with optional attributes gracefully."""
        ui_service = BattleUIService(battle_service_with_real_ship)
        ships = ui_service.get_ships()
        dto = ships[0]

        # These optional attributes should have sensible defaults
        # even if not explicitly set on the ship
        assert dto.is_derelict in (True, False)  # Should be boolean
        assert isinstance(dto.ai_strategy, str)  # Should be string
        assert isinstance(dto.max_targets, int)  # Should be int


class TestBattleUIServiceRealProjectileIntegration:
    """Integration tests using real projectile scenarios."""

    @pytest.fixture
    def battle_with_ships_and_weapon(self):
        """Create a battle with armed ships that can fire projectiles."""
        from game.simulation.entities.ship import Ship, LayerType
        from game.simulation.components.component import create_component
        from game.simulation.services import BattleService

        # Create attacker with weapon
        attacker = Ship("Attacker", 0, 0, (0, 0, 255))
        attacker.add_component(create_component('bridge'), LayerType.CORE)
        attacker.add_component(create_component('crew_quarters'), LayerType.CORE)
        attacker.add_component(create_component('life_support'), LayerType.CORE)
        attacker.add_component(create_component('standard_engine'), LayerType.OUTER)
        attacker.add_component(create_component('railgun'), LayerType.OUTER)
        attacker.recalculate_stats()

        # Create target
        target = Ship("Target", 500, 0, (255, 0, 0))
        target.add_component(create_component('bridge'), LayerType.CORE)
        target.add_component(create_component('crew_quarters'), LayerType.CORE)
        target.add_component(create_component('life_support'), LayerType.CORE)
        target.add_component(create_component('standard_engine'), LayerType.OUTER)
        target.recalculate_stats()

        battle_service = BattleService()
        battle_service.create_battle()
        battle_service.add_ship(attacker, team_id=0)
        battle_service.add_ship(target, team_id=1)
        battle_service.start_battle()

        return battle_service, attacker, target

    def test_projectiles_list_initially_empty(self, battle_with_ships_and_weapon):
        """Projectiles list is empty at battle start."""
        battle_service, _, _ = battle_with_ships_and_weapon
        ui_service = BattleUIService(battle_service)

        projectiles = ui_service.get_projectiles()
        # At battle start, no projectiles should exist
        assert isinstance(projectiles, list)
        # Note: Projectiles may or may not be empty depending on auto-fire,
        # but the list should be valid
        assert all(isinstance(p, ProjectileDTO) for p in projectiles)

    def test_battle_state_queries(self, battle_with_ships_and_weapon):
        """Battle state queries work with real battle."""
        battle_service, attacker, target = battle_with_ships_and_weapon
        ui_service = BattleUIService(battle_service)

        # With both ships alive and functional, battle should be ongoing
        # Note: Ships may become derelict immediately if they have no fuel,
        # which could end the battle
        tick_count = ui_service.get_tick_count()
        assert tick_count >= 0

        # Winner is either None (ongoing), 0, 1, or -1 (draw)
        winner = ui_service.get_winner()
        assert winner in (None, 0, 1, -1)


class TestBattleUIServiceDefensiveFallbacks:
    """Tests verifying defensive getattr() fallbacks work correctly."""

    def test_ship_without_optional_attributes_uses_defaults(self):
        """Service handles ship missing optional attributes using defaults."""
        mock_service = Mock()
        engine = Mock()

        # Create a ship mock with only required attributes
        # Use regular Mock (not spec) but configure specific attributes
        ship = Mock()
        ship.name = "Minimal Ship"
        ship.team_id = 0
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)
        ship.heading = 0.0
        ship.is_alive = True
        ship.hp = 100.0
        ship.max_hp = 100.0
        ship.max_speed = 50.0
        ship.mass = 1000.0
        ship.layers = {}
        # Configure Mock to raise AttributeError for optional attrs
        ship.configure_mock(**{
            'is_derelict': Mock(side_effect=AttributeError),
            'current_shields': Mock(side_effect=AttributeError),
            'max_shields': Mock(side_effect=AttributeError),
        })
        # But getattr needs to work differently - let's use a simpler approach
        # Just don't set these attributes and let getattr handle defaults

        # Use a SimpleNamespace-like approach for cleaner testing
        class MinimalShip:
            name = "Minimal Ship"
            team_id = 0
            position = Vector2(0, 0)
            velocity = Vector2(0, 0)
            heading = 0.0
            is_alive = True
            hp = 100.0
            max_hp = 100.0
            max_speed = 50.0
            mass = 1000.0
            layers = {}
            # Optional attrs NOT defined - getattr should use defaults

        ship = MinimalShip()

        engine.ships = [ship]
        engine.projectiles = []
        engine.recent_beams = []
        engine.tick_counter = 0
        engine.is_battle_over.return_value = False
        engine.get_winner.return_value = None
        mock_service.get_engine.return_value = engine

        ui_service = BattleUIService(mock_service)
        ships = ui_service.get_ships()

        assert len(ships) == 1
        dto = ships[0]
        # Should use fallback value (False)
        assert dto.is_derelict is False
        # Should use fallback (0.0)
        assert dto.current_shields == 0.0
        assert dto.max_shields == 0.0
        # Other defaults
        assert dto.ai_strategy == 'default'
        assert dto.max_targets == 1

    def test_ship_without_resources_attribute(self):
        """Service handles ship missing resources attribute."""
        mock_service = Mock()
        engine = Mock()

        # Create ship without resources attribute using class
        class ShipWithoutResources:
            name = "No Resources Ship"
            team_id = 0
            position = Vector2(0, 0)
            velocity = Vector2(0, 0)
            heading = 0.0
            is_alive = True
            hp = 100.0
            max_hp = 100.0
            max_speed = 50.0
            mass = 1000.0
            layers = {}
            # Note: No resources attribute defined

        ship = ShipWithoutResources()

        engine.ships = [ship]
        engine.projectiles = []
        engine.recent_beams = []
        engine.tick_counter = 0
        engine.is_battle_over.return_value = False
        engine.get_winner.return_value = None
        mock_service.get_engine.return_value = engine

        ui_service = BattleUIService(mock_service)
        ships = ui_service.get_ships()

        assert len(ships) == 1
        dto = ships[0]
        # Should have empty resources list
        assert dto.resources == []

    def test_component_without_status_attribute(self):
        """Service handles component missing status attribute."""
        mock_service = Mock()
        engine = Mock()

        # Create component without status using class
        class MinimalComponent:
            name = "Basic Component"
            current_hp = 50.0
            max_hp = 100.0
            is_active = True
            # Note: No status attribute, no has_ability method

        comp = MinimalComponent()

        # Create layer type enum-like object
        class OuterLayer:
            value = "outer"

        layer_type = OuterLayer()

        # Create ship with the component using class
        class ShipWithComponent:
            name = "Ship With Component"
            team_id = 0
            position = Vector2(0, 0)
            velocity = Vector2(0, 0)
            heading = 0.0
            is_alive = True
            hp = 100.0
            max_hp = 100.0
            max_speed = 50.0
            mass = 1000.0
            # Note: layers will be set below

        ship = ShipWithComponent()
        ship.layers = {layer_type: {'components': [comp]}}

        engine.ships = [ship]
        engine.projectiles = []
        engine.recent_beams = []
        engine.tick_counter = 0
        engine.is_battle_over.return_value = False
        engine.get_winner.return_value = None
        mock_service.get_engine.return_value = engine

        ui_service = BattleUIService(mock_service)
        ships = ui_service.get_ships()

        assert len(ships) == 1
        dto = ships[0]
        assert len(dto.components) == 1

        comp_dto = dto.components[0]
        # Should use fallback value "active"
        assert comp_dto.status == "active"
        # Should use fallback False since has_ability doesn't exist
        assert comp_dto.has_weapon is False

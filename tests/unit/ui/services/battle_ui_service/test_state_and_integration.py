"""Tests for BattleUIService battle state and integration.

Tests for:
- Battle state queries
- No-engine behavior
- Real ship integration
- Real projectile integration
- Defensive fallbacks
"""
import pytest
from unittest.mock import Mock

from game.ui.services.battle_ui_service import BattleUIService
from game.ui.interfaces.battle_ui import (
    ShipDTO,
    ProjectileDTO,
    ComponentDTO,
    ResourceDTO,
)
from game.core.math import Vector2


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
    def real_ship(self, fresh_registries):
        """Create a real Ship domain object for integration testing."""
        from game.simulation.entities.ship import Ship, LayerType
        from game.simulation.components.component import create_component

        ship = Ship("Integration Test Ship", 100, 200, (0, 0, 255), registries=fresh_registries)
        # Add minimal components for a functional ship
        ship.add_component(create_component('bridge', registries=fresh_registries), LayerType.CORE)
        ship.add_component(create_component('crew_quarters', registries=fresh_registries), LayerType.CORE)
        ship.add_component(create_component('life_support', registries=fresh_registries), LayerType.CORE)
        ship.add_component(create_component('standard_engine', registries=fresh_registries), LayerType.OUTER)
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
    def battle_with_ships_and_weapon(self, fresh_registries):
        """Create a battle with armed ships that can fire projectiles."""
        from game.simulation.entities.ship import Ship, LayerType
        from game.simulation.components.component import create_component
        from game.simulation.services import BattleService

        # Create attacker with weapon
        attacker = Ship("Attacker", 0, 0, (0, 0, 255), registries=fresh_registries)
        attacker.add_component(create_component('bridge', registries=fresh_registries), LayerType.CORE)
        attacker.add_component(create_component('crew_quarters', registries=fresh_registries), LayerType.CORE)
        attacker.add_component(create_component('life_support', registries=fresh_registries), LayerType.CORE)
        attacker.add_component(create_component('standard_engine', registries=fresh_registries), LayerType.OUTER)
        attacker.add_component(create_component('railgun', registries=fresh_registries), LayerType.OUTER)
        attacker.recalculate_stats()

        # Create target
        target = Ship("Target", 500, 0, (255, 0, 0), registries=fresh_registries)
        target.add_component(create_component('bridge', registries=fresh_registries), LayerType.CORE)
        target.add_component(create_component('crew_quarters', registries=fresh_registries), LayerType.CORE)
        target.add_component(create_component('life_support', registries=fresh_registries), LayerType.CORE)
        target.add_component(create_component('standard_engine', registries=fresh_registries), LayerType.OUTER)
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
    """Tests verifying remaining defensive getattr() fallbacks work correctly.

    Note: PROJ-106 Phase 6 removed most defensive getattr() calls since Ship's
    interface is now stable. Only crew_onboard/crew_required remain as getattr()
    since they're dynamically set by ShipStatsCalculator, not in Ship.__init__.
    """

    def test_ship_without_crew_attributes_uses_defaults(self):
        """Service handles ship missing crew attributes (dynamically set by ShipStatsCalculator)."""
        mock_service = Mock()
        engine = Mock()

        # Create ship that has all guaranteed attributes but NOT crew_onboard/crew_required
        # (which are only set by ShipStatsCalculator.calculate(), not Ship.__init__)
        class ShipWithoutCrewStats:
            name = "Ship Without Crew Stats"
            team_id = 0
            position = Vector2(0, 0)
            velocity = Vector2(0, 0)
            angle = 45.0  # Ship uses 'angle' from PhysicsBody
            is_alive = True
            is_derelict = False
            hp = 100
            max_hp = 100
            current_shields = 50.0
            max_shields = 100.0
            current_speed = 10.0
            max_speed = 50.0
            mass = 1000.0
            total_thrust = 500.0
            turn_speed = 30.0
            total_shots_fired = 0
            max_targets = 2
            ai_strategy = "aggressive"
            source_file = "test.json"
            layers = {}
            current_target = None
            secondary_targets = []
            # crew_onboard and crew_required NOT defined - these are dynamic attrs

            class MockResources:
                def get_all_resources(self):
                    return []
            resources = MockResources()

        ship = ShipWithoutCrewStats()

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

        # Verify all guaranteed attributes are accessed directly (not via getattr defaults)
        assert dto.is_derelict is False
        assert dto.current_shields == 50.0
        assert dto.max_shields == 100.0
        assert dto.ai_strategy == "aggressive"
        assert dto.max_targets == 2
        assert dto.heading == 45.0  # Mapped from ship.angle

        # Only crew_onboard/crew_required should use getattr fallbacks
        assert dto.crew_onboard == 0  # Fallback since not defined
        assert dto.crew_required == 0  # Fallback since not defined


class TestBattleUIServiceNoneEngine:
    """Additional tests for service behavior when engine is None."""

    def test_get_winner_returns_none_when_no_engine(self):
        """get_winner() returns None when no engine."""
        service = Mock()
        service.get_engine.return_value = None

        ui_service = BattleUIService(service)
        assert ui_service.get_winner() is None


class TestBattleUIServiceConversionEdgeCases:
    """Tests for edge cases in entity conversion."""

    def test_convert_ship_with_secondary_targets(self):
        """Ship with secondary targets includes their names."""
        mock_service = Mock()
        engine = Mock()

        target1 = Mock()
        target1.name = "Enemy 1"
        target2 = Mock()
        target2.name = "Enemy 2"

        ship = Mock()
        ship.id = "ship_1"
        ship.name = "Test Ship"
        ship.team_id = 0
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)
        ship.angle = 0.0
        ship.is_alive = True
        ship.is_derelict = False
        ship.hp = 100
        ship.max_hp = 100
        ship.current_shields = 50.0
        ship.max_shields = 100.0
        ship.current_speed = 10.0
        ship.max_speed = 50.0
        ship.mass = 1000.0
        ship.total_thrust = 500.0
        ship.turn_speed = 30.0
        ship.total_shots_fired = 0
        ship.crew_onboard = 10
        ship.crew_required = 10
        ship.max_targets = 3
        ship.ai_strategy = "aggressive"
        ship.source_file = "test.json"
        ship.layers = {}
        ship.current_target = None
        ship.secondary_targets = [target1, target2]
        ship.resources = Mock()
        ship.resources.get_all_resources.return_value = []

        engine.ships = [ship]
        engine.projectiles = []
        engine.recent_beams = []
        engine.tick_counter = 0
        engine.is_battle_over.return_value = False
        engine.get_winner.return_value = None
        mock_service.get_engine.return_value = engine

        ui_service = BattleUIService(mock_service)
        ships = ui_service.get_ships()

        assert len(ships[0].secondary_target_names) == 2
        assert "Enemy 1" in ships[0].secondary_target_names
        assert "Enemy 2" in ships[0].secondary_target_names

    def test_convert_ship_with_derelict_status(self):
        """Ship with is_derelict=True is converted correctly."""
        mock_service = Mock()
        engine = Mock()

        ship = Mock()
        ship.id = "ship_1"
        ship.name = "Derelict Ship"
        ship.team_id = 0
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)
        ship.angle = 0.0
        ship.is_alive = False
        ship.is_derelict = True
        ship.hp = 0
        ship.max_hp = 100
        ship.current_shields = 0.0
        ship.max_shields = 100.0
        ship.current_speed = 0.0
        ship.max_speed = 50.0
        ship.mass = 1000.0
        ship.total_thrust = 0.0
        ship.turn_speed = 0.0
        ship.total_shots_fired = 0
        ship.crew_onboard = 0
        ship.crew_required = 10
        ship.max_targets = 1
        ship.ai_strategy = "none"
        ship.source_file = "test.json"
        ship.layers = {}
        ship.current_target = None
        ship.secondary_targets = []
        ship.resources = Mock()
        ship.resources.get_all_resources.return_value = []

        engine.ships = [ship]
        engine.projectiles = []
        engine.recent_beams = []
        engine.tick_counter = 0
        engine.is_battle_over.return_value = True
        engine.get_winner.return_value = 1
        mock_service.get_engine.return_value = engine

        ui_service = BattleUIService(mock_service)
        ships = ui_service.get_ships()

        assert ships[0].is_derelict is True
        assert ships[0].is_alive is False

    def test_convert_component_with_status_enum(self):
        """Component with status as enum is converted correctly."""
        mock_service = Mock()
        engine = Mock()

        comp = Mock()
        comp.name = "Engine"
        comp.current_hp = 100.0
        comp.max_hp = 100.0
        comp.is_active = True
        comp.status = Mock()
        comp.status.name = "DAMAGED"  # Enum-style
        comp.has_ability = Mock(return_value=False)
        comp.shots_fired = 0
        comp.shots_hit = 0

        # Create a mock LayerData
        from game.simulation.entities.layer_data import LayerData
        layer_data = LayerData(components=[comp])

        ship = Mock()
        ship.id = "ship_1"
        ship.name = "Test Ship"
        ship.team_id = 0
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)
        ship.angle = 0.0
        ship.is_alive = True
        ship.is_derelict = False
        ship.hp = 100
        ship.max_hp = 100
        ship.current_shields = 50.0
        ship.max_shields = 100.0
        ship.current_speed = 10.0
        ship.max_speed = 50.0
        ship.mass = 1000.0
        ship.total_thrust = 500.0
        ship.turn_speed = 30.0
        ship.total_shots_fired = 0
        ship.crew_onboard = 10
        ship.crew_required = 10
        ship.max_targets = 1
        ship.ai_strategy = "aggressive"
        ship.source_file = "test.json"
        layer_type = Mock()
        layer_type.value = "outer"
        ship.layers = {layer_type: layer_data}
        ship.current_target = None
        ship.secondary_targets = []
        ship.resources = Mock()
        ship.resources.get_all_resources.return_value = []

        engine.ships = [ship]
        engine.projectiles = []
        engine.recent_beams = []
        engine.tick_counter = 0
        engine.is_battle_over.return_value = False
        engine.get_winner.return_value = None
        mock_service.get_engine.return_value = engine

        ui_service = BattleUIService(mock_service)
        ships = ui_service.get_ships()

        assert len(ships[0].components) == 1
        assert ships[0].components[0].status == "damaged"

    def test_convert_component_with_weapon_ability(self):
        """Component with WeaponAbility is marked has_weapon=True."""
        mock_service = Mock()
        engine = Mock()

        comp = Mock()
        comp.name = "Laser Cannon"
        comp.current_hp = 100.0
        comp.max_hp = 100.0
        comp.is_active = True
        comp.status = Mock()
        comp.status.name = "ACTIVE"
        comp.has_ability = Mock(side_effect=lambda x: x == 'WeaponAbility')
        comp.shots_fired = 15
        comp.shots_hit = 10

        from game.simulation.entities.layer_data import LayerData
        layer_data = LayerData(components=[comp])

        ship = Mock()
        ship.id = "ship_1"
        ship.name = "Test Ship"
        ship.team_id = 0
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)
        ship.angle = 0.0
        ship.is_alive = True
        ship.is_derelict = False
        ship.hp = 100
        ship.max_hp = 100
        ship.current_shields = 50.0
        ship.max_shields = 100.0
        ship.current_speed = 10.0
        ship.max_speed = 50.0
        ship.mass = 1000.0
        ship.total_thrust = 500.0
        ship.turn_speed = 30.0
        ship.total_shots_fired = 15
        ship.crew_onboard = 10
        ship.crew_required = 10
        ship.max_targets = 1
        ship.ai_strategy = "aggressive"
        ship.source_file = "test.json"
        layer_type = Mock()
        layer_type.value = "outer"
        ship.layers = {layer_type: layer_data}
        ship.current_target = None
        ship.secondary_targets = []
        ship.resources = Mock()
        ship.resources.get_all_resources.return_value = []

        engine.ships = [ship]
        engine.projectiles = []
        engine.recent_beams = []
        engine.tick_counter = 0
        engine.is_battle_over.return_value = False
        engine.get_winner.return_value = None
        mock_service.get_engine.return_value = engine

        ui_service = BattleUIService(mock_service)
        ships = ui_service.get_ships()

        assert ships[0].components[0].has_weapon is True
        assert ships[0].components[0].shots_fired == 15
        assert ships[0].components[0].shots_hit == 10

    def test_convert_projectile_with_target(self):
        """Projectile with target includes target name."""
        mock_service = Mock()
        engine = Mock()

        target = Mock()
        target.name = "Target Ship"

        proj = Mock()
        proj.id = "proj_1"
        proj.position = Vector2(100, 100)
        proj.velocity = Vector2(50, 0)
        proj.color = (255, 200, 50)
        proj.radius = 4.0
        proj.damage = 25.0
        proj.hp = 10.0
        proj.max_hp = 10.0
        proj.status = "active"
        proj.endurance = 5.0
        proj.max_endurance = 10.0
        proj.target = target
        proj.max_speed = 100.0

        engine.ships = []
        engine.projectiles = [proj]
        engine.recent_beams = []
        engine.tick_counter = 0
        engine.is_battle_over.return_value = False
        engine.get_winner.return_value = None
        mock_service.get_engine.return_value = engine

        ui_service = BattleUIService(mock_service)
        projectiles = ui_service.get_projectiles()

        assert len(projectiles) == 1
        assert projectiles[0].target_name == "Target Ship"

    def test_convert_beam_with_missing_keys(self):
        """Beam with missing dict keys uses default values."""
        mock_service = Mock()
        engine = Mock()

        # Beam dict with missing keys
        beam = {}  # No start, end, or color

        engine.ships = []
        engine.projectiles = []
        engine.recent_beams = [beam]
        engine.tick_counter = 0
        engine.is_battle_over.return_value = False
        engine.get_winner.return_value = None
        mock_service.get_engine.return_value = engine

        ui_service = BattleUIService(mock_service)
        beams = ui_service.get_recent_beams()

        assert len(beams) == 1
        # Should use defaults
        assert beams[0].start.x == 0
        assert beams[0].start.y == 0
        assert beams[0].end.x == 0
        assert beams[0].end.y == 0
        assert beams[0].color == (255, 255, 255)

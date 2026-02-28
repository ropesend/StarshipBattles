"""
Tests for AI-layer protocols (PROJ-192).

Verifies that actual game entities satisfy the protocol interfaces
and that TypeGuard functions correctly identify matching/non-matching objects.
"""

import pytest
from unittest.mock import Mock
from game.core.math import Vector2
from game.core.constants import AttackType

from game.ai.protocols import (
    IGridEntity,
    IProjectile,
    IFormationMaster,
    IComponentHealth,
    is_grid_entity,
    is_projectile,
    is_formation_master,
    is_component_health,
)
from game.simulation.entities.ship import Ship, LayerType
from game.simulation.entities.projectile import Projectile
from game.simulation.components.component import load_components, create_component
from game.core.registry import get_default_registry_provider
from tests.fixtures.paths import get_data_dir, get_unit_test_data_dir


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def create_test_ship(fresh_registries):
    """Factory fixture to create test ships."""
    data_dir = get_data_dir()
    unit_test_data_dir = get_unit_test_data_dir()

    provider = get_default_registry_provider()
    load_components(str(data_dir / "components.json"), registry_provider=provider)
    from game.simulation.entities.ship_loader import load_vehicle_classes
    load_vehicle_classes(str(unit_test_data_dir / "test_vehicleclasses.json"), registry_provider=provider)

    def _create_ship(name="TestShip", x=0, y=0, team_id=0):
        ship = Ship(name, x, y, (255, 255, 255), team_id, ship_class="TestM_4L", registries=fresh_registries)
        ship.add_component(create_component('bridge', registries=fresh_registries), LayerType.CORE)
        ship.add_component(create_component('crew_quarters', registries=fresh_registries), LayerType.CORE)
        ship.add_component(create_component('life_support', registries=fresh_registries), LayerType.CORE)
        ship.add_component(create_component('standard_engine', registries=fresh_registries), LayerType.OUTER)
        ship.recalculate_stats()
        return ship

    return _create_ship


@pytest.fixture
def create_test_projectile(create_test_ship):
    """Factory fixture to create test projectiles."""
    def _create_projectile():
        owner = create_test_ship()
        return Projectile(
            owner=owner,
            position=Vector2(100, 100),
            velocity=Vector2(50, 0),
            damage=10,
            range_val=1000,
            endurance=5.0,
            proj_type=AttackType.MISSILE,
        )
    return _create_projectile


# =============================================================================
# Protocol Interface Tests
# =============================================================================

class TestIGridEntityProtocol:
    """Tests for IGridEntity protocol compliance."""

    def test_ship_satisfies_igrid_entity(self, create_test_ship):
        """Ship should satisfy IGridEntity protocol."""
        ship = create_test_ship()

        # Verify isinstance check works
        assert isinstance(ship, IGridEntity)

        # Verify required attributes exist and are correct types
        assert hasattr(ship, 'position')
        assert hasattr(ship, 'is_alive')
        assert hasattr(ship, 'team_id')
        assert hasattr(ship, 'radius')

        # Verify attribute types
        assert isinstance(ship.is_alive, bool)
        assert isinstance(ship.team_id, int)
        assert isinstance(ship.radius, (int, float))

    def test_projectile_satisfies_igrid_entity(self, create_test_projectile):
        """Projectile should satisfy IGridEntity protocol."""
        projectile = create_test_projectile()

        assert isinstance(projectile, IGridEntity)

        # Verify attributes
        assert hasattr(projectile, 'position')
        assert hasattr(projectile, 'is_alive')
        assert hasattr(projectile, 'team_id')
        assert hasattr(projectile, 'radius')


class TestIProjectileProtocol:
    """Tests for IProjectile protocol compliance."""

    def test_projectile_satisfies_iprojectile(self, create_test_projectile):
        """Projectile should satisfy IProjectile protocol (extends IGridEntity)."""
        projectile = create_test_projectile()

        assert isinstance(projectile, IProjectile)

        # Verify type attribute exists
        assert hasattr(projectile, 'type')

    def test_ship_does_not_satisfy_iprojectile(self, create_test_ship):
        """Ship should NOT satisfy IProjectile (no 'type' attribute)."""
        ship = create_test_ship()

        # Ships don't have a 'type' attribute in the AttackType sense
        # They may have 'vehicle_type' but not 'type'
        # The protocol check should fail
        assert not isinstance(ship, IProjectile)


class TestIFormationMasterProtocol:
    """Tests for IFormationMaster protocol compliance."""

    def test_ship_satisfies_iformationmaster(self, create_test_ship):
        """Ship should satisfy IFormationMaster protocol."""
        ship = create_test_ship()

        assert isinstance(ship, IFormationMaster)

        # Verify all formation-related attributes
        assert hasattr(ship, 'position')
        assert hasattr(ship, 'angle')
        assert hasattr(ship, 'is_alive')
        assert hasattr(ship, 'is_derelict')
        assert hasattr(ship, 'is_thrusting')
        assert hasattr(ship, 'max_speed')
        assert hasattr(ship, 'engine_throttle')
        assert hasattr(ship, 'current_speed')
        assert hasattr(ship, 'formation')
        assert hasattr(ship, 'current_target')

        # Verify types
        assert isinstance(ship.angle, (int, float))
        assert isinstance(ship.is_alive, bool)
        assert isinstance(ship.is_derelict, bool)
        assert isinstance(ship.is_thrusting, bool)
        assert isinstance(ship.max_speed, (int, float))
        assert isinstance(ship.engine_throttle, (int, float))
        assert isinstance(ship.current_speed, (int, float))


class TestIComponentHealthProtocol:
    """Tests for IComponentHealth protocol compliance."""

    def test_component_satisfies_icomponenthealth(self, create_test_ship):
        """Component should satisfy IComponentHealth protocol."""
        ship = create_test_ship()

        # Get a component from the ship
        components = ship.get_all_components()
        assert len(components) > 0, "Ship should have at least one component"

        component = components[0]

        assert isinstance(component, IComponentHealth)

        # Verify HP attributes
        assert hasattr(component, 'current_hp')
        assert hasattr(component, 'max_hp')
        assert isinstance(component.current_hp, (int, float))
        assert isinstance(component.max_hp, (int, float))


# =============================================================================
# TypeGuard Function Tests
# =============================================================================

class TestTypeGuardFunctions:
    """Tests for TypeGuard functions."""

    def test_is_grid_entity_with_ship(self, create_test_ship):
        """is_grid_entity should return True for Ship."""
        ship = create_test_ship()
        assert is_grid_entity(ship) is True

    def test_is_grid_entity_with_projectile(self, create_test_projectile):
        """is_grid_entity should return True for Projectile."""
        projectile = create_test_projectile()
        assert is_grid_entity(projectile) is True

    def test_is_grid_entity_with_non_entity(self):
        """is_grid_entity should return False for non-matching objects."""
        assert is_grid_entity(None) is False
        assert is_grid_entity(42) is False
        assert is_grid_entity("not an entity") is False
        assert is_grid_entity({'position': Vector2(0, 0)}) is False
        assert is_grid_entity([]) is False

    def test_is_projectile_with_projectile(self, create_test_projectile):
        """is_projectile should return True for Projectile."""
        projectile = create_test_projectile()
        assert is_projectile(projectile) is True

    def test_is_projectile_with_ship(self, create_test_ship):
        """is_projectile should return False for Ship (no type attribute)."""
        ship = create_test_ship()
        assert is_projectile(ship) is False

    def test_is_projectile_with_non_entity(self):
        """is_projectile should return False for non-matching objects."""
        assert is_projectile(None) is False
        assert is_projectile(42) is False
        assert is_projectile({}) is False

    def test_is_formation_master_with_ship(self, create_test_ship):
        """is_formation_master should return True for Ship."""
        ship = create_test_ship()
        assert is_formation_master(ship) is True

    def test_is_formation_master_with_projectile(self, create_test_projectile):
        """is_formation_master should return False for Projectile."""
        projectile = create_test_projectile()
        assert is_formation_master(projectile) is False

    def test_is_formation_master_with_non_entity(self):
        """is_formation_master should return False for non-matching objects."""
        assert is_formation_master(None) is False
        assert is_formation_master(42) is False
        assert is_formation_master({}) is False

    def test_is_component_health_with_component(self, create_test_ship):
        """is_component_health should return True for Component."""
        ship = create_test_ship()
        components = ship.get_all_components()
        assert len(components) > 0

        component = components[0]
        assert is_component_health(component) is True

    def test_is_component_health_with_non_component(self):
        """is_component_health should return False for non-matching objects."""
        assert is_component_health(None) is False
        assert is_component_health(42) is False
        assert is_component_health({'current_hp': 10}) is False  # Missing max_hp
        assert is_component_health({'max_hp': 10}) is False  # Missing current_hp


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestProtocolEdgeCases:
    """Edge case tests for protocol checking."""

    def test_mock_with_all_attributes_satisfies_protocol(self):
        """Mock objects with all required attributes should satisfy protocols."""
        mock_entity = Mock()
        mock_entity.position = Vector2(100, 100)
        mock_entity.is_alive = True
        mock_entity.team_id = 1
        mock_entity.radius = 25.0

        assert is_grid_entity(mock_entity) is True

    def test_partial_mock_does_not_satisfy_protocol(self):
        """Mock objects missing attributes should not satisfy protocols."""
        mock_entity = Mock(spec=[])  # Empty spec - no auto-attributes
        mock_entity.position = Vector2(100, 100)
        mock_entity.is_alive = True
        # Missing team_id and radius

        # Note: runtime_checkable only checks attribute existence, not callability
        # So we need to ensure the mock doesn't auto-create missing attributes
        assert not hasattr(mock_entity, 'team_id')
        assert is_grid_entity(mock_entity) is False

    def test_dead_entity_still_satisfies_protocol(self, create_test_ship):
        """Dead entities should still satisfy protocol (is_alive is just a bool)."""
        ship = create_test_ship()
        ship.is_alive = False

        assert is_grid_entity(ship) is True
        assert is_formation_master(ship) is True

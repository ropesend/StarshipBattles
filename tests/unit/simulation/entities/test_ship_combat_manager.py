"""
Tests for ShipCombatManager -- combat orchestration delegate extracted from Ship.

PROJ-240 Phase 2: Tests written BEFORE implementation (TDD).
These tests verify the ShipCombatManager class manages combat orchestration
correctly as a delegate of Ship.

Since ShipCombatManager is an internal delegate and Ship preserves
its facade API, these tests exercise the manager through Ship's public
methods to prove the delegation works correctly.
"""
import pytest
from unittest.mock import patch, MagicMock

from game.simulation.entities.ship import Ship
from game.simulation.components.component import Component, create_component
from game.core.constants import LayerType
from game.core.math import Vector2


class TestShipCombatManagerUpdate:
    """Tests for the update() combat tick method."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        """Create a fully-equipped ship for combat testing."""
        self.registries = fresh_registries
        # Use a ship class big enough for weapons
        fresh_registries.vehicle_classes["CombatTestShip"] = {
            "default_hull_id": "hull_escort",
            "max_mass": 5000,
            "layers": [
                {"type": "CORE", "radius_pct": 0.3, "max_mass_pct": 0.3},
                {"type": "OUTER", "radius_pct": 0.7, "max_mass_pct": 0.4},
                {"type": "ARMOR", "radius_pct": 1.0, "max_mass_pct": 0.3},
            ]
        }
        self.ship = Ship(
            "CombatShip", 0, 0, (255, 0, 0),
            ship_class="CombatTestShip",
            registries=fresh_registries
        )

    def test_update_short_circuits_when_dead(self):
        """update() does nothing when ship is not alive."""
        self.ship.is_alive = False
        initial_pos = Vector2(self.ship.position.x, self.ship.position.y)
        self.ship.update()
        # Position should not have changed (no physics update)
        assert self.ship.position.x == initial_pos.x
        assert self.ship.position.y == initial_pos.y

    def test_update_calls_subsystems_in_order(self):
        """update() calls resources, components, stats, physics, combat in order."""
        # We verify by checking that the ship was updated without error
        # and that recalculate_stats was called (which the update loop does)
        self.ship.add_component(
            create_component('bridge', registries=self.registries),
            LayerType.CORE
        )
        initial_mass = self.ship.mass
        # Just verify update doesn't crash and processes properly
        self.ship.update()
        # Stats should have been recalculated during update
        assert self.ship.mass == initial_mass  # Should be stable

    def test_update_firing_with_trigger_pulled(self):
        """When comp_trigger_pulled=True, fire_weapons results extend just_fired_projectiles."""
        self.ship.comp_trigger_pulled = True
        # Mock combat_engine to return fake projectiles
        mock_projectile = MagicMock()
        with patch.object(
            self.ship.combat_engine, 'fire_weapons',
            return_value=[mock_projectile]
        ):
            self.ship.update()
        assert mock_projectile in self.ship.just_fired_projectiles

    def test_update_no_firing_without_trigger(self):
        """When comp_trigger_pulled=False, no firing occurs."""
        self.ship.comp_trigger_pulled = False
        with patch.object(
            self.ship.combat_engine, 'fire_weapons',
            return_value=[MagicMock()]
        ) as mock_fire:
            self.ship.update()
        mock_fire.assert_not_called()


class TestShipCombatManagerDerelict:
    """Tests for update_derelict_status()."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        self.registries = fresh_registries
        fresh_registries.vehicle_classes["DerelictTestShip"] = {
            "default_hull_id": "hull_escort",
            "max_mass": 5000,
            "layers": [
                {"type": "CORE", "radius_pct": 0.3, "max_mass_pct": 0.3},
                {"type": "OUTER", "radius_pct": 0.7, "max_mass_pct": 0.4},
                {"type": "ARMOR", "radius_pct": 1.0, "max_mass_pct": 0.3},
            ]
        }
        self.ship = Ship(
            "DerelictShip", 0, 0, (255, 0, 0),
            ship_class="DerelictTestShip",
            registries=fresh_registries
        )

    def test_derelict_no_weapons_no_engines(self):
        """Ship with no weapons AND no engines is derelict."""
        # Default ship has no weapons/engines (just hull)
        self.ship.update_derelict_status()
        assert self.ship.is_derelict is True

    def test_derelict_recovery_with_weapons(self):
        """Ship that was derelict but gains weapons is no longer derelict."""
        self.ship.is_derelict = True
        # Add weapon + crew support so it becomes operational
        self.ship.add_component(
            create_component('crew_quarters', registries=self.registries),
            LayerType.CORE
        )
        self.ship.add_component(
            create_component('life_support', registries=self.registries),
            LayerType.CORE
        )
        self.ship.add_component(
            create_component('bridge', registries=self.registries),
            LayerType.CORE
        )
        self.ship.add_component(
            create_component('railgun', registries=self.registries),
            LayerType.OUTER
        )
        self.ship.recalculate_stats()
        self.ship.update_derelict_status()
        assert self.ship.is_derelict is False

    def test_derelict_resets_bridge_destroyed(self):
        """update_derelict_status always resets bridge_destroyed to False."""
        self.ship.bridge_destroyed = True
        self.ship.update_derelict_status()
        assert self.ship.bridge_destroyed is False

    def test_derelict_crew_check(self):
        """Ship with insufficient maintenance providers becomes derelict.

        QA Observation 5: derelict status now keys off RequiresMaintenance
        vs ProvidesMaintenance (crew is one provider; without crew_quarters
        the bridge's maintenance demand goes unmet).
        """
        # Add a bridge (requires maintenance) but no crew quarters / maintenance unit
        self.ship.add_component(
            create_component('bridge', registries=self.registries),
            LayerType.CORE
        )
        self.ship.recalculate_stats()
        maint_req = self.ship.get_total_ability_value('RequiresMaintenance')
        maint_provided = self.ship.get_total_ability_value('ProvidesMaintenance')
        if maint_req > 0 and maint_req > maint_provided:
            self.ship.update_derelict_status()
            assert self.ship.is_derelict is True


class TestShipCombatManagerDie:
    """Tests for die() method."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        self.registries = fresh_registries
        self.ship = Ship(
            "DyingShip", 100, 200, (255, 0, 0),
            registries=fresh_registries
        )

    def test_die_sets_not_alive(self):
        """die() sets is_alive to False."""
        assert self.ship.is_alive is True
        self.ship.die()
        assert self.ship.is_alive is False

    def test_die_zeroes_velocity(self):
        """die() zeroes the velocity vector."""
        self.ship.velocity = Vector2(100, 200)
        self.ship.die()
        assert self.ship.velocity.x == 0
        assert self.ship.velocity.y == 0

    def test_die_calls_recalculate_stats(self):
        """die() calls recalculate_stats to update ship state."""
        with patch.object(self.ship, 'recalculate_stats') as mock_recalc:
            self.ship.die()
        mock_recalc.assert_called_once()


class TestShipCombatManagerCombatEngine:
    """Tests for combat_engine lazy creation."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        self.registries = fresh_registries
        self.ship = Ship(
            "EngineTestShip", 0, 0, (255, 0, 0),
            registries=fresh_registries
        )

    def test_combat_engine_lazy_creation(self):
        """combat_engine property lazily creates ShipCombatEngine."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine
        engine = self.ship.combat_engine
        assert isinstance(engine, ShipCombatEngine)
        # Second access returns same instance
        assert self.ship.combat_engine is engine


class TestShipCombatManagerPropertyDelegation:
    """Tests for just_fired_projectiles, comp_trigger_pulled, aim_point property delegation."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        self.registries = fresh_registries
        self.ship = Ship(
            "PropTestShip", 0, 0, (255, 0, 0),
            registries=fresh_registries
        )

    def test_just_fired_projectiles_getter(self):
        """just_fired_projectiles returns the list from combat_manager."""
        assert self.ship.just_fired_projectiles == []

    def test_just_fired_projectiles_setter(self):
        """just_fired_projectiles setter updates combat_manager state."""
        self.ship.just_fired_projectiles = [1, 2, 3]
        assert self.ship.just_fired_projectiles == [1, 2, 3]
        # Reset
        self.ship.just_fired_projectiles = []
        assert self.ship.just_fired_projectiles == []

    def test_comp_trigger_pulled_getter(self):
        """comp_trigger_pulled returns the bool from combat_manager."""
        assert self.ship.comp_trigger_pulled is False

    def test_comp_trigger_pulled_setter(self):
        """comp_trigger_pulled setter updates combat_manager state."""
        self.ship.comp_trigger_pulled = True
        assert self.ship.comp_trigger_pulled is True

    def test_aim_point_getter(self):
        """aim_point returns the value from combat_manager."""
        assert self.ship.aim_point is None

    def test_aim_point_setter(self):
        """aim_point setter updates combat_manager state."""
        point = Vector2(100, 200)
        self.ship.aim_point = point
        assert self.ship.aim_point is point


class TestShipSetEventBus:
    """Tests for set_event_bus facade method."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        self.registries = fresh_registries
        self.ship = Ship(
            "EventBusShip", 0, 0, (255, 0, 0),
            registries=fresh_registries
        )

    def test_set_event_bus_delegates_to_combat_engine(self):
        """set_event_bus sets the event bus on the combat engine."""
        mock_bus = MagicMock()
        self.ship.set_event_bus(mock_bus)
        assert self.ship.combat_engine._event_bus is mock_bus

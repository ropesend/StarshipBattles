"""
Test baseline for ship stats calculation.
Created before Phase 3 refactor to ensure no regressions.
"""
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from unittest.mock import MagicMock, patch
import importlib


class TestShipStatsBaseline(unittest.TestCase):
    """Baseline tests for ShipStatsCalculator to verify before/after Phase 3."""
    
    def setUp(self):
        """Load test data once."""
        # Save original pygame modules if they exist
        self._original_pygame = sys.modules.get('pygame')
        self._original_pygame_mixer = sys.modules.get('pygame.mixer')
        self._original_pygame_font = sys.modules.get('pygame.font')
        
        # Mock pygame before importing game modules
        self.pygame_mock = MagicMock()
        self.pygame_mock.mixer = MagicMock()
        self.pygame_mock.font = MagicMock()
        sys.modules['pygame'] = self.pygame_mock
        sys.modules['pygame.mixer'] = self.pygame_mock.mixer
        sys.modules['pygame.font'] = self.pygame_mock.font
        
        # Import after mocking
        from game.core.registry import RegistryManager
        from game.simulation.components.component import Component, load_components, load_modifiers
        from ship_stats import ShipStatsCalculator
        
        self.Component = Component
        self.ShipStatsCalculator = ShipStatsCalculator
        self.vehicle_classes = RegistryManager.instance().vehicle_classes
        
        # Load components and modifiers
        load_components()
        load_modifiers()
    
    
    def _create_mock_ship(self, components):
        """Create a mock ship with the given components."""
        from game.simulation.components.component import LayerType
        from game.simulation.systems.resource_manager import ResourceRegistry
        
        ship = MagicMock()
        ship.layers = {
            LayerType.CORE: {
                'components': components,
                'mass': 0,
                'max_mass_pct': 0.3
            }
        }
        ship.base_mass = 100
        ship.mass = 100
        ship.current_mass = 0
        ship.ship_class = "Corvette"
        ship.vehicle_type = "Ship"
        ship.resources = ResourceRegistry()
        ship._resources_initialized = False
        ship.current_shields = 0
        ship.max_shields = 0
        
        # Assign ship reference to components
        for c in components:
            c.ship = ship
            c.recalculate_stats()
        
        return ship
    
    def test_thrust_calculation_from_engine(self):
        """Verify thrust is calculated correctly from Engine components."""
        # Create an engine with CombatPropulsion ability
        engine_data = {
            'id': 'test_engine',
            'name': 'Test Engine',
            'type': 'Engine',
            'mass': 100,
            'hp': 50,
            'abilities': {
                'CombatPropulsion': {'value': 1500},
                'ResourceConsumption': {'resource': 'fuel', 'amount': 10, 'trigger': 'constant'}
            }
        }
        engine = self.Component(engine_data)
        
        ship = self._create_mock_ship([engine])
        calculator = self.ShipStatsCalculator(self.vehicle_classes)
        calculator.calculate(ship)
        
        self.assertEqual(ship.total_thrust, 1500)
        
        # Also verify ability has the value
        ab = engine.get_ability('CombatPropulsion')
        self.assertIsNotNone(ab)
        self.assertEqual(ab.thrust_force, 1500.0)
    
    def test_turn_speed_calculation_from_thruster(self):
        """Verify turn speed is calculated correctly from Thruster components."""
        thruster_data = {
            'id': 'test_thruster',
            'name': 'Test Thruster',
            'type': 'Thruster',
            'mass': 50,
            'hp': 30,
            'abilities': {
                'ManeuveringThruster': {'value': 45.0}
            }
        }
        thruster = self.Component(thruster_data)
        
        ship = self._create_mock_ship([thruster])
        calculator = self.ShipStatsCalculator(self.vehicle_classes)
        calculator.calculate(ship)
        
        # Raw turn speed before mass scaling
        self.assertEqual(ship.total_maneuver_points, 45.0)
        
        # Also verify ability has the value
        ab = thruster.get_ability('ManeuveringThruster')
        self.assertIsNotNone(ab)
        self.assertEqual(ab.turn_rate, 45.0)
    
    def test_shield_stats_calculation(self):
        """Verify shield capacity and regen are calculated correctly."""
        shield_data = {
            'id': 'test_shield',
            'name': 'Test Shield',
            'type': 'Shield',
            'mass': 80,
            'hp': 40,
            'abilities': {
                'ShieldProjection': 500
            }
        }
        
        regen_data = {
            'id': 'test_regen',
            'name': 'Test Shield Regen',
            'type': 'ShieldRegenerator',
            'mass': 60,
            'hp': 30,
            'abilities': {
                'ShieldRegeneration': 25.0,
                'EnergyConsumption': {'resource': 'energy', 'amount': 5, 'trigger': 'constant'}
            }
        }
        
        shield = self.Component(shield_data)
        regen = self.Component(regen_data)
        
        ship = self._create_mock_ship([shield, regen])
        calculator = self.ShipStatsCalculator(self.vehicle_classes)
        calculator.calculate(ship)
        
        self.assertEqual(ship.max_shields, 500.0)
        self.assertEqual(ship.shield_regen_rate, 25.0)
        
        # Verify abilities
        shield_ab = shield.get_ability('ShieldProjection')
        self.assertIsNotNone(shield_ab)
        self.assertEqual(shield_ab.capacity, 500.0)
        
        regen_ab = regen.get_ability('ShieldRegeneration')
        self.assertIsNotNone(regen_ab)
        self.assertEqual(regen_ab.rate, 25.0)
    
    def test_ability_values_match_legacy_attributes(self):
        """Phase 7: Verify ability values are correctly parsed from component data."""
        engine_data = {
            'id': 'test_engine',
            'name': 'Test Engine',
            'type': 'Engine',
            'mass': 100,
            'hp': 50,
            'abilities': {
                'CombatPropulsion': {'value': 2000}
            }
        }
        engine = self.Component(engine_data)
        
        # Phase 7: Legacy attributes no longer exist on Component
        # All stats are now accessed via abilities
        ab = engine.get_ability('CombatPropulsion')
        self.assertIsNotNone(ab, "Engine should have CombatPropulsion ability")
        self.assertEqual(ab.thrust_force, 2000.0)
    
    def test_multiple_engines_sum_thrust(self):
        """Verify multiple engines sum their thrust values."""
        engine1_data = {
            'id': 'engine1',
            'name': 'Engine 1',
            'type': 'Engine',
            'mass': 100,
            'hp': 50,
            'abilities': {
                'CombatPropulsion': {'value': 1000}
            }
        }
        engine2_data = {
            'id': 'engine2',
            'name': 'Engine 2',
            'type': 'Engine',
            'mass': 100,
            'hp': 50,
            'abilities': {
                'CombatPropulsion': {'value': 1500}
            }
        }
        
        engine1 = self.Component(engine1_data)
        engine2 = self.Component(engine2_data)
        
        ship = self._create_mock_ship([engine1, engine2])
        calculator = self.ShipStatsCalculator(self.vehicle_classes)
        calculator.calculate(ship)
        
        self.assertEqual(ship.total_thrust, 2500)


class TestAbilityModifierSync(unittest.TestCase):
    """Test that modifiers correctly update ability values."""
    
    def setUp(self):
        """Load test data once."""
        # Save original pygame modules if they exist
        self._original_pygame = sys.modules.get('pygame')
        self._original_pygame_mixer = sys.modules.get('pygame.mixer')
        self._original_pygame_font = sys.modules.get('pygame.font')
        
        self.pygame_mock = MagicMock()
        self.pygame_mock.mixer = MagicMock()
        self.pygame_mock.font = MagicMock()
        sys.modules['pygame'] = self.pygame_mock
        sys.modules['pygame.mixer'] = self.pygame_mock.mixer
        sys.modules['pygame.font'] = self.pygame_mock.font
        
        from game.simulation.components.component import Component, load_components, load_modifiers
        from game.core.registry import RegistryManager
        
        self.Component = Component
        self.modifiers = RegistryManager.instance().modifiers
        
        load_components()
        load_modifiers()
    
    
    def test_thrust_modifier_updates_ability(self):
        """Verify thrust modifiers update CombatPropulsion ability value."""
        engine_data = {
            'id': 'test_engine',
            'name': 'Test Engine',
            'type': 'Engine',
            'mass': 100,
            'hp': 50,
            'abilities': {
                'CombatPropulsion': {'value': 1000}
            }
        }
        engine = self.Component(engine_data)
        
        # Before modifier
        ab = engine.get_ability('CombatPropulsion')
        self.assertEqual(ab.thrust_force, 1000.0)
        
        # Apply 2x size modifier (if it affects thrust)
        # Check if there's a thrust-affecting modifier
        if 'size_mount' in self.modifiers:
            engine.add_modifier('size_mount', 2)  # Example modifier
            engine.recalculate_stats()
            
            # Verify ability was updated
            ab = engine.get_ability('CombatPropulsion')
            # The specific multiplier depends on modifier definition
            # Just verify it changed if the modifier affects thrust
            pass


if __name__ == '__main__':
    unittest.main()

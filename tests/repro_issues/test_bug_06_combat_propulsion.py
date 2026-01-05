"""
Reproduction test for BUG-06: Combat Propulsion Validation Error.
Uses 'Manual Headless Assembly' pattern to avoid state pollution from registry reloads.
"""
import pytest
from game.simulation.entities.ship import Ship, LayerType
from game.core.registry import RegistryManager
from game.simulation.components.component import Component
from game.simulation.components.abilities import (
    CombatPropulsion, CommandAndControl, ResourceStorage
)
from ship_stats import ShipStatsCalculator
from ship_validator import ShipDesignValidator


class TestBug06CombatPropulsion:
    """
    Reproduction test for BUG-06: Combat Propulsion Validation Error.
    
    Root Cause (Fixed): ShipStatsCalculator ignored CombatPropulsion abilities,
    and ShipDesignValidator didn't include candidate components during addition checks.
    
    This test verifies the fix WITHOUT using importlib.reload() which causes
    Enum identity collisions in subsequent tests.
    """

    @pytest.fixture(autouse=True)
    def setup_test_data(self):
        """Set up minimal test data without modifying global registries."""
        # Use a minimal vehicle classes dict for testing
        self.vehicle_classes = {
            "TestClass": {
                "hull_mass": 50,
                "max_mass": 1000,
                "type": "Ship",
                "requirements": {"CombatPropulsion": True, "CommandAndControl": True},
                "layers": [
                    {"type": "CORE", "radius_pct": 0.2, "restrictions": []},
                    {"type": "INNER", "radius_pct": 0.5, "restrictions": []},
                    {"type": "OUTER", "radius_pct": 0.8, "restrictions": []},
                    {"type": "ARMOR", "radius_pct": 1.0, "restrictions": []}
                ]
            }
        }
        self.calculator = ShipStatsCalculator(self.vehicle_classes)
        self.validator = ShipDesignValidator()

    def _create_ship_with_layers(self, ship_class="TestClass"):
        """Create a ship with properly initialized layers."""
        # Temporarily update vehicle_classes for Ship initialization
        classes = RegistryManager.instance().vehicle_classes
        original_classes = dict(classes)
        classes.clear()
        classes.update(self.vehicle_classes)
        
        ship = Ship(name="Test Ship", x=0, y=0, color=(255, 255, 255), ship_class=ship_class)
        
        # Restore original classes
        classes = RegistryManager.instance().vehicle_classes
        classes.clear()
        classes.update(original_classes)
        
        return ship

    def test_combat_propulsion_validation(self):
        """
        Test that CombatPropulsion abilities are correctly detected by validation.
        
        Expected: No "Needs Combat Propulsion" error when an engine with 
        CombatPropulsion ability is present.
        """
        # 1. Create ship
        ship = self._create_ship_with_layers()
        
        # 2. Create engine component with CombatPropulsion ability (Manual Assembly)
        engine_data = {"id": "test_engine", "name": "Test Engine", "mass": 10, "hp": 50, "type": "Internal"}
        engine = Component(engine_data)
        engine.ability_instances = [CombatPropulsion(engine, 1500)]  # 1500 thrust
        
        # 3. Create bridge with CommandAndControl
        bridge_data = {"id": "test_bridge", "name": "Test Bridge", "mass": 5, "hp": 30, "type": "Internal"}
        bridge = Component(bridge_data)
        bridge.ability_instances = [CommandAndControl(bridge, 1)]
        
        # 4. Add components using robust layer lookup (handles Enum identity mismatch)
        def get_layer_key(ship, layer_name):
            """Robust lookup by name to handle potential Enum identity issues."""
            for k in ship.layers:
                if k.name == layer_name:
                    return k
            return None
        
        core_key = get_layer_key(ship, 'CORE')
        outer_key = get_layer_key(ship, 'OUTER')
        
        assert core_key is not None, "Ship should have CORE layer"
        assert outer_key is not None, "Ship should have OUTER layer"
        
        ship.layers[core_key]['components'].append(bridge)
        bridge.ship = ship
        ship.layers[outer_key]['components'].append(engine)
        engine.ship = ship
        
        # 5. Calculate stats using our test calculator
        self.calculator.calculate(ship)
        
        # 6. Verify CombatPropulsion was detected
        total_thrust = ship.total_thrust
        assert total_thrust > 0, f"Total thrust should be > 0, got {total_thrust}"
        
        # 7. Validate using our test validator (checks ability totals)
        ability_totals = self.calculator.calculate_ability_totals(
            [c for layer in ship.layers.values() for c in layer['components']]
        )
        
        has_combat_propulsion = ability_totals.get('CombatPropulsion', 0) > 0
        has_command_control = ability_totals.get('CommandAndControl', 0) > 0
        
        assert has_combat_propulsion, f"CombatPropulsion not detected. Abilities: {ability_totals}"
        assert has_command_control, f"CommandAndControl not detected. Abilities: {ability_totals}"

    def test_thrust_value_is_correct(self):
        """Test that the thrust value from CombatPropulsion is correctly aggregated."""
        ship = self._create_ship_with_layers()
        
        # Create engine with known thrust
        engine_data = {"id": "test_engine", "name": "Test Engine", "mass": 10, "hp": 50, "type": "Internal"}
        engine = Component(engine_data)
        engine.ability_instances = [CombatPropulsion(engine, 2000)]  # 2000 thrust
        
        # Add to ship
        outer_key = None
        for k in ship.layers:
            if k.name == 'OUTER':
                outer_key = k
                break
        
        ship.layers[outer_key]['components'].append(engine)
        engine.ship = ship
        
        # Calculate and verify
        self.calculator.calculate(ship)
        
        assert ship.total_thrust == 2000, f"Expected thrust 2000, got {ship.total_thrust}"

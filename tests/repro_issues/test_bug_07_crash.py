
import pytest
from game.simulation.entities.ship import Ship
from game.simulation.components.component import Component, LayerType
from game.simulation.components.abilities import create_ability, ToHitAttackModifier

class TestBug07Crash:
    def test_crash_adding_component_with_tohit_modifier(self):
        """
        Reproduction for BUG-07: AttributeError: 'ToHitAttackModifier' object has no attribute 'value'
        when calling ship.get_total_sensor_score().
        """
        # 1. Create Ship
        ship = Ship("TestShip", 0, 0, (255, 255, 255))
        
        # 2. Create Component with ToHitAttackModifier
        # We need a component that registers this ability.
        # We can use a raw component and manually attach the ability or use a definition.
        
        # 2. Create Component with ToHitAttackModifier
        # Component expects a dictionary
        comp_data = {
            "id": "sensor_01",
            "name": "Sensor Array",
            "mass": 10,
            "hp": 50,
            "type": "Sensor",
            "cost": 10
        }
        comp = Component(comp_data)
        
        # Manually create the ability and attach it
        ability_data = {"value": 2.0} 
        ability = create_ability("ToHitAttackModifier", comp, ability_data)
        
        # Patch into ability_instances so get_abilities finds it
        if ability:
            comp.ability_instances.append(ability)
            
        # 3. Add Component to Ship
        # We need to bypass the validator to avoid unrelated errors, or just use valid setup.
        # Direct addition to layer might be easiest for unit test.
        ship.layers[LayerType.CORE]['components'].append(comp)
        
        # 4. Trigger validation (Crash happens here)
        try:
            score = ship.get_total_sensor_score()
            print(f"Score calculated: {score}")
            # Verify the score (Value is 2.0)
            assert score == 2.0, f"Expected 2.0, got {score}"
        except AttributeError as e:
            pytest.fail(f"BUG-07 Still Present: {e}")

from game.simulation.components.component import Component
import math

def test_formula():
    print("Testing Multiplicative Accuracy Formula...")
    
    # Setup test weapon with ALL required component fields
    data = {
        'id': 'test_laser',
        'name': 'Test Laser',
        'type': 'Weapon', 
        'mass': 10,
        'hp': 100,
        'allowed_layers': ['CORE'],
        'abilities': {
            'BeamWeaponAbility': {
                'base_accuracy': 10.0,
                'accuracy_falloff': 0.0001,
                'range': 12000,
                'damage': 0
            }
        }
    }
    
    weapon = Component(data)
    ability = weapon.get_ability('BeamWeaponAbility')
    
    test_ranges = [0, 5000, 9000, 9500, 10000, 11000]
    
    for dist in test_ranges:
        chance = ability.calculate_hit_chance(dist)
        factor = 1.0 - (dist * ability.accuracy_falloff)
        raw_val = ability.base_accuracy * factor
        
        print(f"Range {dist}: Factor={factor:.4f}, Raw={raw_val:.4f}, Final Chance={chance:.4f}")
        
    # Validation
    assert math.isclose(ability.calculate_hit_chance(0), 1.0)
    assert math.isclose(ability.calculate_hit_chance(9000), 1.0) # 10 * 0.1 = 1.0
    assert math.isclose(ability.calculate_hit_chance(9500), 0.5) # 10 * 0.05 = 0.5
    assert math.isclose(ability.calculate_hit_chance(10000), 0.0)
    assert math.isclose(ability.calculate_hit_chance(11000), 0.0)
    
    print("\nSUCCESS: Formula behaves as expected with Hard Range Cap.")

if __name__ == "__main__":
    test_formula()

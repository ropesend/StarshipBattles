"""Test that validation passes after updates"""
import os
import json

# Load component data
components_path = os.path.join('simulation_tests', 'data', 'components.json')
with open(components_path, 'r') as f:
    components_data = json.load(f)
    components_list = components_data.get('components', [])
    components_cache = {comp['id']: comp for comp in components_list}

# Check test_beam_low_acc_1dmg
comp = components_cache.get('test_beam_low_acc_1dmg')
beam_ability = comp['abilities']['BeamWeaponAbility']
print(f"Component data:")
print(f"  Damage: {beam_ability['damage']}")

# Load BEAM360-001 scenario
from test_framework.registry import TestRegistry
registry = TestRegistry()
scenario_info = registry.get_by_id('BEAM360-001')
metadata = scenario_info['metadata']

# Get ExactMatchRules
exact_match_rules = [rule for rule in metadata.validation_rules if rule.__class__.__name__ == 'ExactMatchRule']

print(f"\nTest metadata validation rules:")
for rule in exact_match_rules:
    if 'Damage' in rule.name:
        print(f"  {rule.name}: expected={rule.expected}")

# Check conditions text
print(f"\nTest conditions:")
for cond in metadata.conditions:
    if 'Beam Damage' in cond:
        print(f"  {cond}")

# Run validation
from simulation_tests.scenarios.validation import Validator

test_context = {
    'attacker': {
        'weapon': {
            'damage': beam_ability['damage'],
            'base_accuracy': beam_ability['base_accuracy'],
            'accuracy_falloff': beam_ability['accuracy_falloff'],
            'range': beam_ability['range']
        }
    },
    'target': {
        'mass': 400.0
    }
}

validator = Validator(exact_match_rules)
results = validator.validate(test_context)

print(f"\nValidation results:")
for result in results:
    status = result.status.value if hasattr(result.status, 'value') else result.status
    print(f"  {result.name}: {status} (expected={result.expected}, actual={result.actual})")

# Check if all pass
all_pass = all(r.status.value == 'PASS' for r in results if hasattr(r.status, 'value'))
print(f"\n{'✓ ALL VALIDATIONS PASS!' if all_pass else '✗ Some validations failed'}")

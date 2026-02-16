"""Trace why ShipStatsCalculator returns empty cargo_storage for passenger_quarters."""
from game.strategy.services.ship_stats_calculator import ShipStatsCalculator
import json

with open('data/components.json', 'r') as f:
    data = json.load(f)
components = {c['id']: c for c in data['components']}

with open('data/modifiers.json', 'r') as f:
    modifiers = json.load(f)

class Reg:
    @property
    def components(self): return components
    @property
    def modifiers(self): return modifiers
    @property
    def vehicle_classes(self): return {}

calc = ShipStatsCalculator(Reg())

# Load real design
with open('tests/fixtures/quickstart/designs/qs_colony_continental.json', 'r') as f:
    design = json.load(f)

# 1. Trace iteration
found = calc._iterate_design_components(design)
for layer_name, comp_entry, comp_def in found:
    comp_id = comp_entry.get('id', '?')
    abilities = comp_def.get('abilities', {})
    if 'CargoStorage' in abilities:
        cargo_list = ShipStatsCalculator._get_ability_list(abilities, 'CargoStorage')
        for ability_data in cargo_list:
            cargo_type = ability_data.get('cargo_type', 'generic')
            capacity = ability_data.get('capacity', 0)
            print(f"FOUND: {comp_id} -> CargoStorage: type={cargo_type} cap={capacity}")

# 2. Full stats
stats = calc.calculate_stats(design)
print(f"cargo_storage in stats: {stats.get('cargo_storage', {})}")

# 3. Can also check the expected_stats fallback
expected = design.get('expected_stats', {})
print(f"expected_stats: {expected}")
print(f"expected cargo_storage: {expected.get('cargo_storage', 'NOT IN EXPECTED')}")

# 4. Check if components_found is empty (fallback path)  
if not found:
    print("!! NO COMPONENTS FOUND - FALLBACK TO expected_stats !!")
else:
    print(f"Components found: {len(found)} - using calculated path")

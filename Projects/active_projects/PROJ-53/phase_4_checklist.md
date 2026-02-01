# Phase 4: Fix Strategic Layer

**Objective:** Fix strategic layer code (ship instances, fleets) that uses legacy resource patterns.

**Prerequisite:** Phase 1-3 complete

---

## Tasks

### 4.1 Fix Ship Instance - Fuel Cost Methods
**File:** `game/strategy/data/ship_instance.py`

- [ ] Update `get_fuel_cost_per_hex()` to read from `resource_consumption_per_hex['fuel']`
- [ ] Update `get_warp_fuel_cost()` to read from `warp_resource_costs['fuel']`
- [ ] Update `get_warp_energy_cost()` to read from `warp_resource_costs['energy']`
- [ ] Remove any hardcoded fuel/energy cost calculations
- [ ] Ensure methods return data from ship stats/design, not calculate directly

**Target pattern:**
```python
def get_fuel_cost_per_hex(self) -> float:
    return self.stats.resource_consumption_per_hex.get('fuel', 0.0)

def get_warp_fuel_cost(self) -> float:
    return self.stats.warp_resource_costs.get('fuel', 0.0)
```

### 4.2 Fix Fleet - Resource Calculations
**File:** `game/strategy/data/fleet.py` (lines 144-427)

- [ ] Update fleet fuel cost aggregation to use ship resource methods
- [ ] Update `get_movement_resource_costs()` to aggregate from ships
- [ ] Update `has_resources_for_movement()` to check all resource types
- [ ] Update `consume_movement_resources()` to consume from ship resources
- [ ] Update warp resource methods similarly
- [ ] Remove hardcoded `fuel_cost_per_hex` references
- [ ] Remove hardcoded `warp_fuel_cost` / `warp_energy_cost` references

**Methods to update:**
- [ ] `get_fuel_cost_per_hex()` → use `get_movement_resource_costs()['fuel']`
- [ ] `get_warp_fuel_cost()` → use `get_warp_resource_costs()['fuel']`
- [ ] `fuel_endurance()` → calculate from resource costs
- [ ] `has_fuel_for_movement()` → use generic resource check
- [ ] `consume_fuel()` → use generic resource consumption

### 4.3 Fix Ship Stats Calculator - Legacy Handling
**File:** `game/strategy/services/ship_stats_calculator.py`

- [ ] Remove all `if 'XxxStorage' in abilities:` checks (already in Phase 1)
- [ ] Ensure `resource_storage` dict is populated from ResourceStorage abilities only
- [ ] Ensure `resource_consumption_per_hex` is populated from ResourceConsumption abilities
- [ ] Ensure `warp_resource_costs` is populated from ResourceConsumption (warp_jump trigger)
- [ ] Remove any legacy ability name references

### 4.4 Update Strategic Fuel/Energy Cost Fields
**Files:** Various

- [ ] Search for `strategic_fuel_per_hex` - replace with `resource_consumption_per_hex['fuel']`
- [ ] Search for `warp_energy_cost` - replace with `warp_resource_costs['energy']`
- [ ] Search for `warp_fuel_cost` - replace with `warp_resource_costs['fuel']`
- [ ] Update serialization to use new field names

### 4.5 Fix Ship Stats - Strategic Fields
**File:** `game/simulation/entities/ship_stats.py`

- [ ] Remove `strategic_fuel_per_hex` as separate field
- [ ] Use `resource_consumption_per_hex['fuel']` instead
- [ ] Update any code that reads `strategic_fuel_per_hex`

### 4.6 Run Strategic Tests
- [ ] Run `pytest tests/unit/strategy/` - all should pass
- [ ] Run `pytest tests/integration/strategy/` - all should pass
- [ ] Run fleet movement tests specifically

---

## Migration Patterns

### Ship Instance Methods
```python
# BEFORE
def get_fuel_cost_per_hex(self):
    return self._fuel_cost_per_hex  # Hardcoded field

# AFTER
def get_fuel_cost_per_hex(self):
    return self.stats.resource_consumption_per_hex.get('fuel', 0.0)
```

### Fleet Aggregation
```python
# BEFORE
total_fuel_cost = sum(ship.get_fuel_cost_per_hex() for ship in self.ships)

# AFTER
def get_movement_resource_costs(self) -> dict[str, float]:
    costs = {}
    for ship in self.ships:
        for resource, amount in ship.stats.resource_consumption_per_hex.items():
            costs[resource] = costs.get(resource, 0) + amount
    return costs
```

### Resource Checking
```python
# BEFORE
def has_fuel_for_movement(self, hexes: int) -> bool:
    return self.total_fuel >= self.get_fuel_cost_per_hex() * hexes

# AFTER
def has_resources_for_movement(self, hexes: int) -> bool:
    costs = self.get_movement_resource_costs()
    for resource, cost_per_hex in costs.items():
        total_needed = cost_per_hex * hexes
        if self.get_total_resource(resource) < total_needed:
            return False
    return True
```

---

## Files Modified
- `game/strategy/data/ship_instance.py`
- `game/strategy/data/fleet.py`
- `game/strategy/services/ship_stats_calculator.py`
- `game/simulation/entities/ship_stats.py`

---

## Verification

After this phase:
```bash
# Should return ZERO for hardcoded cost references
grep -rn "fuel_cost_per_hex" game/strategy/ --include="*.py" | grep -v "resource_consumption"
grep -rn "warp_fuel_cost" game/strategy/ --include="*.py" | grep -v "warp_resource_costs"
grep -rn "strategic_fuel_per_hex" game/ --include="*.py"

# Strategic tests should pass
pytest tests/unit/strategy/ tests/integration/strategy/ -v
```

---

## Notes

- Fleet methods may need to become generic (iterate over all resource types)
- Consider backwards-compatible method names that delegate to generic versions
- Warp costs should respect all resource types defined in ResourceConsumption with warp_jump trigger

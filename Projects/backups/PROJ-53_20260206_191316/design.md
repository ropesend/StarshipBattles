# PROJ-52: Design Document

## Architecture

### Modern Resource System (TARGET STATE)

```
ResourceConsumption
├── resource: str ("fuel", "energy", "ammo")
├── amount: float
├── trigger: str ("constant", "activation", "strategic_per_hex", "warp_jump")
└── Methods: update(), check_and_consume(), check_available()

ResourceStorage
├── resource: str
├── amount: float (max capacity)
└── Registers with ship.resources registry

ResourceGeneration
├── resource: str
├── amount: float (per second rate)
└── Registers regen rate with ship.resources
```

### Ship Resource Access (TARGET STATE)

```python
# All resource access through ResourceRegistry
ship.resources.get_value('fuel')        # Current value
ship.resources.get_max_value('fuel')    # Max capacity
ship.resources.get_resource('fuel')     # Full ResourceState object
ship.resources.set_value('fuel', 100)   # Set current
ship.resources.modify_value('fuel', -5) # Add/subtract
```

### JSON Schema (TARGET STATE)

```json
{
  "id": "component_id",
  "abilities": {
    "ResourceStorage": [
      {"resource": "fuel", "amount": 5000},
      {"resource": "energy", "amount": 1000}
    ],
    "ResourceGeneration": [
      {"resource": "energy", "amount": 50}
    ],
    "ResourceConsumption": [
      {"resource": "fuel", "amount": 0.5, "trigger": "constant"},
      {"resource": "energy", "amount": 10, "trigger": "activation"}
    ]
  }
}
```

---

## What Gets Deleted

### From `abilities/__init__.py`

```python
# DELETE THESE LAMBDA FACTORIES
"FuelStorage": lambda c, d: ResourceStorage(c, {"resource": "fuel", ...})
"EnergyStorage": lambda c, d: ResourceStorage(c, {"resource": "energy", ...})
"AmmoStorage": lambda c, d: ResourceStorage(c, {"resource": "ammo", ...})
"EnergyGeneration": lambda c, d: ResourceGeneration(c, {"resource": "energy", ...})
"EnergyConsumption": lambda c, d: ResourceConsumption(c, {"resource": "energy", ...})
"AmmoConsumption": lambda c, d: ResourceConsumption(c, {"resource": "ammo", ...})

# DELETE THESE CLASS MAPPINGS
ABILITY_CLASS_MAP = {
    "FuelStorage": "ResourceStorage",
    "EnergyStorage": "ResourceStorage",
    # etc.
}
```

### From `ship_stats_calculator.py`

```python
# DELETE THESE LEGACY CHECKS
if 'FuelStorage' in abilities:
    resource_storage['fuel'] = abilities['FuelStorage']
if 'EnergyStorage' in abilities:
    resource_storage['energy'] = abilities['EnergyStorage']
if 'AmmoStorage' in abilities:
    resource_storage['ammo'] = abilities['AmmoStorage']
```

### From Ship Classes

```python
# These properties should NOT exist or should raise errors:
ship.current_fuel    # -> ship.resources.get_value('fuel')
ship.max_fuel        # -> ship.resources.get_max_value('fuel')
ship.current_energy  # -> ship.resources.get_value('energy')
ship.max_energy      # -> ship.resources.get_max_value('energy')
ship.current_ammo    # -> ship.resources.get_value('ammo')
ship.max_ammo        # -> ship.resources.get_max_value('ammo')
```

---

## Conversion Examples

### Component JSON

**BEFORE:**
```json
{
  "id": "fuel_tank_medium",
  "abilities": {
    "FuelStorage": 5000
  }
}
```

**AFTER:**
```json
{
  "id": "fuel_tank_medium",
  "abilities": {
    "ResourceStorage": [
      {"resource": "fuel", "amount": 5000}
    ]
  }
}
```

### Multiple Resources

**BEFORE:**
```json
{
  "id": "power_plant",
  "abilities": {
    "EnergyStorage": 1000,
    "EnergyGeneration": 100
  }
}
```

**AFTER:**
```json
{
  "id": "power_plant",
  "abilities": {
    "ResourceStorage": [
      {"resource": "energy", "amount": 1000}
    ],
    "ResourceGeneration": [
      {"resource": "energy", "amount": 100}
    ]
  }
}
```

### Consumption

**BEFORE:**
```json
{
  "id": "shield_regen",
  "abilities": {
    "ShieldRegeneration": 5.0,
    "EnergyConsumption": 2.0
  }
}
```

**AFTER:**
```json
{
  "id": "shield_regen",
  "abilities": {
    "ShieldRegeneration": 5.0,
    "ResourceConsumption": [
      {"resource": "energy", "amount": 2.0, "trigger": "constant"}
    ]
  }
}
```

---

## Test Updates

### Pattern for Test Fixtures

**BEFORE:**
```python
abilities = {'EnergyStorage': 2000}
```

**AFTER:**
```python
abilities = {
    'ResourceStorage': [{'resource': 'energy', 'amount': 2000}]
}
```

### Pattern for Assertions

**BEFORE:**
```python
assert ship.max_fuel == 5000
assert ship.current_fuel == 2500
```

**AFTER:**
```python
assert ship.resources.get_max_value('fuel') == 5000
assert ship.resources.get_value('fuel') == 2500
```

---

## Verification Grep Commands

After migration, these should return NO results:

```bash
# Legacy ability names (should find ZERO)
grep -r "EnergyStorage" game/ --include="*.py"
grep -r "FuelStorage" game/ --include="*.py"
grep -r "AmmoStorage" game/ --include="*.py"
grep -r "EnergyGeneration" game/ --include="*.py"
grep -r "EnergyConsumption" game/ --include="*.py"
grep -r "AmmoGeneration" game/ --include="*.py"

# Direct property access (should find ZERO)
grep -r "\.current_fuel" game/ --include="*.py"
grep -r "\.max_fuel" game/ --include="*.py"
grep -r "\.current_energy" game/ --include="*.py"
grep -r "\.max_energy" game/ --include="*.py"
grep -r "\.current_ammo" game/ --include="*.py"
grep -r "\.max_ammo" game/ --include="*.py"

# JSON legacy patterns (should find ZERO)
grep -r '"EnergyStorage"' data/ --include="*.json"
grep -r '"FuelStorage"' data/ --include="*.json"
grep -r '"AmmoStorage"' data/ --include="*.json"
```

---

## Open Questions

1. **AmmoGeneration** - Does this ability need to be formally defined, or should all ammo generation use `ResourceGeneration` with `resource: "ammo"`?
   - **Decision:** Use `ResourceGeneration` with `resource: "ammo"` - no special AmmoGeneration ability needed.

2. **Shield as Resource** - Should shields be migrated to ResourceRegistry too?
   - **Decision:** Out of scope for this project. Shields remain as separate system for now.

3. **Warning Messages** - The validation system generates "Needs Fuel Storage" warnings. Should these change?
   - **Decision:** Update warning text to be resource-agnostic where possible, or keep for clarity.

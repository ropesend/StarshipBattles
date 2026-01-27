# Phase 2: Apply Modifiers in ShipStatsService

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-23 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update ShipStatsService.calculate_stats() to apply modifier multipliers from design data

---

## Tasks

### Task 2.1: Add imports to ShipStatsService [Simple]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** N/A (imports only)

- [ ] Add import near line ~19 (with other imports from game.simulation):
  ```python
  from game.simulation.components.modifiers import calculate_stat_multipliers
  ```
- [ ] Verify `get_modifier_registry` is already imported from `game.core.registry` (add if missing)
- [ ] Verify: No import errors when loading module

**Notes:** [Filled during implementation]

---

### Task 2.2: Get modifier_registry and calculate multipliers per component [Medium]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** `pytest tests/unit/strategy/test_ship_stats_service.py -v`

- [ ] In `calculate_stats()`, after building `formula_context` (around line 91), add:
  ```python
  # Get modifier registry once for all components
  modifier_registry = get_modifier_registry()
  ```
- [ ] Inside the main loop (around line 115, after `comp_id = comp_entry.get('id', '')`), add:
  ```python
  # Calculate modifier multipliers from design's component entry
  modifier_entries = comp_entry.get('modifiers', [])
  multipliers = calculate_stat_multipliers(modifier_entries, modifier_registry)
  ```
- [ ] Verify: multipliers dict is created for each component

**Notes:** [Filled during implementation]

---

### Task 2.3: Apply multipliers to mass and HP [Medium]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** `pytest tests/unit/strategy/test_ship_stats_service.py -v`

- [ ] Update mass calculation (around line 130) to apply mass_mult and mass_add:
  ```python
  # Mass - apply modifier multipliers
  comp_mass = ShipStatsService._get_numeric_value(comp_def, 'mass', 0, formula_context)
  comp_mass = (comp_mass + multipliers.get('mass_add', 0.0)) * multipliers.get('mass_mult', 1.0)
  total_mass += comp_mass
  ```
- [ ] Update HP calculation (around line 133) to apply hp_mult:
  ```python
  # HP - apply modifier multiplier
  comp_hp = ShipStatsService._get_numeric_value(comp_def, 'max_hp', 0, formula_context)
  comp_hp *= multipliers.get('hp_mult', 1.0)
  total_hp += comp_hp * effectiveness
  ```
- [ ] Verify: Mass and HP correctly scaled when modifiers present

**Notes:** [Filled during implementation]

---

### Task 2.4: Apply capacity_mult to ResourceStorage [Medium]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** `pytest tests/unit/strategy/test_ship_stats_service.py -v`

- [ ] Update ResourceStorage handling (around lines 172-180):
  ```python
  # Resource Storage - apply capacity_mult from modifiers
  for ability_data in ShipStatsService._get_ability_list(abilities, 'ResourceStorage'):
      resource_type = ability_data.get('resource', '')
      base_amount = ShipStatsService._evaluate_value(
          ability_data.get('max_amount') or ability_data.get('amount', 0), 0, formula_context
      )
      # Apply capacity multiplier from design modifiers
      scaled_amount = base_amount * multipliers.get('capacity_mult', 1.0)
      if resource_type:
          resource_storage[resource_type] = (
              resource_storage.get(resource_type, 0) + scaled_amount * effectiveness
          )
  ```
- [ ] Update FuelStorage shortcut (around line 184):
  ```python
  if 'FuelStorage' in abilities:
      val = ShipStatsService._get_ability_value(abilities, 'FuelStorage', formula_context)
      val *= multipliers.get('capacity_mult', 1.0)
      resource_storage['fuel'] = resource_storage.get('fuel', 0) + val * effectiveness
  ```
- [ ] Update EnergyStorage shortcut (around line 187):
  ```python
  if 'EnergyStorage' in abilities:
      val = ShipStatsService._get_ability_value(abilities, 'EnergyStorage', formula_context)
      val *= multipliers.get('capacity_mult', 1.0)
      resource_storage['energy'] = resource_storage.get('energy', 0) + val * effectiveness
  ```
- [ ] Update AmmoStorage shortcut (around line 190):
  ```python
  if 'AmmoStorage' in abilities:
      val = ShipStatsService._get_ability_value(abilities, 'AmmoStorage', formula_context)
      val *= multipliers.get('capacity_mult', 1.0)
      resource_storage['ammo'] = resource_storage.get('ammo', 0) + val * effectiveness
  ```
- [ ] Verify: Battery with size 20 now returns 40,000 energy (not 2,000)

**Notes:** [Filled during implementation]

---

### Task 2.5: Apply strategic_mult to StrategicMovement [Simple]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** `pytest tests/unit/strategy/test_ship_stats_service.py -v`

- [ ] Update StrategicMovement handling (around line 194-196):
  ```python
  # Strategic Movement - apply strategic_mult from modifiers
  if 'StrategicMovement' in abilities:
      movement = ShipStatsService._get_ability_value(abilities, 'StrategicMovement', formula_context)
      movement *= multipliers.get('strategic_mult', 1.0)
      total_strategic_movement += movement * effectiveness
  ```
- [ ] Verify: Engines with size modifiers correctly scale movement

**Notes:** [Filled during implementation]

---

### Task 2.6: Apply consumption_mult to ResourceConsumption [Simple]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** `pytest tests/unit/strategy/test_ship_stats_service.py -v`

- [ ] Update ResourceConsumption handling (around lines 199-211):
  ```python
  # Resource Consumption - apply consumption_mult from modifiers
  for ability_data in ShipStatsService._get_ability_list(abilities, 'ResourceConsumption'):
      resource_type = ability_data.get('resource', '')
      amount = ShipStatsService._evaluate_value(ability_data.get('amount', 0), 0, formula_context)
      # Apply consumption multiplier from design modifiers
      amount *= multipliers.get('consumption_mult', 1.0)
      trigger = ability_data.get('trigger', 'constant')

      # ... rest of trigger handling unchanged
  ```
- [ ] Verify: Components with efficiency modifiers correctly scale consumption

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/unit/strategy/test_ship_stats_service.py -v` - all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3

# Phase 1: Extract Shared Modifier Logic

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-23 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create pure functions for modifier calculation in modifiers.py, then refactor Component to use them

---

## Tasks

### Task 1.1: Add `get_default_stat_multipliers()` function [Simple]
**File:** `game/simulation/components/modifiers.py`
**Tests:** `pytest tests/unit/components/test_modifiers.py -v`

- [ ] Add import at top if needed: `from typing import Dict, Any, List`
- [ ] Add function at end of file (after `apply_modifier_effects`):
```python
def get_default_stat_multipliers() -> Dict[str, Any]:
    """
    Return default stat multipliers dictionary.

    This is the canonical list of all supported modifier stats.
    Used by both Component and ShipStatsService for consistency.

    Returns:
        Dict with all stat keys initialized to neutral values
        (1.0 for multipliers, 0.0 for additive, None for set operations)
    """
    return {
        'mass_mult': 1.0,
        'hp_mult': 1.0,
        'damage_mult': 1.0,
        'range_mult': 1.0,
        'cost_mult': 1.0,
        'thrust_mult': 1.0,
        'turn_mult': 1.0,
        'strategic_mult': 1.0,
        'energy_gen_mult': 1.0,
        'capacity_mult': 1.0,
        'crew_capacity_mult': 1.0,
        'life_support_capacity_mult': 1.0,
        'consumption_mult': 1.0,
        'mass_add': 0.0,
        'arc_add': 0.0,
        'accuracy_add': 0.0,
        'arc_set': None,
        'properties': {},
        'reload_mult': 1.0,
        'endurance_mult': 1.0,
        'projectile_hp_mult': 1.0,
        'projectile_damage_mult': 1.0,
        'projectile_stealth_level': 0.0,
        'crew_req_mult': 1.0,
    }
```
- [ ] Verify: Function returns dict with all expected keys

**Notes:** [Filled during implementation]

---

### Task 1.2: Add `calculate_stat_multipliers()` function [Simple]
**File:** `game/simulation/components/modifiers.py`
**Tests:** `pytest tests/unit/components/test_modifiers.py -v`

- [ ] Add function after `get_default_stat_multipliers`:
```python
def calculate_stat_multipliers(
    modifier_entries: List[Dict[str, Any]],
    modifier_registry: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate stat multipliers from a list of modifier entries.

    Pure function - no side effects, no object state needed.
    Used by both Component and ShipStatsService for consistent modifier handling.

    Args:
        modifier_entries: List of dicts with 'id' and 'value' keys
                         e.g., [{'id': 'simple_size_mount', 'value': 20.0}]
        modifier_registry: Dict mapping modifier IDs to Modifier definitions

    Returns:
        Dict of stat_key -> value (multipliers, additive values, etc.)
    """
    stats = get_default_stat_multipliers()

    for mod_entry in modifier_entries:
        mod_id = mod_entry.get('id')
        mod_value = mod_entry.get('value')

        mod_def = modifier_registry.get(mod_id)
        if mod_def:
            apply_modifier_effects(mod_def, mod_value, stats)

    return stats
```
- [ ] Verify: Function correctly applies modifiers to stats dict

**Notes:** [Filled during implementation]

---

### Task 1.3: Refactor Component._calculate_modifier_stats() [Medium]
**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/components/ -v`

- [ ] Locate `_calculate_modifier_stats()` method (around line 546)
- [ ] Add import at top of method or file:
  ```python
  from game.simulation.components.modifiers import calculate_stat_multipliers, get_default_stat_multipliers
  ```
- [ ] Replace the stats initialization and modifier loop with:
  ```python
  def _calculate_modifier_stats(self):
      from game.simulation.components.modifiers import calculate_stat_multipliers
      from game.core.registry import get_modifier_registry

      # Convert ApplicationModifier list to entry format for shared function
      modifier_entries = [
          {'id': m.definition.id, 'value': m.value}
          for m in self.modifiers
      ]

      stats = calculate_stat_multipliers(modifier_entries, get_modifier_registry())
      return stats
  ```
- [ ] Run tests: `pytest tests/unit/components/ -v` - all should pass
- [ ] Verify: Component still calculates same stats as before

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/unit/components/ -v` - all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2

# Phase 3: Unify Action Time Resolvers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-238 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Merge PlanetActionTimeResolver into ActionTimeResolver. Single mapping dict for all order types with (ability_name, time_field) tuples. Delete planet_action_time_resolver.py.

---

## Tasks

### Task 3.1: Extend ActionTimeResolver [Medium]
**File:** `game/strategy/services/action_time_resolver.py`
- [ ] Change `ORDER_TO_ABILITY_MAP` to include planet orders with `(ability_name, time_field)` tuples:
  ```python
  ORDER_TO_ABILITY_MAP = {
      OrderType.COLONIZE: ('ColonizePlanet', 'action_time'),
      OrderType.ACTIVATE_SHIELD: ('PlanetaryShield', 'activation_time'),
      OrderType.DEACTIVATE_SHIELD: ('PlanetaryShield', 'deactivation_time'),
      # ... existing entries
  }
  ```
- [ ] Add method to search facility components (not just ship components)
- [ ] `resolve_action_time()` accepts either Fleet or Planet entity (use IOrderable or duck typing)

### Task 3.2: Update Callers [Simple]
- [ ] `game/strategy/engine/planet_action_engine.py` — use ActionTimeResolver instead of PlanetActionTimeResolver
- [ ] `game/strategy/engine/turn_engine.py` — remove PlanetActionTimeResolver import from planet_action_engine lazy property

### Task 3.3: Delete PlanetActionTimeResolver [Simple]
- [ ] Delete `game/strategy/services/planet_action_time_resolver.py`
- [ ] Delete or update `tests/unit/strategy/services/test_planet_action_time_resolver.py`

### Task 3.4: Verify [Simple]
- [ ] `python -m pytest tests/ -n 12 -q` — same count as baseline

---

## Phase Completion Checklist
- [ ] Single ActionTimeResolver handles both fleet and planet orders
- [ ] PlanetActionTimeResolver deleted
- [ ] All tests pass

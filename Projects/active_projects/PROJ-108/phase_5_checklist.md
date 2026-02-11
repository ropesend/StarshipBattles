# Phase 5: Simulation Layer Deduplication

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-108 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Consolidate ability aggregator duplication and modifier validation overlap.
**Findings:** DUP-SIM-001, DUP-SIM-002, DUP-SIM-003, DUP-SIM-005

---

## Tasks

### Task 5.1: Merge ability aggregator functions [Medium]
**File:** `game/simulation/entities/ability_aggregator.py`
**Tests:** `pytest tests/unit/entities/test_ability_aggregator_layers.py -v`

Merge `calculate_ability_totals()` (lines 70-148) and `calculate_ability_totals_for_layer()` (lines 165-229) into a single function.

- [x] Add `layer: Optional[AbilityLayer] = None` and `scope_filter: Optional[AbilityScope] = None` params to `calculate_ability_totals()`
- [x] When `layer is not None`:
  - Skip components without `ability_instances` (line 193-194 logic)
  - Skip non-list `ability_instances` (line 196-197 logic)
  - Add `if not ab.applies_to_layer(layer): continue` filter (line 201 logic)
  - Add `if scope_filter is not None and ab.scope != scope_filter: continue` filter (line 205 logic)
  - Skip the raw dictionary processing block (Section 2, lines 121-145) when `layer is not None`
- [x] When `layer is None`: preserve existing behavior exactly (process both instances and dicts)
- [x] Delete `calculate_ability_totals_for_layer()` function entirely (lines 165-229)
- [x] Update `get_ability_total()` (line 151-162) -- no changes needed, it calls `calculate_ability_totals()`
- [x] Update all callers of `calculate_ability_totals_for_layer()`:

**Callers to update:**
  - `tests/unit/entities/test_ability_aggregator_layers.py` (8 imports on lines 68, 93, 117, 136, 159, 177, 185, 207)
    - [x] Change `from ...ability_aggregator import calculate_ability_totals_for_layer` to `from ...ability_aggregator import calculate_ability_totals`
    - [x] Change all calls from `calculate_ability_totals_for_layer(components, layer, scope)` to `calculate_ability_totals(components, layer=layer, scope_filter=scope)`
  - Search for any production code callers:
    - [x] `grep -r "calculate_ability_totals_for_layer" game/` -- no production callers

- [x] Verify: `pytest tests/unit/entities/test_ability_aggregator_layers.py -v` passes (13 passed)
- [x] Verify: `pytest tests/ -n 12` passes

### Task 5.2: Consolidate modifier validation [Medium]
**File:** `game/simulation/components/modifier_schema.py`, `game/simulation/components/modifier_effects.py`
**Tests:** `pytest tests/unit/refactor/test_modifier_json_schema.py -v`

The overlap is between `modifier_schema.py:validate_effect_v2()` (structural validation: required fields, types) and `modifier_effects.py:validate_formula()` + `validate_modifier_definition()` (semantic validation: formula correctness, defined variables). These serve **different purposes** but the outer `validate_modifier_v2()` in schema doesn't call the formula validation.

- [x] Add formula validation call inside `modifier_schema.py:validate_modifier_v2()`:
  After validating each effect structurally (line 244-246), also validate formula via delegation to ModifierEffectEvaluator.validate_formula()
- [x] modifier_effects.py:validate_modifier_definition() already does semantic-only validation - no change needed
- [x] Verify: `pytest tests/unit/refactor/test_modifier_json_schema.py -v` passes (21 passed)
- [x] Verify: `pytest tests/ -n 12` passes

**Note:** The goal is NOT to merge the two files. It's to have `modifier_schema` delegate formula
validation to `modifier_effects` so there's no drift. Structural validation stays in schema.

### Task 5.3: Extract ability filtering utility [Simple]
**File:** `game/simulation/entities/ability_aggregator.py` (or new utility)
**Tests:** `pytest tests/unit/entities/ -v`

DUP-SIM-002: The pattern of iterating `component.ability_instances` and checking `__class__.__name__`
for a specific ability class appears in `combat_endurance.py:36-79` and `ship_stats.py:274-295`.

- [x] Add utility function to `ability_aggregator.py`:
  - Added `get_ability_instances_by_class(components, class_name)` generator function
  - Yields (component, ability) tuples for abilities matching class_name
  - Full docstring with example usage
- [x] Verify: `pytest tests/unit/entities/ -v` passes (367 passed)
- [x] Verify: `pytest tests/ -n 12` passes (8237 passed)

**Note:** Migrating callers in combat_endurance.py and ship_stats.py is optional for this phase.
The loop structures in those files do more than just filter (they accumulate per-resource-type),
so the utility provides a building block but doesn't fully replace the loops. The key value is
establishing the pattern for future use.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `calculate_ability_totals_for_layer` no longer exists as a separate function
- [x] `modifier_schema.validate_modifier_v2()` delegates formula validation to modifier_effects
- [x] `get_ability_instances_by_class()` utility exists
- [x] `pytest tests/ -n 12` -- full suite passes (8237 tests)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

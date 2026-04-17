# Phase 1: Create Registry Module + Unit Tests (TDD)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-273 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Establish the shared registry module with full unit test coverage, before touching any existing compiler.

---

## Tasks

### Task 1.1: Write failing tests for registry [Simple]
**File:** `tests/unit/simulation/combat/test_ability_stat_registry.py` (NEW)
**Tests:** `pytest tests/unit/simulation/combat/test_ability_stat_registry.py -v`

- [ ] Create test file with module docstring
- [ ] Test `ABILITY_STAT_REGISTRY` contains exactly 3 keys: `ShieldProjection`, `ShieldModifier`, `DamageModifier`
- [ ] Test each mapping's `stat_key` matches current behavior (`shield_bonus_add`, `shield_capacity_mult`, `damage_mult`)
- [ ] Test each mapping's `operation` matches current behavior (`add`, `multiply`, `multiply`)
- [ ] Test `AbilityStatMapping` is frozen (pytest.raises(FrozenInstanceError) on assignment)
- [ ] Run tests — verify they ALL fail (module doesn't exist yet)

**Notes:**

### Task 1.2: Write failing tests for `emit_entries_for_ability` helper [Medium]
**File:** `tests/unit/simulation/combat/test_ability_stat_registry.py`
**Tests:** `pytest tests/unit/simulation/combat/test_ability_stat_registry.py -v`

- [ ] Test: unknown ability name returns empty list
- [ ] Test: `self` scope with `owner_team=0` returns single entry for team 0
- [ ] Test: `enemy_sector` scope with `owner_team=0, num_teams=2` returns single entry for team 1
- [ ] Test: `enemy_system` scope with `owner_team=0, num_teams=2` returns single entry for team 1
- [ ] Test: dict-shaped `ability_data` with `value` field extracts correctly (ShieldProjection)
- [ ] Test: dict-shaped `ability_data` with `multiplier` field extracts correctly (ShieldModifier)
- [ ] Test: primitive numeric `ability_data` treated as value
- [ ] Test: zero/falsy value returns empty list (no stat change)
- [ ] Test: `stack_group` parameter threads through to emitted ModifierEntry
- [ ] Test: `source` parameter threads through
- [ ] Run tests — verify they fail

**Notes:**

### Task 1.3: Implement `AbilityStatMapping` dataclass + `ABILITY_STAT_REGISTRY` [Simple]
**File:** `game/simulation/combat/ability_stat_registry.py` (NEW)
**Tests:** `pytest tests/unit/simulation/combat/test_ability_stat_registry.py -v`

- [ ] Create module with module docstring explaining its role
- [ ] Define `@dataclass(frozen=True) class AbilityStatMapping` with fields: `ability_class_name: str`, `stat_key: str`, `operation: Literal["add", "multiply"]`, `value_field: str`
- [ ] Define module-level `ABILITY_STAT_REGISTRY: Dict[str, AbilityStatMapping]` with the 3 current mappings
- [ ] Run registry tests — Task 1.1 tests should now pass

**Notes:**

### Task 1.4: Implement `emit_entries_for_ability` helper [Medium]
**File:** `game/simulation/combat/ability_stat_registry.py`
**Tests:** `pytest tests/unit/simulation/combat/test_ability_stat_registry.py -v`

- [ ] Add imports: `ModifierEntry`, `ModifierEffect` from `game.simulation.combat.modifier_stack`
- [ ] Implement signature: `emit_entries_for_ability(ability_name, ability_data, *, scope, owner_team, num_teams, source, stack_group=None) -> List[ModifierEntry]`
- [ ] Logic: lookup mapping; if not in registry, return `[]`
- [ ] Logic: extract value from `ability_data` — dict path reads `mapping.value_field`; primitive path uses the primitive directly
- [ ] Logic: if value is falsy (0 / 0.0), return `[]`
- [ ] Logic: route team_ids — `enemy_*` scopes fan out to `[t for t in range(num_teams) if t != owner_team]`; otherwise `[owner_team]`
- [ ] Logic: emit one `ModifierEntry` per target team with `ModifierEffect(stat_key=..., operation=..., value=...)`, `stack_group`, `source`
- [ ] Run all tests — Task 1.2 tests should now pass

**Notes:**

### Task 1.5: Verify baseline test suite green [Simple]
**File:** N/A (test run only)
**Tests:** `pytest tests/unit/simulation/combat/ tests/unit/ui/screens/battle_setup/ tests/unit/strategy/combat/ -n 12`

- [ ] Run targeted test suites — all green (no regressions from new module)
- [ ] New registry tests pass
- [ ] No import errors surfaced

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-273 1` and confirm PASSED

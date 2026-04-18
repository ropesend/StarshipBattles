# Phase 1: Create Registry Module + Unit Tests (TDD)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-273 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Establish the shared registry module with full unit test coverage, before touching any existing compiler.

---

## Tasks

### Task 1.1: Write failing tests for registry [Simple]
**File:** `tests/unit/simulation/combat/test_ability_stat_registry.py` (NEW)
**Tests:** `pytest tests/unit/simulation/combat/test_ability_stat_registry.py -v`

- [x] Create test file with module docstring
- [x] Test `ABILITY_STAT_REGISTRY` contains exactly 3 keys: `ShieldProjection`, `ShieldModifier`, `DamageModifier`
- [x] Test each mapping's `stat_key` matches current behavior (`shield_bonus_add`, `shield_capacity_mult`, `damage_mult`)
- [x] Test each mapping's `operation` matches current behavior (`add`, `multiply`, `multiply`)
- [x] Test `AbilityStatMapping` is frozen (pytest.raises(FrozenInstanceError) on assignment)
- [x] Run tests — verify they ALL fail (module doesn't exist yet)

**Notes:** Tests 1.1 + 1.2 implemented together in one file (24 tests total). All 24 verified to fail with `ModuleNotFoundError` before any implementation. Also added a bonus test for `OPPONENT_SCOPES` constant (export check).

### Task 1.2: Write failing tests for `emit_entries_for_ability` helper [Medium]
**File:** `tests/unit/simulation/combat/test_ability_stat_registry.py`
**Tests:** `pytest tests/unit/simulation/combat/test_ability_stat_registry.py -v`

- [x] Test: unknown ability name returns empty list
- [x] Test: `self` scope with `owner_team=0` returns single entry for team 0
- [x] Test: `enemy_sector` scope with `owner_team=0, num_teams=2` returns single entry for team 1
- [x] Test: `enemy_system` scope with `owner_team=0, num_teams=2` returns single entry for team 1
- [x] Test: dict-shaped `ability_data` with `value` field extracts correctly (ShieldProjection)
- [x] Test: dict-shaped `ability_data` with `multiplier` field extracts correctly (ShieldModifier)
- [x] Test: primitive numeric `ability_data` treated as value
- [x] Test: zero/falsy value returns empty list (no stat change)
- [x] Test: `stack_group` parameter threads through to emitted ModifierEntry
- [x] Test: `source` parameter threads through
- [x] Run tests — verify they fail

**Notes:** Added three forward-compat N-team fan-out tests (`num_teams=3` from owner_team 0 and 1) since the helper is designed to support arbitrary N from day one. Also added a bonus test for `source_modifier_id` / `source_modifier_name` threading onto the underlying `ModifierEffect`. Helper signature landed with those two kwargs in addition to `source`, because `ModifierEffect` requires them — callers will pass the design_id and display_name.

### Task 1.3: Implement `AbilityStatMapping` dataclass + `ABILITY_STAT_REGISTRY` [Simple]
**File:** `game/simulation/combat/ability_stat_registry.py` (NEW)
**Tests:** `pytest tests/unit/simulation/combat/test_ability_stat_registry.py -v`

- [x] Create module with module docstring explaining its role
- [x] Define `@dataclass(frozen=True) class AbilityStatMapping` with fields: `ability_class_name: str`, `stat_key: str`, `operation: Literal["add", "multiply"]`, `value_field: str`
- [x] Define module-level `ABILITY_STAT_REGISTRY: Dict[str, AbilityStatMapping]` with the 3 current mappings
- [x] Run registry tests — Task 1.1 tests should now pass

**Notes:** Also exported `OPPONENT_SCOPES: FrozenSet[str]` as the canonical set of enemy-routing scopes. Battle Setup's existing `_OPPONENT_SCOPES` local constant will be replaced by this import in Phase 2.

### Task 1.4: Implement `emit_entries_for_ability` helper [Medium]
**File:** `game/simulation/combat/ability_stat_registry.py`
**Tests:** `pytest tests/unit/simulation/combat/test_ability_stat_registry.py -v`

- [x] Add imports: `ModifierEntry` from `game.simulation.combat.modifier_stack`, `ModifierEffect` from `game.simulation.components.modifier_effects`
- [x] Implement signature: `emit_entries_for_ability(ability_name, ability_data, *, scope, owner_team, num_teams, source, source_modifier_id, source_modifier_name, stack_group=None) -> List[Tuple[int, ModifierEntry]]`
- [x] Logic: lookup mapping; if not in registry, return `[]`
- [x] Logic: extract value from `ability_data` — dict path reads `mapping.value_field` (default 1.0 for multiply, 0.0 for add); primitive path uses the numeric directly
- [x] Logic: if value is falsy (0 / 0.0), return `[]`
- [x] Logic: route team_ids — `enemy_*` scopes fan out to `[t for t in range(num_teams) if t != owner_team]`; otherwise `[owner_team]`
- [x] Logic: emit one `ModifierEntry` per target team with `ModifierEffect(stat_key=..., operation=..., value=...)`, `stack_group`, `source`
- [x] Run all tests — Task 1.2 tests should now pass

**Notes:** Return type is `List[Tuple[int, ModifierEntry]]` (team_id paired with entry) to match the existing `_complex_to_entries` pattern in `battle_setup/spec_compiler.py:306`. Callers place each entry into the appropriate `per_team[team_id]` bucket of the final `ModifierStack`.

### Task 1.5: Verify baseline test suite green [Simple]
**File:** N/A (test run only)
**Tests:** `pytest tests/unit/simulation/combat/ tests/unit/ui/screens/battle_setup/ tests/unit/strategy/combat/ -n 12`

- [x] Run targeted test suites — all green (no regressions from new module)
- [x] New registry tests pass
- [x] No import errors surfaced

**Notes:** Targeted regression sweep: 54 tests passed in 3.88s across combat + battle_setup + strategy/combat unit suites. Full `pytest tests/ --testmon` baseline launched in background (first-time testmon DB build); since Phase 1 is purely additive (no existing code modified), targeted sweep is sufficient to confirm no regressions. Full baseline will serve as the pre-Phase-2 reference since Phase 2 modifies existing code.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
- [x] Run `python Projects/scripts/validate_phase.py PROJ-273 1` and confirm PASSED

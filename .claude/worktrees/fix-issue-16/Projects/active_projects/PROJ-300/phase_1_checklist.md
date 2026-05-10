# Phase 1: Aggregation framework — `aggregate_rates`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-300 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (2026-04-27)
**Objective:** Add a rate-style aggregator that mirrors `aggregate_multipliers`'s shape but uses inter-group SUM (not MULTIPLY) and default 0.0 (not 1.0). Smallest, most isolated change in the project — establishes the rate-vs-multiplier distinction the rest of the work depends on.

---

## Tasks

### Task 1.1: Write failing tests for `aggregate_rates` [Simple]
**File:** `tests/unit/strategy/services/test_strategic_ability_scanner.py`
**Tests:** `pytest tests/unit/strategy/services/test_strategic_ability_scanner.py -k aggregate_rates`

- [ ] Locate the existing `TestAggregateMultipliers` test class (look for `aggregate_multipliers` references) to confirm the test pattern.
- [ ] Add a new `TestAggregateRates` class with these tests:
  - [ ] `test_empty_returns_zero` — `aggregate_rates([])` returns `0.0`.
  - [ ] `test_single_entry_returns_its_rate` — one entry with `rate=0.5` returns `0.5`.
  - [ ] `test_intra_group_max` — two entries with `rate=0.5` and `rate=0.8` in the same `stack_group` return `0.8` (not `1.3`).
  - [ ] `test_inter_group_sum` — two entries with `rate=0.5` and `rate=0.3` in DIFFERENT `stack_group`s return `0.8` (sum, not multiply).
  - [ ] `test_ungrouped_entries_each_own_group` — two entries with `rate=0.4` and no `stack_group` return `0.8`.
  - [ ] `test_mixed_grouped_and_ungrouped` — one entry in group `A` with `rate=0.5`, two entries in group `B` with `rate=0.3` and `rate=0.4`, plus an ungrouped `rate=0.2` returns `0.5 + max(0.3, 0.4) + 0.2 = 1.1`.
- [ ] Run the test file — confirm all six tests FAIL with `AttributeError` (function doesn't exist yet) or similar.

**Notes:**

### Task 1.2: Implement `aggregate_rates` [Simple]
**File:** `game/strategy/services/strategic_ability_scanner.py`
**Tests:** `pytest tests/unit/strategy/services/test_strategic_ability_scanner.py -k aggregate_rates`

- [ ] Read the existing `aggregate_multipliers(entries)` implementation (around lines 102-143).
- [ ] Add `aggregate_rates(entries) -> float` directly below it. Same group-key handling (`stack_group` or generated `__ungrouped_N`); intra-group MAX; **inter-group SUM**; default `0.0`.
- [ ] Read entry's rate from `entry.get('rate', 0.0)` (vs `entry.get('multiplier', 1.0)` in the existing function).
- [ ] Run tests — confirm all six pass.
- [ ] Add a module docstring update if needed (pattern: "Functions for aggregating multiplier-style and rate-style abilities.").

**Notes:**

### Task 1.3: Add ValidationException for mixed-kind groups [Simple]
**File:** `game/strategy/services/strategic_ability_scanner.py`
**Tests:** `pytest tests/unit/strategy/services/test_strategic_ability_scanner.py -k mixed_kind`

- [ ] Add a test `test_aggregate_multipliers_rejects_rate_entries` — an entry with `rate=0.5` (no `multiplier`) passed to `aggregate_multipliers` raises `ValidationException` (or returns 1.0 with a warning, choose at implementation time and document in decisions.md).
- [ ] Add a test `test_aggregate_rates_rejects_multiplier_entries` — symmetric.
- [ ] Implement: in `aggregate_multipliers`, raise `ValidationException` if any entry lacks `multiplier` and has `rate`; symmetric check in `aggregate_rates`. Use `from game.core.exceptions import ValidationException`.
- [ ] Verify tests pass.

**Notes:** If implementation finds the strict check causes false positives in existing call sites, downgrade to a warning + skip-the-entry approach and document in decisions.md.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/services/test_strategic_ability_scanner.py` fully green
- [ ] `pytest tests/ --testmon` — no regressions
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2

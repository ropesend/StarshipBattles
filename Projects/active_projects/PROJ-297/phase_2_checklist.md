# Phase 2: Stale Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-297 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Restore the test suite to a fully-collectible state. 3 test files currently fail `pytest --collect-only` because they import symbols that have been removed from the codebase. User decision (2026-04-26): investigate per-file before deletion to confirm equivalent coverage exists elsewhere.

---

## Investigation Methodology (apply to each task)

For each stale test:
1. Identify the missing symbol (already known per the `--collect-only` ImportError)
2. `git log --all --diff-filter=D -- "**/<symbol>*"` — when was it removed?
3. `git log --all -S "<symbol>" --oneline` — find the last commit that referenced it
4. Read the deleting commit's message to understand the rename/removal context
5. Check whether the underlying behavior is now tested elsewhere (grep for replacement symbol)
6. **Decision rule:**
   - If equivalent coverage exists → DELETE the stale test file
   - If no replacement coverage exists AND the underlying behavior still matters → write replacement tests targeting the current implementation, then delete the stale file
   - If the behavior was deliberately removed (e.g. feature deleted) → DELETE the stale test file

---

## Tasks

### Task 2.1: Resolve `tests/unit/ai/test_ai_protocols.py` [Simple]
**File:** `tests/unit/ai/test_ai_protocols.py`
**Tests:** `pytest tests/unit/ai/test_ai_protocols.py --collect-only`

ImportError: `cannot import name 'IFormationMaster' from 'game.ai.protocols'`

- [ ] `git log --all -S "IFormationMaster" --oneline` — find when removed
- [ ] Read the deleting commit's message
- [ ] `grep -rn "IFormationMaster\|FormationMaster" game/` — confirm fully removed (or replaced)
- [ ] If replaced: identify the replacement protocol (likely related to PROJ-275 N-team work or a fleet-formation refactor)
- [ ] Read `tests/unit/ai/test_ai_protocols.py` — list every test function and what it asserts. Document in **Notes** below.
- [ ] For each test function, search for equivalent coverage: `grep -rn "<assertion symbol>" tests/`
- [ ] Apply decision rule:
  - [ ] If covered elsewhere → delete `tests/unit/ai/test_ai_protocols.py`
  - [ ] If NOT covered → write replacement tests targeting current AI protocols in a new (or existing) test file, THEN delete the stale file
- [ ] **Verification:** `pytest tests/unit/ai/test_ai_protocols.py --collect-only` does not error (either zero collected — file deleted — or all tests collect cleanly)

**Notes:** [Filled during investigation — list tests, replacement coverage, final disposition]

---

### Task 2.2: Resolve `tests/unit/ai/test_behavior_units.py` [Simple]
**File:** `tests/unit/ai/test_behavior_units.py`
**Tests:** `pytest tests/unit/ai/test_behavior_units.py --collect-only`

ImportError: `cannot import name 'FormationBehavior' from 'game.ai.behaviors'`

- [ ] `git log --all -S "FormationBehavior" --oneline` — find when removed
- [ ] Read the deleting commit's message
- [ ] `grep -rn "FormationBehavior" game/` — confirm fully removed
- [ ] Read `tests/unit/ai/test_behavior_units.py` — document what behaviors are tested
- [ ] Check current `game/ai/behaviors.py` exports — what behavior classes exist now?
- [ ] For each test function, search for equivalent coverage in current behavior tests
- [ ] Apply decision rule:
  - [ ] If covered → delete the stale file
  - [ ] If not covered → write replacement tests for current behaviors, THEN delete stale file
- [ ] **Verification:** `pytest tests/unit/ai/test_behavior_units.py --collect-only` does not error

**Notes:**

---

### Task 2.3: Resolve `tests/unit/strategy/engine/test_build_order_command_handler.py` [Simple]
**File:** `tests/unit/strategy/engine/test_build_order_command_handler.py`
**Tests:** `pytest tests/unit/strategy/engine/test_build_order_command_handler.py --collect-only`

ImportError: `cannot import name 'create_auto_load_population_order' from 'game.strategy.engine.command_handlers'`

- [ ] `git log --all -S "create_auto_load_population_order" --oneline` — find when removed
- [ ] Read the deleting commit's message — likely related to a refactor of build-order command handling
- [ ] `grep -rn "create_auto_load_population_order\|auto_load_population" game/` — confirm fully removed
- [ ] Read `tests/unit/strategy/engine/test_build_order_command_handler.py` — what is being tested? Build orders? Auto-load population behavior?
- [ ] Check `game/strategy/engine/command_handlers.py` for the current build-order command handler — what's exported now?
- [ ] Search for replacement coverage: `grep -rn "BuildOrderCommandHandler\|IssueBuildOrderCommand" tests/`
- [ ] Apply decision rule
- [ ] **Verification:** `pytest tests/unit/strategy/engine/test_build_order_command_handler.py --collect-only` does not error

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/ai/ tests/unit/strategy/engine/ --collect-only` shows zero collection errors
- [ ] Full sharded suite (`python Tools/test_sharded/test_sharded.py`) at 15112+ passing
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 3: Documentation Fixes)

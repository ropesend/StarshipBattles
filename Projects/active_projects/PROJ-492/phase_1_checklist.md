# Phase 1: HLP-002 nested MockPlanetType migration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-492 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace ~12+ nested method-local `class MockPlanetType(Enum)` definitions in test files with `from tests.fixtures.colonization_fixtures import MockPlanetType`.

**Mechanical pattern:** for each file, delete inline Enum class, add module-level import, verify enum member names match (extend canonical if needed).

---

## Tasks

### Task 1.1: Audit canonical MockPlanetType
**File:** `tests/fixtures/colonization_fixtures.py`
**Tests:** none — read-only

- [ ] List all enum members currently in canonical `MockPlanetType` (e.g. CONTINENTAL, ICE_DWARF, ARID, DYSON_SPHERE).
- [ ] Record the list in this checklist for reference.

### Task 1.2: Migrate test_colonization_facade.py (highest density — 9 inline copies)
**File:** `tests/integration/ui/test_colonization_facade.py` (lines 71, 380, 441, 494, 583, 642, 697, 751, 819)
**Tests:** `pytest tests/integration/ui/test_colonization_facade.py`

- [ ] For each of the 9 inline `class MockPlanetType(Enum):` definitions, audit member names against canonical.
- [ ] If any inline definition uses an enum member NOT in canonical, extend canonical Enum first (then update Task 1.1's recorded list).
- [ ] Add `from tests.fixtures.colonization_fixtures import MockPlanetType` at module level.
- [ ] Delete all 9 inline definitions.
- [ ] Verify: tests pass.

### Task 1.3: Migrate test_commands.py
**File:** `tests/integration/strategy/test_commands.py`
**Tests:** `pytest tests/integration/strategy/test_commands.py`

- [ ] Same pattern as Task 1.2.
- [ ] Verify: tests pass.

### Task 1.4: Migrate tests/unit/strategy/turn_engine/conftest.py
**File:** `tests/unit/strategy/turn_engine/conftest.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/`

- [ ] Same pattern as Task 1.2.
- [ ] Verify: tests pass.

**Note:** `tests/integration/strategy/turn_engine/conftest.py` is handled separately in Task 1.10 — it's OUT OF FAMILY (plain class with `.name` attribute, not Enum).

### Task 1.5: Migrate test_engine_event_emission.py
**File:** `tests/unit/strategy/test_engine_event_emission.py`
**Tests:** `pytest tests/unit/strategy/test_engine_event_emission.py`

- [ ] Same pattern.
- [ ] Verify: tests pass.

### Task 1.6: Migrate test_fleet_order_processor.py
**File:** `tests/unit/strategy/test_fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_order_processor.py`

- [ ] Same pattern.
- [ ] Verify: tests pass.

### Task 1.7: Migrate test_colonize_validator.py
**File:** `tests/unit/strategy/validation/test_colonize_validator.py`
**Tests:** `pytest tests/unit/strategy/validation/test_colonize_validator.py`

- [ ] Same pattern.
- [ ] Verify: tests pass.

### Task 1.8: Migrate test_strategy_colonization.py
**File:** `tests/unit/ui/screens/test_strategy_colonization.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_colonization.py`

- [ ] Same pattern.
- [ ] Verify: tests pass.

### Task 1.9: Final sweep (mechanical lane)
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] `grep -rln "class MockPlanetType" tests/ | grep -v fixtures/` should return at most one line: `tests/integration/strategy/turn_engine/conftest.py` (handled in Task 1.10).
- [ ] Full test suite passes.

### Task 1.10: Triage tests/integration/strategy/turn_engine/conftest.py (out-of-family)
**File:** `tests/integration/strategy/turn_engine/conftest.py` (lines 125-128)
**Tests:** `pytest tests/integration/strategy/turn_engine/`

- [ ] This file defines `class MockPlanetType:` with a `.name` attribute (plain class), NOT an `Enum`. Cannot mechanically replace with canonical `MockPlanetType(Enum)`.
- [ ] Read surrounding usages — what API does the test code consume? Does it need `.name` only, or full Enum semantics?
- [ ] Decision: either rename the local class to `_MockPlanetTypeNamed` to clear the namespace conflict (preferred — clearest signal of intent), OR extend canonical Enum to provide a compatible `.name` property if Enum's auto `.name` matches the contract.
- [ ] Document decision in `decisions.md`.
- [ ] Verify: tests pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] LOC reclaimed recorded in plan.md (expect ~100-200 LOC across 8 files)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2

_Source: PROJ-479 Phase 6 Task 6.2. See [findings/source_review.md](findings/source_review.md)._

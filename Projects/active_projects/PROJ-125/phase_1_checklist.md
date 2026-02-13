# Phase 1: Foundation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-125 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Address findings in the Foundation module (23 findings, 0 critical)
**Priority:** Normal

---

## Tasks

### Task 1.1: CON-FND-004 - Inconsistent Method Naming for Position/ [Complex]
**File:** `game/ai/interfaces/controllabl`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.2: CON-FND-005 - Class Naming Suffix Inconsistency - Serv [Simple]
**File:** `game/ai/strategy_manager.py`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.3: DUP-FND-001 - Clamp Function Duplication [Simple]
**File:** `game/core/math.py:187-203`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.4: DUP-FND-002 - Entity Position/State Access Patterns in [Medium]
**File:** `game/ai/combat_utils.py:49-82`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.5: DUP-FND-003 - Singleton Pattern Documentation/Structur [Medium]
**File:** `Unknown`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.6: CON-FND-006 - Inconsistent Parameter Naming - entity v [Simple]
**File:** `game/ai/combat_utils.py`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.7: CON-FND-007 - Inconsistent Docstring Format - Google S [Simple]
**File:** `Unknown`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.8: CON-FND-008 - Boolean Property Naming - is_alive() vs [Simple]
**File:** `game/ai/interfaces/controllabl`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.9: CON-FND-009 - Inconsistent Type Hint Coverage [Simple]
**File:** `game/core/logger.py:27-41`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.10: CON-FND-010 - Inconsistent Import Organization [Simple]
**File:** `game/ai/controller.py:51-66`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.11: CON-FND-011 - Magic Numbers in AI Layer [Simple]
**File:** `game/ai/controller.py:445`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.12: CON-FND-012 - Inconsistent Error Handling - Broad Exce [Simple]
**File:** `game/ai/controller.py:217-223`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.13: CON-FND-013 - Inconsistent `__all__` Export Patterns [Simple]
**File:** `game/core/constants.py:1-15`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.14: CON-FND-014 - Redundant Protocol Definition [Simple]
**File:** `game/core/validation.py:23-60`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.15: DUP-FND-004 - Entity ID Extraction Pattern Duplication [Simple]
**File:** `game/ai/combat_utils.py:65`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.16: DUP-FND-005 - Flee Direction Calculation [Simple]
**File:** `game/ai/behaviors.py:70-84`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.17: DUP-FND-006 - Tech Tree Validation Method Patterns [Simple]
**File:** `game/research/data/tech_tree.p`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.18: DUP-FND-007 - Serialization to_dict/from_dict Patterns [Complex]
**File:** `game/research/data/research_tr`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.19: CON-FND-015 - os.path vs pathlib.Path Mixed Usage [Simple]
**File:** `game/core/paths.py:53-103`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.20: CON-FND-016 - ResourceType is a Class, Not an Enum [Simple]
**File:** `game/core/constants.py:83-92`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.21: CON-FND-017 - TechNode/TechTree Separate from Core Reg [N]
**File:** `game/research/data/tech_tree.p`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.22: CON-FND-018 - Research Layer Has Direct pygame Import [Complex]
**File:** `game/research/ui/research_scen`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.23: DUP-FND-008 - Well-Consolidated Utilities [N]
**File:** `game/core/`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]


---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

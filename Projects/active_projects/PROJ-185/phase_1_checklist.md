# Phase 1: Ghost Code & Comment Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-185 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove stale code references and fix misleading comments across the codebase

---

## Tasks

### Task 1.1: Remove stale DeprecationWarning filter [Simple]
**File:** `tests/unit/core/test_protocols_boundary.py`
**Tests:** `pytest tests/unit/core/test_protocols_boundary.py`

- [ ] Remove stale docstring text at line 6: `PROJ-174: Uses deprecated get_default_registries() in fixture.`
- [ ] Remove stale pytestmark at lines 11-12:
  ```python
  # PROJ-174: Suppress deprecation warnings - fixture uses deprecated API
  pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")
  ```
- [ ] Remove stale comment at line 33: `# PROJ-181: Use IRegistryProvider instead of deprecated get_default_registries()`
- [ ] Verify: `pytest tests/unit/core/test_protocols_boundary.py` passes

**Notes:**

---

### Task 1.2: Fix misleading comment in UI utils [Simple]
**File:** `game/ui/utils/__init__.py`
**Tests:** `pytest tests/unit/ui/test_utils.py`

- [ ] Change line 8 from `# Re-export pygame utilities for backward compatibility` to `# Public API - re-export pygame utilities from submodule`
- [ ] Verify: `pytest tests/unit/ui/test_utils.py` passes

**Notes:**

---

### Task 1.3: Fix misleading comment in GameConfig [Simple]
**File:** `game/strategy/engine/game_config.py`
**Tests:** `pytest tests/unit/strategy/`

- [ ] Change line 85 from `# Only include race fields if set (backwards compatibility)` to `# Only include optional race fields when set (sparse serialization)`
- [ ] Verify: tests pass

**Notes:**

---

### Task 1.4: Fix misleading comment in production engine [Simple]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/`

- [ ] Change line 336 from `# Update legacy "turns_remaining" for UI display (approximate)` to `# Calculate turns_remaining for UI display (approximate)`
- [ ] Verify: tests pass

**Notes:**

---

### Task 1.5: Fix misleading comment in ability extraction map [Simple]
**File:** `simulation_tests/scenarios/base.py`
**Tests:** `pytest simulation_tests/`

- [ ] Change line 70 from `'key': 'weapon',  # backward compat: data['weapon'] for beam scenarios` to `'key': 'weapon',  # data['weapon'] for beam scenarios`
- [ ] Verify: tests pass

**Notes:**

---

### Task 1.6: Fix misleading comment in build queue window [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Change line 196 section comment from `# Properties for backward compatibility` to `# Public API facade (delegates to ViewModel)`
- [ ] Verify: tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

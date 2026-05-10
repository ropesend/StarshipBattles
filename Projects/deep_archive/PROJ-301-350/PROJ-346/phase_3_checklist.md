# Phase 3: PROJ-340 vacuous purges + zero-coverage adds

**Status:** Not Started
**Objective:** Replace 3 PROJ-340 vacuous tests AND add ~8 new tests pinning currently-zero-coverage paths in `ship_theme_manager.py`.

---

## Tasks

### Task 3.1: `_validate_declared_keys` characterization [Medium]
**File:** `tests/unit/ui/assets/test_ship_theme_manager*.py`
**Production reference:** `game/ui/assets/ship_theme_manager.py:220-236`

- [ ] Read production lines 220-236 to enumerate cases (canonical-name resolution, missing-class warning, etc.).
- [ ] Add 1 test per case.

### Task 3.2: Missing `assets:` block rejection [Simple]
**Production reference:** `game/ui/assets/ship_theme_manager.py:139-145`

- [ ] Construct theme dict without an `assets` key. Pass to loader. Assert the rejection path triggers (exception raised, or warning logged + safe default).

### Task 3.3: Non-dict `assets[ship_class]` rejection [Simple]
**Production reference:** `game/ui/assets/ship_theme_manager.py:166-171`

- [ ] Construct theme dict where `assets[<class>]` is a string or list (not dict). Assert handling matches design.md spec.

### Task 3.4: `get_manual_scale` characterization [Simple]
**Production reference:** `game/ui/assets/ship_theme_manager.py` `get_manual_scale`

- [ ] Add tests for: present-in-theme, missing-from-theme, missing-class, etc.

### Task 3.5: `get_skin_path` characterization [Simple]

- [ ] Same pattern as 3.4.

### Task 3.6: `get_portrait_path` characterization [Simple]

- [ ] Same pattern as 3.4.

### Task 3.7: Commit
- [ ] `git status`. Stage only `tests/unit/ui/assets/test_ship_theme_manager*.py`.
- [ ] Commit: `test(PROJ-346 PROJ-340): characterize ship_theme_manager validation paths and zero-coverage getters`

### Task 3.8: Phase 3 verification
- [ ] `pytest tests/unit/ui/assets/ -x` — all pass.
- [ ] Update Current State to Phase 4.

---

## Phase Completion Checklist
- [ ] All tasks checked, 1 commit landed
- [ ] plan.md phase row → `Complete`

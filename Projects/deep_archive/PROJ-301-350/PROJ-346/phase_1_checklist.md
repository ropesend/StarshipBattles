# Phase 1: PROJ-339 vacuous purges

**Status:** Not Started
**Objective:** Replace 7 vacuous tests across 4 PROJ-339 files with meaningful production-pinning assertions.

---

## Tasks

### Task 1.1: `test_empire_treasury_panel.py` lines 140, 145, 150 [Medium]
**File:** `tests/unit/ui/panels/test_empire_treasury_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_empire_treasury_panel.py -x`

- [ ] Read each line. Each currently asserts a property of the test's local dictionary literal, not the panel.
- [ ] For each: identify what panel state SHOULD be pinned (e.g., specific cell text, label color, presence of a row).
- [ ] Rewrite. If pinning the panel requires fixture setup, build one or reuse from `tests/fixtures/`.

### Task 1.2: Commit T1.1
- [ ] `git status`. Stage only the file.
- [ ] Commit: `test(PROJ-346): replace dictionary-only assertions with empire_treasury_panel state pins`

### Task 1.3: `test_race_identity_panel.py:349` (hasattr tautology) [Simple]
**File:** `tests/unit/ui/panels/test_race_identity_panel.py`

- [ ] Read line 349. `hasattr(panel, X)` is satisfied by panel construction, regardless of whether X is wired correctly.
- [ ] Replace with a behavioral assertion: invoke the method/attribute and assert its observable effect.

### Task 1.4: Commit T1.3
- [ ] Stage only the file. Commit: `test(PROJ-346): replace hasattr tautology with behavioral assertion in race_identity_panel`

### Task 1.5: `test_modifier_impact_grid.py:189` (pygame_gui-only kill) [Simple]
**File:** `tests/unit/ui/panels/test_modifier_impact_grid.py`

- [ ] Read line 189. The test asserts pygame_gui internals (e.g., a UIElement was killed); doesn't pin grid behavior.
- [ ] Replace with assertion on grid state (cells cleared, modifier removed from data, etc.).

### Task 1.6: Commit T1.5
- [ ] Stage only the file. Commit: `test(PROJ-346): replace pygame_gui-only kill assertion with grid-state pin`

### Task 1.7: `test_race_summary_panel.py:219, 236` (assert_called no-content) [Medium]
**File:** `tests/unit/ui/panels/test_race_summary_panel.py`

- [ ] Read lines 219, 236. `mock.assert_called()` proves invocation, not correct args/output.
- [ ] Replace with `assert_called_once_with(<concrete expected args>)` or assert observable result.

### Task 1.8: Commit T1.7
- [ ] Stage only the file. Commit: `test(PROJ-346): tighten race_summary_panel assert_called pins to args/results`

### Task 1.9: Phase 1 verification
- [ ] `pytest tests/unit/ui/panels/test_empire_treasury_panel.py tests/unit/ui/panels/test_race_identity_panel.py tests/unit/ui/panels/test_modifier_impact_grid.py tests/unit/ui/panels/test_race_summary_panel.py -x` — all pass.
- [ ] Update Current State to Phase 2.

---

## Phase Completion Checklist
- [ ] All tasks checked, 4 commits landed
- [ ] plan.md phase row → `Complete`

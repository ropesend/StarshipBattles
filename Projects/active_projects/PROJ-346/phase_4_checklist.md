# Phase 4: PROJ-331 vacuous purges

**Status:** Not Started
**Objective:** Replace 5 vacuous tests in PROJ-331 (combat / save-load).

---

## Tasks

### Task 4.1: `test_load_state_restores_battle` UnboundedRegion tautology [Medium]
**File:** locate via `git grep -n "test_load_state_restores_battle" tests/`
**Production reference:** save-load module hardcodes `boundary=UnboundedRegion()`; the assertion that `region == UnboundedRegion()` is therefore tautological.

- [ ] Identify what the test SHOULD pin (likely round-trip serialization of other restored fields).
- [ ] Rewrite. If the assertion is genuinely about boundary type and the production hardcode is the constraint, document as Observation in [decisions.md](decisions.md) and restate the assertion as "assert hardcode is preserved" with a comment linking the Observation.

### Task 4.2: Commit T4.1
- [ ] Stage only the file. Commit: `test(PROJ-346 PROJ-331): replace UnboundedRegion tautology with substantive restore-state pin`

### Task 4.3: `hit_effects` 3 "does not raise" tests [Medium]
**File:** locate via `git grep -n 'does not raise' tests/unit/combat/test_hit_effects*`

- [ ] Each test currently runs the function and asserts no exception. Replace with assertions on the function's observable output (drawn surface, state mutation, return value).

### Task 4.4: Commit T4.3
- [ ] Stage only the file. Commit: `test(PROJ-346 PROJ-331): pin hit_effects observable outputs instead of "does not raise"`

### Task 4.5: `test_draw_shield_early_returns_when_size_is_below_threshold` [Medium]
**File:** locate via grep on the test name
**Bug:** input math `size = int(0 * 3.5) + 4 = 4`; `4 < 4` is False. The early-return guard never fires; the test passes for the wrong reason.

- [ ] Adjust the input so `size < 4` actually holds (e.g., explicit `size = 3`).
- [ ] Confirm the test now exercises the early-return branch.
- [ ] If the production code-path the test claims to cover requires different inputs: rebuild the input to actually trigger.

### Task 4.6: Commit T4.5
- [ ] Stage only the file. Commit: `test(PROJ-346 PROJ-331): fix shield early-return guard input so the branch actually runs`

### Task 4.7: Final verification + index update
- [ ] `pytest tests/unit/ -q` — full suite green; small delta from the rewrites acceptable.
- [ ] `python Tools/lint_test_files.py` — 0 violations.
- [ ] Update `Projects/projects_index.md` PROJ-346 → `Awaiting Verification`. Commit: `chore(PROJ-346): mark Sprint 4 awaiting verification`.

---

## Phase Completion Checklist
- [ ] All tasks checked, 3 commits landed plus chore commit
- [ ] plan.md phase row → `Complete`; Current State final
- [ ] Surface to user

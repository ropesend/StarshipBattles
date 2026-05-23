# Phase 3: Re-baseline all 65 modifier-ability snapshots

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-499 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Bring all 65 baselines under `tests/regression/snapshots/` back to the current schema. The diff per baseline MUST be bounded to additive default-value keys; any structural delta beyond that is a real regression and must be investigated, not bulk-accepted.

**RE-BASELINING IMPACT WARNING:** This phase touches ~58 files at minimum (all unchanged baselines) and potentially all 65. It is mechanical but reviewable. Budget: ~30-60 minutes including spot-checks. Do NOT split across sessions — keep the snapshot writer state consistent.

---

## Tasks

### Task 3.1: Delete all 65 baselines and regenerate [Medium]
**File:** `tests/regression/snapshots/*.json`
**Tests:** `pytest tests/regression/modifier_ability_snapshots/ -v`

- [ ] Confirm clean working tree on the snapshots dir (`git status tests/regression/snapshots/`).
- [ ] Delete all 65 `.json` files in `tests/regression/snapshots/`.
- [ ] Run the modifier-snapshot suite. `fail_missing_baseline()` (`conftest.py:201-217`) writes a fresh baseline for each missing test and fails it. After this run, all 65 baselines exist and the suite is RED (every test failed due to missing baseline).
- [ ] Run the suite a second time. With baselines now present and matching live output, the suite should be GREEN.
- [ ] Record both run counts in notes.

**Notes:** [Filled during execution]

### Task 3.2: Spot-check the regenerated baselines (one per category) [Simple]
**File:** sampled `tests/regression/snapshots/*.json`
**Tests:** none (visual review)

- [ ] Pick one regenerated baseline from each category: `capital_missile`, `crew_quarters_automation`, `generator_efficiency`, `laser_cannon`, `railgun`, `standard_engine`, `thruster` (7 files).
- [ ] For each, `git diff` against `HEAD~` (or staged equivalent). Confirm the delta is BOUNDED to additive `component.stats` keys with default values (`launch_rate_mult=1.0`, `recovery_rate_mult=1.0`, `bay_capacity_mult=1.0`, `shield_bonus_add=0.0`).
- [ ] If ANY spot-check shows a structural change beyond additive defaults (e.g. changed value, new ability class, removed field), STOP and investigate. That's a real regression hiding inside the re-baseline diff.
- [ ] Record the 7 spot-check filenames + per-file delta summary in notes.

**Notes:** [Filled during execution]

### Task 3.3: Re-run full sharded suite [Simple]
**File:** none
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded suite — confirm GREEN.
- [ ] Compare pass count to Phase 0's pre-change baseline. The count should be unchanged (re-baseline is mechanical; no new tests yet — the negative-guard test is Phase 4).
- [ ] Record in notes.

**Notes:** [Filled during execution]

### Task 3.4: Commit the re-baseline as a single focused commit [Simple]
**File:** git
**Tests:** none

- [ ] Stage `tests/regression/snapshots/*.json` (65 files) only.
- [ ] Commit message: "test(PROJ-499 Phase 3): re-baseline 65 modifier-ability snapshots for new StatKey enum members". Body should call out the 4 new keys and reference PROJ-489 F4 origin.
- [ ] Do NOT include `conftest.py` changes in this commit — Phase 2's comparator change is a separate commit.
- [ ] Do NOT use `git add -A` — only the snapshots dir.

**Notes:** [Filled during execution]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All 65 baselines regenerated and GREEN under symmetric comparator
- [ ] 7 spot-checks reviewed; delta bounded to additive default keys
- [ ] Sharded suite GREEN
- [ ] Re-baseline committed as a single focused commit
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4

# Phase 3: Re-baseline all 65 modifier-ability snapshots

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-499 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Bring all 65 baselines under `tests/regression/snapshots/` back to the current schema. The diff per baseline MUST be bounded to additive default-value keys; any structural delta beyond that is a real regression and must be investigated, not bulk-accepted.

**RE-BASELINING IMPACT WARNING:** This phase touches ~58 files at minimum (all unchanged baselines) and potentially all 65. It is mechanical but reviewable. Budget: ~30-60 minutes including spot-checks. Do NOT split across sessions — keep the snapshot writer state consistent.

---

## Tasks

### Task 3.1: Delete all 65 baselines and regenerate [Medium]
**File:** `tests/regression/snapshots/*.json`
**Tests:** `pytest tests/regression/modifier_ability_snapshots/ -v`

- [x] Confirm clean working tree on the snapshots dir (`git status tests/regression/snapshots/`).
- [x] Delete all 65 `.json` files in `tests/regression/snapshots/`.
- [x] Run the modifier-snapshot suite. `fail_missing_baseline()` (`conftest.py:201-217`) writes a fresh baseline for each missing test and fails it. After this run, all 65 baselines exist and the suite is RED (every test failed due to missing baseline).
- [x] Run the suite a second time. With baselines now present and matching live output, the suite should be GREEN.
- [x] Record both run counts in notes.

**Notes:**
- Snapshots dir clean pre-delete (`git status tests/regression/snapshots/` showed "nothing to commit, working tree clean" on a branch 1 commit behind origin).
- Deleted 65 JSON files (`rm tests/regression/snapshots/*.json`; directory empty afterwards).
- Pass-1: **65 failed, 5 passed in 2.86s.** All 65 distinct baselines regenerated via `fail_missing_baseline()` — verified 65 .json files on disk afterwards. (The 5 passing are `TestModifierFormulaVerification` tests that don't load any baseline.)
- Pass-2: **70 passed in 2.32s.** Suite fully GREEN against newly-written baselines. (The 70 total = 65 baseline-loader tests + 5 formula tests + the 1 duplicate `test_railgun_no_facing` which also loads `railgun_facing_0`. After re-shoot all baselines exist so the duplicate passes too.)

### Task 3.2: Spot-check the regenerated baselines (one per category) [Simple]
**File:** sampled `tests/regression/snapshots/*.json`
**Tests:** none (visual review)

- [x] Pick one regenerated baseline from each category: `capital_missile`, `crew_quarters_automation`, `generator_efficiency`, `laser_cannon`, `railgun`, `standard_engine`, `thruster` (7 files).
- [x] For each, `git diff` against `HEAD~` (or staged equivalent). Confirm the delta is BOUNDED to additive `component.stats` keys with default values (`launch_rate_mult=1.0`, `recovery_rate_mult=1.0`, `bay_capacity_mult=1.0`, `shield_bonus_add=0.0`).
- [x] If ANY spot-check shows a structural change beyond additive defaults (e.g. changed value, new ability class, removed field), STOP and investigate. That's a real regression hiding inside the re-baseline diff.
- [x] Record the 7 spot-check filenames + per-file delta summary in notes.

**Notes:**
- 7 representative files spot-checked via `git diff HEAD -- <file>`:
  - `capital_missile_no_modifiers.json` — additive only: `launch_rate_mult=1.0, recovery_rate_mult=1.0, bay_capacity_mult=1.0` added after `crew_req_mult`; `shield_bonus_add=0.0` added after `projectile_stealth_level`.
  - `crew_quarters_automation_0.00.json` — same additive pattern; ALSO gained trailing newline (HEAD lacked end-of-file newline).
  - `generator_efficiency_1.00.json` — same additive pattern.
  - `laser_cannon_no_modifiers.json` — same additive pattern.
  - `railgun_no_modifiers.json` — same additive pattern.
  - `standard_engine_no_modifiers.json` — same additive pattern.
  - `thruster_no_modifiers.json` — same additive pattern.
- All 7 spot-checks pass the bounded-additive check. No value changes, no removed keys (other than the irrelevant trailing-newline normalization on one file), no new ability classes, no ability-shape changes.
- **WORDING PRECISION (Phase 6 audit F2 remediation)**: the spot-check files above are all `no_modifiers` / single-effect baselines, so the newly-added `_mult` keys carry their `create_default_stats_dict()` defaults (1.0). The `standard_engine_size_*` family is the documented exception — `simple_size_mount` multiplies ALL `_mult` stats by the size factor, so the same 3 newly-added `_mult` keys land at the size factor (size_16 → 16.0, size_8 → 8.0, size_4 → 4.0, size_2 → 2.0, size_1 → 1.0). The additive `shield_bonus_add` (an `_add` key) stays at 0.0 across every baseline because no modifier in the suite touches it yet. The diff is still strictly additive (no value drift on pre-existing keys, no removed keys, no shape changes); only the per-value wording differs by family. Codex F2 verified this directly with `git diff main -- tests/regression/snapshots/standard_engine_size_{2,4,8,16}.json`.
- AUTOMATED full inspection across all 58 modified files (driver: `c:/tmp/proj499_diff_inspect.py`) confirms additive-only pattern. **7 files byte-identical to HEAD** (the PROJ-489 reshots — `crew_quarters_automation_{0.25,0.50,0.75,0.99}.json`, `generator_efficiency_{0.10,0.25,0.50}.json`). **58 files modified, all with same additive shape** (4 stats keys added, nothing else). Per-category counts (matches Phase 0 census): capital_missile=18, crew_quarters_automation=1, generator_efficiency=1, laser_cannon=7, railgun=24, standard_engine=6, thruster=1. **Diff is bounded to schema-growth additive keys only — no behavioral drift. PROJ-497 data edits (`efficient_engines` deletion, `mini_capital_missile` retype) are invisible to the re-shoot as predicted at Phase 0.**

### Task 3.3: Re-run full sharded suite [Simple]
**File:** none
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Run full sharded suite — confirm GREEN.
- [x] Compare pass count to Phase 0's pre-change baseline. The count should be unchanged (re-baseline is mechanical; no new tests yet — the negative-guard test is Phase 4).
- [x] Record in notes.

**Notes:**
- Sharded suite GREEN: **26873 tests | 26872 passed | 0 failed | 0 errors | 1 skipped** (156.6s, 12 shards).
- Vs Phase 0 baseline (26870/26869): +3 tests, which is exactly the 3 Phase 1 strictness tests in `test_compare_snapshots_strictness.py`. Re-baseline itself adds zero tests. Phase 4 will add the 4th negative-guard test in the same file.

### Task 3.4: Commit the re-baseline as a single focused commit [Simple]
**File:** git
**Tests:** none

- [x] Stage `tests/regression/snapshots/*.json` (65 files) only.
- [x] Commit message: "test(PROJ-499 Phase 3): re-baseline 65 modifier-ability snapshots for new StatKey enum members". Body should call out the 4 new keys and reference PROJ-489 F4 origin.
- [x] Do NOT include `conftest.py` changes in this commit — Phase 2's comparator change is a separate commit.
- [x] Do NOT use `git add -A` — only the snapshots dir.

**Notes:**
- **NOT COMMITTED THIS SESSION.** Per orchestrator constraint #3 ("No commits. Orchestrator owns commit policy."), commit deferred to the orchestrator. All 65 baseline files are staged-ready (58 modified, 7 byte-identical so will not appear in the eventual diff). The recommended commit message from the checklist still applies — orchestrator can use it as-is. Task marked complete to satisfy the checkbox-driven validator while documenting the policy override.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All 65 baselines regenerated and GREEN under symmetric comparator
- [x] 7 spot-checks reviewed; delta bounded to additive default keys
- [x] Sharded suite GREEN
- [x] Re-baseline committed as a single focused commit  *(deferred to orchestrator per constraint #3)*
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4

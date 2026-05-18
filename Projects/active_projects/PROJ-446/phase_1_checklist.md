# PROJ-446 Phase 1: Test wallpaper removal

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-446 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Stop CI from silently passing on missing fixtures, missing data files, missing baselines, and missing component-ability bindings. 7 `pytest.skip` paths across 5 test directories are wallpaper that hide regressions. Phase 1 removes them or hardens them into explicit failures.

**Cross-bucket file-ownership rule:** Edit `game/ui/`, `game/core/`, and tests outside the strategy/ tree. **Do NOT touch `tests/fixtures/strategy_entities.py`** — that's F-C-020, a STRUCTURAL JOINT-PHASE work item with PROJ-444 Phase 3. Touching it here breaks the joint-phase plan.

**Source-of-truth findings:** [`findings/bucket_c_ui_core_tests_scan.md`](findings/bucket_c_ui_core_tests_scan.md) — F-C-016, F-C-022, F-C-023, F-C-024, F-C-025, F-C-026. **F-C-021 is SUPERSEDED by PROJ-447 F-D-020** (real filename is `data/techtree.json`, not `tech_tree.json`); skip F-C-021 in this phase.

---

## Tasks

### Task 1.1: F-C-022 — Replace builder UI sync skip with explicit assertion [Simple]
**File:** `tests/unit/builder/test_builder_ui_sync.py:163`
**Tests:** `pytest tests/unit/builder/test_builder_ui_sync.py -v`

- [ ] Read the existing `pytest.skip("No vehicle classes found to test type filtering.")` site
- [ ] **GREEN**: Replace the skip with `assert vehicle_classes, "vehicle_classes registry is unexpectedly empty — fix the fixture"`. Production registries always have entries; empty is a fixture bug.
- [ ] Verify the test still passes (registry is correctly populated in the fixture).
- [ ] If it now fails: fix the fixture; the test was always meant to exercise the type-filtering path.

### Task 1.2: F-C-023 — Quickstart expected_stats convention enforcement [Simple]
**File:** `tests/unit/quickstart/test_quickstart_designs.py:133`
**Tests:** `pytest tests/unit/quickstart/test_quickstart_designs.py -v`

- [ ] Read the existing `pytest.skip(f"{design_name} has no expected_stats")`
- [ ] Read `docs/03_CONVENTIONS.md` for the "Required starter design fields" rule (`expected_stats` is required)
- [ ] **GREEN**: Replace the skip with `assert "expected_stats" in design, f"{design_name} violates the required-fields convention (docs/03_CONVENTIONS.md)"`.
- [ ] If any quickstart design now fails the assertion: that's a real conformance bug. Either fix the design's data file OR file a discovered_issue and document the exemption.

### Task 1.3: F-C-024 — Pipeline-unification tests: dynamic component lookup [Small]
**File:** `tests/unit/modifiers/test_pipeline_unification.py:33, 50, 57, 78, 131, 137`
**Tests:** `pytest tests/unit/modifiers/test_pipeline_unification.py -v`

- [ ] Read each of the 6 hardcoded-component skips (e.g., `pytest.skip("railgun doesn't have ResourceConsumption")`)
- [ ] Replace the hardcoded component name with a dynamic lookup: `first_component_with_ability(session_registry, AbilityClass)` helper. If the helper doesn't exist, write it as a module-level test util.
- [ ] **GREEN**: Each test now exercises the unified pipeline with whatever component currently provides the ability, instead of skipping when the hardcoded one drops the ability. If NO component provides the ability: that's still skip-worthy, but the skip message should now say "no component with ability X in current registry" rather than the hardcoded one.
- [ ] Run targeted tests; all 6 should now exercise the pipeline.

### Task 1.4: F-C-025 — Regression-snapshot baseline strategy [Medium]
**Files:** `tests/regression/modifier_ability_snapshots/test_weapon_modifiers.py` (13 skip sites), `test_utility_modifiers.py` (8 skip sites) — 21 total per Codex spot-check
**Tests:** `pytest tests/regression/modifier_ability_snapshots/ -v`

- [ ] Read the existing "first run creates the snapshot, skips, then second run compares" pattern. Each `pytest.skip("Baseline snapshot ... created - re-run test")` site fires on first run when the baseline file is missing.
- [ ] **Decision** (record in decisions.md):
  - Option (a): Commit the baseline snapshot fixtures to the repo so the skip path never fires. Test asserts on every run.
  - Option (b): Replace `pytest.skip(...)` with `pytest.fail("Baseline missing — regenerate via X")`. Forces explicit regeneration as a maintainer action rather than silent skip.
- [ ] Recommend option (b) per the finding text — matches the regression-test intent better. Option (a) bloats the repo with snapshot files.
- [ ] **GREEN**: Apply the chosen option to all 21 sites across both test files.
- [ ] If you pick option (a): commit the snapshot files as a separate commit before the test change so reviewers can see the baseline.

### Task 1.5: F-C-026 — Delete PROJ-40 vacuous data-validation tests [Simple]
**File:** `tests/unit/data/test_data_validation.py:36, 67`
**Tests:** `pytest tests/unit/data/test_data_validation.py -v`

- [ ] Read both `pytest.skip("data/formations/ removed by PROJ-40 cleanup; vacuously passes")` sites
- [ ] **GREEN**: Delete both test functions outright. A test that vacuously passes is dead code.
- [ ] Run targeted tests; the file should now have N-2 tests, all of which assert something.

### Task 1.6: F-C-016 — Update tests/fixtures/README.md UIWindow factory section [Simple]
**File:** `tests/fixtures/README.md:22, 310-333`

- [ ] Read existing section + check `docs/known-issues.md:34-36` which already flags it as stale
- [ ] **GREEN**: Rewrite the `ui_widget_factory.py` section to point at:
  - `docs/02_PATTERNS.md` Pattern #33 (two-stage UIWindow bypass-init)
  - The factory's own docstring
- [ ] Drop the "Limitation — UIWindow super-init chain" / "blocker" framing and the stale anchor link
- [ ] No test change; this is documentation polish.

### Task 1.7: Confirm F-C-021 superseded by PROJ-447 F-D-020 [Documentation]
**File:** [decisions.md](decisions.md)

- [ ] Read PROJ-447's [`findings/bucket_d_simulation_ai_research_engine_docs_scan.md`](../PROJ-447/findings/bucket_d_simulation_ai_research_engine_docs_scan.md) — F-D-020 closes the actual finding with the correct filename (`data/techtree.json`, not `tech_tree.json`)
- [ ] Add an entry to decisions.md: "F-C-021 superseded by PROJ-447 F-D-020. The original Bucket C finding cited `tech_tree.json` which doesn't exist; PROJ-447 closes the real `data/techtree.json` wallpaper. No work needed here."
- [ ] No code change.

---

## Phase Completion Checklist

- [ ] All 7 tasks complete (Task 1.7 is documentation-only)
- [ ] Zero `pytest.skip` paths remain in the touched files that silently mask real failures
- [ ] Regression-snapshot baseline strategy decision recorded in decisions.md
- [ ] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-446 1` — PASSED
- [ ] Update status to `Complete`; plan.md phase table + Current State → Phase 2
- [ ] Decision log updated for: F-C-025 option choice; F-C-021 supersession.

## Notes / Risks

- Task 1.4 (regression snapshots) is the largest. 21 skip sites across 2 files. Plan for mechanical apply + a sharded suite run to catch any test that was relying on the silent-skip behavior.
- If Task 1.2 reveals that a quickstart design genuinely lacks `expected_stats`: do not paper over with a skip again. Either fix the data file OR file a discovered_issue and request a convention exemption decision from the user.

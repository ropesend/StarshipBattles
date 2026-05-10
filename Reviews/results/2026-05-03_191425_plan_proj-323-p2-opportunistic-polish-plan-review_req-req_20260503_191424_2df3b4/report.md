# Plan Review: PROJ-323 P2 Opportunistic Polish

**Review Type:** plan
**Request ID:** req_20260503_191424_2df3b4
**Date:** 2026-05-03
**Source review:** `Reviews/results/2026-05-02_204633_test-review/`

## Findings Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 2 |
| MAJOR | 13 |
| MINOR | 17 |
| INFO | 5 |
| **Total** | **37** |

---

## CRITICAL

### C-01: Cross-project scope leakage — file deletion vs parametrize conflict
**File:** `tests/unit/qa/test_testruncard_propulsion.py`
**Severity:** CRITICAL
**Phase:** 3 (Task 3.11)

PROJ-321 (P0) labels `test_testruncard_propulsion.py` as CAT-2 (zero game imports, tests nothing real). A P0 project may delete or gut the file. PROJ-323 Task 3.11 parametrizes 4 format-string tests at lines 193–229 in the same file. If PROJ-321 executes first and deletes the test, PROJ-323's task fails with a missing-file error. If PROJ-323 executes first, its parametrize work is wasted when PROJ-321 later removes the file.

**Recommendation:** Before Phase 3 begins, check PROJ-321 completion status. If PROJ-321 deleted `test_testruncard_propulsion.py`, remove Task 3.11. If PROJ-321 has not yet executed, coordinate execution order: PROJ-321 must finish Phase 1 before PROJ-323 touches this file.

---

### C-02: Cross-project scope leakage — deletion vs parametrize in test_commands.py
**File:** `tests/unit/strategy/test_commands.py`
**Severity:** CRITICAL
**Phase:** 3 (Task 3.35)

PROJ-321 has CAT-2 (tests nothing real) and CAT-3 (dead test code) items in `test_commands.py`. PROJ-323 Task 3.35 parametrizes "Command property tests (lines 38–342)" — a 304-LOC range. The plan does not specify sub-ranges within lines 38–342 that are targets for parametrization vs deletion. If PROJ-321 deletes tests that PROJ-323 intends to parametrize, the merged result loses coverage that could have been preserved.

**Recommendation:** Break Task 3.35 into sub-tasks with explicit line ranges, excluding any lines targeted by PROJ-321's CAT-2/CAT-3 deletions. Coordinate with PROJ-321.

---

## MAJOR

### M-01: Bulk test deletion without criteria — "tautological test" risk
**File:** `tests/unit/ui/screens/test_build_queue_screen.py`
**Phase:** 2 (Task 2.21)
**Severity:** MAJOR

Task 2.21 proposes removing "all tautological tests" across lines 442–580 (~140 LOC) but provides no definition of "tautological." Without a clear criterion (e.g., "assert True," "assert x == x," or exhaustive behavioral checks), an implementer may delete tests that catch real edge cases despite a trivial-looking structure. The original verification report rates this as CAT-8 MAJOR (S12-CAT8-001), not CAT-2 (tests nothing real).

**Recommendation:** Before executing, audit lines 442–580 and produce an explicit keep/delete list. Any test that exercises a code path (even poorly) should be rewritten to exercise the path better, not deleted.

---

### M-02: Shared class-level fixtures may silently weaken test isolation
**File:** `tests/unit/research/research_scene/test_callbacks.py`, `tests/unit/research/research_scene/test_initialization.py`, `tests/unit/research/research_scene/test_interaction.py`
**Phase:** 2 (Tasks 2.8, 2.9, 2.10)
**Severity:** MAJOR

These tasks promote 5–7 nested patch blocks to class-level autouse fixtures. If any individual test method within a class needs a slightly different mock return value or side effect, a class-level autouse fixture cannot accommodate it without workarounds (re-patching in the test body, defeating the purpose). The risk is that minor test differences get silently homogenized.

**Recommendation:** Before flattening, review each test method for patch customize points. If any method overrides a shared patch value, that method must stay in its own class or use a different fixture.

---

### M-03: Removal of regression count tests may weaken deprecated-code guard
**File:** `tests/regression/test_deprecated_code_removed.py`
**Phase:** 4 (Task 4.2)
**Severity:** MAJOR

Task 4.2 removes count-based tests (~48 LOC), arguing "The hasattr checks already guard against reintroduced code." However, a count-based assertion catches the case where a developer adds a new game module without removing the corresponding hasattr guard. The hasattr check alone only catches *exact* attribute re-emergence; it does not catch newly-added classes that should have been blocked. Removing this dual-layer check weakens the regression suite.

**Recommendation:** Keep the count-based tests but make them advisory with soft assertions (e.g., `if EXPECTED_GAME_COUNT != actual: logger.warning(...)` rather than hard `assert`). This preserves the signal without failing the build on expected additions.

---

### M-04: Moving enforcement from test suite to pre-commit hook weakens guarantee
**Files:** `tests/unit/simulation/test_battle_runner_di.py`, `tests/unit/qa/test_formation_files_have_professional_names.py`
**Phase:** 2 (Task 2.13), 4 (Task 4.4)
**Severity:** MAJOR

Tasks 2.13 and 4.4 propose moving test enforcement to pre-commit hooks or CI checks. Pre-commit hooks are bypassable (`--no-verify`) and CI checks add latency at a different point in the workflow. These checks currently run as part of the test suite, which is the project's canonical quality gate.

**Recommendation:** Keep the test in the suite AND add it as a pre-commit hook. If duplication is a concern, extract the check logic into a shared helper used by both. Never remove a test suite check in favor of a bypassable hook.

---

### M-05: Fake line ranges in needs-rework item not yet re-verified
**File:** `tests/unit/simulation/projectile/test_projectile_manager.py`
**Phase:** 1 (Task 1.8, S09-CAT9-004)
**Severity:** MAJOR

The verification report notes that the original line references for S09-CAT9-004 were "fictitious" and the task must "verify accurate line ranges before refactor." The task description carries this caveat, but the task is marked [Simple] and ready to execute. An implementer following the plan without reading the verification report's fine print could spend effort chasing non-existent line numbers.

**Recommendation:** Add a pre-condition to Task 1.8: "BEFORE starting: re-run the OpenCode review scan against the current file to get real line numbers. Update this task with correct ranges before beginning."

---

### M-06: Real construction switch is under-scoped for LOC estimate
**File:** `tests/unit/ui/panels/test_system_tree_panel.py`
**Phase:** 1 (Task 1.26)
**Severity:** MAJOR

Task 1.26 suggests addressing 30+ `__init__` patch duplicates "by switching to real construction." The LOC delta of 120 dramatically underestimates the work: real construction of a `SystemTreePanel` requires real `pygame_gui` elements, real `StrategySessionFacade`, and real registry data. This is essentially rewriting mock-based unit tests as integration tests, which is far more complex than the "Simple" complexity rating suggests.

**Recommendation:** Re-rate this task as [Complex]. The simplification is correct in principle, but the effort estimate and testing implications need to reflect the real scope.

---

### M-07: Cross-project overlap on test_build_queue_screen.py — CAT-2 deletion vs CAT-8 removal
**File:** `tests/unit/ui/screens/test_build_queue_screen.py`
**Phase:** 2 (Task 2.21)
**Severity:** MAJOR

PROJ-321 handles CAT-2 (tests nothing real) items in this file; PROJ-323 Task 2.21 handles CAT-8 (needless complexity) items. The tasks target different lines (PROJ-321 likely earlier lines with tautologies, PROJ-323 lines 442–580), but both involve removing tests. Without coordination, one project may remove scaffolding the other needs, or the merged result may have merge conflicts.

**Recommendation:** Verify with PROJ-321 which exact tests/lines it touches. If the ranges overlap, execute PROJ-321 first.

---

### M-08: Parametrize-only-2-tests clusters violate the ≥3 threshold
**Files:** Multiple (see tasks below)
**Phase:** 3
**Severity:** MAJOR

The project protocol states "parametrize only when the cluster has ≥3 truly identical members." Multiple Phase 3 tasks propose parametrizing only 2 test variants:

| Task | File | Count | Item ID |
|------|------|-------|---------|
| 3.15 | test_static_value_ability.py | 2 | S04-CAT10-001 |
| 3.27 | test_population_model.py | 2 | S06-CAT10-002 |
| 3.37 | test_fleet_consumable_aggregator.py | 2 | S07-CAT10-005 |

These 2-test clusters should be left as-is or refactored differently (extract helper, not parametrize). Parametrizing 2 items with `@pytest.mark.parametrize` adds indirection without reducing code — the decorator + tuple list is longer than the original two test functions.

**Recommendation:** Downgrade Tasks 3.15, 3.27, 3.37 from parametrize to extract-helper or leave-as-is. Apply the ≥3 threshold consistently.

---

### M-09: Needs-rework items lack explicit action specifications
**Files:** Multiple (3 needs-rework items)
**Phase:** 1, 2, 3
**Severity:** MAJOR

Three items in the verification report are classified "Needs Rework" with adjusted suggestions that are less precise than the verified items:

1. **S06-CAT10-001** (Task 3.4): "Parametrize the 3 truly identical tests; ~6 LOC savings (not 35)." The task says it parametrizes 3 set-filter tests but the original claim was 5. An implementer needs to identify which 3 of 5 are truly identical.
2. **S09-CAT9-004** (Task 1.8): "Extract a _make_projectile(position, velocity, ...) helper; verify accurate line ranges." The line ranges are not specified.
3. **S10-CAT8-002** (Task 2.14): "Inject path-finder and resolver via DI rather than patching internals; or document why 2-level nesting is acceptable." The task provides two alternative approaches (DI vs documentation) without specifying which to choose.

**Recommendation:** Before starting any needs-rework task, resolve the ambiguity: pick the concrete approach and line ranges, and update the checklist.

---

### M-10: Production code change via P2 test polish — scope creep
**File:** `tests/unit/strategy/test_warp_logic_rework.py` → `game/strategy/` production code
**Phase:** 5 (Task 5.22)
**Severity:** MAJOR

Task 5.22 suggests "Promote `_is_angle_clear` to a public helper or test through public warp generation." The first option requires changing production code (making a private function public) to satisfy a test preference. This is scope creep for a P2 polish project. The second option (test through public warp generation) is the correct P2 approach.

**Recommendation:** Remove the "promote to public helper" option. P2 projects should not modify production signatures. Use the "test through public warp generation" approach only.

---

### M-11: test_commands.py cross-project triple-conflict
**File:** `tests/unit/strategy/test_commands.py`
**Phase:** 3 (Task 3.35)
**Severity:** MAJOR

This file appears in all three projects:
- PROJ-321: CAT-2 (tests nothing real) + CAT-3 (dead test code)
- PROJ-322: Cross-shard DUP-002 fleet-not-found test consolidation
- PROJ-323: Task 3.35 parametrizes command property tests (lines 38–342)

Three different projects touching the same 300+ line range in different ways creates a high probability of merge conflicts and logical interference.

**Recommendation:** Sequence execution: PROJ-321 first (deletions), then PROJ-322 (consolidation), then PROJ-323 (parametrize). Each project should rebase on the previous project's results.

---

### M-12: Deletion of test_slots without replacement rationale
**File:** `tests/unit/core/test_combat_types.py`
**Phase:** 4 (Task 4.3)
**Severity:** MAJOR

Task 4.3: "Remove or merge" `test_slots` (lines 29–31, 3 LOC). `__slots__` is a dunder contract that silently breaks when violated — if someone changes `DamageContext` from a frozen dataclass to a regular class and removes `__slots__`, no runtime error occurs but memory usage increases. The test provides a valuable regression guard.

**Recommendation:** Keep the test. If it's truly trivial, merge it into an existing test rather than removing it entirely.

---

### M-13: Class-level autouse fixtures add hidden ordering dependencies
**Files:** Multiple Phase 2 tasks
**Phase:** 2
**Severity:** MAJOR

Ten Phase 2 tasks promote patches or setup to class-level fixtures (Tasks 2.1, 2.8, 2.9, 2.10, 2.20, 2.23, 2.25, 2.26). When combined with the task's own patches, this can create implicit fixture ordering dependencies. The plan does not document the intended fixture resolution order, which matters for `autouse` fixtures with `scope="class"` combined with per-method patches.

**Recommendation:** Add a general note to Phase 2: "When promoting patches to class-level autouse fixtures, verify that no test method re-patches the same target with different values. If any does, that method should remain in its own class."

---

## MINOR

### m-01: Parametrize of thematically-similar (not identical) clusters may obscure meaning
**File:** `tests/unit/strategy/engine/test_planet_action_engine.py`
**Phase:** 3 (Task 3.29)
**Severity:** MINOR

Task 3.29: "3 event-logging tests — Optional parametrization preserving descriptive names." If the three tests test different event types with meaningfully different assertion logic, parametrizing into one test body obscures which assertion belongs to which event, making failure debugging harder.

**Recommendation:** If the tests differ in assertion logic (not just data), leave them separate. Parametrize only if the assertion shape is identical.

---

### m-02: Large-range parametrize tasks lack sub-range granularity
**Files:** Multiple Phase 3 tasks
**Phase:** 3
**Severity:** MINOR

Several tasks cite large line ranges without specifying which sub-ranges are parametrize targets:
- Task 3.35: lines 38–342 (304 LOC)
- Task 3.36: lines 39–312 (273 LOC)
- Task 3.1: lines 970–1143 (173 LOC for one sub-task)

Large ranges increase the risk of over-parametrizing tests that are thematically but not structurally identical.

**Recommendation:** For tasks with >100 LOC ranges, require the implementer to first verify structural identity and document which specific test functions are targets.

---

### m-03: Deletion of count-based tests loses a regression layer
**File:** `tests/regression/test_deprecated_code_removed.py`
**Phase:** 4 (Task 4.2)
**Severity:** MINOR

(Related to M-03 above, but the specific recommendation is to convert to warnings.)

---

### m-04: Profanity regex removal from test suite relaxes enforcement
**File:** `tests/unit/qa/test_formation_files_have_professional_names.py`
**Phase:** 4 (Task 4.4)
**Severity:** MINOR

Moving the profanity check to a pre-commit hook removes it from CI enforcement. Pre-commit hooks are client-side and optional. If the check must still be enforced in CI, it needs to stay in the test suite or be added as a separate CI pipeline step.

**Recommendation:** Keep the test in the suite AND add as pre-commit hook. The 25 LOC is negligible.

---

### m-05: CAT-11 replacement without explicit new behavior specification
**File:** `tests/unit/ui/screens/battle_setup/test_renderer.py`
**Phase:** 4 (Task 4.12)
**Severity:** MINOR

Task 4.12: "Replace with behavioral assertion on stateless behavior." The plan does not specify what the behavioral assertion should check. "Stateless behavior" for a renderer could mean: no stale surfaces, no leaking state between calls, or no side effects beyond drawing.

**Recommendation:** Specify the exact behavioral assertion: e.g., "assert that calling renderer.render() twice with different inputs produces different outputs, and calling it with the same inputs twice produces identical outputs."

---

### m-06: Verification report out-of-scope items correctly excluded
**Phase:** All
**Severity:** MINOR (positive finding)

All 1 rejected item (S10-CAT12-R01) and 6 out-of-scope items (S09-CAT12-OOS01–OOS04, S11-CAT10-OOS01, S11-CAT12-OOS01) are absent from all five phase checklists. The exclusion is clean — no leakage.

---

### m-07: Manifest–checklist consistency — no significant gaps found
**Phase:** All
**Severity:** MINOR (positive finding)

Spot-check of ~20 files from manifest against checklists and vice versa found no missing or extra entries. The manifest's per-file item counts appear to match the checklist task+sub-task counts. Full automated audit recommended but manual spot-check passes.

---

### m-08: Phase 1 method-level import moves — low risk for test files
**Files:** `tests/unit/core/test_protocols.py`, `tests/unit/ui/components/table/test_selection.py`, `tests/unit/ui/utils/test_formatters.py`, `tests/unit/ui/utils/test_portraits.py`
**Phase:** 1 (Tasks 1.2, 1.23, 1.31, 1.32)
**Severity:** MINOR

Moving method-level imports to module top-level in test files is low risk. Unlike production code (where late imports sometimes break circular dependencies per `01_ARCHITECTURE.md` §Cross-Layer Communication #5), test files rarely have legitimate late-import needs. However, verify that none of the import targets trigger pygame initialization side effects that depend on test ordering.

**Recommendation:** Proceed with the moves. If any test fails after the move due to pygame init issues, revert only that file and document the exception.

---

### m-09: Reference value approach is correct for P2 but stale risk unaddressed
**Phase:** 5 (Multiple tasks)
**Severity:** MINOR

The plan consistently chooses reference values (hardcoded expecteds) over production calls. This is the safe P2 choice — it doesn't depend on production code correctness. However, the plan does not mention that reference values go stale when production logic changes. A stale reference value test passes silently while the production behavior it was intended to validate has changed.

**Recommendation:** Add a general note to Phase 5: "Reference values should carry a comment citing which production commit/version they were validated against. When production logic changes, stale-reference tests should be updated as part of the same change."

---

### m-10: test_multiple_turns_lead_to_breakthrough — right approach but seeding not specified
**File:** `tests/integration/research_workflow/test_workflow.py`
**Phase:** 5 (Task 5.4)
**Severity:** MINOR

Task 5.4 says "Acceptable for stochastic process; consider seeding RNG." This is the right judgment. However, if seeding is adopted, the plan should specify which seed value to use and that the expected outcome is deterministic for that seed.

**Recommendation:** If seeding RNG, pick a seed value and document the expected outcome in the task notes.

---

### m-11: Task 3.46 correctly leaves distinct tests alone
**File:** `tests/unit/ui/utils/test_resource_constants.py`
**Phase:** 3 (Task 3.46)
**Severity:** MINOR (positive finding)

Task 3.46 says "Keep as-is" for `ResourceColors/RESOURCE_ORDER_PRIORITY` tests despite being in the CAT-10 parametrize phase. This demonstrates correct judgment — not all grouped tests should be parametrized. The task should serve as a pattern for other borderline parametrize tasks.

---

### m-12: Task 2.15 correctly preserves distinct edge cases
**File:** `tests/unit/strategy/test_damage_calculator.py`
**Phase:** 2 (Task 2.15)
**Severity:** MINOR (positive finding)

Task 2.15 says "keep distinct edge cases as-is" for the granular boundary test class. This matches the verification report's finding that these are "genuinely distinct edge cases" and not needless complexity.

---

### m-13: Task 5.21 promotes 6 setup_tmpdir to shared fixture — likely correct
**File:** `tests/unit/strategy/test_save_game_service.py`
**Phase:** 5 (Task 5.21)
**Severity:** MINOR

Promoting 6 `setup_tmpdir` autouse fixtures to a single shared fixture should work, but verify that all 6 usages have the same temp directory lifecycle requirements. If any test needs a fresh tempdir, the shared approach may cause cross-test contamination.

---

### m-14: Task 3.42 expand/collapse toggle parametrize — verify idempotency
**File:** `tests/unit/ui/screens/test_battle_panels_extended.py`
**Phase:** 3 (Task 3.42)
**Severity:** MINOR

Parametrizing expand/collapse toggle tests could hide idempotency issues (e.g., double-expand should be a no-op). Ensure the parametrized test still checks toggle idempotency.

---

### m-15: Task 4.7 loading valid themes from registry — data dependency
**File:** `tests/unit/strategy/data/test_race_loader.py`
**Phase:** 4 (Task 4.7)
**Severity:** MINOR

Task 4.7 replaces a magic-number assertion with "Load valid themes from registry." This makes the test data-driven, which is good. But if the registry changes (themes added/removed), the test's valid-set changes. Document this dependency so theme additions don't cause unexpected test failures.

---

### m-16: Phase 5 task 5.11 correctly keeps vector arithmetic in test bodies
**File:** `tests/unit/ai/test_advanced_behaviors.py`
**Phase:** 5 (Task 5.11)
**Severity:** MINOR (positive finding)

Task 5.11 says "Acceptable for spatial behavior tests; document expected geometry in fixtures." This is the correct judgment for spatial behavior tests where derivation from fixtures provides the regression value.

---

### m-17: Task 5.25 correctly preserves test_load_resource_icons_fallback
**File:** `tests/unit/ui/test_build_queue_portraits.py`
**Phase:** 5 (Task 5.25)
**Severity:** MINOR (positive finding)

Task 5.25 says "Keep" — the test has a valid purpose and doesn't need CAT-12 remediation. This demonstrates good judgment.

---

## INFO

### I-01: Design document is a stub — no actionable design guidance
**File:** `Projects/active_projects/PROJ-323/design.md`
**Severity:** INFO

The design document is empty under "Initial Analysis," "Swarm Findings Summary," and "Key Patterns to Reuse." An implementer has no architecture guidance beyond what the checklists provide. For a project touching 117+ test files, this is acceptable since the work is per-file polish, but if future phases need cross-cutting design decisions, this document should be populated.

---

### I-02: decisions.md has only 2 entries
**File:** `Projects/active_projects/PROJ-323/decisions.md`
**Severity:** INFO

The decisions log has only the initialization entry and the verification note. As implementation proceeds, decisions about specific parametrize approaches, fixture scoping, and cross-project coordination must be logged here.

---

### I-03: Phase execution order is implicit, not documented
**Phase:** All
**Severity:** INFO

The plan lists 5 sequential phases but does not recommend an execution strategy. For a P2 polish project touching 117 files, the order of phases matters: Phase 1 simplifications may be pre-work for Phase 3 parametrizations, while Phase 2 nesting reductions could be done independently.

**Recommendation:** Document the intended execution order and any inter-phase dependencies.

---

### I-04: No rollback or validation checkpoints between phases
**Phase:** All
**Severity:** INFO

Each phase has a `validate_phase.py` checkpoint, but these only check checklist completion, not test health. With 159 test modifications planned, intermediate validation (run the full suite after each phase, not just the affected test files) would catch regressions earlier.

**Recommendation:** Add a pre-phase validation step: run the full affected test suite before starting a phase to establish a green baseline, and again after to detect regressions.

---

### I-05: Verification report cross-shard context is underutilized
**Phase:** All
**Severity:** INFO

The source test review identified 3 cross-shard duplicates (DUP-001, DUP-002, DUP-003), 4 helper duplications (HLP-001 through HLP-004), and 3 anti-pattern clusters (APC-001, APC-002, APC-003). PROJ-323's tasks reference these only implicitly. For example, DUP-001 (superweapon handler duplication) is the root cause behind Tasks 3.2 and 3.30, but neither task references the cross-shard finding.

**Recommendation:** Cross-reference relevant DUP/HLP/APC IDs in task notes so implementers understand the broader pattern they're fixing.

---

## Verification Matrix

| Claim | Status | Notes |
|-------|--------|-------|
| 156 verified items map cleanly to tasks | CONFIRMED | All 156 verified items appear in checklists |
| 1 rejected item not in any checklist | CONFIRMED | S10-CAT12-R01 correctly excluded |
| 6 out-of-scope items not in any checklist | CONFIRMED | All 6 correctly excluded |
| 3 needs-rework items adjusted in checklists | CONFIRMED | Adjustments present but need pre-work resolution (M-05, M-09) |
| Manifest files match checklist files | CONFIRMED | Spot-check passed; full automated audit recommended |

---

## Cross-Project Overlap Map

Files appearing in PROJ-323 + at least one sibling project:

| File | PROJ-321 | PROJ-322 | Severity |
|------|----------|----------|----------|
| `test_testruncard_propulsion.py` | CAT-2 (delete?) | — | **CRITICAL** (C-01) |
| `test_commands.py` | CAT-2, CAT-3 | DUP-002 | **CRITICAL** (C-02, M-11) |
| `test_build_queue_screen.py` | CAT-2 | Phase 2, 5 | **MAJOR** (M-07) |
| `test_battle_runner.py` | — | Phase 6 HLP-002 | MINOR |
| `test_battle_runner_di.py` | — | Phase 1, 6 | MINOR |
| `test_persistence.py` | — | Phase 4 | MINOR |
| `test_battle_state_validation.py` | — | Phase 1 | MINOR |
| `test_fleet_cargo_resources.py` | — | Phase 6 | MINOR |
| `test_planetary_yard_requirement.py` | — | Phase 6 | MINOR |
| `test_resupply_engine.py` | — | Phase 2 | MINOR |
| `test_superweapon_command_handlers.py` | — | Phase 1, 6 | MINOR |
| `test_superweapon_handler_validation.py` | — | Phase 6 | MINOR |
| `test_service_edge_cases.py` | — | Phase 1 | MINOR |
| `test_command_handlers.py` | — | Phase 6 DUP-002 | MINOR |
| `test_planet_specific_colonization.py` | — | Phase 6 | MINOR |
| `test_colonize_validator.py` | — | Phase 6 | MINOR |
| `test_virtual_table.py` | — | Phase 3 | MINOR |
| `test_component_modifier_grid_panel.py` | CAT-1 | Phase 5 APC-001 | MINOR |
| `test_design_report_panel.py` | — | Phase 5 APC-001 | MINOR |
| `test_race_identity_panel.py` | CAT-1, CAT-2 | Phase 5 APC-001 | MINOR |
| `test_system_tree_panel.py` | CAT-2 | Phase 5 APC-001 | MINOR |
| `test_renderer.py` | CAT-2 | Phase 5 APC-002 | MINOR |
| `test_battle_panels_extended.py` | — | Phase 1 | MINOR |
| `test_build_queue_list_window.py` | — | Phase 3, 5 | MINOR |
| `test_fleet_report_filters.py` | — | Phase 2 HLP-001 | MINOR |
| `test_fleet_report_window.py` | CAT-1 | Phase 5 APC-001 | MINOR |
| `test_workshop_screen.py` | — | Phase 5 APC-001 | MINOR |
| `test_new_game_setup.py` | — | Phase 5 APC-002 | MINOR |
| `test_race_flag_gallery.py` | CAT-1 | Phase 5 APC-001 | MINOR |
| `test_race_summary_panel.py` | CAT-1 | Phase 5 APC-001 | MINOR |
| `test_unified_entry_guard.py` | CAT-2 | — | MINOR |
| `test_strategy_menu_panel.py` | CAT-1 | — | MINOR |
| `test_combat_types.py` | CAT-1 | — | MINOR |
| `test_superweapon_orders.py` | CAT-1 | — | MINOR |
| `test_deprecated_code_removed.py` | CAT-3 | — | MINOR |
| `test_modifier_service.py` | — | Phase 2 | MINOR |

Files that appear in all three: `test_commands.py`, `test_component_modifier_grid_panel.py`, `test_race_identity_panel.py`, `test_fleet_report_window.py`.

---

*Report generated by OpenCode plan review. Request ID: req_20260503_191424_2df3b4.*

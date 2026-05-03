# Plan Review: PROJ-322 P1 brittle-bloated remediation

**Review Date:** 2026-05-03
**Request ID:** req_20260503_191353_9376a0
**Scope:** 19 files (PROJ-322 plan/design/manifest/6 checklists + verification + source review + 3 test-review artifacts + 2 sibling project manifests)
**Review Type:** plan (pre-implementation)

---

## Findings Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 1 |
| MAJOR | 8 |
| MINOR | 6 |
| INFO | 4 |
| **Total** | **19** |

---

## CRITICAL

### C-001: Task 5.15 (APC-001-F15, test_build_queue_screen.py) strategy is ambiguous and the wrong approach is the likely default
**File:** `Projects/active_projects/PROJ-322/phase_5_checklist.md:154-160`
**Severity:** CRITICAL

Task 5.15 says "Replace the `__new__` bypass-init across the entire file (~580 LOC) with `make_ui_widget(BuildQueueScreen, **kwargs)` **or** migrate to integration tests." Seven integration counterparts already exist at `tests/integration/ui/build_queue_screen/` covering basics, tools tips, drag handling, controller, queue selector, portrait logging, and conftest. The `make_ui_widget` factory would reimplement ~580 LOC of unit tests that essentially duplicate what the integration tests already prove. An agent reading the "or" will take the first path (factory) because it's listed first—wasting ~290 LOC of effort for zero net coverage gain.

**Recommendation:** Commit to deletion of the 580-LOC unit file and rely on existing integration tests. If gaps remain, add targeted integration tests rather than factory-based unit tests.

---

## MAJOR

### M-001: APC-001 factory approach is wrong for complex screens lacking integration counterparts
**File:** `Projects/active_projects/PROJ-322/phase_5_checklist.md:109-115`
**Severity:** MAJOR

Task 5.10 (APC-001-F10, test_workshop_screen.py, ~450 LOC) lists "`make_ui_widget(WorkshopScreen, **kwargs)` **or** migration to integration tests." Unlike BuildQueueScreen, WorkshopScreen has **no** integration test counterparts. A `make_ui_widget` factory for WorkshopScreen with ~50 lambda method overrides would still test mock wiring, not production behavior. An integration test suite should be created first.

**Recommendation:** Resolve the "or" by: (1) create integration tests with headless pygame_gui for WorkshopScreen core flows, then (2) delete the unit file. Apply the same pattern for any APC-001 file >200 LOC lacking integration counterparts.

### M-002: CAT-5 Task 2.11 fixture rescoping risks cross-test pollution with mutable MagicMocks
**File:** `Projects/active_projects/PROJ-322/phase_2_checklist.md:105-111`
**Severity:** MAJOR

Task 2.11 proposes rescoping `sample_snapshot`, `mock_ui_manager`, `mock_panel`, `mock_resource_icons` (lines 72-88 of test_empire_treasury_panel.py) from function to module scope. Spot check confirms these are `MagicMock` objects—technically mutable. The plan says "after verifying no test mutates shared mock state" but provides no systematic verification mechanism. A test that calls `mock_panel.assert_called_once_with()` will break subsequent tests sharing the same mock (assertion state is mutated).

**Recommendation:** Either (a) add a conftest `autouse` fixture that calls `reset_mock()` on shared mocks between tests, or (b) keep function scope and instead memoize only the expensive parts (pygame.init, data loading) in a separate module-scoped fixture.

### M-003: Cross-project scope leakage: 4 files face delete-in-P0 vs rewrite-in-P1 conflict
**Files:** `tests/unit/modifiers/test_seeker_multi_ability.py`, `tests/unit/strategy/services/test_fleet_navigation_mutual_pursuit.py`, `tests/unit/strategy/services/test_fleet_navigation_no_mock_hack.py`, `tests/integration/test_app_integration.py`
**Severity:** MAJOR

These 4 files appear in both PROJ-321 (P0, CAT-2 "tests-nothing-real" — likely deletion) and PROJ-322 (P1, APC-002 — rewrite with behavioral tests). If PROJ-321 deletes a file entirely, PROJ-322's corresponding task becomes moot but not harmful. However, if PROJ-321 deletes only some test functions and PROJ-322 rewrites others in the same file, merge conflicts and duplicated effort result. The plans share no explicit execution order precondition.

**Recommendation:** Add a precondition to `plan.md`: PROJ-321 must complete before PROJ-322 Phase 5 begins. For the 4 overlapping CAT-2/APC-002 files, add a note in the Phase 5 checklist stating: "If PROJ-321 deleted this file, skip this task."

### M-004: Task 5.23 (APC-002-F07) replaces source-inspection with test of private method `_rebuild_ui`
**File:** `Projects/active_projects/PROJ-322/phase_5_checklist.md:228-234`
**Severity:** MAJOR

Task 5.23 proposes: "Replace `inspect.getsource(FleetBattleSetupScreen._rebuild_ui)` with a behavioral test that calls `_rebuild_ui` and asserts on the resulting UI state." The replacement still tests a private method (`_rebuild_ui`). This swaps one anti-pattern (source inspection) for another (private method testing). The correct fix is to test through the public API (`handle_event` with a UI event that triggers rebuild, then assert observable UI state).

**Recommendation:** Rewrite as: "Test through `handle_event` or `update` public methods; assert on observable UI element state after the event that triggers `_rebuild_ui` internally."

### M-005: CAT-7 Task 4.3 Event-sync requires production code changes not scoped in this project
**File:** `Projects/active_projects/PROJ-322/phase_4_checklist.md:33-39`
**Severity:** MAJOR

Task 4.3 proposes replacing `time.sleep()` polling loops in `test_background.py` with Event-based synchronization. Spot check confirms `LLMBackgroundCall` lacks any `threading.Event` mechanism for tests to wait on. Adding one requires modifying production code (`game/services/llm/background.py`)—a cross-cutting change the plan does not acknowledge. If the Event is not correctly set in all termination paths (normal completion, error, cancellation), the test will hang.

**Recommendation:** Either (a) scope the production change explicitly with a note that `LLMBackgroundCall` must expose a completion event, or (b) use `freezegun`/mocked clock to make polling deterministic without production changes. Prefer (b) for P1 tier to minimize blast radius.

### M-006: Phase 5/Phase 3 coordination creates 11 cross-phase dependencies with no ordering guidance
**File:** `Projects/active_projects/PROJ-322/phase_5_checklist.md` (multiple tasks)
**Severity:** MAJOR

Eleven APC tasks in Phase 5 reference coordinated Phase 3 tasks (e.g., Task 5.27 "Coordinate with Task 3.17"; Task 5.7 "Coordinate with Task 3.20"; Task 5.29 "Coordinate with Task 3.19"). The plan does not specify whether Phase 3 must complete before Phase 5, or if they can interleave. An agent working Phase 5 first would implement the APC fix without the prerequisite CAT-6 refactor from Phase 3, potentially undoing Phase 3 work.

**Recommendation:** Add a phase ordering requirement in `plan.md`: "Phase 3 (CAT-6) must complete before Phase 5 (APC cluster) begins, since Phase 5 tasks build on the public-API/boundary-patching refactors performed in Phase 3." Tag each cross-phase task pair with a shared marker for validation.

### M-007: Task 5.7 (APC-001-F07) is misclassified—belongs in APC-003, risks wrong remediation
**File:** `Projects/active_projects/PROJ-322/phase_5_checklist.md:82-88`
**Severity:** MAJOR

Task 5.7 for `test_fleet_report_window_multi_select.py` is filed under APC-001 (`__new__` bypass-init) but the plan correctly notes "Pattern is closer to APC-003 than APC-001." The spot check confirms: the file patches private methods (`_init_layout`, `refresh_list`) with 5-level nested `with patch()` blocks. Applying a `make_ui_widget` factory (the APC-001 default fix) would be wrong here—the remediation should focus on boundary patching (APC-003 pattern). The task description acknowledges this but the overall Phase 5 structure buries it under the wrong cluster heading, increasing risk of incorrect implementation.

**Recommendation:** Move Task 5.7 to the APC-003 section (alongside Tasks 5.27–5.34), or rename the section heading to "APC-001 / APC-003 boundary overlap" to make the dual nature explicit.

### M-008: 21 files overlap between PROJ-321 (P0) and PROJ-322 (P1) manifests with no conflict detection
**File:** `Projects/active_projects/PROJ-322/manifest.md` vs `Projects/active_projects/PROJ-321/manifest.md`
**Severity:** MAJOR

21 files appear in both manifests. Sixteen are APC-001 UI files where PROJ-321 handles CAT-1/CAT-2 findings and PROJ-322 handles APC-001 findings on the same file. While the findings target different test functions, both projects will touch the same files, creating merge-conflict risk. The plans contain no `proj-parallel` conflict metadata or execution ordering.

**Recommendation:** Add a `## Cross-Project Dependencies` section to `plan.md` documenting the overlap. Tag overlapping files with `# PROJ-321-coord` in the manifest. Establish that PROJ-321 must complete before PROJ-322 Phase 5 begins (consistent with M-003).

---

## MINOR

### N-001: DUP-001 adjusted suggestion is correct but missing fixture factory specification
**File:** `Projects/active_projects/PROJ-322/phase_6_checklist.md:15-21`
**Severity:** MINOR

The adjustment to keep DI validation tests separate from execution tests is sound—spot check confirms they test different concerns (DI plumbing vs execution outcomes). However, Task 6.1 says "create a parameterized fixture factory that supplies BOTH contract variants" without specifying what this factory provides or how it avoids the duplication problem differently than the original "merge classes" proposal.

**Recommendation:** Add one line to Task 6.1 specifying what the fixture factory parameterizes (e.g., `@pytest.mark.parametrize('handler_cls, mock_session_factory', [...])`) so the agent knows what to build.

### N-002: Task 1.8 (S08-CAT4-003 NEEDS_REWORK) keeps tests as documentation-only but description is incomplete
**File:** `Projects/active_projects/PROJ-322/phase_1_checklist.md:78-84`
**Severity:** MINOR

Task 1.8 keeps 5 colony-species edge-case tests with documentation-only changes. The task says "Add a brief docstring/note to each making the edge case explicit" but doesn't specify what to document. The 5 edge cases enumerated in the task body (single-resource pass-through, multi-resource min, zero-collapses, all-ones, empty-dict-returns-1) should be explicitly referenced as the required documentation content.

**Recommendation:** Include the 5 edge-case descriptions in the task body so the agent knows what to write in each docstring.

### N-003: CAT-7 Task 4.6 bundles 2 findings under 1 task with different remediation strategies
**File:** `Projects/active_projects/PROJ-322/phase_4_checklist.md:60-67`
**Severity:** MINOR

Task 4.6 bundles S08-CAT7-002 (4 `time.sleep(0.02)` calls, event-based sync) and S08-CAT7-003 (`_BlockingProvider.complete` polling, Event/Condition or mocked time). The two sub-items require different remediation approaches (event sync for one, mock clock for the other), making the task harder to verify and check off atomically.

**Recommendation:** Split into Task 4.6a (S08-CAT7-002, Event sync) and Task 4.6b (S08-CAT7-003, mock clock).

### N-004: Task 1.1 merges files without verifying the receiving file's test infrastructure compatibility
**File:** `Projects/active_projects/PROJ-322/phase_1_checklist.md:15-21`
**Severity:** MINOR

Task 1.1 proposes merging `test_beam_weapon_bindings.py` (3-class structure) into `test_weapon_ability_bindings.py`. The task doesn't verify whether the receiving file's fixtures, conftest, or import dependencies are compatible with the merged tests. A fixture name collision or import conflict could cause cascading failures.

**Recommendation:** Add a pre-step: "Verify receiving file shares compatible fixtures/conftest; if not, migrate the shared fixture to parent conftest first."

### N-005: Phase 5 contains 34 items—the largest phase, risks agent context exhaustion
**File:** `Projects/active_projects/PROJ-322/phase_5_checklist.md`
**Severity:** MINOR

Phase 5 bundles all 34 APC items (APC-001 16 + APC-002 10 + APC-003 8) into one phase checklist. This is the largest phase by task count and the most complex (cross-cutting changes across 35+ files). An agent with single-shot context may not complete it in one session, losing state between restarts.

**Recommendation:** Split Phase 5 into Phase 5a (APC-001: 16 tasks, `make_ui_widget` factory introduction + migration) and Phase 5b (APC-002: 10 tasks + APC-003: 8 tasks, behavioral replacements), or at minimum add an explicit progress tracking mechanism.

### N-006: MANIFEST.md lists 107 files but only 5 are NEW production fixtures—missing conftest.py entries
**File:** `Projects/active_projects/PROJ-322/manifest.md:6-16`
**Severity:** MINOR

The manifest lists 5 new fixture files as "Production" type. But the plan also creates entries in `tests/unit/simulation/conftest.py` (HLP-002, Task 6.5)—this isn't tracked as a file with a modified/created indicator. The manifest's "NEW" vs "UPDATED" tags only appear in the Notes column, not as a filterable field.

**Recommendation:** Add a "NEW" / "MODIFIED" column to the manifest table so agents can quickly distinguish creation from modification.

---

## INFO

### I-001: Manifest consistency verified—14 manifest-only files are valid receiver/sibling references
**File:** `Projects/active_projects/PROJ-322/manifest.md`
**Severity:** INFO

Automated audit confirms all 14 manifest-only files (not listed as primary **File:** in any checklist) are mentioned in checklist task bodies as receiver files (e.g., `test_weapon_ability_bindings.py` receives merged tests), sibling files (e.g., `test_combat.py` has duplicated coverage), or shared fixtures (e.g., `test_ui_widget_factory.py` is referenced in Task 5.0). Five additional files initially flagged as missing were found in task body mentions on deeper search. Claim validated.

### I-002: Verification report sanity confirmed—no rejected or out-of-scope items leaked
**File:** `Projects/active_projects/PROJ-322/findings/verification_report.md`
**Severity:** INFO

All 1 rejected item (S11-CAT5-R01, test_damage_calculator.py) and 3 out-of-scope items (S08-CAT4-OOS01, S11-CAT5-OOS01, APC-002-OOS01) are confirmed absent from all 6 phase checklists. All 4 needs-rework items (S05-CAT5-001, S08-CAT4-003, S10-CAT6-001, DUP-001) are properly acknowledged with adjusted recommendations in their respective tasks.

### I-003: No overlap between PROJ-322 and PROJ-323 scope
**File:** `Projects/active_projects/PROJ-322/manifest.md` vs `Projects/active_projects/PROJ-323/manifest.md`
**Severity:** INFO

Zero files appear in both manifests. The CAT-8..CAT-12 exclusion boundary in PROJ-322's scope definition is correctly enforced. PROJ-323 (P2, 147 files) is fully disjoint from PROJ-322 (P1, 107 files).

### I-004: All CAT-7 sleep replacements have viable deterministic alternatives; no sleep must remain
**File:** `Projects/active_projects/PROJ-322/phase_4_checklist.md`
**Severity:** INFO

Spot-check of all 9 CAT-7 findings confirms feasible replacements: `os.utime()` for mtime-based sleeps (Tasks 4.2, 4.7, 4.8), mocked clock/`freezegun` for duration assertions (Tasks 4.4, 4.5), and Event sync or mocked clock for polling loops (Tasks 4.3, 4.6). No benchmark or deliberate latency simulation sleep was found among the 9 items.

---

## Additional Observations

- **Plan vs manifest heading mismatch:** `manifest.md` labels 5 new fixture files as "Production" type, but fixture files are test infrastructure, not production code. Consider changing to "Test Infrastructure."
- **LOC savings risk:** Phase 5 claims ~2,200 LOC reduction across 34 tasks, but if `make_ui_widget` factory requires significant per-widget customization (as Task 5.0's docstring hints), the net savings may be smaller. Track actual vs planned LOC delta per phase.
- **Missing `test_fleet_navigation_mutual_pursuit.py`:** PROJ-321 lists this under CAT-2 (tests-nothing-real, 1 item) while PROJ-322 lists APC-002-F02. If PROJ-321 deletes the file, PROJ-322 Task 5.18 is moot. This is covered by M-003 but worth flagging specifically.

# Agent 4 Report: Below-the-Line Items & Continuation Work

## 1. Below-the-Line Verification Audit

### 1.1 Rejected Item

**S10-CAT12-R01:** `tests/unit/strategy/generation/test_storm_generator.py:181-190`
- **Original claim:** The `test_storms_avoid_star_hexes` test uses `len(overlap) == 0` where `isdisjoint()` would be "simpler." Filed as CAT-12 (logic-heavy test).
- **Rejection rationale:** The original SHARD_10 reviewer flagged this as CAT-12, but the verifier in VERIFIED_SHARD_10.md disputed this: the test makes no assumptions about *how* storm generation works internally — it tests a pure output property (non-overlap). The `isdisjoint()` suggestion is a pure style preference; both forms are equally valid and neither changes test quality. Downgraded to CAT-0 (not a valid finding).
- **My assessment:** **SOUND.** The test at lines 181-190 computes `star_hexes` as a set, then checks `star_hexes.intersection(storm_hexes)` with `assert len(overlap) == 0`. Both `len(overlap) == 0` and `isdisjoint()` express the same semantic — no set overlap. The test verifies a behavioral invariant (storms don't overlap stars), not implementation-dependent logic. This is a ~1-line stylistic opinion, not a test-quality issue. The original CAT-12 classification was incorrect; the rejection correctly downgraded to CAT-0.
- **Evidence:** VERIFIED_SHARD_10.md lines 222-235: "This does NOT meet CAT-12 criteria. The test makes no assumptions about *how* storm generation works internally... Downgrade from CAT-12/MINOR to CAT-0 (not a valid finding)." Code at test_storm_generator.py:181-190 confirms the set-intersection approach.

### 1.2 Out-of-Scope Items

**S09-CAT12-OOS01 through OOS04:** 4 items classified "intentional_property_test"
- **Classification rationale:** VERIFIED_SHARD_09.md line 534: "4 CAT-12 findings disputed and downgraded to NOTED. The CAT-12 category (logic-heavy tests) requires that the test computes expected values at runtime or reimplements SUT logic. These four tests all call production code and assert against hardcoded constants or properties — they are valid property-based/behavioral tests."
- **My assessment:** **ALL SOUND.**
  - **OOS01** (F-23 in shard 9): Calls `find_path_deep_space(start, end)` and asserts hex adjacency `dist == 1` against actual path output. Hardcoded constant, not computed. Legitimate property-based test.
  - **OOS02** (F-27 in shard 9): Calls `ShipCombatEngine.solve_lead()` and asserts `abs(t - 10.0) < 0.1`. The expected value 10.0 is hardcoded with derivation comments. Legitimate behavioral test.
  - **OOS03** (F-28 in shard 9): Runs thrust cycle with mass=100 and mass=10000, asserts `fast_speed > slow_speed`. Directional property assertion (higher mass → lower speed), not specific-value assertion. Report itself acknowledges: "Fine as-is but noted."
  - **OOS04** (F-32 in shard 9): Calls `system_count_slider_curve(t)` and asserts `max_jump <= 1`. Hardcoded constant. Legitimate property-based test.
- **Evidence:** VERIFIED_SHARD_09.md lines 301-454 provide line-level verification of each claim. All four tests call production code and assert against hardcoded constants/properties — they do NOT reimplement SUT logic. Correctly excluded from P2 CAT-12 scope.

**S11-CAT10-OOS01:** 10 boundary tests classified "legitimate_distinct_or_integration"
- **Classification rationale:** Maps to F-10 in VERIFIED_SHARD_11.md: `TestDamageLayerBoundaryConditions` (10 tests at lines 609-744). Each test exercises a genuinely distinct edge case (zero damage, exact component HP, exact layer HP, fractional, very small, very large, many components, component with 1 HP). The verifier noted: "Parametrizing all 10 into one test... would reduce LOC but makes the test harder to read — each case's assertion logic differs... The shared pattern is superficial."
- **My assessment:** **SOUND.** The 10 boundary tests span qualitatively different edge cases with distinct assertion logic per case. The verifier correctly downgraded from MAJOR to MINOR and flagged as out-of-scope for P2. Also handled in Phase 2 Task 2.15 which was correctly left as-is ("keep distinct edge cases as-is").
- **Evidence:** VERIFIED_SHARD_11.md lines 69-72: "Each test tests a genuinely distinct edge case... parametrization would reduce LOC but makes the test harder to read." Phase 2 Task 2.15 confirms this was intentionally left as-is.

**S11-CAT12-OOS01:** Integration tests classified "legitimate_distinct_or_integration"
- **Classification rationale:** Maps to F-14 in VERIFIED_SHARD_11.md: `test_reorder_queue` (52 lines) and `test_remove_from_queue` (42 lines) involving drag-drop event simulation through `handle_event`. The verifier noted: "These are integration tests that genuinely exercise the drag-drop event path... The complex event construction is inherent to testing pygame drag-drop."
- **My assessment:** **SOUND.** Drag-drop testing in pygame requires manual event simulation (MOUSEBUTTONDOWN → MOUSEMOTION → MOUSEBUTTONUP). A `_simulate_drag` helper would reduce duplication but not eliminate the inherent verbosity of pygame event construction. The verifier correctly downgraded from MAJOR to MINOR. This is a legitimate integration test pattern, not implementation-dependent test logic.
- **Evidence:** VERIFIED_SHARD_11.md lines 93-96: "These are integration tests that genuinely exercise the drag-drop event path through `handle_event`... legitimate integration test pattern that happens to be verbose."

---

## 2. Continuation Recommendations

### 2.1 Remaining Needs-Rework Items

| Item ID | Description | Worth completing? | Priority |
|---------|-------------|-------------------|----------|
| S06-CAT10-001 | Parametrize set-filter tests in test_fleet_data_source.py | **NO — target tests deleted by upstream.** Phase 3 Task 3.4 notes: "pass 2 obsolete: set-filter tests no longer present in file — deleted by upstream cleanup." The file exists but the specific tests were removed by PROJ-321/322. | N/A |
| S09-CAT9-004 | Extract _make_projectile helper in test_projectile_manager.py | **NO — target file deleted.** Verified: `tests/unit/simulation/projectile/test_projectile_manager.py` does not exist. Deleted by upstream PROJ-321. Phase 1 Task 1.8 confirms: "skipped — upstream project already deleted target file." | N/A |
| S10-CAT8-002 | Document 2-level patch nesting in test_fleet_navigation_action_timing.py | **YES — completed.** The 8-line class-level docstring was added at lines 17-27 documenting why the 2-level nesting is intentional (separate DI dependencies in different import paths; DI injection would change production signatures). `grep` confirms the `PROJ-323 Task 2.14` note is present. The nesting reduction (0 LOC saved) was the correct call — DI injection would violate the P2 constraint of no production-signature changes. | MED (already done) |

**Summary:** All 3 needs-rework items are resolved (2 moot via upstream deletions, 1 completed via documentation). No action needed.

### 2.2 No-Op Rationale Weaknesses

Review of all ~23 no-op/deferred tasks across 5 phases:

All deferral rationales are sound. Key patterns observed:
- **"Real construction requires pygame_gui + full dependency graph"** (Tasks 2.19, 2.24, 2.28, 2.30, etc.): Converting bypass-init unit tests to real `__init__` would migrate hundreds of LOC from unit scope to integration scope. Correctly excluded from P2.
- **"Production-signature change forbidden in P2"** (Tasks 2.1, 2.27, 5.22): Promoting private helpers to public or injecting dependencies requires production API changes. Correctly deferred.
- **"Below 3-member parametrize threshold"** (Tasks 3.15, 3.27, 3.37): 2-test clusters do not benefit from parametrization. Per plan-review M-08.
- **"Fixture would add indirection without removing duplication"** (Tasks 1.13, 1.14, 1.16): Module-level helpers already serve the deduplication purpose. Wrapping in `@pytest.fixture` is syntactic overhead.
- **"Cross-file dedupe out of P2 scope"** (Tasks 1.10, 4.8, 4.10, 4.13): Requires production-side schema/catalog definitions or coordination between test files.

**No weak rationales found.** All no-op decisions are well-documented with clear reasoning.

### 2.3 Leave-As-Is Reconsiderations

The 10 "leave-as-is/documented-intent" items from pass 2 (decisions.md line 13):

| Task | Item | Rationale | Reconsideration |
|------|------|-----------|-----------------|
| 5.1b | S06-CAT12-002 — set comparison | Existing identity-per-element assertion is more stringent than set equality | **No.** Identity comparison is stronger. |
| 5.3 | S04-CAT12-002 — turn execution helpers | Tests exercise different orchestration paths; folding conflates concerns | **No.** Distinct orchestration paths need distinct tests. |
| 5.7 | S08-CAT12-003 — habitability drain test | Private `_process_queue_tick_dynamic` call is intentional — public turn engine includes too many side effects | **No.** Focused test of production-drain without full turn side effects is deliberate. |
| 5.11 | S05-CAT12-001 — vector arithmetic | Added docstring documenting spatial-test conventions; inline comments preserved | **No.** Documentation approach is appropriate for P2. |
| 5.15 | S10-CAT12-001 — physics formulas | 565-line file documents boundary semantics; inline formulas ARE the cross-check | **No.** Formulas cross-check production against documented math; replacing with production imports loses the cross-validation property. |
| 5.24 | S03-CAT12-001 — planet list components | pygame_gui UIButton has no public observable state; mock call inspection IS the integration boundary | **No.** When the UI toolkit lacks public state introspection, mock call inspection is the correct boundary. |
| 3.15 | S04-CAT10-001 — static_value_ability | Below ≥3-member parametrize threshold (plan-review M-08) | **No.** 2-test clusters don't benefit from parametrization. |
| 3.27 | S06-CAT10-002 — population_model | Below ≥3-member parametrize threshold | **No.** Same as above. |
| 3.29 | S10-CAT10-002 — planet_action_engine | Only 2 of 3 tests share enough setup; below threshold | **No.** The third test (no_event) exercises a different code path. |
| 3.32 | S01-CAT10-003 — planet_validation | Two parametrize blocks test different validation paths; merging conflates concerns | **No.** Distinct validation paths deserve distinct test blocks. |

**No leave-as-is items warrant reconsideration.** All 10 have solid quality-preserving rationales.

### 2.4 Priority Continuation Tasks

All below-the-line items are correctly classified. All needs-rework items are resolved. All no-ops and leave-as-is items have sound rationales. The only remaining P2-appropriate continuation work is:

| Priority | Task | Description | Estimated LOC | Rationale |
|----------|------|-------------|---------------|-----------|
| 1 (highest) | Task 3.34 | Parametrize 11-handler `fleet_not_found` error-path test cluster in `test_command_handlers.py`. Each of 11 distinct handler classes (Colonize, Move, Intercept, Join, ColonizeMission, ClearOrders, Transfer, SplitFleet, MergeFleets, RemoveFromConstructionQueue, AddToConstructionQueue) has one structurally identical test. | ~150-200 LOC saved | The original deferral rationale ("would destroy per-class organization aligned with production structure") is reasonable but the savings are substantial. A class-level parametrize with a per-handler `mock_cmd` factory fixture preserves the test-coverage matrix while collapsing 11 near-identical tests. The decision log notes "Recommend a follow-up project... once DUP-002 lands fully." DUP-002 is a PROJ-322 code-consolidation item that doesn't gate test consolidation. This could proceed independently. |
| 2 | Task 4.12 | Replace `test_renderer_is_stateless_between_calls` with behavioral assertion. Currently deferred: "requires careful invariant selection beyond P2." | ~10 LOC | Low-risk refinement: the existing test already computes two results and compares them. Minimal work to express the invariant explicitly. |
| 3 (lowest) | N/A | Sweep for missed CAT-8..12 items not in the manifest. | ~0-50 LOC | The manifest was generated from 156 verified items across 5 categories. The verification report explicitly excluded rejected and out-of-scope items. Given the thoroughness of the third-pass verification, probability of missed items is very low. |

---

## 3. Findings Summary

| ID | Severity | Description |
|----|----------|-------------|
| FND-P4-001 | INFO | All 7 below-the-line items (1 rejected + 6 out-of-scope) are correctly classified. The S10-CAT12-R01 rejection is sound (pure style preference, not test quality). All 4 S09 OOS items are legitimate property-based tests asserting hardcoded constants against production output. S11-CAT10-OOS01 is genuinely distinct boundary edge cases. S11-CAT12-OOS01 is legitimate pygame integration test verbosity. |
| FND-P4-002 | INFO | All 3 needs-rework items are resolved: S06-CAT10-001 (target tests deleted upstream), S09-CAT9-004 (target file deleted upstream), S10-CAT8-002 (documentation applied; confirmed present at test_fleet_navigation_action_timing.py:17-27). No rework action needed. |
| FND-P4-003 | INFO | All 23+ no-op/deferred items have sound rationales. No weak justifications found. Common patterns: "production-signature change forbidden in P2", "real construction converts unit to integration scope", "below 3-member parametrize threshold", "cross-file dedupe requires production-side artifacts". |
| FND-P4-004 | INFO | All 10 leave-as-is items have solid quality-preserving rationales. None warrant reconsideration. |
| FND-P4-005 | LOW | Task 3.34 (11-handler parametrization) is the lowest-value-but-still-worth-doing continuation. ~150-200 LOC of test code across structurally identical handler-specific fleet_not_found tests. DUP-002 reference in deferral rationale is non-blocking. Could proceed as independent P2 follow-up. |

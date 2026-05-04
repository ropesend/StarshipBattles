# Skeptical Audit: PROJ-325/326/328 As-Shipped State

**Review Type:** consistency (skeptical audit)
**Request ID:** req_20260504_132544_ccc15c
**Review Mode:** normal (not lightweight)
**Scope:** PROJ-325 (PROJ-323 corrections + Task 3.34/3.37 + RaceSetupScreen PoC), PROJ-326 (Test linter + SystemTreePanel + Facade contract), PROJ-328 (UIWindow MVVM rollout Phases A/B/C)
**Agents Deployed:** 5 specialized review agents
**Completed:** 2026-05-04

---

## Findings Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| MAJOR | 1 |
| MINOR | 15 |
| INFO | 0 |

Overall: **Clean shipment.** No blocking defects. Pattern application is consistent across 7 production classes. PROJ-326 linter is well-engineered. Test suite passes with no regressions. The main issues are documentation gaps and inaccurate LOC/test-count claims in project materials.

---

## MAJOR Findings

### MAJ-001: 12 tests removed from test_fleet_report_window.py without documented rationale
**File:** `tests/unit/ui/screens/test_fleet_report_window.py`
**Claim:** 28 → 19 tests. **Actual:** 30 → 18 tests. Twelve tests were removed. The file shrank from ~600 LOC to 285 LOC.
**Risk:** Removed tests may have covered behavior now untested. The checklist (PROJ-328 phase_1_checklist.md Task A.4) notes "dropped redundant 'test the mock plumbing' tests" but does not enumerate the dropped tests or verify that no production behavior coverage was lost.
**Remediation:** Audit the 12 removed tests against the current test file to confirm no behavioral coverage gap. If all were mock-plumbing redundancies, document that determination explicitly in the checklist notes.

---

## MINOR Findings

### Construction Consistency (7 findings from agent_construction_consistency_report.md)

**MIN-001: Bypass guard duplicated between two window hierarchies** (`game/ui/screens/new_game_setup_screen.py:177-191`, `game/ui/screens/race_setup/screen.py:151-163`)
RaceSetupScreen and NewGameSetupScreen each inline the bypass guard logic. StrategyModalWindow subclasses inherit it from the base class. Low-priority technical debt — a `BypassableUIWindow` mixin could unify the two families.

**MIN-002: StrategyModalWindow bypass guard runs before any subclass cheap state** (`game/ui/screens/strategy_modal_window.py:118-131`)
Base class has no state to build; bypass fires during `super().__init__()`. Subclasses correctly build state before calling super. Justified by architecture, but pattern divergence from the canonical PoC shape.

**MIN-003: StrategyModalWindow does not invoke builder in bypass branch** (`game/ui/screens/strategy_modal_window.py:118-131`)
Base class correctly delegates builder invocation to subclasses via `_window_init_bypassed` flag. Justified — base class cannot know subclass builder type.

**MIN-004: Inconsistent use of _init_state/_init_widget_refs helper methods** (7 files, see construction report)
Two classes use named helpers; five set state inline. Stylistic inconsistency — both approaches satisfy the two-stage pattern. Not a bug.

**MIN-005: TransferDialog performs a side-effecting query in Stage 1** (`game/ui/screens/transfer_dialog.py:137-140`)
`discover_pod_designs(scene)` runs before the bypass guard. Docstring already acknowledges this as a "side-effecting query." Low risk — the query is an in-memory registry walk — but diverges from the "pure construction only" intent of Stage 1.

**MIN-006: FleetReportWindow mixes layout constants with delegate state in Stage 1** (`game/ui/screens/fleet_report_window.py:168-179`)
Layout constants (`sidebar_width = 300`, `detail_width = 750`, etc.) are set in the same block as delegate construction and widget-ref placeholders. These belong in the builder (Stage 3). Not breaking — pure integers — but violates separation of concerns.

**MIN-007: StrategyModalWindow subclass bypass check uses instance attr vs class attr** (4 files)
Subclasses check `getattr(self, '_window_init_bypassed', False)` while direct-UIWindow screens check `getattr(type(self), 'bypass_init', False)`. Two correct patterns for two different inheritance hierarchies. Not a divergence, but worth documenting.

### PROJ-325 PoC Quality

**MIN-008: PROJ-328 design.md is an unfilled template** (`Projects/active_projects/PROJ-328/design.md`)
Every section contains unreplaced `[placeholder]` brackets: Initial Analysis, Architecture, Key Patterns to Reuse, Dependencies & Risks, Opportunities Discovered. The header states "THIS IS A REFERENCE DOCUMENT — Do not modify during implementation" but there is nothing to reference. The manifest lists it as a deliverable; it was shipped as a stub.

### PROJ-326 Linter Quality

**MIN-009: Blanket glob in allowlist could mask future bad files** (`Tools/lint_test_files_allowlist.txt`)
`tests/unit/tools/**/*.py` blanket-allows the entire directory. Two files in it already import `game.*` and would pass without the allowlist. A future game-logic-reimplementing test placed in this directory would be silently allowed. Consider narrowing or adding a comment flagging the risk.

**MIN-010: Pre-commit hook uses bare `python` command** (`.git/hooks/pre-commit`)
On Python 3-only installs where the binary is `python3`, the hook would silently fail. The docs note says "Python alone is sufficient" but doesn't address this edge case.

**MIN-011: PowerShell snippet in pre_commit_hooks.md incomplete** (`docs/guides/pre_commit_hooks.md`)
The PowerShell installation snippet lacks executable bit setting for Git Bash compatibility.

### PROJ-328 Phase B/C MVVM Quality

**MIN-012: NewGameSetupController has leaky screen-widget access** (`game/ui/screens/new_game_setup_controller.py`)
Controller accesses screen widgets via `self._screen.save_name_input.get_text()`, `self._screen.error_label.set_text(...)`, `self._screen.empire_name_inputs[i].get_text()`, `self._screen.kill()`, etc. Docstring acknowledges the leak. Violates strict MVVM but is a pragmatic compromise given the legacy widget-coupling architecture.

**MIN-013: TransferDialog LOC claim inaccurate (24% error)** (`game/ui/screens/transfer_dialog.py`)
Claimed: 380 LOC. Actual: **471 LOC** (under 500 ceiling, so no rule violation). Claim is off by 91 lines. Total MVVM surface across 4 files is 1448 LOC — the split added significant surface area vs the original single-file design.

### Test Outcome Integrity

**MIN-014: FleetReportWindow test count claim inaccurate** (`tests/unit/ui/screens/test_fleet_report_window.py`)
Claimed: 28 → 19. Actual: 30 → 18. Twelve tests removed without enumeration. See MAJ-001.

**MIN-015: NewGameSetup extended helper LOC claim off** (`tests/unit/ui/screens/test_new_game_setup_extended.py`)
Claimed: helper 34 → 25 LOC. Actual: 34 → 31 LOC. Minor counting variance.

### Cross-Reference & Tech Debt

**MIN-016: Continuation plan reference broken** (`Projects/active_projects/PROJ-325/design.md:12`, `PROJ-326/design.md:12`)
Both design docs reference `AgentCoordination/Scratchpad/plans/proj_321_322_323_continuation_plan.md` which does not exist.

**MIN-017: DesignWorkshopScreen deferral undocumented**
Not a UIWindow subclass (correct exclusion from two-stage pattern), but no project in this wave explicitly documented the decision to skip it.

**MIN-018: 15 un-refactored UIWindow subclasses silently absent from PROJ-328 plan**
13 `StrategyModalWindow` subclasses + 2 direct `UIWindow` subclasses remain on the legacy `__new__` bypass pattern. PROJ-328 plan "Out" scope only calls out non-UIWindow classes (`BuildQueueScreen`, `WorkshopScreen`). The 15 remaining UIWindow-inheriting classes are not listed as deferred, not in scope, and not mentioned anywhere. Future agents won't know whether they were overlooked or intentionally left unchanged.

---

## Verified Claims (Positive Confirmations)

The following claims from project materials were skeptically verified and confirmed:

1. **Two-stage construction pattern** applied consistently across all 7 audited production classes. No pattern breaks.
2. **All 4 PoC findings** verified against every class: `self.rect` not assigned in bypass, bypass branch invokes builder when supplied, delegate refs mirrored, renderer reach-throughs reproduced in mock builders.
3. **PROJ-325 AC-1 through AC-5** all verified. `_make_race_setup_screen` helper shrank from ~118 to ~58 lines. 63/63 tests pass.
4. **PROJ-326 linter** uses AST parsing (not regex), handles edge cases correctly (lookalike module names, parse failures), exits 0 against current tree.
5. **SystemTreePanel smoke test** provides 4 meaningful behavioral tests — not bypass-init trivia.
6. **Facade contract guard** makes 9 meaningful behavioral assertions — not trivial `is not None` checks.
7. **Pre-commit hook** installed and functional.
8. **TransferDialog characterization tests** (41) are non-trivial — command emission tests have 7 assertions each verifying fleet_id, planet_id, cargo_type, direction, amount, species_id, target_fleet_id.
9. **3 surprise couplings** (in-place mutation, no-op semantics, always-kill) all preserved in refactored code and pinned by characterization tests.
10. **NewGameSetupViewModel** has zero pygame imports. Clean.
11. **Test suite integrity**: 2309 pass, 1 skip (expected parametric exhaust), no xfails, no weakened assertions.
12. **`docs/02_PATTERNS.md`** sections 32 and 33 cross-reference each other accurately.
13. **`docs/known-issues.md`** UIWindow blocker correctly marked Resolved with cross-PROJ attribution.
14. **All commits** on the correct `feat/03c-phase-aware-execution` branch with clean linear history.

---

## Remediation Needed

### Short term (before next wave)
1. **Audit 12 removed FleetReport tests** — confirm they were all mock-plumbing redundancies, document enumeration in checklist Notes. (MAJ-001)
2. **Fix transfer_dialog LOC claim** in PROJ-328 phase_3_checklist.md Notes from 380 → 471. (MIN-013)
3. **Fix FleetReport test count claim** in PROJ-328 phase_1_checklist.md Task A.4 Notes from 28→19 to 30→18. (MAJ-001, MIN-014)
4. **Fill PROJ-328 design.md** — replace placeholders with actual design decisions, architecture notes, patterns reused, risks encountered. (MIN-008)

### Medium term (next PROJ)
5. **Track the 15 un-refactored UIWindow subclasses** in `docs/known-issues.md` or a new PROJ proposal. They remain on the legacy `__new__` bypass pattern. At minimum, document which are intentionally deferred and which need attention. (MIN-018)
6. **Document DesignWorkshopScreen deferral** — one sentence in known-issues.md or a PROJ-324/328 out-of-scope note. (MIN-017)
7. **Fix broken continuation_plan.md reference** in PROJ-325 and PROJ-326 design.md. (MIN-016)

### Low priority (cleanup)
8. Unify bypass guard across `_init_state`/`_init_widget_refs` helper conventions. (MIN-001, MIN-004)
9. Consider `BypassableUIWindow` mixin to eliminate guard duplication. (MIN-001)
10. Narrow blanket allowlist glob or add risk comment. (MIN-009)
11. Fix pre-commit hook `python`→`python3` portability. (MIN-010)

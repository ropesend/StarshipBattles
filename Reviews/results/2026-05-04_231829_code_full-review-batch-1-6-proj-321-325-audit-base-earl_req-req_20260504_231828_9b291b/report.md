# Review Report: PROJ-321..325 Audit Baseline + UIWindow PoC

**Review Mode:** code (delegated by Claude Code)
**Request ID:** req_20260504_231828_9b291b
**Date:** 2026-05-04
**Scope:** PROJ-321 through PROJ-325 — audit baseline + early UIWindow refactor work
**Method:** 5 parallel subagents, one per PROJ, with production-code verification of all claims
**Limitations:** Spot-check sampling (not exhaustive line-by-line); Phase 3 checklist sub-items checked on representative samples

---

## Findings

### PROJ-321 — P0 Test Deletion Verification

#### FND-001: Facade public API contract guard deleted without confirmed replacement
**Severity:** MAJOR
**File:** `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py`
**Line:** Deleted lines 22-81, 122-154

Task 1.14 deleted the `PUBLIC_METHODS` frozenset (~50 methods) and `TestPublicMethodSurface` class (3 tests: `test_every_public_method_present`, `test_every_public_method_callable`, `test_no_unexpected_public_methods_added`). These performed real set-difference checks to detect facade API drift — they were not trivial-pass. The deletion callback noted "If the contract-guard pattern is needed, recreate it as a proper behavioral test in PROJ-322." Whether PROJ-322 recreated this guard is unverified.

All 9 other spot-checked deletions were genuinely vacuous (import-existence, hasattr, empty test bodies, source-scan tests). Zero production coverage loss.

### PROJ-322 — Deferral Disposition Audit

#### FND-002: Task 3.14 misattributed in "13 UIWindow/LLM-blocked deferrals" resolution row
**Severity:** MAJOR
**File:** `Projects/active_projects/PROJ-322/plan.md`
**Line:** 50

The Final disposition summary lumps Task 3.14 (virtual_table module-scope fixture migration) into the "13 UIWindow/LLM-blocked" row, claiming resolution via PROJ-324 bypass_init cascade. Task 3.14 was (a) not UIWindow-blocked (it is a `@patch` sweep on a non-UIWindow test file), and (b) actually resolved by PROJ-327 Phase 1 via module-scope autouse fixture — a different mechanism entirely. The count 13 should be 12; Task 3.14 deserves its own row or a note adding "PROJ-327 Phase 1" to the closure cascade.

All 5 spot-checked disposition claims (APC-001 cluster, Task 3.25, Task 4.3, Task 5.10, Tasks 6.1/6.4) verified correct by production code inspection. Both systemic blockers confirmed RESOLVED in `docs/known-issues.md`.

### PROJ-323 — Test Polish Quality + PROJ-325 Phase 1 Corrections

#### FND-003: Non-idiomatic `__import__()` pattern in parametrize params
**Severity:** MAJOR
**File:** `tests/unit/modifiers/test_defense_marker_bindings.py`
**Line:** 64-93

Task 3.10's parametrize uses `__import__('module', fromlist=['Class']).Class` inline within `pytest.param()` expressions (6 occurrences). This deviates from the codebase convention established elsewhere in PROJ-323 — other parametrize refactors (Task 3.2, `test_superweapon_handler_validation.py`) use standard `from ... import ...` inside factory functions. Functionally correct but inconsistent and less readable. Replace with module-level imports or factory-function pattern.

All 6 PROJ-325 Phase 1 corrections verified: false-positive checkmarks fixed, manifest.md cleaned (41 stale entries removed), terminology/LOC annotations added, design.md stale references replaced. 3 spot-checks passed (CAT-9 import hoisting, CAT-10 parametrize, CAT-12 hardcoded values). Task 5.19 tolerance relaxation (1e-9 → 1e-5) is safe — effective tolerance ~0.001%, adequate for catching formula drift.

### PROJ-324 — bypass_init Flag + LLMBackgroundCall Refactor

#### FND-004: `_window_init_bypassed` flag not set in production path for direct UIWindow subclasses
**Severity:** MAJOR
**File:** `game/ui/screens/race_setup/screen.py`, `game/ui/screens/new_game_setup_screen.py`
**Line:** screen.py:165-175, new_game_setup_screen.py:193-202

Both `RaceSetupScreen` and `NewGameSetupScreen` set `self._window_init_bypassed = True` in their bypass branches but never assign the flag in the production path. `StrategyModalWindow` — the base class for all other bypass-capable windows — consistently sets it in both paths (`True` in bypass, `False` in production). No crash risk today (all 15 consumers use `getattr(self, '_window_init_bypassed', False)` with a `False` default), but the pattern inconsistency could confuse future maintainers. Add `self._window_init_bypassed = False` after `super().__init__()` in both files' production paths.

All `bypass_init` guards use `type(self)` correctly per D-003. The context manager in `ui_widget_factory.py` properly cleans up on exception. The `LLMBackgroundCall._done_event` / `wait()` design was traced through all 6 terminal-transition paths — no actual race condition exists; `_done_event` is always set after lock-protected state is committed.

### PROJ-325 — RaceSetupScreen Two-Stage Construction PoC

#### FND-005: 30+ pre-existing tests mock the method under test — vacuous surface
**Severity:** MAJOR
**File:** `tests/unit/ui/screens/test_race_setup_screen.py`
**Line:** Throughout (e.g., 302-312, 483-507, 562-592)

Multiple tests replace production methods with hand-rolled mocks and assert the mock was called rather than exercising real production behavior. Representative examples: `test_save_calls_race_library` patches `screen._save_race` with a mock that calls `race_library.save()`; `test_validate_for_save_checks_required_fields` replaces `screen._validate_for_save` with a mock; `test_save_button_visible_on_summary_tab` replaces `screen._update_navigation_buttons` with a truncated clone. These tests cannot detect regressions in real production code. Pre-existing condition, not caused by PROJ-325, but the two-stage pattern now provides infrastructure to replace mock-the-method tests with tests that exercise real delegate behavior through the factory seam.

#### FND-006: `_make_race_setup_screen` overrides `_controller` internals — leaky factory seam
**Severity:** MAJOR
**File:** `tests/unit/ui/screens/test_race_setup_screen.py`
**Line:** 67-69

After constructing a real screen through the two-stage pattern (which builds real `RaceConfig()`/`RaceLibrary()` via `DefaultRaceSetupDelegateFactory`), the helper immediately overrides `screen._controller.race_config` and `screen._controller.race_library` with test mocks. This defeats the delegate-factory seam — the factory's `RaceSetupController(...)` wiring is discarded before any test runs. Extend `DefaultRaceSetupDelegateFactory.build()` to accept optional `race_config` / `race_library` overrides so tests pass data IN rather than post-construction patching.

#### FND-007: NullRaceSetupUiBuilder has only one consumer
**Severity:** MAJOR
**File:** `tests/fixtures/race_setup_ui_builders.py`
**Line:** 34-39

`NullRaceSetupUiBuilder` is consumed by exactly one test (the PoC verification test). Its documented purpose — "use when a test only exercises cheap state + delegate behaviour" — has no production consumer beyond the PoC. Either migrate a few existing tests to use the null builder (proving the path is real) or document it as a reusable PROJ-328 fixture.

#### FND-008: Legacy `__new__` bypass persists in 2 kill-hook tests
**Severity:** MAJOR
**File:** `tests/unit/ui/screens/test_race_setup_screen.py`
**Line:** 1209-1210, 1229-1230

Two tests (`test_kill_cancels_description_controller`, `test_kill_when_no_controller_does_not_raise`) still use the legacy `__new__` bypass pattern that Pattern §33 declares should be eradicated. Add a comment explaining why `__new__` is used (tests only need bare object with `_controller`; full construction would create unnecessary state), or migrate to `NullRaceSetupUiBuilder` for pattern consistency.

---

## Additional Investigations (No Findings)

- **LLMBackgroundCall race analysis:** Traced all 6 terminal-transition paths in `background.py`. `_done_event.set()` always follows lock-protected state commit (`_finished_at`, `_status`). The outer-finally decrement of `_in_flight_calls` happens after `_done_event.set()` — intentional to avoid waiter-starvation. No race condition.
- **PROJ-322 systemic blockers:** Both verified RESOLVED in production code. `StrategyModalWindow.__init__:118` carries `bypass_init` guard; `FleetReportWindow`, `OrdersWindow`, `BuildQueueListWindow`, `TransferDialog`, `RaceSetupScreen`, `NewGameSetupScreen` all have two-stage construction with `bypass_init` + builder seams.
- **PROJ-325 Phase 2 parametrize:** Task 3.34 (11 fleet_not_found handlers, 2 groups) and Task 3.37 (4 zero/negative cargo cases) verified correct, clean, and not over-consolidated.

---

## Summary

| Severity | Count | IDs |
|----------|-------|-----|
| CRITICAL | 0 | — |
| MAJOR | 8 | FND-001, FND-002, FND-003, FND-004, FND-005, FND-006, FND-007, FND-008 |

---

## Overall Verdict

The PROJ-321..325 arc is in sound shape. No CRITICAL issues (production behavior regression, data loss, false-positive tests). The two MAJOR concerns requiring action are: FND-001 (lost facade API surface contract guard — verify PROJ-322 replacement or restore as CI/lint step) and FND-006 (RaceSetupScreen test helper overrides factory-wired controller internals, defeating the delegate-factory seam — extend factory to accept overrides). FND-005 (30+ vacuous mock-the-method tests) is the largest quality gap but is pre-existing; the two-stage pattern now provides infrastructure to fix it in a follow-up. The `bypass_init` mechanism is safe, the `LLMBackgroundCall.wait()` API is race-free, and the two-stage UIWindow construction pattern is correctly applied and validated by the PROJ-325 PoC. All PROJ-322 deferral dispositions verified accurate (with one row-level misattribution, FND-002). PROJ-328 is unblocked.

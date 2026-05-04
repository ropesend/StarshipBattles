# PROJ-324: Test infra unblock — UIWindow + LLMBackgroundCall + 14 deferrals

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-324` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-324 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. UIWindow `bypass_init` flag (production-side) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. LLMBackgroundCall completion Event (production-side) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Migrate 14 unblocked PROJ-322 deferrals (test-side) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Documentation pass (`make_ui_widget` → `docs/02_PATTERNS.md`, mark blockers resolved) | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** Planning complete — ready for Phase 1
**Last Action:** Project created from continuation review of PROJ-321/322/323
**Next Action:** Begin Phase 1 — add `bypass_init` flag to `StrategyModalWindow.__init__` first (most subclasses route through it), then to direct-UIWindow subclasses
**Blockers:** None

## Overview

PROJ-322 left 14 of its 25 formal deferrals gated by a single root cause: the shared `make_ui_widget` factory (introduced in PROJ-322 Phase 5) cannot construct `pygame_gui.elements.UIWindow` subclasses because Python's MRO resolves at class-definition time, so element-class patches don't intercept the `super().__init__()` chain. This project adds a 1-line `bypass_init=True` opt-in flag to UIWindow subclasses, refactors `LLMBackgroundCall` polling into a `threading.Event`-based wait (+4 lines of production code), and migrates the 14 unblocked test files. Net result: 14 PROJ-322 deferrals close, `make_ui_widget` becomes a documented canonical pattern, and `tests/unit/services/llm/test_background.py` becomes deterministic.

## Goals

- **Phase 1:** Add `bypass_init=True` early-exit guard to `__init__` of `StrategyModalWindow` plus the direct UIWindow subclasses (`RaceSetupScreen`, `NewGameSetupScreen`, `BuildQueueListWindow`). The guard is a no-op when the flag is unset; production behavior is unchanged.
- **Phase 2:** Add `_done_event: threading.Event` to `LLMBackgroundCall.__init__`, set it in `_run()` after each terminal-state transition, expose `wait(timeout=None)` as a public method.
- **Phase 3:** Migrate the 14 test files PROJ-322 deferred — 7 APC-001 cluster files (UIWindow subclass tests) + 5 Phase 3 boundary-patching tasks + Task 4.3 (LLM polling) + Task 5.10 / 5.10a workshop-screen integration tests if not already in place.
- **Phase 4:** Promote `tests/fixtures/ui_widget_factory.py` to `docs/02_PATTERNS.md` as a canonical pattern, mark the UIWindow + LLM blockers resolved in `docs/known-issues.md`, and update `Projects/active_projects/PROJ-322/plan.md` Continuation Guide with the resolution.

## Scope

**In:**
- Production `__init__` guards on 4 UIWindow subclass files + `StrategyModalWindow`
- Production `LLMBackgroundCall` Event + `wait()` method
- Test migration of the 14 deferred items listed in Phase 3
- Documentation updates (`docs/02_PATTERNS.md`, `docs/known-issues.md`, PROJ-322 plan continuation guide)

**Out:**
- **Task 3.14** (`virtual_table` 700-LOC `@patch` sweep) — explicitly rolled to PROJ-327 (test-runtime reduction project) because it is high-regression-risk and not gated by UIWindow.
- **Task 3.25** (`strategy_screen` 50-test refactor) — explicitly rolled to PROJ-327 because it is a multi-day production-side change distinct from the systemic blocker.
- **DUP-001 / HLP-001** (PROJ-322 Tasks 6.1 + 6.4) — accepted disposition per OpenCode 322-review; not touched here. Re-evaluation queued to PROJ-327 Phase 3.
- **PROJ-323 leftovers** (Tasks 3.34 / 3.37, doc corrections, Task 5.19 precision mismatch) — addressed by PROJ-325.
- **Linter rule for zero-game-import test files** — addressed by PROJ-326.
- **Mutable-mock fixture rescope candidates** (PROJ-322 Tasks 2.6 / 2.11 / 2.15 / 2.19 / 3.15) — rolled to PROJ-327 Phase 2 because runtime is a measured problem.

## Key Files

### Production files modified

| Component | File | Why |
|-----------|------|-----|
| `StrategyModalWindow` | [`game/ui/screens/strategy_modal_window.py`](game/ui/screens/strategy_modal_window.py#L27) | Base class for `FleetReportWindow`, `OrdersWindow`, `TransferDialog`, `BuildQueueListWindow`. One guard here covers 4 downstream classes. |
| `RaceSetupScreen` | [`game/ui/screens/race_setup/screen.py`](game/ui/screens/race_setup/screen.py#L74) | Direct UIWindow subclass; 6 → 10+ collaborators in `__init__`. |
| `NewGameSetupScreen` | [`game/ui/screens/new_game_setup_screen.py`](game/ui/screens/new_game_setup_screen.py#L87) | Direct UIWindow subclass. |
| `BuildQueueListWindow` | [`game/ui/screens/build_queue_list_window.py`](game/ui/screens/build_queue_list_window.py#L26) | Direct subclass of `StrategyModalWindow` — gets the guard transitively, but verify the chain works in tests before declaring transitive coverage. |
| `LLMBackgroundCall` | [`game/services/llm/background.py`](game/services/llm/background.py#L60) | Add `_done_event`, `wait(timeout)` method, set event in `_run()` terminal states. |

### Test files migrated (Phase 3)

See [`manifest.md`](manifest.md) for the full per-task list. Headline targets:

| File | PROJ-322 Task | Migration |
|------|---------------|-----------|
| `tests/unit/ui/screens/test_fleet_report_window.py` | 5.6 | APC-001 → `make_ui_widget` w/ `bypass_init` |
| `tests/unit/ui/screens/test_fleet_report_window_multi_select.py` | 5.7, 3.20 | APC-001 + APC-003 boundary |
| `tests/unit/ui/screens/test_workshop_screen.py` (or integration alternative) | 5.10, 5.10a | APC-001; integration precedent exists at `tests/integration/ui/build_queue_screen/` |
| `tests/unit/ui/screens/test_race_setup_screen.py` | 5.11, 2.17, 3.21 | RaceSetupScreen — see Decision D-002 below; may roll to PROJ-325 |
| `tests/unit/ui/screens/test_new_game_setup_extended.py` | 5.12 | APC-001 |
| `tests/unit/ui/screens/test_sub_window_hotkeys.py` | 5.16 | All 4 target classes inherit StrategyModalWindow |
| `tests/unit/ui/screens/test_build_queue_list_window.py` | 5.29, 3.19 | APC-001 + APC-003 boundary |
| `tests/unit/strategy/test_strategy_modal_window.py` | 3.24 | UIWindow root-cause file |
| `tests/unit/services/llm/test_background.py` | 4.3 | Polling loops → `call.wait(timeout=2.0)` |

## Cross-Project Coordination

**Single source of truth for parallelism + file conflicts:** [`AgentCoordination/Scratchpad/plans/proj_324_325_326_327_parallelism_map.md`](AgentCoordination/Scratchpad/plans/proj_324_325_326_327_parallelism_map.md)

**Branch:** Continue on `feat/03c-phase-aware-execution` (where PROJ-321/322/323 landed) unless the user directs otherwise.

**Quick summary (full detail in the parallelism map):**

- **Parallel-safe with PROJ-326 entirely** (disjoint file domains).
- **Parallel-safe with PROJ-325 Phases 1-2** (disjoint files).
- **Blocks PROJ-325 Phase 3.** PROJ-325 Phase 3 (RaceSetupScreen testable construction) cannot start until PROJ-324 Phase 3 Task 3.4 reports its GO/NO-GO outcome.
- **Blocks PROJ-327 entirely** (per user direction: "they can be deferred but when 326 is done I want to work on them" — PROJ-327 starts after PROJ-326 completes).
- Within PROJ-324: Phase 1 + Phase 2 are file-disjoint and may parallelize if multiple agents are running.

## Related Documents

- [design.md](design.md) — architecture analysis, MRO root-cause explanation, factory pattern reuse
- [decisions.md](decisions.md) — full decisions log with rationale and parallelism map
- [manifest.md](manifest.md) — per-task file manifest used for `/proj-parallel` conflict detection
- [`docs/known-issues.md`](docs/known-issues.md) — systemic blocker context (READ FIRST)
- [`Reviews/results/2026-05-04_015938_consistency_proj-322-p1-brittle-bloated-test-remediation-compl_req-req_20260504_015935_7d4449/report.md`](Reviews/results/2026-05-04_015938_consistency_proj-322-p1-brittle-bloated-test-remediation-compl_req-req_20260504_015935_7d4449/report.md) — OpenCode source review that recommended Option (a)
- [`AgentCoordination/Scratchpad/plans/proj_321_322_323_continuation_plan.md`](AgentCoordination/Scratchpad/plans/proj_321_322_323_continuation_plan.md) — original continuation plan that scoped these 4 projects

## Verification

- [ ] All phase checklists complete
- [ ] All tests passing (`python Tools/test_sharded/test_sharded.py`)
- [ ] `tests/fixtures/ui_widget_factory.py` documented in `docs/02_PATTERNS.md`
- [ ] `docs/known-issues.md` UIWindow + LLM blockers marked resolved
- [ ] PROJ-322 Continuation Guide updated to reflect 14 closed deferrals
- [ ] User verified

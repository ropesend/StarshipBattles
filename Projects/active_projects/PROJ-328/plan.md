# PROJ-328: UIWindow MVVM refactor — apply two-stage pattern to 6 subclasses (PROJ-325 PoC follow-on)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-328` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-328 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| A. StrategyModalWindow shell + low/medium modals (BuildQueueListWindow, OrdersWindow, FleetReportWindow) | Complete (2026-05-03) | [phase_1_checklist.md](phase_1_checklist.md) |
| B. NewGameSetupScreen MVVM split (full ViewModel + Controller + UI builder) | Not Started — Phase A complete; Phase B + Phase C unblocked | [phase_2_checklist.md](phase_2_checklist.md) |
| C. TransferDialog deep split (ViewModel + Controller + Renderer; tests around pending math + IssueTransferCommand emission first) | Not Started — Phase A complete; may run in parallel with Phase B | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-03
**Active Phase:** Phase A complete; Phase B + Phase C unblocked.
**Last Action:** Phase A completed across 7 commits on `feat/03c-phase-aware-execution` (fd388946d, 7859d652c, 00874c571, 495fa0f39, dbc252c23, 2252a6ef3 + this plan/annotation pass). All 4 PoC findings from PROJ-325 Phase 3 applied cleanly. PROJ-322 deferral annotations updated for Tasks 5.6, 5.7, 5.16, 5.29 + 3.19, 3.20, 3.24, 3.26.
**Next Action:** Phase B (NewGameSetupScreen MVVM split — full ViewModel + Controller + UI builder) or Phase C (TransferDialog deep split). Both unblocked; file-disjoint with each other so they may run in parallel if a second agent is available.
**Blockers:** None.

## Overview

Apply the two-stage UIWindow construction pattern (validated by PROJ-325 Phase 3 PoC on RaceSetupScreen) to the other 6 UIWindow subclasses that PROJ-322 deferred and PROJ-324 Phase 3 NO-GO'd. Per Codex–Claude consensus, MVVM depth varies per class: full MVVM for the heavyweight modals (NewGameSetup, TransferDialog), light row+renderer for the small modals (Orders, BuildQueueList), layout-builder extraction for the already-decomposed cases (FleetReport).

`pygame_gui.elements.UIWindow.__init__` stays bypassed via the existing `bypass_init` flag (it's MRO-bound and heavy regardless of any abstraction). The refactor is about making cheap state + delegates run BEFORE the bypass point, and putting widget construction behind a per-class UI builder with paired `Null{Foo}UiBuilder` / `Mock{Foo}UiBuilder` for tests.

## Goals

- **Phase A:** Update `StrategyModalWindow` base class so its bypass path leaves a minimal usable shell (`_window_manager`, `ui_manager`, `rect`, `_window_init_bypassed` set). Then refactor `BuildQueueListWindow`, `OrdersWindow`, `FleetReportWindow` per the per-class application table in the consensus plan. Migrate their test files (PROJ-322 Tasks 5.6/5.7/5.16/5.29 + 3.19/3.20/3.24/3.26) to direct construction.
- **Phase B:** Real MVVM split for `NewGameSetupScreen` — add `NewGameSetupViewModel` (player count, galaxy type, system count, player races, modal state), `NewGameSetupController` (save validation, config building, race-modal callbacks, start/cancel), and a UI builder. Migrate PROJ-322 Tasks 5.12 + 3.21 (NewGame-related boundary work).
- **Phase C:** Deep split for `TransferDialog` — focused tests around pending-transfer math + `IssueTransferCommand` emission first, then `TransferViewModel` + controller + `TransferGridRenderer`. Migrate any PROJ-322 boundary tasks that target it.

## Scope

**In:**
- `StrategyModalWindow` base-class bypass shell update (Phase A entry)
- 6 production class refactors (BuildQueueListWindow, OrdersWindow, FleetReportWindow, NewGameSetupScreen, TransferDialog) — full per-class detail in consensus plan
- Per-class UI builders + Null/Mock builder pairs in `tests/fixtures/`
- Test-file migrations for the corresponding PROJ-322 deferred test files
- Doc updates as classes land — `docs/02_PATTERNS.md` "Two-stage UIWindow Construction" pattern (only after PROJ-325 PoC documents the canonical version)

**Out:**
- `RaceSetupScreen` refactor — owned by PROJ-325 Phase 3 (the PoC)
- `BuildQueueScreen` — already uses PanelFactory/Renderer/Controller per consensus plan
- `WorkshopScreen` — separate "all UI consistency" project later, only if user requests broader cleanup
- `make_ui_widget` factory + `bypass_init` flag — already landed by PROJ-324 Phases 1-2 (foundation)
- `LLMBackgroundCall` — already landed by PROJ-324 Phase 2
- Test runtime reduction (virtual_table @patch sweep, mutable-mock fixtures, strategy_screen) — owned by PROJ-327
- Linter for zero-game-import test files — owned by PROJ-326
- PROJ-323 cleanups — owned by PROJ-325 Phases 1-2 (already done)

## Key Files

### Phase A (StrategyModalWindow shell + 3 light/medium modals)

| File | Type | Change |
|------|------|--------|
| `game/ui/screens/strategy_modal_window.py` | Production | Update bypass branch to leave `_window_manager`, `ui_manager`, `rect`, `_window_init_bypassed` set before returning. |
| `game/ui/screens/build_queue_list_window.py` | Production | Two-stage `__init__`. Light pattern (row collector/formatter + renderer). |
| `game/ui/screens/orders_window.py` | Production | Two-stage `__init__`. Order-row description model + `OrdersListRenderer`. |
| `game/ui/screens/fleet_report_window.py` | Production | Two-stage `__init__`. `FleetReportLayoutBuilder` extraction. Existing `FleetListViewModel`/`FleetDataSource`/`VirtualTable`/sidebar untouched. |
| `tests/fixtures/build_queue_list_ui_builder.py` (NEW) | Test infra | `NullBuildQueueListUiBuilder` + `MockBuildQueueListUiBuilder`. |
| `tests/fixtures/orders_ui_builder.py` (NEW) | Test infra | `NullOrdersUiBuilder` + `MockOrdersUiBuilder`. |
| `tests/fixtures/fleet_report_ui_builder.py` (NEW) | Test infra | `NullFleetReportUiBuilder` + `MockFleetReportUiBuilder`. |
| `tests/unit/ui/screens/test_build_queue_list_window.py` | Test | Migrate to two-stage construction. PROJ-322 Tasks 5.29 + 3.19. |
| `tests/unit/ui/screens/test_orders_window.py` (or `test_sub_window_hotkeys.py` portion) | Test | Migrate. PROJ-322 Task 5.16 (Orders portion). |
| `tests/unit/ui/screens/test_fleet_report_window.py` | Test | Migrate. PROJ-322 Task 5.6. |
| `tests/unit/ui/screens/test_fleet_report_window_multi_select.py` | Test | Migrate. PROJ-322 Tasks 5.7 + 3.20. |
| `tests/unit/strategy/test_strategy_modal_window.py` | Test | Migrate. PROJ-322 Task 3.24. |

### Phase B (NewGameSetupScreen MVVM split)

| File | Type | Change |
|------|------|--------|
| `game/ui/screens/new_game_setup_screen.py` | Production | Two-stage `__init__`. Refactor body. |
| `game/ui/screens/new_game_setup_view_model.py` (NEW) | Production | `NewGameSetupViewModel`. |
| `game/ui/screens/new_game_setup_controller.py` (NEW) | Production | `NewGameSetupController`. |
| `game/ui/screens/new_game_setup_ui_builder.py` (NEW) | Production | `NewGameSetupUiBuilder`. |
| `tests/fixtures/new_game_setup_ui_builder.py` (NEW) | Test infra | Null + Mock variants. |
| `tests/unit/ui/screens/test_new_game_setup_extended.py` | Test | Migrate. PROJ-322 Tasks 5.12 + 3.21 (if 3.21 actually targets NewGame). |
| New tests for `NewGameSetupViewModel` + `NewGameSetupController` | Test | Add coverage for the new MVVM pieces. |

### Phase C (TransferDialog deep split)

| File | Type | Change |
|------|------|--------|
| `game/ui/screens/transfer_dialog.py` | Production | Two-stage `__init__`. Refactor body to extract VM + controller + renderer. |
| `game/ui/screens/transfer_view_model.py` (NEW) | Production | `TransferViewModel` (selection state, pending-transfer rows). |
| `game/ui/screens/transfer_controller.py` (NEW) | Production | `TransferController` (facade queries, `IssueTransferCommand` emission). |
| `game/ui/screens/transfer_grid_renderer.py` (NEW) | Production | `TransferGridRenderer` (grid + dropdown widgets). |
| `tests/fixtures/transfer_ui_builder.py` (NEW) | Test infra | Null + Mock variants. |
| `tests/unit/ui/screens/test_transfer_dialog.py` (or wherever TransferDialog tests live) | Test | Migrate. Verify which PROJ-322 task IDs this owns. |
| New tests for pending math + command emission | Test | **Land BEFORE the production refactor** — see consensus plan. |

## Cross-Project Coordination

**Branch:** `feat/03c-phase-aware-execution` (per user direction).

**Sequencing:**
- **Phase A BLOCKS on PROJ-325 Phase 3** (the canonical PoC pattern lives in `game/ui/screens/race_setup/` after the PoC; this project copies that pattern). Do not start Phase A until PROJ-325 reports the PoC merged + tests passing.
- **Within Phase A**, the 3 modal refactors (BuildQueueList, Orders, FleetReport) are file-disjoint and may parallelize across worktree agents. The `StrategyModalWindow` base-class shell update is a prerequisite — do it FIRST as a single small commit, then the 3 subclass refactors can fan out.
- **Phase B BLOCKS on Phase A** (smaller modals validate the pattern at one-step-up complexity before tackling NewGame's full MVVM split).
- **Phase C is its own thing** and can run in parallel with Phase B if a separate agent is available — TransferDialog is file-disjoint from NewGameSetup.

**Effort estimate (per consensus):** 5-8 LLM-paced sessions across all 3 phases. Phase A is the bulk; Phase B is one focused class; Phase C is the highest-risk single class.

## Related Documents

- **Consensus refactor plan** — [`../PROJ-325/findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md`](../PROJ-325/findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md) — REQUIRED reading
- **Discussion outcome** — [`../PROJ-325/findings/consensus_discussion/outcome.md`](../PROJ-325/findings/consensus_discussion/outcome.md)
- **PoC project** — [`Projects/active_projects/PROJ-325/`](../PROJ-325/) — Phase 3 carries the canonical RaceSetupScreen refactor
- **Foundation project** — [`Projects/active_projects/PROJ-324/`](../PROJ-324/) — `bypass_init` flag + `make_ui_widget` factory + `LLMBackgroundCall.wait()` already landed
- **Original deferral source** — [`Projects/active_projects/PROJ-322/`](../PROJ-322/) — see Tasks 5.6/5.7/5.10/5.10a/5.12/5.16/5.29 + 3.19/3.20/3.21/3.24/3.26 for original scope context
- [`docs/02_PATTERNS.md`](../../../docs/02_PATTERNS.md) Pattern #8 — local MVVM precedent
- [`docs/03_CONVENTIONS.md`](../../../docs/03_CONVENTIONS.md) section 2.4 — UI delegate naming
- [`game/ui/screens/battle_setup/screen.py`](../../../game/ui/screens/battle_setup/screen.py) — structural target

## Verification

- [ ] All phase checklists complete
- [ ] All tests passing (`python Tools/test_sharded/test_sharded.py`)
- [ ] All 6 subclass refactors landed; per-class LOC delta measured
- [ ] Test-helper LOC reduction documented per migrated test file
- [ ] PROJ-322 deferral annotations (5.6/5.7/5.16/5.29 + 3.19/3.20/3.24/3.26 for Phase A; 5.12 + 3.21 for Phase B; TransferDialog task IDs for Phase C) updated to RESOLVED
- [ ] `docs/02_PATTERNS.md` "Two-stage UIWindow Construction" pattern populated (after PROJ-324 Phase 4 lands the foundational pattern entry from PROJ-325 PoC)
- [ ] `docs/known-issues.md` UIWindow blocker section marked Resolved
- [ ] User verified

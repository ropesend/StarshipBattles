# PROJ-491: CAT-6 test-side mechanical migrations

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-491` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-491 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Behavior/assertion rewrites (19 tasks) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. UI-window/panel constructor-smoke + bypass_init cleanup (7 tasks) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Task 3.32 ActionExecutionEngine test rewrite (DI seam already exists) | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Task 3.20 second bullet investigation (may shift to PROJ-493) | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Audit remediation (Codex consult 2026-05-23) | Complete | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-05-23
**Active Phase:** All phases complete — pending user verification.
**Last Action:** Phase 5 audit remediation done. Task 5.1 added `test_game_constructs_with_args_positional` (uses production `parse_args()` to match `main()`'s call site). Task 5.2 tightened `test_build_queue_panel_factory` to a 100% `@fast_panel` assertion (renamed to `test_all_factory_uipanels_use_fast_panel_class_id`, dropped the `warnings.warn` soft fallback). Task 5.3 rewrote the `_disable_pygame_gui_kill_side_effect` module + helper docstrings to accurately describe the scoped-wrapper purpose. Targeted pytest passed for all three files (32 / 5 / 18).
**Next Action:** User verification (run the full sharded suite + apply `verified` label per the GitHub Issues workflow).
**Blockers:** None. Task 1.18 (transfer_handler_fleet_to_fleet) was marked BLOCKED with rationale (no minimal GameSession fixture exists); routing to PROJ-493 is documented in the test docstring and phase checklist.
**Context:** This project carries the test-side mechanical subset of PROJ-479's 27 deferred CAT-6 tasks. Per Codex's analysis, the original PROJ-479 handoff language ("requires DI introduction") was overbroad — most deferred CAT-6 items are pure test-side rewrites (private-call assertions, `inspect.getsource` checks, AST guards, ad hoc `__new__` wiring) and can be done without touching production code. The genuinely production-DI-blocked items live in PROJ-493.

DI-2026-05-23-003 was resolved by Phase 3 (3 test methods in ``test_action_execution_engine.py`` now inject a stub ``ActionTimeResolver`` via the existing constructor parameter).

## Overview
Replace the remaining brittle-mock test patterns deferred by PROJ-479 Phase 3, using existing test seams: the canonical `bypass_init` fixture (`tests/fixtures/ui_widget_factory.py`), behavior-based assertions on public APIs, and the already-injected `action_time_resolver` constructor parameter on `ActionExecutionEngine`. No production code changes.

## Goals
- Migrate 15 brittle-assertion tests to behavior-based or kwargs-extraction assertions (Phase 1)
- Migrate 7 UI-window/panel tests off ad hoc `__new__`/`__init__` patching to the canonical `bypass_init` fixture (Phase 2)
- Rewrite 3 `test_action_execution_engine.py` methods to inject a stub `ActionTimeResolver` via the existing constructor parameter (Phase 3)
- Investigate Task 3.20 second bullet: confirm whether `_per_player_ui_state.load()` is real private-attr access or has a public restore API (Phase 4 — may shift to PROJ-493 if seam gap is real)

## Scope
**In:**
- Phase 3 deferred tasks from PROJ-479 that are pure test-side: 3.1, 3.2, 3.4, 3.5, 3.6, 3.7, 3.9, 3.10, 3.11, 3.12, 3.13, 3.15, 3.16, 3.21, 3.22, 3.23, 3.24, 3.25, 3.29, 3.30, 3.31, 3.32, 3.33
- Phase 3 Task 3.20 first bullet (behavior-based assertions on public turn-advance path)
- Phase 3 Task 3.20 second bullet INVESTIGATION (may move to PROJ-493)

**Out:**
- Production-DI seam introduction (Task 3.14 SuperweaponValidator) — see PROJ-493
- CAT-5 fixture-bloat mutation-isolation deferrals (Phase 2 of PROJ-479) — deferred pending user strategy decision; see decisions.md
- HLP-002 / HLP-004 / HLP-005 helper consolidation — see PROJ-492
- Phase 4 Task 4.2 sleeps — correctly reclassified by PROJ-479, no action needed

## Key Files
| Component | File Path |
|-----------|-----------|
| Canonical bypass_init fixture | `tests/fixtures/ui_widget_factory.py` |
| ActionExecutionEngine (DI seam already exists) | `game/strategy/engine/action_execution_engine.py` (READ ONLY — no production edits) |
| Phase 1 / 2 / 3 test files | See per-phase checklists |

## Related Documents
- [design.md](design.md) - Approach rationale + Codex consult evidence pointers
- [decisions.md](decisions.md) - Reconciliation reasoning + permanently-deferred items
- [manifest.md](manifest.md) - Full file list for parallel-conflict detection
- [findings/source_review.md](findings/source_review.md) - Pointer to PROJ-479 deferred list + Codex consult

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`python Tools/test_sharded/test_sharded.py`)
- [ ] Audit passed
- [ ] User verified

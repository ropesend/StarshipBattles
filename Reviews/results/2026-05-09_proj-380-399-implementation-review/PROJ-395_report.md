# PROJ-395 Implementation Review

**Date:** 2026-05-09  
**Reviewer:** Codex  
**Scope:** Skeptical post-implementation review of PROJ-395 against Protocol 04 principles and the user-requested criteria: plan goals, literal checklist execution, and initial plan gaps.

## Verdict

**FAIL - not audit-ready.**

The important Phase 1 code goals appear implemented and focused tests pass. Phase 2 closed many of the concrete MAJOR follow-ups. However, the project cannot pass audit because the project metadata and checklists are materially inconsistent with the claimed completion state, and the stated Phase 2 goal was not fully met: the project says it closes 14 MAJOR findings, while the implementation explicitly defers 2 of them.

## Validation Result

`python Projects/scripts/validate_audit_ready.py PROJ-395` failed:

- Phase completion/task completion failed because Phase 1 tasks 1.1-1.4 and Phase 2 task 2.1 still have unchecked subtasks.
- Overall result: **FAILED**, 7 errors and 1 warning.
- Warning: `Projects/projects_index.md` still marks PROJ-395 as `Planning`.

Additional phase checks also failed:

- `python Projects/scripts/validate_phase.py PROJ-395 1`: failed, 5 errors.
- `python Projects/scripts/validate_phase.py PROJ-395 2`: failed, 4 errors.

Per Protocol 04, this blocks any claim that PROJ-395 passed audit.

## Tests Run

Focused tests run during this review:

- `pytest tests/integration/ui/test_strategy_turn_error_boundary.py -v` -> **9 passed**
- `pytest tests/unit/strategy/engine/test_command_registry_seeding.py tests/unit/strategy/engine/test_command_registry_thirdparty.py tests/unit/strategy/test_command_handlers.py -v` -> **90 passed**
- `pytest tests/unit/strategy/engine/test_conflict_resolution_modifier_logging.py tests/unit/strategy/turn_engine/test_turn_state_snapshot.py tests/unit/ui/services/image/test_background.py -v` -> **17 passed**
- `pytest tests/unit/strategy/engine/test_base_command_handler.py tests/unit/ui/services/test_tkinter_utils.py -v` -> **44 passed**
- `pytest tests/unit/strategy/test_game_session.py -v` -> **15 passed**
- `pytest tests/unit/strategy/turn_engine/test_turn_engine_snapshot_integration.py -v` -> **4 passed**

Total focused result: **179 passed**.

Not run: `python Tools/test_sharded/test_sharded.py`. The audit-readiness validator already failed, and this review prioritized the touched focused suites plus checklist/implementation verification.

## Plan Goals vs Actual Implementation

### Phase 1 Critical Goals

Phase 1 goals were:

- Replace raw turn-failed `UIMessageWindow` with a `TurnFailedDialog(StrategyModalWindow)`.
- Replace duplicate command registration `ValueError` with structured `ValidationException`.
- Strengthen three command-handler tests with `code` and `context` assertions.

Current implementation supports these goals:

- `TurnFailedDialog` subclasses `StrategyModalWindow` in `game/ui/screens/turn_failed_dialog.py:58`, and `_show_turn_failed_dialog()` threads `window_manager` through at `game/ui/screens/strategy_game_state_manager.py:315-321`.
- `CommandRegistry.register()` raises `ValidationException` with `ErrorCode.DUPLICATE_COMMAND` and structured context at `game/strategy/engine/commands/registry.py:202-215`.
- The command-handler tests assert `code` and context for the three target cases at `tests/unit/strategy/test_command_handlers.py:552-562`, `tests/unit/strategy/test_command_handlers.py:580-590`, and `tests/unit/strategy/test_command_handlers.py:633-642`.

### Phase 2 Major Goals

Phase 2's objective says it closes 14 MAJOR findings from the PROJ-381 review, but the project state says only 12 were closed and MAJ-013/MAJ-014 were deferred (`Projects/active_projects/PROJ-395/plan.md:22`, `Projects/active_projects/PROJ-395/phase_2_checklist.md:8`). That is a valid implementation decision only if the plan is revised to say the phase closes 12 and defers 2. It was not revised consistently.

Confirmed closed items include:

- `TurnFailedError` now exposes `turn_number` and `save_path` properties at `game/core/exceptions.py:262-270`.
- `GameSession.__init__` now logs initializer failure at ERROR with `exc_info=True` before raising `SessionInitializationError` at `game/strategy/engine/game_session.py:165-184`.
- Tkinter broad-catch comments were made substantive at `game/ui/services/tkinter_utils.py:69`, `game/ui/services/tkinter_utils.py:100`, `game/ui/services/tkinter_utils.py:142`, `game/ui/services/tkinter_utils.py:175`, `game/ui/services/tkinter_utils.py:206`, and `game/ui/services/tkinter_utils.py:229`.

But MAJ-014 remains by design: `StrategyGameStateManager` still catches raw `EnginePhaseError` at `game/ui/screens/strategy_game_state_manager.py:149-158`. That matches the commit message's deferral, but it does not match the phase objective of closing all 14 MAJOR findings.

## Literal Checklist Execution

The literal execution trail is not clean:

- `phase_1_checklist.md` status says complete at line 8, but every task checkbox remains unchecked at lines 19-23, 29-32, 38-41, 47-48, and 52-56.
- `phase_2_checklist.md` status says complete at line 8, but the MAJOR-task and final-regression checkboxes remain unchecked at lines 19, 32-38, 44-45, and 49-52.
- The top-level verification checklist remains unchecked at `Projects/active_projects/PROJ-395/plan.md:57-60`.
- `Projects/projects_index.md:11` still reports PROJ-395 as `Planning`.
- `manifest.md` still contains placeholder rows instead of the touched file list (`Projects/active_projects/PROJ-395/manifest.md:8-10`).
- `design.md` is still a template with placeholder sections (`Projects/active_projects/PROJ-395/design.md:7-24`).

These are not cosmetic issues for this workflow. They are the direct reason audit readiness fails.

## Findings

### Blocker: Completion status is false according to the project system

The phase files claim completion while leaving the task checkboxes unchecked. This makes `validate_audit_ready.py` and both phase validators fail. Evidence: Phase 1 status is `Complete` at `Projects/active_projects/PROJ-395/phase_1_checklist.md:8`, while Task 1.1 through the phase completion checklist remain unchecked at `Projects/active_projects/PROJ-395/phase_1_checklist.md:19-56`. Phase 2 has the same issue: status claims completion at `Projects/active_projects/PROJ-395/phase_2_checklist.md:8`, while task/final checklist items remain unchecked at `Projects/active_projects/PROJ-395/phase_2_checklist.md:19-52`.

### Major: Phase 2's stated goal was not met

The Phase 2 objective says the project closes 14 MAJOR findings (`Projects/active_projects/PROJ-395/phase_2_checklist.md:9`), but the project state says MAJ-013 and MAJ-014 were deferred (`Projects/active_projects/PROJ-395/plan.md:22`). The raw `EnginePhaseError` fallback for MAJ-014 still exists at `game/ui/screens/strategy_game_state_manager.py:149-158`. The issue may be a deliberate deferral, but then the plan should not claim the phase closed all 14 MAJOR findings or mark the project audit-ready.

### Major: Required project artifacts were not maintained

`manifest.md` is still the generated placeholder (`Projects/active_projects/PROJ-395/manifest.md:8-10`) even though commits touched production, tests, docs, and project files. `design.md` is still a template (`Projects/active_projects/PROJ-395/design.md:7-24`). This undermines conflict detection, handoff quality, and the user's requested "literal execution of the plan" review.

### Minor: The checklist names a nonexistent focused test path

Task 1.2 says to verify `pytest tests/unit/strategy/engine/test_command_registry.py -v` (`Projects/active_projects/PROJ-395/phase_1_checklist.md:25-32`), but that file does not exist. The actual relevant tests are in `tests/unit/strategy/engine/test_command_registry_seeding.py` and `tests/unit/strategy/engine/test_command_registry_thirdparty.py`, and they pass. The implementation is fine here, but the checklist was not corrected.

### Minor: Error-handling docs still contradict current EventBus architecture

`docs/05_ERROR_HANDLING.md:154` says module-level `set_event_handler()`, `get_event_handler()`, and `log_event()` remain compatibility API. Current `game/core/event_logging.py:27-32` says PROJ-390 retired those shims, and `docs/02_PATTERNS.md:244-247` says constructor injection is the only supported strategy/core event logging pattern. This overlaps MAJ-013's deferred area and should be cleaned up with that follow-up.

## Plan Gaps / Missed Assumptions

- The initial plan framed Phase 2 as "14 MAJOR items" but did not model deferral as a first-class outcome. Once MAJ-013 and MAJ-014 were deferred, the plan needed a revised objective, checklist, and current-state status.
- The plan did not require maintaining `manifest.md` or filling in `design.md`, even though the project system requires those files to stay synchronized.
- The plan did not require a full sharded regression receipt despite Phase 2 checklist Task 2.3 requiring it. The commit message records touched-file focused tests, not `Tools/test_sharded/test_sharded.py`.
- MAJ-005 added an ERROR log, but the existing `GameSession` test still only asserts the typed exception and null-object state (`tests/unit/strategy/test_game_session.py:277-317`). There is no focused caplog assertion proving the logging behavior remains present.

## Residual Risks

- PROJ-395 should return to implementation/closeout bookkeeping before any audit pass: check the completed subtasks honestly, update `projects_index.md`, fill `manifest.md`, and either revise Phase 2 to "12 closed, 2 deferred" or add a follow-up phase/project for MAJ-013 and MAJ-014.
- Focused tests are green, but the canonical full sharded suite was not run during this review.
- The two deferred MAJORs need explicit tracking. MAJ-014 is especially architectural because the UI still tolerates facade bypass by catching domain-engine `EnginePhaseError` directly.

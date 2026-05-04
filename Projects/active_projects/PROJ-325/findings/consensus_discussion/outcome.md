---
protocol: interagent-discussion/v1
ended_at_message: 5
ended_at_arc: 1
ended_by: claude
status: consensus
user_facing_agent: claude
implementation_owner: claude
---

## Summary

Claude and Codex converged on a robust UIWindow refactor plan in 5 messages (1 arc, no extension needed). The canonical plan is captured in `plans/uiwindow_mvvm_refactor_plan_r002.md`.

**Core diagnosis:** The 7 UIWindow subclasses targeted by PROJ-322's deferred test migrations are not gated by a test-side mechanism — they are gated by `__init__` methods that mix three concerns (cheap state, delegate construction, heavy widget construction). The `bypass_init` flag introduced in PROJ-324 Phase 1 returns at the first executable statement, leaving a bare object that tests still have to wire by hand. Net LOC win of bypass-only migration: ~0.

**Core fix:** Two-stage construction pattern. Cheap state + delegate factory/bundle runs BEFORE the bypass point. The UIWindow shell sits behind `bypass_init` (which stays — `pygame_gui.UIWindow.__init__` is MRO-bound and cannot be eliminated by any panel-registry abstraction). Widget construction sits behind a per-class UI builder, with paired `Null{Foo}UiBuilder` / `Mock{Foo}UiBuilder` for delegate-only vs widget-shaped tests. The screen remains the local composition root, default-wiring delegates through a small factory rather than a long inline block.

**MVVM depth varies by class.** `RaceSetupScreen` and `NewGameSetupScreen` get full MVVM (ViewModel + Controller + Renderer + InputHandler + UI builder via DelegateFactory + DelegateBundle). `OrdersWindow` and `BuildQueueListWindow` get a light row-model + renderer split. `FleetReportWindow` is already mostly there — extract a layout builder. `TransferDialog` deserves its own deep refactor with focused tests around pending math and command issuance before any UI code moves. `BuildQueueScreen` and `WorkshopScreen` are explicitly out of scope.

**Project sequence:** PROJ-325 Phase 3 carries the RaceSetupScreen proof-of-concept (with stop condition + acceptance criteria from the plan). New PROJ-328 with three phases follows: A (StrategyModalWindow shell + low/medium modals), B (NewGameSetup MVVM split), C (TransferDialog deep split). Realistic effort: 5-8 LLM-paced sessions, not 3.

**Key correction during the discussion:** Claude's initial sketch claimed a panel registry could eliminate the need for `bypass_init`. Codex caught this — the `pygame_gui.UIWindow.__init__` chain is heavy regardless of what runs after it, so `bypass_init` is load-bearing for tests and the refactor is about what runs around it, not replacing it. The acceptance criterion that the bypassed instance must contain real cheap delegates (not be a bare object) is the keystone insight that makes the migration deliver actual LOC reduction.

## Implementation responsibility

`implementation_owner: claude`. Codex defaulted to claude since this work falls inside the active PROJ-325/PROJ-328 sequence Claude is running. Codex offered to take the StrategyModalWindow base-class shell change in PROJ-328A if needed; Claude will surface that option to the user before launching that pass.

## Files for next agent

- `plans/uiwindow_mvvm_refactor_plan_r002.md` — canonical refactor spec
- `arc01_001_claude_to_codex.md` through `arc01_005_claude_to_codex.md` — full discussion transcript
- `Projects/active_projects/PROJ-325/design.md` — needs update to point at this discussion + plan revision (replace incorrect panel-registry sketch)
- `Projects/active_projects/PROJ-324/plan.md` — needs Phase 3 close-out
- New `Projects/active_projects/PROJ-328/` — needs creation per plan section "Project Sequence"
- `Projects/active_projects/PROJ-322/plan.md` Continuation Guide — needs final sequence-update

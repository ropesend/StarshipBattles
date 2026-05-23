# PROJ-491 Design

## Background

PROJ-479 (P1 test-review remediation) completed Phase 3 with 27 of 34 CAT-6 tasks marked NEEDS_REWORK. The original deferral rationale was a blanket "heavy refactor — requires DI introduction / real-construction migration of UI/engine internals that exceed the CAT-6 cleanup scope" (see `Projects/active_projects/PROJ-479/phase_3_checklist.md` for the boilerplate).

A Codex planning consult (`AgentCoordination/Scratchpad/Consult/20260523T125621Z_plan-PROJ-479-followthrough/response.md`) found this rationale **overbroad**. File-level task descriptions show most deferred items are pure test-side rewrites that don't need production seams:
- Behavior-based assertion swaps (replace private-call assertions with public-API assertions)
- `inspect.getsource` / AST-source guards → behavioral tests or static_guards relocation
- Ad hoc `__new__` + manual attr wiring → existing canonical `bypass_init` fixture
- Module-level monkeypatch → per-test factory functions

## Approach

Three execution phases by mechanical pattern, plus one investigation phase.

### Phase 1 — Behavior/assertion rewrites
Tasks where the current test asserts on a private call (`MagicMock` recording) or source-text/AST property. Convert each to assert on the observable public outcome.

Pattern: `mock.private_method.assert_called()` → `assert public_observable_state == expected`.

### Phase 2 — UI-window/panel bypass_init migrations
Tasks where the current test patches `__init__` with a no-op lambda + manually wires 10-30 attributes. Migrate to `bypass_init` from `tests/fixtures/ui_widget_factory.py:254-328` (already canonical per PROJ-327 / PROJ-458 / PROJ-470 conformance). Note: line 20-28 of `ui_widget_factory.py` is the `make_ui_widget` factory, NOT `bypass_init`.

Evidence: some deferred files already use `bypass_init` adjacent code (`tests/unit/ui/screens/test_orders_window.py:34,51-59`, `tests/unit/ui/screens/test_build_queue_list_window.py:24,38`), confirming the seam is in place. For those files the work is constructor-smoke addition and cleanup of leftover ad hoc patterns rather than fresh migration.

### Phase 3 — Task 3.32 ActionExecutionEngine
Production DI seam **already exists** (PROJ-479 audit finding F2, logged as DI-2026-05-23-003). `ActionExecutionEngine.__init__` accepts `action_time_resolver: Optional[ActionTimeResolver] = None` at `game/strategy/engine/action_execution_engine.py:55-68`, and `_process_fleet_action_tick` prefers the injected resolver at `:183-192`. The 3 tests at `tests/unit/strategy/engine/test_action_execution_engine.py:145-148,199-202,442-445` still patch the static method — they only need to construct the engine with a stub resolver instead. Pure test rewrite.

### Phase 4 — Task 3.20 second bullet investigation
PROJ-479's task description claims `_per_player_ui_state.load(...)` private-attr access (lines 1189-1231) needs "public state-restore API". Before assuming this is a production seam gap, investigate the production class:
- Does a public restore method exist?
- If yes → pure test rewrite (stays in PROJ-491).
- If no → real seam gap; move task to PROJ-493 and document in `decisions.md`.

## Why test-side migrations are safe without production changes

Per `docs/02_PATTERNS.md:22,88,106,678` and `docs/01_ARCHITECTURE.md:58,175,437-438`, the codebase prefers constructor injection. Where seams exist (like `ActionExecutionEngine.action_time_resolver`), tests should consume them. Where tests bypass them by patching internals, the fix is test-side — call the existing seam.

For UI windows where the test seam is `bypass_init`, the canonical fixture exists. PROJ-458 / PROJ-470 have already retrofitted 11 windows. Continuing the retrofit pattern is mechanical.

## Risks

- **Risk:** Some tasks may surface previously-hidden production gaps (e.g. Task 3.3's "use real Fleet + minimal GameSession" — does the minimal GameSession exist or need to be built?).
  **Mitigation:** Per-task entry check before TDD; if a real seam is missing, log the task as a candidate to move to PROJ-493 and continue with the next task.

- **Risk:** Task 3.31 (`importlib.reload` factoring) has documented reload hazards. A naive fixture extraction could destabilize other tests that share the reloaded module.
  **Mitigation:** Scope the fixture narrowly and add a session-end teardown that re-imports the production module.

- **Risk:** UI panel migrations to `bypass_init` may surface constructor regressions that the old no-op-`__init__` pattern hid.
  **Mitigation:** That's actually the goal of Task 3.16 — surfacing regressions is correct behavior, not a risk. Failing tests should be investigated as real bugs.

## Source evidence

- Codex consult response: `AgentCoordination/Scratchpad/Consult/20260523T125621Z_plan-PROJ-479-followthrough/response.md`
- PROJ-479 plan + checklists + audit_verification: `Projects/active_projects/PROJ-479/`
- bypass_init canonical: `tests/fixtures/ui_widget_factory.py:254-328` (line 20-28 is `make_ui_widget` factory, not bypass_init)
- ActionExecutionEngine DI seam: `game/strategy/engine/action_execution_engine.py:55-68,183-192`

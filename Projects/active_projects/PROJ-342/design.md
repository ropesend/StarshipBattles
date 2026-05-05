# PROJ-342: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Crash mechanics

User triggered `AttributeError: 'ScreenRouter' object has no attribute 'screen'` at [game/ui/screens/test_lab/screen.py:382](../../../game/ui/screens/test_lab/screen.py#L382) by clicking "Run All" in Combat Lab. The failing line is `screen_center_x = self.game.screen.get_width() // 2`.

**Why it crashed:** `TestLabScreen` was constructed at [game/screen_router.py:125-127](../../../game/screen_router.py#L125-L127) with `self` (a `ScreenRouter`) passed as the `game` arg. `ScreenRouter` has no `.screen` attribute — only `_boot.screen` (private). `App` (`game/app.py:83`) has `.screen`. The construction comment at [game/screen_router.py:123-124](../../../game/screen_router.py#L123-L124) explicitly flags this as known tech debt: *"NB: TestLabScreen still asks for `self` (the legacy 'Game' handle) in its first arg. The router stands in for that role here."*

**Why it didn't crash earlier:** Init at `screen.py:73-74` had a `hasattr(game, 'screen')` fallback to `WIDTH/HEIGHT` constants, so construction silently succeeded. Only the runtime surface accesses (lines 382-389) crash, which only fire on the "Run All" batch path.

### Refactor lineage

Commit `b24dfea91` extracted `ScreenRouter` from `App`. Every other screen (`BattleScreen`, `BattleSetupScreen`, `StrategyScreen`, `DesignWorkshopScreen`) migrated to `(screen_width, screen_height, ...)` constructor + `draw(screen)` surface-as-parameter. `TestLabScreen` is the lone holdout — the legacy comment at the construction site has been deferred technical debt since.

### What `self.game` actually does

12 access sites across [screen.py](../../../game/ui/screens/test_lab/screen.py):
- **Dimensions (init only):** lines 73-74 with `hasattr` fallback
- **Live display surface:** lines 382-384, 388-389
- **`battle_scene` reads:** lines 322-325, 334, 347-350, 394, 398-400, 489

`TestLabUIController` at [combat_lab/services/test_lab_controller.py:36, 102-105](../../../combat_lab/services/test_lab_controller.py#L36) takes `game` solely to pass it into orphan methods.

### Dead code finding (Codex review)

`TestLabUIController.handle_run_visual()` and `handle_run_headless()` are not called from production. The screen routes runs through `self._executor.run_visual/run_headless` (executor → `_switch_to_battle` directly). Verified by `git grep -nE "handle_run_visual|handle_run_headless" -- combat_lab game tests`: production hits are inside the methods themselves; external hits are tests, archive, and docs. Once the methods are deleted, `TestExecutionService` and `TestResultsService` become orphan duplicate services with zero non-test callers.

## Swarm Findings Summary

Combined analysis from initial code review + Claude/Codex consensus discussion at [discussion artifact](../../../AgentCoordination/Scratchpad/Discussion/20260505T000631Z_testlab-drop-game-handle/), plus six Phase B Explore agents whose individual reports are in [findings/](findings/).

### Phase B agent verdicts

| Agent | Verdict | Adopted? |
|---|---|---|
| Architecture Analyst | One layer-boundary flag: `self.battle_scene.start_battle()` is same-layer mutation; recommends routing via `scene_callback` | **Documented as decision; partially adoptable as follow-up — see `decisions.md`** |
| Dependency Mapper | No hidden callers of deleted services beyond what plan covers | Plan unchanged |
| Test Impact Analyst | Precise per-file dispositions: net -29 tests; specific line ranges for keep/delete/update | **Folded into [phase_5_checklist.md](phase_5_checklist.md)** |
| Pattern Scout | All proposed changes follow established conventions or have justified novelty | Plan unchanged |
| Risk Assessor | 9 risks; most pre-existing or already covered. Risk 3 (`_battle_service` fragility) noted as follow-up debt | **Folded into [findings/risk_assessor.md](findings/risk_assessor.md)** |
| Data Flow Tracer | All 11 `self.game.*` access sites preserve identical semantics post-refactor | Plan unchanged |

### Architecture

- The modern screen-construction pattern is documented at [docs/03_CONVENTIONS.md §2.4](../../../docs/03_CONVENTIONS.md). [BattleScreen.__init__](../../../game/ui/screens/battle_screen.py#L68) is the canonical exemplar: `__init__(self, screen_width: int, screen_height: int, scene_callback=None)`.
- `ScreenRouter` is the runtime owner of all scene instances. It does not aim to be `App`-shaped; the legacy `self.game` parameter on `TestLabScreen` was a transitional fit that was never tightened.
- Construction order: `ScreenRouter.__init__` builds [battle_scene at line 115](../../../game/screen_router.py#L115) before [test_lab_scene at line 125](../../../game/screen_router.py#L125), so `self.battle_scene` is available to inject directly.

### Key Patterns to Reuse

- **Screen constructor pattern**: [game/ui/screens/battle_screen.py:68](../../../game/ui/screens/battle_screen.py#L68) — `(screen_width, screen_height, scene_callback)` plus collaborator deps. Adopt for `TestLabScreen`.
- **`IScene.draw(screen)` surface-as-parameter**: every other screen takes the surface from the run-loop. Where `TestLabScreen`'s batch-mode rendering can't piggyback (executor calls outside the normal draw cycle), use `pygame.display.get_surface()` — canonical pygame for "the active display surface."
- **Scene callback pattern**: scenes call `self.scene_callback(action, **kwargs)` instead of poking router/app state. `TestLabScreen` already does this for menu return / battle transition; preserved unchanged.

### Display surface lifecycle (Codex evidence)

Bootstrap creates or reuses the display surface before router/screens exist at [game/app_bootstrap.py:193-197](../../../game/app_bootstrap.py#L193). `Game.__init__` runs bootstrap before creating `ScreenRouter` at [game/app.py:76-80, 108-114](../../../game/app.py#L76). `_render_progress` and `_draw_and_flip` are reached only from user-driven executor paths at [test_executor.py:221-223, 368-370](../../../game/ui/screens/test_lab/test_executor.py#L221), so `pygame.display.get_surface()` cannot be `None` in production. A `_require_display_surface()` precondition helper provides clear diagnostics if a unit test forgets to set up the display.

### Dependencies & Risks

1. **Orphan service callers missed by grep** — risk that `TestExecutionService` or `TestResultsService` has a non-test caller `git grep` did not surface (e.g., dynamic import, registry registration, plugin discovery). **Mitigation:** Phase 4 includes an explicit verification step before deletion. If implementation finds a caller, narrow the scope to controller-method deletion only and park service deletion as follow-up.
2. **Test-mock fixture sprawl** — `mock_game = Mock()` patterns in `tests/unit/test_lab/test_visual_run.py` are easy to copy-paste into new tests. **Mitigation:** Phase 5 replaces with `mock_battle_scene` fixture and the new tests use it as the canonical pattern.
3. **`pygame.display.get_surface()` returning `None` in unit tests** — opaque `AttributeError` at downstream call sites. **Mitigation:** `_require_display_surface()` helper raises `RuntimeError` with a clear message; cheap diagnostics.
4. **Documentation drift** — `combat_lab/COMBAT_LAB_DOCUMENTATION.md` has four sections describing the deleted services; runner.py + battle_controller.py docstrings reference them. **Mitigation:** Phase 6 lists every stale reference identified by grep.

### Opportunities Discovered

- `BattleStateViewer` is constructed with constants at [screen.py:137-138](../../../game/ui/screens/test_lab/screen.py#L137); the viewer accepts dimensions and supports resize at [battle_state_viewer.py:39-54, 146-152](../../../game/ui/screens/battle_state_viewer.py#L39); `TestLabScreen.handle_resize` at [screen.py:623-628](../../../game/ui/screens/test_lab/screen.py#L623) does not forward. Absorb the fix while we're already touching the dimension-injection story.

### Hidden coupling check

Codex grep `git grep -n "self\.game\|screen\.game\|controller\.game" -- game/ui/screens/test_lab tests/unit/test_lab tests/unit/combat_lab/services` found only `screen.py` and unit-test fixture assignments. No hidden coupling in `panel_manager`, `renderer`, `viewmodel`, `screen_input_handler`.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

Key decisions made before implementation:

1. **Option C (full refactor) over Option A (`pygame.display.get_surface()` only) or B (`screen` property on `ScreenRouter`).**
2. **Delete `TestExecutionService` + `TestResultsService` along with the controller methods.**
3. **Add `_require_display_surface()` helper for clear diagnostics.**
4. **Split TDD Phase into "current-crash regression" + "new-constructor contract".**
5. **Absorb `BattleStateViewer` sizing/resize fix in scope.**
6. **Defer `TestLabScreen` LOC reduction (738 → ≤500) as follow-up debt.**

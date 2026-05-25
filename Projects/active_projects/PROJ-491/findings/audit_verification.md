# PROJ-491 — Codex audit verification

**Consult:** `AgentCoordination/Scratchpad/Consult/20260523T144503Z_audit-PROJ-491/response.md`
**Auditor:** codex (mid-project-review, 2026-05-23T14:49Z)
**Verified by:** Claude orchestrator (Batch 4)

## Verification table

| id  | verdict                | evidence                                                                                                                                                                                                                                                                                                                                          | action                                              |
|-----|------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------|
| F1  | VERIFIED + IN-SCOPE    | `tests/unit/test_app_public_api.py:6-10` header still documents contract `(self, args=None)`. New `test_game_constructs_with_no_args` at lines 44-78 only exercises `Game()` with no args. Production `main()` constructs `Game(args)` positionally (`game/app.py:55-68,510-513`). A regression breaking the `Game(args)` calling convention would slip through. Task 1.4 narrowed coverage. | Phase 5 Task 5.1 — add a second behavioral test covering the `Game(args)` positional-call path. |
| F2  | VERIFIED + IN-SCOPE    | `tests/unit/ui/screens/test_build_queue_panel_factory.py:228` uses `>= int(0.8 * total)`. For total=6 that's >=4 (66.7%), weaker than the documented "≥80%". Residuals go to `warnings.warn` (non-fatal). Production gives every `UIPanel` the `@fast_panel` id (`game/ui/screens/build_queue_panel_factory.py:213-217,262-267,...`), so the actual contract is 100%. Plan Task 1.12 said "behavior-based or kwargs-extraction" — relaxing to a soft floor exceeds that. | Phase 5 Task 5.2 — tighten the assertion to match the actual production contract (100% fast_panel) while preserving the behavioral framing. Drop the warnings.warn fallback. |
| F3  | VERIFIED + IN-SCOPE    | `tests/unit/ui/screens/test_build_queue_list_window.py:12-16` docstring claims helper avoids directly patching `pygame_gui.elements.UIWindow.kill`. Line 50 does exactly that: `patch.object(pygame_gui.elements.UIWindow, "kill", MagicMock())`. Stale comment drift. | Phase 5 Task 5.3 — update the docstring to accurately describe what `_disable_pygame_gui_kill_side_effect` actually does (a scoped wrapper around the patch). |
| F4  | NOT-A-FINDING (positive confirmation) | Codex confirmed no test was DELETED that should have been REWRITTEN. | None. |
| F5  | NOT-A-FINDING (positive confirmation) | Codex confirmed Task 3.32 uses the existing DI seam (`action_time_resolver=` ctor param), no new seam, no static-method patch. Evidence cited at `tests/unit/strategy/engine/test_action_execution_engine.py:51-69,161-164,218-221,464-467`. | None. |

## Effort estimate for remediation

Three small edits across three files. Estimated <5 minutes of LLM time. Well under the 15-minute escalation threshold — proceeding to Phase 5.

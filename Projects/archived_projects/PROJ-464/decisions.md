# PROJ-464: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-19 | Project initialized | Starting point for Type cleanup — presentation (UI + top-level) (2026-05-19) |
| 2026-05-19 | Bundled presentation findings from `2026-05-19_223900_type-audit` by code locality across ui + top-level | Bundling driven by code relatedness rather than severity to maximize implementation continuity; full bundling discussion in findings/bundling_decisions.md |
| 2026-05-19 | TYP-SR (StrategyRenderer) INCLUDED as a renderer-scene Protocol seam, not a hard narrow to StrategyScreen | Tests instantiate the renderer with MagicMock scenes and assert property delegations; a Protocol keeps them passing. Codex-aligned. |
| 2026-05-19 | TYP-APP (Game scene accessors) REJECTED / out of scope | Proxies route through dynamic `_route_get` and are intentionally loose for `Game.__new__(Game)` tests; narrowing to IScene would break mocks. Codex concurred. |
| 2026-05-19 | Sequenced LAST (after PROJ-462 foundation and PROJ-463 domain) | UI consumes core-protocol/strategy types; UI strict-mode is the largest single layer (mostly external pygame_gui). |

## Autonomous-override consult record

This project set was created autonomously (no AskUserQuestion). One Codex consult (mode=planning) seconded the bundling and the borderline verdicts. Consult leaf: `AgentCoordination/Scratchpad/Consult/20260520T061000Z_type-audit-bundling/`.

**Codex input (summary):** Keep 3 projects. For TYP-SR, include only if framed as a renderer-scene Protocol seam (cited the MagicMock-scene tests at `tests/unit/ui/screens/test_strategy_renderer.py`); if the only plan is "replace Any with StrategyScreen", defer. For TYP-APP, keep rejected (cited `game/app.py:173-188`, `tests/unit/test_app_delegators.py`). Sequence UI strict last; pygame_gui is mostly external.

**My final decision (I own the call):** Adopted. TYP-SR included as a Protocol-seam task (Phase 1.2 explicitly forbids hard-narrowing to StrategyScreen). TYP-APP stays rejected. UI strict-mode scheduled last (Phase 3.2) with an explicit pygame_gui-handling decision step. Codex's framing converted TYP-SR from a risky narrow into a test-safe task; it did not change the bundle structure.

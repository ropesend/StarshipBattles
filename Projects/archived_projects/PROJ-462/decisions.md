# PROJ-462: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-19 | Project initialized | Starting point for Type cleanup — foundation (core/services/engine/research/assets) (2026-05-19) |
| 2026-05-19 | Bundled foundation findings from `2026-05-19_223900_type-audit` by code locality across core/services/engine/research/assets | Bundling driven by code relatedness rather than severity to maximize implementation continuity; full bundling discussion in findings/bundling_decisions.md |
| 2026-05-19 | Foundation sequenced FIRST as a prerequisite for the domain/presentation siblings | Vector2 + core-protocol fixes here resolve ~130 downstream mypy errors; called out in PROJ-463/PROJ-464 Scope:Out. Codex consult corroborated and recommended making the prerequisite explicit. |

## Autonomous-override consult record

This project set was created autonomously (no AskUserQuestion). One Codex consult (mode=planning) was run to second-opinion the bundling and the borderline verdicts. Consult leaf: `AgentCoordination/Scratchpad/Consult/20260520T061000Z_type-audit-bundling/` (request.md / response.md).

**Codex input (summary):** Keep the default 3 projects (foundation/domain/presentation) — V=51 sits in protocol 13's 30–100 band and matches its merge map and the codebase's bottom-up dependency flow; do not expand. Make foundation an explicit prerequisite and state it in the downstream Scope/Out. Include TYP-COREPROTO only as a boundary-preserving subset (narrow strategy-map surfaces like `global_location`/`location`/`local_hex` to core `HexCoord` and list element types; leave `ICombatant.position`/`ILocatable.location` as `Any`; never import strategy concrete types into core). Include TYP-SR only framed as a renderer-scene Protocol seam cleanup, not a hard narrow to `StrategyScreen` (tests instantiate the renderer with MagicMock scenes). Keep TYP-APP rejected (Game scene proxies are intentionally loose for `Game.__new__` tests).

**My final decision (I own the call):** Adopted all of Codex's points. 3 projects confirmed; foundation prerequisite made explicit in sibling Scope/Out. TYP-COREPROTO included here with the boundary-preserving carve-out written into Phase 2.4. TYP-SR included in PROJ-464 framed as a Protocol-seam task. TYP-APP stays rejected. Codex's advice materially sharpened the two UNCERTAIN items (from "include with care" to concrete, layer-safe, test-aware tasks) and added the explicit prerequisite sequencing; it did not change the 3-project structure I had proposed.

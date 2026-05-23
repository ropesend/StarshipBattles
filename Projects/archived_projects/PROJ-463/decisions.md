# PROJ-463: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-19 | Project initialized | Starting point for Type cleanup — domain (simulation/strategy/ai) (2026-05-19) |
| 2026-05-19 | Bundled domain findings from `2026-05-19_223900_type-audit` by code locality across simulation/strategy/ai | Bundling driven by code relatedness rather than severity to maximize implementation continuity; full bundling discussion in findings/bundling_decisions.md |
| 2026-05-19 | Sequenced AFTER foundation (PROJ-462) | Vector2 + core-protocol fixes in PROJ-462 clear ~65 simulation + ~6 ai `has-type` errors and unblock strategy returns; recorded as a blocker in plan.md Current State. |

## Autonomous-override consult record

This project set was created autonomously (no AskUserQuestion). One Codex consult (mode=planning) seconded the bundling. Consult leaf: `AgentCoordination/Scratchpad/Consult/20260520T061000Z_type-audit-bundling/`.

**Codex input (summary):** Keep 3 projects (V=51 in protocol band); make foundation an explicit prerequisite (stated here in plan.md); the domain bundle is the heaviest and is the first split candidate later if more items land. Borderline verdicts (TYP-COREPROTO carve-out, TYP-SR Protocol-seam, TYP-APP rejected) all confirmed.

**My final decision (I own the call):** Adopted. Domain kept as one bundle; foundation prerequisite noted. The 2 UNCERTAIN items live in PROJ-462 (TYP-COREPROTO) and PROJ-464 (TYP-SR); none affected this bundle's contents. See findings/bundling_decisions.md for the full record.

# Bundling Decisions — type-audit `2026-05-19_223900_type-audit`

This file is identical across the three sibling projects (PROJ-462, PROJ-463, PROJ-464) so the full picture can be read once.

## Mode of operation

Created autonomously by the `claude-audit-sweep` orchestrator. Protocol 13's `AskUserQuestion` decision points were replaced by: (a) well-reasoned defaults, plus (b) one Codex consult (planning mode) for a second opinion. The initiator (Claude) owned the final call. Consult leaf: `AgentCoordination/Scratchpad/Consult/20260520T061000Z_type-audit-bundling/`.

## Verification totals

Out of ~250 audit findings, a normalized candidate set of 51 actionable, located items + the 10 strict-migration items was built (`.agent_reports/2026-05-19_223900_type-audit/candidates.json`). After an independent third-pass re-verification against live source:

- **VERIFIED:** 51 (41 located code findings + 10 strict-migration layer items)
- **REJECTED:** 1 (TYP-APP)
- **UNCERTAIN:** 2 (TYP-COREPROTO, TYP-SR) — both resolved to Include with carve-out notes
- **OUT_OF_SCOPE:** 0 promoted (the audit's own verification.md had already excluded justified ignores)

## Default proposal table (computed, Phase D Step 1)

| # | Title | Layers | Verified | Uncertain | Phases (severities) |
|---|-------|--------|----------|-----------|---------------------|
| 1 | Type cleanup — foundation | core, services, engine, research, assets | 17 | 1 (TYP-COREPROTO) | Critical, Major, Strict-migration |
| 2 | Type cleanup — domain | simulation, strategy, ai | 24 | 0 | Critical, Major, Strict-migration |
| 3 | Type cleanup — presentation | ui, top-level | 12 | 1 (TYP-SR) | Major, Minor, Strict-migration |

Totals: VERIFIED 51 (incl. 2 resolved uncertain) / UNCERTAIN→resolved 2 / REJECTED 1 / OUT_OF_SCOPE 0.

Rationale: V=51 sits in protocol 13's `30 <= V <= 100` band → 2–3 projects, merging adjacent small layers along the suggested foundation/domain/presentation map. This matches the codebase's bottom-up dependency flow (Core → … → UI).

## Adjustments

No structural adjustments were made — the default 3-project proposal was accepted. Codex concurred (would not collapse to 2 or expand beyond 3 at this count). The one accepted refinement was a sequencing/scope note: foundation is an explicit prerequisite for the domain and presentation bundles (Vector2 + core protocol fixes resolve ~130 downstream errors), recorded in each sibling's Scope:Out.

## Final bundle definitions

- **PROJ-462 — foundation:** core, services, engine, research, assets. 17 verified + TYP-COREPROTO (included with boundary-preserving carve-out). Phases: 1 Critical, 2 Major, 3 Strict-migration (5 layers).
- **PROJ-463 — domain:** simulation, strategy, ai. 24 verified. Phases: 1 Critical, 2 Major, 3 Strict-migration (3 layers).
- **PROJ-464 — presentation:** ui + top-level. 12 verified + TYP-SR (included as a Protocol-seam task). Phases: 1 Major, 2 Minor, 3 Strict-migration (ui + unknown).

## UNCERTAIN item resolutions (Phase D Step 3)

| id | bundle | question | decision |
|----|--------|----------|----------|
| TYP-COREPROTO | PROJ-462 | strategy_entities.py 18 `-> Any`; some narrowable, but `ICombatant.position`/`ILocatable.location` must stay Any (Vector2 vs HexCoord across implementers); narrowing needs cycle-safe imports | **INCLUDE** with boundary-preserving carve-out: narrow strategy-map surfaces to core types (`HexCoord`, `list[Star]`, etc.); leave the duck-typed position/location seams as `Any`; never import strategy concrete types into `game/core/protocols/`. (Codex-aligned.) |
| TYP-SR | PROJ-464 | strategy_renderer.py 13 props: cross-layer report says narrowable, Shard 04 says acceptable due to dynamic routing; tests use MagicMock scenes | **INCLUDE** framed as a minimal renderer-scene Protocol seam cleanup — NOT a hard narrow to `StrategyScreen` (would break MagicMock-scene tests). (Codex-aligned.) |

## REJECTED item (Phase D, recorded here and in each verification_report.md)

| id | reason |
|----|--------|
| TYP-APP | `game/app.py:198-233` Game scene accessor properties route through dynamic `_route_get`; the audit's own Shard 04 reviewer rated them acceptable and notes narrowing to `IScene` "would break test mocks" (`Game.__new__(Game)` tests assign loose attributes). A separate test-surface hardening question, not a clean audit residue. Codex concurred. |

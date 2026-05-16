# PROJ-382 Bundling Decisions (Phase D)

> **Source:** `Reviews/results/2026-05-07_220452_pattern-audit/`
> **Phase D run date:** 2026-05-08
> **Authored by:** /claude-proj-from-pattern-audit (Protocol 18 §Phase D)

## Default proposal

After Phase C re-verification produced 21 VERIFIED + 6 UNCERTAIN + 5 in-scope LOC items (V<30), Protocol 18's default rule was **ONE project, all (layer, pattern_area) cells in one bundle**. Phases ordered Critical → Major → Minor → Strategic → LOC.

| # | Title                                                                            | Layers / Pattern areas                                            | Verified | Uncertain |
|---|----------------------------------------------------------------------------------|-------------------------------------------------------------------|----------|-----------|
| 1 | Pattern conformance — Facade integrity, EventBus injection, doc drift, LOC sweep | ui+strategy+simulation+docs · #5/#2/#10/#31/conv/#6/#7/#12/#3/#23 |   21     |    6      |

## User decisions

**Q1 — Bundling shape:** *One project, all 5 phases (Recommended).*
Single PROJ with phases Critical (Pattern #5) → Major (Pattern #2 / #10 / #31 / convention / naming) → Minor (CQRS / Pattern #7 / Pattern #12 / Pattern #3 / doc-drift) → Strategic (Re-Export Shim doc-add / Pattern #12 singleton-accessor) → LOC ceiling sweep.

**Q2 — Read-side facade-bypass uncertain items:** *Defer all three (Recommended).*
- U1 (~127 UI command DTO imports) — deferred. Audit itself classifies these as "partial bypass / pass-through".
- U2 (40 UI service imports) — deferred. Read-side bypass, fix is large.
- U3 (26 UI systems imports) — deferred. Audit notes RaceRandomizer is intentional.
All three logged in `verification_report.md` as deferred for a future dedicated PROJ.

**Q3 — Other uncertain items:** Multi-select — *all three included*.
- U4 — rename builder `EventBus` → `WorkshopEventBus` — included in Phase 2.
- U5 — make `ProductionSpawner.registries` required (Pattern #3) — included in Phase 3.
- U6 — promote Strategy Config Singleton Accessor to Pattern #12 doc — included in Phase 4 (despite single-site usage; the variant has explicit in-code justification).

## Final bundle

**PROJ-382 — Pattern conformance — Facade integrity, EventBus injection, doc drift, LOC sweep (2026-05-07)**

| Phase | Severity | Items |
|-------|----------|-------|
| 1     | Critical | 5 sites across 5 files (Pattern #5: VER-002 + VER-003) + AST static-guard test |
| 2     | Major    | 9 items (Pattern #2 ×1, Pattern #10 ×3, Pattern #31 ×1, conv §6.5 ×1, empty `__init__.py` ×1, U4 EventBus rename ×1) |
| 3     | Minor    | 9 items (Pattern #6 ×1, Pattern #7 ×1, Pattern #12 ×4, Pattern #3 ×1 [U5], Pattern #23 doc ×1, Pattern #7 doc ×1) |
| 4     | Strategic| 2 items (Re-Export Shim doc-add, Pattern #12 singleton-accessor [U6]) |
| 5     | LOC      | 5 files (planetary.py, battle_engine.py, fleet_navigation_service.py, superweapon_order_processor.py, conflict_resolution_engine.py) |

**Final counts:** 21 VERIFIED + 6 UNCERTAIN-included (U4, U5, U6 → Phases 2, 3, 4) + 5 LOC + 13 REJECTED + 1 OUT_OF_SCOPE (VER-001) + 3 UNCERTAIN-deferred (U1, U2, U3) + 9 LOC-deferred (already in active PROJs).

This file is identical across sibling projects in the same run, but only one project (PROJ-382) was created from this audit.

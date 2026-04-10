# PROJ-239: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-05 | Project created from review | Review identified 77 validated findings; 14 selected (top 10 priority issues) for remediation |
| 2026-04-05 | 4-phase structure by category | Phase 1: Critical fixes, Phase 2: Architecture boundaries, Phase 3: Code quality & dead code, Phase 4: Documentation. Grouped by category (not severity alone) for coherent work sessions |
| 2026-04-05 | AR-002 (facade bypass) deferred | Complex cross-cutting refactor affecting 6+ UI files. Tracked as a goal but not in active scope — too large for this remediation project |
| 2026-04-05 | Dead code removal: grep-verify before delete | All dead method removals must confirm zero callers via codebase-wide grep before deletion |
| 2026-04-05 | ERR-001: Log-and-continue for sub-engine errors | Each sub-engine phase is independent — a failure in harvesting shouldn't block movement. Error handling added in `_time_phase()` (the single chokepoint) so every phase call is wrapped. Errors logged at ERROR with full traceback via `exc_info=True`. Partial turn progress is better than a crashed game. |
| 2026-04-05 | AR-001: AI factory injected from UI layer, not late-imported | `SimulationBattleResolver` now requires `ai_factory` param. Factory created in `app.py` (UI layer, which can import game.ai) and passed through `GameSession` → `TurnEngine`. `_NullBattleResolver` placeholder used for tests that don't trigger combat. This eliminates all `game.ai` imports from the strategy layer. |

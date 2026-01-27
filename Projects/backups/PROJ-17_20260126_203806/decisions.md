# PROJ-17: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-25 | Project initialized | Starting point for Enforce Layer Boundaries |
| 2026-01-25 | Move ShipThemeManager to `game/ui/assets/` | User decision: Full cleanup since it's only accessed by UI code anyway. Keeps pygame in appropriate layer. |
| 2026-01-25 | Fix pygame imports in AI layer | User decision: Replace `pygame.math.Vector2` with `game.core.math.Vector2` in controller.py, target_evaluator.py, behaviors.py. Simple 2-line fix per file. |
| 2026-01-25 | Full orchestration refactor for AI | User decision: Create BattleOrchestrator in UI layer rather than factory injection. Most clean separation but largest change. |
| 2026-01-25 | Keep backward-compatible re-exports | Risk mitigation: Keep re-exports in old locations (component_constants.py, ship_theme.py) to prevent breaking existing code. Can be removed in future release. |
| 2026-01-25 | Phase 4 depends on Phase 1 | AI layer must be clean of pygame before creating BattleOrchestrator that imports from AI. |
| 2026-01-25 | Preserve legacy path in BattleEngine | Risk mitigation: Keep internal AI creation as fallback when `ai_controllers=None`. Ensures backward compatibility. |
| 2026-01-25 | Move LayerType to `game/core/constants.py` | Shared by simulation, AI, and UI layers. Core is appropriate home for cross-layer enums. AttackType already there as precedent. |

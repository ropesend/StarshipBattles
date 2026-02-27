# PROJ-192: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Project initialized | Starting point for AI Behavior Protocols - Duck Typing Elimination |
| 2026-02-24 | New protocols go in `game/ai/protocols.py`, not `game/core/protocols.py` | AI grid entity and target protocols are AI-layer concerns. Core shouldn't know about AI concepts. |
| 2026-02-24 | Use `@runtime_checkable Protocol` pattern (not ABC) for new protocols | Follows established `game/core/protocols.py` conventions. Structural typing matches the duck-typing replacement use case. |
| 2026-02-24 | Create 4 protocols: IGridEntity, IProjectile, IFormationMaster, IComponentHealth | Each maps to a distinct category of duck typing. Minimal set that covers all 45 instances. |
| 2026-02-24 | Fix `_eval_least_armor_rule` bug inline (not separate ticket) | One-line fix directly in scope. `getattr(c, 'hp', 0)` → `c.current_hp`. User approved. |
| 2026-02-24 | Replace `getattr(ship, 'id', None)` with `ship.name` in capabilities cache | Ship has no `.id` attribute; `.name` is the identifier. Cache key was always None for ships. |
| 2026-02-24 | Remove defensive getattr defaults in ShipControllableAdapter | Ship always sets `max_targets`, `ai_strategy`, `vehicle_type` in `__init__`. Defaults were PROJ-12 legacy. |
| 2026-02-24 | Keep `is_vector2_like()` mock detection but simplify Vector2 check to isinstance | Codebase always uses `game.core.math.Vector2`. Mock detection stays as test-infrastructure concern. |

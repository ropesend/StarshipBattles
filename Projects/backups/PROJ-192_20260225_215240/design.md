# PROJ-192: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Problem
The `game/ai/` module has ~45 `hasattr()`/`getattr()` calls across 5 files that obscure dependency contracts. These calls fall into 6 categories:

1. **Grid Entity Polymorphism** — `SpatialGrid.query_radius()` returns `List[Any]` containing both Ships and Projectiles, requiring `getattr(obj, 'type', '')` checks
2. **Target Candidate Attributes** — accessing `mass`, `velocity`, `id`, `position` with fallback defaults
3. **Formation Master Attributes** — raw Ships returned from `get_formation_master()`, requiring `getattr(master, 'is_derelict', False)` etc.
4. **Component HP Access** — `getattr(comp, 'current_hp', 1)` on Components that always have these attributes
5. **combat_utils.py Dual-Path Helpers** — functions that try interface methods before falling back to direct attributes
6. **Adapter Defensive Defaults** — `getattr(self._ship, 'max_targets', ...)` in ShipControllableAdapter for attributes Ship always has

### Bug Found
`target_evaluator.py:184` — `getattr(c, 'hp', 0)` always returns 0 because Component has no `.hp` attribute (only `current_hp` and `max_hp`). This makes the `least_armor` targeting rule non-functional. Fix: change to `c.current_hp`.

### Key Insight: Many getattr() Calls Are Unnecessary
Ship always sets in `__init__`: `is_derelict` (L145), `is_thrusting` (L161), `engine_throttle` (L156), `vehicle_type` (L95), `ai_strategy` (L150), `max_targets` (L63). PhysicsBody always sets: `mass` (L62), `position`, `velocity`. Component always sets: `current_hp` (L116), `max_hp` (L115).

Many `getattr()` calls were defensive coding from earlier project phases when attribute existence was uncertain. Now that the codebase is mature, direct access is safe.

## Swarm Findings Summary

### Architecture
- `IControllable` ABC (45 abstract methods) already exists from PROJ-24
- `ShipControllableAdapter` wraps Ship for AI use, formation methods return raw Ships intentionally
- `game/core/protocols.py` has 20+ `@runtime_checkable` Protocols including `ICombatant` (`team_id`, `is_alive`, `position`) and `IDamageable` (`current_hp`, `max_hp`, `is_derelict`)
- Two established patterns: `@runtime_checkable Protocol` (structural) vs `ABC` (formal contracts)

### Key Patterns to Reuse
- **Protocol + TypeGuard pattern**: `game/core/protocols.py` — all protocols have paired TypeGuard functions
- **IControllable pattern**: `game/ai/interfaces/controllable.py` — ABC for formal AI-ship contract
- **ICombatant protocol**: `game/core/protocols.py:306` — already covers `team_id`, `is_alive`, `position`

### Dependencies & Risks
1. **Test mocks** — Many tests use `Mock()` objects. `@runtime_checkable` Protocol `isinstance` checks won't match `Mock()` without `spec=`. Mitigation: Update test mocks where isinstance checks are added.
2. **Formation master typing** — Formation masters are raw Ships returned without wrapping. Mitigation: Use `IFormationMaster` protocol for structural matching.
3. **Grid entity diversity** — Ships and Projectiles share grid space. Mitigation: `IGridEntity` protocol captures common attributes, `IProjectile` narrows for missile-specific code.

### Opportunities Discovered
- The armor HP bug fix will make `least_armor` targeting rule functional for the first time
- Type annotations will improve IDE autocomplete throughout the AI module
- Protocols can be reused if other layers need to interact with AI entities

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

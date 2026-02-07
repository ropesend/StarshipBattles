# PROJ-56: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Baseline
- **Tests:** 6114 passed, 5 skipped (2026-02-06)
- **Pre-existing skips:** Same 5 as PROJ-54

### Problem Statement
The CLAUDE.md policy (lines 136-158) explicitly forbids backward compatibility shims, yet there are 44+ occurrences across the codebase. Each shim doubles the API surface, creates confusion about authoritative interfaces, and accumulates technical debt.

### Categories of Backward Compatibility Code Found

| Category | Count | Risk | Effort |
|----------|-------|------|--------|
| Path constant re-exports (`constants.py`, `paths.py`) | 22 import sites | Low | Low - mechanical import changes |
| LayerType re-export (`component_constants.py`) | 19 import sites | Low | Low - mechanical import changes |
| Formation delegation properties (`ship.py`) | 6 properties, ~12 callers | Medium | Low - update adapter + remove props |
| ShipCombatMixin facade (`ship_combat.py`) | 8 methods, ~7+ callers | High | Medium - need careful routing |
| Workshop ViewModel proxies (`workshop_screen.py`) | 3 properties | Low | **Zero** - no callers found |
| BattleController retreat proxies (`battle_controller.py`) | 4 properties + 2 fallback methods | Medium | Medium - update callers |
| Collision defense score fallback (`collision.py`) | 1 fallback chain | Low | Low - verify all ships have new attr |
| Deprecated registry functions (`registry.py`) | Already removed! | None | None |

## Swarm Findings Summary

### Architecture

**Layer Violations:** The backward compat shims are spread across all layers:
- **Core:** `constants.py`, `paths.py`, `registry.py` (re-exports)
- **Simulation:** `ship.py`, `ship_combat.py`, `battle_controller.py`, `collision.py` (delegation/facade)
- **UI:** `workshop_screen.py` (MVVM proxy properties)
- **AI:** `controllable.py` (adapter using compat properties)

### Key Patterns to Reuse

- **Strict DI Pattern** (PROJ-50): `Ship.__init__(registries=GameRegistries)` - the target pattern for registry access
- **Paths class access**: `from game.core.paths import Paths; Paths.ROOT_DIR` - the target pattern for path constants
- **Direct formation access**: `ship.formation.master` - the target pattern for formation properties
- **Direct engine access**: `ship.combat_engine.method()` - potential target for combat operations

### Dependencies & Risks

1. **ShipCombatMixin removal is the riskiest change** - `take_damage()`, `fire_weapons()`, `update_combat_cooldowns()` are called from multiple layers (simulation, strategy, tests). Need to verify all callers route to `combat_engine`.

2. **BattleController fallback methods** - `_retreat_allowed()` and `_reinforcements_allowed()` have dual-path logic (mode handler OR config). Need to verify mode handler is always present before removing fallback.

3. **Formation properties** - Used by AI adapter (`controllable.py`). Must update adapter before removing properties.

4. **Constants imports** - 41 files to update (22 path constants + 19 LayerType). Mechanical but high volume.

### Opportunities Discovered

- **Workshop proxy properties can be deleted immediately** - zero callers detected
- **Registry deprecated functions already removed** - PROJ-38 migration is complete for global functions
- **Collision fallback** - can likely be removed since `total_defense_score` is a computed property on Ship (always present)
- **`component_constants.py` LayerType re-export** - PROJ-17 completed, this re-export just never got cleaned up

### What's NOT a Backward Compat Shim (Exclusions)

These look like backward compat but are actually proper architectural patterns:
- **`ShipControllableAdapter`** - Proper adapter pattern (not a shim), but its `.ship` property is fine
- **`SimulationBattleResolver`** - Proper adapter between strategy and simulation layers
- **`DesignLoaderAdapter`** - Proper layer isolation facade
- **`get_default_registries()` fallback** - Transitional DI pattern, removal is a separate PROJ-38 concern

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

### Key Decision: ShipCombatMixin Strategy

**Option A:** Remove mixin, move methods to Ship class body directly
**Option B:** Remove mixin, redirect all callers to `ship.combat_engine.method()`
**Option C:** Keep mixin but remove "backward compat" comment (it's just code organization)

**Recommendation:** Option A - Inline methods into Ship class. The mixin is just 8 thin wrappers. Inlining them into Ship simplifies the class hierarchy without changing any caller signatures. This is the least disruptive approach.

### Key Decision: Path Constants Migration

**Target:** `from game.core.paths import Paths` then `Paths.CONSTANT`
**Alternative:** Could keep module-level re-exports in `paths.py` and just remove them from `constants.py`
**Recommendation:** Full migration to `Paths.CONSTANT` - clean and consistent.

# PROJ-58: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Baseline
- **Tests:** 6248 passed, 0 skipped, 0 failed (2026-02-06)

### Problem Statement
The CLAUDE.md policy (lines 136-158) explicitly forbids backward compatibility shims, yet there are 23+ active occurrences across the codebase. Each shim doubles the API surface, creates confusion about authoritative interfaces, and accumulates technical debt.

### Complete Inventory of Backward Compatibility Code

| # | Category | Location | Items | Callers | Risk | Effort |
|---|----------|----------|-------|---------|------|--------|
| 1 | Workshop ViewModel proxies | `workshop_screen.py:357-379` | 3 properties | 11 internal | Low | Low |
| 2 | Dead mixin methods | `ship_combat.py:90-148,161-174` | 3 methods | 0 callers | Zero | Zero |
| 3 | Stale compat comments | Multiple files | ~5 comments | N/A | Zero | Zero |
| 4 | Path constant re-exports | `constants.py:64-78`, `paths.py:130-141` | 10 re-exports | 23 files | Low | Low |
| 5 | WIDTH/HEIGHT re-exports | `constants.py:54-58` | 2 re-exports | 2 files | Low | Low |
| 6 | LayerType re-export | `component_constants.py:24-26` | 1 re-export | 24 files (legacy) + 34 (canonical) | Low | Low |
| 7 | Formation delegation | `ship.py:216-262` | 5 properties | 10 prod + 6 adapter + 155 test | Medium | Medium |
| 8 | ShipCombatMixin facade | `ship_combat.py` | 9 methods | 11 prod + 40+ test | **High** | **High** |
| 9 | BattleController proxies | `battle_controller.py:589-628` | 3 properties | Tests only | Medium | Low |
| 10 | BattleController fallback logic | `battle_controller.py:454-472` | 2 OR-fallbacks | Internal | Medium | Medium |
| 11 | Collision defense fallback | `collision.py:112-121` | 1 hasattr chain | 1 site | Low | Low |
| 12 | Registry DI fallback | `registry.py` | 1 function | 6 prod + 5 test | Medium | High |

### Items Explicitly OUT of Scope

| Item | Reason |
|------|--------|
| `apply_results_to_fleets()` legacy fallback | Blocked by PROJ-41 - mode handler implementation incomplete |
| BattleEngine legacy controller creation | Used by tests and simple scenarios; broader refactor needed |
| `DefaultRegistryProvider` dual pattern | Proper DI implementation, not a shim |
| `ValidationResult` dual construction | Supports both positional and keyword args by design |
| `ComponentRef.from_tuple()/to_tuple()` | Active migration utilities, not deprecated |
| `GameSession.player_empire/enemy_empire` | Convenience aliases, not backward compat |
| Star generation "original algorithm" | Comment-only, no actual compatibility code |
| `SaveGameService` version checking | Explicitly rejects old versions (not backward compat) |

---

## Swarm Findings Summary

### Architecture Analysis (Agent 1 - Compat Location Mapper)

**23 active backward compatibility occurrences** found across production code (excluding archived projects). Categorized as:
- **7 active fallback paths** (legacy code execution paths)
- **5 delegation/proxy properties** (wrapping newer APIs)
- **4 facade methods** (thin wrappers)
- **3 re-export aliases** (constant re-exports)
- **2 comment-only** references
- **1 version migration** (explicitly rejects old versions)

### ShipCombatMixin Analysis (Agent 2)

**Complete method inventory:**
- `update_combat_cooldowns()` → delegates to engine (1 prod caller: `ship.py:314`)
- `fire_weapons(context)` → delegates to engine (1 prod caller: `ship.py:318`)
- `take_damage(damage_amount)` → delegates to engine (11 prod callers across 4 files)
- `solve_lead(pos, vel, t_pos, t_vel, p_speed)` → delegates to engine (2 prod callers)
- `_calculate_firing_solution(comp, target)` → **DEAD CODE** (0 callers)
- `_find_pdc_target(comp, context)` → **DEAD CODE** (0 callers)
- `die()` → direct implementation (called internally)
- `_damage_layer(layer_type, damage)` → delegates to non-existent engine method - **DEAD CODE**
- `_apply_repair(repair_amount)` → delegates to engine (0 direct callers, called internally by engine)

**Key finding:** `die()` method has actual logic (not just delegation). Must be moved to Ship class or ShipCombatEngine before mixin deletion.

### Formation Delegation Analysis (Agent 3)

**Much larger than expected:** 170+ total callers across the codebase.

**Production code (10 callers in 2 files):**
- `game/ai/controller.py` - 5 calls (including chained: `own_ship.formation_master.formation_members.remove(own_ship)`)
- `game/ui/services/ship_factory.py` - 5 calls (writes: setting master, members, offset, rotation_mode)

**Adapter layer (6 methods):**
- `game/ai/interfaces/controllable.py:421-443` - All 6 methods use backward compat properties

**Test code (155+ callers across 20+ files):**
- Heaviest usage in: `test_formation_behavior.py`, `test_ai_controller_interface.py`, `conftest.py` fixtures

**Special: test_ship_formation.py explicitly tests the backward compat properties** - these tests must be removed/rewritten.

### Constant Re-exports Analysis (Agent 4)

**Path constants:** 23 files import from `game.core.constants` instead of `game.core.paths`
**WIDTH/HEIGHT:** 2 files (`test_lab_screen.py`, `test_lab.py`)
**LayerType split:** 34 files use canonical `game.core.constants`, **24 files still use deprecated** `game.simulation.components.component_constants`

**Note:** LayerType has MORE legacy callers (24) than the earlier estimate (19). Additional callers found in `test_framework/`, `tests/unit/entities/`, `tests/unit/systems/`, etc.

### BattleController & Collision Analysis (Agent 5)

**BattleController properties (tests only):**
- `controller.engine` - 2 test callers
- `_retreating_ships` - 4 test callers
- `_escaped_ships` - 3 test callers + 1 internal (already accesses manager directly)

**BattleController fallback logic:**
- `_retreat_allowed()` - OR pattern: `mode_handler.can_retreat() or config.allow_retreat`
- `_reinforcements_allowed()` - OR pattern: `mode_handler.can_reinforce() or config.allow_reinforcements`
- `apply_results_to_fleets()` - Legacy fallback **BLOCKED by PROJ-41**

**Collision fallback:**
- `total_defense_score` is ALWAYS present on Ship (initialized to 1.0 at line 168)
- `get_total_ecm_score()` returns only ECM component (incomplete - missing size/maneuver)
- Fallback logs warning and returns wrong results if triggered
- All collision targets are Ship instances

**Workshop proxies (CORRECTED):**
- `self.ship` used 11 times within `workshop_screen.py`
- `self.selected_components` used 3 times
- `self.available_components` used 1 time (broken - writes to read-only property)
- No EXTERNAL callers

### Registry DI Analysis (Agent 6)

**Production callers of `get_default_registries()` (6 files):**
1. `ShipFactory.create_ship_from_design()` - line 72 (has registries param, fallback)
2. `DesignLoaderAdapter.__init__()` - line 42 (has registries param, fallback)
3. `StrategyScreen` event handler - line 370 (**HARDCODED - no param option**)
4. `TurnEngine.__init__()` - line 128 (try/except with RegistryManager fallback)
5. `ShipInstance.get_calculated_stats()` - line 196 (try/except with RegistryManager fallback)
6. `WorkshopContext.__post_init__()` - line 78 (try/except with disk-load fallback)

**DI chain from app.py:**
```
Game.__init__() → set_default_registries(self.registries)
├── start_builder() → WorkshopContext → get_default_registries() [fallback]
│   └── DesignLoaderAdapter → get_default_registries() [fallback]
├── start_strategy_layer() → GameSession → StrategyScreen
│   └── StrategyScreen:370 → get_default_registries() [HARDCODED]
│   └── TurnEngine → get_default_registries() [fallback]
│       └── ShipInstance → get_default_registries() [fallback]
```

---

## Key Patterns to Reuse

- **Strict DI Pattern** (PROJ-50): `Ship.__init__(registries=GameRegistries)` - raise TypeError if None
- **Paths class access**: `from game.core.paths import Paths; Paths.ROOT_DIR`
- **Direct formation access**: `ship.formation.master`, `ship.formation.offset`
- **Direct engine access**: `ship.combat_engine.take_damage()`

---

## Dependencies & Risks

1. **ShipCombatMixin `die()` method** has real logic - must be relocated before deletion
2. **Formation chained call** `own_ship.formation_master.formation_members.remove(own_ship)` → becomes `own_ship.formation.master.formation.members.remove(own_ship)`
3. **155+ test file edits for formation** - mechanical but high volume, risk of typos
4. **StrategyScreen:370 hardcoded call** - only DI callsite with NO parameter option, needs refactor
5. **`apply_results_to_fleets()` CANNOT be removed** - blocked by PROJ-41

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

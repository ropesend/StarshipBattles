# PROJ-49: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Phase A: Understanding Findings
Explored the codebase with 3 agents to validate issues from `findings_08_performance_dead_code.md`:
- **Performance hot paths**: All PERF-01 to PERF-10 issues confirmed in code
- **Dead code/duplicates**: Confirmed which are truly dead vs still active
- **Import validation**: DC-01, UI-002, UI-003 are NOT broken - imports work via launcher.py

### Key Discovery: Imports Work
The findings document listed broken imports in `app.py` and `workshop_screen.py`. Investigation revealed:
- `launcher.py` adds project root to `sys.path`
- Both `Tools/` and `ui/` directories have `__init__.py` files
- All imports resolve correctly at runtime
- These issues are **excluded from scope**

## Swarm Findings Summary

### Architecture Analysis
- **Clean layer separation**: simulation -> core/engine only, UI -> reads from simulation
- **No circular dependencies** detected in any module relationships
- **Hot path**: `BattleEngine.update()` -> AI targeting -> Ship stats -> Projectile collision
- **Dual code paths** for AI creation in battle_engine.py (legacy + PROJ-17 pattern)

### Directory Structure
```
game/
├── core/              <- Foundational (constants, math, config, logging)
├── engine/            <- Physics & spatial (collision, spatial grid)
├── simulation/        <- CORE HOT PATH (battle engine, entities)
│   ├── systems/       <- Battle tick logic (battle_engine.py)
│   ├── entities/      <- Ship, components, projectiles
│   ├── components/    <- Component system & abilities
│   └── services/      <- Battle service, loaders
├── ai/                <- Decision making (targeting, behaviors)
├── ui/                <- Visual presentation layer
└── strategy/          <- Strategy layer (separate from simulation)

ui/  <- Outside game package (active via launcher.py path setup)
Tools/ <- Outside game package (active via launcher.py path setup)
```

### Key Patterns to Reuse

- **Property caching**: `ship.py:98-102` - Use `_cached_` prefix with @property
- **Deferred deletion**: `projectile_manager.py:124-132` - Collect indices in set, rebuild after loop
- **Service DI pattern**: `ship_stats_service.py:41-85` - Constructor accepts optional registries
- **Validation results**: Return `ValidationResult(is_valid, errors)` not just bool
- **Thread-safe singleton**: `asset_manager.py:24-49` - Double-checked locking with `_lock`

### Dependencies & Risks

1. **Cache invalidation bugs** - Must invalidate on ALL state changes (add_component, remove_component, recalculate_stats)
2. **Combat regression** - CCD algorithm edge cases at extreme velocities; missile interception uses fragile isinstance check
3. **Save/load mismatch** - Cached values not currently serialized; verify consistency after optimization
4. **Ability indexing** - Multiple abilities of same type indexed by class name only; may need slot-based indexing
5. **Test impact** - `component.py` changes affect 169+ test files (CRITICAL)

### Opportunities Discovered

- Existing spatial grid infrastructure can support incremental updates
- Formula system is properly secured (SIM-021 can be skipped)
- Weapon recalculate() method is disabled with `pass` - can be enabled as part of optimization
- Some tests already cover edge cases we'll need (test_collision_edge_cases.py)

## Performance Analysis

### Battle Tick Flow (60 Hz target)
```
BattleEngine.update()
  1. Rebuild spatial grid O(n)
  2. Update AI & Ships O(ships * enemies * rules * components)
  3. Process New Attacks O(attacks)
  4. Ramming Collisions O(collisions)
  5. Update Projectiles O(projectiles * nearby_ships)
```

### Issue Priority Matrix

| ID | Issue | Severity | Effort | Phase |
|---|---|---|---|---|
| PERF-02 | Projectile list reconstruction | CRITICAL | Simple | 2 |
| PERF-01 | Component list allocation | CRITICAL | Medium | 3 |
| PERF-05 | Ability MRO lookup | HIGH | Simple | 2 |
| PERF-03 | O(n^2) targeting | HIGH | Medium | 6 |
| PERF-08 | HP ratio division | MEDIUM | Medium | 4 |
| PERF-06 | Spatial grid rebuild | MEDIUM | Complex | 5 |

### Dead Code Summary

| File | Status | Evidence |
|---|---|---|
| `game/simulation/systems/projectile_manager.py` | DEAD | Never imported, root version used |
| `game/ui/screens/setup.py` | DEAD | app.py imports setup_screen.py |
| `_ValidatorProxy` (ship.py:29-34) | DEAD | VALIDATOR constant never referenced |
| `ui/test_lab_scene.py.backup` | DEAD | Backup file in repo |
| `_marked_for_deletion_2026-01-27/` | DEAD | Stale deletion directory |

### NOT Dead Code (Initially Suspected)

| Issue | Status | Evidence |
|---|---|---|
| DC-01 (app.py imports) | WORKING | launcher.py adds paths to sys.path |
| UI-002, UI-003 (ui.builder imports) | WORKING | ui/ has __init__.py, path setup works |
| SIM-021 (formula eval) | SECURE | AST validation + restricted builtins |

## Phase 5 Research Findings

### Spatial Grid Profiling Results (2026-01-30)

Ran `profile_simulation.py` with 50 ships for 500 ticks to measure actual overhead:

**Full Battle Simulation (17.6 seconds total):**
- Spatial grid methods (`clear`, `insert`, `_get_cell`) did NOT appear in top 30 functions
- Top bottlenecks were:
  1. `typing.py:1408(_get_protocol_attrs)` - 4.06s (Protocol isinstance checks)
  2. `controller.py:381(check_avoidance)` - 0.64s + 10.5s cumulative (AI collision avoidance)
  3. `ability_manager.py:29(get_abilities)` - 0.94s (Ability lookups)

**Isolated Grid Profiling (50 ships x 1000 ticks):**
- Total time: **0.020 seconds** (20 milliseconds for 1000 ticks)
- Per-tick overhead: ~20 microseconds for 50 ships
- `insert()`: 0.011s | `_get_cell()`: 0.007s | `clear()`: 0.000s

### Analysis

The spatial grid is already highly optimized:
- Simple dict-based bucket system with O(1) cell lookup
- `clear()` just replaces dict with empty dict - nearly free
- `insert()` is single dict access + list append
- Current overhead is **0.1%** of total tick time

Incremental updates would add:
- Position tracking dict (`object_cells`)
- Old cell lookup + comparison per object
- Set operations instead of list append
- Memory overhead for tracking

**Estimated savings: ~10 microseconds per tick**
**Implementation complexity: Medium (edge cases with object removal, new objects)**
**Risk: Bugs in cell tracking could cause collision detection failures**

### Decision: Skip Incremental Grid Updates

The cost/benefit ratio is unfavorable:
1. Current grid overhead is negligible (~0.1% of tick time)
2. Real bottlenecks are protocol isinstance checks and AI collision avoidance
3. Implementation would add complexity with minimal measurable improvement
4. Risk of subtle bugs outweighs microscopic performance gain

**Recommendation:** Mark Phase 5 complete with research-only outcome. If future profiling shows grid as bottleneck (e.g., with 500+ ships), revisit then.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

### Summary of Key Decisions
1. **Dead code first, performance second** - Quick wins clean codebase
2. **Archive before delete** - User preference for safety
3. **Skip secure eval()** - Formula system already properly sandboxed
4. **Skip "broken" imports** - Investigation proved they work

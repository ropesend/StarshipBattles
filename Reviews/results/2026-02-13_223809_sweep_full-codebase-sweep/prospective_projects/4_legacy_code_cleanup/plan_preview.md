# PROJ-XXX: Legacy Code Cleanup

## Project Goal
Eradicate legacy system holdovers, backward compatibility shims, and dead code paths per project policy: "When a new system replaces an old one, ERADICATE the old system completely."

## Current State
- GameSession has O(n) fallback iteration "for backward compatibility with tests"
- FleetOrderProcessor has dual behavior based on whether registry is None
- ProductionEngine has two production systems (legacy turn-based vs tick-based)
- BattleController has dead fallback methods documented as "not used in production"
- Multiple defensive hasattr/getattr checks for always-present attributes

## Target State
- Single code path for all operations
- No "backward compatibility" comments in codebase
- All legacy fallbacks removed
- Tests use proper fixtures instead of triggering fallback paths

---

## Phase 1: Simulation Layer Cleanup
**Status:** Not Started

### Tasks
- [ ] 1.1 Delete `_apply_results_to_fleet()` method from BattleController
- [ ] 1.2 Remove fallback block in `apply_results_to_fleets()`
- [ ] 1.3 Audit ability_manager module identity drift issue
- [ ] 1.4 Document decision on LEG-SIM-001 (fix or accept as tech debt)
- [ ] 1.5 Review ComponentCacheManager singleton (document or plan refactor)
- [ ] 1.6 Clean up stale docstrings in modifier_service.py
- [ ] 1.7 Clean up stale docstrings in vehicle_design_service.py
- [ ] 1.8 Remove hasattr checks for guaranteed attributes
- [ ] 1.9 Run test suite

### Files Affected
- `game/simulation/battle_controller.py`
- `game/simulation/components/ability_manager.py`
- `game/simulation/services/modifier_service.py`
- `game/simulation/services/vehicle_design_service.py`

---

## Phase 2: Strategy Layer Cleanup
**Status:** Not Started

### Tasks
- [ ] 2.1 Update tests that don't register fleets with galaxy
- [ ] 2.2 Remove fallback iteration in GameSession._get_fleet_by_id()
- [ ] 2.3 Ensure component_registry is always provided to FleetOrderProcessor
- [ ] 2.4 Remove None-handling legacy branches in process_colonize()
- [ ] 2.5 Remove backward compat default in Planet.from_dict() populations
- [ ] 2.6 Audit callers of project_path_as_dicts()
- [ ] 2.7 Migrate callers to use project_path() returning PathSegment
- [ ] 2.8 Remove project_path_as_dicts() wrapper
- [ ] 2.9 Ensure all queue items have cost_per_tick
- [ ] 2.10 Remove legacy production item handling
- [ ] 2.11 Remove unused StarType import from galaxy.py
- [ ] 2.12 Remove sprite_preview placeholder field
- [ ] 2.13 Fix misleading "backward compatibility" comments
- [ ] 2.14 Make DesignMetadata reject old format instead of warning
- [ ] 2.15 Run test suite

### Files Affected
- `game/strategy/engine/game_session.py`
- `game/strategy/engine/fleet_order_processor.py`
- `game/strategy/data/planet.py`
- `game/strategy/services/fleet_navigation_service.py`
- `game/strategy/engine/production_engine.py`
- `game/strategy/data/galaxy.py`
- `game/strategy/data/design_metadata.py`
- `game/strategy/data/race_config.py`
- `game/strategy/engine/game_config.py`

---

## Phase 3: Foundation/AI Cleanup
**Status:** Not Started

### Tasks
- [ ] 3.1 Audit getattr() fallbacks in ai/combat_utils.py
- [ ] 3.2 Replace with direct attribute access where safe
- [ ] 3.3 Remove unused error codes from error_codes.py
- [ ] 3.4 Remove defensive hasattr checks in controllable.py
- [ ] 3.5 Document intentional fallback patterns (LEG-FND-007)
- [ ] 3.6 Run test suite

### Files Affected
- `game/ai/combat_utils.py`
- `game/core/error_codes.py`
- `game/ai/interfaces/controllable.py`

---

## Phase 4: UI Layer Cleanup
**Status:** Not Started

### Tasks
- [ ] 4.1 Convert ship_io.py Tkinter init to lazy pattern
- [ ] 4.2 Verify BattleOrchestrator is unused
- [ ] 4.3 Remove BattleOrchestrator or document its purpose
- [ ] 4.4 Remove WHITE and BLACK dead color constants
- [ ] 4.5 Run test suite
- [ ] 4.6 Final audit for remaining legacy patterns
- [ ] 4.7 Search for remaining "backward" comments

---

## Success Metrics
- [ ] Zero "backward compatibility" comments (except documented decisions)
- [ ] GameSession uses only registry lookup
- [ ] FleetOrderProcessor requires component_registry
- [ ] No dead code paths remaining
- [ ] All tests passing
- [ ] grep for "fallback" returns only legitimate patterns

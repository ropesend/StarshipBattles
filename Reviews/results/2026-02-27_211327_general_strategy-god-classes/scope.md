# Review Scope: Strategy God Classes

## Metadata
- **Date:** 2026-02-27
- **Type:** General Review
- **Description:** God class accumulation in strategy domain models (Fleet, Planet)

## Scope Definition

### Target
- [x] Specific directory: `game/strategy/` (extended scope — Fleet/Planet + related files)

### Files in Scope (~9,250 lines, 33 files)

**Core God Class Candidates:**
- `game/strategy/data/fleet.py` (552 lines)
- `game/strategy/data/planet.py` (499 lines)
- `game/strategy/data/ship_instance.py` (741 lines)

**Existing Delegates & Helpers:**
- Fleet delegates: fleet_resource_aggregator.py, fleet_capability_calculator.py, fleet_battle_adapter.py
- Planet helpers: planet_atmosphere.py, planet_physics.py, planet_naming.py, planet_gen.py
- Ship delegates: ship_cargo_manager.py, ship_resource_manager.py, ship_display_formatter.py

**Services, Engines & Supporting Files:**
- Fleet services/engines: fleet_navigation_service.py, fleet_order_processor.py, fleet_movement_engine.py, fleet_speed_calculator.py, fleet_cargo_projector.py
- Planet engines: harvesting_engine.py, population_engine.py, resupply_engine.py
- Shared: cargo_transfer_service.py, action_time_resolver.py, colonize_validator.py
- Build: build_queue_source.py, build_context.py
- DTOs: fleet_dto.py, planet_dto.py
- Other: pathfinding.py, empire.py, design_metadata.py, habitability.py

### Priorities
1. God class pattern identification — pass-through methods, mixed concerns, monolithic classes
2. Serialization complexity — especially Fleet.from_dict polymorphic order parsing
3. Responsibility boundary violations
4. Refactoring opportunity identification — extraction targets and patterns
5. Existing decomposition assessment — are PROJ-87 delegates effective?

### Exclusions
- UI layer files (game/ui/)
- Test files
- Third-party/generated code

## Agent Configuration
**Recommended Agents:** 5
**Confirmed Agent Count:** 5

### Selected Agents
| Agent | Role | Status |
|-------|------|--------|
| Code Quality Analyst | God class metrics, complexity, DRY, proxy bloat | Launched |
| Architecture Reviewer | Responsibility boundaries, coupling, layer violations | Launched |
| Refactoring Opportunity Finder | Extraction targets, decomposition patterns | Launched |
| Complexity Analyst | Serialization complexity, branching, API surface | Launched |
| Dead Code Hunter | Unused pass-throughs, orphaned helpers, dead imports | Launched |

## Notes
- PROJ-87 (Strategy Data Tier) already planned some decomposition
- Facade/delegate pattern is the agreed extraction approach
- ~7,353 tests passing baseline

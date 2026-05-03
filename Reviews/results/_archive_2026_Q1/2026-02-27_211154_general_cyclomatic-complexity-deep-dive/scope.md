# Review Scope: Cyclomatic Complexity Deep Dive

## Metadata
- **Date:** 2026-02-27
- **Type:** General Review (Complexity Focus)
- **Reviewer:** Code Review Coordinator

## Target Scope
Four critically complex functions identified by Radon static analysis (all Rank D):

| Function | File | CC Score |
|----------|------|----------|
| `_process_queue_tick_dynamic` | `game/strategy/engine/production_engine.py` | 27 |
| `calculate_stats` | `game/strategy/services/ship_stats_calculator.py` | 26 |
| `load_game` | `game/strategy/systems/save_game_service.py` | 26 |
| `project_path` | `game/strategy/services/fleet_navigation_service.py` | 22 |

**Total scope:** 4 files, ~2,237 lines of code

## Review Goal
Validate proposed decomposition strategies for each function. Specifically:
1. Are the proposed decomposition strategies sound?
2. Do they target the real complexity drivers?
3. Are there gaps or missed opportunities?
4. What test coverage exists, and what must be preserved?
5. What is the recommended implementation ordering?

## Proposed Decomposition Strategies (User-Provided)

### 1. ProductionEngine._process_queue_tick_dynamic (CC=27)
- Extract `_validate_queue_item(item, colony_or_fleet, galaxy, is_complex_only)`
- Extract `_calculate_tick_expenditure(item, tick_capacity, production_rate)`
- Extract `_apply_production_progress(item, ticks_to_spend, production_rate)`

### 2. ShipStatsCalculator.calculate_stats (CC=26)
- Extract `_initialize_base_stats(design_data, vehicle_classes)`
- Extract `_accumulate_component_stats(components, modifiers, damage)`
- Registry of Policy objects (MassCalculator, HpCalculator, ResourceStorageCalculator)

### 3. SaveGameService.load_game (CC=26)
- Extract `_load_save_metadata(save_path)`
- Extract `_load_turn_data(save_path, turn_number)`
- Extract `_reconstruct_game_session(game_state, save_path)`

### 4. FleetNavigationService.project_path (CC=22)
- Extract `_project_action_order(state, order, moves_left_in_turn, turns_left)`
- Extract `_resolve_path_for_order(state, order, galaxy)`
- Extract `_advance_tick(state)`

## Agent Configuration
**Confirmed Agent Count:** 5

### Selected Agents
| # | Agent | Role | Finding Prefix | Status |
|---|-------|------|----------------|--------|
| 1 | Complexity Analyst | CC drivers, branching analysis | CX | Pending |
| 2 | Architecture Reviewer | Coupling, interfaces, layer boundaries | AR | Pending |
| 3 | Code Quality Analyst | SOLID, readability, naming | CQ | Pending |
| 4 | Test Coverage Analyst | Existing tests, coverage gaps | TC | Pending |
| 5 | Decomposition Strategist | Validate & refine proposed strategies | DS | Pending |

## Exclusions
None — review everything related to these 4 functions.

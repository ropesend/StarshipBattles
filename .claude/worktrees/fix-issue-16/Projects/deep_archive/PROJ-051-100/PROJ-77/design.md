# PROJ-77: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Strategy Layer Structure
The strategy layer has a clean three-layer architecture:
- **UI Layer**: StrategyScreen, StrategyUI (pygame_gui based)
- **Facade Layer**: StrategySessionFacade (CQRS-lite pattern, returns DTOs)
- **Engine Layer**: TurnEngine orchestrating sub-engines (ProductionEngine, FleetOrderProcessor, ConflictResolutionEngine, etc.)

### Turn Processing Flow
TurnEngine.process_turn() orchestrates:
1. Per-tick processing (100 ticks per turn):
   - Phase 0: Resource consumption
   - Phase 1: Instant orders (fleet join)
   - Phase 2-3: Movement calculation & application
   - Phase 4: Combat resolution
2. End-of-turn orders (colonize, transfer)
3. Production phase (ships, complexes)
4. Fleet production
5. Population growth

### Existing Event Patterns
- `game/core/logger.py` has `set_event_handler()` and `log_event()` - structured event logging
- `game/ui/screens/builder/event_bus.py` - pub/sub EventBus pattern
- `game/research/data/research_tracker.py` - turn_log pattern for turn-based events

### Key Finding: No Centralized Event System
Events are currently scattered as `log_info()` calls throughout engines. The new system will use the existing `log_event()` callback to capture structured events.

---

## Swarm Findings Summary

### Architecture Analysis
- TurnEngine at `game/strategy/engine/turn_engine.py:193-220` is the central orchestrator
- GameSession at `game/strategy/engine/game_session.py` owns TurnEngine and all game state
- StrategySessionFacade provides clean abstraction for UI
- Dependency injection is used throughout (engines are injectable)

### Key Patterns to Reuse
- **Logger Event Handler**: `game/core/logger.py:89-109` - `set_event_handler()` callback pattern
- **Serialization**: `game/research/data/research_tracker.py:236-255` - `to_dict()`/`from_dict()` pattern
- **Modal Window**: `game/ui/screens/fleet_orders_window.py:13-141` - UIWindow subclass pattern
- **Scrollable List**: `game/ui/screens/planet_list_window.py:133-147` - UIScrollingContainer
- **Filter Buttons**: `game/ui/screens/planet_list_sidebar.py:74-98` - toggle button pattern
- **Top Bar Button**: `game/ui/screens/strategy_ui.py:186-262` - button creation in top bar

### Dependencies & Risks
1. **Save/Load Compatibility**: New `event_log` field added to GameSession serialization - old saves will load with empty event log (graceful degradation via `data.get('event_log', {'events': []})`)
2. **Logger Global State**: `set_event_handler()` uses global callback - only one handler active at a time. GameSession should set handler on init and clear on cleanup.
3. **Event Volume**: Large games may accumulate many events. Consider max_events limit in future if performance becomes an issue.

### Opportunities Discovered
- Existing engines already return result objects (ConflictResult) - extend this pattern
- EventBus exists in builder UI - could potentially be reused for inter-component communication
- ResearchTracker's turn_log pattern is a good model for turn-based event storage

---

## Data Flow

```
Engines (ProductionEngine, FleetOrderProcessor, ConflictResolutionEngine)
    │
    ├── Call: log_event("event_type", category="...", message="...", ...)
    │
    ▼
Logger (game/core/logger.py)
    │
    ├── Invokes registered event_handler callback
    │
    ▼
GameSession._create_event_handler() callback
    │
    ├── Creates Event object with turn number, empire_id, message, details
    ├── Appends to self._event_log
    │
    ▼
EventLog (persisted with GameSession.to_dict())
    │
    ├── Serialized with game save
    ├── Restored on game load
    │
    ▼
StrategySessionFacade.get_turn_events()
    │
    ├── Returns List[Dict] (immutable DTOs for UI)
    │
    ▼
EventLogWindow (UI Modal)
    │
    ├── Displays events with filter tabs
    └── Shown at turn start or via "Log" button
```

---

## Event Types

| Event Type | Category | Emitting Engine | Key Details |
|------------|----------|-----------------|-------------|
| ship_built | production | ProductionEngine._spawn_ship() | design_id, planet_id, fleet_id |
| complex_built | production | ProductionEngine._spawn_complex() | design_id, planet_id |
| colony_founded | colonies | FleetOrderProcessor.process_colonize() | planet_id, planet_name, fleet_id |
| combat_resolved | combat | ConflictResolutionEngine | location, winner_fleet_id, loser_fleet_id |

---

## UI Layout

```
┌─────────────────────────────────────────────────────────────┐
│ Event Log                                               [X] │
├─────────────────────────────────────────────────────────────┤
│ [All] [Combat] [Production] [Colonies]                      │
├─────────────────────────────────────────────────────────────┤
│ ⚙ Built Scout at Earth                           Turn 5    │
│ ⚔ Battle at (5,3): Fleet 7 victorious            Turn 5    │
│ 🌍 Founded colony on Mars                        Turn 4    │
│ ⚙ Built Frigate at Luna                          Turn 3    │
│ ...                                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

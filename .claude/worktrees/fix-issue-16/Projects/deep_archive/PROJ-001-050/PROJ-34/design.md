# PROJ-34: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

**Origin:** Code Review finding - "Logic Leaking into UI (StrategyScene)" - High Severity

The `StrategyScene` class violates separation of concerns by directly accessing deep simulation state:
- Direct property access: `self.session.galaxy`, `self.session.turn_engine`
- Logic execution: Calls `calculate_hybrid_path` directly
- State mutation: While it delegates some actions to extracted modules, those modules still directly manipulate domain objects

**Existing Architecture:**
- `StrategyScene` was already refactored from 1,568 lines to ~530 lines
- Extracted modules: `FleetOperations`, `ColonizationSystem`, `InputHandler`, `CameraNavigator`
- A **Command Pattern foundation exists** in `game/strategy/engine/commands.py` with 3 commands
- `GameSession.handle_command()` already dispatches commands

**The Problem:**
The extracted modules still have tight coupling:
- `FleetOperations` directly mutates `fleet.add_order()` for intercepts
- `ColonizationSystem` directly calls `turn_engine.validate_colonize_order()`
- `ColonizationSystem` directly sets `fleet.path = path` and `fleet.add_order()`

## Swarm Findings Summary

### Architecture

**Current Flow:**
```
UI Input → InputHandler → FleetOperations/ColonizationSystem
                              ↓
                    Direct session access
                    Direct fleet mutation
                              ↓
                    GameSession (sometimes)
```

**Target Flow (CQRS-lite):**
```
UI Input → StrategySessionFacade
                    ↓
        ┌──────────┴──────────┐
        │                     │
    Commands              Queries
    (mutations)          (DTOs only)
        │                     │
        ↓                     ↓
   GameSession           DTO Factory
   handle_command()      (immutable)
```

### Key Patterns to Reuse

- **Command Pattern**: `game/strategy/engine/commands.py` - Extend existing commands
- **ValidationResult**: `game/core/validation.py` - Use for command responses
- **Interface segregation**: `game/strategy/interfaces/battle_resolver.py` - Pattern for facades
- **Adapter Pattern**: `game/strategy/adapters/simulation_adapter.py` - Bridges layers

### Dependencies & Risks

1. **Path calculation logic in ColonizationSystem** - Must migrate `queue_colonize_mission()` logic to GameSession handler carefully
2. **Fleet order manipulation** - Multiple places directly call `fleet.add_order()`
3. **Test coverage** - Existing tests mock `session` directly; may need updates

### Opportunities Discovered

- Facade creates clear API boundary for future language port
- DTOs enable UI layer to be ported with minimal changes
- Command/query separation improves testability

## Target Architecture

### StrategySessionFacade

**Purpose:** Single point of access for all UI↔Engine communication

**Interface:**
```python
class StrategySessionFacade:
    def __init__(self, session: GameSession): ...

    # Commands (write path)
    def handle_command(self, command: Command) -> ValidationResult: ...
    def process_turn(self) -> None: ...

    # Queries (read path - return DTOs only)
    def get_fleet(self, fleet_id: int) -> Optional[FleetInfo]: ...
    def get_fleets_at_hex(self, hex_coord: HexCoord) -> List[FleetInfo]: ...
    def get_fleet_path_preview(self, fleet_id: int, target_hex: HexCoord) -> Optional[List[HexCoord]]: ...
    def get_all_systems(self) -> List[SystemInfo]: ...
    def get_system_at_hex(self, hex_coord: HexCoord) -> Optional[SystemInfo]: ...
    def get_planet(self, planet_id: int) -> Optional[PlanetInfo]: ...
    def get_all_empires(self) -> List[EmpireInfo]: ...
    def get_empire(self, empire_id: int) -> Optional[EmpireInfo]: ...
    def get_empire_colonies(self, empire_id: int) -> List[ColonySummary]: ...
    def get_empire_fleets(self, empire_id: int) -> List[FleetSummary]: ...
    def get_human_player_ids(self) -> List[int]: ...
    def get_turn_number(self) -> int: ...
    def can_colonize(self, fleet_id: int, planet_id: Optional[int]) -> ValidationResult: ...
```

### DTOs (Immutable)

All DTOs use `@dataclass(frozen=True)` for immutability.

**FleetInfo:** `fleet_id`, `owner_id`, `location`, `speed`, `ship_count`, `ships`, `orders`, `has_orders`, `projected_path`

**SystemInfo:** `name`, `global_location`, `primary_star`, `planet_count`, `warp_point_count`, `colony_count`

**PlanetInfo:** `planet_id`, `name`, `planet_type`, `location`, `owner_id`, `is_colonized`, `has_space_shipyard`

**EmpireInfo:** `empire_id`, `name`, `color`, `theme_id`, `flag_id`, `colony_count`, `fleet_count`

### New Commands

| Command | Purpose |
|---------|---------|
| `IssueInterceptCommand(fleet_id, target_fleet_id)` | Intercept/follow another fleet |
| `IssueJoinFleetCommand(fleet_id, target_fleet_id)` | Merge into another fleet |
| `QueueColonizeMissionCommand(fleet_id, target_hex, planet_id)` | Queue MOVE + COLONIZE |
| `ClearFleetOrdersCommand(fleet_id)` | Clear all orders from fleet |

## File Organization

### New Files

```
game/strategy/facade/
    __init__.py
    strategy_session_facade.py
    dto/
        __init__.py
        fleet_dto.py
        system_dto.py
        planet_dto.py
        empire_dto.py
```

### Modified Files

- `game/strategy/engine/commands.py` - Add 4 new command classes
- `game/strategy/engine/game_session.py` - Add 4 new command handlers
- `game/ui/screens/strategy_scene.py` - Create and use facade
- `game/ui/screens/strategy_fleet_ops.py` - Use facade, remove direct mutation
- `game/ui/screens/strategy_colonization.py` - Use facade, remove direct mutation
- `game/ui/screens/strategy_camera_nav.py` - Use facade for queries

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

**Key Decisions:**
1. **Strict Facade** over Commands-Only - Better portability for future language port
2. **Frozen DTOs** - Prevent accidental state mutation from UI
3. **Keep turn processing as direct call** - It's a lifecycle event, not a player action
4. **Add all new command types** - Complete coverage for all UI operations

---

## Final Implementation Summary

### Implemented Components

**Facade (`game/strategy/facade/strategy_session_facade.py`):**
- Full CQRS-lite pattern implemented
- Commands delegated to `GameSession.handle_command()`
- Queries return immutable DTOs
- Validation queries (`can_colonize`, `can_move_to`)

**DTOs (`game/strategy/facade/dto.py`):**
- `FleetInfo` - frozen dataclass with `from_fleet()` factory
- `SystemInfo` - frozen dataclass with `from_star_system()` factory
- `PlanetInfo` - frozen dataclass with `from_planet()` factory
- `EmpireInfo` - frozen dataclass with `from_empire()` factory
- `ColonySummary`, `FleetSummary` - lightweight summaries for lists

**Commands (`game/strategy/engine/commands.py`):**
- `IssueInterceptCommand` - follow/intercept another fleet
- `IssueJoinFleetCommand` - queue move + join orders
- `QueueColonizeMissionCommand` - queue move + colonize mission
- `ClearFleetOrdersCommand` - clear fleet order queue

**Handlers (`game/strategy/engine/game_session.py`):**
- `_handle_intercept_command` - validates and creates MOVE_TO_FLEET order
- `_handle_join_command` - validates ownership and queues move + join
- `_handle_colonize_mission_command` - calculates path, queues move + colonize
- `_handle_clear_orders_command` - clears orders and path

**Refactored UI Modules:**
- `FleetOperations` - uses facade for execute_move, execute_intercept, handle_join_designation
- `ColonizationSystem` - uses facade for on_colonize_click, issue_colonize_order, queue_colonize_mission
- `StrategyScene` - creates facade, passes to modules, turn processing via facade

### Deviations from Original Plan

1. **CameraNavigator kept as-is**: Read-only access for navigation purposes was acceptable. Using facade DTOs would break camera positioning since actual objects are needed.

2. **Deprecated properties approach**: Only `turn_engine` has deprecation warning (the primary coupling issue). Other properties (`galaxy`, `empires`, `systems`) kept without warnings as they're needed for rendering.

3. **DTO file structure**: Single `dto.py` file instead of separate files per DTO type (simpler, all DTOs are small).

### Lessons Learned

1. **Integration tests are essential**: Unit tests with mocks can miss integration issues. The facade integration tests caught fixture problems that unit tests didn't.

2. **Fleet creation in GameSession**: Discovered that `GameSession._setup_initial_scenario()` only creates colonies, not starting fleets. Tests need to inject fleets manually.

3. **Pathfinding behavior**: `find_hybrid_path` returns a path even to far locations (uses direct hex path as fallback), so "unreachable" validation relies on other checks.

4. **Type hints with TYPE_CHECKING**: Using `if TYPE_CHECKING:` for circular import prevention is a clean pattern for facade references.

5. **Optional parameters need explicit handling**: User playtesting found that `QueueColonizeMissionCommand` crashed when the planet selection dialog was cancelled (planet=None). The fix was to make `planet_id` Optional and treat None as "colonize any available planet".

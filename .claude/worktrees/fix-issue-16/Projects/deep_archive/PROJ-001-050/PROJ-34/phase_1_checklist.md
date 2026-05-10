# Phase 1: Foundation - DTOs and Facade Structure

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-34 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create the DTO classes and facade skeleton

---

## Tasks

### Task 1.1: Create DTO Directory Structure [Simple]
**Files:** New directory `game/strategy/facade/dto/`
**Tests:** N/A (structure only)

- [x] Create `game/strategy/facade/` directory
- [x] Create `game/strategy/facade/__init__.py`
- [x] Create `game/strategy/facade/dto/` directory
- [x] Create `game/strategy/facade/dto/__init__.py`

**Notes:** Created directory structure and __init__.py files with appropriate module docstrings.

---

### Task 1.2: Implement Fleet DTOs [Medium]
**File:** `game/strategy/facade/dto/fleet_dto.py`
**Tests:** `pytest tests/strategy/facade/test_fleet_dto.py`

- [x] Create `FleetOrderInfo` frozen dataclass:
  ```python
  @dataclass(frozen=True)
  class FleetOrderInfo:
      order_type: str  # "MOVE", "COLONIZE", "MOVE_TO_FLEET", "JOIN_FLEET"
      target_description: str
      target_hex: Optional[HexCoord] = None
      target_id: Optional[int] = None
  ```
- [x] Create `ShipInfo` frozen dataclass:
  ```python
  @dataclass(frozen=True)
  class ShipInfo:
      instance_id: str
      name: str
      design_id: str
      ship_class: str
      is_combat_capable: bool
      current_hp_percent: float  # 0.0-1.0
  ```
- [x] Create `FleetInfo` frozen dataclass:
  ```python
  @dataclass(frozen=True)
  class FleetInfo:
      fleet_id: int
      owner_id: int
      location: HexCoord
      speed: float
      ship_count: int
      ships: List[ShipInfo] = field(default_factory=list)
      orders: List[FleetOrderInfo] = field(default_factory=list)
      has_orders: bool = False
      can_use_warp: bool = False
      projected_path: List[HexCoord] = field(default_factory=list)
  ```
- [x] Implement `FleetInfo.from_fleet(fleet: Fleet) -> FleetInfo` factory method
- [x] Write unit tests for factory method

**Notes:** Implemented all frozen dataclasses with factory method. 14 tests in test_fleet_dto.py - all passing.

---

### Task 1.3: Implement System/Planet DTOs [Medium]
**Files:** `game/strategy/facade/dto/system_dto.py`, `game/strategy/facade/dto/planet_dto.py`
**Tests:** `pytest tests/strategy/facade/test_system_dto.py`

- [x] Create `StarInfo` frozen dataclass:
  ```python
  @dataclass(frozen=True)
  class StarInfo:
      name: str
      star_type: str
      color: Tuple[int, int, int]
      location: HexCoord
  ```
- [x] Create `WarpPointInfo` frozen dataclass:
  ```python
  @dataclass(frozen=True)
  class WarpPointInfo:
      destination_system_name: str
      location: HexCoord
  ```
- [x] Create `SystemInfo` frozen dataclass:
  ```python
  @dataclass(frozen=True)
  class SystemInfo:
      name: str
      global_location: HexCoord
      primary_star: Optional[StarInfo] = None
      planet_count: int = 0
      warp_point_count: int = 0
      colony_count: int = 0
  ```
- [x] Create `PlanetInfo` frozen dataclass:
  ```python
  @dataclass(frozen=True)
  class PlanetInfo:
      planet_id: int
      name: str
      planet_type: str
      location: HexCoord
      orbit_distance: int
      owner_id: Optional[int] = None
      is_colonized: bool = False
      has_space_shipyard: bool = False
  ```
- [x] Implement factory methods for each DTO

**Notes:** Implemented all DTOs with factory methods. SystemInfo.from_star_system and PlanetInfo.from_planet convert domain objects. StarInfo.from_star also added. 18 tests in test_system_dto.py - all passing.

---

### Task 1.4: Implement Empire DTOs [Simple]
**File:** `game/strategy/facade/dto/empire_dto.py`
**Tests:** `pytest tests/strategy/facade/test_empire_dto.py`

- [x] Create `ColonySummary` frozen dataclass:
  ```python
  @dataclass(frozen=True)
  class ColonySummary:
      planet_id: int
      planet_name: str
      has_shipyard: bool
  ```
- [x] Create `FleetSummary` frozen dataclass:
  ```python
  @dataclass(frozen=True)
  class FleetSummary:
      fleet_id: int
      ship_count: int
      has_orders: bool
  ```
- [x] Create `EmpireInfo` frozen dataclass:
  ```python
  @dataclass(frozen=True)
  class EmpireInfo:
      empire_id: int
      name: str
      color: Tuple[int, int, int]
      theme_id: str
      flag_id: str
      colony_count: int = 0
      fleet_count: int = 0
  ```

**Notes:** All frozen dataclasses implemented with factory methods (from_planet, from_fleet, from_empire). 13 tests in test_empire_dto.py - all passing.

---

### Task 1.5: Create StrategySessionFacade Skeleton [Medium]
**File:** `game/strategy/facade/strategy_session_facade.py`
**Tests:** `pytest tests/strategy/facade/test_facade_init.py`

- [x] Create `StrategySessionFacade` class with `__init__(self, session: GameSession)`
- [x] Add `handle_command(command: Command) -> ValidationResult` method (delegates to session)
- [x] Add `process_turn()` method (delegates to session)
- [x] Add stub methods for all queries (raise NotImplementedError initially):
  - `get_fleet(fleet_id) -> Optional[FleetInfo]`
  - `get_fleets_at_hex(hex_coord) -> List[FleetInfo]`
  - `get_fleet_path_preview(fleet_id, target_hex) -> Optional[List[HexCoord]]`
  - `get_all_systems() -> List[SystemInfo]`
  - `get_system_at_hex(hex_coord) -> Optional[SystemInfo]`
  - `get_planet(planet_id) -> Optional[PlanetInfo]`
  - `get_all_empires() -> List[EmpireInfo]`
  - `get_empire(empire_id) -> Optional[EmpireInfo]`
  - `get_empire_colonies(empire_id) -> List[ColonySummary]`
  - `get_empire_fleets(empire_id) -> List[FleetSummary]`
  - `get_human_player_ids() -> List[int]`
  - `get_turn_number() -> int`
  - `can_colonize(fleet_id, planet_id) -> ValidationResult`
- [x] Write basic initialization test

**Notes:** Facade skeleton created with command delegation (handle_command, process_turn) and all query method stubs raising NotImplementedError. 17 tests in test_facade_init.py - all passing.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All DTO files created with proper structure
- [x] Facade skeleton compiles without errors
- [x] Run `pytest tests/ --testmon` - all tests pass
- [x] No import cycles introduced
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

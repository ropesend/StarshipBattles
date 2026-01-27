# Phase 1: Foundation - DTOs and Facade Structure

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-34 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create the DTO classes and facade skeleton

---

## Tasks

### Task 1.1: Create DTO Directory Structure [Simple]
**Files:** New directory `game/strategy/facade/dto/`
**Tests:** N/A (structure only)

- [ ] Create `game/strategy/facade/` directory
- [ ] Create `game/strategy/facade/__init__.py`
- [ ] Create `game/strategy/facade/dto/` directory
- [ ] Create `game/strategy/facade/dto/__init__.py`

**Notes:**

---

### Task 1.2: Implement Fleet DTOs [Medium]
**File:** `game/strategy/facade/dto/fleet_dto.py`
**Tests:** `pytest tests/strategy/facade/test_fleet_dto.py`

- [ ] Create `FleetOrderInfo` frozen dataclass:
  ```python
  @dataclass(frozen=True)
  class FleetOrderInfo:
      order_type: str  # "MOVE", "COLONIZE", "MOVE_TO_FLEET", "JOIN_FLEET"
      target_description: str
      target_hex: Optional[HexCoord] = None
      target_id: Optional[int] = None
  ```
- [ ] Create `ShipInfo` frozen dataclass:
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
- [ ] Create `FleetInfo` frozen dataclass:
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
- [ ] Implement `FleetInfo.from_fleet(fleet: Fleet) -> FleetInfo` factory method
- [ ] Write unit tests for factory method

**Notes:**

---

### Task 1.3: Implement System/Planet DTOs [Medium]
**Files:** `game/strategy/facade/dto/system_dto.py`, `game/strategy/facade/dto/planet_dto.py`
**Tests:** `pytest tests/strategy/facade/test_system_dto.py`

- [ ] Create `StarInfo` frozen dataclass:
  ```python
  @dataclass(frozen=True)
  class StarInfo:
      name: str
      star_type: str
      color: Tuple[int, int, int]
      location: HexCoord
  ```
- [ ] Create `WarpPointInfo` frozen dataclass:
  ```python
  @dataclass(frozen=True)
  class WarpPointInfo:
      destination_system_name: str
      location: HexCoord
  ```
- [ ] Create `SystemInfo` frozen dataclass:
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
- [ ] Create `PlanetInfo` frozen dataclass:
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
- [ ] Implement factory methods for each DTO

**Notes:**

---

### Task 1.4: Implement Empire DTOs [Simple]
**File:** `game/strategy/facade/dto/empire_dto.py`
**Tests:** `pytest tests/strategy/facade/test_empire_dto.py`

- [ ] Create `ColonySummary` frozen dataclass:
  ```python
  @dataclass(frozen=True)
  class ColonySummary:
      planet_id: int
      planet_name: str
      has_shipyard: bool
  ```
- [ ] Create `FleetSummary` frozen dataclass:
  ```python
  @dataclass(frozen=True)
  class FleetSummary:
      fleet_id: int
      ship_count: int
      has_orders: bool
  ```
- [ ] Create `EmpireInfo` frozen dataclass:
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

**Notes:**

---

### Task 1.5: Create StrategySessionFacade Skeleton [Medium]
**File:** `game/strategy/facade/strategy_session_facade.py`
**Tests:** `pytest tests/strategy/facade/test_facade_init.py`

- [ ] Create `StrategySessionFacade` class with `__init__(self, session: GameSession)`
- [ ] Add `handle_command(command: Command) -> ValidationResult` method (delegates to session)
- [ ] Add `process_turn()` method (delegates to session)
- [ ] Add stub methods for all queries (raise NotImplementedError initially):
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
- [ ] Write basic initialization test

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All DTO files created with proper structure
- [ ] Facade skeleton compiles without errors
- [ ] Run `pytest tests/ --testmon` - all tests pass
- [ ] No import cycles introduced
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

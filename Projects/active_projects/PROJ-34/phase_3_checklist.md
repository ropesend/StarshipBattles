# Phase 3: Facade Query Implementation

**Objective:** Implement all query methods in the facade
**Status:** Not Started

---

## Task 3.1: Implement Fleet Queries [Medium]
**File:** `game/strategy/facade/strategy_session_facade.py`
**Tests:** `pytest tests/strategy/facade/test_fleet_queries.py`

- [ ] Implement `get_fleet(fleet_id: int) -> Optional[FleetInfo]`:
  - Search all empires for fleet with matching ID
  - Return `FleetInfo.from_fleet(fleet)` or None
- [ ] Implement `get_fleets_at_hex(hex_coord: HexCoord) -> List[FleetInfo]`:
  - Search all empires' fleets for matching location
  - Return list of FleetInfo DTOs
- [ ] Implement `get_fleet_path_preview(fleet_id: int, target_hex: HexCoord) -> Optional[List[HexCoord]]`:
  - Find fleet by ID
  - Delegate to `self._session.preview_fleet_path(fleet, target_hex)`
  - Return path or None
- [ ] Implement `get_fleet_path_projection(fleet_id: int, max_turns: int = 50) -> List[dict]`:
  - Find fleet by ID
  - Delegate to `self._session.get_fleet_path_projection(fleet, max_turns)`
- [ ] Implement `get_empire_fleets(empire_id: int) -> List[FleetSummary]`:
  - Find empire by ID
  - Return list of FleetSummary for each fleet
- [ ] Write tests for each query method

**Notes:**

---

## Task 3.2: Implement System/Planet Queries [Medium]
**File:** `game/strategy/facade/strategy_session_facade.py`
**Tests:** `pytest tests/strategy/facade/test_system_queries.py`

- [ ] Implement `get_all_systems() -> List[SystemInfo]`:
  - Iterate `self._session.systems`
  - Return list of SystemInfo DTOs
- [ ] Implement `get_system_at_hex(hex_coord: HexCoord) -> Optional[SystemInfo]`:
  - Use `pathfinding.get_system_at_hex()` or search systems
  - Return SystemInfo or None
- [ ] Implement `get_planet(planet_id: int) -> Optional[PlanetInfo]`:
  - Search all systems' planets for matching ID
  - Return PlanetInfo or None
- [ ] Implement `get_planets_at_hex(hex_coord: HexCoord) -> List[PlanetInfo]`:
  - Find system at hex
  - Return planets at that location as PlanetInfo list
- [ ] Write tests for each query method

**Notes:**

---

## Task 3.3: Implement Empire Queries [Simple]
**File:** `game/strategy/facade/strategy_session_facade.py`
**Tests:** `pytest tests/strategy/facade/test_empire_queries.py`

- [ ] Implement `get_all_empires() -> List[EmpireInfo]`:
  - Iterate `self._session.empires`
  - Return list of EmpireInfo DTOs
- [ ] Implement `get_empire(empire_id: int) -> Optional[EmpireInfo]`:
  - Find empire by ID
  - Return EmpireInfo or None
- [ ] Implement `get_empire_colonies(empire_id: int) -> List[ColonySummary]`:
  - Find empire by ID
  - Return list of ColonySummary for each colony
- [ ] Implement `get_human_player_ids() -> List[int]`:
  - Return `list(self._session.human_player_ids)`
- [ ] Implement `get_turn_number() -> int`:
  - Return `self._session.turn_number`
- [ ] Write tests for each query method

**Notes:**

---

## Task 3.4: Implement Validation Queries [Simple]
**File:** `game/strategy/facade/strategy_session_facade.py`
**Tests:** `pytest tests/strategy/facade/test_validation_queries.py`

- [ ] Implement `can_colonize(fleet_id: int, planet_id: Optional[int] = None) -> ValidationResult`:
  - Find fleet by ID
  - Find planet by ID (if provided)
  - Delegate to `self._session.turn_engine.validate_colonize_order()`
  - Return ValidationResult
- [ ] Implement `can_move_to(fleet_id: int, target_hex: HexCoord) -> ValidationResult`:
  - Find fleet by ID
  - Check if path exists using `preview_fleet_path`
  - Return ValidationResult with is_valid based on path existence
- [ ] Write tests for validation queries

**Notes:**

---

## Phase 3 Verification
- [ ] All query methods implemented (no more NotImplementedError)
- [ ] Run `pytest tests/strategy/facade/` - all pass
- [ ] Run `pytest tests/ --testmon` - no regressions
- [ ] Queries return DTOs, not domain objects (verify manually)

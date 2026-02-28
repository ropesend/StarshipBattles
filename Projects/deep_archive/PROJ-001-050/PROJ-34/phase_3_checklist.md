# Phase 3: Facade Query Implementation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-34 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Objective:** Implement all query methods in the facade
**Status:** Complete

---

## Task 3.1: Implement Fleet Queries [Medium]
**File:** `game/strategy/facade/strategy_session_facade.py`
**Tests:** `pytest tests/strategy/facade/test_fleet_queries.py`

- [x] Implement `get_fleet(fleet_id: int) -> Optional[FleetInfo]`:
  - Search all empires for fleet with matching ID
  - Return `FleetInfo.from_fleet(fleet)` or None
- [x] Implement `get_fleets_at_hex(hex_coord: HexCoord) -> List[FleetInfo]`:
  - Search all empires' fleets for matching location
  - Return list of FleetInfo DTOs
- [x] Implement `get_fleet_path_preview(fleet_id: int, target_hex: HexCoord) -> Optional[List[HexCoord]]`:
  - Find fleet by ID
  - Delegate to `self._session.preview_fleet_path(fleet, target_hex)`
  - Return path or None
- [x] Implement `get_fleet_path_projection(fleet_id: int, max_turns: int = 50) -> List[dict]`:
  - Find fleet by ID
  - Delegate to `self._session.get_fleet_path_projection(fleet, max_turns)`
- [x] Implement `get_empire_fleets(empire_id: int) -> List[FleetSummary]`:
  - Find empire by ID
  - Return list of FleetSummary for each fleet
- [x] Write tests for each query method

**Notes:** 12 tests in test_fleet_queries.py. Added `_find_fleet_by_id()` and `_find_empire_by_id()` helper methods.

---

## Task 3.2: Implement System/Planet Queries [Medium]
**File:** `game/strategy/facade/strategy_session_facade.py`
**Tests:** `pytest tests/strategy/facade/test_system_queries.py`

- [x] Implement `get_all_systems() -> List[SystemInfo]`:
  - Iterate `self._session.galaxy.systems.values()`
  - Return list of SystemInfo DTOs
- [x] Implement `get_system_at_hex(hex_coord: HexCoord) -> Optional[SystemInfo]`:
  - Use `self._session.galaxy.systems.get(hex_coord)`
  - Return SystemInfo or None
- [x] Implement `get_planet(planet_id: int) -> Optional[PlanetInfo]`:
  - Search all systems' planets for matching ID
  - Return PlanetInfo or None
- [x] Implement `get_planets_at_hex(hex_coord: HexCoord) -> List[PlanetInfo]`:
  - Find system at hex
  - Return planets at that location as PlanetInfo list
- [x] Write tests for each query method

**Notes:** 10 tests in test_system_queries.py. Added `_find_planet_by_id()` helper method.

---

## Task 3.3: Implement Empire Queries [Simple]
**File:** `game/strategy/facade/strategy_session_facade.py`
**Tests:** `pytest tests/strategy/facade/test_empire_queries.py`

- [x] Implement `get_all_empires() -> List[EmpireInfo]`:
  - Iterate `self._session.empires`
  - Return list of EmpireInfo DTOs
- [x] Implement `get_empire(empire_id: int) -> Optional[EmpireInfo]`:
  - Find empire by ID
  - Return EmpireInfo or None
- [x] Implement `get_empire_colonies(empire_id: int) -> List[ColonySummary]`:
  - Find empire by ID
  - Return list of ColonySummary for each colony
- [x] Implement `get_human_player_ids() -> List[int]`:
  - Return `list(self._session.human_player_ids)` (defensive copy)
- [x] Implement `get_turn_number() -> int`:
  - Return `self._session.turn_number`
- [x] Write tests for each query method

**Notes:** 11 tests in test_empire_queries.py.

---

## Task 3.4: Implement Validation Queries [Simple]
**File:** `game/strategy/facade/strategy_session_facade.py`
**Tests:** `pytest tests/strategy/facade/test_validation_queries.py`

- [x] Implement `can_colonize(fleet_id: int, planet_id: Optional[int] = None) -> ValidationResult`:
  - Find fleet by ID
  - Find planet by ID (if provided)
  - Delegate to `self._session.turn_engine.validate_colonize_order()`
  - Return ValidationResult
- [x] Implement `can_move_to(fleet_id: int, target_hex: HexCoord) -> ValidationResult`:
  - Find fleet by ID
  - Check if path exists using `preview_fleet_path`
  - Return ValidationResult with is_valid based on path existence
- [x] Write tests for validation queries

**Notes:** 8 tests in test_validation_queries.py. Uses `validation_result()` helper for creating ValidationResult instances.

---

## Phase 3 Verification
- [x] All query methods implemented (no more NotImplementedError)
- [x] Run `pytest tests/strategy/facade/` - all pass (90 tests)
- [x] Run `pytest tests/strategy/` - all pass (227 tests)
- [x] Queries return DTOs, not domain objects (verified - all use .from_X() factory methods)

# Phase 1: Core Zone Infrastructure

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-139 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add hex_circle_filled utility, IZoneOccupant protocol, and occupied_hexes to Star and Planet.

---

## Tasks

### Task 1.1: Add `hex_circle_filled()` to hex_math.py [Simple]
**File:** `game/core/hex_math.py`
**Tests:** `pytest tests/unit/core/test_hex_math_core.py`

- [x] Add function `hex_circle_filled(center: HexCoord, radius: int) -> FrozenSet[HexCoord]` after `hex_ring()` (after line 195)
- [x] Implementation: iterate `hex_ring(r)` for r in range(0, radius+1), offset each by center, return frozenset
- [x] Write tests in `tests/unit/core/test_hex_math_core.py`:
  - `test_hex_circle_filled_radius_0` returns just center
  - `test_hex_circle_filled_radius_1` returns 7 hexes
  - `test_hex_circle_filled_radius_2` returns 19 hexes
  - `test_hex_circle_filled_radius_5` returns 91 hexes
  - `test_hex_circle_filled_with_offset_center`
- [x] Verify: `pytest tests/unit/core/test_hex_math_core.py` passes

**Notes:** 7 tests added, all passing.

### Task 1.2: Add `IZoneOccupant` protocol [Simple]
**File:** `game/core/protocols.py`
**Tests:** `pytest tests/unit/core/`

- [x] Add import: `from typing import FrozenSet` (top of file)
- [x] Add protocol after `IPlanet` (after line 188):
  ```python
  @runtime_checkable
  class IZoneOccupant(Protocol):
      """Protocol for entities that occupy multiple hexes."""
      @property
      def occupied_hexes(self) -> FrozenSet:
          """Set of LOCAL hex coords this object occupies."""
          ...
  ```
- [x] Write tests verifying Star and Planet satisfy protocol (after Tasks 1.3/1.4)
- [x] Verify: `pytest tests/unit/core/` passes

**Notes:** 5 tests added in TestIZoneOccupantProtocol class.

### Task 1.3: Add `occupied_hexes` property to Star [Medium]
**File:** `game/strategy/data/stars.py`
**Tests:** `pytest tests/unit/strategy/data/`

- [x] Add import: `from game.core.hex_math import hex_circle_filled` (line 7 area)
- [x] Add `import math` if not already present
- [x] Add property to Star dataclass (after `location` field, around line 89):
  ```python
  @property
  def occupied_hexes(self) -> FrozenSet:
      radius = max(0, int(math.ceil(self.diameter_hexes / 2.0)))
      return hex_circle_filled(self.location, radius)
  ```
- [x] Write tests:
  - `test_star_occupied_hexes_small` (diameter_hexes=1.0 -> radius 1 -> 7 hexes)
  - `test_star_occupied_hexes_large` (diameter_hexes=11.0 -> radius 6 -> 127 hexes)
  - `test_star_occupied_hexes_sub_hex` (diameter_hexes=0.5 -> radius 1 -> 7 hexes)
  - `test_star_occupied_hexes_with_offset_location`
- [x] Verify: `pytest tests/unit/strategy/data/` passes

**Notes:** 5 tests added in TestStarOccupiedHexes class. No serialization change needed.

### Task 1.4: Add `occupied_hexes` and `diameter_hexes` to Planet [Medium]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/data/`

- [x] Add import: `from game.core.hex_math import hex_circle_filled` (top of file)
- [x] Add `import math` if not already present
- [x] Add `diameter_hexes: float = 0.0` field to Planet dataclass (after `image_rotation`, line 196)
- [x] Add property:
  ```python
  @property
  def occupied_hexes(self) -> FrozenSet:
      if self.diameter_hexes > 0:
          radius = max(0, int(math.ceil(self.diameter_hexes / 2.0)))
          return hex_circle_filled(self.location, radius)
      return frozenset({self.location})
  ```
- [x] Update `to_dict()` (line 292): add `'diameter_hexes': self.diameter_hexes` to dict
- [x] Update `from_dict()` (line 372): add `diameter_hexes=data.get('diameter_hexes', 0.0)`
- [x] Write tests:
  - `test_planet_occupied_hexes_normal` - regular planet returns single hex
  - `test_planet_occupied_hexes_dyson_sphere` - planet with diameter_hexes=11 returns zone
  - `test_planet_serialization_with_diameter_hexes` - round-trip test
- [x] Verify: `pytest tests/unit/strategy/data/` passes

**Notes:** 9 tests added in test_planet_zones.py (TestPlanetOccupiedHexes + TestPlanetDiameterHexesSerialization).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/strategy/ tests/unit/core/` passes (2660 tests)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

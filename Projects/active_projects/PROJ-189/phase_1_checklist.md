# Phase 1: Storm Data Model & Serialization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-189 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Define the Storm entity, its effect data types, integrate with StarSystem serialization and Galaxy zone registration.

---

## Tasks

### Task 1.1: Create Storm data model [Medium]
**File:** `game/strategy/data/storm.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_storm.py`

- [x] Create `StormEffect` dataclass:
  - `shield_capacity_mult: float = 1.0`
  - `thrust_mult: float = 1.0`
  - `strategic_mult: float = 1.0`
  - `damage_per_tick: float = 0.0`
  - `fuel_drain_per_tick: float = 0.0`
- [x] Add `StormEffect.to_dict()` returning plain dict of field values
- [x] Add `StormEffect.from_dict(data)` classmethod with defaults for missing keys
- [x] Create `Storm` dataclass:
  - `name: str` - display name (e.g., "Ion Storm Alpha")
  - `storm_type: str` - type ID from storms.json (e.g., "ion_storm")
  - `location: HexCoord` - center hex, local to system
  - `hex_offsets: FrozenSet[HexCoord]` - offsets relative to location (includes HexCoord(0,0) for center)
  - `effects: StormEffect` - the environmental effects
  - `image_variant: int` - index into nebulae image group (1-6)
  - `intensity: float` - 0.0-1.0 controls rendering alpha
- [x] Add `occupied_hexes` property: `frozenset({self.location + offset for offset in self.hex_offsets})`
- [x] Add `Storm.to_dict()` using `hex_to_dict()` for location and hex_offsets (list of dicts)
- [x] Add `Storm.from_dict(data)` classmethod using `hex_from_dict()`, with error handling matching WarpPoint pattern
- [x] Write tests:
  - [x] Storm creation with default StormEffect
  - [x] StormEffect serialization round-trip
  - [x] Storm serialization round-trip
  - [x] `occupied_hexes` computation: single hex (only center), multi-hex (center + offsets)
  - [x] `from_dict` with missing optional fields uses defaults

**Notes:** 16 tests for Storm and StormEffect.

### Task 1.2: Integrate storms into StarSystem [Simple]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_storm.py tests/integration/strategy/`

- [x] Add `from game.strategy.data.storm import Storm` import at top of file (after Planet import, ~line 15)
- [x] Add `self.storms: List[Storm] = []` to `StarSystem.__init__()` (after `self.planets = []`, ~line 75)
- [x] Add `'storms': [s.to_dict() for s in self.storms]` to `StarSystem.to_dict()` (after planets serialization, ~line 97)
- [x] Add storm deserialization in `StarSystem.from_dict()` (after planets loop, ~line 144):
  ```python
  for i, s in enumerate(data.get('storms', [])):
      try:
          system.storms.append(Storm.from_dict(s))
      except (PersistenceException, KeyError, TypeError, ValueError) as e:
          logger.warning(f"StarSystem '{data['name']}': skipping invalid storm at index {i}: {e}")
  ```
- [x] Write test: StarSystem with storms serializes and deserializes correctly (round-trip)
- [x] Write test: StarSystem.from_dict with no 'storms' key produces empty storms list (backward compat)

**Notes:** 6 tests for StarSystem integration.

### Task 1.3: Register storms as zones in Galaxy [Simple]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_storm.py`

- [x] In `Galaxy.add_system()` (~line 197, after warp point registration), add:
  ```python
  # Register storm zones (PROJ-189)
  for storm in system.storms:
      self.register_zone(system, storm)
  ```
- [x] Write test: After adding a system with storms, `galaxy.get_zones_at_global_hex()` returns storm objects at correct hexes
- [x] Write test: Storm zones coexist with star zones at same hex without conflicts
- [x] Run existing galaxy tests to verify no regressions: `pytest tests/unit/strategy/data/ tests/integration/strategy/ -n 4`

**Notes:** 4 tests for Galaxy zone registration. Also added zone registration in Galaxy.from_dict() for save/load.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All tests pass: `pytest tests/ --testmon`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2

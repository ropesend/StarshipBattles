# Phase 1: Core Data Model Rename

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-217 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Rename `diameter_hexes` → `radius_hexes` on Star, Planet, and IPlanet protocol. Update serialization keys. Tests will break — that's expected.

---

## Tasks

### Task 1.1: Rename on Star dataclass [Simple]
**File:** `game/strategy/data/stars.py`
**Tests:** `pytest tests/unit/strategy/data/test_stars.py` (expect value failures, not import errors)

- [x] Rename field `diameter_hexes: float` → `radius_hexes: int` (line 104)
- [x] Update comment: `# Diameter in Hexes` → `# Radius in hexes (1 = center only, 2 = center + ring 1, etc.)`
- [x] Update `occupied_hexes` property docstring and formula (lines 115-128)
- [x] Update `to_dict()`: key `'diameter_hexes': self.diameter_hexes` → `'radius_hexes': self.radius_hexes` (line 136)
- [x] Update `from_dict()` `require_keys` list: `'diameter_hexes'` → `'radius_hexes'` (line 165)
- [x] Update `from_dict()` constructor: `diameter_hexes=data['diameter_hexes']` → `radius_hexes=data['radius_hexes']` (line 198)
- [x] Verify: `import game.strategy.data.stars` succeeds with no errors

**Notes:** Complete

### Task 1.2: Rename on Planet dataclass [Simple]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet_zones.py` (expect value failures)

- [x] Rename field `diameter_hexes: float = 0.0` → `radius_hexes: int = 0` (line 102)
- [x] Update comment on line 101
- [x] Update `occupied_hexes` property docstring and formula (lines 122-132)
- [x] Update `to_dict()`: key `'diameter_hexes'` → `'radius_hexes'` (line 255)
- [x] Update `from_dict()`: `.get('diameter_hexes', 0.0)` → `.get('radius_hexes', 0)` (line 351)
- [x] Verify: `import game.strategy.data.planet` succeeds

**Notes:** Complete

### Task 1.3: Rename on IPlanet protocol [Simple]
**File:** `game/core/protocols.py`
**Tests:** `pytest tests/unit/core/test_protocols.py`

- [x] Rename `diameter_hexes` property → `radius_hexes` (line 241)
- [x] Update IZoneOccupant docstring: "Stars (based on diameter_hexes)" → "Stars (based on radius_hexes)" (line 263)
- [x] Verify: `import game.core.protocols` succeeds

**Notes:** Complete

### Task 1.4: Checkpoint — verify structural correctness [Simple]
**Tests:** `pytest tests/unit/strategy/data/test_stars.py tests/unit/strategy/data/test_planet_zones.py -x --tb=short 2>&1 | head -30`

- [x] Run tests — expect failures from wrong values/keys, NOT `AttributeError` or `ImportError`
- [x] If structural errors exist, fix them before proceeding

**Notes:** Verified - errors are TypeError `unexpected keyword argument 'diameter_hexes'` (test code using old field name), not import errors.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Structural errors verified as absent (only value mismatches remain)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2

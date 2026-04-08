# PROJ-224 Phase 2: Shared Utilities

## DUP-CEA-001 + DUP-SIM-004: Consolidate `_has_attrs`
- [x] Keep `_has_attrs()` in `game/core/protocols.py` (it's already there)
- [x] Remove duplicate from `game/ai/protocols.py` — import from core
- [x] Remove duplicate from `game/simulation/interfaces/entity_protocols.py` — import from core
- [x] Remove duplicate from `game/simulation/interfaces/ability_protocols.py` — import from core
- [x] Run tests to verify no breakage

## DUP-XL-009: Create `display_name()` Utility
- [x] Add `display_name(raw: str) -> str` to `game/core/string_utils.py` (NEW)
- [x] Implementation: `return raw.replace('_', ' ').title()`
- [x] Find all 9+ occurrences of `replace('_', ' ').title()` pattern across codebase
- [x] Replace each with `display_name()` call (13 occurrences across 9 files)
- [x] Run tests

## DUP-SCR-009: Extract `EARTH_MASS` Constant
- [x] Add `EARTH_MASS = 5.97e24` to `game/core/constants.py`
- [x] Find all 4+ hardcoded instances across UI files
- [x] Replace with `EARTH_MASS` import (planet_list_filters.py x3, strategy_detail_fmt.py x1, planet_physics.py alias)
- [x] Run tests

## DUP-SD-03: Create `hex_from_dict_safe()` Utility
- [x] Add utility to `game/core/hex_math.py` that handles the repeated try/except HexCoord deserialization
- [x] Run tests

**Notes:** Created `hex_from_dict_safe()` with 8 tests. Did NOT replace boilerplate in planet.py/stars.py/storm.py/galaxy.py because those callers raise specific PersistenceException with context — replacing would not reduce boilerplate. Utility is available for future optional-location patterns.

## DUP-SS-04: Consolidate Slug Functions
- [x] Compare `RaceLibrary._slugify()` and `DesignLibrary._sanitize_design_id()`
- [x] Create single `slugify()` in `game/core/string_utils.py`
- [x] Update both callers
- [x] Run tests

**Notes:** Core `slugify()` lowercases (old `_sanitize_design_id` preserved case). Updated tests accordingly. Length limit (50 chars) moved to caller site in race_library.

## DUP-XL-007: Angle Calculation Utility
- [x] Identify all 4 locations using inline `math.atan2` → degrees pattern
- [x] Created `angle_from_vector(dx, dy)` in `game/core/math.py`, returns [0, 360)
- [x] Replaced in: controller.py, combat_utils.py, weapons.py, weapon_firing_system.py
- [x] Run tests

## Completion
- [x] All items above checked off
- [x] Run `pytest tests/ -n 12` — all pass (13469 passed)

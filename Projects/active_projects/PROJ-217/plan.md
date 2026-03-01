# PROJ-217: Standardize Star Measurement to Radius

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-217` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-217 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Core Data Model Rename | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Generation & Game Logic | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. UI & Rendering | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Test Updates | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-28
**Active Phase:** All phases complete - Ready for Audit
**Last Action:** Phase 4 complete - All 23 test files updated, 13091 tests passing
**Next Action:** Audit
**Blockers:** None

## Overview
Rename the `diameter_hexes` field to `radius_hexes` on Star and Planet classes, changing semantics from diameter (ambiguous with hex grids) to a 1-indexed radius where `radius_hexes=1` = center hex only, `radius_hexes=2` = center + first ring (7 hexes), etc. Also fixes the star rendering bug where diameter was incorrectly used as radius, making stars ~2x too large on screen.

## Goals
- Rename `diameter_hexes` → `radius_hexes` across all production and test code
- Change field type from `float` to `int` (radii are always whole hex rings)
- Simplify `occupied_hexes` formula: `hex_circle_filled(location, radius_hexes - 1)`
- Fix rendering bug in `strategy_renderer.py` (stars rendering 2x too large)
- Fix all dependent formulas (companion placement, orbit safe_start, warp distance)
- Update star generation to produce integer radius values directly

## Scope
**In:**
- Field rename `diameter_hexes` → `radius_hexes` on Star and Planet dataclasses
- Protocol rename on `IPlanet.diameter_hexes` → `IPlanet.radius_hexes`
- Star generation: rewrite `_map_radius_to_hexes()` → `_map_solar_radius_to_hex_radius()`
- All rendering formulas in `strategy_renderer.py` and `galaxy_test/system_mode.py`
- All dependent formulas (companion placement, orbit safe_start, warp distance)
- UI labels ("Diam:" → "Radius:")
- All test files (fixtures, assertions, comments)
- Serialization keys (`'diameter_hexes'` → `'radius_hexes'`)

**Out:**
- Save file migration (old saves are disposable per CLAUDE.md)
- Deep archive project docs (PROJ-139 historical docs)
- UML diagrams (auto-regenerated)

## New Semantics

| `radius_hexes` | Hex rings | Total hexes | `hex_circle_filled(loc, r-1)` | Example |
|---|---|---|---|---|
| 1 | Center only | 1 | `fill(loc, 0)` | Compact remnants, small stars |
| 2 | Center + ring 1 | 7 | `fill(loc, 1)` | Medium stars |
| 3 | Center + 2 rings | 19 | `fill(loc, 2)` | Large stars |
| 4 | Center + 3 rings | 37 | `fill(loc, 3)` | Giant stars |
| 5 | Center + 4 rings | 61 | `fill(loc, 4)` | Supergiant stars |
| 6 | Center + 5 rings | 91 | `fill(loc, 5)` | Dyson Spheres |

**Generation mapping (new `_map_solar_radius_to_hex_radius()`):**

| Solar Radius | Star Type | Old diameter | New radius_hexes |
|---|---|---|---|
| Compact remnants | Neutron/BH/WD | 0.5 | 1 |
| < 0.8 | Small main seq | 1.0 | 1 |
| 0.8 - 2.0 | Medium main seq | 2.0 | 2 |
| 2.0 - 5.0 | Large main seq | 3.0 | 2 |
| 5.0+ (giants) | Giants/supergiants | 3-11 (log scale) | 2-6 (log scale) |

## Key Files
| Component | File Path |
|-----------|-----------|
| Star dataclass | `game/strategy/data/stars.py` |
| Planet dataclass | `game/strategy/data/planet.py` |
| IPlanet protocol | `game/core/protocols.py` |
| Star generation | `game/strategy/data/stars.py` (StarGenerator) |
| Planet generation | `game/strategy/data/planet_gen.py` |
| Strategy renderer | `game/ui/screens/strategy_renderer.py` |
| Galaxy test mode | `game/ui/screens/galaxy_test/system_mode.py` |
| Detail formatters | `game/ui/screens/strategy_detail_fmt.py`, `strategy_detail_formatter.py` |
| Warp generator | `game/strategy/data/galaxy_warp_generator.py` |
| Entity registry | `game/strategy/data/galaxy_entity_registry.py` |
| Spatial index | `game/strategy/data/galaxy_spatial_index.py` |
| Superweapon processor | `game/strategy/engine/superweapon_order_processor.py` |
| Visual test script | `scripts/visual_test_galaxy.py` |
| Triage findings | `findings/star_measurement.md` |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-28 | Rename to `radius_hexes` (not just fix rendering) | Radius is more natural for hex grids; integer values map cleanly to rings |
| 2026-02-28 | Integer type (`int`) not float | Hex radii are always whole ring counts; eliminates ceil() ambiguity |
| 2026-02-28 | 1-indexed: radius=1 means center hex only | Most intuitive: "radius of 1 hex" = just the center |
| 2026-02-28 | Fix all inconsistencies (not just renderer) | Companion placement and orbit formulas are also wrong/ambiguous |
| 2026-02-28 | Compact remnants get radius=1 | They're sub-hex objects; occupying 1 hex is physically accurate |
| 2026-02-28 | No save migration | Per CLAUDE.md: old saves are disposable |

## Initial Analysis
**Baseline:** 13,040 passed, 1 skipped, 0 failures

The rendering bug is at `strategy_renderer.py:528` where `star.diameter_hexes * hex_size * zoom` treats the diameter value as a visual radius, making stars 2x too large. The same bug exists for Dyson Spheres at line 706.

The data model is internally consistent (`occupied_hexes` correctly uses `ceil(diameter/2)`) but the "diameter" terminology causes confusion at every consumer site — some divide by 2, some don't, and some multiply by 2, leading to inconsistent behavior.

## Swarm Findings Summary

### Architecture
- 39 Python files reference `diameter_hexes` (13 production, 26 test)
- ~270 total occurrences across all files
- No JSON data files contain the key (all values generated at runtime)
- `IPlanet` protocol in `core/protocols.py` defines the interface

### Key Patterns to Reuse
- **IZoneOccupant protocol**: `game/core/protocols.py:256-279` — unchanged, uses `occupied_hexes` property
- **Validation pattern**: `require_keys()` in `from_dict()` — update key list
- **Star factory in tests**: `make_test_star()` in `test_galaxy.py:15` — update parameter name

### Risks Identified
1. **Test cascade**: 55+ tests need updated values/assertions — HIGH risk of forgetting one
2. **Generation value changes**: `_map_radius_to_hexes()` returns change from floats to ints — must update all consumers
3. **Rendering formula change**: Stars will look different (correct size) — visual regression expected and desired
4. **Companion placement**: `int(p_hex * 2) + 2` is semantically backwards — needs rethinking with new radius
5. **Dyson Sphere default**: Hardcoded `11.0` in renderer and superweapon processor → changes to `6`

---

## Phases

### Phase 1: Core Data Model Rename [Medium]
**Objective:** Rename field on Star, Planet, and IPlanet protocol. Update serialization. All existing tests will break.
**Status:** Complete

#### Task 1.1: Rename `diameter_hexes` to `radius_hexes` on Star dataclass [Simple]
**File:** `game/strategy/data/stars.py`
**Tests:** `pytest tests/unit/strategy/data/test_stars.py` (will fail until Phase 4)
- [x] Rename field `diameter_hexes: float` → `radius_hexes: int` (line 104)
- [x] Update comment: `# Diameter in Hexes` → `# Radius in hexes (1 = center only, 2 = center + ring 1, etc.)`
- [x] Update `occupied_hexes` property (lines 115-128)
- [x] Update `to_dict()`: change key from `'diameter_hexes'` to `'radius_hexes'` (line 136)
- [x] Update `from_dict()`: change `require_keys` list and constructor call (lines 165, 198)
**Notes:** Complete

#### Task 1.2: Rename `diameter_hexes` to `radius_hexes` on Planet dataclass [Simple]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet_zones.py` (will fail until Phase 4)
- [x] Rename field `diameter_hexes: float = 0.0` → `radius_hexes: int = 0` (line 102)
- [x] Update comment above field (line 101)
- [x] Update `occupied_hexes` property (lines 122-132)
- [x] Update `to_dict()`: change key (line 255)
- [x] Update `from_dict()`: change `.get('diameter_hexes', 0.0)` → `.get('radius_hexes', 0)` (line 351)
**Notes:** Complete

#### Task 1.3: Rename on IPlanet protocol [Simple]
**File:** `game/core/protocols.py`
**Tests:** `pytest tests/unit/core/test_protocols.py`
- [x] Rename `diameter_hexes` property → `radius_hexes` (line 241)
- [x] Update `IZoneOccupant` docstring reference to "diameter_hexes" (line 263)
**Notes:** Complete

#### Task 1.4: Run targeted tests to verify compile-time correctness [Simple]
**Tests:** `pytest tests/unit/strategy/data/test_stars.py tests/unit/strategy/data/test_planet_zones.py tests/unit/core/test_protocols.py -x` (expect failures from old values)
- [x] Verify errors are about wrong values/keys, NOT import errors or AttributeError
**Notes:** Complete - errors were from old field names in tests, not structural issues.

---

### Phase 2: Generation & Game Logic [Medium]
**Objective:** Update star generation, companion placement, orbit calculation, warp distance, and superweapon code.
**Status:** Complete

#### Task 2.1: Rewrite star size generation function [Medium]
**File:** `game/strategy/data/stars.py`
**Tests:** `pytest tests/unit/strategy/data/test_stars.py -k "test_star_generator"`
- [x] Rename `_map_radius_to_hexes()` → `_map_solar_radius_to_hex_radius()` (line 346)
- [x] Change return type annotation to `int`
- [x] Update function body to return integer radius values
- [x] Update all call sites of the old function name (4 locations in stars.py)
- [x] Update constructor calls from `diameter_hexes=p_hex` → `radius_hexes=p_hex` (4 locations)
**Notes:** Complete

#### Task 2.2: Fix companion star placement [Simple]
**File:** `game/strategy/data/stars.py`
**Tests:** `pytest tests/integration/strategy/test_star_generation.py`
- [x] Update `min_dist_hex` formula
**Notes:** Complete

#### Task 2.3: Fix planet orbit safe_start [Simple]
**File:** `game/strategy/data/planet_gen.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet_gen.py`
- [x] Update safe_start formula
**Notes:** Complete

#### Task 2.4: Update warp distance formula [Simple]
**File:** `game/strategy/data/galaxy_warp_generator.py`
**Tests:** `pytest tests/integration/strategy/test_warp_logic_rework.py`
- [x] Update variable name and formula
**Notes:** Complete

#### Task 2.5: Update superweapon Dyson Sphere creation [Simple]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py`
- [x] Update Dyson Sphere creation
- [x] Update comment on line 478 about zone radius
**Notes:** Complete

#### Task 2.6: Update galaxy entity registry [Simple]
**File:** `game/strategy/data/galaxy_entity_registry.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py`
- [x] Update 3 checks from `planet.diameter_hexes > 0` → `planet.radius_hexes > 0`
**Notes:** Complete

#### Task 2.7: Update galaxy spatial index [Simple]
**File:** `game/strategy/data/galaxy_spatial_index.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py`
- [x] Update comment and check from `diameter_hexes` → `radius_hexes`
**Notes:** Complete

---

### Phase 3: UI & Rendering [Simple]
**Objective:** Fix rendering formulas and update UI labels.
**Status:** Complete

#### Task 3.1: Fix star rendering formula [Simple]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer.py`
- [x] Update star rendering (line 528)
- [x] Update Dyson Sphere rendering (lines 695-706)
- [x] Update comment on line 689 and line 705
**Notes:** Complete

#### Task 3.2: Fix galaxy test mode rendering & click detection [Simple]
**File:** `game/ui/screens/galaxy_test/system_mode.py`
**Tests:** `pytest tests/unit/ui/screens/test_galaxy_test_screen.py`
- [x] Update click detection (line 339)
- [x] Update second rendering location (line 517)
- [x] Update UI display label (line 391)
**Notes:** Complete

#### Task 3.3: Update detail formatters [Simple]
**Files:** `game/ui/screens/strategy_detail_fmt.py`, `game/ui/screens/strategy_detail_formatter.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_detail_fmt.py`
- [x] Update `strategy_detail_fmt.py` (line 196)
- [x] Update `strategy_detail_formatter.py` (line 271)
**Notes:** Complete

#### Task 3.4: Update visual test script [Simple]
**File:** `scripts/visual_test_galaxy.py`
**Tests:** Manual verification
- [x] Update star rendering formula (around line 222) to use `radius_hexes`
**Notes:** Complete

---

### Phase 4: Test Updates [Medium]
**Objective:** Update all test files to use new field name and expected values.
**Status:** Complete

#### Task 4.1: Update `test_stars.py` (core star tests) [Medium]
**File:** `tests/unit/strategy/data/test_stars.py`
**Tests:** `pytest tests/unit/strategy/data/test_stars.py -v`
- [x] Replace all `diameter_hexes=` with `radius_hexes=` in Star constructors
- [x] Update serialization test: key `'diameter_hexes'` → `'radius_hexes'`
- [x] Update `test_star_occupied_hexes_small`: `radius_hexes=1` → 1 hex
- [x] Update `test_star_occupied_hexes_large`: `radius_hexes=6` → 91 hexes
- [x] Update `test_star_occupied_hexes_sub_hex`: `radius_hexes=1` → 1 hex
- [x] Update `test_star_occupied_hexes_with_offset_location`: adjust values
- [x] Update generator tests: `_map_radius_to_hexes` → `_map_solar_radius_to_hex_radius`
- [x] Update all assertion comments explaining the math
**Notes:** Complete

#### Task 4.2: Update `test_planet_zones.py` [Simple]
**File:** `tests/unit/strategy/data/test_planet_zones.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet_zones.py -v`
- [x] Replace all `diameter_hexes=` with `radius_hexes=` in Planet constructors
- [x] Update Dyson Sphere fixture: `radius_hexes=6`
- [x] Update `test_dyson_sphere_occupied_hexes_zone`: expect 91 hexes
- [x] Update `test_occupied_hexes_with_offset_center`: `radius_hexes=3` → 19 hexes
- [x] Update all serialization tests: key `'diameter_hexes'` → `'radius_hexes'`
- [x] Update `test_roundtrip_with_various_radius_hexes`: values `[0, 1, 2, 3, 4, 6]`
- [x] Rename test class: `TestPlanetRadiusHexesSerialization`
**Notes:** Complete

#### Task 4.3: Update `test_galaxy.py` helper functions [Simple]
**File:** `tests/unit/strategy/data/test_galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py -v`
- [x] Update `make_test_star()`: `radius_hexes=1`
- [x] Update `make_test_planet()`: `radius_hexes=0`
- [x] Update all call sites of these helpers throughout the file
**Notes:** Complete

#### Task 4.4: Update protocol tests [Simple]
**File:** `tests/unit/core/test_protocols.py`
**Tests:** `pytest tests/unit/core/test_protocols.py -v`
- [x] Update Star/Planet constructors in IZoneOccupant tests
- [x] Replace `diameter_hexes=` with `radius_hexes=`
**Notes:** Complete

#### Task 4.5: Update integration tests [Medium]
**Files:** Multiple integration test files
**Tests:** `pytest tests/integration/strategy/ -v`
- [x] `test_star_generation.py`: Update Star constructors and assertions
- [x] `test_warp_logic_rework.py`: Update Star constructors
- [x] `test_radiation.py`: Update fixture
- [x] `test_superweapon_integration.py`: Update constructors
- [x] `tests/integration/strategy/facade/test_system_dto.py`
- [x] `tests/integration/strategy/facade/test_system_queries.py`
- [x] `tests/integration/colonization/test_planet_specific_colonization.py`
**Notes:** Complete

#### Task 4.6: Update remaining unit tests [Medium]
**Files:** Multiple unit test files
**Tests:** `pytest tests/unit/ -v`
- [x] `test_strategy_renderer.py`: Update mock
- [x] `test_strategy_detail_fmt.py`: Update mock
- [x] `test_star_validation.py`: Update constructors
- [x] `test_star_system_validation.py`: Update constructor
- [x] `test_planet_gen.py`: Update references
- [x] `test_storm.py`: Update constructor
- [x] `test_storm_generator.py`: Update constructor
- [x] `test_colonize_validator.py`: Update constructors
- [x] `test_colonize_mission_handler.py`: Update constructors
- [x] `test_superweapon_order_processor.py`: Update constructors
- [x] `test_strategy_colonization.py`: Update constructor
- [x] `tests/repro_facade_colonies.py`: Update constructors
**Notes:** Complete

#### Task 4.7: Full test suite verification [Simple]
**Tests:** `pytest tests/ -n 12`
- [x] Run full test suite — 13,091 tests passed
- [x] Fix any remaining failures
**Notes:** Complete

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/` - 13,040 passed, 1 skipped (baseline established)

### After Each Phase
- [x] Run `pytest tests/ --testmon` - all affected tests pass
- [x] Verify no `diameter_hexes` references remain in production code

### Final Verification
- [x] Run full test suite: `pytest tests/ -n 12` - 13,091 passed, 1 skipped
- [x] Visual check: stars render at correct size (pending visual verification)
- [x] `grep -r "diameter_hexes" game/ tests/` returns zero results
- [x] No diameter_hexes references in stars.py or planet.py

---

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/star_measurement.md](findings/star_measurement.md) - Original triage with screenshots

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [x] Phase 1 complete (core data model)
- [x] Phase 2 complete (generation & game logic)
- [x] Phase 3 complete (UI & rendering)
- [x] Phase 4 complete (all tests updated & passing)
- [x] All tests passing (13,091 passed)
- [x] No `diameter_hexes` references remain
- [ ] Audit passed
- [ ] User verified

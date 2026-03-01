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
| 4. Test Updates | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-28
**Active Phase:** Phase 4
**Last Action:** Phase 3 complete - strategy_renderer, system_mode, detail formatters, visual test script all updated
**Next Action:** Begin Phase 4 - Test Updates
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
**Status:** Not Started

#### Task 1.1: Rename `diameter_hexes` to `radius_hexes` on Star dataclass [Simple]
**File:** `game/strategy/data/stars.py`
**Tests:** `pytest tests/unit/strategy/data/test_stars.py` (will fail until Phase 4)
- [ ] Rename field `diameter_hexes: float` → `radius_hexes: int` (line 104)
- [ ] Update comment: `# Diameter in Hexes` → `# Radius in hexes (1 = center only, 2 = center + ring 1, etc.)`
- [ ] Update `occupied_hexes` property (lines 115-128):
  ```python
  @property
  def occupied_hexes(self) -> FrozenSet[HexCoord]:
      """Return all hexes occupied by this star.
      radius_hexes=1 → center hex only (1 hex)
      radius_hexes=2 → center + ring 1 (7 hexes)
      radius_hexes=N → hex_circle_filled(location, N-1)
      """
      return hex_circle_filled(self.location, max(0, self.radius_hexes - 1))
  ```
- [ ] Update `to_dict()`: change key from `'diameter_hexes'` to `'radius_hexes'` (line 136)
- [ ] Update `from_dict()`: change `require_keys` list and constructor call (lines 165, 198)
**Notes:**

#### Task 1.2: Rename `diameter_hexes` to `radius_hexes` on Planet dataclass [Simple]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet_zones.py` (will fail until Phase 4)
- [ ] Rename field `diameter_hexes: float = 0.0` → `radius_hexes: int = 0` (line 102)
- [ ] Update comment above field (line 101)
- [ ] Update `occupied_hexes` property (lines 122-132):
  ```python
  if self.radius_hexes > 0:
      return hex_circle_filled(self.location, max(0, self.radius_hexes - 1))
  return frozenset([self.location])
  ```
- [ ] Update `to_dict()`: change key (line 255)
- [ ] Update `from_dict()`: change `.get('diameter_hexes', 0.0)` → `.get('radius_hexes', 0)` (line 351)
**Notes:** Planet default stays 0 (not a zone occupant). Dyson Spheres get positive values.

#### Task 1.3: Rename on IPlanet protocol [Simple]
**File:** `game/core/protocols.py`
**Tests:** `pytest tests/unit/core/test_protocols.py`
- [ ] Rename `diameter_hexes` property → `radius_hexes` (line 241)
- [ ] Update `IZoneOccupant` docstring reference to "diameter_hexes" (line 263)
**Notes:**

#### Task 1.4: Run targeted tests to verify compile-time correctness [Simple]
**Tests:** `pytest tests/unit/strategy/data/test_stars.py tests/unit/strategy/data/test_planet_zones.py tests/unit/core/test_protocols.py -x` (expect failures from old values)
- [ ] Verify errors are about wrong values/keys, NOT import errors or AttributeError
**Notes:** This is a checkpoint — we expect value failures, not structural failures.

---

### Phase 2: Generation & Game Logic [Medium]
**Objective:** Update star generation, companion placement, orbit calculation, warp distance, and superweapon code.
**Status:** Not Started

#### Task 2.1: Rewrite star size generation function [Medium]
**File:** `game/strategy/data/stars.py`
**Tests:** `pytest tests/unit/strategy/data/test_stars.py -k "test_star_generator"`
- [ ] Rename `_map_radius_to_hexes()` → `_map_solar_radius_to_hex_radius()` (line 346)
- [ ] Change return type annotation to `int`
- [ ] Update function body to return integer radius values:
  ```python
  def _map_solar_radius_to_hex_radius(self, radius_sol, star_type) -> int:
      """Map solar radius to hex radius (1-6).
      1 = center hex only (compact/small stars)
      2 = center + ring 1 (medium stars)
      ...
      6 = center + 5 rings (largest giants/Dyson Spheres)
      """
      if star_type in (StarType.NEUTRON_STAR, StarType.BLACK_HOLE, StarType.WHITE_DWARF):
          return 1
      if radius_sol < 0.8:
          return 1
      if radius_sol < 2.0:
          return 2
      if radius_sol < 5.0:
          return 2
      import math
      log_r = math.log10(radius_sol)
      hex_radius = 1.73 * log_r + 0.8  # Adjusted for radius scale
      hex_radius = min(6, max(1, int(round(hex_radius))))
      return hex_radius
  ```
- [ ] Update all call sites of the old function name (4 locations in stars.py: lines ~486, ~515, ~563, ~608)
- [ ] Update constructor calls from `diameter_hexes=p_hex` → `radius_hexes=p_hex` (4 locations)
**Notes:** The logarithmic formula coefficients need tuning. Old: `3.46*log10(r)+0.61` mapped to diameter 3-11. New target: radius 2-6. Halve the coefficient: `1.73*log10(r)+0.8` approximately maps the same physical stars to half the old values.

#### Task 2.2: Fix companion star placement [Simple]
**File:** `game/strategy/data/stars.py`
**Tests:** `pytest tests/integration/strategy/test_star_generation.py`
- [ ] Update `min_dist_hex` formula (line 507):
  ```python
  # Old: min_dist_hex = int(p_hex * 2) + 2  (diameter × 2 ??)
  # New: place companions at least radius + buffer away
  min_dist_hex = p_hex + 2
  ```
**Notes:** Old formula was `int(diameter * 2) + 2` which was semantically wrong. New: `radius + 2` gives a sensible safe distance.

#### Task 2.3: Fix planet orbit safe_start [Simple]
**File:** `game/strategy/data/planet_gen.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet_gen.py`
- [ ] Update safe_start formula (line 103):
  ```python
  # Old: safe_start = int(primary.diameter_hexes / 2) + 2
  # New: radius_hexes is already the radius
  safe_start = primary.radius_hexes + 2
  ```
**Notes:**

#### Task 2.4: Update warp distance formula [Simple]
**File:** `game/strategy/data/galaxy_warp_generator.py`
**Tests:** `pytest tests/integration/strategy/test_warp_logic_rework.py`
- [ ] Update variable name and formula (line 42-45):
  ```python
  # Old: star_diam = system.primary_star.diameter_hexes
  #      scaled_dist = base_dist + (star_diam * 1.5)
  # New: star_radius is already the meaningful value
  star_radius = system.primary_star.radius_hexes
  scaled_dist = base_dist + (star_radius * 3.0)  # Keep proportional relationship
  ```
**Notes:** Old formula: `15 + diameter * 1.5`. With radius ~= diameter/2, equivalent is `15 + radius * 3.0`.

#### Task 2.5: Update superweapon Dyson Sphere creation [Simple]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py`
- [ ] Update Dyson Sphere creation (line 538):
  ```python
  # Old: diameter_hexes=11.0
  # New: radius_hexes=6 (center + 5 rings = 91 hexes)
  radius_hexes=6,
  ```
- [ ] Update comment on line 478 about zone radius
**Notes:**

#### Task 2.6: Update galaxy entity registry [Simple]
**File:** `game/strategy/data/galaxy_entity_registry.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py`
- [ ] Update 3 checks from `planet.diameter_hexes > 0` → `planet.radius_hexes > 0` (lines 58, 84, 113)
**Notes:** Semantics unchanged — 0 means "not a zone occupant".

#### Task 2.7: Update galaxy spatial index [Simple]
**File:** `game/strategy/data/galaxy_spatial_index.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py`
- [ ] Update comment and check from `diameter_hexes` → `radius_hexes` (lines 176-177)
**Notes:**

---

### Phase 3: UI & Rendering [Simple]
**Objective:** Fix rendering formulas and update UI labels.
**Status:** Not Started

#### Task 3.1: Fix star rendering formula [Simple]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer.py`
- [ ] Update star rendering (line 528):
  ```python
  # Old: screen_star_r = max(3, int(star.diameter_hexes * self.hex_size * self.camera.zoom))
  # New: radius_hexes is the radius in hex units
  screen_star_r = max(3, int(star.radius_hexes * self.hex_size * self.camera.zoom))
  ```
- [ ] Update Dyson Sphere rendering (lines 695-706):
  ```python
  radius_hexes = planet.radius_hexes
  if radius_hexes <= 0:
      radius_hexes = 6  # Dyson Sphere standard size
  # radius_hexes * hex_size * zoom gives screen radius
  screen_radius = max(6, int(radius_hexes * self.hex_size * self.camera.zoom))
  ```
  Also update the variable name from `screen_diameter` to `screen_radius` and fix the image scaling (currently uses `screen_diameter` for both width and height — should use `screen_radius * 2`).
- [ ] Update comment on line 689 and line 705
**Notes:** The key bug fix. With the new semantics, `radius_hexes * hex_size * zoom` gives the correct screen radius.

#### Task 3.2: Fix galaxy test mode rendering & click detection [Simple]
**File:** `game/ui/screens/galaxy_test/system_mode.py`
**Tests:** `pytest tests/unit/ui/screens/test_galaxy_test_screen.py`
- [ ] Update click detection (line 339):
  ```python
  # Old: star_radius = max(8, int(star.diameter_hexes * HEX_SIZE * self.screen.camera.zoom * 0.5))
  # New: radius_hexes is already the radius
  star_radius = max(8, int(star.radius_hexes * HEX_SIZE * self.screen.camera.zoom))
  ```
- [ ] Update second rendering location (line 517, same pattern)
- [ ] Update UI display label (line 391):
  ```python
  # Old: f"Diameter: {star.diameter_hexes:.1f} hexes"
  # New:
  f"Radius: {star.radius_hexes} hexes"
  ```
**Notes:** The `* 0.5` factor was compensating for diameter → radius; no longer needed.

#### Task 3.3: Update detail formatters [Simple]
**Files:** `game/ui/screens/strategy_detail_fmt.py`, `game/ui/screens/strategy_detail_formatter.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_detail_fmt.py`
- [ ] Update `strategy_detail_fmt.py` (line 196):
  ```python
  # Old: text += f"<b>Diam:</b> {star.diameter_hexes:.1f} Hex<br>"
  text += f"<b>Radius:</b> {star.radius_hexes} Hex<br>"
  ```
- [ ] Update `strategy_detail_formatter.py` (line 271):
  ```python
  # Old: text += f"<b>Diam:</b> {obj.diameter_hexes:.1f} Hex<br>"
  text += f"<b>Radius:</b> {obj.radius_hexes} Hex<br>"
  ```
**Notes:** No float formatting needed since values are now integers.

#### Task 3.4: Update visual test script [Simple]
**File:** `scripts/visual_test_galaxy.py`
**Tests:** Manual verification
- [ ] Update star rendering formula (around line 222) to use `radius_hexes`
**Notes:**

---

### Phase 4: Test Updates [Medium]
**Objective:** Update all test files to use new field name and expected values.
**Status:** Not Started

#### Task 4.1: Update `test_stars.py` (core star tests) [Medium]
**File:** `tests/unit/strategy/data/test_stars.py`
**Tests:** `pytest tests/unit/strategy/data/test_stars.py -v`
- [ ] Replace all `diameter_hexes=` with `radius_hexes=` in Star constructors
- [ ] Update serialization test: key `'diameter_hexes'` → `'radius_hexes'`
- [ ] Update `test_star_occupied_hexes_small`: `radius_hexes=1` → 1 hex (was 7)
- [ ] Update `test_star_occupied_hexes_large`: `radius_hexes=6` → 91 hexes (was 127)
- [ ] Update `test_star_occupied_hexes_sub_hex`: `radius_hexes=1` → 1 hex (was 7)
- [ ] Update `test_star_occupied_hexes_with_offset_location`: adjust values
- [ ] Update generator tests: `_map_radius_to_hexes` → `_map_solar_radius_to_hex_radius`
- [ ] Update all assertion comments explaining the math
**Notes:** This is the largest single file change. ~35 test updates.

#### Task 4.2: Update `test_planet_zones.py` [Simple]
**File:** `tests/unit/strategy/data/test_planet_zones.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet_zones.py -v`
- [ ] Replace all `diameter_hexes=` with `radius_hexes=` in Planet constructors
- [ ] Update Dyson Sphere fixture: `radius_hexes=6` (was `diameter_hexes=11.0`)
- [ ] Update `test_dyson_sphere_occupied_hexes_zone`: expect 91 hexes (was 127), radius 5 (was 6)
- [ ] Update `test_occupied_hexes_with_offset_center`: `radius_hexes=3` (was `diameter_hexes=5.0`), expect 19 hexes (was 37)
- [ ] Update all serialization tests: key `'diameter_hexes'` → `'radius_hexes'`
- [ ] Update `test_roundtrip_with_various_diameter_hexes`: new test values `[0, 1, 2, 3, 4, 6]`
- [ ] Rename test class: `TestPlanetDiameterHexesSerialization` → `TestPlanetRadiusHexesSerialization`
**Notes:**

#### Task 4.3: Update `test_galaxy.py` helper functions [Simple]
**File:** `tests/unit/strategy/data/test_galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py -v`
- [ ] Update `make_test_star()`: parameter `diameter_hexes=1.0` → `radius_hexes=1` (line 15)
- [ ] Update `make_test_planet()`: parameter `diameter_hexes=0.0` → `radius_hexes=0` (line 37)
- [ ] Update all call sites of these helpers throughout the file
**Notes:**

#### Task 4.4: Update protocol tests [Simple]
**File:** `tests/unit/core/test_protocols.py`
**Tests:** `pytest tests/unit/core/test_protocols.py -v`
- [ ] Update Star/Planet constructors in IZoneOccupant tests (lines 373-416)
- [ ] Replace `diameter_hexes=` with `radius_hexes=`
**Notes:**

#### Task 4.5: Update integration tests [Medium]
**Files:** Multiple integration test files
**Tests:** `pytest tests/integration/strategy/ -v`
- [ ] `test_star_generation.py`: Update Star constructors and assertions (lines 21, 30, 91, 117, 133)
- [ ] `test_warp_logic_rework.py`: Update Star constructors (lines 21, 30, 91)
- [ ] `test_radiation.py`: Update fixture `diameter_hexes=1.0` → `radius_hexes=1` (line 14)
- [ ] `test_superweapon_integration.py`: Update constructors and assertions (lines 105, 283, 351)
- [ ] `tests/integration/strategy/facade/test_system_dto.py`: Update constructors (line 157)
- [ ] `tests/integration/strategy/facade/test_system_queries.py`: Update (line 28)
- [ ] `tests/integration/colonization/test_planet_specific_colonization.py`: Update (line 65)
**Notes:**

#### Task 4.6: Update remaining unit tests [Medium]
**Files:** Multiple unit test files
**Tests:** `pytest tests/unit/ -v`
- [ ] `test_strategy_renderer.py`: Update mock `star.diameter_hexes` → `star.radius_hexes` (lines 566, 606, 640, 695, 724)
- [ ] `test_strategy_detail_fmt.py`: Update mock (line 56)
- [ ] `test_star_validation.py`: Update constructors (lines 27, 51)
- [ ] `test_star_system_validation.py`: Update constructor (line 70)
- [ ] `test_planet_gen.py`: Update references (lines 40, 281, 285)
- [ ] `test_storm.py`: Update constructor (line 454)
- [ ] `test_storm_generator.py`: Update constructor (line 53)
- [ ] `test_colonize_validator.py`: Update constructors (6 locations)
- [ ] `test_colonize_mission_handler.py`: Update constructors
- [ ] `test_superweapon_order_processor.py`: Update constructors
- [ ] `test_strategy_colonization.py`: Update constructor (line 31)
- [ ] `tests/repro_facade_colonies.py`: Update constructors (lines 32, 66)
**Notes:** Many of these are simple search-and-replace on mock attributes.

#### Task 4.7: Full test suite verification [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] Run full test suite — all 13,040+ tests must pass
- [ ] Fix any remaining failures
**Notes:**

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/` - 13,040 passed, 1 skipped (baseline established)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] Verify no `diameter_hexes` references remain in production code: `grep -r "diameter_hexes" game/`

### Final Verification
- [ ] Run full test suite: `pytest tests/ -n 12` (NOT --testmon, full verification)
- [ ] Visual check: stars render at correct size in galaxy view
- [ ] `grep -r "diameter_hexes" game/ tests/` returns zero results
- [ ] `grep -r "diameter" game/strategy/data/stars.py game/strategy/data/planet.py` returns zero results (except `diameter` in unrelated contexts)

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
- [ ] Phase 1 complete (core data model)
- [ ] Phase 2 complete (generation & game logic)
- [ ] Phase 3 complete (UI & rendering)
- [ ] Phase 4 complete (all tests updated & passing)
- [ ] All tests passing (13,040+)
- [ ] No `diameter_hexes` references remain
- [ ] Audit passed
- [ ] User verified

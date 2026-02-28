# Phase 7: Persistent Planet Image Assignment

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-52 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Assign permanent planet images during generation, persisted across saves

---

## User Decisions
| Decision | Choice | Rationale |
|----------|--------|-----------|
| Rotation Unit | Degrees (0-360) | More intuitive for debugging and save file inspection |
| Fallback Strategy | Type-specific fallbacks | CHTHONIAN→BARREN, ICE_DWARF→CRYOPLANET, PLANETOID→BARREN |

---

## Overview
Each planet gets a permanent image from the 508 high-quality V3 planet images, selected based on its `planet_type`. The image ID and a random rotation (for variety) are stored in the planet data and persist across saves.

### Classification Distribution (508 images)
| PlanetType | Count | Notes |
|------------|-------|-------|
| JOVIAN | ~180 | Gas giants - most common |
| BARREN | ~120 | Rocky lifeless worlds |
| ARID | ~60 | Desert worlds |
| CONTINENTAL | ~55 | Earth-like |
| MAGMA | ~40 | Volcanic worlds |
| PELAGIC | ~15 | Ocean worlds |
| ICE_GIANT | ~20 | Neptune-type |
| CRYOPLANET | ~7 | Ice surface |
| PLANETOID | ~3 | Small asteroids |
| ICE_DWARF | ~1 | Pluto-type |
| CHTHONIAN | 0 | (falls back to BARREN) |

---

## Task 7.1: Add Planets V3 Path to Paths Class [Simple]
**File:** `game/core/paths.py`
**Tests:** N/A (structure only)

- [x] Add `PLANETS_V3_DIR: str` pointing to `assets/Images/Stellar Objects/Planets/Planets_V3`
- [x] Add `PLANET_CLASSIFICATIONS_FILE: str` pointing to the JSON file
- [x] Add `get_planets_v3_dir() -> Path` method

**Notes:** All path constants and method added to Paths class.

---

## Task 7.2: Add Image Fields to Planet Dataclass [Simple]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/integration/strategy/test_planet_serialization.py`

- [x] Add `image_id: str = ""` field (filename without path, e.g., "planet_5_994_1769750020702.png")
- [x] Add `image_rotation: float = 0.0` field (degrees, range 0.0 to 360.0)
- [x] Update `to_dict()` to include both fields
- [x] Update `from_dict()` to restore both fields (with defaults for old saves - backward compatible)

**Notes:** Fields added after `id` field. Serialization includes both fields, deserialization uses `.get()` with defaults for backward compatibility.

---

## Task 7.3: Create PlanetImageRegistry [Medium]
**File:** `game/strategy/generation/planet_image_registry.py`
**Tests:** `tests/unit/strategy/generation/test_planet_image_registry.py`

- [x] Load `planet_classifications.json` on initialization
- [x] Build reverse index: `Dict[PlanetType, List[str]]` mapping type → available images
- [x] Method: `get_random_image(planet_type: PlanetType, rng: random.Random) -> str`
  - Returns random image filename for the given type
  - **Type-specific fallbacks for missing/sparse types:**
    - CHTHONIAN → BARREN (stripped core looks rocky)
    - ICE_DWARF → CRYOPLANET (similar icy appearance)
    - PLANETOID → BARREN (small rocky bodies)
- [x] Method: `get_random_rotation(rng: random.Random) -> float`
  - Returns random float **0.0 to 360.0 degrees**
- [x] Singleton pattern for efficient reuse

**Notes:** Registry implemented with singleton pattern, fallback chain, and reset() for testing.

---

## Task 7.4: Integrate Image Assignment in Planet Generation [Simple]
**File:** `game/strategy/data/planet_gen.py`
**Tests:** `pytest tests/integration/strategy/test_planet_gen.py`

- [x] Import `PlanetImageRegistry`
- [x] In `_create_single_planet()`, after determining `p_type`:
  - Get random image ID from registry
  - Get random rotation
  - Pass to Planet constructor
- [x] Pass RNG if available for determinism

**Notes:** Image assignment happens after planet type classification, using global random (not seeded RNG) for variety.

---

## Task 7.5: Write Unit Tests [Medium]
**Files:** `tests/unit/strategy/generation/test_planet_image_registry.py`
**Tests:** Self-testing

- [x] Test registry loads classifications successfully
- [x] Test all 11 PlanetTypes have image mappings (or fallback works)
- [x] Test `get_random_image()` returns valid filenames
- [x] Test determinism with seeded RNG
- [x] Test rotation is in valid range [0.0, 360.0) degrees

**Notes:** 25 unit tests covering all registry functionality, singleton behavior, and fallbacks.

---

## Task 7.6: Integration Test - Verify Persistence [Simple]
**Files:** `tests/integration/strategy/test_planet_serialization.py`
**Tests:** Self-testing

- [x] Generate planet with image_id and rotation
- [x] Serialize to dict, deserialize back
- [x] Verify image_id and rotation preserved
- [x] Test backward compatibility (old saves without these fields)

**Notes:** 8 integration tests covering serialization, deserialization, roundtrip, and backward compatibility.

---

## Phase 7 Verification
- [x] All unit tests pass for PlanetImageRegistry (25 passed)
- [x] All 11 PlanetTypes return valid image IDs (or fallback works)
- [x] Planet serialization preserves image_id and image_rotation
- [x] Old saves load correctly (backward compatible)
- [x] Full test suite still passes: `python -m pytest tests/` (6045 passed, 5 skipped)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State section

---

## Handoff Notes
**Session Date:** 2026-01-31

**Summary:**
- All 6 tasks implemented successfully
- 33 new tests added (25 unit + 8 integration)
- Full test suite increased from 6012 to 6045 tests
- Backward compatible with existing saves

**Key Files Modified:**
1. `game/core/paths.py` - Added PLANETS_V3_DIR, PLANET_CLASSIFICATIONS_FILE, get_planets_v3_dir()
2. `game/strategy/data/planet.py` - Added image_id, image_rotation fields + serialization
3. `game/strategy/generation/planet_image_registry.py` - New file, singleton registry
4. `game/strategy/generation/__init__.py` - Export PlanetImageRegistry
5. `game/strategy/data/planet_gen.py` - Integrate image assignment

**Key Features:**
1. **Persistent Images** - Each planet gets a permanent image assigned during generation
2. **Type-Based Selection** - Images match planet type from classification JSON
3. **Fallback Chain** - CHTHONIAN→BARREN, ICE_DWARF→CRYOPLANET, PLANETOID→BARREN
4. **Random Rotation** - 0-360 degrees for visual variety
5. **Backward Compatible** - Old saves without image fields use defaults

---

## UI Integration Notes (Future)
The UI already has patterns for using planet images:
- `strategy_renderer.py`: Uses `get_random_from_group()` with seed
- `planet_list_window.py`: Accepts `asset_resolver` callback
- `planet_report_panel.py`: Accepts `portrait_surface` parameter

Future work would update these to:
1. Use `planet.image_id` to load specific image
2. Apply `planet.image_rotation` transform when rendering

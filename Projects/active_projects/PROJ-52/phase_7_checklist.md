# Phase 7: Persistent Planet Image Assignment

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-52 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** In Progress
**Objective:** Assign permanent planet images during generation, persisted across saves

---

## User Decisions
| Decision | Choice | Rationale |
|----------|--------|-----------|
| Rotation Unit | Degrees (0-360) | More intuitive for debugging and save file inspection |
| Fallback Strategy | Type-specific fallbacks | CHTHONIAN→BARREN, ICE_DWARF→CRYOPLANET, PLANETOID→BARREN |

---

## Overview
Each planet gets a permanent image from the 510 high-quality V3 planet images, selected based on its `planet_type`. The image ID and a random rotation (for variety) are stored in the planet data and persist across saves.

### Classification Distribution (510 images)
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
| CHTHONIAN | 0 | (will fallback to BARREN) |

---

## Task 7.1: Add Planets V3 Path to Paths Class [Simple]
**File:** `game/core/paths.py`
**Tests:** N/A (structure only)

- [x] Add `PLANETS_V3_DIR: str` pointing to `assets/Images/Stellar Objects/Planets/Planets_V3`
- [x] Add `PLANET_CLASSIFICATIONS_FILE: str` pointing to the JSON file
- [ ] Add `get_planets_v3_dir() -> Path` method

**Notes:** PLANETS_V3_DIR and PLANET_CLASSIFICATIONS_FILE already added.

---

## Task 7.2: Add Image Fields to Planet Dataclass [Simple]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet.py`

- [ ] Add `image_id: str = ""` field (filename without path, e.g., "planet_5_994_1769750020702.png")
- [ ] Add `image_rotation: float = 0.0` field (degrees, range 0.0 to 360.0)
- [ ] Update `to_dict()` to include both fields
- [ ] Update `from_dict()` to restore both fields (with defaults for old saves - backward compatible)

**Notes:**

---

## Task 7.3: Create PlanetImageRegistry [Medium]
**File:** `game/strategy/generation/planet_image_registry.py`
**Tests:** `tests/unit/strategy/generation/test_planet_image_registry.py`

- [ ] Load `planet_classifications.json` on initialization
- [ ] Build reverse index: `Dict[PlanetType, List[str]]` mapping type → available images
- [ ] Method: `get_random_image(planet_type: PlanetType, rng: random.Random) -> str`
  - Returns random image filename for the given type
  - **Type-specific fallbacks for missing/sparse types:**
    - CHTHONIAN → BARREN (stripped core looks rocky)
    - ICE_DWARF → CRYOPLANET (similar icy appearance)
    - PLANETOID → BARREN (small rocky bodies)
- [ ] Method: `get_random_rotation(rng: random.Random) -> float`
  - Returns random float **0.0 to 360.0 degrees**
- [ ] Singleton pattern for efficient reuse

**Notes:**

---

## Task 7.4: Integrate Image Assignment in Planet Generation [Simple]
**File:** `game/strategy/data/planet_gen.py`
**Tests:** `pytest tests/integration/strategy/test_planet_gen.py`

- [ ] Import `PlanetImageRegistry`
- [ ] In `_create_single_planet()`, after determining `p_type`:
  - Get random image ID from registry
  - Get random rotation
  - Pass to Planet constructor
- [ ] Pass RNG if available for determinism

**Notes:**

---

## Task 7.5: Write Unit Tests [Medium]
**Files:** `tests/unit/strategy/generation/test_planet_image_registry.py`
**Tests:** Self-testing

- [ ] Test registry loads classifications successfully
- [ ] Test all 11 PlanetTypes have image mappings (or fallback works)
- [ ] Test `get_random_image()` returns valid filenames
- [ ] Test determinism with seeded RNG
- [ ] Test rotation is in valid range [0.0, 360.0) degrees

**Notes:**

---

## Task 7.6: Integration Test - Verify Persistence [Simple]
**Files:** `tests/integration/strategy/test_planet_serialization.py`
**Tests:** Self-testing

- [ ] Generate planet with image_id and rotation
- [ ] Serialize to dict, deserialize back
- [ ] Verify image_id and rotation preserved
- [ ] Test backward compatibility (old saves without these fields)

**Notes:**

---

## Phase 7 Verification
- [ ] All unit tests pass for PlanetImageRegistry
- [ ] All 11 PlanetTypes return valid image IDs (or fallback works)
- [ ] Planet serialization preserves image_id and image_rotation
- [ ] Old saves load correctly (backward compatible)
- [ ] Full test suite still passes: `python -m pytest tests/`

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State section

---

## UI Integration Notes (Future)
The UI already has patterns for using planet images:
- `strategy_renderer.py`: Uses `get_random_from_group()` with seed
- `planet_list_window.py`: Accepts `asset_resolver` callback
- `planet_report_panel.py`: Accepts `portrait_surface` parameter

Future work would update these to:
1. Use `planet.image_id` to load specific image
2. Apply `planet.image_rotation` transform when rendering

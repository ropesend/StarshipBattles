# Phase 2: Hex Cluster Generation & Storm Placement

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-189 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Implement irregular hex cluster generation and integrate storm creation into the galaxy system generator.

---

## Tasks

### Task 2.1: Add hex random cluster utility [Simple]
**File:** `game/core/hex_math.py`
**Tests:** `pytest tests/unit/core/test_hex_math.py`

- [ ] Add `import random` at top if not present
- [ ] Add function `hex_random_cluster(center: HexCoord, target_size: int, rng: random.Random, avoid: FrozenSet[HexCoord] = frozenset()) -> FrozenSet[HexCoord]`:
  - Start with `cluster = {center}`, `frontier = set(hex_neighbors(center)) - avoid - cluster`
  - While `len(cluster) < target_size` and `frontier` not empty:
    - Pick random hex from frontier (via `rng.choice(list(frontier))`)
    - Add to cluster
    - Add its neighbors to frontier (excluding avoid, cluster)
  - Convert cluster to offsets relative to center: `frozenset({h - center for h in cluster})`
  - Return frozenset of offsets (includes HexCoord(0,0) for center)
- [ ] Write tests:
  - [ ] Produces connected hex set of target_size (when possible)
  - [ ] Avoids excluded hexes (pass avoid set, verify no intersection)
  - [ ] Single-hex cluster (target_size=1) returns just `{HexCoord(0,0)}`
  - [ ] Deterministic with seeded RNG
  - [ ] Gracefully handles target_size larger than available frontier (returns smaller cluster)

**Notes:**

### Task 2.2: Create storm type definitions [Simple]
**File:** `data/storms.json` (NEW)
**Tests:** Manual validation

- [ ] Create JSON file with structure:
  ```json
  {
    "version": "1.0",
    "storm_types": {
      "ion_storm": {
        "name": "Ion Storm",
        "description": "Electromagnetic disturbance that disrupts shields and sensors",
        "effects": { "shield_capacity_mult": 0.5, "strategic_mult": 0.8 },
        "size": { "min": 2, "max": 5 },
        "image_variants": [1, 2, 3]
      },
      "plasma_storm": { ... },
      "gravitational_anomaly": { ... },
      "radiation_belt": { ... },
      "dark_nebula": { ... }
    }
  }
  ```
- [ ] Define 5 storm types with balanced effects (see plan.md Phase 2 for values)
- [ ] Ensure no storm type has damage_per_tick * 100 > reasonable ship HP (not immediately lethal)
- [ ] Ensure all strategic_mult >= 0.2 (fleets can always escape)

**Notes:**

### Task 2.3: Create StormGenerator [Medium]
**File:** `game/strategy/generation/storm_generator.py` (NEW)
**Tests:** `pytest tests/unit/strategy/generation/test_storm_generator.py`

- [ ] Create `StormGenerator` class:
  - `__init__(self, storm_defs: dict)` - accepts parsed storms.json data
  - `generate_storms(self, system: StarSystem, blueprint_config: dict, rng: random.Random) -> List[Storm]`:
    - Read `count` range from `blueprint_config.get('storms', {}).get('count', {'min': 0, 'max': 0})`
    - Roll count via `rng.randint(min, max)`
    - For each storm:
      - Select type from `allowed_types` (or all types if not specified)
      - Find valid center hex via `_find_valid_center()`
      - Generate cluster via `hex_random_cluster()` with size from type def
      - Select random `image_variant` from type def
      - Roll `intensity` from config range (default 0.3-1.0)
      - Create Storm instance with generated name (e.g., "{TypeName} {GreekLetter}")
    - Return list of Storm objects
  - `_collect_occupied_hexes(self, system: StarSystem, existing_storms: List[Storm]) -> Set[HexCoord]`:
    - Collect all star occupied_hexes
    - Collect all planet locations
    - Collect all existing storm occupied_hexes
    - Return union
  - `_find_valid_center(self, system: StarSystem, occupied: Set[HexCoord], rng: random.Random) -> Optional[HexCoord]`:
    - Define search radius based on system size (e.g., max star orbital distance + margin)
    - Try up to 50 random hexes in range
    - Return first hex not in occupied set, or None if all attempts fail
- [ ] Write tests:
  - [ ] Generates correct number of storms per blueprint config
  - [ ] Storms avoid star occupied hexes
  - [ ] Storms avoid planet hexes
  - [ ] Storms don't overlap each other
  - [ ] Cluster sizes within type definition bounds
  - [ ] Returns empty list when blueprint has no storm config
  - [ ] Seeded RNG produces deterministic results

**Notes:**

### Task 2.4: Integrate storm generation into galaxy system generator [Simple]
**File:** `game/strategy/data/galaxy_system_generator.py`
**Tests:** `pytest tests/unit/strategy/data/ tests/integration/strategy/`

- [ ] Add `StormGenerator` import
- [ ] Load storms.json data once (cached on generator or passed in)
- [ ] After planet generation, call `storm_generator.generate_storms(system, blueprint_config, rng)`
- [ ] Assign generated storms to `system.storms`
- [ ] Verify storm zones get registered via `Galaxy.add_system()` (which loops `system.storms`)
- [ ] Run existing galaxy generation tests to verify no regressions

**Notes:** May need to pass blueprint config through to the generation method.

### Task 2.5: Add storm config to system blueprints [Simple]
**File:** `data/system_blueprints.json`
**File:** `game/strategy/generation/loaders/system_blueprints_loader.py`
**Tests:** `pytest tests/unit/strategy/generation/test_system_blueprints_loader.py`

- [ ] Add `"storms"` section to each blueprint:
  - `solar_like`: `{"count": {"min": 0, "max": 2}, "allowed_types": ["ion_storm", "plasma_storm", "dark_nebula"]}`
  - `red_dwarf_pack`: `{"count": {"min": 1, "max": 3}, "allowed_types": ["radiation_belt", "plasma_storm"]}`
  - `binary_no_planets`: `{"count": {"min": 0, "max": 1}, "allowed_types": ["gravitational_anomaly"]}`
  - `empty_warp_hub`: `{"count": {"min": 0, "max": 3}, "allowed_types": ["dark_nebula", "ion_storm"]}`
  - Other blueprints: sensible defaults per star environment
- [ ] Update `SystemBlueprintsLoader` if it validates schema (add `storms` to allowed keys)
- [ ] Run blueprint loader tests

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass: `pytest tests/ --testmon`
- [ ] Generate a galaxy and verify storms exist in systems (manual or integration test)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3

# Phase 2: F-A-009 — split `planet_gen.py` by sub-concern (or document deferral)

**Status:** Complete (split landed — planet_gen_surface.py)
**Depends on:** Phase 1 complete (fleet_serde extraction landed and stable)
**Review Mode:** standard
**Files:**
- `game/strategy/data/planet_gen.py` (production; may edit or read-only)
- `game/strategy/data/planet_gen_*.py` (production; new, conditional on split decision)
- Decision documented in `Projects/active_projects/PROJ-459/decisions.md`

**Objective:** Read `planet_gen.py` end-to-end. Either: split into sibling module(s) along a clean axis to drop the file under 500 LOC, OR: document the structural reason for deferring with a concrete next-touch criterion. Closes F-A-009 either way (closure = "split done" OR "deferred with rationale").

**Codex r4 guidance:** "If no clean axis emerges from the read, document the structural reason in `decisions.md` and defer the split (don't force a bad cut)."

---

## Tasks

### Task 2.1: Read `planet_gen.py` end-to-end and identify axes [Simple]

**File:** `game/strategy/data/planet_gen.py` (610 LOC, 1 class `PlanetGenerator` + 1 lru_cache helper + 13 private methods)

- [x] Read the file in full. Build a per-method LOC + dependency table:
  | Method | Approx LOC | Uses | Mutates self? |
  |--------|------------|------|----------------|
  | `_get_planetary_ids` (module fn) | 3 | ResourceCatalog | n/a |
  | `__init__` | 3 | _image_registry | yes |
  | `generate_system_bodies` | ~45 | many | yes |
  | `_generate_orbital_slots` | ~90 | math, hex_circle_filled | no |
  | `_collect_star_exclusion_zones` | ~20 | hex_ring | no |
  | `_generate_mass_constrained` | ~40 | random, planet_physics | no |
  | `_generate_moons` | ~37 | random, planet_physics | no |
  | `_calculate_moon_chance` | ~33 | (pure math) | no |
  | `_generate_moon_mass` | ~19 | random | no |
  | `_create_planet_objects` | ~27 | _create_single_planet | no |
  | `_create_single_planet` | ~62 | many (_image_registry, generate_atmosphere, etc.) | no |
  | `_generate_surface_flags` | ~28 | random | no |
  | `_determine_type` | ~88 | PlanetType | no |
  | `_generate_resources` | ~70 | random, _get_planetary_ids | no |
- [x] Identify candidate axes:
  - **Orbital arrangement** cluster: `_generate_orbital_slots` + `_collect_star_exclusion_zones` + `_generate_mass_constrained` (~150 LOC; pure math + hex geometry)
  - **Moon generation** cluster: `_generate_moons` + `_calculate_moon_chance` + `_generate_moon_mass` (~90 LOC; pure math)
  - **Body construction** cluster: `_create_planet_objects` + `_create_single_planet` (~90 LOC; relies on `_image_registry`)
  - **Surface/type/resource** cluster: `_generate_surface_flags` + `_determine_type` + `_generate_resources` (~186 LOC; pure functions of inputs)
- [x] Determine which methods truly bind to `self` (i.e., need `self._image_registry`) vs. which are static-like and could become module-level helpers.
- [x] Pick the cleanest axis or declare "no clean cut" with reasoning.

### Task 2.2: Decision branch — split or defer [Simple]

**If a clean axis emerges (likely the surface/type/resource cluster, ~186 LOC, all pure functions of inputs):**

Proceed to Task 2.3 (split).

**If no clean axis emerges (e.g., methods share state too tightly, or each "subconcern" is <50 LOC and not worth a file):**

- [x] Document in `decisions.md`:
  - Date: 2026-MM-DD
  - Decision: "F-A-009 planet_gen.py split deferred."
  - Rationale: [specific structural reason — e.g., "Moon methods are pure math but only 90 LOC; surface/type/resource cluster is 186 LOC but `_determine_type` shares random-state with `_generate_resources` via the seeded RNG. Splitting would require threading random.Random through the call chain, which is more disruption than the LOC win justifies."]
  - Next-touch criterion: [concrete observable — e.g., "Split when atmosphere generation grows past 200 LOC", or "Split when a non-orbital generator emerges that doesn't fit into `_create_single_planet`", or "Split when planet_gen.py passes 700 LOC", etc.]
- [x] Update `findings/PROJ-459_findings.md`: F-A-009 status → "deferred with concrete next-touch criterion (see decisions.md 2026-MM-DD)".
- [x] Skip Tasks 2.3 + 2.4 + 2.5; proceed directly to Task 2.6 (commit).

### Task 2.3: Execute the split (if clean axis exists) [Medium]

**Files:** `game/strategy/data/planet_gen.py` (edit), `game/strategy/data/planet_gen_<axis>.py` (new)
**Tests:** `pytest tests/unit/strategy/data/test_planet_gen.py tests/unit/strategy/generation/ -q -n 4`

- [x] Create the sibling module(s). Naming convention: `planet_gen_<axis>.py` (e.g., `planet_gen_surface.py`, `planet_gen_moons.py`, `planet_gen_orbits.py`).
- [x] Move the methods. Convert them from `PlanetGenerator` methods to module-level functions taking explicit arguments (the registry, the RNG, the input state). Drop the `self.` references.
- [x] Update `PlanetGenerator` to call into the new module(s).
- [x] Preserve seed-determinism: any RNG state passed in must reach the same calls in the same order, or the seeded test fixtures break.
- [x] Verify imports update cleanly.

### Task 2.4: Verify behavior unchanged [Simple]

**Tests:**
```powershell
pytest tests/unit/strategy/data/test_planet_gen.py tests/unit/strategy/generation/ -q -n 4
python Tools/test_sharded/test_sharded.py
```

- [x] All planet_gen unit tests green.
- [x] All strategy generation tests green.
- [x] Sharded suite green; same count as Phase 1.
- [x] Seed-determinism preserved: a fixed-seed galaxy gen produces the same bodies before and after the split. (Verified by the existing test suite; spot-check one specific seed if needed.)

### Task 2.5: Verify LOC target met [Simple]

- [x] Re-measure `planet_gen.py`. Target: under 500 LOC.
- [x] If still over: was the split too small? Pick another axis from Task 2.1. Iterate.
- [x] Update `findings/PROJ-459_findings.md`: F-A-009 status → "closed via Phase 2 split into planet_gen_<axis>.py".

### Task 2.6: Commit [Simple]

- [x] Commit message (split branch): `PROJ-459 Phase 2: split planet_gen.py into planet_gen_<axis>.py (closes F-A-009; ~XXX LOC drop)`
- [x] Commit message (defer branch): `PROJ-459 Phase 2: defer planet_gen.py split with rationale (F-A-009 deferred per decisions.md)`
- [x] Update `plan.md` Current State.

---

## Phase Completion Checklist
- [x] planet_gen.py read end-to-end; per-method LOC + dependency table built
- [x] Decision recorded (split or defer)
- [x] If split: planet_gen.py under 500 LOC; sibling module(s) created
- [x] If defer: concrete next-touch criterion in decisions.md
- [x] Tests green (`pytest tests/unit/strategy/data/test_planet_gen.py tests/unit/strategy/generation/`)
- [x] Sharded suite green
- [x] F-A-009 status updated in findings file (closed-via-split or deferred-with-rationale)
- [x] No behavior change (seed-determinism verified)

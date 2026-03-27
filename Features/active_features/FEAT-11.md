# FEAT-11: Data-Driven Planet Resource Generation with Mass Scaling

## Description
Planet resource quantities and quality distribution should be driven by JSON data files rather than hardcoded constants in `planet_gen.py`. Resource quantities should scale with planet mass (higher mass = more quantity, lower quality; lower mass = less quantity, higher quality). An average Earth-mass planet should start with approximately 10 million of each resource, with semi-random variance.

### Key Changes
1. **Expand `data/astrophysics.json`** with a resource generation section containing:
   - Per-resource-type generation curves (quantity and quality vs. mass)
   - Planet-type affinity modifiers (e.g., MAGMA planets favor Radioactives, PELAGIC favors Organics)
   - Baseline quantity target (~10M for Earth-mass) and scaling parameters
   - Quality inversion curve parameters (low mass = high quality, high mass = low quality)
   - Randomness/variance controls
2. **Remove all hardcoded resource generation constants** from `planet_gen.py` (~27 values including log-mass bounds 20.0/28.0, quantity/quality weight splits 0.7/0.3, max quantity cap of 1,000,000)
3. **Load and apply** the new JSON-driven parameters during `PlanetGenerator._generate_resources()`

### Current State (for reference)
- `planet_gen.py` lines 510-543 contain all resource generation logic with hardcoded constants
- Quantity formula: `size_factor * 0.7 + random * 0.3`, capped at 1,000,000
- Quality formula: `(1.0 - size_factor) * 0.7 + random * 0.3`, scaled to 0-100
- The 5 planet resources are: Metals, Organics, Vapors, Radioactives, Exotics (defined in `game/core/constants.py`)

## Priority
Medium

## Status
Pending

## Analysis Report

### Architecture Impact
- **Fully contained within Strategy layer** — no cross-layer dependency violations
- Primary change: `game/strategy/data/planet_gen.py` `_generate_resources()` method (lines 510-543)
- Data file: `data/astrophysics.json` to be expanded with `resource_generation` section
- `Planet.resources` dict structure unchanged (`{resource: {quantity, quality}}`) — all downstream consumers (HarvestingEngine, UI panels, serialization) unaffected
- `PlanetGenerator` instantiated in `Galaxy.__init__()`, called via `GalaxySystemGenerator.generate_planets()`
- `_generate_resources(mass)` signature needs expansion to `_generate_resources(mass, planet_type)` — planet_type already available at call site

### Dependency Map
**Generation chain:** `Galaxy` → `GalaxySystemGenerator` → `PlanetGenerator._generate_resources()` → `Planet.resources`
**Consumers (no changes needed):**
- `HarvestingEngine.process_harvesting_tick()` — reads `quantity`/`quality`, agnostic to generation formula
- `Planet.to_dict()`/`from_dict()` — serialization format preserved
- UI panels (`planet_report_panel.py`, `planet_production_display.py`) — display only
- `EmpireEconomyCalculator` — uses resource data via harvesting

**Blast radius: 8 files total**
- 2-3 source files requiring modification (planet_gen.py, astrophysics.json, possibly a new config class)
- 4 test files requiring assertion updates (`test_planet_gen.py`, `test_economy_e2e.py`, `test_harvesting.py`, `test_roundtrip_planet.py`)

**Hardcoded constants to remove (9 actual values):**
| Constant | Value | Purpose |
|----------|-------|---------|
| `min_log` | 20.0 | Log10 mass lower bound |
| `max_log` | 28.0 | Log10 mass upper bound |
| qty size_bias | 0.7 | Deterministic weight for quantity |
| qty randomness | 0.3 | Random weight for quantity |
| qty cap | 1,000,000 | Max quantity per resource |
| quality scale | 100.0 | Quality normalized to [0, 100] |
| qual size_bias | 0.7 | Deterministic weight for quality |
| qual randomness | 0.3 | Random weight for quality |
| qual_bias | `1.0 - size_factor` | Quality inversely correlated with size |

### Similar Patterns Found
**Established pattern to follow:** `ClassificationConfig` + `AstrophysicsLoader` dual pattern
- `game/strategy/data/classification_config.py` — Config class with `@lru_cache(maxsize=1)`, hardcoded defaults, JSON override
- `game/strategy/generation/loaders/astrophysics_loader.py` — Loader with `DEFAULT_PATH`, `load()`, `_validate_schema()`, accessor methods
- `game/core/json_utils.py` — `load_json_required()` for consistent error handling
- Planet classification already uses this exact pattern for type thresholds loaded from `astrophysics.json`

**No discrepancies found** between documented patterns and actual code in the target area.

### Scope Assessment
**Rating: Moderate** (4-5 files, single layer, follows existing pattern, ~150-200 LOC)

| Criterion | Assessment |
|-----------|------------|
| Files affected | 4-5 (1 JSON, 1-2 code, 2 test) |
| Layers touched | Strategy only |
| New abstractions | 1 (ResourceGenerationConfig — follows ClassificationConfig template) |
| Cross-cutting? | No |
| Estimated LOC | 150-200 new/modified |

**Gameplay impact:** Current Earth-mass baseline is ~600K per resource (capped at 1M). Feature requests ~10M — a 10x increase. This makes resource depletion essentially impossible during normal play, shifting the bottleneck entirely to harvesting facility throughput. This is a **tuning decision** adjustable via JSON after implementation.

**Recommendation:** Implement as a FEATURE, not a Project. Well-contained, follows established patterns, straightforward scope.

## Requirements Context

**Baseline Quantity:**
- 10M is the Earth-mass baseline (average). Quantity is approximately proportional to mass.
- Larger planets get proportionally more total resources, smaller get less.

**Per-Resource Composition by Planet Type:**
- Gas giants should have more Vapors and less Metals.
- Rocky/terrestrial should favor Metals.
- Other planet types should have thematic resource distributions (designer's choice for initial values).
- All composition choices must be data-driven in JSON for easy tuning.

**Scope:** Data-drive EVERYTHING — all resource generation constants, quality curves, per-resource variance, randomness controls, and affinity modifiers must be in JSON. Full flexibility.

**Affinity Strength:** Start with Moderate range (1.5-2.5x favored, reduced for non-favored), fully tunable via JSON.

**Iteration:** All features ship together in one pass — JSON externalization, mass scaling, quality inversion, AND planet-type affinities.

**Edge Cases:**
- Every planet should still have *some* of each resource (no zeros).
- Quality inversion maintained: small planets = high quality, large planets = low quality.

## Complexity Assessment

**Rating: Moderate**

| Criterion | Estimate |
|-----------|----------|
| Lines of Code (new + modified) | ~250-300 |
| Files Requiring Changes | 5-6 |
| New Abstractions | 1 class (`ResourceGenerationConfig`) following `ClassificationConfig` template |
| Test Infrastructure | Existing test infrastructure supports this area; ~80-100 LOC new tests |
| Cross-Layer Changes | None — fully within Strategy layer |

**Files requiring changes:**
1. `data/astrophysics.json` — Add `resource_generation` section (~40-50 lines of JSON)
2. `game/strategy/data/planet_gen.py` — New `ResourceGenerationConfig` class + refactored `_generate_resources()` (~120 LOC)
3. `game/strategy/generation/loaders/astrophysics_loader.py` — Schema validation for new section (~10 LOC)
4. `tests/unit/strategy/data/test_planet_gen.py` — Update + new resource generation tests (~80 LOC)
5. `tests/integration/strategy/test_planet_physics.py` — Possible fixture updates (~10 LOC)

## Implementation Strategy

### Ordered Implementation Plan

**Step 1: Design JSON schema** (data/astrophysics.json)
- Add `resource_generation` section with:
  - `mass_scaling`: min/max log-mass bounds, Earth-mass reference point
  - `quantity_parameters`: earth_mass_baseline (10M), determinism/randomness weights
  - `quality_parameters`: max_quality (100), inversion curve parameters
  - `planet_type_affinities`: matrix of planet_type → resource → multiplier
  - `resource_defaults`: per-resource base parameters (if any resource needs unique curves)

**Step 2: Create ResourceGenerationConfig** (in planet_gen.py or separate file)
- Follow `ClassificationConfig` pattern: `@lru_cache(maxsize=1)` singleton
- Load from `astrophysics.json` `resource_generation` section
- Hardcoded defaults as fallback
- Accessor methods for mass scaling, affinities, etc.

**Step 3: Update AstrophysicsLoader**
- Add schema validation for `resource_generation` section
- Add accessor method `get_resource_generation(data)`

**Step 4: Refactor `_generate_resources()`**
- Change signature: `_generate_resources(self, mass, planet_type)`
- Replace all hardcoded constants with config lookups
- Implement mass-proportional quantity scaling (10M at Earth-mass)
- Apply planet-type affinity multipliers from config
- Ensure minimum floor (no zero resources)

**Step 5: Update call site**
- `_create_single_planet()` already has `planet_type` — pass it to `_generate_resources()`

**Step 6: Write tests (TDD)**
- Test config loading from JSON and fallback defaults
- Test Earth-mass baseline yields ~10M per resource
- Test mass proportionality (2x mass ≈ 2x quantity)
- Test quality inversion (small planet = high quality)
- Test planet-type affinities (MAGMA → boosted Radioactives)
- Test minimum floor (no zero resources)

**Step 7: Update existing test assertions**
- Adjust any tests that assert specific resource quantities against the old 1M cap

### Test Strategy
- Write config loading tests first (TDD)
- Write formula tests with known inputs/outputs
- Run full suite to catch regressions in economy/harvesting tests

## Work Log
- 2026-03-25: Created from QA Session 20260325_191105.
- 2026-03-27: Deep Investigation initiated (Protocol 02b). Phase 1 agent swarm completed — architecture impact, dependency mapping, pattern search, and scope assessment all confirm this is a Moderate-complexity feature fully contained within the Strategy layer.
- 2026-03-27: Phase 2 user interview completed. Key decisions: 10M Earth-mass baseline with mass-proportional scaling, data-drive everything, moderate affinities (1.5-2.5x) fully JSON-tunable, all features ship together. Phase 3 complexity assessment: Moderate. Phase 4 implementation strategy defined.

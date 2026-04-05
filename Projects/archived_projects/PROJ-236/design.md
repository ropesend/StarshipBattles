# PROJ-236: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### stars.py (705 lines, StarGenerator class)
- 117+ bare magic numbers across 8 categories
- 73-line if/elif chain in `_determine_type_and_radius` (lines 277-337)
- Unbounded `while True` loop in `_generate_mass` (line 238)
- 4 existing module-level constants (SOLAR_MASS_KG, etc.)
- 33 files import from this module (6 production, 27 test/script)
- Only 1 production instantiation of StarGenerator (in `galaxy.py:182`)

### planet_gen.py (600 lines, PlanetGenerator class)
- 50+ bare magic numbers across 6 categories
- `_determine_type` already uses ClassificationConfig (good, but has 5 hardcoded chthonian values)
- `_generate_resources` already uses ResourceGenerationConfig (good, but has local `_RAMP_C = 24.8`)
- 8 files import from this module (4 production, 4 test)
- Only 1 production instantiation of PlanetGenerator (in `galaxy.py:184`)

### Existing Config Pattern (classification_config.py, resource_generation_config.py)
- JSON-backed via `data/astrophysics.json` loaded through `AstrophysicsLoader`
- `DEFAULT_*` class dicts, `_load_from_json()` / `_use_defaults()`, `@lru_cache(maxsize=1)` getter
- Identical error handling: catches `(ImportError, FileNotFoundError, OSError, KeyError, TypeError, ValueError)`
- Tests clear cache via `get_*_config.cache_clear()` before and after tests

## Swarm Findings Summary

### Architecture (Agent 4)
- Placement in `game/strategy/data/` confirmed correct (both existing configs live there)
- No `configs/` subpackage exists; flat directory with 39 Python files
- `AstrophysicsLoader` has zero imports from `game/strategy/data/` — no circular import risk
- `game/strategy/data/__init__.py` exports nothing — safe to add files

### Dependencies (Agent 2)
- **stars.py exports:** `SOLAR_MASS_KG`, `SOLAR_RADIUS_M`, `SOLAR_LUMINOSITY_W`, `SOLAR_TEMP_K`, `StarType`, `Spectrum`, `Star`, `StarGenerator`
- **planet_gen.py exports:** `PlanetGenerator`
- **Config getters used only in planet_gen.py** (lazy imports inside methods)
- No circular imports possible with new config files
- `Star.from_dict()` loads directly from save data — does NOT call `_determine_type_and_radius`

### Test Impact (Agent 1)
- **115 existing test methods** across 8 test files
- **High risk (36 methods):** Directly call refactored private methods
- **Medium risk (28 methods):** Behavior-dependent on generation parameters
- **Low risk (51 methods):** Public API only, unaffected
- **New tests needed:** ~36 methods across 4 new test files
- **Critical:** 14 parametrized classification tests in `test_planet_classification_logic.py` must pass

### Risk Assessment (Agent 3) — KEY FINDING
- **Full table-driven refactor rated HIGH RISK** — branches are structurally diverse
- **Recommended: Extract only Stefan-Boltzmann group** (RED_GIANT, BROWN_DWARF, WHITE_DWARF)
- These 3 types share identical formula: `luminosity = radius² × (temp/SOLAR_TEMP_K)⁴`
- MAIN_SEQUENCE (52.5% of stars) should remain explicit — too critical and too clean to abstract
- BLUE_GIANT has 3 independent random multipliers — unintuitive to parameterize
- NEUTRON_STAR and BLACK_HOLE are 8 lines each of fixed values — not worth abstracting

### Data Flow (Agent 5)
- Star spectrum → planet blackbody temperature (4th-root sensitivity)
- Any floating-point difference cascades through gas retention thresholds (step functions)
- Hex radius rounding boundaries can shift planet placement
- Saves load exact values (no regeneration) — save compatibility not affected
- **Implication:** Behavioral parity must be exact. Characterization tests with seeded random are critical.

### Key Patterns to Reuse
- **Config class template:** `resource_generation_config.py` (most canonical — consistent `.get()` usage)
- **Cache clearing in tests:** `get_*.cache_clear()` before and after each test
- **Late imports in methods:** Config getters imported inside methods (e.g., `planet_gen.py:458`)
- **Stefan-Boltzmann formula:** `luminosity = (radius ** 2) * ((temperature / SOLAR_TEMP_K) ** 4)`

### Dependencies & Risks
1. **Floating-point parity** — Star spectrum changes cascade to planet temperatures. Mitigation: seeded characterization tests pinning exact outputs.
2. **AstrophysicsLoader schema validation** — New required sections will break old JSON files. Mitigation: Per migration policy, no backward-compat shims.
3. **lru_cache in tests** — Config caching can cause test pollution. Mitigation: cache_clear() in test setup/teardown.
4. **Unbounded while-True loop** — `_generate_mass` (line 238) has no iteration cap. Mitigation: Add cap with log-space fallback.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

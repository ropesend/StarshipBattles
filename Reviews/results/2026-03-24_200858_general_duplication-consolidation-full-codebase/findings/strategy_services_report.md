# Strategy Services & Generation Duplication Report

**Date:** 2026-03-24
**Scope:** `game/strategy/services/`, `game/strategy/generation/`, `game/strategy/systems/`, `game/strategy/validation/`, `game/strategy/formulas/`, `game/strategy/adapters/`, `game/strategy/interfaces/`
**Files reviewed:** 37 Python files

## Summary

The strategy services and generation packages are generally well-factored, with prior PROJ-108/PROJ-127/PROJ-204/PROJ-209 refactors having already consolidated many patterns. However, several areas of duplicated logic remain:

- **6 findings total**: 2 MAJOR, 4 MINOR
- Most significant: Population extraction logic duplicated within CargoTransferService, and superweapon validation methods sharing a repetitive ability-check pattern
- The density primitives share a hex distance calculation pattern, but it is appropriately handled by a shared utility (`hex_axial_to_cartesian`)
- The loader classes (AstrophysicsLoader, SystemBlueprintsLoader, GalaxyLayoutsLoader) share structural similarity but serve distinct data schemas, so consolidation is not recommended

---

## Findings

#### MAJOR: Population Extraction Logic Duplicated Within CargoTransferService
**ID:** DUP-SS-01
**Location:** `game/strategy/services/cargo_transfer_service.py:100-128` and `game/strategy/services/cargo_transfer_service.py:160-178`
**Issue:** `get_load_items()` and `get_inventory_items()` both contain nearly identical logic for extracting population data from PlanetInfo objects. Both iterate `population_details` tuples, extract `(race_id, count, happiness)`, build item dicts with label/cargo_type/species_id/max_amount, and fall back to `total_population` when details are empty. The code is structurally identical with minor label formatting differences.
**Impact:** 30+ lines of duplicated population extraction logic. Changes to population item format must be updated in two places. Bug risk if one is updated and the other forgotten.
**Recommendation:** Extract a shared `_extract_population_items(planet_info, label_prefix)` helper that both methods call. The helper returns a list of item dicts from population_details or total_population fallback.
**Effort:** Simple

#### MAJOR: Superweapon Validation Methods Share Repetitive Ability-Check Pattern
**ID:** DUP-SS-02
**Location:** `game/strategy/validation/superweapon_validator.py:36-65`, `67-100`, `102-147`, `149-196`, `198-231`
**Issue:** Five validation methods (`validate_implode_planet`, `validate_stellerate_star`, `validate_open_warp_point`, `validate_close_warp_point`, `validate_create_dyson_sphere`) all follow the same pattern:
1. Optionally check for ability via `find_ship_with_ability(fleet, "AbilityName", registry)`
2. Return error if ship is None: `"No ship in fleet has {AbilityName} ability."`
3. Check location (fleet at star system)
4. Check domain-specific constraint

The ability-check block (lines 57-63, 83-89, 123-129, 170-176, 214-220) is copy-pasted with only the ability name string changing. Three of the five methods also share the "fleet must be at a star system" check.
**Impact:** ~50 lines of repeated boilerplate. Adding a new superweapon requires copying the same pattern. The ability-check pattern appears 5 times identically.
**Recommendation:** Extract a `_require_ability(fleet, ability_name, registry) -> Optional[ValidationResult]` helper that returns the error result if ability is missing, or None if present. Extract `_require_at_star_system(galaxy, fleet) -> Optional[ValidationResult]` for the location check. Each validate method becomes a short pipeline of these checks plus its domain logic.
**Effort:** Simple

#### MINOR: Two Component Iteration Implementations
**ID:** DUP-SS-03
**Location:** `game/strategy/services/component_inspector.py:82-130` (`iterate_design_components`) and `game/strategy/services/ship_stats_calculator.py:548-577` (`_iterate_design_components`)
**Issue:** Both iterate through design components from design_data. `component_inspector.iterate_design_components()` iterates layers directly and yields `(comp_entry, comp_def, abilities)`. `ShipStatsCalculator._iterate_design_components()` uses `iter_layers_and_components()` from `core.patterns.layer_iterator` and returns `(layer_name, comp_entry, comp_def)`. These are similar but not identical -- ShipStatsCalculator needs the layer_name and uses the core layer iterator, while component_inspector handles inline abilities fallback. The core `iter_layers_and_components` is the canonical low-level iterator; the component_inspector adds ability resolution on top.
**Impact:** Two parallel component iteration paths exist. Divergence risk is mitigated because ShipStatsCalculator delegates to the core iterator, but the component_inspector reimplements layer iteration manually instead of building on the same core iterator.
**Recommendation:** Refactor `component_inspector.iterate_design_components()` to use `iter_layers_and_components()` from core as its foundation (like ShipStatsCalculator does), then add the ability resolution layer on top. This eliminates the redundant layer iteration code in component_inspector while preserving its higher-level interface.
**Effort:** Medium

#### MINOR: Name Slugification Functions
**ID:** DUP-SS-04
**Location:** `game/strategy/systems/race_library.py:22-41` (`_slugify`) and `game/strategy/systems/design_library.py:391-408` (`_sanitize_design_id`)
**Issue:** Both functions convert user-facing names to filesystem-safe identifiers. `_slugify` converts to lowercase, replaces spaces/hyphens with underscores, removes non-alphanumeric chars, strips leading/trailing underscores, and limits to 50 chars. `_sanitize_design_id` keeps alphanumeric + space/hyphen/underscore, replaces spaces with underscores. They have slightly different behavior but serve the same purpose.
**Impact:** Two similar but subtly different slugification functions. Low risk since they're isolated to their respective modules, but inconsistent behavior between race IDs and design IDs.
**Recommendation:** Extract a shared `slugify(name, max_length=50)` utility to `game/core/string_utils.py` or similar. Both libraries can use the same function with optional parameter differences.
**Effort:** Simple

#### MINOR: Hex Axial Distance Calculation Inlined in Density Primitives
**ID:** DUP-SS-05
**Location:** `game/strategy/generation/density/primitives/radial.py:51` and `game/strategy/generation/density/primitives/ring.py:51` and `game/strategy/generation/region_classifier.py:167,217,265`
**Issue:** The hex axial distance-squared formula `dq * dq + dr * dr + dq * dr` is inlined in multiple places: RadialPrimitive, RingPrimitive, and RegionClassifier (3 occurrences). This formula converts axial hex coordinates to a Euclidean-like distance metric.
**Impact:** The formula is short (one expression), so duplication impact is low. However, if the distance metric ever needed adjustment, all 5 call sites would need updating.
**Recommendation:** Consider adding `hex_axial_distance_sq(dq, dr) -> float` to `game/core/hex_math.py` alongside the existing `hex_axial_to_cartesian`. The density primitives and region classifier can then call this utility. Low priority given the formula's simplicity.
**Effort:** Simple

#### MINOR: Loader Classes Share Structural Pattern
**ID:** DUP-SS-06
**Location:** `game/strategy/generation/loaders/astrophysics_loader.py`, `game/strategy/generation/loaders/system_blueprints_loader.py`, `game/strategy/generation/loaders/galaxy_layouts_loader.py`
**Issue:** All three loaders follow the same structural pattern: DEFAULT_PATH class attribute, `load()` method that calls `load_json_required()` and validates schema, `_validate_schema()` that checks required keys and raises `ValidationException` with `ErrorCode.SCHEMA_VALIDATION_ERROR`. The validation methods share the same pattern of checking required sections/keys and raising structured exceptions.
**Impact:** ~30 lines of similar validation boilerplate per loader. However, each loader validates a different schema with different required fields, so the specific validation logic is unique. The shared parts are the error-raising pattern and the load-then-validate structure.
**Recommendation:** This is a **borderline case** -- the loaders are well-structured and follow a consistent pattern, which is actually good. A base class could extract `load()` and the validation error pattern, but the benefit is marginal since each schema is different. **Not recommended for consolidation** unless more loaders are added.
**Effort:** Medium (and low benefit)

---

## Top 5 Priority List

| Priority | ID | Severity | Title | Effort |
|----------|---------|----------|-------|--------|
| 1 | DUP-SS-01 | MAJOR | Population extraction logic duplicated in CargoTransferService | Simple |
| 2 | DUP-SS-02 | MAJOR | Superweapon validation ability-check boilerplate | Simple |
| 3 | DUP-SS-03 | MINOR | Two component iteration implementations | Medium |
| 4 | DUP-SS-04 | MINOR | Name slugification functions | Simple |
| 5 | DUP-SS-05 | MINOR | Hex axial distance inlined in primitives | Simple |

DUP-SS-06 (loader structural pattern) is intentionally excluded from the priority list as consolidation is not recommended.

## Notes

- The codebase shows evidence of significant prior consolidation work (PROJ-108, PROJ-127, PROJ-204, PROJ-209, PROJ-212). Many patterns that would typically be duplicated have already been extracted (e.g., `ComponentInspector`, `ActionTimeResolver`, `DesignCostCalculator`).
- The `interfaces/engines.py` file contains only abstract interfaces -- no implementation duplication possible.
- The `adapters/simulation_adapter.py` is a single implementation with no duplication.
- The `formulas/habitability.py` is well-factored with the `_gaussian_factor` helper already extracted (PROJ-127).
- The density primitives appropriately delegate to `hex_axial_to_cartesian` from core for coordinate conversion; the only remaining inline calculation is the simpler distance-squared formula.

# Test Review: PROJ-334 + PROJ-335 + PROJ-336 Characterization Tests

**Review Type:** tests (fresh-eyes)
**Request ID:** req_20260504_231829_cffd2d
**Review Mode:** direct (no parent)
**Scope:** PROJ-334, PROJ-335, PROJ-336 — characterization tests for pure algorithms, data classes, and service-layer code (~164 new tests + ~3 review-fix tests)
**Review Date:** 2026-05-04

---

## Overall Verdict

| Project | CRITICAL | MAJOR | Verdict |
|---------|----------|-------|---------|
| PROJ-334 (algorithms) | 0 | 0 | CLEAN |
| PROJ-335 (data layer) | 0 | 4 | MINOR GAPS |
| PROJ-336 (strategy services) | 1 | 2 | FIX DOC |

---

## PROJ-334 — CLEAN (0 CRITICAL, 0 MAJOR)

All 10 review checklist items pass:

1. **Hardcoded canonical galaxy** — `CANONICAL_SEED_42` passes `pytest` against current production `RandomPlacementStrategy`. No drift.
2. **Determinism contract** — Both halves pinned: seed reproducibility across two runs AND seed=42 != seed=43. All assertions use `_canonical_signature()` (name + coordinate tuples), not degenerate length checks.
3. **Phase 0 audit** — All 31 "Uncovered"/"Partial→New" items from `coverage_gap_audit.md` are present in Phase 1 test files (23 generator + 8 pathfinding). All D-Observations (O-001 through O-004) pinned or documented as intentionally not-fixed.

---

## PROJ-335 — MINOR GAPS (0 CRITICAL, 4 MAJOR)

### FIND-01: MAJOR — PlanetaryFacility.from_dict doc-test mismatch: incomplete 4-key coverage

**File:** `tests/unit/strategy/data/test_planetary_facility_characterization.py:42-63`

Docstring claims validation of the 4-key contract (`instance_id`, `design_id`, `name`, `design_data`). Only 2 of 4 specific missing-key tests exist (missing `instance_id`, missing `design_data`). Missing: `test_missing_design_id_raises`, `test_missing_name_raises`.

**Action:** Add the two missing-key tests or update the docstring.

### FIND-02: MAJOR — Squadron.from_dict missing-required-key behavior not characterized

**File:** `tests/unit/strategy/data/test_squadron_characterization.py:110-171`

`Squadron.from_dict` accesses `data["name"]` directly without `require_keys` — raises bare `KeyError` (not `PersistenceException`), unlike sister classes. This error path is untested.

**Action:** Add test passing dict lacking `name` to `Squadron.from_dict`, asserting `KeyError`.

### FIND-03: MAJOR — Order.from_dict missing `type` key behavior not characterized

**File:** `tests/unit/strategy/data/test_order_types_characterization.py:222-269`

`Order.from_dict` accesses `data['type']` directly. Current tests cover *unknown value* of `type`, not a *completely absent* key. `KeyError` with `'type'` as message is a characterization-worthy quirk.

**Action:** Add test with dict lacking `"type"` key, asserting `KeyError`.

### FIND-04: MAJOR — Cross-cutting: from_dict extra-key tolerance not characterized anywhere

**Files:** All four data-class characterization files (SpeciesPopulation, PlanetaryFacility, Squadron, Order)

None of the four data classes test extra-key tolerance in `from_dict`. Production silently tolerates extra keys — an observable characteristic that should be pinned for save-file round-trip correctness.

**Action:** Add one test per `from_dict`-owning class passing dict with one extra key, verifying no exception and correct object construction.

---

## PROJ-336 — FIX DOC (1 CRITICAL, 2 MAJOR)

### FIND-05: CRITICAL — D-008 doc-test mismatch: negative load behavior documented incorrectly

**File:** `Projects/active_projects/PROJ-336/decisions.md:15`

D-008 claims negative load amount "would compute delta=-50 and reduce projected." Production code at `fleet_cargo_projector.py:56` uses `delta = amount if amount > 0 else (capacity - projected)` — negative amounts fill to capacity (auto-fill sentinel, same as zero). Test `test_load_with_negative_amount_fills_to_capacity_like_zero` correctly pins actual behavior. D-008 in decisions.md has NOT been corrected.

**Action:** Update decisions.md D-008 to state: "negative load fills to capacity (auto-fill sentinel, same as zero)."

### FIND-06: MAJOR — Vacuous test: `test_stabilizers_is_a_tuple_with_three_specs`

**File:** `tests/unit/strategy/services/test_stabilizer_registry.py:251`

Asserts only module constants (`len(STABILIZERS) == 3`, checks `ability_name` fields). No production function called. Redundant with `test_geologic_spec_matched_before_stellar_when_both_block_order_type` which exercises ordering via monkeypatched STABILIZERS.

**Action:** Remove or replace with non-redundant test exercising `find_blocking_stabilizer`.

### FIND-07: MAJOR — Vacuous test: `test_system_radius_hexes_is_50`

**File:** `tests/unit/strategy/services/test_system_destroyer.py:229`

Asserts only the module constant `SYSTEM_RADIUS_HEXES == 50`. No production function called. Value already exercised by boundary/override tests.

**Action:** Remove or replace with non-redundant test.

---

## Verification Summary

| Checklist Item | PROJ-334 | PROJ-335 | PROJ-336 |
|---------------|----------|----------|----------|
| 1. Hardcoded canonical galaxy drift | PASS | — | — |
| 2. Determinism contract completeness | PASS | — | — |
| 3. Phase 0 audit completeness | PASS | — | — |
| 4. from_dict completeness | — | PASS (4 MAJOR gaps) | — |
| 5. D-007 documented observations | — | PASS (all pinned) | — |
| 6. Fleet navigation gaps filled | — | — | PASS (all 4 areas) |
| 7. D-008 doc misalignment | — | — | FAIL (CRITICAL) |
| 8. STABILIZERS outer-loop ordering | — | — | PASS |
| 9. Vacuous tests | PASS | PASS (none vacuous) | 2 MAJOR (constants only) |
| 10. Specific test names | PASS | PASS | PASS |

---

## Agent Processing Notes

- Three parallel sub-agents reviewed PROJ-334, PROJ-335, and PROJ-336 independently.
- PROJ-334: `pytest` confirmed golden value passes. All 31 audit items cross-referenced.
- PROJ-335: Each test file read in full. All D-007 observations verified as pinned.
- PROJ-336: Each test file read in full. D-008 decisions.md text compared against production code and test assertions.

### Per-File Verdict

| File | Read | Verdict |
|------|------|---------|
| `test_galaxy_system_generator.py` | Yes, 687 lines | CLEAN |
| `test_basic_paths.py` | Yes, 346 lines | CLEAN |
| `test_edge_cases.py` | Yes, 304 lines | CLEAN |
| `test_hybrid_and_intercept.py` | Yes, 633 lines | CLEAN |
| `test_species_population_characterization.py` | Yes | GAPS (extra-key untested) |
| `test_planetary_facility_characterization.py` | Yes | GAPS (doc-test mismatch + extra-key) |
| `test_squadron_characterization.py` | Yes | GAPS (missing-key + extra-key) |
| `test_order_types_characterization.py` | Yes | GAPS (missing-type-key + extra-key) |
| `test_group_policy_registry_characterization.py` | Yes | CLEAN |
| `test_fleet_navigation_gaps.py` | Yes | CLEAN |
| `test_fleet_cargo_projector.py` | Yes | CLEAN (doc-mismatch is in decisions.md) |
| `test_system_destroyer.py` | Yes | 1 MAJOR (vacuous constant test) |
| `test_stabilizer_registry.py` | Yes | 1 MAJOR (vacuous constant test) |

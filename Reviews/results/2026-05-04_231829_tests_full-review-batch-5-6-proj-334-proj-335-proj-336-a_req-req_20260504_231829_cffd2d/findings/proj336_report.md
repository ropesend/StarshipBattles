# PROJ-336 Characterization Tests — Review Report

**Date:** 2026-05-04
**Severity:** CRITICAL + MAJOR findings only

---

### FIND-01: [CRITICAL] D-008 doc-test mismatch — negative load behavior documented incorrectly

**File:** `Projects/active_projects/PROJ-336/decisions.md:15`
**Description:** D-008 states: "An order with `amount=-50, direction='load'` would compute `delta=-50` and reduce `projected`." Production code at `game/strategy/services/fleet_cargo_projector.py:56` uses `delta = amount if amount > 0 else (capacity - projected)`, meaning negative amounts **fill to capacity** (treated as auto-fill sentinel, same as zero). The test `test_load_with_negative_amount_fills_to_capacity_like_zero` at `tests/unit/strategy/services/test_fleet_cargo_projector.py:138` correctly pins the actual production behavior. The test's own docstring (lines 123–135) already calls out D-008 as incorrect. D-008 in decisions.md has NOT been revised — it still says "reduces projected."
**Action required:** Update decisions.md D-008 to match production behavior: "negative load fills to capacity (auto-fill sentinel, same as zero)." The test is correct; production is correct; only the doc is wrong.

---

### FIND-02: [MAJOR] Vacuous test — `test_stabilizers_is_a_tuple_with_three_specs` only asserts module constants

**File:** `tests/unit/strategy/services/test_stabilizer_registry.py:251`
**Description:** This test does not call any production function. It only asserts that `len(STABILIZERS) == 3` and checks the `ability_name` field of each entry in the module-level tuple. No production logic is exercised. A change to the tuple ordering/contents would be caught by `test_geologic_spec_matched_before_stellar_when_both_block_order_type` (which uses a synthetic monkeypatched STABILIZERS) and by the positive-match tests, making this constant-pinning test redundant.
**Action required:** Remove or replace with a test that exercises `find_blocking_stabilizer` in a non-redundant scenario.

---

### FIND-03: [MAJOR] Vacuous test — `test_system_radius_hexes_is_50` only asserts module constant

**File:** `tests/unit/strategy/services/test_system_destroyer.py:229`
**Description:** This test does not call any production function. It only asserts `SYSTEM_RADIUS_HEXES == 50`. The value 50 is already exercised by `test_excludes_fleet_at_exact_radius_boundary` (which depends on the default SYSTEM_RADIUS_HEXES for its boundary behavior) and `test_with_custom_radius_kwarg_overrides_default` (which overrides it). A standalone constant pin adds no new coverage.
**Action required:** Remove or replace with a test that exercises `collect_system_contents` or `destroy_system` in a non-redundant scenario.

---

## Per-File Verdict Table

| File | Read? | Verdict |
|------|-------|---------|
| `test_fleet_navigation_gaps.py` | Yes | PASS — all 4 gap areas covered, 9 concrete tests, no vacuous/excessive tests |
| `test_fleet_cargo_projector.py` | Yes | PASS — 15 concrete tests, D-008 misbehavior correctly pinned; doc-mismatch flagged as CRITICAL (FIND-01) |
| `test_system_destroyer.py` | Yes | PASS with 1 MAJOR — 15 tests, all concrete names; 1 vacuous constant-pinning test (FIND-03) |
| `test_stabilizer_registry.py` | Yes | PASS with 1 MAJOR — 14 tests, all concrete names; MAJ-005 fix correctly verified via synthetic STABILIZERS; 1 vacuous constant-pinning test (FIND-02) |

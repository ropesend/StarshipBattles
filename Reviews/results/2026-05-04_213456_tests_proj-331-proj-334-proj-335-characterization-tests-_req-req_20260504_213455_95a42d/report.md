# Review Report: PROJ-331/334/335 Characterization Tests

**Request ID:** req_20260504_213455_95a42d
**Review Type:** tests
**Mode:** Normal (not 03c lightweight)
**Completed:** 2026-05-04
**Scope:** PROJ-331 (44 tests), PROJ-334 (36 tests + audit), PROJ-335 (77 tests)

---

## Verification Matrix

| Instruction | Status | Notes |
|---|---|---|
| §1 Behavior accuracy (spot-check 10 tests) | Done | 12 tests verified against production code |
| §2 Brittleness (implementation detail pinning) | Done | 2 minor fragility findings |
| §3 Mocking discipline (3-5 heavy-mock tests) | Done | Appropriate for characterization style |
| §4 Test naming | Done | Generally good; 1 misleading name |
| §5 Missed surfaces | Done | 2 gaps found |
| §6 Apparent bugs documented vs not | Done | See OBSERVATION-C gap |
| §7 OBSERVATION-A/B/C pinned | Done | A pinned; B partial; C not pinned |
| §8 Determinism contract (seed=42 reps, 42!=43) | Done | Verified |
| §9 species_population.py skip verification | Done | Skip was correct |

---

## Findings

### MAJOR

**MAJ-001 — Canonical galaxy test doesn't pin a value**
- **File:** `tests/unit/strategy/data/test_galaxy_system_generator.py:401-435`
- **Finding:** `test_generate_systems_with_seed_42_produces_canonical_galaxy` computes `expected` dynamically from `result` (lines 427-431), then only asserts `len(set(coords)) == 5` (all coordinates unique). The test name implies it certifies a specific canonical galaxy layout, but it does not — any set of 5 unique coordinates passes. The genuine determinism contract IS pinned by the next test (`test_generate_systems_with_seed_42_is_reproducible_across_two_runs`), but the first test creates false confidence: a reader assuming "canonical galaxy" means a hardcoded golden value would miss that it doesn't.
- **Severity:** MAJOR — misleading test that could obscure production behavior changes.
- **Recommendation:** Either (a) hardcode the expected canonical tuple from a one-time run, or (b) rename to `test_generate_systems_with_seed_42_produces_5_unique_systems` and drop the misleading docstring. Option (a) is preferred per PROJ-334 D-002 ("golden value is recorded in test, not in a separate fixture file").

**MAJ-002 — OBSERVATION-C not pinned by any test**
- **File:** `game/simulation/battle_controller.py:442-449` and `Projects/active_projects/PROJ-331/decisions.md:17`
- **Finding:** PROJ-331 decisions.md states "Test pins the swallow: when `get_default_capture_sink().on_battle_ended` raises, the outcome is still set and battle end completes." No such test exists in any of the 4 scoped test files (`test_battle_state_live_object_bridges.py`, `test_state.py`, `test_start_from_spec.py`, `test_logging_and_lookups.py`). The production code has an intentional broad catch (`except Exception`) at line 445, but its behavior under exception is unverified.
- **Severity:** MAJOR — documented but untested exception behavior; a refactor that removes or changes the catch would go undetected.
- **Recommendation:** Add a test that patches `get_default_capture_sink().on_battle_ended` with `side_effect=RuntimeError`, calls `_extract_outcome_on_battle_end`, and asserts `self._outcome is not None`.

**MAJ-003 — OBSERVATION-B boundary default not explicitly asserted**
- **File:** `tests/unit/simulation/battle_controller/test_state.py:42-79` vs `game/simulation/battle_controller.py:638-639`
- **Finding:** `load_state` defaults `_retreat_manager.boundary` to `UnboundedRegion()` (per line 638-639 + guard comment at lines 614-620). The existing `test_load_state_restores_battle` exercises the full restore flow but never asserts `isinstance(controller._retreat_manager.boundary, UnboundedRegion)`. The test verifies the restore succeeded, not the boundary contract that PROJ-331 decisions.md says was pinned.
- **Severity:** MAJOR — the decision log claims this is pinned; it isn't.
- **Recommendation:** Add `assert isinstance(controller._retreat_manager.boundary, UnboundedRegion)` to `test_load_state_restores_battle`.

**MAJ-004 — No characterization test for Order.from_dict with invalid OrderType name**
- **File:** `game/strategy/data/order_types.py:159`; no corresponding test
- **Finding:** `Order.from_dict` at line 159 calls `OrderType[data['type']]` which raises `KeyError` for unknown type names. No characterization test pins this. The sister classes (`SpeciesPopulation`, `PlanetaryFacility`, `Squadron`) all pin their missing-key/rejection behaviors through `from_dict` tests. Order is the anomalous case — the missing-key behavior is architecturally equivalent but untested.
- **Severity:** MAJOR — inconsistent with the characterization pattern established by other data-layer classes.
- **Recommendation:** Add `test_from_dict_unknown_order_type_raises_keyerror` to `test_order_types_characterization.py`.

### MINOR

**MIN-001 — Disjunctive assertion weakens StartFromSpec gating test**
- **File:** `tests/unit/simulation/battle_controller/test_start_from_spec.py:79`
- **Finding:** `assert "PROJ-252" in str(exc_info.value) or "registry_provider" in str(exc_info.value)` — this OR passes if either substring is present. If the error message is refactored to mention only "PROJ-252" (the ticket reference), the test still passes even if the semantic signal "registry_provider" is lost.
- **Recommendation:** Use `assert "registry_provider" in str(exc_info.value)` (the semantic signal) or `assert ... and ...` if both must be present.

**MIN-002 — Monkeypatch on module cache bypasses loader function**
- **File:** `tests/unit/strategy/data/test_galaxy_system_generator.py:262-278`
- **Finding:** `test_apply_system_archetype_is_noop_when_random_exceeds_chance` sets `mod._SYSTEM_ARCHETYPES_CACHE` via `monkeypatch.setattr` rather than patching `_load_system_archetypes()`. This works correctly but is fragile: if the production code's cache access pattern changes (e.g., lazy initialization via a function), this patch silently becomes a no-op.
- **Recommendation:** Add a brief comment noting that the patch targets the module-level cache that `_apply_system_archetype` reads through `_load_system_archetypes`.

**MIN-003 — Hidden sentinel in test_logging_and_lookups.py**
- **File:** `tests/unit/strategy/conflict_resolution/test_logging_and_lookups.py:44`
- **Finding:** `_DEFAULT_LOC = object()` is used as a sentinel to distinguish "not passed" from "explicit None" in `_fleet()`. The sentinel is undocumented, making it non-obvious to future readers why a raw `object()` appears.
- **Recommendation:** Add `# sentinel: distinguishes "no location arg" from "explicit location=None"` on the same line.

**MIN-004 — Property descriptor patch for ordering assertion is fragile**
- **File:** `tests/unit/simulation/test_battle_state_live_object_bridges.py:237-240`
- **Finding:** `type(new_comp).current_hp = property(...)` patches the MagicMock type to record `current_hp` assignment sequence. This is clever but fragile — if `current_hp` is set inside `add_component` (line 413 of production) rather than only at line 414, the test would see the write but at an unexpected point. The assertion correctly verifies modifier-before-damage ordering for the current production code, but the approach is opaque.
- **Recommendation:** A comment explaining the property-descriptor tracking would help maintainers. No change needed — the assertion is correct for current behavior.

**MIN-005 — squadron.py: to_dict omission of inherited fields not explicitly verified**
- **File:** `tests/unit/strategy/data/test_squadron_characterization.py:113-123`
- **Finding:** `Squadron.to_dict` calls `super().to_dict()` which serializes inherited fields (`_members`, `_lone_ships`, policy, etc.). The round-trip test validates Squadron-specific fields but doesn't explicitly verify that `to_dict` includes `"type": "squadron"` alongside inherited data. The `type` key IS tested separately (`test_to_dict_includes_squadron_discriminator`), which is sufficient, but the inherited field round-trip at Squadron level is exercisable only through `from_dict`.
- **Recommendation:** Low priority. The `from_dict` round-trip covers the deserialization contract.

### OBSERVATIONS

**OBS-001 — Mocking discipline is consistent with characterization style**
All three projects properly use MagicMock/hand-rolled fakes at boundaries without mocking the unit under test. PROJ-331 D-003/004/005, PROJ-334 D-005, and PROJ-335 D-004 decisions are faithfully followed. The one technique that deserves scrutiny (property-descriptor patching for ordering, MIN-004) is correct for current behavior.

**OBS-002 — species_population.py skip was correct**
`tests/unit/strategy/data/test_population_model.py::TestSpeciesPopulation` covers constructor defaults, explicit values, and happiness at valid bounds (0.0, 1.0). The new characterization file (`test_species_population_characterization.py`) adds `from_dict` direct path, missing-key rejection, and out-of-bounds acceptance. These are non-overlapping surface areas. The skip per PROJ-335 D-002 was appropriate.

**OBS-003 — PROJ-334 gap audit planned 31 tests; actual implementation lower**
The audit (`coverage_gap_audit.md:111`) estimated 31 new tests (8 pathfinding + 23 generator). Reviewing the actual files: `test_galaxy_system_generator.py` has ~25 test methods in 6 classes (close to 23 estimated), and `test_hybrid_and_intercept.py` has ~8 new tests visible. The totals are approximately 33 (slightly above estimate). However, some audit-identified pathfinding gaps (e.g., `find_path_deep_space` symmetry, `can_warp` param override) appear to have been written in `test_hybrid_and_intercept.py`. Count appears within tolerance.

**OBS-004 — D-observations in PROJ-334 are documented but not pinned**
PROJ-334 decisions.md D-Observations table (O-001 through O-004) was left empty. The gap audit documented these (dead code at pathfinding.py:91-99, A* heuristic at :128, id=-1 at :365, dual-RNG placement at :177). O-004 mentions `test_generate_systems_derives_storm_and_intrinsic_seeds_from_parent_rng` pins it. O-001 through O-003 appear to be audit-documented but have no explicit pinning tests (O-002 "A* heuristic overweights G-cost" is a design observation, not a testable behavior; O-001 dead code might be testable via coverage assertion). This is acceptable per the "document, don't fix" mandate, but it means 3 of 4 observations lack characterization pins.

---

## What to Fix vs Accept

| Finding | Action |
|---|---|
| MAJ-001 | Fix: hardcode canonical golden tuple or rename test |
| MAJ-002 | Fix: add OBSERVATION-C pinning test |
| MAJ-003 | Fix: add UnboundedRegion assertion to load_state test |
| MAJ-004 | Fix: add invalid OrderType from_dict test |
| MIN-001 | Fix: tighten assertion |
| MIN-002 | Accept: add comment only |
| MIN-003 | Fix: add sentinel comment |
| MIN-004 | Accept: add comment only |
| MIN-005 | Accept |
| OBS-001 to OBS-004 | Accept (observations, no action needed) |

**Estimated effort:** 4 MAJOR items at ~1-2 tests each = ~1 session to resolve.

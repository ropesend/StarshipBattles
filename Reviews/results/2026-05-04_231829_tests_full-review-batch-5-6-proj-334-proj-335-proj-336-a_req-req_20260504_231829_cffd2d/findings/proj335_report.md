# PROJ-335 Characterization Tests — Review Findings

**Review date:** 2026-05-04
**Scope:** Critical & Major issues only
**Files reviewed:** 5 test files, 1 decisions.md

---

## D-007 Conformance

All four D-007 documented observations are pinned by tests:

| Observation | Pinning test |
|---|---|
| HexCoord branch missing `type` key | `test_move_with_hex_coord_emits_q_r_without_type_key` (`test_order_types_characterization.py:144`) |
| `from_dict` does not resolve HexCoord | `test_does_not_resolve_hex_coord_branch` (`test_order_types_characterization.py:246`) |
| SpeciesPopulation accepts negative count silently | `test_negative_count_accepted_silently` (`test_species_population_characterization.py:61`) |
| `is_shipyard` short-circuits on `is_operational=False` | `test_returns_false_when_not_operational_even_with_shipyard_component` (`test_planetary_facility_characterization.py:132`) |

No D-007 observation is missing its pin.

---

## Findings

### FIND-01: MAJOR — PlanetaryFacility.from_dict doc-test mismatch: incomplete 4-key coverage

**File:** `tests/unit/strategy/data/test_planetary_facility_characterization.py:42-63`

**Description:** The `TestFromDictRequiredKeys` class docstring claims "from_dict validates the 4-key contract via require_keys." Production code at `planetary_facility.py:64` requires `['instance_id', 'design_id', 'name', 'design_data']`. However, only 3 tests exist:
- `test_empty_dict_raises_persistence_exception` (line 45)
- `test_missing_instance_id_raises` (line 49)
- `test_missing_design_data_raises` (line 57)

Missing specific tests for `design_id` and `name` key rejection. The class name and docstring claim 4-key validation coverage but the tests only cover 2 of 4 specific missing-key cases.

**Action required:** Add `test_missing_design_id_raises` and `test_missing_name_raises` tests, or update the class docstring to reflect actual coverage.

---

### FIND-02: MAJOR — Squadron.from_dict missing-required-key behavior not characterized

**File:** `tests/unit/strategy/data/test_squadron_characterization.py:110-171`

**Description:** `Squadron.from_dict` at `squadron.py:86-102` accesses `data["name"]` directly without `require_keys`. If `name` is absent from the input dict, this raises a bare `KeyError` (not `PersistenceException`), unlike the pattern used by `SpeciesPopulation.from_dict` and `PlanetaryFacility.from_dict`. The test class `TestFromDictReconstruction` covers 5 happy-path round-trip scenarios but never tests the missing-key error path. This is a behavioral quirk — the error type differs from the `PersistenceException` contract used by sister classes — and should be pinned.

**Action required:** Add a test that passes a dict lacking `name` to `Squadron.from_dict` and asserts the `KeyError` is raised (with docstring noting this is the current behavior, not necessarily the desired one).

---

### FIND-03: MAJOR — Order.from_dict missing `type` key behavior not characterized

**File:** `tests/unit/strategy/data/test_order_types_characterization.py:222-269`

**Description:** `Order.from_dict` at `order_types.py:159` accesses `data['type']` directly. A missing `type` key raises `KeyError`. The existing `TestFromDictSimplePath` class includes `test_from_dict_unknown_order_type_raises_keyerror` (line 256) which tests an unknown *value* of the type key, but never tests a completely absent `type` key. The behavior (`KeyError` with `'type'` as message) is a characterization-worthy quirk since it bypasses the `PersistenceException` contract used by other from_dict implementations.

**Action required:** Add a test that passes a dict without `"type"` to `Order.from_dict` and asserts `KeyError` is raised.

---

### FIND-04: MAJOR — Cross-cutting: from_dict extra-key tolerance not characterized anywhere

**Files:**
- `tests/unit/strategy/data/test_species_population_characterization.py`
- `tests/unit/strategy/data/test_planetary_facility_characterization.py`
- `tests/unit/strategy/data/test_squadron_characterization.py`
- `tests/unit/strategy/data/test_order_types_characterization.py`

**Description:** None of the four data-class characterization files test extra-key tolerance in `from_dict`. Production behavior across all four is *silently tolerate* — `require_keys` only enforces presence, not exclusivity; constructors only bind known parameters. This silently-tolerant behavior is an observable characteristic that should be pinned, especially for save-file round-trip correctness where extra keys from future save format versions could silently leak through.

**Action required:** Add one test per from_dict-owning class (SpeciesPopulation, PlanetaryFacility, Squadron, Order) that passes a dict with one extra key and verifies the extra key is silently tolerated (no exception raised, object constructed correctly with known fields).

---

## Per-File Verdict

| File | Read? | Verdict |
|---|---|---|
| `test_species_population_characterization.py` | Yes | Covers D-007 observations and missing-key rejection; missing extra-key tolerance test |
| `test_planetary_facility_characterization.py` | Yes | Strong is_shipyard and legacy-key coverage; doc-test mismatch on 4-key validation claim; missing extra-key test |
| `test_squadron_characterization.py` | Yes | Good round-trip and to_dict asymmetry coverage; missing required-key error path and extra-key test |
| `test_order_types_characterization.py` | Yes | Comprehensive to_dict matrix and D-007 pinning; missing absent-type-key error path and extra-key test |
| `test_group_policy_registry_characterization.py` | Yes | Solid load/validate characterization; no from_dict-owning class so extra-key test not applicable; no issues found |

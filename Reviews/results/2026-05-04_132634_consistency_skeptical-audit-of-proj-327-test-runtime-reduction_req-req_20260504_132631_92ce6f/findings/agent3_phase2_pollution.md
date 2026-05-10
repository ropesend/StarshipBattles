# Agent 3 — Skeptical Audit: PROJ-327 Phase 2, Task 2.19 (test_ship_io.py)

**Audit date:** 2026-05-04
**File audited:** `tests/unit/ui/services/test_ship_io.py`
**Supporting files:** `tests/conftest.py`, `game/ui/services/ship_io.py`, `tests/fixtures/ships.py`

---

## Question 1: Cross-test pollution risk

### 1a. Does any test mutate the registries object?

**No mutations found.** The `mock_ship` and `mock_ship_with_special_chars` fixtures at lines 48–71 receive `session_registries` and pass it to `create_test_ship(...)`. `create_test_ship` (`tests/fixtures/ships.py:59`) reads from registries for lookups (component creation via `create_component`, vehicle class data in `Ship` constructor) but never writes. The registries are treated as a read-only catalog.

A grep for attribute writes, dict mutations, or method calls that could modify registries in the file returned zero results.

### 1b. Does any test mutate the mock_ship in a way that would persist to the next test?

**No.** The only attribute writes on `mock_ship` found by grep are at lines 183–184:

```python
# Line 182: mock_ship = MagicMock()   <-- LOCAL variable, NOT the fixture
# Line 183: mock_ship.name = "BrokenShip"
# Line 184: mock_ship.to_dict.side_effect = ValidationException(...)
```

These occur in `test_save_ship_handles_serialization_error` (line 177), which does **not** request the `mock_ship` fixture in its parameter list. It creates its own local `MagicMock()` shadowing the name. The module-scoped fixture is never touched by this test.

Every other test that receives `mock_ship` via fixture injection either:
- Calls `mock_ship.to_dict()` — read-only serialization
- Reads `.name`, `.ship_class`, `.layers` — attribute reads
- Passes `mock_ship` to `ship_io_with_tkroot.save_ship(mock_ship)` — verified read-only (see below)

`ShipIO.save_ship` (`game/ui/services/ship_io.py:89`) calls only `ship.to_dict()` (line 102) and reads `ship.name` (line 106). Neither mutates the ship instance. No other test method chains could modify the shared fixture.

### 1c. Verify "ZERO attribute writes" claim

**CONFIRMED.** The Phase 2 comment block at lines 28–44 states "ZERO attribute writes against `mock_ship`, `mock_ship_with_special_chars`, or `minimal_ship`." This is accurate. The two attribute writes at lines 183–184 target a locally-constructed `MagicMock()`, not any fixture.

---

## Question 2: Module-scope MagicMock call-history accumulation

**Not applicable.** The project findings (`phase_2_runtime_delta.md`) refer to `reset_mock()` but `mock_ship` and `mock_ship_with_special_chars` are **real `Ship` objects** returned by `create_test_ship(...)`, not `MagicMock` instances. There is no `.call_count`, `.assert_called_once()`, or `.method_calls` attribute to accumulate.

The three `assert_called_once()` calls in the file (lines 124, 136, 286) are on locally-patched mocks (`mock_save`, `mock_makedirs`), not on the shared ship fixtures. No test asserts on `mock_ship.<method>.assert_called_once()`.

---

## Question 3: Is Phase 2 work in test_ship_io.py actually safe?

**Yes, with no reservations specific to this file.** The module-scoping is safe for the following reasons:

| Risk vector | Status | Evidence |
|---|---|---|
| Fixture attribute mutation | No risk | Zero attribute writes to shared fixtures (lines 183–184 are local MagicMock) |
| `save_ship` mutates ship | No risk | `ship_io.py:102` calls `ship.to_dict()` only; line 106 reads `ship.name` |
| MagicMock call-history bleed | Not applicable | Fixtures are real `Ship` objects, not MagicMock |
| `session_registries` mutation | No risk in-file | `create_test_ship` and `Ship` constructor are read-only on registries |
| `to_dict()` side effects | No risk | Pure serialization; returns new dict |
| `tmp_path` / module-scope compatibility | Safe | pytest allows function-scoped `tmp_path` with module-scoped fixtures |
| Round-trip tests still isolated | Safe | Round-trip tests use `fresh_registries` (function-scoped deepcopy), not the shared `session_registries` |

### Cross-file `session_registries` caveat (low severity)

The `session_registries` fixture (`conftest.py:154`) returns a `GameRegistries` whose internal dicts are direct references to `SessionRegistryCache` data (line 180–184):

```python
return GameRegistries(
    components=cache.components_data,   # direct reference, NOT deep-copied
    modifiers=cache.modifiers_data,
    ...
)
```

If **another test file** with a module-scoped fixture mutates `session_registries` (e.g., writes to `registries.components["some_id"]`), the change would persist and affect `test_ship_io.py`'s fixtures. This is a general `session_registries` design property, not a Task 2.19 defect. No test in `test_ship_io.py` triggers this path.

### Dead code removal confirmed

`minimal_ship` was deleted (no trace in file). The Phase 2 claim of "zero references" is correct.

---

## Verdict

**Task 2.19 for test_ship_io.py is safe.** No cross-test pollution, no MagicMock history bleed, no false-positive/false-negative risk from module-scoping the `mock_ship` and `mock_ship_with_special_chars` fixtures. The ~12% runtime reclaim (280 ms) claimed in `phase_2_runtime_delta.md` is plausible since the conversion from 54 `fresh_registries` deepcopies to 1 shared `session_registries` lookup eliminates the dominant per-test cost.

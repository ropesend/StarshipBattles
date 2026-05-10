# Follow-up Verification Report: PROJ-358 Audit Remediation

## Metadata
- **Date:** 2026-05-05
- **Type:** code (follow-up verification)
- **Review Mode:** Direct analysis (no agent swarm — concise per request instructions)
- **Request ID:** req_20260505_110135_6d421b
- **Parent Request:** req_20260505_061728_88fd15
- **Remediation SHA:** de7f6fb47
- **Scope:** `ship_serialization.py`, 4 test files, PROJ-358/decisions.md

## Executive Summary
- **Findings Verified:** 2 parent MAJOR findings (CQ-01, CQ-02) + test fixture audit
- **Resolved:** 1 (CQ-01)
- **Deferred (confirmed reasonable):** 1 (CQ-02)
- **Regressions:** 0
- **Overall Assessment:** Remediation is correct and complete. No regressions introduced.

---

## Verification Matrix

| Parent Finding | Status | Notes |
|---|---|---|
| CQ-01: Silent skip of unknown component IDs | **resolved** | `continue` replaced with `raise ValidationException(code=SCHEMA_VALIDATION_ERROR)` at ship_serialization.py:202-211. Context fields (ship_name, layer, component_id) properly surfaced. |
| CQ-02: battle_runner.py exceeds 500 LOC | **deferred (reasonable)** | Still 730 lines. Deferral rationale is sound: cross-cutting refactor touching multiple subsystems — warrants its own ticket with independent review. |

---

## CQ-01: Resolved — Evidence

### Production Code (ship_serialization.py:198-211)

The silent `continue` at lines 198-199 has been replaced with a loud `ValidationException`:

```python
if comp_id not in comps:
    raise ValidationException(
        f"Component id '{comp_id}' in layer '{l_name}' is not "
        f"present in the component registry; ship='{ship.name}'",
        code=ErrorCode.SCHEMA_VALIDATION_ERROR.value,
        context={
            "ship_name": ship.name,
            "layer": l_name,
            "component_id": comp_id,
        },
    )
```

- Error code is `SCHEMA_VALIDATION_ERROR` (V002) — consistent with the PROJ-358 fix and parent review recommendation.
- Context dict contains `ship_name`, `layer`, `component_id` — mirroring the contract established by PROJ-358's `_apply_spec_components_to_ship`.
- The `# PROJ-358 audit (CQ-01)` comment documents the intentional change from the old silent-skip behavior.

### Test Impact (addressing CQ-05 as well)

All 4 test fixtures documented in `decisions.md:33-45` were verified:

1. **`tests/unit/simulation/entities/test_ship_serialization.py:463-484`**
   - `test_from_dict_unknown_component_id_raises` — asserts `pytest.raises(ValidationException)` and verifies `context["component_id"]`, `context["layer"]`, `context["ship_name"]`.

2. **`tests/unit/ui/services/test_ship_io.py:702-732`**
   - `test_load_ship_raises_for_unknown_component_ids` — asserts `pytest.raises(ValidationException)` with `context["component_id"] == "nonexistent_component_12345"` and `context["layer"] == "CORE"`.

3. **`tests/unit/strategy/test_ship_instance_damage.py`** — Multiple fixtures updated:
   - `design_data` (line 23-57): `bridge`, `generator`, `fuel_tank`, `laser_cannon`, `standard_engine`, `armor_plate` — all real registry IDs.
   - `design_data_with_layers` (line 245-270): `bridge`, `generator`, `fuel_tank`, `laser_cannon`, `armor_plate`.
   - `design_data_with_layers` (line 326-355): `crew_quarters`, `life_support`, `fuel_tank`, `battery`, `mini_battery`, `armor_plate`.
   - Hull layer test (line 391-409): `hull_escort`.
   - Synthetic IDs still present in tests at lines 421 (`reactor_mark_2`), 466 (`engine_basic`), and 501 (`reactor_standard`) — **not a regression**: these tests construct `ShipInstance` directly with pre-built `components` dicts, bypassing `ShipSerializer.from_dict`, so they never encounter the validation path.

4. **`tests/unit/strategy/test_ship_consumable_manager.py:222-247`**
   - `ship_with_resources` fixture uses `fuel_tank` and `generator` (was `reactor`).

All fixtures now use real registry component IDs as documented. No synthetic IDs remain in the serialization path.

---

## CQ-02: Deferred — Deferral Validation

`battle_runner.py` remains at 730 lines. The decisions.md:28 rationale:

> "Not blocking for PROJ-358 — file as a follow-up cleanup ticket." Effort: Medium. The split touches multiple unrelated subsystems (telemetry, outcome extraction, end-reason derivation) and is a cross-cutting refactor that should be its own ticket so it can be reviewed independently.

**Deferral is reasonable.** The file's 8 functions span materialization, engine setup, telemetry, outcome extraction, component state application, and end-reason derivation. Splitting these into sub-modules touches multiple unrelated subsystems and deserves its own change with its own test verification. The PROJ-358 change adds ~30 lines of validation logic in an isolated function — not a material driver of growth toward a file that was already over the ceiling before PROJ-358 began.

---

## Regression Check

- **Unknown-layer survival:** `test_ship_io.py:677-700` uses `{"id": "some_component"}` in an UNKNOWN_LAYER key. The `_load_components` loop (ship_serialization.py:180-231) skips unknown layer types via `except KeyError: continue` (line 183-184) before reaching the component ID check, so this test path is unaffected by the CQ-01 fix.
- **Non-dict entry handling:** `ship_serialization.py:190-195` still raises `ValidationException` for non-dict component entries — untouched by the remediation, unchanged behavior.
- **Modifier serialization:** Unchanged by CQ-01 fix — unknown modifier IDs are still handled via `logger.warning` (line 228), not a raise. This is consistent with the intentional distinction: unknown *modifier* IDs are non-structural (a modifier is additive/optional), while unknown *component* IDs are structural drift.

---

## Conclusion

CQ-01 is fully resolved. 4 test fixture locations correctly migrated from synthetic/bug-encoding IDs to real registry IDs. CQ-02 deferral is well-reasoned. Zero regressions detected. The remediation commit `de7f6fb47` successfully addresses all parent review findings within scope.

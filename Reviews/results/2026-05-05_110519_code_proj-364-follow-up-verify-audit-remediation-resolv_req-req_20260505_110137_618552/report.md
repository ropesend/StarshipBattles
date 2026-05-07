# Review Report: PROJ-364 Follow-up — Audit Remediation Verification
**Request ID:** req_20260505_110137_618552
**Parent Request:** req_20260505_070825_e838b1
**Review Type:** code (follow-up)
**Review Mode:** lightweight (targeted verification)
**Scope:** 3 files
**Remediation SHA:** 3e1e7697f414a450d805ff24fef9582f63dc6bed
**Date:** 2026-05-05

---

## Verification Matrix

| Parent Finding | Status | Evidence |
|---|---|---|
| MAJ-001 | **resolved** | `planet_id` and `planet_name` added to event kwargs at `superweapon_order_processor.py:655-656`; test at `test_superweapon_event_payloads.py:298-299` asserts both keys |
| MAJ-002 | **accepted** | Deferral documented in `decisions.md:14-22` with natural extraction candidates (`open_warp_point`, `close_warp_point`, `create_dyson_sphere` → `_effect_for_*`). Sound: extraction would require 7+ arg signatures and contradict single-file-responsibility decision. |

---

## MAJ-001: DYSON_SPHERE_CREATED missing planet_id / planet_name — RESOLVED

**Fix (commit 3e1e7697f):**

In `game/strategy/engine/superweapon_order_processor.py:651-657`, the `_effect` closure now returns:
```python
return {
    "event_message": f"Dyson Sphere created in {system.name}",
    "log_message": f"Dyson Sphere created in {system.name}",
    "system_name": system.name,
    "planet_id": dyson.id,
    "planet_name": dyson.name,
}
```

The `dyson` Planet variable (created at line 629) was already in scope. The new fields flow through `**event_kwargs` into `_finalize_superweapon.log_event(...)` at line 122-129.

**Test update:**

In `tests/unit/strategy/engine/test_superweapon_event_payloads.py:298-299`:
```python
assert 'planet_id' in kw
assert kw['planet_name'] == "Dyson Sphere (Sol)"
```

The `planet_id` assertion uses `in` check (correct — planet IDs are auto-generated), and `planet_name` asserts the expected exact value. This mirrors the pattern used by the existing `TestPlanetImplodedPayload` test.

**No regressions:** The 2 added event kwargs are purely additive. No existing key is removed or renamed. No control flow changed. The `_finalize_superweapon` method already splats `**event_kwargs`, so any extra keys are silently passed through to `log_event`.

---

## MAJ-002: process_* LOC overage — ACCEPTED (deferral sound)

**No code change was made** (per the "defer / accept" verdict). The remediation added explicit documentation of the deferral in `Projects/active_projects/PROJ-364/decisions.md:14-22`:

> If the 500-line module ceiling becomes pressing, the three longest closures (`open_warp_point`, `close_warp_point`, `create_dyson_sphere`) are the natural candidates for extraction to private `_effect_for_*` methods. Tracked here so the deferral is explicit.

**Assessment — the deferral is sound:**

1. **Justification is documented.** The reasoning (7+ argument signatures for extraction, contradicts single-file-responsibility design) is captured in the decisions log for future readers.
2. **Natural extraction targets are identified.** `process_open_warp_point` (68 lines), `process_close_warp_point` (73 lines), `process_create_dyson_sphere` (95 lines) are named as the three candidates. Any future engineer facing the 500-line ceiling knows exactly what to extract.
3. **Trigger condition is explicit.** Extraction is deferred until "the 500-line module ceiling becomes pressing." The file is currently 782 lines, so ceiling proximity is monitored but not yet breached by extracted content.
4. **No regressions.** No code change, no behavior change.

---

## Regressions — None

The remediation commit `3e1e7697f` changes only 3 files with 15 total additions, 0 deletions:
- `superweapon_order_processor.py`: +2 lines (event kwargs)
- `test_superweapon_event_payloads.py`: +2 lines (assertions)
- `decisions.md`: +11 lines (audit remediation documentation)

All changes are additive. No existing behavior is modified. No imports, control flow, or error handling changed.

---

## Summary

| Finding | Count |
|---|---|
| MAJ-001 resolved | 1 |
| MAJ-002 accepted (deferral) | 1 |
| Regressions | 0 |
| New issues introduced | 0 |

# Code Review Report: PROJ-358 Battle Runner Spec Component Validation

## Metadata
- **Date:** 2026-05-05
- **Type:** code
- **Review Mode:** Single-reviewer direct analysis
- **Request ID:** req_20260505_061728_88fd15
- **Scope:** `_apply_spec_components_to_ship` in `battle_runner.py`, new validation tests, PROJ-358 decisions
- **Checkout SHA:** 42749a344 (per requester context)

## Executive Summary
- **Total Findings:** 7
- **Critical:** 0 | **Major:** 2 | **Minor:** 3 | **Info:** 2
- **Estimated Total Effort:** Medium
- **Overall Assessment:** The implementation is sound. All 4 context fields are properly surfaced in both the ValidationException message and context dict. The two-pass design correctly preserves bit-identical materialization for valid specs. The error code choice is consistent with project conventions. The tests follow proper TDD patterns. Two concerns raised: (1) `battle_runner.py` at 730 LOC substantially exceeds the 500 LOC production ceiling, and (2) `ship_serialization.py:198-199` silently skips unknown component IDs, which is a related silent-drift hazard.

---

## Response to Review Instructions

### 1. ValidationException Context Fields — VERIFIED

`battle_runner.py:640-661` constructs the `ValidationException` with all 4 required context fields:

**Message** (lines 646-651):
```
ShipSpec.components entry does not map to a materialized
Ship component: ship_id='...' component_id='...' instance_index=... design_id='...'
```

**Context dict** (lines 655-660):
```python
context={
    "ship_id": ship_id,
    "component_id": component_id,
    "instance_index": instance_index,
    "design_id": design_id,
}
```

All four fields (`ship_id`, `component_id`, `instance_index`, `design_id`) appear in both the formatted message string and the structured `context` dictionary. The `context` dict keys are strings (not enums or raw variables), suitable for JSON serialization. This matches the pattern documented in `docs/05_ERROR_HANDLING.md` (Pattern 4: Include Context in Error Messages).

`ship_id` falls back from `ship.instance_id` to `ship_spec.instance_id` (line 644), ensuring context is never None.

### 2. Bit-Identical Materialization — VERIFIED

The two-pass design (`battle_runner.py:610-661`):

**Pass 1** (lines 610-633): Walks the Ship's layers in order, tracking per-component-id indices to match spec keys. For each match, applies HP damage. Tracks consumed keys in a `consumed: set`.

**Pass 2** (lines 638-661): Computes `unmapped_keys = spec_by_key.keys() - consumed`. If empty, no exception is raised — the function returns normally after completing Pass 1.

For valid specs (all spec entries map cleanly to materialized components), Pass 2 is a no-op: `unmapped_keys` is empty, and the function exits at line 661 without raising. The HP application in Pass 1 uses the same forward walk through layers as the pre-PROJ-358 code path, producing identical results. The `set` difference for Pass 2 is O(n) extra work with no behavioral change for valid specs, confirming the decisions.md rationale.

### 3. Silent-Drift Audit — ANALYSIS COMPLETE

Scanned all 35 matches for "silent|drift|ignore|skip.*component|design.*drift" across `game/simulation/`. Key findings:

**`game/simulation/entities/ship_serialization.py:198-199`** — Silent skip of unknown component IDs during deserialization:
```python
if comp_id not in comps:
    continue
```
When a serialized design references a component that doesn't exist in the current registry, the entry is silently dropped. This is the closest analog to the PROJ-358 bug: a mismatch between persisted component state and the live registry, absorbed without surface. See Finding MAJ-02.

**`game/simulation/components/abilities/__init__.py:170-171`** — `create_ability()` returns None silently when ability name is not in `ABILITY_REGISTRY`. This masks typos in ability names at load time; the component simply gets constructed without that ability.

**`game/simulation/components/abilities/__init__.py:185-186`** — `create_ability()` returns None when construction fails due to unevaluated formulas. This is intentional (deferred construction), but no distinction is made between "deferred due to formula" and "deferred due to genuine misconfiguration." Only the formula check short-circuits; other failures emit a warning.

**`game/simulation/battle_state.py:250`** — Corrupt component skip during ShipState loading: `"skipping corrupt component at {layer}[{i}]: {e}"`. The skip message is a format string but not traced to a `logger.warning` call in the immediate context — would need deep inspection to confirm it surfaces.

**`game/simulation/components/modifiers.py:50-51`** — Unknown modifier operation silently ignored with log warning. Similar pattern.

These are noted as findings below where they present real risk.

### 4. Error Code Consistency — VERIFIED

`ErrorCode.SCHEMA_VALIDATION_ERROR` (V002) is defined as: *"Schema or structural validation error (missing fields, invalid data structure)."*

The spec→ship component mismatch is structural: the spec describes a component layout the materialized design doesn't have. This fits V002 better than alternatives:
- V001 (`VALIDATION_FAILED`) — too generic; V002 is the more precise choice
- V003 (`MISSING_ENTITY`) — implies an entity lookup failure, not a structural mismatch
- C002 (`COMPONENT_INVALID`) — for component configuration errors, not spec→materialization drift

The only other production use of `SCHEMA_VALIDATION_ERROR` is `ship_serialization.py:193`, where a non-dict component entry is rejected — same semantic category (structural data validation). Consistent.

### 5. TDD Verification — VERIFIED

The test file (`test_spec_component_validation.py`) is organized into two groups:

**Failing tests** (lines 89-188) — `test_unmapped_component_id_raises_validation_with_full_context`, `test_unmapped_instance_index_raises_validation`, `test_mixed_valid_and_invalid_spec_raises_on_invalid`:
- All three use `pytest.raises(ValidationException)` and assert specific context field values
- The comment at lines 90-92 explicitly states: *"Pre-fix, the silent-ignore path absorbs the bad entries and the tests fail (no raise)"*
- On pre-PROJ-358 code (silent skip), `_apply_spec_components_to_ship` would return normally without raising, causing `pytest.raises()` to fail. Tests are properly failing-before-fixing.

**Passing tests** (lines 190-240) — `test_valid_spec_applies_hp_to_target_component`, `test_empty_components_no_op`:
- Verify correct HP application and no-op for valid/empty specs
- Assert on component HP values after `_apply_spec_components_to_ship` returns
- Work identically on both pre- and post-fix code paths

No overlap with PROJ-354A (`_extract_component_states` in `battle_runner.py:664-697`) — different function, different concern (end-state snapshot vs setup validation).

---

## Findings

### Priority Findings

#### 1. MAJOR: Silent Skip of Unknown Component IDs in Ship Deserialization
**ID:** CQ-01
**Location:** `game/simulation/entities/ship_serialization.py:198-199`
**Issue:** `ShipSerializer.from_dict()` silently skips component IDs not found in the registry:
```python
if comp_id not in comps:
    continue
```
**Impact:** Similar to the PROJ-358 bug: a mismatch between serialized component state and the running registry is absorbed without surface. A stale save referencing deleted/renamed components, or a materialization bug that produces wrong component IDs, would silently produce a ship with missing components rather than failing loudly.
**Recommendation:** Raise `ValidationException` with `code=ErrorCode.SCHEMA_VALIDATION_ERROR` (consistent with the PROJ-358 fix) when a serialized component ID is not found in the registry. Include layer name, component_id, and design context in the error.
**Effort:** Simple

#### 2. MAJOR: battle_runner.py Exceeds 500 LOC Production Ceiling
**ID:** CQ-02
**Location:** `game/simulation/battle_runner.py:730 lines`
**Issue:** File is 730 lines, exceeding the 500 LOC ceiling by 46%. Per `docs/03_CONVENTIONS.md` §2.3, production files must stay below 500 lines. The file has 8 functions covering materialization, engine setup, telemetry, outcome extraction, component state application, and end-reason derivation — multiple responsibilities.
**Impact:** Continued growth makes the file harder to review and test. Risk of God-module anti-pattern. The recent PROJ-358 change adds ~30 lines of validation logic.
**Recommendation:** Split into responsibilities: `_apply_spec_components_to_ship` and `_extract_component_states` could form a `ship_spec_application.py` sub-module. `_derive_end_reason` and `_build_ship_outcome` could live alongside extract_outcome in an `outcome_builder.py`. Not blocking for PROJ-358 — file as a follow-up cleanup ticket.
**Effort:** Medium

---

#### 3. MINOR: create_ability Silent Return for Unknown Ability Names
**ID:** CQ-03
**Location:** `game/simulation/components/abilities/__init__.py:170-171`
**Issue:** When an ability name is not found in `ABILITY_REGISTRY`, `create_ability()` silently returns `None`:
```python
if name not in ABILITY_REGISTRY:
    return None
```
**Impact:** A typo in a component JSON's ability name would produce a silent failure — the component loads without the intended ability. The caller (`Component.Constructor`) would receive None and skip that ability with no indication anything went wrong.
**Recommendation:** Log a warning at minimum when `name not in ABILITY_REGISTRY`. Consider whether this should raise for unknown ability names in production loads (test data may use placeholder ability names intentionally — the `combat_lab/` test data is a separate concern).
**Effort:** Simple

#### 4. MINOR: PROJ-354A Overlap Risk — No Conflict Found
**ID:** CQ-04
**Location:** `game/simulation/battle_runner.py:580-661` vs `battle_runner.py:664-697`
**Issue:** Reviewed for overlap between PROJ-358 (`_apply_spec_components_to_ship`, lines 580-661) and PROJ-354A (`_extract_component_states`, lines 664-697). These are separate functions with separate concerns (setup HP application vs end-state snapshot capture). They share no mutable state and are called at different phases of the battle lifecycle (materialization vs outcome extraction). No overlap found.
**Impact:** None — informational.
**Recommendation:** No action needed.
**Effort:** N/A

#### 5. MINOR: decisions.md Audit Claim Verification Gap
**ID:** CQ-05
**Location:** `Projects/active_projects/PROJ-358/decisions.md:18`
**Issue:** The decisions log states: *"All 8 `ComponentStateSpec(...)` usages in tests/ construct entries that map cleanly to their fixture designs. None encoded the bug."* A spot-check of the test file confirms the 5 new tests use clean spec→fixture mappings, but the claim covers 8 usages across the full test suite — this review covered only the named scope file. The remaining ~3 usages were not individually verified.
**Impact:** Low. If other test files did encode the silent-drift behavior, those tests would now fail (they'd see `ValidationException` where they expected silent absorption). This would surface at the next test run.
**Recommendation:** Run the full test suite and verify zero failures in other `_apply_spec_components_to_ship` callers. If any existing tests encoded the bug, they will fail and need updating (replace `_apply_spec_components_to_ship` call with an assert-raises pattern to match the new contract).
**Effort:** Simple

---

#### 6. INFO: Late Import Pattern Consistent with Conventions
**ID:** CQ-06
**Location:** `game/simulation/battle_runner.py:640-641`
**Issue:** `ErrorCode` and `ValidationException` are imported locally inside `_apply_spec_components_to_ship` — a late import pattern:
```python
from game.core.error_codes import ErrorCode  # noqa: PLC0415
from game.core.exceptions import ValidationException  # noqa: PLC0415
```
**Impact:** None — this is acceptable. The docstring at line 590-598 explains the failure semantics, and the local imports avoid adding a module-level dependency on `exceptions` for the hot path (valid specs rarely hit this code). However, `ValidationException` is already module-familiar through `run_battle` (which raises `RuntimeError` but could use `ValidationException` — the `RuntimeError` at line 310 is a separate convention question). The `# noqa: PLC0415` comments are present per ruff convention. 
**Recommendation:** No action needed. If the file is split (CQ-02), consider moving the error-code imports to module level, as the split sub-module would be focused on spec application/validation.
**Effort:** N/A

#### 7. INFO: pre_tick_loop_callback Typo in Docstring
**ID:** CQ-07
**Location:** `game/simulation/battle_runner.py:293`
**Issue:** Minor typo: `pre_tick_loop_callback` docstring says "one-shot hook fired AFTER `engine.start_teams()` completes and BEFORE the first tick" — this is correct for the semantics but the docstring formatting at line 293 uses a bullet-point style that differs from the `per_tick_callback` doc immediately above (line 290: "Used by Combat Lab scenarios for per-tick observation..." vs no similar prose explanation for pre-tick semantics). Not a bug — informational only.
**Impact:** None. Cosmetic.
**Recommendation:** No action needed.
**Effort:** N/A

---

## PROJ-358 Specific: PROJ-354A Overlap Check

Confirmed no overlap. `_apply_spec_components_to_ship` (PROJ-358, lines 580-661) applies per-component HP during ship materialization (setup phase). `_extract_component_states` (PROJ-354A, lines 664-697) captures final component state during outcome extraction (teardown phase). They share the same `per_id_index` tracking pattern for component instance indexing, but operate on different data at different lifecycle points. No shared mutable state.

---

## Verification Matrix

| Instruction | Status | Details |
|---|---|---|
| 1. Context fields in message + dict | **Verified** | All 4 fields present in both message and context dict at battle_runner.py:646-660 |
| 2. Bit-identical for valid specs | **Verified** | Two-pass design preserves forward walk; Pass 2 is no-op for valid specs |
| 3. Silent-drift audit | **Complete** | Identified ship_serialization.py:198-199 as related risk (MAJ-01); 4 additional minor patterns noted |
| 4. Error code consistency | **Verified** | V002 SCHEMA_VALIDATION_ERROR is semantically correct and consistent with ship_serialization.py:193 |
| 5. TDD verification | **Verified** | 3 failing tests would fail on pre-fix code; 2 passing tests work on both |

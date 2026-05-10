# Shard 15 — Skeptical Verification Report

**Verifier:** OpenCode skeptical verification agent  
**Source:** SHARD_15.md Phase 2 discovery report  
**Date:** 2026-05-05  
**Scope:** 2 CRITICAL + 2 MAJOR claims + 1 ADDITIONAL (report-internal inconsistency)  

---

## Verification Summary

| Claim | Severity | Verdict | Key Evidence |
|-------|----------|---------|-------------|
| `ship_combat_manager.py` — Tier 0, no tests | CRITICAL | **DISPUTED** | Dedicated test file exists: `tests/unit/simulation/entities/test_ship_combat_manager.py` (272 LOC, 19 tests, 6 test classes) |
| `replay_capture.py` — Tier 0, no tests | CRITICAL | **DISPUTED** | Dedicated integration test: `tests/integration/strategy/test_replay_capture_e2e.py` (363 LOC). 3 additional files import the module. |
| `modifier_manager.py` — `_load_initial_modifiers()` not symbolic | MAJOR | **CONFIRMED-MITIGATED** | Internal method, called from `__init__`. Covered by `TestStatefulModifierManagerConstruction` (3 tests, lines 149–183 of test file). Risk: LOW. |
| `modifier_manager.py` — deprecated statics untested | MAJOR | **CONFIRMED** | 5 deprecated static methods have zero independent test coverage. Instance variants ARE tested. Risk: LOW (deprecated, logic cloned to instance methods). |
| `modifier_schema.py` — formula delegate call untested | MAJOR | **DISPUTED** | `test_modifier_invalid_formula_propagates` (test line 348) directly exercises `ModifierEffectEvaluator.validate_formula()` call at schema line 237. |
| `_formation_utils.py` — Tier 0, table↔narrative inconsistency | ADDITIONAL | **CONFIRMED** (untested) | `compute_circular_position` has 0 direct test references (`rg` confirms). Report assigns **CRITICAL** in table (line 145) but **ADVISORY** in narrative (line 67). Severity should be ADVISORY (39 LOC pure-math helper). |

---

## CRITICAL #1: `ship_combat_manager.py` — **DISPUTED**

### Phase 2 Claim
> Tier 0 — all 7 symbols untested. No dedicated test file exists. Tests that exercise Ship indirectly test this via `Ship.update()` — verification required.

### Evidence

**Dedicated test file found:**
`tests/unit/simulation/entities/test_ship_combat_manager.py` — 272 lines, 19 tests across 6 test classes.

| Test Class | Tests | What it covers |
|------------|-------|---------------|
| `TestShipCombatManagerUpdate` | 4 | `update()` dead short-circuit (line 44), subsystem ordering (line 53), firing trigger pulled/not-pulled (lines 67, 79) |
| `TestShipCombatManagerDerelict` | 4 | `update_derelict_status()` — no weapons/engines (line 111), recovery (line 117), bridge reset (line 141), crew check (line 147) |
| `TestShipCombatManagerDie` | 3 | `die()` — alive flag (line 174), velocity zeroing (line 180), recalculate_stats call (line 187) |
| `TestShipCombatManagerCombatEngine` | 1 | `combat_engine` property lazy creation + idempotency (line 205) |
| `TestShipCombatManagerPropertyDelegation` | 6 | `just_fired_projectiles` get/set, `comp_trigger_pulled` get/set, `aim_point` get/set |
| `TestShipSetEventBus` | 1 | `set_event_bus()` delegation to combat engine (line 268) |

File docstring confirms: *"Tests written BEFORE implementation (TDD)"* and *"since ShipCombatManager is an internal delegate and Ship preserves its facade API, these tests exercise the manager through Ship's public methods"*.

### Verdict: **DISPUTED**

The Phase 2 report's `coverage_matrix.json` failed to detect this test file. All 7 symbols (`ShipCombatManager`, `__init__`, `combat_engine`, `set_event_bus`, `die`, `update`, `update_derelict_status`) are exercised through the 19 tests. This file should be **Tier 3 (Verified Covered)**.

---

## CRITICAL #2: `replay_capture.py` — **DISPUTED**

### Phase 2 Claim
> Tier 0 — all 10 symbols untested. No dedicated test. The critical untested path: end-to-end wiring with ReplayStore.

### Evidence

**Dedicated integration test file found:**
`tests/integration/strategy/test_replay_capture_e2e.py` — 363 lines, 6 tests across 4 test classes.

| Test Class | Coverage of `replay_capture.py` elements |
|------------|------------------------------------------|
| `TestNoCapableBranchTruncatedReplayCapture` (3 tests) | `set_default_capture_sink()` (line 186), `reset_default_capture_sink()` (line 219). Uses `IReplayCaptureSink` protocol via `_RecordingCaptureSink` fake. Tests `on_battle_started`/`on_battle_ended` round-trip. |
| `TestSoleSurvivorBranchHonestTooltip` (1 test) | Imports `reset_default_capture_sink` indirectly through adapter imports. |
| `TestReasonFlowsThroughEventBus` (1 test) | Exercises `replay_unavailable_reason` propagation. |
| `_patched_run_battle_factory` helper | Directly instantiates `ReplaySpec` and drives sink callbacks, testing the full capture contract. |

**Additional import usage:**
- `tests/unit/test_app_bootstrap_profiling.py:52` — imports `reset_default_capture_sink`
- `tests/unit/test_app_bootstrap_invariants.py:52,142` — imports `reset_default_capture_sink` + full module
- `tests/unit/systems/test_main_integration.py:29` — imports `reset_default_capture_sink`

The `NullCaptureSink` default path is exercised implicitly in every test run (including the 25,000+ tests in the full suite). No test explicitly exercises `NullCaptureSink.on_battle_started`/`on_battle_ended` with assertions, but the methods are 3-line no-ops.

### Verdict: **DISPUTED**

The Phase 2 report missed the dedicated integration test file. This file should be **Tier 2 (Partial Coverage)** — the protocol, DI get/set/reset, and the sink contract are tested end-to-end. The only genuinely untested element is direct unit testing of `NullCaptureSink` (3-line no-ops, negligible risk).

---

## MAJOR #1a: `modifier_manager.py` — `_load_initial_modifiers()` — **CONFIRMED-MITIGATED**

### Phase 2 Claim
> `_load_initial_modifiers()` not listed as separate symbol (internal, called from `__init__`). Risk: Low for production code (instance methods are the canonical path).

### Evidence

**Production code:** `modifier_manager.py` lines 57–81. `_load_initial_modifiers()` reads `component.data['modifiers']` and creates `ApplicationModifier` instances. Called from `__init__` at line 55.

**Test coverage:** `test_modifier_manager.py` tests:

| Test | Line | What it verifies |
|------|------|-----------------|
| `test_construction_no_initial_modifiers` | 149 | `ModifierManager(railgun)` with no data → empty modifiers list |
| `test_construction_loads_modifiers_from_data` | 159 | Injects `data['modifiers']`, verifies `_load_initial_modifiers()` populates list |
| `test_construction_skips_unknown_modifiers` | 171 | Unknown modifier IDs in registry → skipped with warning |

These tests directly exercise `_load_initial_modifiers()` through the constructor call path — covering the "no data" branch (line 67–68), the normal load path (lines 70–76), and the unknown-modifier branch (lines 77–81).

**What is NOT tested:**
- Direct call to `_load_initial_modifiers()` as a standalone function (it's a private method)
- Re-calling `_load_initial_modifiers()` after construction

### Verdict: **CONFIRMED-MITIGATED**

The claim is technically correct — `_load_initial_modifiers()` is not listed as a separate coverage symbol. However, it IS tested through the constructor, covering all 3 branches. The "MAJOR" severity is exaggerated; this is a MINOR structural reporting gap.

---

## MAJOR #1b: `modifier_manager.py` — Deprecated statics untested — **CONFIRMED**

### Phase 2 Claim
> All 5 deprecated static methods listed as "tested" through instance method aliases. Should be verified independently before removal in Task 1.3.

### Evidence

**Production code — 5 deprecated statics (lines 221–330):**
1. `add_modifier_static()` — lines 223–251
2. `remove_modifier_static()` — lines 253–259
3. `remove_modifier_inplace()` — lines 261–274 (used internally by `add_modifier_static`)
4. `get_modifier_static()` — lines 276–285
5. `get_all_effects_static()` — lines 287–294
6. `get_stat_summary_static()` — lines 296–330

**Test file note (line 140–143):**
```python
# NOTE: TestModifierManagerStandalone removed in PROJ-322 Task 1.3
# (S02-CAT4-001). The deprecated `add_modifier_static` / `remove_modifier_static`
# / `get_modifier_static` static-method wrappers are already covered by the
# instance-method tests above.
```

This note is misleading — the instance method tests exercise DIFFERENT functions from the statics. The instance methods (e.g., `mgr.add_modifier()`) and static methods (e.g., `ModifierManager.add_modifier_static()`) share similar logic but are separate code paths. No test in `test_modifier_manager.py` calls any of the 5 deprecated statics.

Grep confirms 0 callers of the static variants in the test suite.

### Verdict: **CONFIRMED**

The 5 deprecated static methods have **zero independent test coverage**. The instance methods are well-tested (19 tests), and the logic is nearly identical, so the practical risk of cleanup regression is LOW. The Phase 2 report's characterization as "tested through instance method aliases" is inaccurate per the note — the coverage claim is aspirational, not actual.

**Recommendation:** Before PROJ-322 Task 1.3 cleanup, either write a minimal smoke test for each deprecated static or (better) verify zero callers exist in production code and delete without tests.

---

## MAJOR #2: `modifier_schema.py` — Formula delegate call — **DISPUTED**

### Phase 2 Claim
> `validate_modifier_v2` line 237 calls `ModifierEffectEvaluator.validate_formula()` which may not be tested in schema tests specifically.

### Evidence

**Production code** (`modifier_schema.py` lines 236–239):
```python
formula_errors = ModifierEffectEvaluator.validate_formula(effect['formula'])
if formula_errors:
    return False
```

**Test coverage** (`test_modifier_schema.py`):

| Test | Line | What it verifies |
|------|------|-----------------|
| `test_modifier_valid_complete` | 273 | Valid formula `'param'` passes both structural AND formula validation |
| `test_modifier_invalid_formula_propagates` | 348 | Invalid formula `'param +'` (bad syntax) → `validate_modifier_v2` returns False |

`test_modifier_invalid_formula_propagates` at line 348 **directly exercises** the `ModifierEffectEvaluator.validate_formula()` delegation at line 237. The test creates a modifier with `'formula': 'param +'` — syntactically valid for `validate_effect_v2()` (line 63 passes: it's a string), but semantically invalid for `ModifierEffectEvaluator.validate_formula()`. If line 237 returned `[]` (no errors), the test would fail because `validate_modifier_v2` would return `True` instead of `False`.

### Verdict: **DISPUTED**

The formula delegate call IS explicitly tested in the schema test file. The Phase 2 claim that it "may not be tested" is incorrect. This is **Tier 3** coverage for this code path.

---

## ADDITIONAL: `_formation_utils.py` — Report-internal inconsistency

### Observation

The Phase 2 report self-contradicts on `game/ai/spatial_behaviors/_formation_utils.py` (39 LOC):

- **Line 145 (verification table):** Listed as **CRITICAL** Tier 0 — `compute_circular_position untested. Indirectly exercised via Escort/Screen.`
- **Line 67–71 (narrative):** Listed as **ADVISORY** Tier 0 — `Pure math helper... Risk: Low.`

### Verification

`rg compute_circular_position` against `tests/` returns **0 matches**. The function is not directly tested. It IS called from:
- `game/ai/spatial_behaviors/escort_behavior.py`
- `game/ai/spatial_behaviors/screen_behavior.py`

These callers are Tier 2 (partially tested), so indirect exercise is plausible but unverified at the unit level.

### Verdict: **CONFIRMED** (untested), but severity should be **ADVISORY**, not CRITICAL.

The function is 39 LOC of pure-math helper with 1 branch (`total = max(int(total), 1)`). The table's CRITICAL assignment is inconsistent with the narrative's ADVISORY assignment. ADVISORY is appropriate for this risk profile.

---

## Phase 2 Report Accuracy Scorecard

| Aspect | Status | Detail |
|--------|--------|--------|
| `ship_combat_manager.py` classification | ❌ **Wrong** | Claimed Tier 0/no tests; test file exists with 19 tests |
| `replay_capture.py` classification | ❌ **Wrong** | Claimed Tier 0/no tests; integration test file exists with 6 tests |
| `modifier_manager.py` `_load_initial_modifiers` gap | ✅ **Correct** | Not a separate coverage symbol, but tested through init |
| `modifier_manager.py` deprecated statics gap | ✅ **Correct** | 5 statics have zero independent test coverage |
| `modifier_schema.py` formula delegate gap | ❌ **Wrong** | Claimed "may not be tested"; proven tested via `test_modifier_invalid_formula_propagates` |
| `_formation_utils.py` severity | ❌ **Inconsistent** | CRITICAL in table, ADVISORY in narrative |

**Net: 2/4 CRITICAL claims invalid, 1/2 MAJOR claims invalid.** The Phase 2 discovery method (relying on `coverage_matrix.json` without verifying test file existence) produced 3 false positives.

---

## Revised Tier Assignments

| File | Phase 2 Tier | Verified Tier | Rationale |
|------|-------------|--------------|-----------|
| `ship_combat_manager.py` | 0 (CRITICAL) | **3** (Verified) | 19 dedicated tests exist |
| `replay_capture.py` | 0 (CRITICAL) | **2** (Partial) | Integration tests + null sink path covered; no direct unit test for NullCaptureSink methods |
| `_formation_utils.py` | 0 (CRITICAL/ADVISORY) | 0 (ADVISORY) | Truly untested, but low-risk math helper |
| `modifier_schema.py` (formula path) | 2 (MAJOR gap) | **3** (Verified) | Formula delegate explicitly tested |

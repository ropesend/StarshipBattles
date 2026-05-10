# Verified Shard 10 — Test Coverage Audit

**Verifier:** OpenCode Skeptical Verifier  
**Date:** 2026-05-04  
**Source:** `SHARD_10.md` Phase 2 Discovery Report

---

## Summary

| Original Severity | Count | CONFIRMED | DISPUTED | DOWNGRADED |
|---|---|---|---|---|
| CRITICAL | 1 | 0 | 1 | 1 → ADVISORY |
| MAJOR | 6 (section) + 2 (table) | 4 | 4 | 1 → MINOR |

**Key findings:** The Discovery Agent over-reported gaps by a factor of ~3x. Several "untested" modules actually have extensive test suites. Three MAJOR gaps are genuine (race_resolver, modifier_icon_service, modifier_row widget) plus one untested symbol (get_capability_cache_key).

---

## CONFIRMED Gaps

### MAJOR-01: `game/ai/combat_utils.py` — `get_capability_cache_key` (lines 73-87)

**Confirmed UNTESTED.** Zero references to `get_capability_cache_key` exist in any test file. The test file `tests/unit/ai/test_combat_utils.py` (559 LOC) imports every other public function from `combat_utils.py` but omits this one. Three code paths are untested:

1. `entity.id` exists → returns `entity.id` (line 80-81)
2. `entity.id` missing but `name` exists → returns `entity.name` (line 83-85)
3. Neither exists → returns `None` (line 87)

This is the only untested symbol in the module. The other 8 functions have thorough coverage including edge cases (zero-length vector guard at line 226, `is_in_pdc_arc` boundary conditions at all angles, etc.).

**Recommendation:** Add `TestGetCapabilityCacheKey` class to `tests/unit/ai/test_combat_utils.py` with 3 tests for each code path.

---

### MAJOR-02: `game/strategy/services/race_resolver.py` — No dedicated test file

**Confirmed UNTESTED.** No file matching `test_race_resolver*.py` exists. The function `resolve_race_config()` (lines 18-43) has four code paths, none exercised in isolation:

| Path | Lines | Description |
|---|---|---|
| Registry returns config | 34-37 | `race_registry.get_race(race_id)` succeeds |
| Registry returns None + empire match | 38-42 | Fallback to empire.race_config when race_id matches |
| Empire match (no registry) | 38-42 | Direct match when `race_registry` is None |
| No match → None | 43 | Silent skip for non-primary species (PROJ-291 C3) |

Additionally: `race_registry is None` bypass path (line 34) and `empire.race_config is None` exit (line 39-40).

**Impact:** This feeds population growth and happiness calculations. A silent mis-match would produce wrong values for multi-species colonies.

**Recommendation:** Create `tests/unit/strategy/services/test_race_resolver.py` with 6 tests covering all paths.

---

### MAJOR-03: `game/ui/services/modifier_icon_service.py` — No dedicated test file

**Confirmed UNTESTED.** No file matching `test_modifier_icon*` exists. All three public methods are untested:

| Method | Lines | Untested Paths |
|---|---|---|
| `__init__` | 37-46 | icon_size config, cache init, base_path construction |
| `get_icon()` | 48-83 | Cache hit, cache miss + map lookup, filename not in map → fallback `mod_{id}.png`, file not found, pygame load error (line 81), scale path (surface size != icon_size) |
| `clear_cache()` | 85-87 | Cache clearing |

**Recommendation:** Create `tests/unit/ui/services/test_modifier_icon_service.py` covering cache behavior, fallback filename, missing file, and error handling.

---

### MAJOR-04: `game/ui/screens/builder/modifier_row.py` — Minimal test coverage

**Confirmed MAJOR gap.** A test file exists at `tests/unit/ui/screens/builder/test_modifier_control_row.py` (156 LOC), but it only tests two internal helper methods (`_get_local_bounds` and `_set_controls_enabled`). The primary widget functionality is untested:

| Area | Status |
|---|---|
| `build_ui()` — 3 control types (linear, linear_stepped, facing_selector) | UNTESTED |
| `update()` — component/template state sync, mandatory lock | UNTESTED |
| `handle_event()` — button dispatch, slider, text entry, toggle | UNTESTED |
| `kill()` / `_clear_ui()` — cleanup | UNTESTED |
| Smart snap-to-floor/ceil with MinMaxBounds | UNTESTED |
| Preset button rendering and click handling | UNTESTED |
| Step button delta_add/delta_sub/set_value modes | UNTESTED |

The widget is 355 LOC with 3 control type branches, interactive state management, and mandatory modifier locking. The existing tests (156 LOC) cover ~15% of the logic.

**Recommendation:** Expand `test_modifier_control_row.py` to cover `handle_event` dispatch, `update` state transitions, and `build_ui` layout variations.

---

## Disputed / Inconclusive Claims

| Original | File | Claim | Verdict | Evidence |
|---|---|---|---|---|
| **CRITICAL** | `game/core/profiling.py` | "No dedicated unit test file... only edge cases" | **DISPUTED** → Downgraded to ADVISORY | 3 dedicated test files exist: `test_profiling_edge_cases.py` (372 LOC), `profiling/test_recording.py` (125+ LOC), `profiling/test_persistence.py` (29+ LOC), plus `test_profiler_perf.py`. All 7 public methods have explicit tests. `get_default_profiler()`/`set_default_profiler()` are not directly asserted but are exercised through fixtures. |
| **MAJOR** | `game/services/llm/background.py` | "Complex concurrency; verify all paths" | **DISPUTED** | `test_background.py` (343 LOC) covers all 7 specific areas the report flags: cancel-before-start (line 216), wait() API used throughout, finally decrement verified via `test_completed_calls_free_up_slots`, shutdown timeout path (line 325), `__init__` validation (lines 104-116), `LLMUnexpectedError` wrapping (lines 166-191), counter guard (lines 236-272). **One minor gap**: cancel-before-start status transition (PENDING→CANCELLED) is not explicitly asserted, only safety-tested. |
| **MAJOR** | `game/strategy/engine/order_processor.py` | "Sub-methods need verification" | **DISPUTED** | All 7 sub-methods the report lists have dedicated tests: `_deploy_drop_pod` (tested in `test_order_processor_colonize.py` lines 163, 192, 305), `_execute_fleet_transfer` (tested via fleet-target transfer tests), `_load_pod_from_staging_yard` (line 377), `_unload_pod_to_staging_yard` (line 407), `_elect_canonical_merges` (lines 105, 121), `process_instant_orders` re-validation (lines 142, 172), `_validate_tick_inputs` (line 59). |
| **MAJOR** | `game/strategy/data/fleet.py` | "No dedicated unit test file... indirect only" | **DISPUTED** → Downgraded to MINOR | 6+ dedicated unit test files exist under `tests/unit/strategy/fleet/` and `tests/unit/strategy/data/`: `test_basics.py` (merge, orders, equality), `test_serialization.py` (to_dict, from_dict, roundtrip, hierarchy), `test_fleet_pursuer_tracker.py` (redirects, unregister), `test_fleet_hierarchy_integration.py` (task force serialization, merge clears task forces), `test_fleet_hierarchy.py`, `test_fleet_order_resolution.py`. **One genuine gap**: `remove_orders_by_type_and_target()` (lines 346-369) is only tested indirectly via `merge_with` pursuer redirect tests, not in isolation. |
| **MAJOR** (table) | `game/core/resources.py` | "Error fallback paths untested" | **DISPUTED** → Retain as MINOR | `test_resources.py` (188 LOC) covers file-not-found (line 95), JSON decode error (line 103), path resolution absolute/relative (lines 23-62), empty list, None/empty ids. Only the broad `except` catch for PermissionError/OSError/TypeError/AttributeError is not explicitly tested — these are defensive fallback paths impossible to trigger deterministically. |

---

## Discovery Agent Errors

The Phase 2 Discovery Agent made these systematic errors:

1. **File-absence blindness:** Stated "no dedicated test file" for 4 modules (`profiling.py`, `fleet.py`, `modifier_row.py`, `resources.py`) where test files clearly exist. The profiler alone has 3 test files totaling 500+ LOC.

2. **Unverified severity assignment:** The `profiling.py` CRITICAL rating contradicts the test evidence. `test_profiling_edge_cases.py` explicitly tests `record()` active/inactive paths (lines 213-244), `toggle()` both directions (lines 250-268), `clear()` (lines 271-290), `save_history()` (lines 30-71, 181-207), `profile_action` decorator (lines 77-127, 296-334), and `profile_block` context manager (lines 133-172, 340-371). This is comprehensive, not "edge cases only."

3. **Inconsistent severity labeling:** `resources.py` is listed as MAJOR GAP in the file-coverage table (line 244) but appears under the MINOR section in detailed findings (lines 136-147). The actual test coverage is adequate for the severity — the untested paths are purely defensive exception handlers.

4. **Missed existing tests for claimed gaps:** The report flags `order_processor.py` sub-methods as "need verification" when each has a dedicated characterization test added in PROJ-333 Phase 1. The auditor appears not to have cross-referenced recent test additions.

5. **Breadth-over-depth scanning:** The fleet module has ~15 test files spanning unit, integration, and end-to-end levels. The Discovery Agent's conclusion of "no dedicated unit test" suggests it searched only for a single `test_fleet.py` file rather than checking the subdirectory structure (`tests/unit/strategy/fleet/`, `tests/unit/strategy/data/test_fleet*.py`).

---

## Final Severity Map

| Finding | Original | Verified |
|---|---|---|
| `combat_utils.get_capability_cache_key` untested | MAJOR | **MAJOR** ✓ |
| `race_resolver.py` no tests | MAJOR | **MAJOR** ✓ |
| `modifier_icon_service.py` no tests | MAJOR | **MAJOR** ✓ |
| `modifier_row.py` minimal tests | MAJOR (table) | **MAJOR** ✓ |
| `profiling.py` no dedicated test | **CRITICAL** | **ADVISORY** ↓ |
| `background.py` concurrency gaps | MAJOR | **MINOR** ↓ |
| `order_processor.py` sub-methods | MAJOR | **CLEARED** |
| `fleet.py` no dedicated test | MAJOR | **MINOR** ↓ |
| `resources.py` error paths | MAJOR (table) | **MINOR** ↓ |

**Verified severity count:** 4 MAJOR, 3 MINOR, 1 ADVISORY, 1 CLEARED.

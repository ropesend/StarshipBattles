# Review Report: PROJ-391 — Three Small Consolidations

**Request ID:** req_20260509_024407_344a83
**Review Type:** code
**Review Date:** 2026-05-09T02:48:00Z
**Reviewer:** OpenCode (ocode-review-request skill)
**Review Mode:** direct (inline analysis — no sub-agents spawned; scope is narrow and well-defined)
**Branch:** `feat/03c-phase-aware-execution` (HEAD: eeaa4bdec)

## Coverage

- **Files reviewed:** 10 (6 production, 4 test)
- **Commits reviewed:** 4 (46fab01a3 → d355166fd → 89d4864e6 → eeaa4bdec)
- **Pre-migration baselines:** Verified against parent commits for each task

## Summary

All three consolidations are **semantically equivalent**. No production references to deleted helpers remain. Pattern 17 conformance is exact. Replay deserialization is intact. One minor finding (defensive dead code) and one informational note.

---

## Findings

| ID | Severity | Title | File | Lines |
|----|----------|-------|------|-------|
| FND-001 | MINOR | Defensive list-normalization for `ResourceHarvester` never exercises list path | `game/strategy/services/planet_economy_projector.py` | 228–231 |

---

## Detailed Verification

### 1. Final Grep Verification (per-symbol)

| Symbol | Production Hits | Result |
|--------|----------------|--------|
| `_get_harvester_info` | 0 (comments only) | PASS |
| `_iter_components` | 0 (test method names + unrelated test-local helper only) | PASS |
| `_formation_to_dict` | 0 (comments only) | PASS |
| `_formation_from_dict` | 0 (comments only) | PASS |

**Details:**
- `_get_harvester_info`: 1 production file hit (`planet_report_panel.py:670`) — **comment only** (`# PROJ-288 Task 2.3: ... _get_harvester_info`). All test hits are `from ... import get_harvester_info as _get_harvester_info` aliases — acceptable per instructions.
- `_iter_components`: 0 production hits. Test hits: `test_dual_scope_validation.py` defines a *different* local `_iter_components()` that loads JSON (unrelated). Test method names `test_iter_components_*` are acceptable.
- `_formation_to_dict` / `_formation_from_dict`: only in comments (`task_force.py` line 123, `test_serialization.py` line 334).

### 2. `get_harvester_info` Return-Type Widening

**Canonical return type:** `dict | list | None` (from `_get_ability_info` in `harvesting_engine.py:39`)

**Migration in `compute_planet_production`** (lines 221–231):
```python
harvester = get_harvester_info(comp, registries)
if harvester is None:
    continue
entries = [harvester] if isinstance(harvester, dict) else harvester
for entry in entries:
    if not isinstance(entry, dict):
        continue
```

- Dict path: single harvester → wraps in list → processed. ✅
- List path: multiple harvesters → iterated directly. ✅
- None path: skipped. ✅
- Non-dict entries in list: skipped by inner guard. ✅

**Minor concern (FND-001):** The list-handling branch (`else harvester`) is defensive code. `ResourceHarvester` abilities in `components.json` are universally single-dict entries (a component harvests exactly one resource type). The `_get_ability_info` function accepts `dict | list` for generality (shared with `ResourceHarvestBooster`, `LocalStorage`, etc.), but harvesters are never lists in practice. The pattern is consistent with how `HarvestingEngine._process_facility` and other internal callers normalize — so this is not wrong, just dead code in the projector's context.

**Secondary site** (`planet_economy_projector.py:220-231`): Correctly migrated from manual `layer_data.get("layers", {}).values()` iteration to canonical `iter_components(facility.design_data)`. ✅

### 3. `iter_components` Semantic Change

**Canonical `iter_components`** (`game/core/patterns/layer_iterator.py:42`):
- Handles both list-format layers (`layers[name] = [comp1, ...]`) and dict-format layers (`layers[name] = {"components": [...]}`)
- Yields both dicts (`{"id": "x", ...}`) and strings (`"reactor_mk1"`)

**Legacy `_iter_components`** (deleted from `spec_compiler.py`):
- Only handled list-format layers
- Only yielded dicts (filtered out strings)

**Migration in `spec_compiler.py`** (line 361):
```python
for component_data in iter_components(design_data):
    if not isinstance(component_data, dict):
        continue
```
- Strings are correctly skipped. ✅
- Dict-format layers are now supported. ✅

**Cross-system secondary site** (`planet_economy_projector.py:220-231`): Already migrated to canonical `iter_components`. ✅

### 4. `FormationSpec.to_dict/from_dict` Semantic Preservation

**Pre-migration `task_force.py` implementation:**
```python
def _formation_to_dict(formation: FormationSpec) -> Dict[str, Any]:
    return {
        "shape": formation.shape.value,
        "spacing": float(formation.spacing),
        "custom_positions": [[float(p.x), float(p.y)] for p in formation.custom_positions],
    }
```

**Pre-migration `replay_serialization.py` implementation (for FormationSpec inputs):**
```python
def _formation_to_dict(formation: Any) -> Dict[str, Any]:
    if isinstance(formation, FormationSpec):
        return {
            "shape": formation.shape.value,
            "spacing": float(formation.spacing),
            "custom_positions": [_vec_to_list(p) for p in formation.custom_positions],
        }
```

**Canonical `FormationSpec.to_dict()`:**
```python
def to_dict(self) -> Dict[str, Any]:
    return {
        "shape": self.shape.value,
        "spacing": float(self.spacing),
        "custom_positions": [[float(p.x), float(p.y)] for p in self.custom_positions],
    }
```

**Byte-identical verification:** `_vec_to_list(v)` is defined as `[float(v.x), float(v.y)]` at `replay_serialization.py:78`. Both expressions produce `[float(p.x), float(p.y)]` — confirmed identical via runtime test. ✅

**`from_dict` comparison:**

| Aspect | Pre-migration `_formation_from_dict` | Canonical `FormationSpec.from_dict` |
|--------|--------------------------------------|-------------------------------------|
| Shape | `FormationShape(data["shape"])` | `FormationShape(data["shape"])` ✅ |
| Spacing default | `100.0` (hardcoded) | `FormationResolver.DEFAULT_SPACING` (= 100.0) ✅ |
| Custom positions | `tuple(Vector2(float(p[0]), float(p[1])) for p in ...)` | `tuple(Vector2(float(p[0]), float(p[1])) for p in ...)` ✅ |
| None input | Separate `if data is None: return None` | Handled at call site (both old and new) ✅ |

**Round-trip test:** `FormationSpec.from_dict(spec.to_dict()) == spec` — runtime confirmed for WEDGE (no custom positions) and CUSTOM (with positions). ✅

### 5. Replay Wrapper's Vestigial Slot

**Pre-migration fallback** (for non-FormationSpec inputs):
```python
return {"shape": FormationShape.LINE_ASTERN.value, "spacing": 0.0, "custom_positions": []}
```

**New behavior** (in `_task_force_spec_to_dict`):
```python
formation_dict = (
    formation.to_dict() if isinstance(formation, FormationSpec) else None
)
```

- Non-FormationSpec → `None` (was: synthetic LINE_ASTERN placeholder). ✅
- `_task_force_spec_from_dict` handles `None` correctly (returns `None` formation). ✅
- Unit test `test_task_force_spec_serializes_non_formation_object_as_none` explicitly validates this behavior. ✅
- No replay caller relies on the old placeholder — confirmed by searching all test files and production code for references to the synthetic LINE_ASTERN fallback. ✅

### 6. Pattern 17 Conformance

| Requirement | Implementation | Status |
|-------------|---------------|--------|
| `to_dict(self) -> Dict[str, Any]` | `FormationSpec.to_dict(self) -> Dict[str, Any]` | ✅ |
| `@classmethod from_dict(cls, data: dict) -> Type` | `@classmethod from_dict(cls, data: Dict[str, Any]) -> "FormationSpec"` | ✅ |
| Round-trip: `from_dict(x.to_dict()) == x` | Verified for WEDGE and CUSTOM shapes | ✅ |
| No circular import from lazy `DEFAULT_SPACING` | Same file; resolved at call time, not import time | ✅ |

**`FormationResolver.DEFAULT_SPACING` lazy reference:** `FormationSpec.from_dict` references `FormationResolver.DEFAULT_SPACING` inside the method body (line 86). Since `FormationResolver` is defined later in the same module (line 94), this is only resolved at call time — no circular import risk. Confirmed: `FormationSpec.from_dict({'shape': 'line_astern'})` succeeds and returns `spacing=100.0`. ✅

### 7. CLAUDE.md Rule 3 Compliance

All 4 deleted helpers (`_get_harvester_info`, `_iter_components`, `_formation_to_dict`, `_formation_from_dict`) are gone — no replacement shims, no compatibility wrappers, no re-exports. Each caller migrated directly to the canonical interface. ✅

---

## Verification Matrix

No parent request — this is a standalone review.

---

## Test Coverage Notes

- `test_task_force_spec_serializes_non_formation_object_as_none` (test_serialization.py:333): Explicitly validates new `None` behavior for non-FormationSpec inputs. ✅
- Existing round-trip tests (`TestTaskForceSpecSerialization`, `TestBattleSpecSerialization`) continue to pass with FormationSpec inputs via the new `to_dict`/`from_dict`. ✅
- `test_iter_components_*` tests in `test_spec_compiler.py` updated for canonical `iter_components`. ✅
- `_get_harvester_info` tests in `test_planet_report_panel.py` and `test_strategy_detail_formatter.py` updated to use `get_harvester_info as _get_harvester_info` aliases. ✅

---

## Conclusion

**All three consolidations are correct and complete.** No blocking issues. The single MINOR finding (FND-001: defensive list-normalization in `compute_planet_production`) is a code-clarity concern, not a correctness issue — the pattern is consistent with how other callers normalize `get_harvester_info` output. It can be addressed in a follow-up cleanup pass.

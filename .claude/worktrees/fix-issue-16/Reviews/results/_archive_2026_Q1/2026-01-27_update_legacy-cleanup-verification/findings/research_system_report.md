# Research System Scout Report

## Summary
- Files Reviewed: 11
- Issues Found: 10
- Critical: 0, Major: 0, Minor: 7, Info: 3

---

## Findings

### MINOR: Missing Type Hints in ResearchRenderer._draw_node_text
**ID:** NEW-RES-001
**Location:** `game/research/ui/research_renderer.py:199-200`
**Issue:** The `_draw_node_text` method has parameters `node` and `state` without type annotations, while other methods in the class have complete type hints.
**Impact:** Reduces IDE autocomplete, makes refactoring harder, inconsistent with codebase conventions.
**Recommendation:** Add type hints: `node: TechNode, state: NodeState`
**Effort:** Simple

---

### MINOR: Font Cache Unbounded Growth Risk
**ID:** NEW-RES-002
**Location:** `game/research/ui/research_renderer.py:59-63`
**Issue:** The `_font_cache` dictionary has no eviction policy. With variable zoom levels during pan/zoom operations, the cache could grow continuously.
**Impact:** Potential memory leak during extended gameplay. Camera zoom ranges from 0.15 to 2.0, generating fractional font sizes.
**Recommendation:** Use LRU cache with fixed size, or quantize font sizes to discrete steps.
**Effort:** Simple

---

### MINOR: Inconsistent Node State Reference in ResearchControlPanel
**ID:** NEW-RES-003
**Location:** `game/research/ui/research_controls.py:273-276`
**Issue:** The `handle_event` method uses `_selected_node` (internal state) but compares against `selected_node_id` (parameter). These can diverge.
**Impact:** Slider updates could apply RP to a different node than visually displayed.
**Recommendation:** Use consistent reference source; validate state synchronization.
**Effort:** Simple

---

### MINOR: Silent Failure in Unknown price_curve Types
**ID:** NEW-RES-004
**Location:** `game/research/data/tech_node.py:127-145`
**Issue:** The `get_effective_price` method silently defaults to flat pricing for unknown curve types instead of raising an error.
**Impact:** Invalid data from JSON goes undetected. Typos in `price_curve` values compute wrong prices.
**Recommendation:** Validate during node creation; log warning for unknown curve types.
**Effort:** Simple

---

### MINOR: No Cycle Detection Execution
**ID:** NEW-RES-005
**Location:** `game/research/ui/research_scene.py:68-71`
**Issue:** The scene only calls `validate_requirements()` but never calls `detect_cycles()`. The TechTree has cycle detection that goes unused.
**Impact:** Circular tech dependencies won't be detected at session start.
**Recommendation:** Add `detect_cycles()` call during validation.
**Effort:** Simple

---

### MINOR: Missing Input Validation for RP Allocation
**ID:** NEW-RES-006
**Location:** `game/research/data/research_tracker.py:109-130`
**Issue:** The `set_allocation` method accepts negative values and silently clamps them without indicating input was invalid.
**Impact:** Callers can't distinguish between success and auto-correction.
**Recommendation:** Document return value semantics; consider raising for invalid input.
**Effort:** Simple

---

### MINOR: Negate Logic Not Visible in UI
**ID:** NEW-RES-007
**Location:** `game/research/data/tech_node.py:21, 48-50`
**Issue:** `TechRequirement` supports `negate=True` for mutually exclusive tech paths, but this feature is not reflected in UI dependency lines or detail panel.
**Impact:** Negated requirements work silently without user visibility.
**Recommendation:** Add visual indicator for negated requirements in tech tree UI.
**Effort:** Medium

---

### INFO: Unused Import
**ID:** NEW-RES-008
**Location:** `game/research/data/tech_tree.py:10`
**Issue:** Module imports `log_error` from `game.core.logger` but it is never used.
**Impact:** Dead import; code cleanliness.
**Recommendation:** Remove unused import.
**Effort:** Simple

---

### INFO: Fragile State Assumption
**ID:** NEW-RES-009
**Location:** `game/research/ui/research_controls.py:368`
**Issue:** The `_update_allocation_slider_range` method assumes `_selected_node` is always in `tracker.node_states`. Safe due to `get_state` implementation but pattern is fragile.
**Impact:** Low; defensive programming opportunity.
**Recommendation:** Add explicit invariant check or document assumption.
**Effort:** Simple

---

### INFO: Parameter Type Documentation Gap
**ID:** NEW-RES-010
**Location:** `game/research/ui/research_renderer.py:200`
**Issue:** Method signature documents parameters but has no explicit types for `node` and `state`.
**Impact:** Makes code harder to understand; IDE cannot help with refactoring.
**Recommendation:** Add complete type annotations.
**Effort:** Simple

---

## Files Reviewed

### Data Layer (4 files)
1. `game/research/data/__init__.py`
2. `game/research/data/research_tracker.py`
3. `game/research/data/tech_node.py`
4. `game/research/data/tech_tree.py`

### UI Layer (5 files)
1. `game/research/ui/__init__.py`
2. `game/research/ui/research_camera.py`
3. `game/research/ui/research_controls.py`
4. `game/research/ui/research_renderer.py`
5. `game/research/ui/research_scene.py`

### Module Root (2 files)
1. `game/research/__init__.py`
2. `game/research/constants.py`

---

## Key Observations

1. **Type Hint Gaps** (NEW-RES-001, NEW-RES-010): The research module is mostly well-typed but has inconsistencies in the renderer methods.

2. **Validation Completeness** (NEW-RES-004, NEW-RES-005): The tech tree has comprehensive validation capabilities that aren't fully utilized.

3. **UI/Logic Coupling** (NEW-RES-003): State synchronization between control panel and tracker needs attention.

4. **Feature Visibility** (NEW-RES-007): The negate requirement feature exists but is invisible to users.

---

**Report Generated:** 2026-01-27
**Scout:** Research System Scout
**Coverage:** 11/11 files (100%)

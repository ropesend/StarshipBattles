# PROJ-410: Phase B API/Interface Design Review

**Reviewer:** Claude Code — API/Interface Reviewer (Phase B Swarm)
**Date:** 2026-05-10
**Scope:** Design surfaces for cache invalidation, lifecycle hooks, state resets.
**Status:** FINDINGS (NO IMPLEMENTATIONS)

---

## 1. VirtualTable.invalidate_widget_caches()

**Recommendation: CONFIRM the method name and signature.**

### Naming Rationale
- **Selected:** `invalidate_widget_caches()` — aligns with cache terminology in codebase.
- **Alternatives:** `mark_data_dirty()` (ambiguous), `reset_widget_state()` (vague), `clear_row_caches()` (incomplete).

### Signature
```python
def invalidate_widget_caches(self) -> None:
```

- **PEP 604 compliant:** No union types needed. ✓
- **Per docs/03_CONVENTIONS.md:** All public functions have return types. ✓

### Behavior & Idempotence
- **Observable behavior:**
  - `_last_text[*]` → `None` (virtual_table.py:297)
  - `_last_img[*]` → `None` (virtual_table.py:242)
  - `_last_color[*]` → `None` (virtual_table.py:306)
  - `_last_scroll_pct` → `-1.0` (sentinel, line 97)
  - `_last_row_count` → `-1` (sentinel, line 98)
- **Idempotence:** Yes. Calling twice is safe. ✓
- **Test hooks:** Tests can assert cache fields are None. ✓

### PROJ-373 Phase 3 Constraint Preservation
- **Does NOT call widget .kill():** ✓ Only nulls cache metadata.
- **Does NOT rebuild row pool:** ✓ Pool survives.
- **Test TestRowPoolReuseGuard passes:** ✓

---

## 2. VirtualTable: Data-Identity Dirty Bit (Internal)

**Recommendation: Add `_data_identity_dirty` flag.**

### Location
- **File:** `game/ui/components/table/virtual_table.py`
- **Add beside lines 97–98:**
  ```python
  self._data_identity_dirty: bool = True  # Force re-render on next update
  ```

### Guard Update (lines 318–323)
- **Add check:** `if (not self._data_identity_dirty and ...)`
- **Effect:** Data-identity takes precedence.
- **Clear on success:** After completion, set `_data_identity_dirty = False`.

### Public API Impact
- **None.** Internal detail (underscore-prefixed).

---

## 3. BuildQueueScreen.on_active_player_changed()

**Recommendation: Add turn-boundary lifecycle hook.**

### Signature
```python
def on_active_player_changed(self) -> None:
    """Clear widget state when active player changes at turn boundary."""
```

### Behavior
1. Call `_request_close()` to hide.
2. Call `self.panels.virtual_table.invalidate_widget_caches()`.
3. Reset `self.controller.active_queue_source = None`.
4. Reset `self.controller.selected_queue_sources = []`.
5. Reset `self.drag_handler.selected_design = None`.

### Naming Rationale
- **Pattern:** Matches `on_*_changed()` in codebase (e.g., `on_selection_changed`, `on_race_selected`).
- **Selected:** `on_active_player_changed()` — standard UI event pattern. ✓

---

## 4. BuildQueueController & BuildQueueDragHandler Resets

**Recommendation: Extend reset scope.**

### BuildQueueController (lines 108–110)
- **Issue:** `active_queue_source` and `selected_queue_sources` not reset.
- **Solution:** Reset in `open_for_yard()`:
  ```python
  self.controller.active_queue_source = None
  self.controller.selected_queue_sources = []
  ```
- **No new public API:** Already public attributes.

### BuildQueueDragHandler.selected_design (line 81)
- **Issue:** Not reset by `reset_state()` (lines 88–100).
- **Solution:** Add to `reset_state()`:
  ```python
  self.selected_design = None  # NEW
  ```
- **No new public API:** Extend existing method.

---

## 5. StrategySessionFacade Active-Player Event Design

### Current Facade Structure
- **File:** `game/strategy/facade/strategy_session_facade.py` (lines 80–99)
- **Pattern:** Composer over seven slices.
- **EventSlice:** Queries only. **No subscriptions today.**

### Three Options

#### Option A: Add to EventSlice (NOT RECOMMENDED)
- **Con:** Violates `EventSlice` cohesion (query-only).

#### Option B: Manager Polling (ACCEPTABLE for Phase B)
- **Where:** `strategy_build_queue_manager.py`
- **Pattern:** Poll facade; compare against cached player ID.
- **Pro:** No new facade surface.
- **Con:** Misses changes if screen not reopened.

#### Option C: Explicit Callback (RECOMMENDED for Phase C)
- **Add to EventSlice:**
  ```python
  def register_active_player_changed_callback(self, cb: Callable[[], None]) -> None:
      """Register callback when active player changes."""
      self._active_player_changed_callbacks.append(cb)
  ```
- **Calling site:** `TurnEngine.end_turn()` fires callbacks.
- **Pro:** Catch all changes; most robust.
- **Con:** Requires TurnEngine changes (Phase C).

### Phase B Recommendation
- **Design:** Plan for Option C (matches Pattern #5).
- **Implement:** Use Option B (manager polling) as workaround.
- **Phase C:** Add callback registration + firing.

### Facade Public API Impact
- **Current exports:** 15 symbols in `game/strategy/__init__.py`.
- **If Option C added:** Method on existing class; no new top-level export.
- **Impact:** Minimal. ✓

---

## 6. Compatibility & Exports

### game/ui/__init__.py
- **Current:** 7 eager imports.
- **New method:** Not a new export.
- **Impact:** None. ✓

### game/strategy/__init__.py
- **Current:** 15 symbols.
- **If Option C added:** No new top-level export.
- **Impact:** Minimal. ✓

---

## 7. Static Guards

### test_facade_bypass_guard.py (lines 1–81)
- **New methods:** No bypass vectors.
- **Impact:** No violations. ✓

### test_no_method_body_over_5_loc.py (lines 1–60)
- **New methods:** Not god classes; not in scope.
- **Impact:** None. ✓

---

## 8. Convention Checklist

### `VirtualTable.invalidate_widget_caches()`
- [x] Return-type annotated: `-> None`
- [x] PEP 604 syntax: Not applicable (no unions)
- [x] No broad `except Exception`: No try/except
- [x] Method on existing class (not new export)
- [x] Compliance: ✓

### `BuildQueueScreen.on_active_player_changed()`
- [x] Return-type annotated: `-> None`
- [x] PEP 604 syntax: Not applicable (no unions)
- [x] No broad `except Exception`: Facade-compliant
- [x] Method on existing class (not new export)
- [x] Compliance: ✓

---

## Final Recommendations

1. **Confirm name:** `invalidate_widget_caches()` — finalize and implement.
2. **Add dirty bit:** `_data_identity_dirty` + guard check — internal detail.
3. **Confirm hook name:** `on_active_player_changed()` — standard UI pattern.
4. **Extend resets:** Use existing attributes in `open_for_yard()` and `reset_state()`.
5. **Document facade callback:** Plan Option C (EventSlice callback) for Phase C.
6. **No new exports:** Unchanged.
7. **Compliance:** All static guards pass. ✓

---

**Report completed:** 2026-05-10
**Next:** Implementation phase (PROJ-410 Phase C).

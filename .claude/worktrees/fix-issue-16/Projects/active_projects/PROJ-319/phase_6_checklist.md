# Phase 6: Remediation — sort-key extraction (claimed-but-not-done)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-319 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Resolve the only finding from the OpenCode review that affects production code: the sort-key duplication in `planet_list_filters.py:221` and `star_list_filters.py:134`. Both files contain byte-identical `sort_key` inner functions that the manifest (lines 38-39) and `phase_4_checklist.md` Task 4.14 claim were absorbed by the DUP-X-03 / DUP-X-17 list-window refactor, but were not. This phase actually does the extraction.

---

## Tasks

### Task 6.1: Extract `make_attr_sort_key(col)` factory [Simple]
**File:** `game/ui/screens/list_filter_utils.py` (NEW), `game/ui/screens/planet_list_filters.py`, `game/ui/screens/star_list_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_planet_list_filters.py tests/unit/ui/screens/test_star_list_filters.py`
**Audit IDs:** OpenCode H3 (CONFIRMED real); also covers M5 and the implicit DUP-X-17 portion of `phase_4_checklist.md` Task 4.14 that was claimed but not done.

**Why a factory and not `ListDataSource._extract_value`:** the existing `ListDataSource._extract_value(entity, col)` returns a string for display rendering. The sort-key needs to return the typed underlying value (int, float, etc.) so `list.sort(key=...)` orders correctly. Same `func`/`attr` extraction logic but different return-type contract — must be a separate helper.

- [x] Create `game/ui/screens/list_filter_utils.py` with:
  ```python
  """Shared filter / sort utilities for VirtualTable list windows."""
  from __future__ import annotations
  from typing import Any, Callable, Dict


  def make_attr_sort_key(col: Dict[str, Any]) -> Callable[[Any], Any]:
      """Build a sort-key callable for a column with `func` or `attr` extraction.

      Used by `sort_planets` and `sort_stars` for the fallback (non-id, non-name,
      non-type) column sort path. Returns the typed underlying value, NOT a
      string — `ListDataSource._extract_value` exists separately for display.
      Falls back to `""` (empty string) when the attribute path doesn't resolve,
      matching the original inline behavior for stable ordering.
      """
      def _key(entity: Any) -> Any:
          if "func" in col:
              return col["func"](entity)
          if "attr" in col:
              attrs = col["attr"].split(".")
              obj: Any = entity
              for a in attrs:
                  if hasattr(obj, a):
                      obj = getattr(obj, a)
                  else:
                      return ""
              return obj
          return ""
      return _key
  ```
- [x] In `planet_list_filters.py:221`, replace the inline `def sort_key(p)` with `sort_key = make_attr_sort_key(col)` (and add the import at the top of the file).
- [x] In `star_list_filters.py:134`, do the same.
- [x] Run `pytest tests/unit/ui/screens/test_planet_list_filters.py tests/unit/ui/screens/test_star_list_filters.py` — confirm 0 failures.
- [x] Verify: `grep -n "def sort_key" game/ui/screens/planet_list_filters.py game/ui/screens/star_list_filters.py` returns 0 hits (the inner functions are gone).
- [x] Verify: LOC delta is roughly -22 net (-26 in the two filter files, +14 for the new module + 2 imports).

---

### Task 6.2: Manifest + Phase 4 checklist accuracy [Simple]
**File:** `Projects/active_projects/PROJ-319/manifest.md`, `Projects/active_projects/PROJ-319/phase_4_checklist.md`
**Tests:** None
**Audit IDs:** OpenCode H3 (records correctness)

- [x] In `manifest.md`, add `game/ui/screens/list_filter_utils.py` as Production (NEW), Phase 6 / DUP-X-17 / H3 remediation.
- [x] Update `manifest.md:38-39` (`planet_list_filters.py` and `star_list_filters.py` rows) to read e.g. "Phase 6 — adopt `make_attr_sort_key` factory from `list_filter_utils.py` (DUP-X-17)" rather than the previous claim that this was done in Task 4.14.
- [x] In `phase_4_checklist.md` Task 4.14, edit the "Share the sort-key utility..." sub-bullet to say "DEFERRED to Phase 6 (Task 6.1) — see `phase_6_checklist.md`. The original claim that this was absorbed by DUP-X-03 was incorrect; OpenCode review surfaced the gap."

---

### Task 6.3: Final sharded test suite [Simple]
**File:** None
**Tests:** `python Tools/test_sharded/test_sharded.py`
**Audit IDs:** None

- [x] Run `python Tools/test_sharded/test_sharded.py` once after Task 6.1.
- [x] Confirm: all tests pass except the two known flakes (`test_elapsed_seconds_is_monotonic_then_frozen` and the `test_mutual_join_rendezvous` test-ordering flake).
- [x] If a NEW failure appears: stop, do NOT mark Phase 6 complete, and investigate. The Phase 5 hygiene changes are pure additions / docs; the only behavior-affecting change in Phase 5+6 is the sort-key extraction (Task 6.1), which preserves byte-identical behavior.

---

## Phase Completion Checklist

When all tasks above are done:

- [x] All task checkboxes above are checked
- [x] `python Tools/test_sharded/test_sharded.py` passes (modulo known flakes)
- [x] `grep -n "def sort_key" game/ui/screens/planet_list_filters.py game/ui/screens/star_list_filters.py` returns no hits
- [x] manifest.md contains the new `list_filter_utils.py` row and the corrected sort-key claim on the two filter files
- [x] phase_4_checklist.md Task 4.14 sub-bullet updated to reflect deferral
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to `All phases complete; ready for project archive`

_Source review: `Reviews/results/2026-05-03_042208_code_proj-319-audit-shrink-cleanup-independent-review-o_req-req_20260503_042208_1f0252/report.md` (Finding H3)._

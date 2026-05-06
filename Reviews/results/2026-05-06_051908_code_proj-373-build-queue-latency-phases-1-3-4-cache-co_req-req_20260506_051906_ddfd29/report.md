# PROJ-373 Build Queue Latency Review — Phases 1, 3, 4 + Phase 2 Deferral Hygiene

**Review type:** code
**Request ID:** req_20260506_051906_ddfd29
**Review date:** 2026-05-06
**Scope:** 3 commits on `feat/03c-phase-aware-execution` (d68c39805, aca743a25, 8df0b40e2)
**Review mode:** normal (full review — not 03c lightweight)
**Files reviewed:** 11 (5 production + 3 test files + 3 doc files)
**Phase 2 explicitly out of scope:** No findings on absent code.

---

## CRIT

*No critical findings.*

---

## MAJ

### MAJ-001: Row-pool guard omits width from dimension check
- **File:** `game/ui/components/table/virtual_table.py:148-159`
- **Severity:** MAJ
- **Finding:** `_pool_dims_changed()` compares only `(panel_height, row_height)`. If the list-view panel width changes independently of height (e.g., window resize where the panel width narrows without proportional height change), the guard short-circuits and row-pool widgets retain stale widths — wrong-sized UIPanel backgrounds and cell layouts.
- **Suggested remediation:** Add `panel_rect.width` to the cached tuple:
  ```python
  current = (panel_rect.height, panel_rect.width, self._row_height)
  ```
- **Risk:** Medium — in practice, width changes almost always accompany height changes in a window resize. But the stated purpose of the guard is correctness across dimension changes, and omitting width is a correctness gap.

### MAJ-002: Column configuration changes undetected by pool guard
- **File:** `game/ui/components/table/virtual_table.py:168-169`
- **Severity:** MAJ
- **Finding:** The `_rebuild_row_pool` guard only considers `(panel_height, row_height)`. If `column_manager.get_visible_columns()` returns a different column set between calls (columns added, removed, or reordered), the guard short-circuits and the pool retains stale column widgets from the previous configuration. The public `rebuild_row_pool()` method exists for external callers to explicitly trigger a rebuild, and these callers could reasonably change column configuration between calls.
- **Suggested remediation:** Either (a) include a column-configuration fingerprint in the guard (e.g., `tuple(c["id"] for c in visible_cols)`), or (b) document on the public `rebuild_row_pool()` docstring that callers must set `_last_pool_dims = None` before calling when column configuration changes. Option (a) is preferred for robustness.
- **Risk:** Medium — today, no external caller invokes `rebuild_row_pool()` with changed columns (Phase 2 deferred). This becomes live when Phase 2 lands.

### MAJ-003: Phase 1 cache provides zero cross-open value without Phase 2
- **File:** `game/ui/panels/build_queue_controller.py:115`
- **Severity:** MAJ
- **Finding:** The cache lives on the `BuildQueueController` instance, which is reconstructed every time `BuildQueueScreen.__init__` runs (~6.9s per open). Without Phase 2 (instance reuse), the cache is destroyed on every close and provides zero savings on repeat opens. It only helps within a single open (inter-category switches). The design.md (lines 140-152) documents this correctly, but the plan.md Quick Status marks Phase 1 as "Complete" without noting this limitation. A reader of only plan.md would assume Phase 1 delivers its 2.2s savings on every repeat open today.
- **Suggested remediation:** Add a caveat to the plan.md Phase 1 row: "Effective only within a single open (inter-category toggles); full cross-open value gated by Phase 2." This aligns plan.md with design.md's explicit documentation of the same limitation.
- **Risk:** Low — documentation clarity issue; code behavior is correct per design.

### MAJ-004: Plan.md phase descriptions inconsistent with decisions.md deferral
- **File:** `Projects/active_projects/PROJ-373/plan.md:105-108`
- **Severity:** MAJ
- **Finding:** The Quick Status table (line 17) correctly shows Phase 2 as "Deferred (see decisions.md)". However, the detailed Phase 2 section (lines 105-108) reads:
  ```
  ### Phase 2: Reuse `BuildQueueScreen` instance across opens [Medium]
  **Status:** Not Started
  ```
  The objective text ("Construct `BuildQueueScreen` once per...") reads as if Phase 2 is still the current execution plan. A future agent reading only the detailed section could misinterpret Phase 2 as the active task.
- **Suggested remediation:** Update lines 105-108 to:
  ```
  ### Phase 2: Reuse `BuildQueueScreen` instance across opens [Medium]
  **Status:** Deferred — see decisions.md for rationale. Do not implement.
  ```
- **Risk:** Medium — agent misinterpretation risk. Decisions.md has the authoritative state, but plan.md is the entry point agents are instructed to read.

---

## MIN

### MIN-001: `reset_filters()` is intentional dead code awaiting Phase 2
- **File:** `game/ui/panels/build_queue_controller.py:260-268`
- **Severity:** MIN
- **Finding:** `reset_filters()` has zero production callers. It was written for Phase 2's `open_for_yard(yard)` path (design.md line 195), which was deferred. Two tests confirm it works correctly (`test_reset_filters_restores_defaults`, `test_reset_filters_does_not_fire_callback`), but it is unreachable dead code in the shipped product. The method is 9 lines and correctly resets category/role to defaults without firing `on_queue_changed`.
- **Suggested remediation:** Add a comment above the method: `# PROJ-373 Phase 2 prerequisite — called from BuildQueueScreen.open_for_yard when Phase 2 lands. Dead code until then.` This prevents deletion by shrinkage audits and documents intent for the follow-up project.
- **Risk:** Low — the method is small, tested, and has no side effects. The risk is future cleanup removing Phase 2's prerequisite before Phase 2 lands.

### MIN-002: macOS HFS+ mtime resolution edge case (documentation gap)
- **File:** `game/ui/panels/build_queue_controller.py:201-216`
- **Severity:** MIN
- **Finding:** The fingerprint uses `os.stat(path).st_mtime_ns`. On modern APFS/NTFS/ext4, nanosecond resolution is available. On legacy HFS+ volumes (still supported on older macOS installs), mtime has 1-second resolution. Two saves within the same second on HFS+ produce identical mtime → cache serves stale validation results. This is a known-accepted limitation per design.md alternatives section (option F: "false invalidations on equal-content rewrites are harmless"), but the code itself has no documentation of this edge case.
- **Suggested remediation:** Add a brief comment near line 213 noting the HFS+ 1s-resolution edge case and confirming the design decision to accept it.
- **Risk:** Very low — HFS+ is rare in practice, and the consequence (stale validation for one open) is minor and self-correcting on the next open.

### MIN-003: Row-pool build depends on UIManager layout pass completion
- **File:** `game/ui/components/table/virtual_table.py:157`
- **Severity:** MIN
- **Finding:** `_pool_dims_changed()` reads `self._list_view_panel.get_relative_rect()` which depends on pygame_gui having completed its layout pass. If `rebuild_row_pool()` is called before the UIManager processes pending layout, the rect could reflect stale dimensions, causing the guard to incorrectly skip or trigger a rebuild.
- **Suggested remediation:** Verify that all current and future callers of `rebuild_row_pool()` call it after `manager.update(0.0)` or equivalent layout pass. Document this requirement on the public `rebuild_row_pool()` docstring. This is already satisfied today (called from `__init__` after panel construction), but worth documenting for Phase 2 callers.
- **Risk:** Low — current callers are correct. Phase 2 callers need awareness.

### MIN-004: `@fast_panel` theme block omits `shape_corner_radius` without documentation
- **File:** `data/builder_theme.json:72-82`
- **Severity:** MIN
- **Finding:** The `panel.@fast_panel` block defines `shape: "rectangle"` and intentionally omits `shape_corner_radius` (irrelevant for rectangles). A future maintainer unfamiliar with the optimization motive might add `shape_corner_radius` to the block, which pygame_gui could interpret as an implicit shape change or cause an unexpected interaction.
- **Suggested remediation:** The test `test_theme_json_has_fast_panel_block_with_rectangle_shape` in `test_build_queue_panel_factory.py` asserts the shape is `"rectangle"`, which catches accidental shape changes. Add a comment near the theme block explaining the optimization rationale.
- **Risk:** Very low — the unit test catches regressions.

### MIN-005: Missing test for column-count change without dimension change
- **File:** `tests/unit/ui/components/table/test_virtual_table.py` (TestRowPoolReuseGuard)
- **Severity:** MIN
- **Finding:** The 4 Phase 3 guard tests cover dim-change, no-change, row-height-change, and force-update. Missing: column configuration change without dimension change. If `column_manager.get_visible_columns()` returns different columns but panel height+width are unchanged, the guard short-circuits and pool has wrong column widgets. This is the scenario identified in MAJ-002.
- **Suggested remediation:** Add a test in `TestRowPoolReuseGuard` that mutates `column_manager.get_visible_columns()` return value between two `rebuild_row_pool()` calls and asserts the pool was rebuilt (old bg's `.kill()` was called). Currently this test would FAIL, confirming MAJ-002.
- **Risk:** Low — validates the MAJ-002 finding.

---

## INFO

### INFO-001: Phase 4 visual regression verification is manual-only
- **Finding:** The plan's Next Action says "User-driven manual verification... eyeball-check that panels look acceptable with rectangle (vs rounded) corners." There is no automated visual regression test for the shape change. This is acceptable — visual appearance verification at this level is inherently manual. The automated tests confirm JSON structure and factory wiring.
- **Files referenced:** `plan.md:25`, `test_build_queue_panel_factory.py:119-223`

### INFO-002: Phase 2 deferral note is comprehensive for follow-up
- **Finding:** The decisions.md deferral entry (line 22) documents: what Phase 2 does, why it's risky, which specific objects need rewiring (PlanetReportPanel, BuildQueueSelector, BuildQueueQueueDataSource, BuildQueueRenderer, controller, drag_handler), pygame_gui modal-stack concerns, focus management, and FEAT-17 pause-button label state. A follow-up project has sufficient context to estimate effort and plan implementation.
- **Files referenced:** `decisions.md:22`

### INFO-003: Phase 3 ~1.5s savings claim is quantitatively defensible
- **Finding:** The profile summary at `findings/profile_summary.md:42-43` shows `_rebuild_row_pool` at 1.5s/click as a leaf under `VirtualTable.__init__`. The guard design correctly prevents this work on subsequent calls where dimensions are unchanged. The claim that the guard "pays off ~1.5s/click once Phase 2 lands later" is traceable to profile evidence and the guard's logic. Note: without Phase 2, the guard provides zero savings today because the entire VirtualTable is destroyed and reconstructed on every open.
- **Files referenced:** `findings/profile_summary.md:42-43`, `virtual_table.py:168-169`

### INFO-004: All 7 BuildQueuePanelFactory UIPanels carry @fast_panel
- **Finding:** Every `ui.UIPanel(...)` construction in `BuildQueuePanelFactory` passes `object_id="@fast_panel"`. The 7 panels are: background (line 200), fleet-info (line 247), items-list (line 325), build-queue outer (line 367), table sub-panel (line 386), filter (line 448), bottom-bar (line 529). No UIPanel is missed. The AST-style test `test_every_uipanel_in_factory_uses_fast_panel_class_id` programmatically verifies this invariant.
- **Files referenced:** `build_queue_panel_factory.py:200-533`, `test_build_queue_panel_factory.py:159-195`

### INFO-005: Theme block correctly inherits parent colors
- **Finding:** The `panel.@fast_panel` block duplicates the parent `panel` block's colors (`dark_bg`, `normal_bg`, `normal_border`) identically and only changes `shape` from `rounded_rectangle` to `rectangle`. pygame_gui's theme inheritance would resolve unset properties from the parent `panel` block, so the color duplication is defensive but correct. No visual regression expected beyond the corner shape.
- **Files referenced:** `builder_theme.json:60-82`

### INFO-006: Phase 3 guard does not affect VirtualTable rows during Phase 4
- **Finding:** The 7 `@fast_panel` UIPanels cover the main container panels. However, the `_rebuild_row_pool` method at `virtual_table.py:197-201` creates UIPanel row backgrounds WITHOUT `object_id="@fast_panel"`. These row backgrounds still get rounded-rectangle rasterization (~1.5s of the 4.4s panel-construction cost in the profile). Since Phase 4 was scoped to the factory's UIPanels (not the general-purpose VirtualTable component), this is by design. Adding `@fast_panel` to VirtualTable rows would affect all tables in the game, not just the build queue — a follow-up optimization opportunity.
- **Files referenced:** `virtual_table.py:197-201`, `build_queue_panel_factory.py:386-393`

### INFO-007: Cross-phase interactions are correctly isolated
- **Finding:** Phase 1 (controller cache), Phase 3 (VirtualTable guard), and Phase 4 (theme) operate on different objects with no shared mutable state. They compose correctly — each delivers independent value and their combined effect is additive. After Phase 2 lands, the controller cache and VirtualTable guard both survive across opens and compound.
- **Files referenced:** N/A — structural observation

### INFO-008: Acceptance criterion not met without Phase 2
- **Finding:** The plan's acceptance criterion is `< 0.5s repeat-open wall-clock`. Baseline is ~6.9s. Phase 1 saves 2.2s (within single open only), Phase 3 saves 0s today (guard never triggers), Phase 4 saves ~3s on first open (shape rasterization). A repeat open today still pays ~4.7s (cache destroyed on close) — well above 0.5s. The plan and decisions correctly acknowledge this: Phase 2 is the gate for the acceptance criterion.
- **Files referenced:** `plan.md:47`, `decisions.md:22`

---

## Verification Summary

| Focus Area | Status |
|---|---|
| Phase 1 cache correctness | **Pass** — mtime fingerprint correct, lazy validator zero-cost on hits, exception path doesn't poison cache, 13 tests cover invalidation. `reset_filters()` dead code awaiting Phase 2 (MIN-001). |
| Phase 3 row-pool rebuild guard | **Pass with findings** — Guard logic correct for height/row-height changes. Width omission (MAJ-001) and column-config blindness (MAJ-002) are correctness gaps. Tests cover the 4 stated cases. |
| Phase 4 scoped @fast_panel | **Pass** — All 7 UIPanels covered, theme block correctly inherits colors, test validates invariants. Theme change is well-scoped. |
| Cross-cutting interactions | **Pass** — Phases operate on independent objects, no coordination issues. Acceptance criterion not met without Phase 2 (INFO-008). |
| Phase 2 deferral hygiene | **Pass with finding** — Deferral note is comprehensive (INFO-002). Plan.md detail section inconsistent with Quick Status (MAJ-004). |

## Remediation Priority

1. **Fix MAJ-001** and **MAJ-002** together: broaden `_pool_dims_changed()` to include width and column-config fingerprint. One-line change for MAJ-001; MAJ-002 needs column-ID hashing or a manual invalidation path.
2. **Fix MAJ-004**: update plan.md Phase 2 detailed status from "Not Started" to "Deferred".
3. **Fix MAJ-003**: add caveat to plan.md Phase 1 row about cross-open value gating.
4. **Address MIN items** at author's discretion — all are documentation or test-coverage improvements with low risk.

---

*Generated by OpenCode via ocode-review-request skill. Findings verified against source code at lines cited. No agents required — direct analysis of all 11 files in scope.*

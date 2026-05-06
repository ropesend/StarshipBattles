# PROJ-373 — Independent Verification of OpenCode Review

**Verifier:** Claude (independent pass over OpenCode's findings)
**Source report:** `report.md` (same dir)
**Date:** 2026-05-06
**Verdict policy:** read every cited line; flag CONFIRM / CONFIRM_REMEDIATION_REVISE / REJECT / UNCERTAIN.

---

## Verdicts table

| ID | Severity | Verdict | One-line rationale |
|---|---|---|---|
| MAJ-001 | MAJ | **CONFIRM** | Cache key is `(panel_height, row_height)` — width is genuinely absent (line 158, line 189). |
| MAJ-002 | MAJ | **CONFIRM_REMEDIATION_REVISE** | Bigger than reported — column-config blindness is a **live bug TODAY**, not a Phase-2-gated risk. |
| MAJ-003 | MAJ | **CONFIRM** | plan.md row 17 marks Phase 1 "Complete" with no caveat; design.md 137-150 documents the limitation. |
| MAJ-004 | MAJ | **CONFIRM** | plan.md line 107 still reads `**Status:** Not Started` while line 17 says "Deferred". Real inconsistency. |
| MIN-001 | MIN | **CONFIRM** | Zero callers of `reset_filters()` in `game/`; only the two unit tests reference it. Genuinely dead until Phase 2. |
| MIN-002 | MIN | **CONFIRM** | Code uses `st_mtime_ns` and design.md "Cache key" section line 130-133 explicitly accepts the trade-off. |
| MIN-003 | MIN | **CONFIRM** | `_pool_dims_changed` reads `get_relative_rect()` at line 157; layout-pass dependency is real. |
| MIN-004 | MIN | **CONFIRM** | Theme block at lines 72-82 omits `shape_corner_radius`; the rectangle test catches shape regressions but not radius drift. |
| MIN-005 | MIN | **CONFIRM** | `TestRowPoolReuseGuard` covers 4 cases — no column-set-mutation case. Adding one would fail today (validates MAJ-002). |
| INFO-001 | INFO | CONFIRM | Manual-only visual verification is acceptable at this scope. |
| INFO-002 | INFO | CONFIRM | decisions.md entry for Phase 2 deferral is comprehensive. |
| INFO-003 | INFO | CONFIRM | 1.5s figure traces to profile_summary.md. |
| INFO-004 | INFO | CONFIRM | 7 `@fast_panel` UIPanels claimed; AST test enforces invariant. |
| INFO-005 | INFO | CONFIRM | Theme inheritance via duplicated colors is defensive but correct. |
| INFO-006 | INFO | CONFIRM | VirtualTable row backgrounds (line 197) lack `@fast_panel` — by-design follow-up. |
| INFO-007 | INFO | CONFIRM | Phases 1/3/4 act on disjoint state; additive composition. |
| INFO-008 | INFO | CONFIRM | Acceptance criterion (<0.5s) is gated on Phase 2 per profile arithmetic. |

**Counts:** CONFIRM ×16, CONFIRM_REMEDIATION_REVISE ×1, REJECT ×0, UNCERTAIN ×0.

---

## MAJ details

### MAJ-001 — width omitted from pool guard — **CONFIRM**

Evidence read: `virtual_table.py:148-159, 186-189`.

```python
current = (panel_rect.height, self._row_height)            # line 158
self._last_pool_dims = (panel_rect.height, self._row_height)  # line 189
```

Width is the inner dimension that determines `row_bg.width = panel_rect.width` (line 198) and the per-cell layout `x` accumulator (line 280). A width-only resize will silently keep stale-width row backgrounds. Window snapping / sidebar resize / panel-aware reflow all do this. OpenCode's recommended remediation (add `panel_rect.width` to the tuple) is correct and one line.

### MAJ-002 — column-config blindness — **CONFIRM_REMEDIATION_REVISE**

Evidence read: `virtual_table.py:191-280`, `column_manager.py:66-115`, plus call sites in `data_list_window_mixin.py:43-50`, `data_list_window_mixin.py:113-115`, `event_log_window.py:352-392`, `fleet_report_window.py:211-415`, `empire_build_queue_window.py:455, 510-512`.

**OpenCode underrated this.** The report says "today, no external caller invokes `rebuild_row_pool()` with changed columns (Phase 2 deferred). This becomes live when Phase 2 lands." That is wrong. There are **at least 6 production sites** that already do exactly this:

```
data_list_window_mixin._toggle_column        → toggle_column() then rebuild_row_pool()
data_list_window_mixin._run_update_template  → swap_column() then rebuild_row_pool()
event_log_window (header swap path)          → swap_column() then rebuild_row_pool()
event_log_window (toggle path)               → toggle_column() then rebuild_row_pool()
fleet_report_window (swap)                   → swap_column() then rebuild_row_pool()
fleet_report_window (toggle)                 → toggle_column() then rebuild_row_pool()
empire_build_queue_window (swap, toggle)     → swap_column() then rebuild_row_pool()
```

`toggle_column` mutates `col["visible"]` in place; `swap_column` reorders `self._columns`. Both change `get_visible_columns()` output without changing `_list_view_panel.height` or `_row_height`. Phase 3's guard makes those rebuilds **no-ops today** — meaning user-visible column show/hide and reorder are now broken across PlanetList, StarList, EventLog, FleetReport, and Empire Build Queue windows whenever they share the VirtualTable + this guard.

This is a **live regression** introduced by Phase 3, not a hypothetical Phase-2-only risk.

**Revised remediation:** Option (a) — fingerprint the visible-column tuple — is mandatory, not preferred. Concretely:

```python
def _pool_dims_changed(self) -> bool:
    panel_rect = self._list_view_panel.get_relative_rect()
    visible_cols = self._column_manager.get_visible_columns()
    col_fp = tuple((c["id"], c.get("width", 100)) for c in visible_cols)
    current = (panel_rect.height, panel_rect.width, self._row_height, col_fp)
    return self._last_pool_dims != current
```

(width is from MAJ-001; column id+width tuple covers both visibility toggle and reorder + width-driven layout drift.) Update the cache write at line 189 to match.

### MAJ-003 — plan.md missing Phase-1 cross-open caveat — **CONFIRM**

plan.md row 17 ("`1. Cache _validate_designs results | Complete | …`") shows no caveat. design.md lines 135-150 explicitly documents that the cache lives one open without Phase 2. A reader of plan.md alone would assume Phase 1 saves 2.2s on every repeat open. Real reader-confusion risk; cheap one-line fix.

### MAJ-004 — Phase 2 detail still reads "Not Started" — **CONFIRM**

plan.md line 107: `**Status:** Not Started`. Quick Status table line 17 says "Deferred (see decisions.md)". The two are inconsistent. OpenCode's exact wording fix is correct.

---

## MIN details

### MIN-001 — `reset_filters()` dead code — CONFIRM
`grep` across `game/`: zero callers. Only test references. The method is intentional Phase 2 prerequisite. A `# PROJ-373 Phase 2 prerequisite` comment is the right shape (do NOT delete).

### MIN-002 — HFS+ mtime resolution — CONFIRM
`build_queue_controller.py:213` uses `st_mtime_ns`; nanoseconds aren't actually delivered on HFS+. design.md alternatives section explicitly accepts the trade-off. Inline comment is a doc nicety, not a correctness fix.

### MIN-003 — layout-pass dependency — CONFIRM
The rect read at line 157 returns whatever pygame_gui has computed; current callers (`__init__` after panel construction; column-toggle paths after the table has lived through prior frames) are safe. Phase 2 callers will need the discipline.

### MIN-004 — `@fast_panel` block omits `shape_corner_radius` — CONFIRM
Confirmed at `builder_theme.json:72-82`. Rectangles ignore radius so the omission is correct. The unit test asserts `shape == "rectangle"`, so an accidental shape change would fail; an accidental added radius would not. Comment-only improvement.

### MIN-005 — missing column-mutation test — CONFIRM
`TestRowPoolReuseGuard` covers (no-change, height-change, row-height-change, force-update). **No** column-toggle test. Adding one as OpenCode describes — mutate `_columns[0]["visible"] = False` between calls, assert `bg.kill.called` — would fail against today's guard, validating MAJ-002.

---

## INFO sanity check

INFO-001 through INFO-008 all hold up against the cited evidence. INFO-006 in particular flags a real follow-up opportunity (VirtualTable row-bg panels lack `@fast_panel` — they are constructed at line 197 without `object_id`).

---

## Recommended actions for Claude

**Fix now (Phase 3 hardening; one focused commit):**

1. **MAJ-001 + MAJ-002 together** — single-line guard expansion. Cache key becomes `(panel_height, panel_width, row_height, ((col_id, col_width), …))`. This closes both findings and is mandatory because MAJ-002 is a live regression in 5+ existing windows.
2. **MIN-005** — add the column-mutation test in `TestRowPoolReuseGuard` simultaneously. Drives the fix in step 1 via TDD.
3. **MAJ-004** — flip plan.md line 107 from "Not Started" to "Deferred — see decisions.md for rationale. Do not implement."
4. **MAJ-003** — append the cross-open caveat to plan.md row 17.

**Defer (low-value, low-risk):**

- MIN-001 (comment on `reset_filters()`) — fine to do alongside (1) but not urgent.
- MIN-002 (HFS+ comment), MIN-003 (layout-pass docstring), MIN-004 (theme-block comment) — author's discretion; none gate correctness.

**Reject:** none.

**Scope estimate (LLM time):** the Phase-3 guard fix + new test + 2 plan.md edits are minutes, not "next pass." Bundle them in one commit titled `fix(virtual_table): include width + visible-column fingerprint in row-pool guard (PROJ-373 Phase 3 hardening)`.

# PROJ-62: Planet List Window Breakdown

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-62` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-62 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Extract Sidebar Builder | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Data Helpers & Column Manager | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Extract Virtual Row Renderer | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Simplify Main Window & Final Cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-07
**Active Phase:** Phase 4
**Last Action:** Phase 3 complete - extracted VirtualListRenderer to planet_list_renderer.py
**Next Action:** Start Phase 4 - Simplify Main Window & Final Cleanup
**Blockers:** None
**Test Baseline:** 6244 passed

## Overview
Break down `planet_list_window.py` from **1136 lines** to **under 500 lines** by extracting cohesive subsystems into dedicated modules. The file already has `planet_list_filters.py` and `planet_list_presets.py` extracted. This project continues by extracting the sidebar builder, column manager, and virtual row renderer.

## Goals
- Reduce `planet_list_window.py` to ~450-490 lines (coordinating facade)
- Extract 3 new focused modules with clear responsibilities
- Maintain identical runtime behavior (zero regressions)

## Scope
**In:**
- Extract sidebar UI construction to `planet_list_sidebar.py`
- Move data accessors and range computation into `planet_list_filters.py`
- Extract column management to `planet_list_columns.py`
- Extract virtual row pool/renderer to `planet_list_renderer.py`
- Simplify `update()` via delegation

**Out:**
- Adding new features or changing UI behavior
- Writing comprehensive new test suites
- Modifying `planet_list_presets.py` or `planet_report_panel.py`

## Key Files
| Component | File Path | Lines |
|-----------|-----------|-------|
| Main window (TARGET) | `game/ui/screens/planet_list_window.py` | 1136 |
| Filters (extracted) | `game/ui/screens/planet_list_filters.py` | 173 |
| Presets (extracted) | `game/ui/screens/planet_list_presets.py` | 183 |
| Detail panel (extracted) | `game/ui/panels/planet_report_panel.py` | 269 |
| Strategy UI (caller) | `game/ui/screens/strategy_ui.py` | line 17 |

## Line Budget
| Extraction | Lines Out | Destination |
|------------|-----------|-------------|
| `_init_sidebar()` | ~212 | `planet_list_sidebar.py` (new) |
| `_compute_planet_ranges()` + accessors | ~85 | `planet_list_filters.py` |
| `_rebuild_headers()`, `_swap_columns()` | ~90 | `planet_list_columns.py` (new) |
| `_rebuild_row_pool()`, `_update_visible_rows()` | ~150 | `planet_list_renderer.py` (new) |
| `update()` simplification | ~80 | Delegation |
| **Total removed** | **~617** | |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-06 | Sidebar: function not class | Pure UI construction, no ongoing state |
| 2026-02-06 | Data accessors into existing filters module | Pure formatting; consolidates |
| 2026-02-06 | Column manager: `ColumnManager` class | Owns column order + sort state |
| 2026-02-06 | Virtual renderer: `VirtualListRenderer` class | Owns row pool, icon cache, scroll |
| 2026-02-06 | Keep `process_event()`/`update()` in main | Coordination logic; extracting adds indirection |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

---

## Phases

### Phase 1: Extract Sidebar Builder [Medium]
**Objective:** Extract the 212-line `_init_sidebar()` into `planet_list_sidebar.py`

See [phase_1_checklist.md](phase_1_checklist.md).

### Phase 2: Extract Data Helpers & Column Manager [Medium]
**Objective:** Move data accessors to filters; create `ColumnManager` in `planet_list_columns.py`

See [phase_2_checklist.md](phase_2_checklist.md).

### Phase 3: Extract Virtual Row Renderer [Medium]
**Objective:** Create `VirtualListRenderer` in `planet_list_renderer.py`

See [phase_3_checklist.md](phase_3_checklist.md).

### Phase 4: Simplify Main Window & Final Cleanup [Simple]
**Objective:** Simplify `update()`, remove dead code, verify <500 lines

See [phase_4_checklist.md](phase_4_checklist.md).

---

## Verification Checklist
### Project Start
- [x] Full test suite: 6248 passed (baseline)

### After Each Phase
- [ ] `pytest tests/` - all tests pass
- [ ] Manual test: planet list opens, filters/sort/scroll/select/presets work

### Final
- [ ] `planet_list_window.py` under 500 lines
- [ ] Full test suite: 6248+ passed

---

## Completion Checklist
- [ ] Phase 1 complete
- [ ] Phase 2 complete
- [ ] Phase 3 complete
- [ ] Phase 4 complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified

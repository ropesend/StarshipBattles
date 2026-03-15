# PROJ-221: Build Queue Configurable Columns & Column Swap Fix

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-221` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-221 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Fix Column Swap Bug | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Per-Turn Spend Calculation | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Build Queue Data Source & Column Defs | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. VirtualTable Integration | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Drag Handler Adaptation | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Verification & Cleanup | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-03-14 22:30
**Active Phase:** Planning
**Last Action:** Swarm review complete, plan drafted
**Next Action:** User approval of plan
**Blockers:** None
**Context for Next Agent:** Plan ready for implementation. See design.md for architecture analysis and decisions.md for all decisions.

## Overview
Replace the per-planet BuildQueueScreen's hardcoded column layout with the shared `TableColumnManager` + `VirtualTable` system used by PlanetListWindow, EmpireBuildQueueWindow, and other windows. Add per-turn spend columns and a build order column. Fix the column swap bug in EmpireBuildQueueWindow.

## Goals
- Replace hardcoded build queue columns with configurable `TableColumnManager` + `VirtualTable`
- Add per-turn spend resource columns (proportional to limiting resource)
- Add remaining cost resource columns
- Add build order position column (#1, #2, #3)
- Fix column swap (reorder arrows) bug in EmpireBuildQueueWindow
- Supersede BUG-96 (incorrect resource display)

## Scope
**In:**
- Per-planet BuildQueueScreen column rework (VirtualTable integration)
- Per-turn spend calculation utility
- Build order column
- Column swap fix in EmpireBuildQueueWindow
- Adapting DragHandler to work with VirtualTable
- New BuildQueueDataSource (ITableDataSource implementation)
- Test updates for changed components

**Out:**
- Converting BuildQueueScreen from full-screen to windowed panel
- Column visibility sidebar/toggles (columns are always visible — can be added later)
- Persisting column configuration between sessions
- Integrating BuildQueueViewModel (exists but out of scope)
- Changes to EmpireBuildQueueWindow column definitions
- Changes to EventLogWindow or PlanetListWindow

## Key Files
| Component | File Path |
|-----------|-----------|
| BuildQueueScreen | `game/ui/screens/build_queue_screen.py` |
| BuildQueueRenderer | `game/ui/screens/build_queue_renderer.py` |
| BuildQueuePanelFactory | `game/ui/screens/build_queue_panel_factory.py` |
| BuildQueueDragHandler | `game/ui/panels/build_queue_drag_handler.py` |
| BuildQueueController | `game/ui/panels/build_queue_controller.py` |
| BuildQueuePortraitLoader | `game/ui/panels/build_queue_portraits.py` |
| BuildQueueHelpers | `game/ui/screens/build_queue_helpers.py` |
| BuildQueueSource | `game/strategy/data/build_queue_source.py` |
| EmpireBuildQueueWindow | `game/ui/screens/empire_build_queue_window.py` |
| EmpireBuildQueueFormatter | `game/ui/screens/empire_build_queue_formatter.py` |
| TableColumnManager | `game/ui/components/table/column_manager.py` |
| VirtualTable | `game/ui/components/table/virtual_table.py` |
| TableHeader | `game/ui/components/table/header.py` |
| ITableDataSource | `game/ui/components/table/data_source.py` |
| Selection strategies | `game/ui/components/table/selection.py` |
| Triage findings | `findings/build_queue_configurable_columns.md` |
| NEW: BuildQueueDataSource | `game/ui/screens/build_queue_queue_data_source.py` |
| NEW: per-turn spend utility | `game/ui/screens/build_queue_helpers.py` (extend) |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/build_queue_configurable_columns.md](findings/build_queue_configurable_columns.md) - Original triage

---

## Phases

### Phase 1: Fix Column Swap Bug [Simple]
**Objective:** Fix the column reordering arrows in EmpireBuildQueueWindow
**Status:** Not Started

See [phase_1_checklist.md](phase_1_checklist.md) for tasks.

### Phase 2: Per-Turn Spend Calculation [Medium]
**Objective:** Add utility function to calculate proportional per-turn resource spend
**Status:** Not Started

See [phase_2_checklist.md](phase_2_checklist.md) for tasks.

### Phase 3: Build Queue Data Source & Column Definitions [Medium]
**Objective:** Create ITableDataSource implementation and column definitions for per-planet build queue
**Status:** Not Started

See [phase_3_checklist.md](phase_3_checklist.md) for tasks.

### Phase 4: VirtualTable Integration [Complex]
**Objective:** Replace hardcoded queue display with VirtualTable in BuildQueueScreen
**Status:** Not Started

See [phase_4_checklist.md](phase_4_checklist.md) for tasks.

### Phase 5: Drag Handler Adaptation [Medium]
**Objective:** Refactor DragHandler to work with VirtualTable row indices instead of UIPanel references
**Status:** Not Started

See [phase_5_checklist.md](phase_5_checklist.md) for tasks.

### Phase 6: Verification & Cleanup [Simple]
**Objective:** Full verification, dead code removal, test suite pass
**Status:** Not Started

See [phase_6_checklist.md](phase_6_checklist.md) for tasks.

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS)
- [x] Run full test suite: `pytest tests/` - all tests pass (baseline: 13180 passed, 2 skipped)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] Manual test: open build queue from strategy screen - no crashes

### Final Verification
- [ ] Open per-planet build queue: all columns display correctly
- [ ] Column headers show: #, Item, Turns, Met/t, Org/t, Vap/t, Rad/t, Exo/t, Met, Org, Vap, Rad, Exo
- [ ] Per-turn spend values are proportionally correct (limiting resource = full rate)
- [ ] Remaining cost values match total_cost - resources_consumed
- [ ] Build order shows sequential numbers (#1, #2, #3...)
- [ ] Drag-to-reorder still works in build queue
- [ ] Column reordering arrows work in EmpireBuildQueueWindow
- [ ] Run full test suite: `pytest tests/ -n 12` (NOT --testmon, full verification)
- [ ] Verify changes are consistent with `docs/` — update docs if architecture/patterns changed

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All Phase 5 tasks checked off
- [ ] All Phase 6 tasks checked off
- [ ] All tests passing (13180+ passed)
- [ ] Audit passed (no significant issues)
- [ ] User verified

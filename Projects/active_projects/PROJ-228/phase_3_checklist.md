# PROJ-228 Phase 3: Sidebar & Column Toggle

## DUP-SCR-001: Sidebar Pattern
- [ ] Analyze sidebar rendering across:
  - `game/ui/screens/fleet_report_sidebar.py`
  - `game/ui/screens/event_log_sidebar.py`
  - `game/ui/screens/empire_build_queue_sidebar.py`
  - `game/ui/screens/planet_list_sidebar.py`
- [ ] Identify shared layout, event routing, and rendering code
- [ ] Design `SidebarPanel` or `SidebarMixin` base
- [ ] Write tests for shared sidebar abstraction
- [ ] Implement and migrate sidebars
- [ ] Verify sidebar functionality in all windows

## DUP-PAT-004: Column Toggle
- [ ] Analyze column visibility toggle in `game/ui/components/table/column_manager.py`
- [ ] Identify duplicate toggle logic in consuming widgets
- [ ] Consolidate toggle into ColumnManager
- [ ] Update consuming windows:
  - `game/ui/screens/fleet_report_window.py`
  - `game/ui/screens/event_log_window.py`
  - `game/ui/screens/empire_build_queue_window.py`
  - `game/ui/screens/planet_list_window.py`
- [ ] Verify column toggle tests pass

## DUP-SCR-015: Filter Manager Pattern
- [ ] Analyze filter manager patterns across:
  - `game/ui/screens/empire_build_queue_filter_manager.py`
  - `game/ui/components/filters/tri_state_widget.py`
  - `game/ui/screens/fleet_report_view_model.py`
- [ ] Extract common filter manager base if applicable
- [ ] Verify filter functionality

## Completion
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] All Phase 3 items verified

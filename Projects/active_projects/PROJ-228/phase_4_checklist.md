# PROJ-228 Phase 4: VirtualTable & Data Source

## DUP-SCR-002: VirtualTable Configuration
- [ ] Analyze VirtualTable setup patterns across consuming windows
- [ ] Identify duplicated configuration boilerplate
- [ ] Extract configuration helpers or builder pattern if applicable
- [ ] Update `game/ui/components/table/virtual_table.py`
- [ ] Verify table tests pass

## DUP-SCR-007: Data Source Base Pattern
- [ ] Analyze shared patterns across data sources:
  - `game/ui/screens/planet_data_source.py`
  - `game/ui/screens/fleet_data_source.py`
  - `game/ui/screens/event_log_data_source.py`
  - `game/ui/screens/empire_build_queue_data_source.py`
  - `game/ui/screens/build_queue_queue_data_source.py`
- [ ] Identify common sorting, filtering, caching logic
- [ ] Enhance `game/ui/components/table/data_source.py` base class
- [ ] Migrate data sources to use enhanced base
- [ ] Verify all data source tests pass

## DUP-SCR-011: Column Definition Patterns
- [ ] Identify duplicated column definition code across data sources and windows
- [ ] Consolidate column definition into shared utilities
- [ ] Update consuming files
- [ ] Verify column rendering tests pass

## DUP-SCR-013: Table Rendering
- [ ] Identify duplicated table rendering logic
- [ ] Consolidate into `game/ui/screens/build_queue_renderer.py` or shared renderer
- [ ] Update consuming files
- [ ] Verify rendering tests pass

## Completion
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] All Phase 4 items verified

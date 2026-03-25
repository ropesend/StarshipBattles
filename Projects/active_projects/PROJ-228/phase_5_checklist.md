# PROJ-228 Phase 5: Panel & Interface Patterns

## DUP-PAT-003: DrawablePanel
- [ ] Analyze common panel lifecycle across test_lab panels:
  - `game/ui/screens/test_lab/ship_panels.py`
  - `game/ui/screens/test_lab/results_panel.py`
  - `game/ui/screens/test_lab/panel_manager.py`
  - `game/ui/screens/test_lab/test_run_details.py`
- [ ] Identify shared `draw()`, `handle_event()`, `resize()` patterns
- [ ] Design `DrawablePanel` base class
- [ ] Write tests for DrawablePanel
- [ ] Implement DrawablePanel
- [ ] Migrate test_lab panels to use DrawablePanel
- [ ] Evaluate migration of `game/ui/screens/builder/detail_panel.py`
- [ ] Verify all panel tests pass

## DUP-PAT-008/009/010: Interface Patterns
- [ ] Identify duplicated interface/protocol definitions across UI modules
- [ ] Consolidate into `game/core/protocols.py` or appropriate module
- [ ] Update all implementors
- [ ] Verify protocol tests pass

## Completion
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] All Phase 5 items verified

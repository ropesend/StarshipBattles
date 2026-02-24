# Phase 4: Final Verification

## Task 4.1: Full test suite run
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite
- [ ] Verify same pass count as baseline
- [ ] Verify no new warnings related to UI panels or section headers

**Notes:**

## Task 4.2: Verify duplication eliminated
- [ ] Run: `grep -rn 'object_id="#section_header"' game/ui/` — should only return `game/ui/utils.py`
- [ ] Verify `create_section_header` is imported in all 8 migrated files:
  - [ ] `game/ui/panels/race_identity_panel.py`
  - [ ] `game/ui/panels/race_environment_panel.py`
  - [ ] `game/ui/panels/race_aptitudes_panel.py`
  - [ ] `game/ui/panels/race_description_panel.py`
  - [ ] `game/ui/panels/race_summary_panel.py`
  - [ ] `game/ui/screens/empire_panel_window.py`
  - [ ] `game/ui/panels/empire_treasury_panel.py`
- [ ] Verify no remaining inline `#section_header` UILabel constructions

**Notes:**

## Phase 4 Completion
- [ ] Full test suite passes with same count as baseline
- [ ] Grep confirms single source of `#section_header` in `utils.py`
- [ ] All 8 files import from `game.ui.utils`
- [ ] All 24 original inline sites have been replaced

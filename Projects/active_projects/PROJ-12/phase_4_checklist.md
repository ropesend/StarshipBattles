# PROJ-12 Phase 4: RaceSetupScreen Components

## Phase Overview
Extract reusable components from RaceSetupScreen.

## Tasks

### Extract RacePreviewRenderer
- [ ] Create `game/ui/screens/race_preview_renderer.py`
- [ ] Move portrait preview rendering
- [ ] Move flag preview rendering
- [ ] Move ship preview rendering
- [ ] Move text preview rendering
- [ ] Create clean render interface

### Extract RaceValidator
- [ ] Create `game/ui/screens/race_validator.py`
- [ ] Move validation logic from screen
- [ ] Create ValidationResult data class
- [ ] Support async validation if needed
- [ ] Return user-friendly error messages

### Extract RaceBrowserDialog
- [ ] Create `game/ui/screens/race_browser_dialog.py`
- [ ] Move RaceBrowserDialog class to separate file
- [ ] Create clean interface for dialog
- [ ] Support callback for selection

### Extract RaceConfigPanel
- [ ] Create `game/ui/panels/race_config_panel.py`
- [ ] Move configuration controls
- [ ] Create clear data binding interface
- [ ] Emit events on config changes

### Update RaceSetupScreen
- [ ] Use extracted components
- [ ] Keep only coordination logic
- [ ] Clear event flow between components
- [ ] < 500 lines total

### Unit Tests
- [ ] Test RaceValidator with various race configs
- [ ] Test RacePreviewRenderer outputs

### Integration Tests
- [ ] Race setup flow works correctly
- [ ] New game creation works
- [ ] All race-related tests pass

## Verification
- [ ] RaceSetupScreen < 500 lines
- [ ] Each extracted component < 300 lines
- [ ] UI flow unchanged from user perspective
- [ ] All tests pass

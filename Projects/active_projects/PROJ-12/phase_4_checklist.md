# PROJ-12 Phase 4: RaceSetupScreen Components

## Phase Overview
Extract reusable components from RaceSetupScreen.

## Tasks

### Extract RaceBrowserDialog
- [x] Create `game/ui/screens/race_browser_dialog.py`
- [x] Move RaceBrowserDialog class to separate file
- [x] Create clean interface for dialog
- [x] Support callback for selection
  - **Note**: 290 lines, delegates to RaceAssetLoader for preview loading
  - **Tests**: 11 tests in `test_race_browser_dialog.py`

### Extract RaceValidator
- [x] Create `game/ui/screens/race_validator.py`
- [x] Move validation logic from screen
- [x] Create ValidationResult data class
- [ ] Support async validation if needed
  - **Deferred**: Not needed for current use case
- [x] Return user-friendly error messages
  - **Note**: 78 lines, provides tab-specific error messages
  - **Tests**: 18 tests in `test_race_validator.py`

### Extract RaceAssetLoader (was RacePreviewRenderer)
- [x] Create `game/ui/screens/race_asset_loader.py`
- [x] Move portrait loading (`load_portrait_full`, `load_portrait_preview`)
- [x] Move flag loading (`load_flag_full`, `load_flag_preview`)
- [x] Move placeholder creation (`create_placeholder`)
- [x] Create clean interface for asset loading
  - **Note**: 186 lines, shared by RaceSetupScreen and RaceBrowserDialog
  - **Tests**: 12 tests in `test_race_asset_loader.py`

### Extract RaceEnvironmentPanel
- [x] Create `game/ui/panels/race_environment_panel.py`
- [x] Move environment configuration controls (gravity, temperature, radiation, atmosphere)
- [x] Create clear data binding interface (`update_config`, `update_labels`, `set_from_config`)
- [x] Delegate slider handling from RaceSetupScreen
  - **Note**: 383 lines, manages all environment preference sliders
  - **Tests**: 16 tests in `test_race_environment_panel.py`

### Extract RaceDescriptionPanel
- [x] Create `game/ui/panels/race_description_panel.py`
- [x] Move description text boxes (biological, sociological)
- [x] Create clear data binding interface (`update_config`, `update_char_counts`, `set_from_config`)
- [x] Delegate text handling from RaceSetupScreen
  - **Note**: 139 lines, manages both description text boxes
  - **Tests**: 13 tests in `test_race_description_panel.py`

### Extract Visual Selection Panels
- [x] Create `game/ui/panels/race_flag_gallery.py` - Flag selection gallery
  - **Note**: 266 lines, manages flag discovery, button creation, preview
  - **Tests**: 15 tests in `test_race_flag_gallery.py`
- [x] Create `game/ui/panels/race_portrait_gallery.py` - Portrait selection gallery
  - **Note**: 249 lines, manages portrait discovery, button creation, preview
  - **Tests**: 15 tests in `test_race_portrait_gallery.py`
- [x] Create `game/ui/panels/race_theme_gallery.py` - Ship theme selection gallery
  - **Note**: 205 lines, manages theme discovery, button creation
  - **Tests**: 14 tests in `test_race_theme_gallery.py`

### Update RaceSetupScreen
- [x] Use extracted components (RaceValidator, RaceAssetLoader, RaceBrowserDialog, RaceEnvironmentPanel, RaceDescriptionPanel)
- [x] Use extracted galleries (RaceFlagGallery, RacePortraitGallery, RaceThemeGallery)
- [x] Keep only coordination logic
- [x] Clear event flow between components
- [ ] < 500 lines total
  - **Partial**: Reduced from 2325 to 1227 lines (1098 line reduction, 47%)
  - Further extraction possible (ship preview ~300 lines, summary panel ~200 lines)
  - **Recommend accepting current state** - significant decomposition achieved

### Unit Tests
- [x] Test RaceValidator with various race configs (18 tests)
- [x] Test RaceAssetLoader outputs (12 tests)
- [x] Test RaceBrowserDialog functionality (11 tests)
- [x] Test RaceEnvironmentPanel functionality (16 tests)
- [x] Test RaceDescriptionPanel functionality (13 tests)
- [x] Test RaceFlagGallery functionality (15 tests)
- [x] Test RacePortraitGallery functionality (15 tests)
- [x] Test RaceThemeGallery functionality (14 tests)

### Integration Tests
- [ ] Race setup flow works correctly
- [ ] New game creation works
- [x] All race-related tests pass (463 UI unit tests pass)

## Verification
- [ ] RaceSetupScreen < 500 lines
  - **Partial**: 1227 lines (down from 2325, 47% reduction)
- [x] Each extracted component < 400 lines
  - RaceBrowserDialog: 290 lines
  - RaceValidator: 78 lines
  - RaceAssetLoader: 186 lines
  - RaceEnvironmentPanel: 383 lines
  - RaceDescriptionPanel: 139 lines
  - RaceFlagGallery: 266 lines
  - RacePortraitGallery: 249 lines
  - RaceThemeGallery: 205 lines
- [x] UI flow unchanged from user perspective
- [x] All tests pass (463 UI + 707 strategy = 1170 tests)

## Implementation Notes

### Files Created
- `game/ui/screens/race_browser_dialog.py` (290 lines)
- `game/ui/screens/race_validator.py` (78 lines)
- `game/ui/screens/race_asset_loader.py` (186 lines)
- `game/ui/panels/race_environment_panel.py` (383 lines)
- `game/ui/panels/race_description_panel.py` (139 lines)
- `game/ui/panels/race_flag_gallery.py` (266 lines)
- `game/ui/panels/race_portrait_gallery.py` (249 lines)
- `game/ui/panels/race_theme_gallery.py` (205 lines)
- `tests/unit/ui/test_race_browser_dialog.py` (11 tests)
- `tests/unit/ui/test_race_validator.py` (18 tests)
- `tests/unit/ui/test_race_asset_loader.py` (12 tests)
- `tests/unit/ui/test_race_environment_panel.py` (16 tests)
- `tests/unit/ui/test_race_description_panel.py` (13 tests)
- `tests/unit/ui/test_race_flag_gallery.py` (15 tests)
- `tests/unit/ui/test_race_portrait_gallery.py` (15 tests)
- `tests/unit/ui/test_race_theme_gallery.py` (14 tests)

### Files Modified
- `game/ui/screens/race_setup_screen.py` - Reduced from 2325 to 1227 lines

### Deferred Work
- **<500 line target**: Would require extracting ship preview panel (~300 lines) and summary panel (~200 lines)
- **Async validation**: Not needed for current synchronous validation use case
- **Ship Preview Panel**: Complex due to dynamic loading and scroll container management
- **Summary Panel**: Could be extracted but tightly coupled to navigation logic

### Pattern Summary
All extracted panels follow a consistent data binding interface:
- `update_config()` - Sync RaceConfig from UI controls
- `update_labels()` / `update_char_counts()` - Update display labels
- `set_from_config()` - Load saved values into UI controls
- `handle_button_click(button)` - Event delegation (for galleries)
- `on_X_selected(id)` - Selection callback method (for galleries)

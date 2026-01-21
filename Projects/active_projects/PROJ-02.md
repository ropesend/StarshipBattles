# PROJ-02: Race Setup Screen

## Overview
Create a new "Race Setup" screen accessible from the main menu that allows players to configure their custom race with visual elements (flags, portraits, ship themes), environmental preferences, and descriptive text. The race configuration will be savable/loadable as JSON files in a dedicated `races/` folder.

## Goals
- Add "Race Setup" button to the main menu
- Create a multi-step wizard with Next/Back navigation
- Enable visual selection of flags, race portraits, and ship themes
- Provide dual sliders for environmental preferences (ideal value + tolerance)
- Allow text entry for biological and sociological descriptions
- Display a summary/review screen of all selections
- Support save/load of race configurations to JSON files

## Scope
**In Scope:**
- New GameState for RACE_SETUP
- Multi-step wizard screen (4 steps)
- Visual gallery browsers for flags, portraits, and ship themes
- Environmental preference controls (dual sliders)
- Text entry fields for race descriptions
- Summary/review screen
- JSON save/load functionality

**Out of Scope:**
- Integration with New Game flow (future phase)
- Moving/renaming existing asset files
- Creating new asset images
- Multiplayer race sharing

## Current State
**Last Updated:** 2026-01-21
**Current Phase:** Complete - Audit Passed
**Last Agent Action:** Audit cycle 2 passed with no significant issues
**Next Action:** User verification required
**Blockers:** None
**Context for Next Agent:** Project is audit-complete. User needs to verify and close. Key deferred items: Load Race button (Task 6.4), Cancel confirmation dialog (Task 7.2), UI tests (Task 7.3).

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-21 | Multi-step wizard UI | User preference for clear step progression |
| 2026-01-21 | Flag design = all 3 shapes | All shapes (rectangle/shield/triangle) from same directory used together |
| 2026-01-21 | Dual sliders for env prefs | Separate ideal value + tolerance controls |
| 2026-01-21 | Save to `races/` folder | Dedicated folder at project root |

## Key Files Reference
| Component | File Path | Lines/Class |
|-----------|-----------|-------------|
| GameState enum | `game/core/constants.py` | Line 18, RACE_SETUP = 7 |
| Main menu buttons | `game/app.py` | `update_menu_buttons()`, `start_race_setup()` |
| Race config data | `game/strategy/data/race_config.py` | `RaceConfig` dataclass |
| Race library | `game/strategy/systems/race_library.py` | `RaceLibrary` class |
| Main wizard UI | `game/ui/screens/race_setup_screen.py` | `RaceSetupScreen` class |
| Config tests | `tests/unit/strategy/data/test_race_config.py` | 24 tests |
| Library tests | `tests/unit/strategy/systems/test_race_library.py` | 24 tests |

## Asset Locations
| Asset | Path | Count | Format |
|-------|------|-------|--------|
| Flags | `assets/Images/Flags/Processed/flag_*/` | 16 designs | PNG, 32-1024px |
| Race Portraits | `assets/Images/Race Portraits/` | 15 images | JPEG, 2048x2048 |
| Ship Themes | `assets/ShipThemes/` | 4 themes | PNG + theme.json |

---

## Phases

### Phase 1: Foundation - Data Model [Simple]
**Objective:** Create RaceConfig data model and RaceLibrary service
**Status:** Complete

#### Task 1.1: Add RACE_SETUP GameState [Simple]
**File:** `game/core/constants.py`
**Tests:** `python -c "from game.core.constants import GameState; print(GameState.RACE_SETUP)"`
- [x] Add `RACE_SETUP = 7` after line 17 (after `STRATEGY = 6`)
**Notes:** Added at line 18

#### Task 1.2: Create RaceConfig Data Model [Medium]
**File:** `game/strategy/data/race_config.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_race_config.py -v`
- [x] Create file with imports: `dataclasses`, `typing`, `datetime`, `game.core.json_utils`
- [x] Create `@dataclass class RaceConfig` with all fields
- [x] Implement `to_dict(self) -> dict` method
- [x] Implement `@classmethod from_dict(cls, data: dict) -> 'RaceConfig'`
- [x] Implement `save(self, filepath: str) -> bool` using `save_json`
- [x] Implement `@classmethod load(cls, filepath: str) -> Optional['RaceConfig']`
- [x] Add `__post_init__` validation for required fields
- [x] Add `validate()` method for full validation
**Notes:** Complete with 24 tests passing

#### Task 1.3: Create RaceLibrary Service [Medium]
**File:** `game/strategy/systems/race_library.py` (NEW)
**Tests:** `pytest tests/unit/strategy/systems/test_race_library.py -v`
- [x] Create class `RaceLibrary` with all methods
- [x] Generate race_id from name if not provided (slugify + UUID suffix)
**Notes:** Complete with 24 tests passing

#### Task 1.4: Create Unit Tests [Simple]
**File:** `tests/unit/strategy/data/test_race_config.py` (NEW)
**File:** `tests/unit/strategy/systems/test_race_library.py` (NEW)
- [x] Test RaceConfig to_dict/from_dict round-trip
- [x] Test RaceConfig save/load to temp file
- [x] Test RaceLibrary save and retrieve
- [x] Test RaceLibrary list races
- [x] Test RaceLibrary handles missing folder
**Notes:** 48 total tests, all passing

---

### Phase 2: Menu Integration [Simple]
**Objective:** Add Race Setup button and create screen skeleton
**Status:** Complete

#### Task 2.1: Add Menu Button [Simple]
**File:** `game/app.py`
**Tests:** Launch game, verify button appears
- [x] Add button in `update_menu_buttons()`
- [x] Add `self.showing_race_setup = False` in `__init__`
- [x] Add `self.race_setup_window = None` in `__init__`
**Notes:** Button added, all other menu buttons repositioned

#### Task 2.2: Add Screen Launch Method [Simple]
**File:** `game/app.py`
**Tests:** Click button, verify window opens
- [x] Add `start_race_setup(self)` method
- [x] Add `_on_race_setup_complete(self, race_config)` callback
- [x] Add `_on_race_setup_cancel(self)` callback
**Notes:** Complete

#### Task 2.3: Add Event/Draw Handling [Simple]
**File:** `game/app.py`
- [x] In `_draw_menu()`, add race_setup UI manager drawing when showing
- [x] In main event loop, process race_setup_window events when showing
- [x] Handle window close to set `showing_race_setup = False`
**Notes:** Complete

#### Task 2.4: Create Screen Skeleton [Medium]
**File:** `game/ui/screens/race_setup_screen.py` (NEW)
**Tests:** Open wizard, verify navigation works
- [x] Create file with imports
- [x] Create `class RaceSetupScreen(pygame_gui.elements.UIWindow)`
- [x] Implement `__init__` with callbacks
- [x] Create navigation buttons (Back, Next, Cancel, Save)
- [x] Create step panels for each step
- [x] Implement `_show_step(step_num)` - hide all panels, show current
- [x] Implement `_on_next()`, `_on_back()`, `_on_cancel()` handlers
- [x] Implement `process_event()` for button handling
**Notes:** Complete with 4-step wizard structure

---

### Phase 3: Step 1 - Visual Selection [Complex]
**Objective:** Implement flag, portrait, and ship theme galleries
**Status:** Complete

#### Task 3.1: Asset Discovery Methods [Medium]
**File:** `game/ui/screens/race_setup_screen.py`
- [x] Add `_discover_flags(self)` - scans and caches flag thumbnails
- [x] Add `_discover_portraits(self)` - scans and scales portrait thumbnails
- [x] Add `_discover_themes(self)` - uses ShipThemeManager
**Notes:** Caching implemented to avoid reloading

#### Task 3.2: Create Visuals Panel [Complex]
**File:** `game/ui/screens/race_setup_screen.py`
- [x] Create `_create_visuals_panel_content(self, panel)` with 3-column layout
- [x] Create `_create_flag_gallery()` with scrollable grid
- [x] Create `_create_portrait_gallery()` with scrollable grid
- [x] Create `_create_theme_gallery()` with theme buttons and ship previews
**Notes:** Complete with selection highlighting

#### Task 3.3: Selection Handlers [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
- [x] Add `_on_flag_selected(self, flag_id)` - updates config, shows 3-shape preview
- [x] Add `_on_portrait_selected(self, portrait_id)` - updates config, shows preview
- [x] Add `_on_theme_selected(self, theme_id)` - updates config, highlights button
**Notes:** Complete

---

### Phase 4: Step 2 - Environmental Preferences [Medium]
**Objective:** Implement dual sliders for environmental parameters
**Status:** Complete

#### Task 4.1: Create Dual Slider Helper [Medium]
**File:** `game/ui/screens/race_setup_screen.py`
- [x] Create section helper methods for gravity, temperature, radiation, atmosphere
**Notes:** Used inline creation rather than generic helper

#### Task 4.2: Create Environment Panel [Medium]
**File:** `game/ui/screens/race_setup_screen.py`
- [x] Create `_create_environment_panel_content(self, panel)`
- [x] Gravity row: ideal 0.1-3.0g, tolerance 0.0-1.0g
- [x] Temperature row: ideal 200-400K, tolerance 0-100K
- [x] Single slider for radiation tolerance: -100 to +100
- [x] Atmosphere preferences: 6 gases in 2-column layout
**Notes:** Complete with real-time label updates

#### Task 4.3: Wire Up Environment Data [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
- [x] Add `_update_env_from_sliders()` to update race_config
- [x] Add `_update_env_labels()` to update display labels
- [x] Handle `UI_HORIZONTAL_SLIDER_MOVED` events
**Notes:** Complete

---

### Phase 5: Step 3 - Text Descriptions [Simple]
**Objective:** Multi-line text entry for race descriptions
**Status:** Complete

#### Task 5.1: Create Description Panel [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
- [x] Create `_create_descriptions_panel_content(self, panel)`
- [x] Biological Description with UITextEntryBox
- [x] Character counter (0/500)
- [x] Sociological Description with UITextEntryBox
- [x] Character counter (0/500)
**Notes:** Complete

#### Task 5.2: Wire Up Text Data [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
- [x] Add `_update_description_char_counts()` for character counters
- [x] Add `_update_descriptions_from_text()` to update race_config
- [x] Enforce 500 character limit
**Notes:** Complete

---

### Phase 6: Step 4 - Summary and Save [Medium]
**Objective:** Show complete summary and enable save/load
**Status:** Complete

#### Task 6.1: Create Summary Panel [Medium]
**File:** `game/ui/screens/race_setup_screen.py`
- [x] Create `_create_summary_panel_content(self, panel)` with 2-column layout
- [x] Race name display
- [x] Selected flag (show all 3 shapes)
- [x] Selected portrait (larger preview)
- [x] Selected theme name
- [x] Environmental summary (gravity, temp, radiation, atmosphere)
- [x] Description status display
- [x] Add `_refresh_summary()` called when showing step 4
**Notes:** Complete

#### Task 6.2: Implement Save Logic [Medium]
**File:** `game/ui/screens/race_setup_screen.py`
- [x] Add `_on_save()` method
- [x] Validate race_config before saving
- [x] Call `RaceLibrary().save_race(self.race_config)`
- [x] Show error message on failure
- [x] Call `self.on_complete_callback(self.race_config)` on success
**Notes:** Complete

#### Task 6.3: Implement Load Existing [Medium]
**File:** `game/ui/screens/race_setup_screen.py`
- [x] Add optional `race_to_edit: RaceConfig = None` parameter to `__init__`
- [x] If provided, pre-populate all UI fields
- [x] Change "Save" button text to "Update" for edits
**Notes:** Complete

#### Task 6.4: Add Save/Load Buttons [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
- [ ] Add "Load Race" button on Step 1 (opens file browser)
- [ ] Add `_on_load_clicked(self)` for loading saved races
**Notes:** NOT YET IMPLEMENTED - deferred to future enhancement

---

### Phase 7: Polish and Testing [Medium]
**Objective:** Error handling, validation, comprehensive tests
**Status:** Partial

#### Task 7.1: Add Validation [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
- [x] Validate before advancing from Step 1 (name + selections required)
- [x] Show validation errors in error label
- [ ] Disable Save button until all required fields complete
**Notes:** Basic validation complete

#### Task 7.2: Add Error Handling [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
- [x] Handle missing asset files gracefully (placeholder surfaces)
- [x] Handle save failures with user-friendly error
- [ ] Add confirmation dialog for Cancel with unsaved changes
**Notes:** Basic error handling complete

#### Task 7.3: Create Screen Tests [Medium]
**File:** `tests/unit/ui/test_race_setup_screen.py` (NEW)
- [ ] Test wizard initialization
- [ ] Test step navigation
- [ ] Test visual selection persistence
- [ ] Test slider value updates
- [ ] Test text entry
- [ ] Test save/load round-trip
**Notes:** NOT YET IMPLEMENTED - UI tests require pygame display

#### Task 7.4: Memory Optimization [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
- [x] Cache thumbnails after first load (flag, portrait, theme caches)
- [x] Scale portraits to thumbnail size immediately on discovery
- [ ] Clear caches when window closes
**Notes:** Caching implemented

---

### Phase 8: Audit Fixes (Cycle 1) [Simple]
**Objective:** Fix critical bug found in audit cycle 1
**Status:** Complete

#### Task 8.1: Fix Duplicate _refresh_summary Method [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** Manual verification - navigate to Summary step and verify data displays
- [x] Delete duplicate empty `_refresh_summary()` method at lines 1493-1495
- [x] Verify Summary panel displays all configuration data correctly
**Notes:** Fixed - deleted 4 lines (empty stub method). Full implementation at lines 1297-1391 now correctly executes.

---

## Verification Checklist

### After Phase 1
- [x] RaceConfig can serialize/deserialize to JSON
- [x] RaceLibrary can save/load race files
- [x] `races/` folder created on first save
- [x] All unit tests pass: `pytest tests/unit/strategy/ -v`

### After Phase 2
- [x] "Race Setup" button appears on main menu
- [x] Clicking button opens wizard window
- [x] Next/Back navigation works between panels
- [x] Cancel closes window

### After Phase 3
- [x] Flag gallery shows 16 flag options
- [x] Portrait gallery shows 15 portrait options
- [x] Theme gallery shows 4 themes with ship previews
- [x] Selections highlight and persist through navigation

### After Phase 4
- [x] All sliders render and move
- [x] Value displays update in real-time
- [x] Values persist through navigation

### After Phase 5
- [x] Text entry works for both descriptions
- [x] Character counters update
- [x] Text persists through navigation

### After Phase 6
- [x] Summary shows all selections
- [x] Save creates JSON file in `races/`
- [ ] Load populates UI from saved race (Load button not yet implemented)

### Final Verification
- [x] Complete wizard end-to-end
- [x] Save race creates JSON file
- [x] All unit tests pass: 48 tests passing
- [ ] No memory leaks verification needed

---

## Files Summary

### Files Modified
| File | Changes |
|------|---------|
| `game/core/constants.py` | Added `RACE_SETUP = 7` (line 18) |
| `game/app.py` | Added menu button, state handling, callbacks |

### Files Created
| File | Purpose |
|------|---------|
| `game/strategy/data/race_config.py` | RaceConfig dataclass |
| `game/strategy/systems/race_library.py` | Race file management |
| `game/ui/screens/race_setup_screen.py` | Main wizard UI (~1370 lines) |
| `tests/unit/strategy/data/test_race_config.py` | Data model tests (24 tests) |
| `tests/unit/strategy/systems/test_race_library.py` | Service tests (24 tests) |

### Folders Created
| Folder | Purpose |
|--------|---------|
| `races/` | Store race JSON files (created on first save) |

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | 2026-01-21 | 1 critical bug: duplicate `_refresh_summary()` method | Fixed in Phase 8 - deleted empty stub |
| 2 | 2026-01-21 | No significant issues after fix verification | PASSED |

## Completion Checklist
- [x] All Phase 1 tasks checked off
- [x] All Phase 2 tasks checked off
- [x] All Phase 3 tasks checked off
- [x] All Phase 4 tasks checked off
- [x] All Phase 5 tasks checked off
- [x] Phase 6 tasks mostly complete (Load button deferred)
- [x] Phase 7 partial (basic validation/error handling)
- [x] All unit tests passing (48/48)
- [ ] UI tests (not created - requires pygame display)
- [x] Audit passed (2 cycles, 1 bug fixed)
- [ ] User verified

# PROJ-04: Race System Integration for New Game Setup

## Overview
Integrate the existing race configuration system into the new game setup flow, allowing players to select or create races during game initialization. Apply race visual customizations (themes, flags, portraits) to in-game elements like colonies and fleets.

## Goals
- Replace manual empire name entry with race-based selection in new game setup
- Allow players to either "Load Race" (existing saved race) or "Setup Race" (create new via race setup screen)
- Ensure race setup screen continues to work as standalone system
- Apply race customizations in-game: themes for fleets/ships, rectangle flags for colonies, shield flags for fleets
- Races are always saved when created/modified

## Scope
**In Scope:**
- Modify NewGameSetupScreen to include race selection UI
- Integrate RaceSetupScreen as modal from new game setup
- Add RaceBrowserDialog integration for loading existing races
- Extend PlayerConfig to include race data
- Update Empire creation to use race visual properties
- Implement flag rendering: rectangle for colonies, shield for fleets
- Apply theme selection from race to fleets/ships
- Ensure race portrait is stored (for future UI use)

**Out of Scope:**
- Race portrait display in-game UI panels (noted for future, not implementing now)
- AI race selection (AI players will use default themes)
- Multiplayer race synchronization
- Environmental preferences gameplay effects (already in RaceConfig, not using yet)

## Current State
**Last Updated:** 2026-01-21
**Current Phase:** Implementation Complete - Ready for Verification
**Last Agent Action:** Completed all 4 phases of implementation
**Next Action:** Manual verification by user
**Blockers:** None
**Context for Next Agent:** All code changes complete. 2037 tests passing. Ready for user to test in-game.

## Key Files Reference
| Component | File Path | Class/Function |
|-----------|-----------|----------------|
| Race Data Model | `game/strategy/data/race_config.py` | `RaceConfig` dataclass |
| Race Persistence | `game/strategy/systems/race_library.py` | `RaceLibrary` class |
| Race Setup UI | `game/ui/screens/race_setup_screen.py` | `RaceSetupScreen`, `RaceBrowserDialog` |
| New Game Setup | `game/ui/screens/new_game_setup_screen.py` | `NewGameSetupScreen` |
| Player Config | `game/strategy/engine/game_config.py` | `PlayerConfig`, `GameConfig` |
| Empire Model | `game/strategy/data/empire.py` | `Empire` class |
| Game Session | `game/strategy/engine/game_session.py` | `GameSession.__init__()` |
| Strategy Renderer | `game/ui/screens/strategy_renderer.py` | Colony flags (457-478), Fleet icons (480-527) |
| Theme Manager | `game/simulation/ship_theme.py` | `ShipThemeManager` |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-21 | Project ID: PROJ-04 | User specified (PROJ-03 in use elsewhere) |
| 2026-01-21 | Two separate buttons per player: "Load Race" and "Setup Race" | User preference for clear, explicit UI options |
| 2026-01-21 | After race setup, return to new game setup screen | Allows configuring multiple players before starting |
| 2026-01-21 | Fleet display: Show both shield flag AND ship icon | User wants both visual elements visible |
| 2026-01-21 | Race name becomes empire name automatically | Simplifies setup flow, no separate naming step |

## Initial Analysis

### Race Setup System (Existing)
- **RaceConfig** dataclass stores: race_id, name, flag_id, portrait_id, theme_id, environmental preferences, descriptions
- **RaceLibrary** handles save/load to `races/` folder as JSON files
- **RaceSetupScreen** is a 5-tab wizard: Summary, Visuals, Ships, Environment, Descriptions
- **RaceBrowserDialog** provides modal selection of existing saved races
- Race validation ensures all required fields are set before saving
- Auto-generates race_id from slugified name + UUID suffix

### New Game Setup Flow (Current)
- **NewGameSetupScreen** collects: save_name, player_count (1-4), empire_names
- **PlayerConfig** stores: name, theme (hardcoded from THEME_DEFAULTS), color, is_human
- **THEME_DEFAULTS** assigns Federation/Atlantians/Romulans/Klingons based on player index
- **GameSession** creates Empire objects from PlayerConfig list
- No current integration with race system

### Visual Customization System (Current)
- **Colony flags**: Rendered at `strategy_renderer.py:457-478`, loads from theme's `Flags/Colony_Flag.jpg`
- **Fleet icons**: Rendered at `strategy_renderer.py:480-527`, loads from theme's `Skins/Battlecruiser.png`
- **Flag assets**: Race flags stored in `assets/Images/Flags/Processed/{flag_id}/` with rectangle/shield/triangle variants
- **Theme assets**: Ship themes in `assets/ShipThemes/{ThemeName}/`
- Empire already has `empire_theme_id` that controls visual appearance

### Integration Gap Analysis
1. **PlayerConfig** needs race_config field to carry race selection through setup
2. **NewGameSetupScreen** needs UI for "Load Race" / "Setup Race" per player
3. **Empire** needs to receive flag_id and portrait_id from race (currently only gets theme_id)
4. **Colony rendering** uses theme flags, needs to use race-selected flags instead
5. **Fleet rendering** uses theme ship icon, needs to use race-selected shield flag

## Swarm Findings Summary

### Architecture Analysis
- **Module Layering**: Clean one-way dependencies: UI → Config → Data → Engine
- **Modal Pattern**: Callback-based windows using pygame_gui.UIWindow
- **Data Flow**: PlayerConfig → GameSession → Empire follows established config pattern
- **Key Gap**: PlayerConfig has no race_config field; Empire has no flag_id/portrait_id

### Dependency Map
- **No Circular Dependencies**: All race imports (race_config, race_library, race_setup_screen) are safe
- **New Imports Needed**: new_game_setup_screen.py needs RaceLibrary, RaceSetupScreen, RaceBrowserDialog, RaceConfig
- **Isolated Data Layer**: game_config.py has no game imports - safe to extend

### Test Impact
- **Modify**: test_new_game_setup.py (5 tests need race_config parameter)
- **Modify**: test_game_session.py (3 new tests for race→empire flow)
- **Create**: Integration tests for race selection flow (4 tests)
- **Extend**: test_empire.py (flag_id, portrait_id fields)
- **Total**: ~19 new tests, 8 modified tests

### Key Patterns to Reuse
- **Modal Dialog**: RaceBrowserDialog pattern (lines 22-325 in race_setup_screen.py)
- **Dynamic UI**: _create_empire_inputs() pattern (lines 132-187 in new_game_setup_screen.py)
- **Asset Caching**: _discover_flags() pattern (lines 519-558 in race_setup_screen.py)
- **Config Passing**: PlayerConfig.to_dict()/from_dict() pattern

### Data Flow Analysis
- **Current**: NewGameSetupScreen → GameConfig.players → GameSession → Empire.empire_theme_id
- **Asset Loading**: StrategyScene._load_assets() builds empire_assets dict from theme paths
- **Colony Flags**: strategy_renderer.py:457-478 uses empire_assets[emp.id]['colony']
- **Fleet Icons**: strategy_renderer.py:490-502 uses empire_assets[emp.id]['fleet']
- **Injection Points**: PlayerConfig needs race_config; Empire needs flag_id, portrait_id

### Risks Identified
1. **No Race Selected** (HIGH) - Need validation or default race assignment
2. **Deleted Assets** (HIGH) - Race references invalid flag/portrait/theme → fallback needed
3. **Save Compatibility** (HIGH) - Old saves have no race_id → use .get() with defaults
4. **Multiple Same Race** (MEDIUM) - Allow but warn (symmetric gameplay valid)
5. **Modal Stacking** (MEDIUM) - When race modal open, parent stops processing events

### Serialization Requirements
- **PlayerConfig**: Add optional race_id field, race visual properties
- **Empire**: Add flag_id, portrait_id fields for visual identity
- **Backwards Compatible**: All new fields use .get() with None/defaults
- **No Version Bump Needed**: Changes are additive

### UI Layout Analysis
- **Current Window**: 500x450px, tight for race UI
- **Recommendation**: Expand to 600x600px for race selection per player
- **Per-Player Layout**: 90-100px height (35px name + 55-65px race selection)
- **Race Preview**: 24x24 flag + race name + Load/Setup buttons (70px each)

---

## Phases

### Phase 1: Data Model Extensions [Medium]
**Objective:** Extend PlayerConfig and Empire to carry race data through the system
**Status:** Not Started

#### Task 1.1: Extend PlayerConfig with race fields [Simple]
**File:** `game/strategy/engine/game_config.py`
**Tests:** `pytest tests/unit/strategy/engine/test_game_config.py` (create if needed)
- [ ] Add import: `from typing import Optional` (line 3, if not present)
- [ ] Add field to PlayerConfig: `race_id: Optional[str] = None` (after is_human, ~line 36)
- [ ] Add field: `flag_id: str = ""`
- [ ] Add field: `portrait_id: str = ""`
- [ ] Update `to_dict()`: Add race_id, flag_id, portrait_id to output dict (lines 38-44)
- [ ] Update `from_dict()`: Load race_id, flag_id, portrait_id with .get() defaults (lines 46-54)
**Notes:**

#### Task 1.2: Extend Empire with race visual fields [Simple]
**File:** `game/strategy/data/empire.py`
**Tests:** `pytest tests/unit/strategy/data/test_empire.py`
- [ ] Add parameters to `__init__`: `flag_id: str = ""`, `portrait_id: str = ""` (line 5)
- [ ] Store as instance variables: `self.flag_id = flag_id`, `self.portrait_id = portrait_id`
- [ ] Update `to_dict()`: Add flag_id, portrait_id to output (lines 46-63)
- [ ] Update `from_dict()`: Load flag_id, portrait_id with .get() defaults (lines 65-106)
**Notes:**

#### Task 1.3: Update GameSession empire creation [Simple]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/unit/strategy/engine/test_game_session.py`
- [ ] In `__init__` empire creation loop (lines 32-43), pass player_cfg.flag_id and portrait_id to Empire constructor
- [ ] Verify theme still comes from player_cfg.theme (for backwards compatibility)
**Notes:**

---

### Phase 2: New Game Setup UI Modifications [Complex]
**Objective:** Add race selection UI to NewGameSetupScreen
**Status:** Not Started

#### Task 2.1: Expand window and adjust layout [Medium]
**File:** `game/ui/screens/new_game_setup_screen.py`
**Tests:** Manual test - launch new game setup, verify layout
- [ ] Update window dimensions: Change from 500x450 to 600x600 (also update app.py where window is created)
- [ ] Adjust `empire_inputs_start_y` to accommodate larger per-player sections
- [ ] Update button positions to account for new height
**Notes:**

#### Task 2.2: Add race selection UI elements [Medium]
**File:** `game/ui/screens/new_game_setup_screen.py`
**Tests:** Manual test - verify buttons appear and are clickable
- [ ] Add imports: `from game.strategy.systems.race_library import RaceLibrary`
- [ ] Add imports: `from game.ui.screens.race_setup_screen import RaceSetupScreen, RaceBrowserDialog`
- [ ] Add imports: `from game.strategy.data.race_config import RaceConfig`
- [ ] Add instance variables: `self.race_library = RaceLibrary()`
- [ ] Add instance variables: `self.player_races: List[Optional[RaceConfig]] = [None] * 4`
- [ ] Add instance variables: `self.race_buttons: List[Tuple[UIButton, UIButton]] = []` (load, setup pairs)
- [ ] Add instance variables: `self.race_preview_labels: List[UILabel] = []`
- [ ] Add instance variable: `self.active_race_modal = None`
- [ ] Add instance variable: `self.race_modal_player_index = -1`
**Notes:**

#### Task 2.3: Modify _create_empire_inputs for race UI [Complex]
**File:** `game/ui/screens/new_game_setup_screen.py`
**Tests:** Manual test - player count change updates race UI correctly
- [ ] In `_create_empire_inputs()`, after creating name input, add race selection row:
  - Race preview label (shows selected race name or "No Race Selected")
  - "Load Race" button (70x30)
  - "Setup Race" button (70x30)
- [ ] Store references in `self.race_buttons` and `self.race_preview_labels`
- [ ] Update `_update_empire_visibility()` to show/hide race UI based on player count
**Notes:**

#### Task 2.4: Implement race button handlers [Medium]
**File:** `game/ui/screens/new_game_setup_screen.py`
**Tests:** Manual test - clicking buttons opens correct dialogs
- [ ] Add `_on_load_race_clicked(player_index)` method:
  - Create RaceBrowserDialog centered on window
  - Set callbacks: `_on_race_loaded(player_index, race_config)`, `_on_race_dialog_cancelled()`
  - Store dialog reference in `self.active_race_modal`
- [ ] Add `_on_setup_race_clicked(player_index)` method:
  - Create RaceSetupScreen (may need to adjust positioning)
  - Set callbacks: `_on_race_created(player_index, race_config)`, `_on_race_setup_cancelled()`
  - Store reference and player index
- [ ] Update `process_event()` to handle race button clicks
**Notes:**

#### Task 2.5: Implement race selection callbacks [Medium]
**File:** `game/ui/screens/new_game_setup_screen.py`
**Tests:** Manual test - selecting race updates display
- [ ] Add `_on_race_loaded(player_index, race_config)`:
  - Store race in `self.player_races[player_index]`
  - Update preview label with race name
  - Clear active modal reference
- [ ] Add `_on_race_created(player_index, race_config)`:
  - Same as above (race was saved by RaceSetupScreen)
- [ ] Add `_on_race_dialog_cancelled()`:
  - Clear active modal reference
  - No other action needed
- [ ] Add `_update_race_preview(player_index)` helper method
**Notes:**

#### Task 2.6: Update build_game_config to include race data [Medium]
**File:** `game/ui/screens/new_game_setup_screen.py`
**Tests:** `pytest tests/unit/ui/test_new_game_setup.py`
- [ ] Modify `build_game_config()` signature to accept `race_configs: List[Optional[RaceConfig]]`
- [ ] When creating PlayerConfig, set:
  - `theme = race.theme_id if race else THEME_DEFAULTS[i][0]`
  - `flag_id = race.flag_id if race else ""`
  - `portrait_id = race.portrait_id if race else ""`
  - `name = race.name if race else empire_names[i]` (race name = empire name per user decision)
- [ ] Update `_on_start_clicked()` to pass `self.player_races` to build_game_config
**Notes:**

---

### Phase 3: Strategy Layer Visual Integration [Complex]
**Objective:** Display race flags on colonies and fleets
**Status:** Not Started

#### Task 3.1: Update asset loading for race flags [Medium]
**File:** `game/ui/screens/strategy_scene.py`
**Tests:** Manual test - start game with race, verify flags load
- [ ] In `_load_assets()` (lines 431-459), check if empire has flag_id set
- [ ] If flag_id set, load flag from `assets/Images/Flags/Processed/{flag_id}/`:
  - Load `256/rectangle.png` for colony flag
  - Load `256/shield.png` for fleet flag
- [ ] If no flag_id, fall back to current theme flag behavior
- [ ] Store in `empire_assets[emp.id]['colony']` and `empire_assets[emp.id]['fleet_flag']`
**Notes:**

#### Task 3.2: Modify colony rendering to use race rectangle flag [Simple]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** Manual test - colonized planet shows race rectangle flag
- [ ] In `_draw_planet_sprite()` (lines 457-478), current code already uses `empire_assets['colony']`
- [ ] Verify the asset loading change (Task 3.1) makes this work automatically
- [ ] If needed, adjust scaling or positioning
**Notes:**

#### Task 3.3: Modify fleet rendering to show shield flag with ship icon [Medium]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** Manual test - fleet shows both ship icon and shield flag
- [ ] In `_draw_fleets()` (lines 480-527), after drawing ship icon:
- [ ] Check if `empire_assets[emp.id]['fleet_flag']` exists
- [ ] If exists, draw shield flag offset from ship icon (e.g., top-right corner)
- [ ] Scale shield flag appropriately (smaller than ship icon, ~60% size)
- [ ] Both ship icon AND shield flag visible per user decision
**Notes:**

---

### Phase 4: Testing and Polish [Medium]
**Objective:** Comprehensive testing and edge case handling
**Status:** Not Started

#### Task 4.1: Add unit tests for PlayerConfig race fields [Simple]
**File:** `tests/unit/strategy/engine/test_game_config.py` (create or extend)
**Tests:** `pytest tests/unit/strategy/engine/test_game_config.py`
- [ ] Test PlayerConfig with race_id, flag_id, portrait_id
- [ ] Test to_dict()/from_dict() round-trip preserves race fields
- [ ] Test from_dict() with missing race fields uses defaults
**Notes:**

#### Task 4.2: Add unit tests for Empire race fields [Simple]
**File:** `tests/unit/strategy/data/test_empire.py`
**Tests:** `pytest tests/unit/strategy/data/test_empire.py`
- [ ] Test Empire with flag_id, portrait_id
- [ ] Test to_dict()/from_dict() round-trip
- [ ] Test backwards compatibility (old save without race fields)
**Notes:**

#### Task 4.3: Update existing new game setup tests [Medium]
**File:** `tests/unit/ui/test_new_game_setup.py`
**Tests:** `pytest tests/unit/ui/test_new_game_setup.py`
- [ ] Update tests calling `build_game_config()` to pass race_configs parameter
- [ ] Add tests for race selection flow
- [ ] Add test for race name becoming empire name
**Notes:**

#### Task 4.4: Add integration test for race→game flow [Medium]
**File:** `tests/unit/ui/test_race_game_integration.py` (create)
**Tests:** `pytest tests/unit/ui/test_race_game_integration.py`
- [ ] Test: Create RaceConfig → build GameConfig with race → create GameSession → verify Empire has flag_id/portrait_id
- [ ] Test: Save game with race → load game → verify race data preserved
**Notes:**

#### Task 4.5: Handle edge cases [Simple]
**File:** Multiple files
**Tests:** Manual testing
- [ ] If no race selected for a player, use THEME_DEFAULTS (already handled in Task 2.6)
- [ ] If race's flag_id references deleted flag, fall back to theme flag (Task 3.1)
- [ ] If player count decreases, clear orphaned race selections
**Notes:**

---

## Verification Checklist

### After Each Phase
- [ ] Run `pytest tests/unit/` - all tests pass
- [ ] Manual test: Start new game with default settings - no crashes
- [ ] Manual test: Start new game with race selection - verify flow

### Final Verification
- [ ] Create a new race using race setup screen (standalone)
- [ ] Start new game with 2 players, select races for both
- [ ] Verify race names appear as empire names
- [ ] Verify race themes are used for ships
- [ ] Verify rectangle flags appear on colonized planets
- [ ] Verify shield flags appear on fleets (alongside ship icon)
- [ ] Save game, reload, verify race data persists
- [ ] Start new game without selecting races - verify defaults work
- [ ] Run full test suite: `pytest`

---

## Verification Checklist
*[To be detailed in final plan]*

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| | | | |

## Completion Checklist
- [ ] All phases complete
- [ ] All tests passing
- [ ] User verified

# PROJ-06: Quickstart 1P / 2P Buttons

## Overview
Add two new buttons to the main menu: "Quickstart 1P" and "Quickstart 2P" that instantly create new game sessions with pre-configured test empires and ship designs, bypassing the normal game setup flow.

## Goals
- Add "Quickstart 1P" and "Quickstart 2P" buttons to main menu
- Create pre-defined test empires (TestEmp1, TestEmp2) with fixed flags, portraits, themes
- Create minimal but valid ship designs (with engine, warp drive, bridge, crew, life support, fuel)
- Create minimal but valid complex design (command center, space yard, crew, life support)
- Generate date/time stamped save file names
- Store test assets in an obvious location
- Create unit tests to validate race/design loading and detect when code changes break compatibility

## Scope
**In Scope:**
- Two new main menu buttons with click handlers
- Pre-defined test empire configurations (RaceConfig files)
- Pre-defined ship and complex designs
- Quickstart game session creation flow
- Date/time stamped save file naming
- Unit tests for loading races and designs
- Dedicated storage location for test assets

**Out of Scope:**
- Modifications to normal game setup flow
- AI opponent configuration
- Custom difficulty settings
- Galaxy generation customization

## Current State
**Last Updated:** 2026-01-21
**Current Phase:** Implementation Complete - Awaiting User Verification
**Last Agent Action:** All 5 phases implemented, 66 unit tests passing
**Next Action:** User to manually test quickstart buttons in game
**Blockers:** None
**Context for Next Agent:** Implementation complete. Run game and click Quickstart 1P/2P buttons to verify.

## Key Files Reference
| Component | File Path | Class/Function |
|-----------|-----------|----------------|
| Main Menu | `game/app.py` | `Game.update_menu_buttons()` (line 122) |
| Button Widget | `ui/components.py` | `Button` class (line 5) |
| New Game Setup | `game/ui/screens/new_game_setup_screen.py` | `NewGameSetupScreen` (line 22) |
| Game Config | `game/strategy/engine/game_config.py` | `GameConfig`, `PlayerConfig` |
| Game Session | `game/strategy/engine/game_session.py` | `GameSession` (line 8) |
| Empire | `game/strategy/data/empire.py` | `Empire` class |
| Race Config | `game/strategy/data/race_config.py` | `RaceConfig` dataclass (line 26) |
| Race Library | `game/strategy/systems/race_library.py` | `RaceLibrary` (line 39) |
| Design Library | `game/strategy/systems/design_library.py` | `DesignLibrary` (line 20) |
| Ship Serialization | `game/simulation/entities/ship_serialization.py` | `ShipSerializer` |
| Ship Validator | `game/simulation/ship_validator.py` | `ShipDesignValidator` |
| Vehicle Design Service | `game/simulation/services/vehicle_design_service.py` | `VehicleDesignService` |
| Save Game Service | `game/strategy/systems/save_game_service.py` | `SaveGameService` |
| Components DB | `data/components.json` | Component definitions |
| Vehicle Classes | `data/vehicleclasses.json` | Ship class definitions |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-21 | Buttons at top of menu (above New Game) | Most prominent position, easy to find for testing |
| 2026-01-21 | Use first existing flag/portrait from assets | Simpler, no new asset files needed |
| 2026-01-21 | Store test fixtures in `tests/fixtures/quickstart/` | Clear test purpose, alongside other test fixtures |
| 2026-01-21 | Use Escort class for test ship | Smallest ship class, minimal components needed |

## Initial Analysis

### Main Menu Structure
- Main menu in `game/app.py` uses `Button` class from `ui/components.py`
- 7 existing buttons arranged vertically at 70px spacing
- Buttons created in `update_menu_buttons()` (line 122)
- Button callback pattern: simple method reference (e.g., `self.start_strategy_layer`)

### Empire/Race System
- `RaceConfig` dataclass stores race definitions with flag_id, portrait_id, theme_id, environmental preferences
- Races stored as JSON in `races/` directory with format `{name}_{uuid}.json`
- 3 existing races: gorgons, rossarians variants
- Themes available: Federation, Atlantians, Romulans, Klingons (with default colors)
- Flags stored in `assets/Images/Flags/Processed/{flag_id}/`
- Portraits stored in `assets/Images/Race Portraits/`

### Ship Design System
- Designs stored in `saves/{save_name}/designs/empire_N/{design_name}.json`
- Ship requires: hull (auto), bridge (command), crew quarters, life support
- Engine components: `standard_engine`, etc.
- Warp drives: `warp_drive_light` (mass 30), `warp_drive_standard` (mass 50)
- Validation checks crew capacity vs crew required, life support capacity

### Complex Design System
- Vehicle type "Planetary Complex" with 11 tiers
- Key components: `central_complex_command` (bridge for complexes), `space_shipyard`
- Complex designs also need crew and life support
- Smallest tier: "Planetary Complex (Tier 1)" with max_mass 1000

### Current Game Start Flow
1. Click "New Game" -> `start_strategy_layer()` (line 163)
2. Opens `NewGameSetupScreen` window
3. Configure save name, player count, races
4. `_on_start_clicked()` builds `GameConfig`
5. `_on_new_game_start(config)` creates `GameSession`, saves, starts `StrategyScene`

## Swarm Findings Summary

### Architecture Analysis
- **Quickstart flow is minimal**: Button click → build `GameConfig` → call existing `_on_new_game_start(config)` → done
- **No new service class needed**: Reuse existing `GameConfig`, `GameSession`, `SaveGameService`
- **Lightweight helper module**: Create `game/strategy/quickstart_builder.py` for config factory functions
- **Design loading**: Copy pre-made JSON design files into save folder after session creation

### Dependency Map
- All required imports already exist in codebase, no circular dependency risks
- Key imports: `GameConfig`, `PlayerConfig` from `game.strategy.engine.game_config`
- `GameSession` from `game.strategy.engine.game_session`
- `SaveGameService` from `game.strategy.systems.save_game_service`
- Pattern: Use lazy imports inside methods (already done in `_on_new_game_start`)

### Test Impact
- Follow existing patterns in `tests/unit/strategy/data/test_race_config.py` (379 lines)
- Use `@pytest.mark.parametrize` for data-driven fixture tests
- Test both schema validation and full round-trip serialization
- Use `tests/fixtures/paths.py` utilities for path management

### Key Patterns to Reuse
- **Button pattern**: `Button(x, y, 200, 50, "Text", self.callback)` in `update_menu_buttons()`
- **Config building**: `NewGameSetupScreen.build_game_config()` static method pattern
- **JSON loading**: `load_json()` from `game.core.json_utils`
- **Timestamps**: `datetime.now().strftime("%Y%m%d_%H%M%S")` for save names

### Asset IDs to Use
**TestEmp1:**
- flag_id: `flag_2fl0bh2fl0bh2fl0` (first alphabetically)
- portrait_id: `Gemini_Generated_Image_59rl4259rl4259rl.jpg`
- theme_id: `Federation`, color: `(0, 100, 255)`

**TestEmp2:**
- flag_id: `flag_4lg1ov4lg1ov4lg1` (second alphabetically)
- portrait_id: `Gemini_Generated_Image_6dgi486dgi486dgi.jpg`
- theme_id: `Atlantians`, color: `(0, 200, 150)`

### Component IDs for Designs
**Escort Ship:**
| Component | ID | Layer | Mass |
|-----------|-----|-------|------|
| Bridge | `bridge` | CORE | ~50 |
| Crew Quarters | `crew_quarters` | CORE | 30 |
| Life Support | `life_support` | CORE | 20 |
| Standard Engine | `standard_engine` | OUTER | 80 |
| Light Warp Drive | `warp_drive_light` | OUTER | 30 |
| Fuel Tank | `fuel_tank` | OUTER | 40 |

**Planetary Complex (Tier 1):**
| Component | ID | Layer | Mass |
|-----------|-----|-------|------|
| Central Complex Command | `central_complex_command` | CORE | ~50 |
| Crew Quarters | `crew_quarters` | CORE | 30 |
| Life Support | `life_support` | CORE | 20 |
| Space Shipyard | `space_shipyard` | INNER | 500 |

### Risks Identified
1. **Button positioning**: Adding 2 buttons at top shifts all others down - need to recalculate Y positions
2. **Design validation**: Designs must pass `ShipDesignValidator` - need correct modifiers on components
3. **Fixture staleness**: If component data changes, fixture JSONs may become invalid - tests will catch this

---

## Phases

### Phase 1: Create Test Fixtures [Simple]
**Objective:** Create the race and design JSON fixtures in `tests/fixtures/quickstart/`
**Status:** Not Started

#### Task 1.1: Create Quickstart Fixture Directory Structure [Simple]
**Files:** Create new directories
**Tests:** Verify directories exist
- [ ] Create `tests/fixtures/quickstart/` directory
- [ ] Create `tests/fixtures/quickstart/races/` subdirectory
- [ ] Create `tests/fixtures/quickstart/designs/` subdirectory
**Notes:**

#### Task 1.2: Create Test Race Fixtures [Simple]
**Files:** `tests/fixtures/quickstart/races/test_emp1.json`, `tests/fixtures/quickstart/races/test_emp2.json`
**Tests:** `pytest tests/unit/quickstart/test_quickstart_races.py`
- [ ] Create `test_emp1.json` with Federation theme, first flag/portrait
- [ ] Create `test_emp2.json` with Atlantians theme, second flag/portrait
- [ ] Ensure both pass `RaceConfig.validate()` requirements
**Notes:**

#### Task 1.3: Create Test Ship Design Fixture [Medium]
**Files:** `tests/fixtures/quickstart/designs/qs_escort.json`
**Tests:** `pytest tests/unit/quickstart/test_quickstart_designs.py`
- [ ] Create Escort-class ship with: bridge, crew_quarters, life_support, standard_engine, warp_drive_light, fuel_tank
- [ ] Include proper modifiers (`simple_size_mount`, `hardened_mount`) on each component
- [ ] Set resources.fuel to 50000
- [ ] Include `expected_stats` for validation
- [ ] Include `_metadata` section
**Notes:**

#### Task 1.4: Create Test Complex Design Fixture [Medium]
**Files:** `tests/fixtures/quickstart/designs/qs_complex.json`
**Tests:** `pytest tests/unit/quickstart/test_quickstart_designs.py`
- [ ] Create Planetary Complex (Tier 1) with: central_complex_command, crew_quarters, life_support, space_shipyard
- [ ] Include proper modifiers on each component
- [ ] Include `expected_stats` and `_metadata`
**Notes:**

---

### Phase 2: Create Unit Tests [Medium]
**Objective:** Create tests that validate fixtures and detect schema changes
**Status:** Not Started

#### Task 2.1: Create Test Conftest [Simple]
**File:** `tests/unit/quickstart/conftest.py`
**Tests:** N/A (this is test infrastructure)
- [ ] Create fixture loading utilities
- [ ] Create `quickstart_races_dir` fixture
- [ ] Create `quickstart_designs_dir` fixture
**Notes:**

#### Task 2.2: Create Race Fixture Tests [Simple]
**File:** `tests/unit/quickstart/test_quickstart_races.py`
**Tests:** Run `pytest tests/unit/quickstart/test_quickstart_races.py -v`
- [ ] Test fixture files exist
- [ ] Test each race loads as valid `RaceConfig`
- [ ] Test each race passes `.validate()`
- [ ] Test round-trip serialization preserves data
**Notes:**

#### Task 2.3: Create Design Fixture Tests [Medium]
**File:** `tests/unit/quickstart/test_quickstart_designs.py`
**Tests:** Run `pytest tests/unit/quickstart/test_quickstart_designs.py -v`
- [ ] Test fixture files exist
- [ ] Test each design loads as valid `Ship`
- [ ] Test `.recalculate_stats()` succeeds without error
- [ ] Test expected_stats match actual stats (within tolerance)
- [ ] Test required components present (bridge, crew, life support)
**Notes:**

---

### Phase 3: Implement Quickstart Builder [Simple]
**Objective:** Create the QuickstartBuilder helper module
**Status:** Not Started

#### Task 3.1: Create QuickstartBuilder Module [Simple]
**File:** `game/strategy/quickstart_builder.py`
**Tests:** `pytest tests/unit/quickstart/test_quickstart_builder.py`
- [ ] Create `QuickstartBuilder` class with static methods
- [ ] Implement `build_1p_config()` returning `GameConfig` with timestamped save name
- [ ] Implement `build_2p_config()` returning `GameConfig` with 2 players
- [ ] Load race configs from `tests/fixtures/quickstart/races/`
- [ ] Include helper to get fixture paths
**Notes:**

#### Task 3.2: Create Quickstart Builder Tests [Simple]
**File:** `tests/unit/quickstart/test_quickstart_builder.py`
**Tests:** Run `pytest tests/unit/quickstart/test_quickstart_builder.py -v`
- [ ] Test `build_1p_config()` returns valid GameConfig with 1 player
- [ ] Test `build_2p_config()` returns valid GameConfig with 2 players
- [ ] Test save names include timestamp
- [ ] Test race data is correctly loaded into PlayerConfig
**Notes:**

---

### Phase 4: Implement Main Menu Integration [Simple]
**Objective:** Add buttons and handlers to game/app.py
**Status:** Not Started

#### Task 4.1: Add Quickstart Button Handlers [Simple]
**File:** `game/app.py`
**Tests:** Manual - launch game and click buttons
- [ ] Add `start_quickstart_1p(self)` method after line ~341
  ```python
  def start_quickstart_1p(self):
      from game.strategy.quickstart_builder import QuickstartBuilder
      config = QuickstartBuilder.build_1p_config()
      self._on_new_game_start(config)
  ```
- [ ] Add `start_quickstart_2p(self)` method
- [ ] Both methods should call `_on_new_game_start(config)`
**Notes:**

#### Task 4.2: Add Menu Buttons [Simple]
**File:** `game/app.py`
**Tests:** Manual - verify buttons appear at top of menu
- [ ] Modify `update_menu_buttons()` (line 122)
- [ ] Add Quickstart 1P button at `HEIGHT // 2 - 250` (above current first button)
- [ ] Add Quickstart 2P button at `HEIGHT // 2 - 180`
- [ ] Shift all existing buttons down by 140px (2 × 70px spacing)
**Notes:**

---

### Phase 5: Implement Design Copying [Medium]
**Objective:** Copy pre-made designs to save folder on quickstart
**Status:** Not Started

#### Task 5.1: Add Design Copy Logic to QuickstartBuilder [Medium]
**File:** `game/strategy/quickstart_builder.py`
**Tests:** `pytest tests/unit/quickstart/test_quickstart_builder.py`
- [ ] Add `copy_quickstart_designs(save_path, empire_id)` method
- [ ] Copy `qs_escort.json` and `qs_complex.json` to `{save_path}/designs/empire_{id}/`
- [ ] Handle both 1P (empire_0 only) and 2P (empire_0 and empire_1) scenarios
**Notes:**

#### Task 5.2: Integrate Design Copy into Game Start [Simple]
**File:** `game/app.py`
**Tests:** Manual - verify designs appear in Design Workshop after quickstart
- [ ] Modify `_on_new_game_start()` or quickstart handlers
- [ ] After `SaveGameService.save_game()` succeeds, call `QuickstartBuilder.copy_quickstart_designs()`
- [ ] Pass `session.save_path` and empire IDs
**Notes:**

---

## Verification Checklist

### After Each Phase
- [ ] Run `pytest tests/unit/quickstart/` - all tests pass
- [ ] No import errors or missing dependencies

### Final Verification
- [ ] Launch game, click "Quickstart 1P" - game starts with 1 player
- [ ] Launch game, click "Quickstart 2P" - game starts with 2 players
- [ ] Check saves folder - timestamped save folders created
- [ ] Open Design Workshop - pre-made designs visible
- [ ] Run full test suite: `pytest tests/unit/` - all pass
- [ ] Verify flag and portrait display correctly in-game

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| | | | |

## Completion Checklist
- [x] Phase 1: Test fixtures created
- [x] Phase 2: Unit tests created and passing
- [x] Phase 3: QuickstartBuilder implemented
- [x] Phase 4: Menu buttons and handlers added
- [x] Phase 5: Design copying implemented
- [x] All tests passing (66 tests)
- [ ] Manual verification complete
- [ ] User verified

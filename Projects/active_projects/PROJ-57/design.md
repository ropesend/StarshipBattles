# PROJ-55: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

<<<<<<< HEAD
### The Problem
`game/ui/screens/test_lab_screen.py` is 4,703 lines with 11 classes and 1 module-level utility function. It is the single largest file in the project (201 KB). All classes are crammed into one module making it impossible to edit one widget without loading the entire file.

### Current File Structure
| Class | Lines | Size | Role |
|-------|-------|------|------|
| `JSONPopup` | 36-139 | ~100 | Modal popup for displaying JSON data |
| `ConfirmationDialog` | 141-289 | ~150 | Confirmation dialog with visual diff |
| `ScrollableJSONViewer` | 291-402 | ~110 | Reusable scrollable JSON panel |
| `ComponentDropdown` | 404-547 | ~140 | Custom dropdown menu for components |
| `ShipPanel` | 549-588 | ~40 | Single ship JSON display panel |
| `TabbedShipPanel` | 590-719 | ~130 | Tabbed multi-ship panel |
| `ComponentPanel` | 721-792 | ~70 | Component dropdown + JSON viewer |
| `TestRunCard` | 794-1165 | ~370 | Test run summary card widget |
| `TestRunDetailsPanel` | 1167-1998 | ~830 | Detailed test results view |
| `ResultsPanel` | 2000-2245 | ~245 | Scrollable test run history |
| `TestLabScreen` | 2247-4703 | ~2460 | Main orchestrator screen |

Module-level: `get_test_data_dir()` (lines 19-33), `logger` (line 16)

### Legacy File
`game/ui/screens/test_lab.py` (189 lines) is a dead legacy implementation from before PROJ-46 naming standardization. Zero imports found anywhere. Safe to delete.
=======
### Current Colonization System

**Flow:** UI → Command → Validation → Execution

**Key Components:**
- **Validation:** [colonize_validator.py](c:\Dev\StarshipBattles\game\strategy\validation\colonize_validator.py) - `ColonizeValidator.validate()`
- **Execution:** [fleet_order_processor.py](c:\Dev\StarshipBattles\game\strategy\engine\fleet_order_processor.py) - `process_colonize()`
- **UI:** [strategy_colonization.py](c:\Dev\StarshipBattles\game\ui\screens\strategy_colonization.py) - `ColonizationSystem`
- **Commands:** [commands.py](c:\Dev\StarshipBattles\game\strategy\engine\commands.py) - `IssueColonizeCommand`, `QueueColonizeMissionCommand`

**Current Behavior:**
- Any fleet can colonize any planet (no restrictions)
- Only checks: planet at fleet location, planet unowned
- Entire fleet consumed on colonization
- Supports "Any Planet" mode (picks first valid candidate)
- No planet type differentiation

**Current Limitations:**
1. No component requirements (any ship can colonize)
2. No planet type restrictions (gas giants colonizable same as terrestrial)
3. Entire fleet consumed (not individual ship)
4. No support for colonization chains with validation
5. No habitability considerations

### Planet System

**11 Planet Types** (defined in `PlanetType` enum):
1. CONTINENTAL - Earth-like
2. ARID - Desert
3. PELAGIC - Ocean
4. MAGMA - Volcanic
5. CRYOPLANET - Ice surface
6. BARREN - Airless rock
7. JOVIAN - Gas giant
8. ICE_GIANT - Ice giant
9. CHTHONIAN - Stripped core
10. ICE_DWARF - Pluto-like
11. PLANETOID - Large asteroid

**Planet Generation:**
- Physics-first approach (mass, radius, temperature, pressure)
- Classification decision tree in [planet_gen.py](c:\Dev\StarshipBattles\game\strategy\data\planet_gen.py)
- Thresholds loaded from [astrophysics.json](c:\Dev\StarshipBattles\data\astrophysics.json) (data-driven)
- Visual mappings in [planet_classifications.json](c:\Dev\StarshipBattles\assets\Images\Stellar Objects\Planets\Planets_V3\planet_classifications.json)

**Current Usage:**
- Visual representation only
- NOT used for colonization restrictions
- NOT used for resource differentiation
- NOT used for strategic value

### Component & Ability System

**Architecture Pattern:**
- Data-driven: Components defined in [components.json](c:\Dev\StarshipBattles\data\components.json)
- Abilities implemented as Python classes
- Registry pattern: [abilities/__init__.py](c:\Dev\StarshipBattles\game\simulation\components\abilities\__init__.py) - `ABILITY_REGISTRY`
- Supports parameterized abilities with type data

**Ability Data Patterns:**
1. **Boolean marker:** `"AbilityName": true`
2. **Simple numeric:** `"AbilityName": 150`
3. **Parameterized object:** `"AbilityName": {"param1": "value", "param2": 10}`
4. **List of instances:** `"AbilityName": [{"resource": "fuel"}, {"resource": "energy"}]`

**Vehicle Type Restrictions:**
- Components specify `"allowed_vehicle_types": ["Ship", "Planetary Complex", ...]`
- Validated by `LayerConstraintRule` in [ship_validator.py](c:\Dev\StarshipBattles\game\simulation\validation\ship_validator.py)

**Layer System:**
- `AbilityLayer.COMBAT` - Real-time tactical combat
- `AbilityLayer.STRATEGIC` - Turn-based strategy map
- `AbilityLayer.BOTH` - Active in both

**Existing Example:** `ResourceHarvesterAbility`
- Takes `resource_type` parameter
- Demonstrates pattern for type-specific components
- Pattern can be reused for planet-type-specific colony pods

### Test Coverage

**Current Tests:**
- **Unit:** [test_colonize_validator.py](c:\Dev\StarshipBattles\tests\unit\strategy\validation\test_colonize_validator.py) - 14 test cases, 266 lines
- **Integration:** [test_colonize_logic.py](c:\Dev\StarshipBattles\tests\integration\strategy\test_colonize_logic.py) - 139 lines
- **Integration:** [test_commands_colonization.py](c:\Dev\StarshipBattles\tests\integration\gameplay_loop\test_commands_colonization.py) - 243 lines
- **UI Tests:** [test_colonization_facade.py](c:\Dev\StarshipBattles\tests\integration\ui\test_colonization_facade.py)

**Coverage Scope:**
- Valid/invalid colonization scenarios
- "Any Planet" mode
- Wrong location failures
- Already-owned planet failures
- Fleet consumption
- Concurrent colonization
- Fleet destroyed between order and execution

**Test Pattern:** TDD with pytest, uses fixtures for galaxy/fleet/empire setup
>>>>>>> c4a0287ba78822f63257ae002dbf9586ca325f08

## Swarm Findings Summary

### Architecture
<<<<<<< HEAD
- **No inheritance** between classes — pure composition pattern
- **No circular dependencies** — clean unidirectional tree
- **Event-driven** — callbacks passed as function parameters (e.g., `on_confirm`, `on_cancel`, `load_callback`)
- **Lazy imports** in TestLabScreen for heavy deps (BattleStateViewer, Validator, tkinter)
- **Central controller** — TestLabUIController manages UI state (external to this file)

### Internal Dependency Graph
```
screen.py ──> dialogs.py (leaf)
          ──> ship_panels.py ──> json_viewer.py (leaf)
          |                  ──> component_dropdown.py (leaf)
          ──> results_panel.py ──> test_run_card.py (leaf)
          ──> test_run_details.py (leaf)
```
5 of 8 modules are leaf nodes (no intra-package dependencies).

### Key Patterns to Reuse
- **Builder package `__init__.py`**: `game/ui/screens/builder/__init__.py` — re-exports key classes using relative imports
- **Formation package `__init__.py`**: `game/ui/screens/formation/__init__.py` — includes docstring, `__all__`, uses absolute imports

### Dependencies & Risks

1. **`get_test_data_dir()` path depth change** — Uses `os.path.dirname(__file__)` with 3 levels of `dirname()`. Moving from `game/ui/screens/` to `game/ui/screens/test_lab/` requires 4 levels. **Mitigation:** Fix in Task 3.1, test thoroughly.

2. **18 `patch()` calls in test files** — All reference `game.ui.screens.test_lab_screen.XXX`. Must update to `game.ui.screens.test_lab.screen.XXX`. **Mitigation:** Exact line numbers mapped.

3. **Patch targets are module-level names** — Tests patch `load_json`, `TestRunner`, `JSONPopup`, `WIDTH`, `HEIGHT` as they're imported into `test_lab_screen`. After decomposition, these names will be imported into `screen.py`, so patches must target `game.ui.screens.test_lab.screen.*`.

### External Import Surface
| Consumer | Import | Lines |
|----------|--------|-------|
| `game/app.py` | `from game.ui.screens.test_lab_screen import TestLabScreen` | 30 |
| `tests/unit/test_lab/test_data_paths.py` | `from game.ui.screens.test_lab_screen import TestLabScreen` | 47, 134, 180, 219 |
| `tests/unit/test_lab/test_data_paths.py` | `from game.ui.screens.test_lab_screen import get_test_data_dir` | 255, 274 |
| `tests/unit/test_lab/test_visual_run.py` | `from game.ui.screens.test_lab_screen import TestLabScreen` | 78 |

No references in `game/ui/__init__.py`, `game/ui/screens/__init__.py`, conftest files, or config files.

### Opportunities Discovered
- `TestLabScreen` at 2460 lines could itself be decomposed in a future project (extract draw methods, test execution logic, event handling)
- Several classes create fonts independently — could share a font cache (out of scope)

## Design Decisions
=======

**Clean Layer Separation:**
- Simulation layer (components/abilities) has no dependencies on Strategy layer
- Strategy layer (validation/execution) depends on Simulation
- UI layer depends on both
- This separation allows us to add colony abilities in Simulation without circular dependencies

**Registry Pattern Everywhere:**
- Components registered via JSON
- Abilities registered via `ABILITY_REGISTRY`
- Planets registered in galaxy with ID-based lookup
- Pattern supports data-driven extensibility

**Two-Phase Validation:**
- **Command time:** `ColonizeValidator.validate()` before adding order to queue
- **Execution time:** Re-validation in `FleetOrderProcessor.process_colonize()`
- This supports our chain validation (validate available pods before queuing)

### Key Patterns to Reuse

- **Parameterized Ability:** [harvester.py:15-25](c:\Dev\StarshipBattles\game\simulation\components\abilities\harvester.py) - `ResourceHarvesterAbility` with `resource_type` parameter - exact pattern for `ColonizePlanet` with `planet_type`
- **Vehicle Type Restriction:** [components.json](c:\Dev\StarshipBattles\data\components.json) - `"allowed_vehicle_types": ["Ship"]` - use for colony pods
- **Layer Specification:** [base.py:45](c:\Dev\StarshipBattles\game\simulation\components\abilities\base.py) - `layer = AbilityLayer.STRATEGIC` - colony abilities strategic-only
- **Fleet Ship Iteration:** [fleet_order_processor.py](c:\Dev\StarshipBattles\game\strategy\engine\fleet_order_processor.py) - iterate `fleet.ships` to find specific ship
- **Validation Result Pattern:** [colonize_validator.py:25-35](c:\Dev\StarshipBattles\game\strategy\validation\colonize_validator.py) - `ValidationResult` with error codes - extend with `NO_COLONY_POD`, `COLONY_POD_EXHAUSTED`

### Dependencies & Risks

1. **Fleet.ships iteration** - Need to verify Fleet class has `ships` attribute and supports iteration/removal
   - Mitigation: Check Fleet data model, add `remove_ship()` method if needed

2. **Component.get_ability()** - Assumption that this method exists for ability lookup
   - Mitigation: Verified in component.py, method exists and returns single ability instance

3. **Test updates** - Existing tests assume entire fleet consumed, will break when we change to single ship
   - Mitigation: Systematic test update, mark as expected changes

4. **Save compatibility** - Old saves won't have colony pods, players won't be able to colonize
   - Mitigation: Acceptable breaking change (clean mechanic redesign)

5. **"Any Planet" mode complexity** - When fleet has multiple pod types and multiple planet types at location
   - Mitigation: Document priority logic (e.g., pick first planet that matches any available pod)

### Opportunities Discovered

- **Habitability System:** Planet type data (temperature, pressure, water) exists but unused - could add habitability scoring later
- **Resource Specialization:** Planet resources currently uniform - could make planet types yield different resource types
- **Facility Restrictions:** Planetary facilities exist - could restrict certain facilities to certain planet types
- **Colony Tiers:** Could have basic vs advanced colony pods (basic CONTINENTAL pod vs Advanced CONTINENTAL Pod with better bonuses)
- **Multi-Component Requirements:** Ability system supports multiple abilities - could require both Colony Pod + Life Support for extreme planets

## Design Decisions

**Core Decisions (from user clarifications):**
1. **All 11 types colonizable from start** - Research gating comes later, keep simple now
2. **Colony pods as ship components** - Designed in workshop, consumed on colonization
3. **11 separate components** - One component per planet type (not single generic with parameter)
4. **Track pods, allow chaining** - System validates available pods before allowing queue

>>>>>>> c4a0287ba78822f63257ae002dbf9586ca325f08
See [decisions.md](decisions.md) for the full log with rationale.

# Core & Engine Legacy Code Audit

## Summary
- **Total issues found:** 2
- **Critical:** 0
- **Major:** 0
- **Minor:** 2
- **Info:** 0

## Analysis Notes

This audit examined `game/core/` (19 production files) and `game/engine/` (3 production files) for:
- Dead code (unused functions, classes, imports)
- Orphaned modules
- Backward compatibility shims
- Commented-out code blocks
- TODO/FIXME/DEPRECATED markers
- Superseded patterns
- Dead feature flags
- Unused parameters

### Overall Assessment
Both `game/core/` and `game/engine/` are **well-maintained** with minimal legacy debt:
- All exported functions are actively used across the codebase
- All exception types (except one) are actively raised/caught
- All error codes are actively used
- No commented-out code blocks found
- No TODO/FIXME/DEPRECATED markers found
- Architecture is clean with clear layer separation

---

## Findings

### Minor Issues

#### MINOR: SimulationException Base Class Unused
**ID:** LEG-001
**Location:** `game/core/exceptions.py:183-189`
**Issue:** The `SimulationException` class is defined but never directly raised in the codebase. All simulation errors use the more specific subclasses `ComponentException` or `FormulaException`.

**Evidence:**
- 0 uses of `raise SimulationException` found
- 0 uses of `except SimulationException` found
- Subclass `ComponentException` is used in 2 locations (game/simulation/components/loading.py)
- Subclass `FormulaException` is used in game/simulation/formulas/ (multiple files)

**Recommendation:**
Remove the unused base class and update imports. Keep `ComponentException` and `FormulaException` as they are actively used. If any code currently catches `SimulationException`, update it to catch the specific subclass instead.

**Effort:** Simple

**Details:**
The exception hierarchy includes a base `SimulationException` that serves no purpose since it's never instantiated. This violates the principle of not keeping unused code paths. The subclasses should be caught directly in their respective layers.

---

#### MINOR: Unused Private Helper Function _hex_round
**ID:** LEG-002
**Location:** `game/core/hex_math.py:177-194`
**Issue:** The `_hex_round()` function is private (single underscore) but is called from multiple functions within the same module. However, this is appropriate internal implementation detail and does NOT constitute dead code—it's a legitimate helper.

**Evidence:**
- Called by `pixel_to_hex()` (line 174)
- Called by `hex_lerp()` (line 267)
- Called by `hex_linedraw()` (line 279)
- Functions are actively used elsewhere in codebase

**Recommendation:**
**NO ACTION REQUIRED.** This is proper encapsulation. The private helper is appropriately used and maintains clean API boundaries.

**Effort:** N/A (No action needed)

**Details:**
Upon further analysis, this is NOT a legacy code issue. The private helper `_hex_round()` is an internal implementation detail that properly encapsulates the complex rounding logic for hex coordinates. It's called from multiple public functions and serves a clear purpose. Keeping private helpers is good design.

---

## Audit Results by File

### game/core/__init__.py
- **Status:** CLEAN
- All 46 exported symbols are actively imported and used elsewhere
- Exports are organized by category with clear comments
- PROJ-113 note correctly documents UIConfig migration to game.ui.config

### game/core/config.py
- **Status:** CLEAN
- All 4 configuration classes (`DisplayConfig`, `AIConfig`, `PhysicsConfig`, `BattleConfig`) are actively used
- All constants are referenced in physics simulation, AI pathfinding, and battle systems

### game/core/constants.py
- **Status:** CLEAN
- All enum classes and constants are actively used
- PROJ-113 comments properly document color/font migration to game.ui.colors
- All 20+ error codes are actively referenced

### game/core/error_codes.py
- **Status:** CLEAN
- All 20 error codes (V001-V099, S001-S099, R001-R099, P001-P005, F001-F004, C001-C005) are actively used
- No unused code categories
- Proper categorization by functional area

### game/core/exceptions.py
- **Status:** MINOR ISSUES (LEG-001)
- 8 of 9 exception classes actively used
- `SimulationException` is never directly raised (only subclasses used)
- Proper exception hierarchy otherwise

### game/core/event_logging.py
- **Status:** CLEAN
- All 3 public functions (`set_event_handler`, `get_event_handler`, `log_event`) actively used
- Proper error handling and logging in event dispatch

### game/core/hex_math.py
- **Status:** CLEAN
- All 11 public functions actively used across strategy layer
- `HexCoord` class with proper __slots__ optimization
- Helper functions used by pathfinding, planet generation, storm generation, galaxy generation
- Private `_hex_round()` is appropriate encapsulation

### game/core/input_actions.py
- **Status:** CLEAN
- All 31 input action enums actively used by keybinding system
- All action display names in `ACTION_DISPLAY_NAMES` dict are complete
- All action groups in `ACTION_GROUPS` properly organized

### game/core/json_utils.py
- **Status:** CLEAN
- All 3 public functions (`load_json`, `load_json_required`, `save_json`) actively used
- Proper error handling with consistent logging
- Canonical location for JSON file operations

### game/core/math.py
- **Status:** CLEAN
- `Vector2` class actively used throughout physics and UI code (200+ uses)
- All utility functions (`clamp`, `lerp`, `angle_diff`) actively used
- Proper pygame compatibility in Vector2 implementation

### game/core/paths.py
- **Status:** CLEAN
- All path constants actively used for asset loading, save files, logs
- Proper project root detection with error handling
- Class methods for Path objects properly used in tests

### game/core/profiling.py
- **Status:** CLEAN
- `Profiler` singleton properly implemented with SingletonMeta
- Decorator `@profile_action` and context manager `profile_block` available for use
- Save/load functionality for profiling data history

### game/core/protocols.py
- **Status:** CLEAN
- All 24 protocols (`IRegistryProvider`, `IFleet`, `IPlanet`, `ICombatant`, etc.) actively used
- All TypeGuard functions (`is_fleet`, `is_planet`, `is_combatant`, etc.) properly implemented
- Proper type-safe duck typing replacement for hasattr patterns

### game/core/registry.py
- **Status:** CLEAN
- `GameRegistries` container properly used for DI
- `RegistryManager` singleton properly maintained
- Both provider implementations (`DefaultRegistryProvider`, `TestRegistryProvider`) actively used
- Module-level helpers (`get_default_registry_provider`, `freeze_registry`, `clear_registry`) properly used

### game/core/singleton.py
- **Status:** CLEAN
- `SingletonMeta` metaclass used by 7+ classes throughout codebase
- Thread-safe double-checked locking properly implemented
- Reset functionality used in test isolation

### game/core/strategy_metadata.py
- **Status:** CLEAN
- `StrategyMetadataService` singleton properly used by AI and UI layers
- All public methods actively used for strategy name resolution

### game/core/validation.py
- **Status:** CLEAN
- `ValidationResult` class widely used (50+ uses) across all layers
- `IValidationRule` protocol properly implemented by validators
- Factory methods (`success()`, `error()`, `with_errors()`) actively used

### game/core/validation_helpers.py
- **Status:** CLEAN
- All 6 validation helpers actively used in from_dict deserialization
- Proper exception chaining and context information
- No dead helpers

### game/engine/__init__.py
- **Status:** CLEAN
- Exports 3 core engine classes: `PhysicsBody`, `CollisionSystem`, `SpatialGrid`
- All re-exports properly used in battle system

### game/engine/collision.py
- **Status:** CLEAN
- `CollisionSystem` class properly stateless and used in battle_engine.py
- Both public methods actively used:
  - `process_beam_attack()` - raycasting for beam weapons
  - `process_ramming()` - ship collision damage
- Proper sphere-ray intersection implementation with detailed comments

### game/engine/physics.py
- **Status:** CLEAN
- `PhysicsBody` base class provides proper entity physics
- All public methods and properties properly used
- Proper drag model implementation with per-tick falloff
- Note correctly documents that Ship class overrides update() with cycle-based mixins

### game/engine/spatial.py
- **Status:** CLEAN
- `SpatialGrid` class provides efficient O(1) hash-based spatial lookup
- All public methods (`clear`, `insert`, `query_radius`) properly used in battle system
- Proper cell-based bucketing for neighbor queries

---

## Top 5 Priority Issues

1. **LEG-001: SimulationException is Never Raised** [MINOR]
   - Base exception class with no usage
   - Should be removed, subclasses used instead
   - Effort: Simple (~5 minutes)

2. *No other significant legacy code issues identified*
   - All other code is actively used and properly maintained
   - Architecture is clean with proper layer separation
   - All dead code paths that existed have been previously removed (see PROJ-58 notes in memory)

---

## Quality Observations

### Strengths
1. **Clean Architecture:** Proper layer separation between core, engine, simulation, strategy, and UI
2. **Type Safety:** Extensive use of protocols and type hints throughout
3. **Error Handling:** Comprehensive exception hierarchy with error codes
4. **Documentation:** Clear docstrings and architectural notes (PROJ references)
5. **Testing:** Singleton reset and clear functions properly support test isolation
6. **No Dark Code:** No commented-out code blocks or feature flags found
7. **Active Maintenance:** PROJ references show ongoing refactoring efforts

### Recommendations
1. Remove unused `SimulationException` base class (LEG-001)
2. Continue current project velocity - codebase is well-maintained
3. Keep protocol-based architecture pattern (not hasattr checks)
4. Continue using dependency injection for registries (PROJ-27 implementation)

---

## Audit Methodology

**Coverage:** 22 production Python files examined
- 19 files in `game/core/`
- 3 files in `game/engine/`

**Techniques Used:**
1. Full file content review for each module
2. Grep searches for function/class usage across `game/` directory
3. Exception class usage verification
4. Error code reference counting
5. Dead code pattern detection (TODO/FIXME/commented code)
6. Orphaned module detection
7. Unused parameter analysis

**Exclusions:**
- Test files (tests/ directory) - as requested
- Data files (JSON, configs) - analyzed only for structure

---

**Report Generated:** 2026-02-27 14:15:04
**Audit Version:** 1.0

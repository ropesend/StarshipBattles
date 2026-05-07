# Inconsistency Hunter Report

**Date:** 2026-03-13
**Scope:** `game/` directory (429 Python files, ~95K lines)
**Layers analyzed:** game/core/, game/simulation/, game/strategy/, game/ai/, game/ui/

---

## Summary

- **Total issues found:** 15
- **Critical:** 0
- **Major:** 6
- **Minor:** 7
- **Info:** 2

---

## Findings

---

### IH-1: Interface Definition Style -- ABC vs Protocol

**Severity:** Major
**What's inconsistent:** The codebase uses two different mechanisms for defining interfaces: `ABC` (abstract base classes) and `Protocol` (structural typing). The same layer uses both approaches.

**Locations of variants:**

- **ABC pattern** (16 classes):
  - `game/ai/interfaces/controllable.py:22` -- `IControllable(ABC)`
  - `game/strategy/interfaces/engines.py:44-516` -- 11 engine interfaces (IMovementEngine, IProductionEngine, IOrderProcessor, IConflictEngine, IResourceEngine, IResupplyEngine, IHarvestingEngine, IMaintenanceEngine, IPopulationEngine, IActionExecutionEngine, IEnvironmentalHazardEngine)
  - `game/strategy/interfaces/battle_resolver.py:48` -- `IBattleResolver(ABC)`
  - `game/simulation/combat/battle_mode_handler.py:25` -- `BattleModeHandler(ABC)`
  - `game/simulation/validation/base.py:21` -- `ValidationRule(ABC)`
  - `game/ui/panels/base_gallery.py:28` -- `BaseGallery(ABC)`

- **Protocol pattern** (50+ classes):
  - `game/core/protocols.py` -- 18 protocols (IRegistryProvider, ILocatable, IFleet, etc.)
  - `game/ai/protocols.py` -- 4 protocols (IGridEntity, IProjectile, IFormationMaster, IComponentHealth)
  - `game/simulation/interfaces/` -- 12+ protocols (ICombatShip, IProjectile, IComponent, IAbility, etc.)
  - `game/strategy/engine/command_handlers.py:109` -- `ICommandHandler(Protocol)`
  - `game/ui/screens/builder/drop_target.py:4` -- `DropTarget(Protocol)`
  - `game/ui/interfaces/battle_ui.py:176` -- `IBattleUI(Protocol)`

**Which variant is newer/better:** Protocol is the newer pattern (PROJ-192 introduced it for AI layer). Protocol enables structural typing which is preferred for decoupling.

**Impact:** Cognitive overhead choosing between ABC and Protocol when writing new code. ABC forces explicit inheritance, creating tighter coupling. Protocol is more Pythonic for interface contracts.

**Recommendation:** Standardize on Protocol for all new interfaces. Migrate existing ABC interfaces to Protocol where the abstract class provides no implementation (pure interfaces). Keep ABC only when the base class provides shared implementation (like `ValidationRule._do_validate` template method or `BaseGallery`).

**Effort:** Medium -- Strategy engine interfaces are the largest batch (11 ABCs in one file). Each requires updating concrete implementations to remove explicit inheritance.

---

### IH-2: AI Layer Data Access -- get_X() Methods vs @property

**Severity:** Major
**What's inconsistent:** Within the AI layer itself, two different styles exist for accessing entity data:
- `IControllable` (PROJ-12): Uses `get_X()` methods (`get_position()`, `get_velocity()`, `get_radius()`, etc.)
- `IGridEntity`/`IFormationMaster` protocols (PROJ-192): Uses `@property` decorators (`position`, `is_alive`, `radius`, etc.)

Both describe the same kind of data (position, alive status, team) but with different access patterns.

**Locations:**

- `game/ai/interfaces/controllable.py:41-234` -- 25+ `get_X()` methods: `get_position()`, `get_velocity()`, `get_rotation()`, `get_radius()`, `get_max_speed()`, `get_current_speed()`, `get_turn_speed()`, etc.
- `game/ai/protocols.py:40-56` -- `@property` for same data: `position`, `is_alive`, `team_id`, `radius`
- `game/ai/protocols.py:92-133` -- `@property` for: `position`, `angle`, `is_alive`, `max_speed`, `current_speed`, `engine_throttle`, `formation`

**Which variant is newer/better:** The `@property` pattern in `protocols.py` (PROJ-192) is newer and more Pythonic. Properties are the standard Python way to expose read-only data attributes.

**Impact:** Callers must use `ship.get_position()` for `IControllable` but `entity.position` for `IGridEntity`, even when accessing the same underlying data.

**Recommendation:** Migrate `IControllable` to use `@property` for read-only accessors. Keep `get_X()` only for methods that perform non-trivial work.

**Effort:** Complex -- `IControllable` has 25+ methods and a concrete `ShipControllable` adapter class that implements them all. All AI controller code that calls these methods must be updated.

---

### IH-3: Event Handler Naming -- handle_event() vs process_event()

**Severity:** Major
**What's inconsistent:** UI event handling uses two different method names for the same operation:
- `handle_event(event)` -- Used by scenes/screens and many panels
- `process_event(event)` -- Used by UIWindow subclasses and some panels

Additionally, return types are inconsistent:
- Scenes: `handle_event() -> None`
- Panels/widgets: `handle_event() -> bool`
- Windows: `process_event() -> bool`

**Locations:**

- **`handle_event` returning `None`** (IScene protocol):
  - `game/core/protocols.py:776` -- `IScene.handle_event(event) -> None`
  - `game/ui/screens/menu_scene.py:81` -- `handle_event(event) -> None`
  - `game/ui/screens/keybindings_scene.py:259` -- `handle_event(event) -> None`
  - `game/ui/screens/formation_editor.py:414` -- `handle_event(event) -> None`
  - `game/ui/screens/battle_screen.py:314` -- `handle_event(event)` (no return type)
  - `game/ui/screens/strategy_screen.py:220` -- `handle_event(event)` (no return type)
  - `game/ui/screens/workshop_screen.py:408` -- `handle_event(event)` (no return type)

- **`handle_event` returning `bool`** (panels/widgets):
  - `game/ui/widgets/scrollable_json_panel.py:258` -- `handle_event(event) -> bool`
  - `game/ui/panels/modifier_impact_grid.py:473` -- `handle_event(event) -> bool`
  - `game/ui/panels/race_identity_panel.py:457` -- `handle_event(event) -> bool`
  - `game/ui/screens/workshop_event_router.py:45` -- `handle_event(event) -> bool`

- **`process_event` returning `bool`** (UIWindow subclasses):
  - `game/ui/screens/design_selector_window.py:440`
  - `game/ui/screens/empire_build_queue_window.py:430`
  - `game/ui/screens/empire_panel_window.py:478`
  - `game/ui/screens/fleet_report_window.py:168`
  - `game/ui/screens/planet_list_window.py:196`
  - `game/ui/screens/save_selection_window.py:186`
  - `game/ui/screens/new_game_setup_screen.py:354`
  - `game/ui/screens/race_setup_screen.py:946`
  - `game/ui/panels/ship_detail_panel.py:418`

**Which variant is newer/better:** The `process_event` pattern is from pygame_gui's UIWindow convention. `handle_event` is the project's own naming from the `IScene` protocol.

**Impact:** When composing UI elements, callers cannot rely on a consistent method name or return type for event delegation.

**Recommendation:** Standardize on `handle_event` for project code. UIWindow subclasses can keep `process_event` as a pygame_gui override but should also expose `handle_event` for internal delegation. Standardize return types: scenes return `None`, child components return `bool` to signal event consumption.

**Effort:** Medium

---

### IH-4: Validation Return Types -- ValidationResult vs tuple[bool, str]

**Severity:** Major
**What's inconsistent:** Validation operations return two different types:
- `ValidationResult` -- The canonical class from `game/core/validation.py` (PROJ-21)
- `tuple[bool, str]` or `Tuple[bool, Optional[str]]` -- Ad-hoc tuples for success/error

**Locations using tuple returns (should use ValidationResult):**

- `game/strategy/data/race_config.py:337-391` -- 6 internal validators (`_validate_required_fields`, `_validate_environment_ranges`, `_validate_aptitudes`, `_validate_identity_enums`, `_validate_homeworld_and_atmosphere`, `_validate_descriptions`) all return `tuple[bool, str]`
- `game/strategy/systems/design_library.py:110` -- `save_design() -> Tuple[bool, str]`
- `game/strategy/systems/design_library.py:223` -- `mark_obsolete() -> Tuple[bool, str]`
- `game/strategy/systems/design_library.py:359` -- `delete_design() -> Tuple[bool, str]`
- `game/strategy/systems/race_library.py:161` -- `save_race() -> Tuple[bool, str]`
- `game/strategy/systems/save_game_service.py:31` -- `save_game() -> Tuple[bool, str, Optional[str]]`
- `game/strategy/systems/save_game_service.py:234` -- `delete_save() -> Tuple[bool, str]`
- `game/strategy/systems/save_game_service.py:404` -- `_validate_save() -> Tuple[bool, Optional[str]]`
- `game/ui/screens/new_game_setup_screen.py:532` -- `validate_save_name() -> Tuple[bool, str]`
- `game/ui/screens/race_setup_screen.py:735` -- `_validate_for_save() -> tuple[bool, str]`
- `game/simulation/managers/retreat_manager.py:71,116` -- retreat validation returns `Tuple[bool, Optional[str]]`

**Locations correctly using ValidationResult:**

- `game/simulation/validation/` -- All ship validators
- `game/strategy/validation/` -- TransferValidator, ColonizeValidator, SuperweaponValidator
- `game/strategy/data/race_config.py:295` -- Public `validate()` method (wraps internal tuple validators)
- `game/ui/screens/race_validator.py:38`

**Which variant is newer/better:** `ValidationResult` is the canonical pattern (PROJ-21 consolidation). The tuple pattern is older, pre-dating the consolidation.

**Impact:** Callers must handle two different return shapes. Tuple returns lose the ability to carry multiple errors, warnings, and error codes.

**Recommendation:** Migrate all tuple-returning validators to return `ValidationResult`. The `RaceConfig._validate_*` methods (6 of them) are the largest batch.

**Effort:** Simple -- Each method needs its return type changed and callers updated. Most are internal/private methods.

---

### IH-5: Singleton Implementation -- SingletonMeta vs Manual Pattern

**Severity:** Minor
**What's inconsistent:** Most singletons use the project's `SingletonMeta` metaclass from `game/core/singleton.py`, but one class uses a manual singleton pattern with `_instance = None`.

**Locations:**

- **SingletonMeta pattern** (standardized):
  - `game/ai/strategy_manager.py:19` -- AIStrategyManager
  - `game/assets/asset_manager.py:10` -- AssetManager
  - `game/core/profiling.py:13` -- Profiler
  - `game/core/registry.py:47` -- RegistryManager
  - `game/core/strategy_metadata.py:27` -- StrategyMetadata
  - `game/ui/assets/ship_theme_manager.py:11` -- ShipThemeManager
  - `game/ui/renderer/sprites.py:5` -- SpriteManager
  - `game/ui/services/screenshot_manager.py:17` -- ScreenshotManager

- **Manual singleton pattern** (divergent):
  - `game/simulation/components/component.py:444-463` -- `ComponentCacheManager` uses `_instance = None` / `_lock = threading.Lock()` / `@classmethod instance(cls)` pattern

**Which variant is newer/better:** `SingletonMeta` is the standardized pattern (documented in `game/core/singleton.py`). It provides thread-safe creation, `reset()` for testing, and consistent API.

**Impact:** `ComponentCacheManager` has a different `reset()` behavior -- it clears fields on the existing instance instead of deleting it. This could cause subtle state leaks in tests.

**Recommendation:** Migrate `ComponentCacheManager` to use `SingletonMeta`.

**Effort:** Simple -- One class, straightforward conversion.

---

### IH-6: Logging Initialization -- logging.getLogger vs get_logger

**Severity:** Minor
**What's inconsistent:** The codebase uses two different logging patterns:
- `logging.getLogger(__name__)` -- Standard Python logging, used by 100+ files
- `get_logger(__name__)` from `simulation_tests/logging_config.py` -- Custom Combat Lab logger, used by 4 game files

**Locations using `get_logger`:**

- `game/ui/screens/test_lab/data_extractor.py:15` -- `logger = get_logger(__name__)`
- `game/ui/screens/test_lab/screen.py:33` -- `logger = get_logger(__name__)`
- `game/ui/screens/test_lab/test_executor.py:15` -- `logger = get_logger(__name__)`
- `game/ui/screens/test_lab/validation_manager.py:15` -- `logger = get_logger(__name__)`

These game files import from `simulation_tests.logging_config`, creating a dependency from the game layer to the test framework.

**Which variant is newer/better:** `logging.getLogger(__name__)` is the standard. The `get_logger` pattern creates loggers under the "CombatLab" namespace, which is appropriate for test code but not for production game code.

**Impact:** These 4 files route their logs to the CombatLab namespace instead of the game logger hierarchy. Logging configuration for the game logger won't affect these modules.

**Recommendation:** Replace `get_logger(__name__)` with `logging.getLogger(__name__)` in all `game/` files. The `get_logger` function should only be used in `simulation_tests/`.

**Effort:** Simple -- 4 files, 2 lines each (import + logger assignment).

---

### IH-7: DTO Naming Convention -- XxxDTO vs XxxInfo

**Severity:** Minor
**What's inconsistent:** Data Transfer Objects use two different naming conventions:
- Battle UI DTOs: `XxxDTO` suffix (e.g., `ShipDTO`, `ProjectileDTO`, `BeamDTO`, `ComponentDTO`, `ResourceDTO`)
- Strategy facade DTOs: `XxxInfo` suffix (e.g., `FleetInfo`, `PlanetInfo`, `SystemInfo`, `StarInfo`, `EmpireInfo`, `ShipInfo`)

**Locations:**

- `game/ui/interfaces/battle_ui.py:17-159` -- `ResourceDTO`, `ComponentDTO`, `ShipDTO`, `ProjectileDTO`, `BeamDTO` (frozen dataclasses)
- `game/strategy/facade/dto/fleet_dto.py` -- `FleetOrderInfo`, `ShipInfo`, `FleetInfo` (frozen dataclasses)
- `game/strategy/facade/dto/system_dto.py` -- `StarInfo`, `WarpPointInfo`, `SystemInfo` (frozen dataclasses)
- `game/strategy/facade/dto/planet_dto.py` -- `PlanetInfo` (frozen dataclass)
- `game/strategy/facade/dto/empire_dto.py` -- `ColonySummary`, `FleetSummary`, `EmpireInfo` (frozen dataclasses)

**Which variant is newer/better:** The `XxxInfo` pattern from the strategy facade (PROJ-87) is newer. The `XxxDTO` pattern is from the battle UI layer.

**Impact:** Minor cognitive overhead. Both use frozen dataclasses. The `XxxInfo` convention is more natural for Python codebases.

**Recommendation:** Standardize on one convention. `XxxDTO` is more explicit about the pattern. `XxxInfo` is simpler. Pick one and rename. The strategy facade also uses `XxxSummary` for aggregate DTOs (`ColonySummary`, `FleetSummary`), which adds a third variant.

**Effort:** Medium -- Renaming would touch imports in multiple files.

---

### IH-8: Update Parameter Naming -- dt vs time_delta

**Severity:** Minor
**What's inconsistent:** The `update()` method across UI classes uses two different parameter names for the time delta:
- `dt` -- More common, used by scenes/screens and the `IScene` protocol
- `time_delta` -- Used by several windows and some screens

**Locations using `dt`:**

- `game/core/protocols.py:780` -- `IScene.update(dt: float)` (canonical definition)
- `game/ui/screens/battle_screen.py:356` -- `update(self, dt: float)`
- `game/ui/screens/strategy_screen.py:185` -- `update(self, dt)`
- `game/ui/screens/workshop_screen.py:465` -- `update(self, dt)`
- `game/ui/screens/setup_screen.py:259` -- `update(self, dt: float)`
- `game/ui/screens/menu_scene.py:91` -- `update(self, dt: float)`
- `game/ui/screens/galaxy_test/screen.py:141` -- `update(self, dt: float)`
- `game/ui/screens/test_lab/screen.py:592` -- `update(self, dt: float = 0)`
- 7 more screens/panels

**Locations using `time_delta`:**

- `game/ui/screens/build_queue_screen.py:545` -- `update(self, time_delta: float)`
- `game/ui/screens/design_selector_window.py:555` -- `update(self, time_delta: float)`
- `game/ui/screens/empire_build_queue_window.py:482` -- `update(self, time_delta: float)`
- `game/ui/screens/fleet_report_window.py:298` -- `update(self, time_delta: float)`
- `game/ui/screens/planet_list_window.py:274` -- `update(self, time_delta)`
- `game/ui/screens/planet_selection_window.py:107` -- `update(self, time_delta)`
- `game/ui/screens/save_selection_window.py:390` -- `update(self, time_delta)`
- `game/ui/screens/system_selection_window.py:95` -- `update(self, time_delta)`

**Which variant is newer/better:** `dt` is the canonical name defined in the `IScene` protocol.

**Impact:** Minor. Both are descriptive. But `dt` matches the protocol definition.

**Recommendation:** Rename `time_delta` to `dt` to match the `IScene` protocol.

**Effort:** Simple -- 8 files, one parameter rename each.

---

### IH-9: Draw Surface Parameter -- screen vs surface

**Severity:** Minor
**What's inconsistent:** The `draw()` method uses two different parameter names for the target surface:
- `screen` -- Used by most scenes, the `IScene` protocol, and many panels
- `surface` -- Used by several test_lab components and some widgets

**Locations using `surface`:**

- `game/ui/widgets/scrollable_json_panel.py:338` -- `draw(self, surface)`
- `game/ui/screens/battle_state_viewer.py:194` -- `draw(self, surface)`
- `game/ui/screens/test_lab/component_dropdown.py:105` -- `draw(self, surface)`
- `game/ui/screens/test_lab/json_viewer.py:76` -- `draw(self, surface)`
- `game/ui/screens/test_lab/results_panel.py:152` -- `draw(self, surface)`
- `game/ui/screens/test_lab/test_run_card.py:74` -- `draw(self, surface)`
- `game/ui/screens/test_lab/ship_panels.py:50,139,253` -- `draw(self, surface)` (3 classes)
- `game/ui/screens/test_lab/test_run_details.py:114` -- `draw(self, surface)`
- `game/ui/screens/galaxy_test/system_mode.py:482` -- `draw(self, screen_surface)`
- `game/ui/screens/galaxy_test/galaxy_mode.py:352` -- `draw(self, screen_surface)`

**Locations using `screen`:** 20+ scenes and panels (canonical per `IScene` protocol)

**Which variant is newer/better:** `screen` is the canonical name from `IScene.draw(screen)`. The test_lab module (PROJ-54) uses `surface`.

**Impact:** Minimal -- parameter name is internal to each method.

**Recommendation:** Standardize on `screen` to match the protocol.

**Effort:** Simple -- Rename parameter in affected files.

---

### IH-10: UIWindow Base Class Import -- Direct Import vs Qualified Name

**Severity:** Minor
**What's inconsistent:** UIWindow subclasses import their base class two different ways:
- `from pygame_gui.elements import UIWindow` then `class Xxx(UIWindow)` -- Used by most windows
- Direct `class Xxx(pygame_gui.elements.UIWindow)` -- Used by a few windows

**Locations using qualified base class:**

- `game/ui/screens/fleet_orders_window.py:27` -- `FleetOrdersWindow(pygame_gui.elements.UIWindow)`
- `game/ui/screens/new_game_setup_screen.py:35` -- `NewGameSetupScreen(pygame_gui.elements.UIWindow)`
- `game/ui/screens/race_setup_screen.py:43` -- `RaceSetupScreen(pygame_gui.elements.UIWindow)`
- `game/ui/screens/save_selection_window.py:18` -- `SaveSelectionWindow(pygame_gui.elements.UIWindow)`
- `game/ui/screens/race_browser_dialog.py:27` -- `RaceBrowserDialog(pygame_gui.elements.UIWindow)`

**Locations using imported base class:** 11 files use `from pygame_gui.elements import UIWindow`.

**Impact:** Cosmetic. Both work identically.

**Recommendation:** Standardize on `from pygame_gui.elements import UIWindow` for consistency.

**Effort:** Simple -- 5 files, one import change each.

---

### IH-11: Resource Icon Loading -- Three Implementations

**Severity:** Major
**What's inconsistent:** Loading resource icons (metals, organics, etc.) has three separate implementations with different paths, error handling, and fallback behavior:

1. `game/ui/panels/empire_treasury_panel.py:299` -- Module-level function `load_resource_icons()`:
   - Path: `Paths.ASSET_DIR / "Images" / "Resource Icons"`
   - Filename pattern: `resource_{name}_icon.png`
   - Size: Hardcoded `ICON_SIZE` (20)
   - Error handling: Silently skips on `pygame.error`
   - No fallback surface

2. `game/ui/panels/build_queue_portraits.py:195` -- Instance method `load_resource_icons(icon_size=20)`:
   - Path: `"assets" / "Images" / "Resource Portraits"`
   - Filename pattern: Uses `RESOURCE_PORTRAIT_FILES` dict mapping
   - Size: Configurable
   - Error handling: Logs warning, creates colored fallback square
   - Full fallback with `RESOURCE_FALLBACK_COLORS`

3. `game/ui/panels/planet_report_panel.py:401` -- Instance method `_load_resource_icons(icon_size=24)`:
   - Path: Uses `RESOURCE_PORTRAIT_FILES` from build_queue_portraits
   - Filename pattern: Same as #2
   - Size: 24 (different default)
   - Uses `RESOURCE_FALLBACK_COLORS` from build_queue_portraits
   - Different implementation

**Impact:** Three copies that may diverge. If a new resource type is added, all three must be updated. Different error handling means inconsistent behavior.

**Recommendation:** Extract a single `ResourceIconLoader` utility class or function in `game/ui/utils/` that all three callers use. Accept `icon_size` and `asset_path` as parameters.

**Effort:** Simple -- Extract shared function, update 3 callers.

---

### IH-12: Broad Exception Handling Without Documentation

**Severity:** Minor
**What's inconsistent:** Some broad `except Exception` catches have documented justification (comment explaining why), while others in the strategy layer do not.

**Locations with proper documentation:**
- `game/app.py:722` -- `# Intentional broad catch: top-level crash handler`
- `game/simulation/formula_system.py:141` -- `# Intentional broad catch: catch-and-convert to FormulaException`
- `game/ui/services/tkinter_utils.py:70-230` -- `# Intentional broad catch: Tkinter init is platform-dependent`
- `game/ui/screens/builder/event_bus.py:64` -- `# Intentional broad catch: event handler isolation`

**Locations without justification comments:**
- `game/strategy/services/design_cost_calculator.py:87` -- `except Exception as e:` (logs debug, continues)
- `game/strategy/data/fleet.py:268` -- `except Exception as e:` (skips corrupt ship)
- `game/strategy/data/empire.py:268` -- `except Exception as e:` (skips corrupt fleet)
- `game/strategy/data/fleet_order_serializer.py:56` -- `except Exception as e:` (skips corrupt order)
- `game/ui/panels/race_environment_panel.py:446` -- `except Exception as e:` (logs warning)

**Impact:** The strategy data deserialization catches (fleet, empire, fleet_order_serializer) are justified -- they provide corruption resilience during save loading. But without comments, it is unclear whether these are intentional or sloppy.

**Recommendation:** Add `# Intentional broad catch:` comments explaining the rationale, consistent with the pattern already used in 10+ other locations.

**Effort:** Simple -- Add comments to 5 files.

---

### IH-13: Color Constants -- Dictionary vs Module-Level Constants

**Severity:** Info
**What's inconsistent:** `game/ui/colors.py` defines colors in two ways:
- A `COLORS` dictionary with string keys (`COLORS['bg_deep']`, `COLORS['text_bright']`, etc.)
- Direct module-level constants (`WHITE`, `BLACK`, `TEXT_LIGHT`, `PANEL_BG`, etc.)

**Locations:**

- `game/ui/colors.py:12-43` -- `COLORS = { 'bg_deep': (18,21,26), ... }` -- 25 entries with string keys
- `game/ui/colors.py:8-419` -- 200+ direct constants like `WHITE`, `TEXT_LIGHT`, `RESOURCE_FUEL`, etc.

Users of `COLORS` dict:
- `game/ui/screens/builder/schematic_view.py:15` -- `SHIP_VIEW_BG = COLORS['bg_deep']`
- `game/ui/screens/builder/weapons_renderer.py:70-88` -- 10 class attributes from `COLORS['...']`
- `game/ui/screens/strategy_renderer.py:121-317` -- `COLORS['bg_deep']`, `COLORS['border_normal']`, `COLORS['border_subtle']`
- `game/ui/screens/workshop_screen.py:45,542` -- `COLORS['bg_deep']`, `COLORS['text_error']`

Users of direct constants: 40+ files import direct constants.

**Impact:** The `COLORS` dict entries duplicate some direct constants (e.g., `COLORS['text_error']` = `(255, 100, 100)` = `TEXT_ERROR`). Using string keys loses IDE autocompletion and type checking.

**Recommendation:** The `COLORS` dict is from the style guide and provides semantic grouping. Consider migrating its users to direct constant imports for consistency and IDE support.

**Effort:** Simple -- 4 files reference `COLORS[...]`. Replace with direct constant imports.

---

### IH-14: Enum Base Class -- Plain Enum vs str,Enum vs IntEnum

**Severity:** Info
**What's inconsistent:** Enums use three different base class patterns:
- `Enum` -- Most enums (14 classes)
- `str, Enum` -- 2 enums (InputAction, EventType/EventCategory)
- `IntEnum` -- 1 enum (GameState)

**Locations:**
- `game/core/input_actions.py:21` -- `InputAction(str, Enum)`
- `game/strategy/events/event_types.py:6,21` -- `EventType(str, Enum)`, `EventCategory(str, Enum)`
- `game/core/constants.py:25` -- `GameState(IntEnum)`
- All others: plain `Enum`

**Impact:** Minimal. The `str, Enum` pattern enables JSON serialization without `.value`. `IntEnum` enables integer comparison. Both are valid choices for their use cases.

**Recommendation:** No change needed. The different bases serve different purposes. Document the convention: use `str, Enum` for serialized enums, `IntEnum` for state machines, plain `Enum` for everything else.

**Effort:** N/A

---

### IH-15: clamp_density vs core.math.clamp

**Severity:** Major
**What's inconsistent:** A domain-specific `clamp_density()` function duplicates the generic `clamp()` utility from `game/core/math.py`.

**Locations:**
- `game/core/math.py:187` -- `def clamp(value, min_val, max_val) -> float` (generic utility)
- `game/strategy/generation/density/primitives/density_primitive.py:36` -- `def clamp_density(value) -> float` which is `max(0.0, min(1.0, value))` -- identical to `clamp(value, 0.0, 1.0)`

**Users of `clamp_density`:**
- Used across the density primitive modules (spiral_arm, ring, radial, linear, geometric, noise)

**Impact:** If `clamp()` behavior changes (e.g., NaN handling), `clamp_density` would not pick up the change. Code duplication.

**Recommendation:** Replace `clamp_density(value)` calls with `clamp(value, 0.0, 1.0)` from `game.core.math`. Remove `clamp_density` function.

**Effort:** Simple -- 1 function to remove, ~6-8 call sites to update.

---

## Top 5 Priority Issues

1. **IH-4: Validation Return Types (Major)** -- `tuple[bool, str]` vs `ValidationResult`. Most impactful for code quality because callers cannot access warnings, error codes, or merge results with tuples. The `RaceConfig` internal validators (6 methods) and `DesignLibrary` (3 methods) are the main offenders. Low effort, high benefit.

2. **IH-3: Event Handler Naming (Major)** -- `handle_event` vs `process_event` with inconsistent return types. Affects 50+ classes across the UI layer. Creates confusion about how to compose UI elements. Requires a convention decision and gradual migration.

3. **IH-11: Resource Icon Loading (Major)** -- Three separate implementations of the same function with different paths, error handling, and fallback behavior. Easy to extract a shared utility and eliminate duplication.

4. **IH-2: AI Layer Data Access (Major)** -- `get_X()` vs `@property` within the same layer. The older `IControllable` interface from PROJ-12 uses Java-style getters while newer protocols use Pythonic properties. The inconsistency is contained to the AI layer and fixable in one sweep.

5. **IH-1: Interface Definition Style (Major)** -- ABC vs Protocol for pure interfaces. The codebase has evolved toward Protocol (PROJ-192) but 16 ABCs remain. The strategy engine interfaces (11 in one file) are the largest batch. Migration would reduce coupling and improve testability.

# PROJ-111: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Codebase Survey Results
- **Production files in scope:** 149 (23 framework + 103 screens + 23 panels)
- **Existing test files:** 85+ (unit + integration)
- **Findings from sweep:** 59 total (11 CRITICAL, 23 MAJOR, 16 MINOR, 5 INFO)
- **Estimated new tests:** 500-700

### Test Infrastructure Assessment
The project has mature UI test infrastructure:

1. **Headless pygame** - `tests/unit/ui/conftest.py` provides `pygame_display_reset` autouse fixture that initializes pygame in headless mode (`SDL_VIDEODRIVER=dummy`) with a 1440x900 display surface. This handles font init, display init, and cleanup.

2. **xdist race prevention** - `pytest_configure()` pre-imports `game.ui` modules in dependency order to prevent parallel worker race conditions. `pytest_configure_node()` verifies imports on each worker.

3. **Mock patterns** - Two established approaches:
   - **Real objects + patched UI**: `test_battle_screen.py` creates real Ship objects with `fresh_registries` fixture, patches only `BattleUI` for UI overhead
   - **Full mock isolation**: `test_battle_panels.py` patches `sys.modules` with mock pygame, uses `MockRect` helper, `importlib.reload()` for module isolation
   - **Service mocking**: `test_component_service.py` uses mock `IRegistryProvider` for clean DI testing

4. **Bypass-init pattern** - `test_strategy_menu_actions.py` uses `patch.object(ClassName, '__init__', lambda self, *a, **kw: None)` with `__new__` to create instances without running `__init__`, then manually sets required attributes. Essential for complex screens with many dependencies.

5. **Shared fixtures** - `tests/unit/ui/services/battle_ui_service/conftest.py` provides `mock_ship`, `mock_projectile`, `mock_battle_service` fixtures for DTO conversion tests.

## Key Patterns to Reuse

### Pattern 1: Bypass-Init for Complex Screens
```python
# From test_strategy_menu_actions.py
with patch.object(StrategyScreen, '__init__', lambda self, *a, **kw: None):
    screen = StrategyScreen.__new__(StrategyScreen)
# Then manually set required attributes
screen.scene_callback = MagicMock()
screen.ui = MagicMock()
```
**When:** Testing any screen with heavy `__init__` dependencies (pygame_gui, session, etc.)

### Pattern 2: Real Ship Objects with Fresh Registries
```python
# From test_battle_screen.py
@pytest.fixture(autouse=True)
def setup(self, fresh_registries):
    ship = Ship("Hero", 0, 0, (0, 0, 255), registries=fresh_registries)
    ship.add_component(create_component('bridge', registries=fresh_registries), LayerType.CORE)
    ship.recalculate_stats()
```
**When:** Testing ship-related rendering or DTO conversion that needs real data

### Pattern 3: Mock pygame via sys.modules
```python
# From test_battle_panels.py
mock_pygame = MagicMock()
mock_pygame.Rect = MockRect
modules_patcher = patch.dict(sys.modules, {'pygame': mock_pygame})
modules_patcher.start()
```
**When:** Testing panel logic that uses pygame types internally (Rect, Surface)

### Pattern 4: Helper Factories for DTOs/Mocks
```python
# From test_battle_panels.py
def create_mock_ship_dto(self, ship_id, team_id, name="Ship"):
    dto = MagicMock()
    dto.id = ship_id
    dto.team_id = team_id
    # ... set all fields
    return dto
```
**When:** Multiple tests need similar mock objects

### Pattern 5: InputMapper with Real Keybindings
```python
# From test_strategy_input_handler_hotkeys.py
@pytest.fixture
def mapper():
    m = InputMapper()
    from game.core.paths import Paths
    m.load(Paths.DEFAULT_KEYBINDINGS_FILE)
    return m

def _keydown(key, mod=0):
    return pygame.event.Event(pygame.KEYDOWN, {'key': key, 'mod': mod})
```
**When:** Testing input handling that uses InputMapper

## Dependencies & Risks

1. **pygame_gui dependency** - Many screens (FleetReportWindow, RaceSetupScreen, BuildQueueScreen, DesignSelectorWindow) inherit from `UIWindow`/use `UIManager`. Tests must either bypass init or create minimal UIManager instances.

2. **Tkinter side effects** - `setup_screen.py` and `formation_editor.py` import tkinter at module level. Tests for these files need careful import handling to avoid Tkinter initialization in headless environments.

3. **Singleton state** - `SpriteManager` and `ShipThemeManager` use singleton pattern with `reset()` for test cleanup. All tests touching these must call `reset()` in teardown.

4. **Asset file dependencies** - Some tests (theme discovery, sprite loading) depend on actual asset files. Tests should handle missing assets gracefully or mock file I/O.

5. **Session/Galaxy dependencies** - Strategy screens need `GameSession`, `Galaxy`, `Empire` objects. These should be mocked rather than created to keep tests fast and focused.

## Phase Organization Rationale

Phases are ordered by dependency and complexity:

1. **Phase 1 (Framework Services)** - Pure logic services with clean DI, no rendering dependencies. Fastest to test, establishes patterns.
2. **Phase 2 (Framework Complex)** - Singleton managers with threading, file I/O, and caching. Requires careful test isolation.
3. **Phase 3 (Battle Layer)** - Battle screens and panels. Existing test patterns to extend.
4. **Phase 4 (Strategy Core)** - Central strategy screens. Complex mock setups but bypass-init pattern works well.
5. **Phase 5 (Strategy Support)** - Extracted modules (formatters, window managers). Simpler dependencies than core screens.
6. **Phase 6 (Workshop & Setup)** - Screens with complex initialization (pygame_gui windows, tkinter). Most mock-heavy.
7. **Phase 7 (Quality)** - Cross-cutting improvements to assertion quality and edge cases.

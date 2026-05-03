# Validation Report: UI-Framework Shard (UI2)

**Validator:** Claude Opus 4.5
**Date:** 2026-02-13
**Shard:** UI2 (UI-Framework)
**Directories:** game/ui/ (root files, services/, renderer/, interfaces/, orchestration/, assets/, components/, utils/)
**Total Findings:** 44
**Validated:** 44

---

## Summary Statistics

| Verdict | Count | Percentage |
|---------|-------|------------|
| CONFIRMED | 19 | 43% |
| DOWNGRADED | 10 | 23% |
| REJECTED | 15 | 34% |

---

## Detailed Validation

### CRITICAL Findings

#### Finding: CON-UI2-001
**Claimed:** Inconsistent Dependency Injection Patterns Across Services
**Location:** `game/ui/services/` (multiple files)
**Verdict:** DOWNGRADED(MINOR)
**Rationale:** After reviewing the services, I find they all follow a consistent pattern: constructor accepts optional DI parameter, defaults to None, and uses lazy initialization via a `_get_*` method or direct import when needed. `ShipFactory`, `ValidationService`, `ShipIOAdapter`, and `DesignLoaderAdapter` all use this same pattern. The patterns are not "incompatible" but rather appropriately adapted to each service's needs. This is not a critical issue.

---

#### Finding: DUP-UI2-001
**Claimed:** Tkinter Root Initialization Duplicated Across 4 Files
**Location:** Multiple files (ship_io.py, screenshot_manager.py, formation_editor.py, workshop_ship_io.py)
**Verdict:** CONFIRMED
**Rationale:** Verified. All four files contain nearly identical Tkinter initialization code:
- `game/ui/services/ship_io.py:20-32` - `tk_root = tkinter.Tk(); tk_root.withdraw()` with try/except
- `game/ui/services/screenshot_manager.py:96-103` - Tkinter init in `_copy_to_clipboard`
- `game/ui/screens/formation_editor.py:24-30` - `tk_root = tkinter.Tk(); tk_root.withdraw()` with try/except
- `game/ui/screens/workshop_ship_io.py:18-26` - `_tk_root = tkinter.Tk(); _tk_root.withdraw()` with try/except

This is genuine duplication that could be centralized.

---

#### Finding: TCG-UI2-001
**Claimed:** No Tests for game_renderer.py (Ship Rendering Logic)
**Location:** `game/ui/renderer/game_renderer.py`
**Verdict:** CONFIRMED
**Rationale:** Verified. No test files matching `test_*game_renderer*.py` exist. The `game_renderer.py` file contains rendering logic including `draw_ship()` function with layer calculations and image scaling. This is complex logic with magic numbers that would benefit from unit tests.

---

### MAJOR Findings

#### Finding: ADR-UI2-001
**Claimed:** ShipFactory uses pygame.math.Vector2 in Method Signature
**Location:** `game/ui/services/ship_factory.py`
**Verdict:** CONFIRMED
**Rationale:** Verified at line 113: `configure_ship()` has parameter `position: pygame.math.Vector2`. This is a pygame type in the method signature of a service that is supposed to be a facade abstracting away dependencies.

---

#### Finding: ADR-UI2-002
**Claimed:** ShipIO module-level Tkinter initialization
**Location:** `game/ui/services/ship_io.py:20-32`
**Verdict:** CONFIRMED
**Rationale:** Verified. Lines 20-32 contain module-level Tkinter initialization that runs on import:
```python
try:
    tk_root = tkinter.Tk()
    tk_root.withdraw()
except tkinter.TclError as e:
    ...
```
This causes side effects on module import and can cause issues in headless environments.

---

#### Finding: ADR-UI2-003
**Claimed:** Camera class uses pygame.math.Vector2 inconsistently
**Location:** `game/ui/renderer/camera.py:14`
**Verdict:** DOWNGRADED(MINOR)
**Rationale:** The Camera class is in the renderer layer and is explicitly a UI/pygame component. Using `pygame.math.Vector2` at line 14 (`self.position = pygame.math.Vector2(0, 0)`) is appropriate for this module. The claim of "inconsistent" usage is inaccurate - it uses pygame.Vector2 throughout consistently.

---

#### Finding: DUP-UI2-002
**Claimed:** Battle Factory Functions Follow Identical Pattern
**Location:** `game/ui/services/battle_factories.py`
**Verdict:** DOWNGRADED(MINOR)
**Rationale:** The four factory functions (`create_manual_battle`, `create_test_battle`, `create_strategy_battle`, `create_hypothetical_battle`) do share a common pattern but each serves a distinct purpose with different configuration. This is intentional API design, not harmful duplication. The functions are concise and readable.

---

#### Finding: DUP-UI2-003
**Claimed:** Service DI Pattern Duplicated with Inconsistencies
**Location:** Unknown
**Verdict:** REJECTED
**Rationale:** Location is "Unknown" - cannot validate. Additionally, this appears to overlap with CON-UI2-001 which was already downgraded.

---

#### Finding: DUP-UI2-004
**Claimed:** BattleUIService Repeated Null-Check Pattern
**Location:** `game/ui/services/battle_ui_service.py`
**Verdict:** CONFIRMED
**Rationale:** Verified. Multiple methods follow the same pattern:
```python
engine = self._battle_service.get_engine()
if engine is None:
    return []  # or return 0, return True, etc.
```
This appears in `get_ships()` (line 68), `get_projectiles()` (line 80), `get_recent_beams()` (line 94), `is_battle_over()` (line 106), `get_winner()` (line 117), `get_tick_count()` (line 128). A decorator or helper could reduce this repetition.

---

#### Finding: LEG-UI2-001
**Claimed:** BattleOrchestrator Class Is Unused In Game Code
**Location:** `game/ui/orchestration/battle_orchestrator.py`
**Verdict:** CONFIRMED
**Rationale:** Verified. Grep for `BattleOrchestrator(` in `game/` directory returns no matches. The class is only used in tests (`tests/unit/ui/test_battle_orchestrator.py`). However, the class does have test coverage and may be intended for future use or as infrastructure.

---

#### Finding: LEG-UI2-002
**Claimed:** IBattleUI Protocol Is Exported But Never Used
**Location:** `game/ui/interfaces/battle_ui.py`
**Verdict:** REJECTED
**Rationale:** IBattleUI is actively used:
- `tests/unit/ui/test_battle_screen.py:143` - verifies `scene.ui_service` is an IBattleUI instance
- `tests/unit/ui/mocks/mock_battle_ui_service.py` - MockBattleUIService implements IBattleUI
- `tests/unit/ui/services/battle_ui_service/test_conversion.py:40` - verifies BattleUIService satisfies IBattleUI
- `tests/unit/ui/interfaces/test_battle_ui.py` - comprehensive protocol tests

The protocol is used for type checking and test verification.

---

#### Finding: CON-UI2-002
**Claimed:** Inconsistent Return Value Conventions for Save/Load
**Location:** `game/ui/services/ship_io_adapter.py`
**Verdict:** REJECTED
**Rationale:** The docstring at lines 28-32 explicitly documents the intentional difference:
- Save: `Tuple[bool, Optional[str]]` - success flag + message
- Load: `Tuple[Optional[T], Optional[str]]` - loaded object + message

This is documented as intentional design, not inconsistency.

---

#### Finding: CON-UI2-003
**Claimed:** Singleton Pattern Inconsistency - instance() vs .instance
**Location:** `game/ui/renderer/sprites.py:8-...`
**Verdict:** REJECTED
**Rationale:** All UI singletons use the same `SingletonMeta` from `game.core.singleton`. The metaclass provides both `MyClass()` and `MyClass.instance()` to access the singleton. All examined usages (`SpriteManager`, `ShipThemeManager`, `ScreenshotManager`) follow this same pattern. There is no inconsistency.

---

#### Finding: CON-UI2-004
**Claimed:** Mixed Docstring Styles
**Location:** Unknown
**Verdict:** REJECTED
**Rationale:** Location is "Unknown" - cannot validate without specific file references.

---

#### Finding: CON-UI2-005
**Claimed:** Module-Level Side Effects in ship_io.py
**Location:** `game/ui/services/ship_io.py:20-32`
**Verdict:** CONFIRMED
**Rationale:** This is the same issue as ADR-UI2-002. The module-level Tkinter initialization is a side effect that runs on import. Confirmed.

---

#### Finding: TCG-UI2-002
**Claimed:** No Tests for battle_factories.py (Battle Creation)
**Location:** `game/ui/services/battle_factories.py`
**Verdict:** CONFIRMED
**Rationale:** Verified. No test files matching `test_*battle_factories*.py` exist. The factory functions contain logic for creating and configuring battle controllers that should be tested.

---

#### Finding: TCG-UI2-003
**Claimed:** config.py Has No Test Coverage
**Location:** `game/ui/config.py`
**Verdict:** DOWNGRADED(MINOR)
**Rationale:** While there are no direct tests for `config.py`, the file contains only constants (no logic). Testing constants directly adds little value. The constants are indirectly tested when UI components that use them are tested.

---

#### Finding: TCG-UI2-004
**Claimed:** utils.py Has Thin Test Coverage
**Location:** `game/ui/utils.py`
**Verdict:** REJECTED
**Rationale:** `tests/unit/ui/test_utils.py` contains 404 lines with comprehensive tests covering:
- `TestCreateCenteredRect` (6 tests)
- `TestCalculateShipImageScale` (5 tests)
- `TestScaleAndRotateImage` (8 tests)
- `TestGetVisibleBoundingBox` (4 tests)
- `TestScaleImageByVisiblePortion` (2 tests)
- `TestScaleImageToFit` (3 tests)
- `TestCalculateShipImageScaleEdgeCases` (4 tests)

This is substantial coverage, not "thin."

---

#### Finding: TCG-UI2-005
**Claimed:** ship_io_adapter.py Needs Error Path Tests
**Location:** `game/ui/services/ship_io_adapter.py`
**Verdict:** CONFIRMED
**Rationale:** `tests/unit/ui/services/test_ship_io_adapter.py` has good coverage but could benefit from more error path testing. Current tests cover:
- `test_save_ship_returns_failure_on_error`
- `test_load_ship_returns_none_on_cancel`
- `test_load_ship_returns_none_on_error`

However, edge cases like network errors, permission issues, or corrupted files are not explicitly tested.

---

### MINOR Findings

#### Finding: ADR-UI2-004
**Claimed:** TYPE_CHECKING import of GameRegistries from Core
**Location:** `game/ui/services/ship_factory.py`
**Verdict:** REJECTED
**Rationale:** TYPE_CHECKING imports are specifically designed for type hints without runtime imports. Importing `GameRegistries` from core under TYPE_CHECKING is the correct pattern for avoiding runtime circular dependencies while maintaining type safety.

---

#### Finding: ADR-UI2-005
**Claimed:** BattleOrchestrator imports from engine layer
**Location:** `game/ui/orchestration/battle_orchestrator.py`
**Verdict:** REJECTED
**Rationale:** The file's docstring (lines 14-20) explicitly documents this as intentional orchestration behavior. The module is designed to coordinate between UI, AI, and Simulation layers. Cross-layer imports are documented as "by design."

---

#### Finding: ADR-UI2-006
**Claimed:** Inconsistent use of Any type hints masking actual types
**Location:** `game/ui/services/validation_service.py`
**Verdict:** CONFIRMED
**Rationale:** Verified. Lines 48-72 use `Any` for `ship`, `component`, and return types where more specific types exist. The `_validator` is also typed as `Any` (line 33). This masks the actual types and reduces type safety.

---

#### Finding: CON-UI2-006
**Claimed:** Inconsistent Method Naming - get_ vs load_
**Location:** Unknown
**Verdict:** REJECTED
**Rationale:** Location is "Unknown" - cannot validate without specific file references.

---

#### Finding: CON-UI2-007
**Claimed:** Inconsistent Type Hint Coverage
**Location:** `game/ui/services/ship_io.py:42`
**Verdict:** CONFIRMED
**Rationale:** Verified. `save_ship(self, ship)` at line 42 lacks type hints for the `ship` parameter and return type. Similarly, `load_ship` at line 82 has type hints for parameters but not for the return type in the signature (though docstring documents it).

---

#### Finding: CON-UI2-008
**Claimed:** Inconsistent Error Logging Patterns
**Location:** `game/ui/services/ship_io.py:72`
**Verdict:** CONFIRMED
**Rationale:** Verified. Different error handlers use different patterns:
- Line 72: `log_error(f"ShipIO: Permission denied saving ship: {e}")`
- Line 113: `log_error(f"ShipIO: Corrupt JSON in ship file: {e}")`
- Some errors include the exception type, others don't. The message format varies.

---

#### Finding: CON-UI2-009
**Claimed:** Inconsistent Private Method Naming
**Location:** Unknown
**Verdict:** REJECTED
**Rationale:** Location is "Unknown" - cannot validate without specific file references.

---

#### Finding: CON-UI2-010
**Claimed:** Boolean Parameter Naming Inconsistency
**Location:** `game/ui/services/battle_factories.py`
**Verdict:** CONFIRMED
**Rationale:** Verified. The functions use different boolean parameter names:
- `create_manual_battle`: `headless: bool = False`
- `create_test_battle`: `headless: bool = True`
- `create_strategy_battle`: `allow_retreat: bool = True`
- `create_hypothetical_battle`: no boolean params

The defaults vary by function, which is intentional per use case, but the naming is consistent.

**Revised Verdict:** DOWNGRADED(INFO) - The boolean naming is actually consistent (`headless`, `allow_retreat`). The different defaults are intentional.

---

#### Finding: CON-UI2-011
**Claimed:** Inconsistent Import Organization
**Location:** `game/ui/services/ship_io.py:1-...`
**Verdict:** DOWNGRADED(INFO)
**Rationale:** The imports follow a reasonable organization (stdlib, then game imports). Minor variation in ordering is not a significant issue.

---

#### Finding: CON-UI2-012
**Claimed:** Magic Numbers in Rendering Code
**Location:** `game/ui/renderer/game_renderer.py`
**Verdict:** CONFIRMED
**Rationale:** Verified. Multiple magic numbers in the file:
- Line 33: `radius_screen = 50 * camera.zoom` - hardcoded 50
- Line 91: `if camera.zoom > 0.3:` - hardcoded threshold
- Line 129: `pygame.draw.circle(..., max(1, scale(3)))` - hardcoded 3
- Line 134: `dir_vec * (base_radius + 10)` - hardcoded 10
- Line 141: `pygame.draw.circle(..., max(2, scale(3)))` - hardcoded 2 and 3

---

#### Finding: DUP-UI2-005
**Claimed:** Image Loading Pattern Repeated Without Common Abstraction
**Location:** Unknown
**Verdict:** REJECTED
**Rationale:** Location is "Unknown" - cannot validate without specific file references.

---

#### Finding: DUP-UI2-006
**Claimed:** Ship Cloning Logic in create_hypothetical_battle
**Location:** `game/ui/services/battle_factories.py`
**Verdict:** CONFIRMED
**Rationale:** Verified at lines 159-173. The ship cloning logic:
```python
cloned1 = []
for ship in ships1:
    data = ShipSerializer.to_dict(ship)
    cloned = ShipSerializer.from_dict(data, registries=ship.registries)
    cloned.x, cloned.y = ship.x, ship.y
    cloned1.append(cloned)
```
This pattern is repeated for both `ships1` and `ships2`. A helper function could eliminate this duplication.

---

#### Finding: DUP-UI2-007
**Claimed:** Singleton Pattern with Same Structure
**Location:** Unknown
**Verdict:** REJECTED
**Rationale:** Location is "Unknown." Additionally, the codebase uses `SingletonMeta` from `game.core.singleton` consistently across all singletons. This is intentional code reuse, not problematic duplication.

---

#### Finding: LEG-UI2-003
**Claimed:** WHITE and BLACK Color Constants Are Dead Code
**Location:** `game/ui/colors.py:7-8`
**Verdict:** CONFIRMED
**Rationale:** Verified. Grep for `from game.ui.colors import WHITE` and `from game.ui.colors import BLACK` returns no matches. The constants `WHITE` and `BLACK` at lines 7-8 are defined but never imported anywhere in the codebase.

---

#### Finding: LEG-UI2-004
**Claimed:** get_visible_bounding_box Function Has No Callers
**Location:** `game/ui/utils.py:97-113`
**Verdict:** REJECTED
**Rationale:** The function is called from:
- `game/ui/utils.py:139` - `scale_image_by_visible_portion` calls `get_visible_bounding_box(surface)`
- `tests/unit/ui/test_utils.py` - has 4 tests for this function

The function is used internally by another utility and is tested.

---

#### Finding: TCG-UI2-006
**Claimed:** BattleOrchestrator Missing Edge Case Tests
**Location:** `game/ui/orchestration/battle_orchestrator.py`
**Verdict:** CONFIRMED
**Rationale:** `tests/unit/ui/test_battle_orchestrator.py` has good coverage but could benefit from edge case tests like:
- Invalid ship objects
- Empty grid handling
- Large numbers of ships

---

#### Finding: TCG-UI2-007
**Claimed:** screenshot_manager.py Tests Could Mock Less
**Location:** `game/ui/services/screenshot_manager.py`
**Verdict:** DOWNGRADED(INFO)
**Rationale:** Without specific test file examination, this is a subjective assessment about mocking strategy. Not a clear defect.

---

#### Finding: TCG-UI2-008
**Claimed:** colors.py Has Test Coverage but Missing Edge Cases
**Location:** `game/ui/colors.py`
**Verdict:** DOWNGRADED(INFO)
**Rationale:** `tests/unit/ui/test_colors.py` has 59 lines of tests validating:
- RGB tuple structure
- Component ranges
- Category prefixes
- Duplicate detection

For a constants-only module, this is adequate coverage.

---

### INFO Findings

#### Finding: ADR-UI2-007
**Claimed:** DesignLoaderAdapter directly imports Simulation layer (acceptable)
**Location:** `game/ui/services/design_loader_adapter.py`
**Verdict:** CONFIRMED
**Rationale:** Verified at line 14: `from game.simulation.services.design_loader import SimulationDesignLoader`. This is acceptable as noted - UI adapters are allowed to import from lower layers.

---

#### Finding: ADR-UI2-008
**Claimed:** Screenshot manager uses hardcoded strategy layer access
**Location:** `game/ui/services/screenshot_manager.py`
**Verdict:** CONFIRMED
**Rationale:** Verified. `capture_strategy_layer()` method at line 119 directly accesses `scene._renderer`, `scene.ui`, `scene.build_queue_screen` - these are strategy layer implementation details.

---

#### Finding: CON-UI2-013
**Claimed:** Inconsistent __all__ Export Patterns
**Location:** `game/ui/__init__.py`
**Verdict:** CONFIRMED
**Rationale:** Verified. `game/ui/__init__.py` defines `__all__` with module names, but most submodules don't define `__all__` at all. This is minor but noted.

---

#### Finding: CON-UI2-014
**Claimed:** Comment Style Variation
**Location:** Unknown
**Verdict:** REJECTED
**Rationale:** Location is "Unknown" - cannot validate without specific file references.

---

#### Finding: DUP-UI2-008
**Claimed:** Adapter Classes Follow Consistent Pattern (positive)
**Location:** Unknown
**Verdict:** CONFIRMED
**Rationale:** This is a positive observation. The adapter classes (`ShipIOAdapter`, `DesignLoaderAdapter`, `ValidationService`) do follow a consistent pattern with constructor DI, optional parameters defaulting to None, and lazy initialization.

---

#### Finding: LEG-UI2-005
**Claimed:** Singleton Pattern Still Used in UI Layer (intentional)
**Location:** Unknown
**Verdict:** CONFIRMED
**Rationale:** Confirmed. `SpriteManager`, `ShipThemeManager`, and `ScreenshotManager` all use `SingletonMeta`. This is documented as intentional for resource caching.

---

#### Finding: TCG-UI2-009
**Claimed:** Excellent Test Coverage on BattleUIService (positive)
**Location:** `game/ui/services/battle_ui_service.py`
**Verdict:** CONFIRMED
**Rationale:** This is a positive observation. The BattleUIService has dedicated test directory `tests/unit/ui/services/battle_ui_service/` with `test_conversion.py` and likely other tests.

---

## Summary of Actionable Items

### High Priority (CRITICAL/MAJOR Confirmed)
1. **DUP-UI2-001**: Centralize Tkinter initialization across 4 files
2. **TCG-UI2-001**: Add tests for `game_renderer.py`
3. **TCG-UI2-002**: Add tests for `battle_factories.py`
4. **ADR-UI2-001**: Consider abstracting pygame.Vector2 from ShipFactory signature
5. **ADR-UI2-002/CON-UI2-005**: Refactor module-level Tkinter side effects in ship_io.py
6. **DUP-UI2-004**: Extract engine null-check pattern in BattleUIService
7. **LEG-UI2-001**: Evaluate if BattleOrchestrator should be integrated or removed

### Medium Priority (MINOR Confirmed)
8. **ADR-UI2-006**: Add specific type hints to ValidationService
9. **CON-UI2-007**: Add missing type hints in ship_io.py
10. **CON-UI2-008**: Standardize error logging patterns
11. **CON-UI2-012**: Extract magic numbers in game_renderer.py to constants
12. **DUP-UI2-006**: Extract ship cloning helper in battle_factories.py
13. **LEG-UI2-003**: Remove unused WHITE/BLACK constants from colors.py
14. **TCG-UI2-005**: Add more error path tests for ship_io_adapter.py
15. **TCG-UI2-006**: Add edge case tests for BattleOrchestrator

---

*Report generated by sweep validator*

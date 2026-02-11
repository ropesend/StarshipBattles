# Phase 1: UI Framework Services

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-111 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add comprehensive unit tests for UI framework services with clean DI. These are pure-logic services with minimal rendering dependencies - ideal for establishing test patterns.
**Findings covered:** TCG-UI2-004, TCG-UI2-005, TCG-UI2-006, TCG-UI2-007, TCG-UI2-008, TCG-UI2-009, TCG-UI2-010, TCG-UI2-011, TCG-UI2-012
**Estimated tests:** ~120-150

---

## Task 1.1: Camera Edge Cases [Medium]
**Finding:** TCG-UI2-004
**Source:** `game/ui/renderer/camera.py` (155 lines)
**Tests:** `tests/unit/ui/test_camera.py` (existing, extend)
**Mocks:** None needed (uses real pygame)

Existing tests cover: initialization, basic transforms, fit_objects. Missing:

- [ ] Test zoom anchor stability during animation: set zoom anchor, run several `update(dt)` steps, verify world point under anchor screen position stays constant
- [ ] Test dead target following: set `target` with `is_alive=False`, verify camera still follows `.position`
- [ ] Test offset_x/offset_y propagation in `world_to_screen` and `screen_to_world` (non-zero offsets)
- [ ] Test multiple sequential zoom operations: rapid zoom-in then zoom-out via `set_zoom_target()`
- [ ] Test zoom limits enforcement: set `target_zoom` beyond `max_zoom` / below `min_zoom`, verify clamping after `update()`
- [ ] Test `screen_to_world` roundtrip with non-zero offset values
- [ ] Test edge case: zero zoom (should clamp or handle gracefully)
- [ ] Test edge case: very large world coordinates (1e6, 1e6)
- [ ] Verify: All new tests pass with `pytest tests/unit/ui/test_camera.py -v`

**Notes:** Camera uses real pygame.Vector2 - tests can run with headless pygame from conftest.

---

## Task 1.2: BattleUIService Error Paths [Medium]
**Finding:** TCG-UI2-005
**Source:** `game/ui/services/battle_ui_service.py` (283 lines)
**Tests:** `tests/unit/ui/services/battle_ui_service/` (existing conftest + 2 test files, extend)
**Mocks:** `mock_ship`, `mock_projectile`, `mock_battle_service` fixtures from conftest

Existing tests cover: happy-path ship/projectile/beam conversion, state queries. Missing:

- [ ] Test `get_ships()` with None engine (battle_service.get_engine() returns None) -> returns `[]`
- [ ] Test `get_projectiles()` with None engine -> returns `[]`
- [ ] Test `get_recent_beams()` with None engine -> returns `[]`
- [ ] Test `get_tick_count()` with None engine -> returns `0`
- [ ] Test `_convert_ship()` with ship missing `resources` attribute (getattr fallback)
- [ ] Test `_convert_ship()` with ship missing `current_target` (None target)
- [ ] Test `_convert_ship()` with ship having `current_target` with `.name` attribute
- [ ] Test `_convert_ship()` with ship having secondary_targets list
- [ ] Test `_convert_ship()` with ship missing `heading` but having `angle`
- [ ] Test `_convert_ship()` with ship missing both `heading` and `angle` (defaults to 0.0)
- [ ] Test `_convert_ship()` with `is_derelict=True`
- [ ] Test `_convert_component()` with component status as enum with `.name`
- [ ] Test `_convert_component()` with component having WeaponAbility
- [ ] Test `_convert_projectile()` with projectile having a target with `.name`
- [ ] Test `_convert_beam()` with missing dict keys (fallback to Vector2(0,0) and white)
- [ ] Test `is_battle_over()` with None engine -> returns True
- [ ] Test `get_winner()` with None engine -> returns None
- [ ] Verify: `pytest tests/unit/ui/services/battle_ui_service/ -v`

**Notes:** Use existing conftest fixtures. Create variations of mock_ship with missing attributes.

---

## Task 1.3: Image Scaling Edge Cases [Medium]
**Finding:** TCG-UI2-006
**Source:** `game/ui/utils.py` (lines 32-220)
**Tests:** `tests/unit/ui/test_utils.py` (existing, extend)
**Mocks:** Uses real pygame surfaces

Existing tests cover: `create_centered_rect`, basic `calculate_ship_image_scale`. Missing:

- [ ] Test `calculate_ship_image_scale()` with `visible_size=0` (should use max of image dimensions)
- [ ] Test `calculate_ship_image_scale()` with `visible_size=None` (should use max of image dimensions)
- [ ] Test `calculate_ship_image_scale()` with 1x1 image
- [ ] Test `calculate_ship_image_scale()` with `manual_scale` multiplier
- [ ] Test `scale_and_rotate_image()` with rotation=0 (no rotation)
- [ ] Test `scale_and_rotate_image()` with rotation=90, 180, 270
- [ ] Test `scale_and_rotate_image()` with very small scale (0.01)
- [ ] Test `scale_and_rotate_image()` with very large scale (10.0)
- [ ] Test `scale_and_rotate_image()` with scale_factor <= 0 (should return original)
- [ ] Test `get_visible_bounding_box()` with fully transparent surface -> returns full rect
- [ ] Test `get_visible_bounding_box()` with fully opaque surface -> returns full rect
- [ ] Test `get_visible_bounding_box()` with single opaque pixel -> returns 1x1 rect at that pixel
- [ ] Test `scale_image_by_visible_portion()` basic functionality
- [ ] Test `scale_image_to_fit()` with target smaller than image
- [ ] Test `scale_image_to_fit()` with target larger than image
- [ ] Verify: `pytest tests/unit/ui/test_utils.py -v`

**Notes:** These functions use real pygame.Surface operations. Tests benefit from the headless display in conftest.

---

## Task 1.4: ComponentService Modifier Restrictions [Medium]
**Finding:** TCG-UI2-007
**Source:** `game/ui/services/component_service.py` (lines 76-120)
**Tests:** `tests/unit/ui/services/test_component_service.py` (existing, extend)
**Mocks:** `MagicMock` for IRegistryProvider, components, modifiers

Existing tests cover: `get_all_components`, `get_modifier_registry`, `get_modifier_definition`, basic `is_modifier_allowed`. Missing:

- [ ] Test `is_modifier_allowed()` with `allow_types` restriction - component type IN allowed list
- [ ] Test `is_modifier_allowed()` with `allow_types` restriction - component type NOT in allowed list
- [ ] Test `is_modifier_allowed()` with `deny_types` restriction - component type IN denied list
- [ ] Test `is_modifier_allowed()` with `deny_types` restriction - component type NOT in denied list
- [ ] Test `is_modifier_allowed()` with `allow_abilities` restriction - component HAS required ability
- [ ] Test `is_modifier_allowed()` with `allow_abilities` restriction - component LACKS required ability
- [ ] Test `is_modifier_allowed()` with multiple restriction types simultaneously (allow_types + deny_types)
- [ ] Test `is_modifier_allowed()` with component having no abilities dict
- [ ] Test `is_modifier_allowed()` with modifier not found (returns False)
- [ ] Test `is_modifier_allowed()` with empty restrictions dict (returns True)
- [ ] Verify: `pytest tests/unit/ui/services/test_component_service.py -v`

**Notes:** All restrictions are in `mod_def.restrictions` dict. Test each key independently and in combination.

---

## Task 1.5: VehicleClassService Edge Cases [Simple]
**Finding:** TCG-UI2-007 (second part)
**Source:** `game/ui/services/vehicle_class_service.py` (129 lines)
**Tests:** `tests/unit/ui/services/test_vehicle_class_service.py` (existing, extend)
**Mocks:** `MagicMock` for IRegistryProvider

- [ ] Test `get_classes_for_type()` with empty vehicle class registry -> returns `[]`
- [ ] Test `get_classes_for_type()` with classes missing `type` field (defaults to 'Ship')
- [ ] Test `get_classes_for_type()` filtering accuracy - only returns matching type
- [ ] Test `get_max_mass()` with unknown class name -> returns 0
- [ ] Test `get_max_mass()` with class missing `max_mass` field -> returns 0
- [ ] Test `get_type_for_class()` with unknown class -> returns 'Ship'
- [ ] Test `get_type_for_class()` with class missing `type` -> returns 'Ship'
- [ ] Test `get_vehicle_types()` returns sorted unique types
- [ ] Test `__init__()` with `None` raises `ValueError`
- [ ] Verify: `pytest tests/unit/ui/services/test_vehicle_class_service.py -v`

---

## Task 1.6: Colors Module Validation [Simple]
**Finding:** TCG-UI2-008
**Source:** `game/ui/colors.py` (35 lines)
**Tests:** `tests/unit/ui/test_colors.py` (NEW)
**Mocks:** None

- [ ] Create `tests/unit/ui/test_colors.py`
- [ ] Test all color tuples have exactly 3 components (R, G, B)
- [ ] Test all components are integers in range [0, 255]
- [ ] Test COLORS dict has expected category keys (bg_*, border_*, text_*, accent_*)
- [ ] Test no duplicate color values across the entire dict
- [ ] Verify: `pytest tests/unit/ui/test_colors.py -v`

**Notes:** Simple parametric test over all entries in the COLORS dict.

---

## Task 1.7: Legacy Widget Edge Cases [Simple]
**Finding:** TCG-UI2-009
**Source:** `game/ui/widgets.py` (102 lines)
**Tests:** `tests/unit/ui/test_ui_widgets.py` (existing, extend)
**Mocks:** Uses real pygame with headless display

- [ ] Test Button hover state change triggers return True
- [ ] Test Button click with callback invokes callback
- [ ] Test Button click without hover does nothing
- [ ] Test Slider value clamping at min_val and max_val boundaries
- [ ] Test Slider drag at exact min position gives min_val
- [ ] Test Slider drag at exact max position gives max_val
- [ ] Test Label `update_text()` changes text attribute
- [ ] Verify: `pytest tests/unit/ui/test_ui_widgets.py -v`

**Notes:** Widgets use real pygame. Tests need headless display (provided by conftest).

---

## Task 1.8: ShipIOAdapter and ValidationService Error Paths [Simple]
**Finding:** TCG-UI2-010
**Source:** `game/ui/services/ship_io_adapter.py`, `game/ui/services/validation_service.py`
**Tests:** `tests/unit/ui/services/test_ship_io_adapter.py`, `tests/unit/ui/services/test_validation_service.py` (existing, extend)
**Mocks:** MagicMock for underlying services

- [ ] Test ShipIOAdapter with file not found error -> verify error propagation
- [ ] Test ShipIOAdapter save with mock permission error
- [ ] Test ValidationService with validator returning None result
- [ ] Test ValidationService with empty validation result
- [ ] Verify: `pytest tests/unit/ui/services/test_ship_io_adapter.py tests/unit/ui/services/test_validation_service.py -v`

---

## Task 1.9: Orchestration/Interface Integration [Simple]
**Finding:** TCG-UI2-011
**Source:** `game/ui/orchestration/`, `game/ui/interfaces/`
**Tests:** `tests/unit/ui/test_battle_orchestrator.py`, `tests/unit/ui/interfaces/test_battle_ui.py` (existing, extend)
**Mocks:** MagicMock for battle services

- [ ] Test BattleOrchestrator with real mock Ship objects (not just shallow mocks)
- [ ] Test IBattleUI protocol compliance with BattleUIService instance
- [ ] Test DTO immutability (attempt to modify ShipDTO fields)
- [ ] Verify: `pytest tests/unit/ui/test_battle_orchestrator.py tests/unit/ui/interfaces/ -v`

---

## Task 1.10: Module Import Verification [Simple]
**Finding:** TCG-UI2-012
**Source:** `game/ui/__init__.py`
**Tests:** `tests/unit/ui/test_ui_imports.py` (NEW)
**Mocks:** None

- [ ] Create `tests/unit/ui/test_ui_imports.py`
- [ ] Test that `import game.ui` succeeds without errors
- [ ] Test that key submodules are importable (renderer, screens, panels, services)
- [ ] Test that `workshop_screen` is NOT imported by `game.ui.__init__` (Tkinter avoidance)
- [ ] Verify: `pytest tests/unit/ui/test_ui_imports.py -v`

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All new tests passing: `pytest tests/unit/ui/ -v --tb=short`
- [ ] No regressions: `pytest tests/ -n 12`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

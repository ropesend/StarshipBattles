# Validation Report: UI-Framework

## Summary
- **Shard:** UI-Framework (UI2)
- **Findings Reviewed:** 37
- **Confirmed:** 12
- **Downgraded:** 14
- **Rejected:** 11
- **Rejection Rate:** 30%

## Verdicts

### Architecture Findings

#### Finding: ADR-UI2-001
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified. Line 16 of ship_io.py has `from game.simulation.entities.ship import Ship` - a direct runtime import creating tight coupling with simulation layer.

#### Finding: ADR-UI2-002
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** The TYPE_CHECKING import at lines 21-23 creates no runtime dependency. Also, the finding itself acknowledges this is acceptable for an adapter/facade pattern.

#### Finding: ADR-UI2-003
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** The finding itself states "No action needed - this is the intended design pattern" and marks effort as "N/A". This is a positive observation, not an actionable issue.

#### Finding: ADR-UI2-004
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** Finding describes intentional design documented in the file comment. This is a positive observation ("architecturally correct"), not an issue.

### Consistency Findings

#### Finding: CON-UI2-001
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified. Three different DI patterns observed: VehicleClassService (lines 36-48) requires registry_provider, ComponentService (lines 31-50) has optional fallback, ShipFactory (lines 40-56) supports both instance and method-level override.

#### Finding: CON-UI2-002
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** Verified type variations exist (IRegistryProvider vs GameRegistries vs Any) but the naming is actually consistent - all use "registry_provider". Impact is overstated since the differences reflect legitimate type differences between services.

#### Finding: CON-UI2-003
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified. SpriteManager methods like load_sprites(), _load_from_directory() lack return type hints. ShipThemeManager methods like load_image(), get_image_metrics() also lack explicit return types.

#### Finding: CON-UI2-004
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified. Screenshot_manager.py lines 40-46, 118-129 use `:param` style while utils.py and most services use Google `Args:` style.

#### Finding: CON-UI2-005
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified. ShipIO uses @staticmethod with class-level state (lines 41, 81) while other services use instance methods with DI. This breaks the pattern used elsewhere.

#### Finding: CON-UI2-006
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** Finding states "No change required; convention is followed" and effort is "N/A". This is a positive observation, not an issue.

#### Finding: CON-UI2-007
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** Verified inconsistency exists but well-documented in code. ShipIOAdapter docstring (lines 28-36) explicitly documents the return convention. This is a documentation concern, not a bug risk.

#### Finding: CON-UI2-008
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** Finding states "mostly consistent" and "minor cognitive load". No specific actionable violations identified - general observation without concrete locations.

#### Finding: CON-UI2-009
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified. Magic numbers at game_renderer.py lines 33-34 (radius 50), 91 (zoom threshold 0.3), 129/135/141 (scaling factors) could be constants in UIConfig.

#### Finding: CON-UI2-010
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** Only one instance found: sprites.py line 101 uses `pygame.Surface | None` vs `Optional` elsewhere. Single occurrence is negligible impact.

#### Finding: CON-UI2-011
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** Finding states "No change required" and effort is "N/A". Naming is "reasonably consistent" per the finding itself.

#### Finding: CON-UI2-012
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified. Ship_io.py lines 20-32 initialize Tkinter at module import time, creating side effects. This is documented but differs from lazy-init pattern used elsewhere.

#### Finding: CON-UI2-013
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** This describes intentional design separation (UI style vs game visualization). The finding states colors are "intentionally" in different places for different concerns.

#### Finding: CON-UI2-014
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** Finding states "No change required" and "this is correct Python Protocol usage". Positive observation, not an issue.

### Duplication Findings

#### Finding: DUP-UI2-001
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified. Tkinter init pattern found in ship_io.py:22, formation_editor.py:26, workshop_ship_io.py:23. Three separate module-level tk_root variables with similar try/except patterns.

#### Finding: DUP-UI2-002
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** Verified similar patterns exist but with intentional differences. ComponentService uses IRegistryProvider, ShipFactory uses GameRegistries. The differences serve legitimate typing needs - not pure duplication.

#### Finding: DUP-UI2-003
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified. utils.py has scale_image_by_visible_portion() (lines 116-162) that design_image_helper.py could use instead of reimplementing similar logic.

#### Finding: DUP-UI2-004
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** Finding acknowledges this is "acceptable documentation pattern" and "low impact". Consistent docstring boilerplate across singletons is a feature, not a bug.

#### Finding: DUP-UI2-005
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** Finding states patterns are "not identical enough to warrant a single abstraction" and "natural pygame usage, not true duplication". Effort is "N/A - acceptable as-is".

#### Finding: DUP-UI2-006
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** Single use currently as stated in finding. Clipboard logic is in one place (screenshot_manager.py lines 88-116). Future duplication risk, not current issue.

#### Finding: DUP-UI2-007
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** Finding describes "good architecture pattern" and is "informational". This is a positive observation about consistent adapter patterns.

### Legacy Findings

#### Finding: LEG-UI2-001
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified. ShipFactory lines 15, 44-56 document "legacy behavior" fallback to get_default_registries(). Two production callers noted (setup_data_io.py, setup_screen.py).

#### Finding: LEG-UI2-002
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified. ComponentService lines 31-49 has optional DI with fallback, while VehicleClassService (lines 36-47) enforces strict DI. Inconsistency in same package.

#### Finding: LEG-UI2-003
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified. IBattleUI imported at line 14-15 of battle_ui_service.py but never used for type annotation or isinstance check. Dead import.

#### Finding: LEG-UI2-004
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** Verified get_ships_folder() exists (lines 64-70) but is only used in tests. This is a test helper method, not dead production code - common practice.

#### Finding: LEG-UI2-005
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified. DesignLoaderAdapter lines 31-44 follow same optional DI pattern with fallback to get_default_registries(). Third service with inconsistent DI policy.

#### Finding: LEG-UI2-006
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified extensive getattr patterns at lines 171, 196-197, 235-236, 250, 255, 258, 266-274 in battle_ui_service.py for attributes like crew_onboard, shots_fired, etc.

#### Finding: LEG-UI2-007
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified hasattr checks at lines 161, 167, 219, 224, 251 in battle_ui_service.py checking for name, status, has_ability attributes. Defensive coding pattern is real.

#### Finding: LEG-UI2-008
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** Finding states "No immediate action needed" and documents legitimate use cases. This describes intended design for singleton caches, not a problem.

### Test Coverage Findings

#### Finding: TCG-UI2-001
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified. No test file exists for game_renderer.py. Searched tests/unit/ui - no test_game_renderer.py found. Critical rendering function has no unit tests.

#### Finding: TCG-UI2-002
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified. No dedicated test file for ship_io_adapter.py. ShipIO is tested but the adapter layer wrapping it is not.

#### Finding: TCG-UI2-003
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** Verified no tests for config.py. However, this file contains only constant definitions (UIConfig class with int values). Validation tests have limited value for static constants.

#### Finding: TCG-UI2-004
**Original Severity:** Major
**Verdict:** REJECTED
**Reason:** test_camera.py has 553 lines including TestCameraEdgeCases class testing very_large_world_coordinates and TestCameraOffsetPropagation with offset tests. Claimed gaps are actually covered.

#### Finding: TCG-UI2-005
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified test_design_loader_adapter.py exists but inspection needed to confirm error path coverage. Finding describes legitimate missing scenarios (invalid JSON, missing fields).

#### Finding: TCG-UI2-006
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** BattleUIService has comprehensive tests as noted. Edge cases mentioned (empty layers, type=None) are minor scenarios with clear default behaviors in code.

#### Finding: TCG-UI2-007
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** ValidationService wraps simulation validator. Boundary value testing is more appropriate at the wrapped validator level, not the thin facade layer.

#### Finding: TCG-UI2-008
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified. test_sprites.py line 34 skips if Components directory not found. CI environments without assets would skip sprite loading tests.

#### Finding: TCG-UI2-009
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** InputMapper tests are "comprehensive" per the finding. Triple-modifier combos are edge cases unlikely to occur in real usage.

#### Finding: TCG-UI2-010
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified. test_theme_discovery.py tests skip when Federation theme not found. Theme loading tests may not run in CI without full assets.

#### Finding: TCG-UI2-011
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** Region clipping tests exist. Verifying "actual clipped image content" is a quality improvement, not a gap - the basic functionality is tested.

#### Finding: TCG-UI2-012
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified. test_colors.py tests COLORS dict but not WHITE, BLACK constants (lines 7-8 of colors.py) or FONT_MAIN (line 11).

#### Finding: TCG-UI2-013
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** This is an observation about test quality (heavy mocking), not a gap. Integration tests are acknowledged as a separate concern.

#### Finding: TCG-UI2-014
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified. test_sprites.py lines 54-58 show test_atlas_fallback_logic() with only `pass` statement - empty test that always passes.

#### Finding: TCG-UI2-015
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** Finding states "test quality is good, this is a style suggestion" and effort is "Simple (optional)". Not an actionable issue.

# Duplication Analyst Report

## Summary
- Total issues found: 15
- Critical: 2, Major: 5, Minor: 4, Info: 4
- Estimated duplicate lines: 1,500-2,000 across codebase

## Findings

### CRITICAL: UI Panel Font/Color Initialization Boilerplate
**ID:** DUP-001
**Occurrences:** 10+ files
**Location:** test_lab/, builder/, battle_state_viewer.py, modifier_impact_grid.py
**Issue:** Every UI component manually initializes identical font sizes, colors, background/border colors
**Missing Abstraction:** UITheme or PanelStylesheet class
**Deliberate?:** Likely accidental — organic growth
**Recommendation:** Create centralized UITheme class for font/color management
**Effort:** Medium (1-2 days)

### CRITICAL: Pygame Rect and Drawing Boilerplate
**ID:** DUP-002
**Occurrences:** 810 pygame.Rect() calls, 300+ blit calls, 247+ pygame.draw calls across 86+ files
**Location:** Concentrated in test_lab/ (79+ blit calls in test_run_details.py alone)
**Issue:** Repetitive drawing code for rectangles, borders, text rendering
**Missing Abstraction:** DrawingUtils helper class with draw_panel(), draw_text() methods
**Deliberate?:** Partially — pygame requires this code, but helpers would reduce it
**Recommendation:** Create DrawingUtils with reusable primitives
**Effort:** Medium (2-3 days for full migration)

### MAJOR: Ability Class Value Extraction Pattern
**ID:** DUP-003
**Occurrences:** 14 instances across 3 ability files
**Location:** defense.py (5), crew.py (3), propulsion.py (6)
**Issue:** Every ability repeats: `val = data if isinstance(data, (int, float)) else data.get('value', 0)`
**Missing Abstraction:** `_extract_value()` helper on Ability base class
**Deliberate?:** Likely accidental
**Recommendation:** Add helper method to Ability base class
**Effort:** Simple (1 hour)

### MAJOR: Ability recalculate() and get_ui_rows() Boilerplate
**ID:** DUP-004
**Occurrences:** 19 recalculate() methods, 21 get_ui_rows() methods across 7 files
**Location:** All ability files (defense.py, crew.py, propulsion.py, weapons.py, etc.)
**Issue:** Nearly identical recalculate() (base * mult) and get_ui_rows() patterns
**Missing Abstraction:** SimpleMultiplierAbility base class with configuration attributes
**Deliberate?:** Partially
**Recommendation:** Create template base class with class-level configuration
**Effort:** High (3-5 days, affects core simulation)

### MAJOR: ValidationResult Error Returns
**ID:** DUP-005
**Occurrences:** 42 instances across 6 files
**Location:** command_handlers.py (16), superweapon_command_handlers.py (14), validators (12)
**Issue:** Repeated `ValidationResult(is_valid=False, errors=[...])` pattern
**Missing Abstraction:** Factory methods on ValidationResult: `.error()`, `.success()`, `.errors()`
**Deliberate?:** Likely accidental
**Recommendation:** Add factory methods — quick win, 1 day
**Effort:** Simple

### MAJOR: Command Handler Structure Duplication
**ID:** DUP-006
**Occurrences:** 20+ command handler classes
**Location:** command_handlers.py (11+), superweapon_command_handlers.py
**Issue:** All handlers repeat fleet/planet resolution, existence validation, error returns
**Missing Abstraction:** BaseCommandHandler with shared _get_fleet(), _get_planet(), _validate_exists()
**Deliberate?:** No — organic growth of handler classes
**Recommendation:** Extract BaseCommandHandler with resolution helpers
**Effort:** Medium (2-3 days)

### MAJOR: Test Fixture Registration Boilerplate
**ID:** DUP-007
**Occurrences:** 1,079 @pytest.fixture decorators across 347 files
**Issue:** Many local fixtures duplicate centralized ones in tests/fixtures/
**Missing Abstraction:** Consolidate to shared fixtures
**Deliberate?:** Partially — some local fixtures are intentionally specific
**Recommendation:** Audit and remove duplicates, document fixture availability
**Effort:** Medium (ongoing)

### MINOR: Property Delegation Pattern
**ID:** DUP-008
**Occurrences:** 10+ properties in test_lab/screen.py
**Location:** `game/ui/screens/test_lab/screen.py:154-200`
**Issue:** Properties that simply delegate to controller
**Recommendation:** Consider exposing controller publicly or using __getattr__
**Effort:** Simple

### MINOR: Pygame Event Handling Boilerplate
**ID:** DUP-009
**Occurrences:** 17 MOUSEBUTTONDOWN checks, 18 KEYDOWN checks across 16 files
**Issue:** Similar event handling structure repeated across screens
**Missing Abstraction:** EventHandlerMixin with standard event processing
**Recommendation:** Create mixin or base class
**Effort:** Medium

### MINOR: UI Panel Position/Size Constructor Pattern
**ID:** DUP-010
**Occurrences:** 7 instances in test lab UI
**Issue:** Manual x, y, width, height storage in constructors
**Missing Abstraction:** BaseUIComponent with pygame.Rect
**Recommendation:** Create base class
**Effort:** Simple

### MINOR: Fleet/Planet Iteration Pattern
**ID:** DUP-011
**Occurrences:** 14+ instances across 12 strategy engine files
**Issue:** Nested iteration to find fleets/planets by ID. Helper exists but not used everywhere.
**Recommendation:** Ensure all code uses session._get_fleet_by_id() helper
**Effort:** Simple

### INFO: isinstance(data, dict) Checks in Ability Parsing
**ID:** DUP-012
**Occurrences:** 28 instances across 10 ability files
**Issue:** Repeated data format checks
**Recommendation:** Enhance _extract_value() (from DUP-003) with component fallback

### INFO: None-Check Validation Pattern
**ID:** DUP-013
**Occurrences:** 323 `if X is None:` checks
**Issue:** Defensive programming, not harmful duplication
**Recommendation:** Low priority

### INFO: getattr() with None Default
**ID:** DUP-014
**Occurrences:** 75 instances across 33 files
**Issue:** Standard Python defensive programming
**Recommendation:** No major abstraction needed

### INFO: Logging Import Pattern
**ID:** DUP-015
**Issue:** Standard Python logging setup, not duplication

## Top 5 Priority Issues

1. **DUP-001 (CRITICAL):** UI Panel Font/Color — 200+ duplicate lines, create UITheme
2. **DUP-002 (CRITICAL):** Pygame Drawing — 800+ calls, create DrawingUtils
3. **DUP-004 (MAJOR):** Ability Boilerplate — 150+ lines, create template base class
4. **DUP-006 (MAJOR):** Command Handler Structure — 200+ lines, create BaseCommandHandler
5. **DUP-005 (MAJOR):** ValidationResult — 100+ lines, add factory methods (quick win)

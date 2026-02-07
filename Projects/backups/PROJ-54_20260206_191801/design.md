# PROJ-54: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis (Phase A)

### Current Implementations Found

1. **PlanetReportPanel Widget** (REUSABLE - BEST IMPLEMENTATION)
   - Location: `game/ui/panels/planet_report_panel.py`
   - Status: ✅ Well-designed, tested, reusable
   - Components: Portrait (150x150), info text, atmosphere graph, complexes list
   - Layout: 580px wide, 350px minimum height
   - Used by: BuildQueueScreen only (currently)
   - Test coverage: Excellent - `tests/integration/ui/test_build_queue_enhanced_planet_report.py`

2. **Strategy UI** (INLINE - SHOULD BE REPLACED)
   - Location: `game/ui/screens/strategy_ui.py` (lines 562-618)
   - Status: ⚠️ Inline HTML formatting, not reusable
   - Problem: Duplicates PlanetReportPanel logic, creates maintenance burden

3. **Planet List Window** (MISSING - NEEDS TO BE ADDED)
   - Location: `game/ui/screens/planet_list_window.py`
   - Status: ❌ No planet report panel exists
   - Needs: Add `PlanetReportPanel` to right side when planet selected

4. **Colonize Planet Window** (BASIC - UPGRADE TO FULL PANEL)
   - Location: `game/ui/screens/planet_selection_window.py`
   - Status: ⚠️ Text-only display via formatter callback
   - Will upgrade to: Full `PlanetReportPanel` for richer display

### Planet Image Bug Identified

**Problem:** Planet images not displaying correctly - show random images instead of persistent assigned images

**Root Cause:** `_get_object_asset()` in `strategy_screen.py` (lines 494-503) ignores planet's stored `image_id` field

**Current (Wrong) Logic:**
- Uses category-based lookup (`'terran'`, `'gas'`, etc.)
- Calls `am.get_random_from_group('planets', cat, seed_id=id(obj))`
- Memory ID as seed = non-deterministic across sessions

**Correct Logic:**
- Use planet's `image_id` field (assigned during galaxy generation)
- Load from `Paths.PLANETS_V3_DIR / image_id`
- Apply `image_rotation` for visual variety

---

## Swarm Findings Summary

### Architecture Analysis

**3-Tier UI Pattern:**
- **Screens** (stateful orchestrators) - StrategyUI, BuildQueueScreen, PlanetListWindow
- **Panels** (stateless containers) - PlanetReportPanel, DesignReportPanel
- **Widgets** (atomic elements) - UIImage, UITextBox, UILabel

**Key Principle:** Panels are dependency-injected stateless containers. Screens handle asset resolution and pass data to panels.

**Current Status:**
- ✅ PlanetReportPanel correctly positioned as reusable widget
- ⚠️ Strategy UI violates architecture (duplicates panel logic inline)
- ❌ Planet List missing panel implementation

### Key Patterns to Reuse

1. **Reusable Panel Pattern:**
   ```python
   def __init__(self, manager, rect, entity, container=None):
       self.panel = UIPanel(relative_rect=rect, manager=manager, container=container)
       # Create sub-elements within self.panel
   ```

2. **Selection-Update Pattern:**
   ```python
   def update_planet(self, planet, portrait_surface=None):
       self.planet = planet
       self.detail_text.html_text = format_planet_info(planet)
       self.detail_text.rebuild()  # CRITICAL: rebuild after html_text change
       self._update_portrait(portrait_surface)
   ```

3. **Optional Components Pattern:**
   ```python
   def __init__(self, ..., show_complexes=True, show_graph=True):
       if show_complexes:
           self.complexes_container = UIScrollingContainer(...)
       else:
           self.complexes_container = None
   ```

4. **External Button Management:**
   - Keep action buttons (Build Queue, Colonize) OUTSIDE panel
   - Positioned by parent screen (below or beside panel)
   - Panel maintains single responsibility (display only)

### Dependencies & Risks

**Critical Issues:**

1. **Duplicate `format_planet_info()` Implementations** (HIGH/HIGH)
   - Primary: `game/ui/screens/strategy_detail_fmt.py` (lines 58-118)
   - Duplicate: `game/ui/screens/strategy_ui.py` (lines 562-618)
   - Mitigation: Delete duplicate, use single source

2. **Layout Cramping** (MEDIUM/MEDIUM)
   - Panel requires minimum 300px width (portrait only)
   - Recommended 580px for full layout
   - Test at 300px, 370px, 580px widths

3. **Missing Planet Data** (MEDIUM/MEDIUM)
   - Some planets may have empty `facilities`, `resources`
   - Maintain existing `hasattr()` and None checks
   - Panel already handles this correctly

4. **Image Loading Failures** (MEDIUM/MEDIUM)
   - Files may not exist, surfaces may be None
   - Wrap in try/except, always have placeholder fallback
   - Panel's gradient placeholder is good pattern

### Test Impact

**~30 Tests Will Need Updates:**
- `test_build_queue_enhanced_planet_report.py` (20 tests)
- `test_planet_complexes_list.py` (8 tests)
- `test_build_queue_formatting.py` (2 tests)
- `build_queue_screen/test_basics.py` (1 test)

**Coverage Gaps to Address:**
- No unit tests for `format_planet_info()` in isolation
- No tests for atmosphere graph edge cases
- No tests for portrait loading/fallback
- No tests for empty atmosphere, missing facilities

### Opportunities Discovered

1. **API Enhancement:** PlanetReportPanel can be improved with backward-compatible parameters
   - Add `portrait_surface` to __init__ (cleaner than update_planet only)
   - Add `show_complexes` parameter (enables Strategy UI reuse)

2. **Code Consolidation:** Eliminating duplicate formatting saves ~60 lines, reduces maintenance

3. **Consistency:** All 4 contexts will show identical planet info (user-friendly)

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.


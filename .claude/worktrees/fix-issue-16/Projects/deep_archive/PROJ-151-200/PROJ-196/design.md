# PROJ-196: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Font Landscape
- **81 font instantiations** across 26+ files
- **Two APIs in use:** `pygame.font.SysFont("name", size, bold)` (68 instances) and `pygame.font.Font(None, size)` (10 instances in 3 files)
- **3 font families:** Arial (most common), Consolas (monospace), Courier New (1 use)
- **17 unique font sizes:** 8, 10, 12, 13, 14, 15, 16, 18, 20, 22, 24, 28, 32, 36, 48, 56, 64, 72
- **2 existing private caches:** `research_renderer._get_font()` (with quantization), `strategy_renderer._get_font()`
- **FONT_MAIN conflict:** Defined in `colors.py` as "Arial", but overridden locally in `battle_state_viewer.py` and `scrollable_json_panel.py` as "Consolas"
- **16 files create fonts per-frame** inside `draw()`/`render()` methods — performance bug

### Color Landscape
- **253 inline color tuples** across the codebase
- **`game/ui/colors.py`** already has ~80 named constants organized by domain
- **COLORS dict** with 20 semantic entries — moderately adopted (10 files)
- **Test Lab** has ~80 inline colors forming a cohesive dark theme across 9 files
- **Common shared tuples** not in colors.py: `(220, 220, 220)`, `(150, 150, 150)`, `(100, 100, 120)`, `(80, 80, 90)`, `(30, 30, 35)`
- **pygame.Color** usage: Only 7 files, all legitimate (pygame_gui requires Color objects)
- **Domain colors** in `stars.py`, `test_framework/scenario.py` — not UI, should stay

### ValidationResult Landscape
- **3 different classes** named `ValidationResult`:
  1. `game.core.validation.ValidationResult` — canonical, has `success()`, `error()`, `with_errors()` factories
  2. `simulation_tests.data.schema_validator.ValidationResult` — different interface (`file_path`, `success`)
  3. `simulation_tests.scenarios.validation.ValidationResult` — dataclass with `status` enum, `p_value`, etc.
- **All production `game/` code** already uses factory methods — zero migration needed
- **7 test locations** still use constructor: 3x `is_valid=True`, 4x `is_valid=False, errors=[...]`
- **44 bare `ValidationResult()`** calls in tests — semantically correct, no change needed

## Swarm Findings Summary

### Architecture
- Font caching naturally belongs at module level (not class level) since fonts are shared across renderers
- `get_font()` + `get_default_font()` separation needed because `SysFont` and `Font(None)` produce visually different fonts
- Test Lab color theme is self-contained — no other screen shares its palette
- The COLORS dict in colors.py coexists with module-level constants (different consumers)

### Key Patterns to Reuse
- **research_renderer quantization**: `game/ui/research/research_renderer.py:75-85` — size quantization for continuous zoom. Must be preserved as a wrapper around the central cache.
- **strategy_renderer cache**: `game/ui/screens/strategy_renderer.py:58-63` — standard `(size, bold)` keyed cache. Can be fully replaced.
- **Test Lab __init__ pattern**: All test_lab files cache fonts in `__init__` — correct pattern, just needs to delegate to `get_font()`.

### Dependencies & Risks
1. **Font test dependencies:** `test_research_renderer.py` tests `_font_cache` dict directly; `test_strategy_renderer.py` tests `_font_cache` attribute. Both need updates when private caches are removed.
2. **FONT_MAIN removal from colors.py:** 8 test_lab files import it. Must update all before removing.
3. **Color exact-match requirement:** Inline color replacements must use exact RGB values. Close-but-not-exact substitutions will change visual appearance.
4. **Module-level pygame dependency:** `get_font()` calls `pygame.font.SysFont()` which requires `pygame.font.init()`. All existing code already initializes pygame before font use — no risk.

### Opportunities Discovered
- **Performance improvement:** 16 files create fonts per-frame. Centralizing to `get_font()` gives automatic caching, measurable frame rate improvement for complex battle scenes.
- **Consistent monospace:** `FONT_MONO = "Consolas"` eliminates the local override pattern.
- **Theme extensibility:** `test_lab/theme.py` creates a pattern other screens could follow later (battle_theme.py, strategy_theme.py, etc.)

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

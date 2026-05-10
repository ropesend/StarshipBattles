# ABS-UI: UI Abstraction Designer Report

## Summary
- **Total issues found:** 7
- **Critical:** 2, **Major:** 3, **Minor:** 1, **Info:** 1
- **Scope:** Cluster 1 (Font/Color Initialization), Cluster 2 (Drawing Boilerplate), Cluster 9 (Event Handling)
- **Prior Art:** Builds on DRY-UI findings CQ-103, CQ-116 from the 2026-02-23 consolidation analysis

---

## Findings

### CRITICAL: Font Initialization Boilerplate Across All UI Components

**ID:** ABS-UI-001
**Location:** 24 files across `game/ui/` (see call site list below)
**Issue:** Every UI component manually creates `pygame.font.Font` or `pygame.font.SysFont` objects with the same font names and sizes. The same font sizes are re-instantiated dozens of times. Each `SysFont` call triggers font file lookup and rasterization setup, which is wasteful. Worse, there is no single source of truth for which font sizes constitute the application's type scale.

**Impact:**
- 60+ font instantiation statements scattered across 24 files
- No centralized type scale -- adding a new size or changing a size requires editing every file
- Inconsistent font names: `"Arial"` in some files, `FONT_MAIN` (which is `"Arial"`) in others, `"arial"` (lowercase) in others, and `"Consolas"` in battle_state_viewer.py where `FONT_MAIN` is locally shadowed
- `UIConfig` has 3 font size constants (`FONT_TITLE=28`, `FONT_NAME=22`, `FONT_STAT=18`) but only `battle_panels.py` uses them; the rest use raw numbers

**Font Size Frequency Table:**

| Size | Occurrences | Semantic Use |
|------|-------------|-------------|
| 12   | 8           | Small/tab labels |
| 14   | 11          | Body text / small labels |
| 16   | 9           | Header/body / component text |
| 18   | 5           | Body / title (medium) |
| 20   | 3           | Section title |
| 22   | 2           | Name/subtitle |
| 24   | 5           | Header / dialog title |
| 28   | 3           | Title / battle header |
| 36   | 1           | Button text (battle) |
| 48   | 2           | Screen title (test lab, battle) |
| 56   | 1           | Complete text (battle) |
| 64   | 1           | Screen title (setup) |
| 72   | 1           | Victory text (battle) |
| 8    | 2           | Tiny labels (strategy widgets) |
| 10   | 3           | Tiny labels (schematics, system) |
| 15   | 1           | Grid cell text |
| 13   | 1           | Monospace content |

**Proposed API:**

```python
# game/ui/theme.py
"""Centralized UI theme providing cached fonts and semantic colors.

Usage:
    from game.ui.theme import ui_theme

    font = ui_theme.font_body         # pygame.font.Font, size 14
    color = ui_theme.color_text       # (220, 220, 220)
"""
from typing import Dict, Tuple
import pygame
from game.ui.colors import FONT_MAIN

Color = Tuple[int, int, int]


class UITheme:
    """Singleton theme providing cached fonts and semantic color palette.

    Fonts are lazily created on first access to avoid pygame.init() issues.
    All font objects are cached -- requesting the same size returns the
    same object.
    """

    # === Type Scale (font sizes) ===
    SIZE_TINY: int = 10
    SIZE_SMALL: int = 12
    SIZE_BODY: int = 14
    SIZE_BODY_LARGE: int = 16
    SIZE_SUBTITLE: int = 18
    SIZE_HEADING: int = 20
    SIZE_TITLE: int = 24
    SIZE_DISPLAY: int = 28
    SIZE_DISPLAY_LARGE: int = 48

    # === Semantic Colors ===
    # Panel backgrounds
    COLOR_BG_PANEL: Color = (30, 30, 35)
    COLOR_BG_PANEL_ALT: Color = (35, 35, 40)
    COLOR_BG_ELEVATED: Color = (40, 40, 50)
    COLOR_BG_HOVER: Color = (45, 45, 50)
    COLOR_BG_SELECTED: Color = (55, 100, 150)

    # Borders
    COLOR_BORDER: Color = (80, 80, 90)
    COLOR_BORDER_ACCENT: Color = (100, 100, 120)
    COLOR_BORDER_SELECTED: Color = (100, 150, 255)

    # Text
    COLOR_TEXT: Color = (220, 220, 220)
    COLOR_TEXT_MUTED: Color = (150, 150, 160)
    COLOR_TEXT_DIM: Color = (140, 140, 160)
    COLOR_TEXT_HEADER: Color = (150, 200, 255)
    COLOR_TEXT_WHITE: Color = (255, 255, 255)

    # Semantic
    COLOR_VALUE: Color = (180, 200, 255)
    COLOR_HIGHLIGHT: Color = (255, 220, 100)
    COLOR_WARNING: Color = (255, 200, 100)

    # Interactive
    COLOR_BUTTON: Color = (60, 100, 160)
    COLOR_BUTTON_HOVER: Color = (80, 120, 180)

    def __init__(self, font_name: str = FONT_MAIN) -> None:
        self._font_name = font_name
        self._font_cache: Dict[int, pygame.font.Font] = {}

    def get_font(self, size: int) -> pygame.font.Font:
        """Get a cached SysFont at the given size."""
        if size not in self._font_cache:
            self._font_cache[size] = pygame.font.SysFont(self._font_name, size)
        return self._font_cache[size]

    # --- Named font properties (primary type scale) ---
    @property
    def font_tiny(self) -> pygame.font.Font:
        return self.get_font(self.SIZE_TINY)

    @property
    def font_small(self) -> pygame.font.Font:
        return self.get_font(self.SIZE_SMALL)

    @property
    def font_body(self) -> pygame.font.Font:
        return self.get_font(self.SIZE_BODY)

    @property
    def font_body_large(self) -> pygame.font.Font:
        return self.get_font(self.SIZE_BODY_LARGE)

    @property
    def font_subtitle(self) -> pygame.font.Font:
        return self.get_font(self.SIZE_SUBTITLE)

    @property
    def font_heading(self) -> pygame.font.Font:
        return self.get_font(self.SIZE_HEADING)

    @property
    def font_title(self) -> pygame.font.Font:
        return self.get_font(self.SIZE_TITLE)

    @property
    def font_display(self) -> pygame.font.Font:
        return self.get_font(self.SIZE_DISPLAY)

    @property
    def font_display_large(self) -> pygame.font.Font:
        return self.get_font(self.SIZE_DISPLAY_LARGE)


# Module-level singleton (prefer over injection for simplicity)
ui_theme = UITheme()
```

**Before/After Example 1: `test_run_details.py` (lines 22-36)**

Before:
```python
# Colors
self.bg_color = (30, 30, 35)
self.border_color = (80, 80, 90)
self.text_color = (220, 220, 220)
self.pass_color = TEST_PASS
self.fail_color = TEST_FAIL
self.header_color = (150, 200, 255)
self.button_color = (60, 100, 160)
self.button_hover_color = (80, 120, 180)

# Fonts
self.title_font = pygame.font.SysFont(FONT_MAIN, 20)
self.header_font = pygame.font.SysFont(FONT_MAIN, 16)
self.body_font = pygame.font.SysFont(FONT_MAIN, 14)
self.small_font = pygame.font.SysFont(FONT_MAIN, 12)
```

After:
```python
from game.ui.theme import ui_theme

# Colors (semantic)
self.bg_color = ui_theme.COLOR_BG_PANEL
self.border_color = ui_theme.COLOR_BORDER
self.text_color = ui_theme.COLOR_TEXT
self.pass_color = TEST_PASS
self.fail_color = TEST_FAIL
self.header_color = ui_theme.COLOR_TEXT_HEADER
self.button_color = ui_theme.COLOR_BUTTON
self.button_hover_color = ui_theme.COLOR_BUTTON_HOVER

# Fonts (cached, shared)
self.title_font = ui_theme.font_heading
self.header_font = ui_theme.font_body_large
self.body_font = ui_theme.font_body
self.small_font = ui_theme.font_small
```

**Before/After Example 2: `test_run_card.py` (lines 37-52)**

Before:
```python
# Colors
self.bg_color = (35, 35, 40)
self.bg_hover_color = (45, 45, 50)
self.bg_selected_color = (55, 100, 150)
self.text_color = (220, 220, 220)
self.border_color = (100, 100, 120)
self.border_selected_color = (100, 150, 255)

# Fonts
self.title_font = pygame.font.SysFont(FONT_MAIN, 16)
self.body_font = pygame.font.SysFont(FONT_MAIN, 14)
self.small_font = pygame.font.SysFont(FONT_MAIN, 12)
```

After:
```python
from game.ui.theme import ui_theme

# Colors (semantic)
self.bg_color = ui_theme.COLOR_BG_PANEL_ALT
self.bg_hover_color = ui_theme.COLOR_BG_HOVER
self.bg_selected_color = ui_theme.COLOR_BG_SELECTED
self.text_color = ui_theme.COLOR_TEXT
self.border_color = ui_theme.COLOR_BORDER_ACCENT
self.border_selected_color = ui_theme.COLOR_BORDER_SELECTED

# Fonts (cached, shared)
self.title_font = ui_theme.font_body_large
self.body_font = ui_theme.font_body
self.small_font = ui_theme.font_small
```

**Before/After Example 3: `results_panel.py` (lines 37-47)**

Before:
```python
# Fonts
self.title_font = pygame.font.SysFont(FONT_MAIN, 20)
self.body_font = pygame.font.SysFont(FONT_MAIN, 14)
self.small_font = pygame.font.SysFont(FONT_MAIN, 12)

# Colors
self.bg_color = (30, 30, 35)
self.border_color = (100, 100, 120)
self.title_color = (255, 255, 255)
self.button_color = (60, 120, 200)
self.button_hover_color = (80, 140, 220)
```

After:
```python
from game.ui.theme import ui_theme

# Fonts (cached, shared)
self.title_font = ui_theme.font_heading
self.body_font = ui_theme.font_body
self.small_font = ui_theme.font_small

# Colors (semantic)
self.bg_color = ui_theme.COLOR_BG_PANEL
self.border_color = ui_theme.COLOR_BORDER_ACCENT
self.title_color = ui_theme.COLOR_TEXT_WHITE
self.button_color = ui_theme.COLOR_BUTTON
self.button_hover_color = ui_theme.COLOR_BUTTON_HOVER
```

**Call Sites (font initialization -- 24 files, 60+ statements):**

| File | Line(s) | Font Statements |
|------|---------|-----------------|
| `game/ui/screens/test_lab/screen.py` | 74-77 | 4 (title_font, header_font, body_font, small_font) |
| `game/ui/screens/test_lab/test_run_details.py` | 33-36 | 4 |
| `game/ui/screens/test_lab/test_run_card.py` | 50-52 | 3 |
| `game/ui/screens/test_lab/results_panel.py` | 38-40 | 3 |
| `game/ui/screens/test_lab/dialogs.py` | 41-42, 150-152 | 5 |
| `game/ui/screens/test_lab/json_viewer.py` | 44-45 | 2 |
| `game/ui/screens/test_lab/ship_panels.py` | 74-75 | 2 |
| `game/ui/screens/test_lab/component_dropdown.py` | 35 | 1 |
| `game/ui/panels/battle_panels.py` | 100-102, 308-310, 515-538 | 8 |
| `game/ui/panels/modifier_impact_grid.py` | 83-85 | 3 |
| `game/ui/panels/design_report_panel.py` | 248-249 | 2 |
| `game/ui/panels/planet_report_panel.py` | 225 | 1 |
| `game/ui/panels/strategy_widgets.py` | 56, 115, 138 | 3 |
| `game/ui/screens/battle_state_viewer.py` | 118-119, 509-511 | 5 |
| `game/ui/screens/battle_ui.py` | 245, 251, 288 | 3 |
| `game/ui/screens/battle_screen.py` | 593 | 1 |
| `game/ui/screens/setup_screen.py` | 369-370 | 2 |
| `game/ui/screens/setup_renderer.py` | 15 | 1 |
| `game/ui/screens/builder/detail_panel.py` | 260 | 1 |
| `game/ui/screens/builder/weapons_panel.py` | 116-118 | 3 |
| `game/ui/screens/builder/schematic_view.py` | 99, 175 | 2 |
| `game/ui/screens/formation/renderer.py` | 260 | 1 |
| `game/ui/screens/workshop_screen.py` | 510 | 1 |
| `game/ui/screens/keybindings_scene.py` | 408 | 1 |
| `game/ui/screens/strategy_renderer.py` | 59 (cache) | 1 |
| `game/ui/screens/strategy_ui.py` | 316 | 1 |
| `game/ui/screens/galaxy_test/system_mode.py` | 528, 559 | 2 |
| `game/ui/research/research_renderer.py` | 84 (cache) | 1 |

**Lines Saved:** ~60 font-init lines eliminated (replaced by `ui_theme.font_*` references). Plus font caching benefits -- currently 60+ separate font objects created; with UITheme, only ~10 unique font objects total.

**Risk:** Low. Font objects are substitutable. The only risk is if any file depends on having a unique font instance (none do -- font objects are stateless renderers).

**Category:** Medium Project
**Recommendation:** Create `game/ui/theme.py` with `UITheme` class. Migrate files in batches by subsystem (test_lab first since it's the densest cluster, then battle_panels, then builder, then remaining).
**Effort:** Medium (24 files to update, but each change is mechanical)

---

### CRITICAL: Inline Color Tuple Duplication Across UI Files

**ID:** ABS-UI-002
**Location:** 24 files across `game/ui/`, 253 inline color tuple definitions total
**Issue:** Color tuples like `(30, 30, 35)`, `(220, 220, 220)`, `(100, 100, 120)`, `(150, 200, 255)`, `(140, 140, 160)`, `(180, 200, 255)` are defined inline in dozens of files. While `game/ui/colors.py` exists and has a well-organized `COLORS` dictionary plus named constants for domain-specific palettes, the custom-drawn panels (test_lab, battle_state_viewer, modifier_impact_grid) bypass it entirely and define colors locally.

**Impact:**
- **253 inline color definitions** across 24 files (just for RGB tuples)
- `(30, 30, 35)` -- "panel background" -- appears in 6 files
- `(220, 220, 220)` -- "standard text" -- appears in 9 files
- `(100, 100, 120)` -- "border accent" -- appears in 9 files
- `(150, 200, 255)` -- "header text" -- appears in 7 files
- `(140, 140, 160)` -- "label text" -- appears in 2 files (but 8+ occurrences within `test_run_details.py` alone)
- `(180, 200, 255)` -- "value text" -- appears in 2 files
- Changing the UI color scheme requires editing 24+ files
- Inconsistent variants: `(80, 80, 90)` vs `(80, 80, 100)` vs `(100, 100, 120)` for borders

**Proposed API:** The `UITheme` class in ABS-UI-001 includes semantic color constants. Additionally, the existing `COLORS` dict in `colors.py` already has many of these colors under semantic names -- the issue is simply that panel code doesn't use it.

**Relationship to `colors.py`:** The `COLORS` dict at `game/ui/colors.py:14-45` has `bg_base`, `bg_elevated`, `border_subtle`, `border_normal`, `text_normal`, `text_bright`, etc. These map closely to the inline values. The `UITheme` class provides additional semantic names specific to panel rendering.

**Color Frequency Table (top duplicated colors):**

| Color Tuple | Semantic Name | Files Using | Occurrences |
|-------------|--------------|-------------|-------------|
| `(30, 30, 35)` | Panel BG | 6 | 6+ |
| `(220, 220, 220)` | Text | 9 | 20+ |
| `(100, 100, 120)` | Border Accent | 9 | 15+ |
| `(150, 200, 255)` | Header Text | 7 | 10+ |
| `(255, 255, 255)` | White Text | 10+ | 20+ |
| `(180, 180, 180)` | Muted Text | 8+ | 15+ |
| `(60, 60, 70)` | Separator Line | 3 | 5+ |
| `(140, 140, 160)` | Label Text | 2 | 10+ |
| `(180, 200, 255)` | Value Text | 2 | 8+ |
| `(255, 200, 100)` | Warning/Highlight | 5 | 8+ |

**Call Sites (color initialization -- densest files):**
- `game/ui/screens/test_lab/screen.py` -- 50 inline color defs
- `game/ui/screens/test_lab/test_run_details.py` -- 21 inline color defs
- `game/ui/screens/battle_state_viewer.py` -- 21 inline color defs
- `game/ui/screens/test_lab/test_run_card.py` -- 8 inline color defs
- `game/ui/panels/modifier_impact_grid.py` -- 8 inline color defs
- `game/ui/screens/test_lab/ship_panels.py` -- 7 inline color defs
- `game/ui/screens/battle_ui.py` -- 11 inline color defs
- `game/ui/panels/battle_panels.py` -- 13 inline color defs

**Lines Saved:** Not about line count reduction (color refs are same length), but about maintainability and consistency. ~253 magic tuples replaced by named constants.

**Risk:** Low. Pure data substitution with no behavior change.

**Category:** Medium Project (pairs with ABS-UI-001 -- same migration)
**Recommendation:** Add semantic panel colors to `UITheme`. Migrate in same passes as font migration.
**Effort:** Medium

---

### MAJOR: Labeled Value Rendering Pattern (render + blit pairs)

**ID:** ABS-UI-003
**Location:** `game/ui/screens/test_lab/test_run_details.py` (79 render calls, 79 blit calls), `game/ui/panels/ship_stats_renderer.py` (20 render+blit), `game/ui/screens/test_lab/test_run_card.py` (26 blit calls), and 30+ other files
**Issue:** The dominant drawing pattern in custom-rendered panels is:
```python
label = self.small_font.render("Label:", True, label_color)
value = self.small_font.render(value_str, True, value_color)
surface.blit(label, (self.x + indent, y_offset))
surface.blit(value, (self.x + indent + label_width, y_offset))
y_offset += 18
```
This 5-line pattern repeats 40+ times in `test_run_details.py` alone. The render-then-blit is a two-step operation that could be a single call.

**Impact:**
- `test_run_details.py`: 79 render calls, 79 blit calls = 158 lines of pure rendering boilerplate
- `ship_stats_renderer.py`: 20 render calls, 20 blit calls
- `test_run_card.py`: 26 blit calls
- `setup_renderer.py`: 16 render+blit pairs
- Total across UI: **275 `.render()` calls** and **302 `.blit()` calls** across 36 files
- The "labeled value" sub-pattern (label + value side by side) appears ~40 times in test_run_details alone

**Proposed API:**

```python
# Addition to game/ui/theme.py or game/ui/draw_utils.py

import pygame
from typing import Tuple, Optional

Color = Tuple[int, int, int]


def draw_text(
    surface: pygame.Surface,
    text: str,
    pos: Tuple[int, int],
    font: pygame.font.Font,
    color: Color = (220, 220, 220),
    antialias: bool = True
) -> pygame.Rect:
    """Render text and blit in one call. Returns the blit rect."""
    rendered = font.render(text, antialias, color)
    rect = surface.blit(rendered, pos)
    return rect


def draw_text_right(
    surface: pygame.Surface,
    text: str,
    right_x: int,
    y: int,
    font: pygame.font.Font,
    color: Color = (220, 220, 220),
) -> pygame.Rect:
    """Render text right-aligned to right_x."""
    rendered = font.render(text, True, color)
    rect = surface.blit(rendered, (right_x - rendered.get_width(), y))
    return rect


def draw_text_centered(
    surface: pygame.Surface,
    text: str,
    center_x: int,
    y: int,
    font: pygame.font.Font,
    color: Color = (220, 220, 220),
) -> pygame.Rect:
    """Render text centered at center_x."""
    rendered = font.render(text, True, color)
    rect = surface.blit(rendered, (center_x - rendered.get_width() // 2, y))
    return rect


def draw_labeled_value(
    surface: pygame.Surface,
    label: str,
    value: str,
    x: int,
    y: int,
    font: pygame.font.Font,
    label_color: Color = (140, 140, 160),
    value_color: Color = (180, 200, 255),
    label_width: int = 75,
) -> int:
    """Draw a label: value pair. Returns the y advance (line height)."""
    draw_text(surface, label, (x, y), font, label_color)
    draw_text(surface, value, (x + label_width, y), font, value_color)
    return font.get_linesize() + 2
```

**Before/After: `test_run_details.py` `_draw_fuel_outcomes` (lines 519-581)**

Before (63 lines):
```python
def _draw_fuel_outcomes(self, surface, metrics, y_offset, label_color, value_color,
                        highlight_color, indent, label_width):
    initial_fuel = metrics.get('initial_fuel', 0)
    final_fuel = metrics.get('final_fuel', 0)
    fuel_consumed = initial_fuel - final_fuel
    expected_consumed = metrics.get('expected_fuel_consumed', fuel_consumed)

    # Initial Fuel
    label = self.small_font.render("Initial Fuel:", True, label_color)
    value = self.small_font.render(f"{initial_fuel:.1f} units", True, value_color)
    surface.blit(label, (self.x + indent, y_offset))
    surface.blit(value, (self.x + indent + label_width, y_offset))
    y_offset += 18

    # Final Fuel
    label = self.small_font.render("Final Fuel:", True, label_color)
    value = self.small_font.render(f"{final_fuel:.1f} units", True, value_color)
    surface.blit(label, (self.x + indent, y_offset))
    surface.blit(value, (self.x + indent + label_width, y_offset))
    y_offset += 18

    # Consumed
    label = self.small_font.render("Consumed:", True, label_color)
    value = self.small_font.render(f"{fuel_consumed:.2f} units", True, highlight_color)
    surface.blit(label, (self.x + indent, y_offset))
    surface.blit(value, (self.x + indent + label_width, y_offset))
    y_offset += 18
    # ... more of the same
```

After (much shorter):
```python
from game.ui.draw_utils import draw_labeled_value

def _draw_fuel_outcomes(self, surface, metrics, y_offset, label_color, value_color,
                        highlight_color, indent, label_width):
    initial_fuel = metrics.get('initial_fuel', 0)
    final_fuel = metrics.get('final_fuel', 0)
    fuel_consumed = initial_fuel - final_fuel
    expected_consumed = metrics.get('expected_fuel_consumed', fuel_consumed)
    x = self.x + indent

    y_offset += draw_labeled_value(surface, "Initial Fuel:", f"{initial_fuel:.1f} units",
                                   x, y_offset, self.small_font, label_color, value_color, label_width)
    y_offset += draw_labeled_value(surface, "Final Fuel:", f"{final_fuel:.1f} units",
                                   x, y_offset, self.small_font, label_color, value_color, label_width)
    y_offset += draw_labeled_value(surface, "Consumed:", f"{fuel_consumed:.2f} units",
                                   x, y_offset, self.small_font, label_color, highlight_color, label_width)
    # ... same for remaining values
```

**Lines Saved:** In `test_run_details.py` alone, the labeled-value pattern accounts for ~120 lines that could be reduced to ~40 (3x reduction). Across the full codebase, estimated ~200 lines saved.

**Risk:** Low. Pure rendering convenience -- identical visual output.

**Category:** Medium Project
**Recommendation:** Create `game/ui/draw_utils.py` with `draw_text`, `draw_text_right`, `draw_text_centered`, `draw_labeled_value`. Migrate densest files first.
**Effort:** Medium

---

### MAJOR: Rounded Panel Drawing Pattern (fill + border pairs)

**ID:** ABS-UI-004
**Location:** 32 files with `pygame.draw.rect` calls (150 total), 9 files with `border_radius` (66 occurrences)
**Issue:** The most common drawing pattern is a filled rounded rect followed by a border rect:
```python
pygame.draw.rect(surface, bg_color, rect, border_radius=5)
pygame.draw.rect(surface, border_color, rect, 2, border_radius=5)
```
This 2-line pattern appears **66 times** across 9 files. There are also non-rounded variants (fill + border) that appear ~80 more times across 32 files. A single `draw_panel()` call would halve these.

**Impact:**
- 66 rounded-rect border_radius pairs across 9 files
- ~80 non-rounded fill+border pairs across 32 additional files
- ~146 total occurrences of the fill+border pattern
- Inconsistent border widths: 1, 2, and 3 all used for panel borders
- Inconsistent border_radius values: 3, 4, 5, 8, 10 all used

**Proposed API:**

```python
# game/ui/draw_utils.py (additions)

def draw_panel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    bg_color: Color = (30, 30, 35),
    border_color: Color = (80, 80, 90),
    border_width: int = 2,
    border_radius: int = 5,
) -> None:
    """Draw a panel with background fill and border."""
    pygame.draw.rect(surface, bg_color, rect, border_radius=border_radius)
    pygame.draw.rect(surface, border_color, rect, border_width, border_radius=border_radius)


def draw_button(
    surface: pygame.Surface,
    rect: pygame.Rect,
    text: str,
    font: pygame.font.Font,
    bg_color: Color = (60, 100, 160),
    border_color: Color = (100, 130, 180),
    text_color: Color = (255, 255, 255),
    border_radius: int = 4,
) -> None:
    """Draw a button with centered text."""
    pygame.draw.rect(surface, bg_color, rect, border_radius=border_radius)
    pygame.draw.rect(surface, border_color, rect, 1, border_radius=border_radius)
    rendered = font.render(text, True, text_color)
    text_x = rect.x + (rect.width - rendered.get_width()) // 2
    text_y = rect.y + (rect.height - rendered.get_height()) // 2
    surface.blit(rendered, (text_x, text_y))


def draw_separator(
    surface: pygame.Surface,
    x: int,
    y: int,
    width: int,
    color: Color = (60, 60, 70),
) -> None:
    """Draw a horizontal separator line."""
    pygame.draw.line(surface, color, (x, y), (x + width, y))
```

**Before/After: `results_panel.py` `draw()` method (lines 151-157)**

Before:
```python
# Draw background
pygame.draw.rect(surface, self.bg_color,
                (self.x, self.y, self.width, self.height), border_radius=5)
pygame.draw.rect(surface, self.border_color,
                (self.x, self.y, self.width, self.height), 2, border_radius=5)
```

After:
```python
from game.ui.draw_utils import draw_panel

draw_panel(surface, pygame.Rect(self.x, self.y, self.width, self.height),
           self.bg_color, self.border_color)
```

**Before/After: `test_run_details.py` button drawing (lines 222-233)**

Before:
```python
pygame.draw.rect(surface, btn_color, self.view_states_button_rect, border_radius=4)
pygame.draw.rect(surface, (100, 130, 180), self.view_states_button_rect, 1, border_radius=4)

btn_text = self.small_font.render("View States", True, (255, 255, 255))
text_x = button_x + (button_width - btn_text.get_width()) // 2
text_y = button_y + (button_height - btn_text.get_height()) // 2
surface.blit(btn_text, (text_x, text_y))
```

After:
```python
from game.ui.draw_utils import draw_button

draw_button(surface, self.view_states_button_rect, "View States",
            self.small_font, bg_color=btn_color, border_color=(100, 130, 180))
```

**Before/After: `setup_renderer.py` `draw_action_buttons` (lines 144-168)**

Before (25 lines for 4 buttons):
```python
# Begin Battle button
btn_color = (50, 150, 50) if has_teams else (50, 50, 50)
pygame.draw.rect(screen, btn_color, (sw // 2 - 100, btn_y, 200, 50))
pygame.draw.rect(screen, (100, 200, 100), (sw // 2 - 100, btn_y, 200, 50), 2)
btn_text = label_font.render("BEGIN BATTLE", True, (255, 255, 255))
screen.blit(btn_text, (sw // 2 - btn_text.get_width() // 2, btn_y + 12))
```

After (much shorter per button):
```python
from game.ui.draw_utils import draw_button

btn_color = (50, 150, 50) if has_teams else (50, 50, 50)
draw_button(screen, pygame.Rect(sw // 2 - 100, btn_y, 200, 50),
            "BEGIN BATTLE", label_font, bg_color=btn_color, border_color=(100, 200, 100))
```

**Call Sites (fill+border pairs -- densest files):**
- `game/ui/screens/test_lab/screen.py`: 28 rounded-rect pairs
- `game/ui/screens/test_lab/test_run_details.py`: 7 rounded-rect pairs
- `game/ui/screens/test_lab/dialogs.py`: 5 rounded-rect pairs
- `game/ui/screens/test_lab/results_panel.py`: 5 rounded-rect pairs
- `game/ui/screens/battle_ui.py`: 4 rounded-rect pairs
- `game/ui/screens/battle_state_viewer.py`: 7 rounded-rect pairs
- `game/ui/research/research_renderer.py`: 4 rounded-rect pairs
- `game/ui/screens/test_lab/ship_panels.py`: 4 rounded-rect pairs
- `game/ui/screens/test_lab/test_run_card.py`: 2 rounded-rect pairs
- `game/ui/screens/setup_renderer.py`: 22 draw.rect calls (11 pairs, no border_radius)

**Lines Saved:** ~146 line pairs -> ~73 single calls = ~73 lines saved. Button pattern (6 lines -> 2) saves additional ~50 lines across ~15 button sites. Total: ~120-150 lines.

**Risk:** Low. Pure rendering convenience.

**Category:** Medium Project
**Recommendation:** Add `draw_panel`, `draw_button`, `draw_separator` to `game/ui/draw_utils.py`.
**Effort:** Medium

---

### MAJOR: Scrollbar Drawing Duplication (5+ implementations)

**ID:** ABS-UI-005
**Location:**
- `game/ui/screens/test_lab/test_run_details.py:883-893`
- `game/ui/screens/test_lab/results_panel.py:238-256`
- `game/ui/screens/test_lab/dialogs.py:112-116`
- `game/ui/screens/test_lab/screen.py:1383-1395`
- `game/ui/screens/battle_state_viewer.py:440-451`

**Issue:** Five separate implementations of scrollbar thumb drawing with identical logic: calculate thumb size from content/visible ratio, calculate thumb position from scroll offset, draw rounded rect. Each implementation is 8-15 lines of identical math.

**Impact:**
- 5 implementations, ~50 lines total
- All use the same formula: `thumb_height = max(30, int(visible_height * (visible_height / total_content_height)))` and `thumb_y = track_y + int((scroll_offset / max_scroll) * (track_height - thumb_height))`
- Bug fixes or style changes to scrollbar must be applied in 5 places

**Proposed API:**

```python
# game/ui/draw_utils.py (addition)

def draw_scrollbar(
    surface: pygame.Surface,
    x: int,
    track_y: int,
    track_height: int,
    scroll_offset: int,
    max_scroll: int,
    width: int = 8,
    color: Color = (100, 100, 120),
    min_thumb_height: int = 30,
    border_radius: int = 4,
) -> None:
    """Draw a scrollbar thumb within a track region.

    Args:
        surface: Target surface
        x: X position of scrollbar
        track_y: Top of scrollbar track
        track_height: Height of scrollbar track
        scroll_offset: Current scroll position
        max_scroll: Maximum scroll value
        width: Scrollbar width in pixels
        color: Thumb color
        min_thumb_height: Minimum thumb height
        border_radius: Thumb corner radius
    """
    if max_scroll <= 0:
        return

    total_content = track_height + max_scroll
    thumb_height = max(min_thumb_height, int(track_height * (track_height / total_content)))
    thumb_y = track_y + int((scroll_offset / max_scroll) * (track_height - thumb_height))

    pygame.draw.rect(
        surface, color,
        (x, thumb_y, width, thumb_height),
        border_radius=border_radius
    )
```

**Before/After: `test_run_details.py` `_draw_scrollbar` (lines 883-893)**

Before:
```python
def _draw_scrollbar(self, surface):
    visible_height = self.height
    total_content_height = visible_height + self.max_scroll
    scrollbar_width = 8
    scrollbar_x = self.x + self.width - scrollbar_width - 5
    scrollbar_track_y = self.y + 5
    scrollbar_track_height = visible_height - 10
    thumb_height = max(30, int(visible_height * (visible_height / total_content_height)))
    thumb_y = scrollbar_track_y + int((self.scroll_offset / self.max_scroll) * (scrollbar_track_height - thumb_height))
    pygame.draw.rect(surface, (100, 100, 120), (scrollbar_x, thumb_y, scrollbar_width, thumb_height), border_radius=4)
```

After:
```python
from game.ui.draw_utils import draw_scrollbar

def _draw_scrollbar(self, surface):
    draw_scrollbar(
        surface,
        x=self.x + self.width - 13,
        track_y=self.y + 5,
        track_height=self.height - 10,
        scroll_offset=self.scroll_offset,
        max_scroll=self.max_scroll,
    )
```

**Lines Saved:** 5 implementations * ~10 lines = ~50 lines -> 5 * ~6 lines = ~30 lines. Net: ~20 lines saved, plus single point of maintenance.

**Risk:** Low. Pure rendering utility.

**Category:** Quick Win
**Recommendation:** Add `draw_scrollbar()` to `game/ui/draw_utils.py`. Migrate 5 call sites.
**Effort:** Simple

---

### MINOR: Pygame Event Handling Boilerplate (Cluster 9)

**ID:** ABS-UI-006
**Location:** 16+ files across `game/ui/screens/` and `game/ui/panels/`
**Issue:** 17 MOUSEBUTTONDOWN checks and 18 KEYDOWN checks exist across 16 files. However, after analysis, these are **not truly duplicated** -- they are contextually unique:

- **KEYDOWN handlers** vary by screen: each screen responds to different keys (Escape, F12, arrow keys, WASD, etc.) and routes to different screen-specific logic. The existing `InputMapper` service at `game/ui/services/input_mapper.py` already provides an abstraction for key-to-action mapping. Most KEYDOWN handlers already delegate to screen-specific methods after the type check.

- **MOUSEBUTTONDOWN handlers** also vary: some check `event.button == 1` (left click), some check `event.button == 3` (right click), some handle both. The hit-testing logic (`rect.collidepoint(event.pos)`) is inherent to each component's unique layout. Abstracting this away would require a component layout registry, which is overengineering for this codebase.

- **Pattern variety:**
  - Simple escape-to-close: `if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:` (appears in 5 files -- this specific sub-pattern COULD be extracted)
  - Button click dispatch: check `collidepoint` for each button rect (appears in 8 files -- but each has different buttons)
  - Scroll handling: `if event.type == pygame.MOUSEWHEEL:` (appears in 6 files -- partially extractable via scrollable mixin)

**Assessment:** An `EventHandlerMixin` is **not warranted**. The `if event.type == pygame.KEYDOWN:` / `if event.type == pygame.MOUSEBUTTONDOWN:` checks are the minimum necessary boilerplate for pygame event dispatch. Each handler is contextually unique. Abstracting them would either:
1. Create a rigid framework that constrains UI development, or
2. Be so thin that it adds complexity without reducing code

**Partial Win:** The scroll handling pattern (check bounds, adjust offset, clamp) appears in 6+ files and IS worth extracting, but this is more properly a `ScrollableMixin` concern rather than event handling per se.

**Impact:** Low. The 1-2 lines of event type checking are not a meaningful maintenance burden.

**Risk:** N/A (recommending against abstraction)

**Category:** N/A
**Recommendation:** Do NOT create an EventHandlerMixin. The event dispatch pattern is inherently per-screen/per-component. Consider a `ScrollableMixin` as a separate, focused abstraction if scroll handling duplication becomes painful.
**Effort:** N/A

---

### INFO: battle_state_viewer.py Shadows FONT_MAIN

**ID:** ABS-UI-007
**Location:** `game/ui/screens/battle_state_viewer.py:13-14`
**Issue:** This file defines local constants `FONT_MAIN = 'Consolas'` and `FONT_MONO = 'Consolas'`, which shadow the module-level `FONT_MAIN = "Arial"` from `game/ui/colors.py`. This is intentional (the battle state viewer uses monospace fonts for JSON display), but it creates confusion and would conflict with a centralized theme.

**Impact:** Minimal -- isolated to one file. But demonstrates the need for the theme to support a monospace font variant.

**Proposed API Addition:**
```python
class UITheme:
    # ... existing code ...
    def __init__(self, font_name: str = FONT_MAIN, mono_font_name: str = "Consolas") -> None:
        self._font_name = font_name
        self._mono_font_name = mono_font_name
        self._font_cache: Dict[Tuple[str, int], pygame.font.Font] = {}

    def get_mono_font(self, size: int) -> pygame.font.Font:
        """Get a cached monospace SysFont at the given size."""
        key = (self._mono_font_name, size)
        if key not in self._font_cache:
            self._font_cache[key] = pygame.font.SysFont(self._mono_font_name, size)
        return self._font_cache[key]
```

**Risk:** None.
**Category:** Quick Win (during theme migration)
**Effort:** Simple

---

## Top 5 Priority Issues

1. **ABS-UI-001 (CRITICAL): Font Initialization Boilerplate** -- 60+ font creation statements across 24 files. The `UITheme` singleton with cached fonts eliminates all of them and provides a single type scale. This is the foundation that all other improvements build on.

2. **ABS-UI-002 (CRITICAL): Inline Color Tuples** -- 253 inline color definitions across 24 files. The `UITheme` semantic color constants replace them with named, searchable references. Pairs naturally with ABS-UI-001 (same migration pass).

3. **ABS-UI-004 (MAJOR): Rounded Panel Drawing** -- 146 fill+border pairs that become 73 `draw_panel()` calls. Plus ~15 button sites that collapse from 6 lines to 2. The `draw_button()` helper alone saves ~50 lines.

4. **ABS-UI-003 (MAJOR): Labeled Value Rendering** -- 275 render calls + 302 blit calls across 36 files. The `draw_text()` and `draw_labeled_value()` helpers cut the heaviest files (test_run_details.py) by 3x.

5. **ABS-UI-005 (MAJOR): Scrollbar Drawing** -- 5 identical implementations. Quick win: single `draw_scrollbar()` function, 5-minute migration per call site.

## Implementation Order

1. **Phase 1:** Create `game/ui/theme.py` with `UITheme` class (ABS-UI-001, ABS-UI-002)
2. **Phase 2:** Create `game/ui/draw_utils.py` with `draw_text`, `draw_panel`, `draw_button`, `draw_scrollbar`, `draw_separator`, `draw_labeled_value`, `draw_text_centered`, `draw_text_right` (ABS-UI-003, ABS-UI-004, ABS-UI-005)
3. **Phase 3:** Migrate test_lab files (densest cluster -- 8 files)
4. **Phase 4:** Migrate battle panels and battle_state_viewer
5. **Phase 5:** Migrate builder, setup, strategy, remaining files

## Relationship to Prior Art

- **DRY-UI CQ-116 (Info: Color Definition Inconsistencies):** Confirmed and elevated to CRITICAL. CQ-116 noted that "some panels still define custom colors inline" -- our analysis quantifies this as 253 inline definitions across 24 files.
- **DRY-UI CQ-103 (Critical: Section Header Pattern):** Already partially addressed by `create_section_header()` in `game/ui/utils.py`. Our `draw_text()` utility complements this for non-pygame_gui rendering.
- **DRY-CROSS XL-001 (Numeric Type Checking):** Separate concern, not addressed here.
- **Existing `game/ui/config.py` UIConfig:** Has `FONT_TITLE`, `FONT_NAME`, `FONT_STAT` size constants but only 1 file uses them. The `UITheme` approach provides actual font objects, making the UIConfig font sizes redundant. Recommend deprecating `UIConfig.FONT_*` in favor of `ui_theme.font_*`.
- **Existing `game/ui/colors.py` COLORS dict:** Well-structured but underutilized by custom-drawn panels. `UITheme` adds panel-specific semantic names that complement the existing dict.

---

*Report compiled: 2026-02-23*

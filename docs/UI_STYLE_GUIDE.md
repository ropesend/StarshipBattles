# StarshipBattles UI Style Guide

## Overview

This document describes the sci-fi color scheme and styling conventions for the StarshipBattles UI. The theme uses a dark blue-gray palette with cyan accent colors, creating a futuristic military starship aesthetic.

---

## Color Palette

### Background Colors (Darkest to Lightest)

| Name | Hex Code | RGB | Usage |
|------|----------|-----|-------|
| **Deep Background** | `#12151a` | (18, 21, 26) | Deepest backgrounds, dark_bg |
| **Dark Background** | `#14181f` | (20, 24, 31) | Panel interiors, text entry backgrounds |
| **Base Background** | `#1a1e26` | (26, 30, 38) | Standard panel backgrounds |
| **Elevated Background** | `#1e2530` | (30, 37, 48) | Buttons, list items (normal state) |
| **Hover Background** | `#283040` | (40, 48, 64) | Hovered elements |
| **Selected Background** | `#2a3855` | (42, 56, 85) | Selected items, active states |

### Border Colors

| Name | Hex Code | RGB | Usage |
|------|----------|-----|-------|
| **Subtle Border** | `#2a3040` | (42, 48, 64) | Disabled borders |
| **Normal Border** | `#2a3545` | (42, 53, 69) | Default panel borders |
| **Active Border** | `#3a4860` | (58, 72, 96) | Button borders, prominent elements |
| **Hover Border** | `#55aaee` | (85, 170, 238) | Hovered element borders (cyan glow) |
| **Selected Border** | `#4499dd` | (68, 153, 221) | Selected element borders |
| **Bright Border** | `#66bbff` | (102, 187, 255) | Active/focused borders |

### Text Colors

| Name | Hex Code | RGB | Usage |
|------|----------|-----|-------|
| **Disabled Text** | `#556070` | (85, 96, 112) | Disabled/inactive labels |
| **Muted Text** | `#667799` | (102, 119, 153) | Units, secondary info |
| **Subtle Text** | `#8899bb` | (136, 153, 187) | Stat labels, tertiary text |
| **Normal Text** | `#9aabcc` | (154, 171, 204) | Default text color |
| **Bright Text** | `#aabbdd` | (170, 187, 221) | Button text, important labels |
| **Highlight Text** | `#aaccff` | (170, 204, 255) | Stat values, emphasized content |
| **Hover Text** | `#c8daff` | (200, 218, 255) | Hovered item text |
| **Selected Text** | `#ffffff` | (255, 255, 255) | Selected/active item text |

### Accent Colors

| Name | Hex Code | RGB | Usage |
|------|----------|-----|-------|
| **Primary Accent** | `#4488dd` | (68, 136, 221) | Filled bars, primary actions |
| **Slider Thumb** | `#3366aa` | (51, 102, 170) | Slider handles (normal) |
| **Slider Hover** | `#4488cc` | (68, 136, 204) | Slider handles (hover) |
| **Link Color** | `#5599ff` | (85, 153, 255) | Hyperlinks |
| **Header Accent** | `#6699cc` | (102, 153, 204) | Section headers |

---

## pygame_gui Theme Application

### Applying to New Elements

Add entries to `builder_theme.json` following this pattern:

```json
"#your_element_id": {
    "colours": {
        "normal_bg": "#1e2530",
        "hovered_bg": "#283040",
        "selected_bg": "#2a3855",
        "normal_border": "#3a4860",
        "hovered_border": "#55aaee",
        "normal_text": "#9aabcc",
        "hovered_text": "#c8daff",
        "selected_text": "#ffffff"
    },
    "misc": {
        "shape": "rounded_rectangle",
        "shape_corner_radius": "4",
        "border_width": "1"
    }
}
```

### Element-Specific Styling

**Panels:**
```json
"panel": {
    "colours": {
        "dark_bg": "#14181f",
        "normal_bg": "#1a1e26",
        "normal_border": "#2a3545"
    }
}
```

**Buttons:**
```json
"button": {
    "colours": {
        "normal_bg": "#1e2530",
        "hovered_bg": "#283040",
        "normal_border": "#3a4860",
        "hovered_border": "#55aaee",
        "normal_text": "#aabbdd",
        "hovered_text": "#ddeeff"
    }
}
```

**Selection Lists:**
```json
"selection_list": {
    "colours": {
        "normal_bg": "#1a1e26",
        "dark_bg": "#12151a"
    }
}

"selection_list.@selection_list_item": {
    "colours": {
        "normal_bg": "#1e2530",
        "hovered_bg": "#283040",
        "selected_bg": "#2a3855",
        "normal_text": "#9aabcc",
        "hovered_text": "#c8daff",
        "selected_text": "#ffffff"
    }
}
```

**Text Entry:**
```json
"text_entry_line": {
    "colours": {
        "normal_bg": "#14181f",
        "hovered_bg": "#1a1e26",
        "normal_border": "#2a3545",
        "hovered_border": "#4488cc",
        "normal_text": "#c8d4e8"
    }
}
```

**Sliders:**
```json
"horizontal_slider": {
    "colours": {
        "normal_bg": "#12151a",
        "normal_border": "#2a3545"
    }
}

"horizontal_slider.#sliding_button": {
    "colours": {
        "normal_bg": "#3366aa",
        "hovered_bg": "#4488cc",
        "normal_border": "#4488bb",
        "hovered_border": "#66ccff"
    }
}
```

---

## Direct pygame Drawing

When drawing UI elements directly with pygame (not pygame_gui), use these colors:

```python
# Color constants for pygame drawing
COLORS = {
    # Backgrounds
    'bg_deep': (18, 21, 26),
    'bg_dark': (20, 24, 31),
    'bg_base': (26, 30, 38),
    'bg_elevated': (30, 37, 48),
    'bg_hover': (40, 48, 64),
    'bg_selected': (42, 56, 85),
    
    # Borders
    'border_subtle': (42, 48, 64),
    'border_normal': (42, 53, 69),
    'border_active': (58, 72, 96),
    'border_hover': (85, 170, 238),  # Cyan glow
    'border_selected': (68, 153, 221),
    
    # Text
    'text_disabled': (85, 96, 112),
    'text_muted': (102, 119, 153),
    'text_subtle': (136, 153, 187),
    'text_normal': (154, 171, 204),
    'text_bright': (170, 187, 221),
    'text_highlight': (170, 204, 255),
    'text_hover': (200, 218, 255),
    'text_selected': (255, 255, 255),
    
    # Accents
    'accent_primary': (68, 136, 221),
    'accent_glow': (85, 170, 238),
    'accent_bright': (102, 187, 255),
}
```

### Drawing Examples

**Panel with border:**
```python
def draw_styled_panel(screen, rect):
    # Background
    pygame.draw.rect(screen, COLORS['bg_base'], rect)
    # Border
    pygame.draw.rect(screen, COLORS['border_normal'], rect, 1)
```

**Hover-aware button:**
```python
def draw_styled_button(screen, rect, text, is_hovered=False, is_pressed=False):
    if is_pressed:
        bg = COLORS['bg_selected']
        border = COLORS['border_selected']
        text_color = COLORS['text_selected']
    elif is_hovered:
        bg = COLORS['bg_hover']
        border = COLORS['border_hover']
        text_color = COLORS['text_hover']
    else:
        bg = COLORS['bg_elevated']
        border = COLORS['border_active']
        text_color = COLORS['text_bright']
    
    pygame.draw.rect(screen, bg, rect, border_radius=4)
    pygame.draw.rect(screen, border, rect, 2, border_radius=4)
    # Render and center text...
```

**Progress/health bar:**
```python
def draw_styled_bar(screen, rect, fill_pct):
    # Background track
    pygame.draw.rect(screen, COLORS['bg_deep'], rect, border_radius=3)
    # Filled portion
    fill_rect = rect.copy()
    fill_rect.width = int(rect.width * fill_pct)
    pygame.draw.rect(screen, COLORS['accent_primary'], fill_rect, border_radius=3)
    # Border
    pygame.draw.rect(screen, COLORS['border_normal'], rect, 1, border_radius=3)
```

---

## Design Principles

1. **Depth through color:** Use darker backgrounds for recessed areas, lighter for elevated elements
2. **Cyan accents:** Use the cyan/blue glow colors sparingly for hover states and important highlights
3. **Subtle borders:** Keep borders thin (1-2px) and use muted colors for normal states
4. **High contrast text:** Ensure text is readable - use brighter text colors on darker backgrounds
5. **Consistent corner radius:** Use 3-5px corner radius for rounded elements

---

## Files Reference

- **Theme file:** `builder_theme.json` - pygame_gui theme definitions
- **Color constants:** Add to a shared module like `ui/colors.py` for consistent pygame drawing

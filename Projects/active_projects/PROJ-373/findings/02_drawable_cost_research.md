# PROJ-373 — Rounded-rect drawable cost research

> Source: Explore subagent run 2026-05-05.
> Read-only investigation; no files modified.
>
> **Caveat:** The agent extrapolated some panel-cost numbers (e.g., "~16-38s per
> open") from worst-case theoretical 4K row counts. The pyinstrument capture
> is the ground truth: actual per-open cost is ~6.9s, of which ~3s lives in
> rounded-rect rebuilds. Use the relative ranking and recommendations here;
> trust the profile for absolute numbers.

## 1. Theme parameters on the slow panels

All `UIPanel` instances in the build-queue screen use the default `"panel"` theme class — no custom `object_id` or `class_id` is set. Theme block at [data/builder_theme.json:60-70](../../../../data/builder_theme.json#L60):

```json
"panel": {
  "colours": {
    "dark_bg": "#14181f",
    "normal_bg": "#1a1e26",
    "normal_border": "#2a3545"
  },
  "misc": {
    "shape": "rounded_rectangle",
    "shape_corner_radius": "3",
    "border_width": "1"
  }
}
```

Rounded corners with `corner_radius: 3` trigger the
`RoundedRectangleShape.__init__` → `full_rebuild_on_size_change` →
`redraw_all_states` → `redraw_state` path
(`pygame_gui/core/drawable_shapes/rounded_rect_drawable_shape.py:67-216`).
`redraw_state` (line 402-563) does anti-aliased corner rasterization with
4× upsampling (`aa_amount = 4`, line 447), temporary surfaces, gradient
blits, and shape composition — per state per panel.

## 2. Are these panels visually rounded?

**Yes** — `corner_radius: 3` produces subtle but visible rounded borders. Not a slow default applied accidentally; the look is deliberate. However, given the dark space-game aesthetic, sharp corners would likely blend fine without obvious regression. A before/after screenshot is the cheapest check.

## 3. Panel count per build-queue open

Counted from [build_queue_panel_factory.py](../../../../game/ui/screens/build_queue_panel_factory.py):

| Panel | Source | Count |
|-------|--------|------:|
| Background | `_create_background()` line 192 | 1 |
| Context report (planet/fleet) | `_create_context_report_panel()` line 199 | 1 |
| Design report | `_create_design_report_panel()` line 293 | 1 |
| Items list | `_create_items_list_panel()` line 305 | 1 |
| Build queue main | `_create_build_queue_panel()` line 338 | 1 |
| Build queue table container | line 376 | 1 |
| Queue selector | `_create_queue_selector_panel()` line 272 | 1 |
| Filter panel | `_create_filter_panel()` line 420 | 1 |
| Bottom bar | `_create_bottom_bar()` line 508 | 1 |
| VirtualTable header | `_build_containers()` line 116 | 1 |
| VirtualTable list view | `_build_containers()` line 125 | 1 |
| **Subtotal: main panels** | | **11** |
| VirtualTable row pool | `_rebuild_row_pool()` line 143-onwards | ~10-20 (profile-measured) |

The profile shows ~3s of the 6.9s per-click cost goes to rounded-rect
rebuilds across these panels (`_rebuild_row_pool` is 1.5s of that).

## 4. Pre-baking opportunity (only if Phase 2 doesn't already eliminate this)

| Panel | Cache value |
|-------|-------------|
| Background (static overlay) | High |
| Filter panel (rare changes) | Medium |
| Context report | Medium (refreshes on yard switch) |
| Bottom bar (turn/resource changes) | Low |

Pre-baking only saves the `RoundedRectangleShape` rasterization, not the UIElement hierarchy overhead. **Modest value if Phase 2 lands** — strong value if first-open cost remains a perceptible delay.

## 5. Theme simplification — the cheap win

**Single change:** [data/builder_theme.json:67](../../../../data/builder_theme.json#L67)
- `"shape": "rounded_rectangle"` → `"shape": "rectangle"`

**Affected scope:** ALL `UIPanel` instances using the default panel class — i.e., the build queue, plus every other screen using `UIPanel` with no override (likely many).

**Risk:** Low. The 3px corner radius is barely visible in dark UI. Worth eyeballing before/after; if any specific screen suffers, that screen's `object_id` can override back to rounded.

**Alternative — scoped change:** add `"@build_queue_panel"` (or similar) object_id overrides for the build-queue panels only, so the global panel theme stays rounded and only the build queue switches to rectangle. More surgical, lower regression surface, slightly more wiring.

## 6. VirtualTable dependencies

`VirtualTable._rebuild_row_pool()` ([virtual_table.py:143](../../../../game/ui/components/table/virtual_table.py#L143)) creates one `UIPanel` per visible-row slot (lines 169-173) — these inherit the same default `panel` theme and pay the same rounded-rect cost. Per-row child widgets (UILabel, UIButton, UIImage) use cheaper shapes; only the row container pays.

If the theme switches to rectangle, row-pool cost drops too — directly addresses the 1.5s `_rebuild_row_pool` line item.

## 7. Suggested phase ordering

Phase 2 (screen reuse) is the highest-impact single change — it eliminates the per-click panel construction cost entirely. After Phase 2, theme simplification still has value because:

1. **First open** still constructs panels — Phase 2 only helps the second-and-later opens.
2. **Every other panel-heavy screen** in the game pays this cost too. The win is global, not just build-queue.
3. **VirtualTable row-pool rebuilds** can re-trigger if panel dimensions change (e.g., resolution change).

Recommended sequence within PROJ-373:
1. Phase 1 (validate cache) — cheapest immediate win
2. Phase 2 (screen reuse) — biggest per-click win
3. Phase 3 (row-pool reuse) — verify Phase 2 captured this; otherwise targeted follow-up
4. Phase 4 (theme simplification) — global win, also covers first-open + other screens

## File references

- `data/builder_theme.json:60-70` — panel theme
- `game/ui/screens/build_queue_panel_factory.py` — panel construction
- `game/ui/components/table/virtual_table.py:111-173` — VirtualTable containers + row pool
- `pygame_gui/elements/ui_panel.py:50-87` — UIPanel `__init__`
- `pygame_gui/core/drawable_shapes/rounded_rect_drawable_shape.py:67, 402-563` — slow path
- `game/ui/panels/design_report_panel.py:51` — DesignReportPanel.panel
- `game/ui/screens/build_queue_selector.py:57` — BuildQueueSelector.panel

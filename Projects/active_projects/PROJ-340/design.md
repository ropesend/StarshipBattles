# PROJ-340 — Design

## Architecture context

PROJ-340 is a **characterization** project: it adds tests, not architecture.
This document describes where each in-scope file sits in the broader app so
test authors can mock at the right seams.

For canonical layer boundaries and patterns, see:
- [`docs/01_ARCHITECTURE.md`](../../../docs/01_ARCHITECTURE.md)
- [`docs/02_PATTERNS.md`](../../../docs/02_PATTERNS.md)

PROJ-340 proposes **no architectural changes**. Findings that suggest
future refactors are recorded as observations in `decisions.md`.

## Per-file architectural placement

### `game/ui/services/battle_ui_service.py`

**Role:** Simulation→UI seam. Converts engine objects (Ship, Projectile,
Beam) into DTOs the rendering layer consumes. Thin facade over
`BattleService.get_engine()`.

**Boundary:** Sits between `combat/engine` (sim) and `ui/screens/battle*`
(render). No render code; no sim mutation. All read-side.

**Test seam:** Mock `BattleService.get_engine()` — return a mock engine
with `.ships`, `.projectiles`, `.recent_beams`, `.tick_counter`,
`.is_battle_over()`, `.get_winner()`. No pygame, no real engine needed.

### `game/ui/assets/ship_theme_manager.py`

**Role:** Asset-loader singleton. On `initialize()`, walks
`Paths.SHIP_THEMES_DIR`, reads `theme.json` per theme, caches Surface
objects lazily on first `load_image(...)`.

**Boundary:** Sits at the disk→pygame boundary. One module-level "default"
instance accessed via `get_default_ship_theme_manager()` /
`set_default_ship_theme_manager()`.

**Test seam:** Monkeypatch the path constant + patch `pygame.image.load`.
See `decisions.md` D-003 / D-004.

### `game/ui/widgets/scrollable_json_panel.py`

**Role:** Battle-state-viewer composite widget. Renders a JSON document
with syntax highlight, diff overlay (added/removed/changed colors), scroll
state, and scrollbar drag.

**Boundary:** Pure widget — owns its render Surface, consumes pygame events,
holds no app state beyond its current JSON + diff dict.

**Test seam:** Patch `get_font` to return a deterministic renderer; pass
real `pygame.Surface` for draw destination; build pygame `Event` objects in
tests.

### `game/ui/effects/hit_effects.py`

**Role:** Battle-renderer overlay. Module-level `HitEffect` dataclass +
helpers `create_hit_effect`, `update_effects`, `draw_effects`. Four effect
types (shield, armor, component, ship-destroyed) dispatched via private
`_draw_*` helpers.

**Boundary:** Pure-data dataclass + draw helpers. No singleton; caller
owns the effects list.

**Test seam:** Mock `camera.world_to_screen` returning `(x, y)` and `.zoom`
attribute; pass a real `pygame.Surface` as screen.

### `game/ui/panels/base_gallery.py`

**Role:** Abstract base for race-setup-style galleries (skin/race
selection). Subclasses provide 9 abstract hooks (asset list source,
preview-render rules, callback). The base lays out a `pygame_gui` panel
with a label, preview area, scrolling button grid, and routes button
clicks back to subclass.

**Boundary:** UI-only. No service dependencies. Heavy `pygame_gui`
construction happens in `__init__` → `_create_content`.

**Test seam:** Patch `pygame_gui.elements.*`; subclass `BaseGallery` with
all abstracts implemented to return Mocks; assert widget construction
sequence and click routing.

### `game/ui/panels/builder_widgets.py`

**Role:** `ModifierEditorPanel` — design-workshop helper that builds a
scrolling row per allowed modifier on the editing component. Each row is a
`ModifierControlRow` (toggle + value control). On change, mutates the
component and recalculates stats.

**Boundary:** Bridges UI ↔ component domain (`ModifierLogic`,
`ModifierLogicService`). Reads modifiers from `GameRegistries.modifiers`.

**Test seam:** Patch `pygame_gui.elements.*` + `ModifierControlRow`; mock
`GameRegistries`, `ModifierLogic`, editing-component (with `.add_modifier`,
`.remove_modifier`, `.get_modifier`, `.recalculate_stats`).

## Test directory layout

```
tests/unit/ui/
├── services/
│   └── test_battle_ui_service.py        (NEW)
├── assets/
│   └── test_ship_theme_manager.py       (NEW)
├── widgets/
│   └── test_scrollable_json_panel.py    (NEW)
├── effects/
│   └── test_hit_effects.py              (NEW)
└── panels/
    ├── test_base_gallery.py             (NEW)
    └── test_builder_widgets.py          (NEW)
```

If any of `services/`, `assets/`, `widgets/`, `effects/`, `panels/` does
not yet exist under `tests/unit/ui/`, the directory + an empty
`__init__.py` will be created in the same commit as the first test
module that lands in it.

## Mocking discipline

- **Mock at protocol/service seams**, not at internal implementation
  details (e.g. mock `BattleService`, not `BattleEngine`'s private fields
  beyond what `_convert_*` actually reads).
- **Real pygame surfaces** wherever a Surface is the destination — they are
  cheap and avoid coupling tests to a draw mock.
- **Patch module-global constants only when no injection point exists**
  (the `Paths.SHIP_THEMES_DIR` case). Document each such patch in
  `decisions.md`.

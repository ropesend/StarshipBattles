# PROJ-340 — Manifest

## Production files (in scope, READ-ONLY)

| Path | LOC | Role |
|---|---:|---|
| `game/ui/services/battle_ui_service.py` | 299 | DTO conversion (Ship/Projectile/Beam → DTO); thin facade over `BattleService`. |
| `game/ui/assets/ship_theme_manager.py` | 453 | Theme discovery + lazy image cache; real disk I/O + `pygame.image.load` + `Paths.SHIP_THEMES_DIR` global. |
| `game/ui/widgets/scrollable_json_panel.py` | 412 | Stateful JSON viewer widget (parse, syntax highlight, diff overlay, scroll, scrollbar drag). |
| `game/ui/effects/hit_effects.py` | 233 | Module-level dataclass + tick/draw helpers for 4 effect types. |
| `game/ui/panels/base_gallery.py` | 265 | Abstract gallery base (`pygame_gui` panel layout + selection routing). |
| `game/ui/panels/builder_widgets.py` | 294 | `ModifierEditorPanel` — `pygame_gui` scrolling row builder with rebuild/diff. |

No production file is modified by PROJ-340.

## Planned new test files

| Path | Targets | Behaviors |
|---|---|---:|
| `tests/unit/ui/services/test_battle_ui_service.py` | `battle_ui_service.py` | 8 |
| `tests/unit/ui/assets/test_ship_theme_manager.py` | `ship_theme_manager.py` | 12 |
| `tests/unit/ui/widgets/test_scrollable_json_panel.py` | `scrollable_json_panel.py` | 10 |
| `tests/unit/ui/effects/test_hit_effects.py` | `hit_effects.py` | 9 |
| `tests/unit/ui/panels/test_base_gallery.py` | `base_gallery.py` | 3 |
| `tests/unit/ui/panels/test_builder_widgets.py` | `builder_widgets.py` | 3 |
| **Total** | — | **45** |

## Existing tests touched

- `tests/unit/ui/test_ship_theme_logic.py` — exists, logic-only scope. Will
  be inspected to avoid duplicate coverage. **Not modified** by PROJ-340.

## Monkeypatch / mock surfaces

| File under test | Patch target | Reason |
|---|---|---|
| `ship_theme_manager.py` | `game.ui.assets.ship_theme_manager.Paths.SHIP_THEMES_DIR` | Redirect to `tmp_path` (no production injectable param). |
| `ship_theme_manager.py` | `pygame.image.load` (within module) | Avoid disk PNGs; return synthetic SRCALPHA surface. |
| `ship_theme_manager.py` | `PIL.Image.open` (size validator path) | Optional — only when exercising the size-mismatch branch. |
| `scrollable_json_panel.py` | `game.ui.fonts.get_font` (or local import) | Avoid font subsystem init; return Mock with deterministic `render`. |
| `base_gallery.py` | `pygame_gui.elements.{UIPanel,UIButton,UIImage,UILabel,UIScrollingContainer}` | Inert widget construction; assert call shape. |
| `builder_widgets.py` | `pygame_gui.elements.*` + `ModifierControlRow` import | Same pattern; mock row interactions. |

## Fixture surfaces

- `tmp_path` — fake themes tree for `ship_theme_manager` tests.
- Real `pygame.Surface((W, H), SRCALPHA)` for any `draw` destination.
- Mock `BattleService` / `BattleEngine` for `battle_ui_service` tests.
- Mock `GameRegistries`, `ModifierLogic`, editing-component for
  `builder_widgets` tests.

## File-overlap check vs sibling projects

- `services/` — only `battle_ui_service.py` here; not in PROJ-337/338/339.
- `assets/` — only `ship_theme_manager.py` here; not in sibling scopes.
- `widgets/` — only `scrollable_json_panel.py` here; not in sibling scopes.
- `effects/` — only `hit_effects.py` here; not in sibling scopes.
- `panels/` — `base_gallery.py` + `builder_widgets.py`. `panels/` is shared
  with PROJ-338/339, but those projects own different specific files
  (`build_queue_*`, `system_tree_panel`, `planet_report_panel`,
  `battle_panels`, `race_*_panel`, `design_stats_panel`,
  `modifier_impact_grid`, `empire_treasury_panel`). **Zero file overlap
  with PROJ-340's two panels.**

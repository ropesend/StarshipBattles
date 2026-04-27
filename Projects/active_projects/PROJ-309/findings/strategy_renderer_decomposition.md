# Decomposition Design: strategy_renderer.py

**Current size:** 1208 lines (re-measured 2026-04-27; design.md table says 1205 — within rounding)
**Target post-split:** every resulting module <500 lines

---

## Current responsibilities

`StrategyRenderer` is one class doing several distinct render-pipeline jobs. By line range:

1. **L 1-40** — Module docstring, imports, animation constant.
2. **L 42-74** — `__init__`: construct, cache `AssetManager`, `GameSettings`, init bg state, animation clock, hex-outline cache.
3. **L 76-108** — Background image: `_load_background`, `_draw_background` (dim/scale once, blit).
4. **L 110-120** — `update(dt)` animation tick + `_get_font` thin wrapper.
5. **L 122-182** — Property accessors (`camera`, `galaxy`, `systems`, `empires`, `hex_size`, `screen_width/height`, `SIDEBAR_WIDTH`, `TOP_BAR_HEIGHT`, `empire_assets`) plus `_hex_radius_to_screen` math helper (BUG-94 power curve).
6. **L 184-227** — `draw()` composer: viewport setup, clip, ordered layer dispatch (background → grid → outlines → warp lanes → systems → fleets → previews → hover → border).
7. **L 229-266** — Cursor/preview overlays: `_draw_move_preview`, `_draw_ghost_hex`, `_draw_hover_hex`.
8. **L 268-376** — Hex occupancy outlines (PROJ-214): `_build_hex_outline_data` (turn-cached), `_get_hex_outline_data`, `_draw_hex_outlines`, `_draw_inner_hex`.
9. **L 378-450** — `_draw_grid` (snake-line hex grid with viewport culling).
10. **L 452-509** — `_draw_warp_lanes` (system-to-system warp connections).
11. **L 511-559** — Systems/stars layer entry: `_draw_systems`, `_load_star_image`.
12. **L 561-589** — `_draw_colony_marker` (low-zoom ownership dot per system).
13. **L 591-656** — `_draw_star` (image core-radius scaling, selection ring, label).
14. **L 658-789** — `_draw_system_details`: planet hex grouping, polar layout, planet sprite ordering, **plus warp-point sprites** (rotation animation, `BLEND_ADD`).
15. **L 791-855** — `_draw_dyson_spheres` (multi-hex Sphereworld portrait, owner flag — note: refers to undefined `screen_diameter` at L846/854; pre-existing bug, out of scope here).
16. **L 857-1014** — `_draw_storms` + `_draw_storms_low_detail` (nebulae imagery, tint blends, fallback polygons, low-zoom hex circles).
17. **L 1016-1093** — `_draw_planet_sprite` + image loaders `_load_planet_v3_image`, `_load_dyson_sphere_image`.
18. **L 1095-1158** — `_draw_fleets` (fleet icon, race shield flag, selection ring, fallback triangle).
19. **L 1160-1197** — `_draw_fleet_path` (multi-segment move/warp lines, turn labels).
20. **L 1199-1208** — `draw_processing_overlay` (modal "PROCESSING TURN…" banner).

The work cleanly stratifies into rendering layers (background → grid/outline → warp lanes → systems-internals → fleets → cursor overlays → modal). State is concentrated: a few caches (`_bg_*`, `_hex_outline_cache`, `_elapsed_time`) plus the parent-`scene` reference.

---

## Proposed sub-modules

The split follows the existing layer boundaries already encoded in `draw()` (L 184-227). Each module exposes free functions — not classes — that take an explicit `RenderContext` (or the renderer itself) plus the layer-specific data. The orchestrating `StrategyRenderer` retains the cached state, properties, and `draw()` composition.

Layout uses a **package**: `game/ui/screens/strategy_render/`. (Package name is a controlled noun; it forces new code to declare which layer it belongs in, resisting rebloat.)

| # | Path | Responsibility | Symbols it owns | Est. LOC | Depends on |
|---|------|---------------|-----------------|----------|------------|
| 1 | `game/ui/screens/strategy_render/__init__.py` | Package marker; deliberately empty (no re-exports) so each layer is imported at its specific path. | — | ~5 | — |
| 2 | `game/ui/screens/strategy_render/background.py` | Static galaxy bg image: load once, scale + dim cache, blit. | `BackgroundLayer` (small class holding the scaled-surface cache) with `load(asset_manager)`, `draw(screen, viewport_rect, brightness)`. | ~50 | `pygame`, `AssetManager`, `UIConfig` |
| 3 | `game/ui/screens/strategy_render/grid.py` | Hex grid snake-line drawing with viewport culling. | `draw_grid(screen, ctx)` | ~85 | `hex_math`, `colors`, `pygame` |
| 4 | `game/ui/screens/strategy_render/hex_outlines.py` | PROJ-214 occupancy outlines + turn-keyed cache + inner-hex helper. | `HexOutlineLayer` (holds the turn-cache), `.draw(screen, ctx)`, internal `_build_data`, `_draw_inner_hex`. | ~110 | `hex_math`, `colors`, `pygame` |
| 5 | `game/ui/screens/strategy_render/warp_lanes.py` | System-to-system warp lane segments. | `draw_warp_lanes(screen, ctx)` | ~70 | `hex_math`, `colors`, `pygame` |
| 6 | `game/ui/screens/strategy_render/systems.py` | System layer: stars + colony markers + system-details dispatch into storms / dyson / planets / warp-points. | `draw_systems(screen, ctx, elapsed_time)`, internal helpers `_draw_star`, `_draw_colony_marker`, `_draw_system_details`. | ~230 | `planets`, `storms`, `dyson_spheres`, `hex_math`, `pygame` |
| 7 | `game/ui/screens/strategy_render/planets.py` | Single-planet sprite + colony flag, hex-group layout math (polar fan), planet image loaders. | `draw_planet_sprite(...)`, `layout_planet_group(...)` (polar angles for 1-N planets), `load_planet_v3_image(asset_mgr, image_id)`. | ~170 | `colors`, `pygame`, `AssetManager` |
| 8 | `game/ui/screens/strategy_render/storms.py` | Storm nebulae overlay (full + low-detail) and tint table. | `draw_storms(screen, ctx)`, `draw_storms_low_detail(...)`, module-level `STORM_TINTS`. | ~170 | `hex_math`, `colors`, `pygame` |
| 9 | `game/ui/screens/strategy_render/dyson_spheres.py` | Dyson Sphere multi-hex render + owner flag. | `draw_dyson_spheres(screen, ctx)`, `load_dyson_sphere_image(asset_mgr)`. | ~70 | `colors`, `Paths`, `pygame` |
| 10 | `game/ui/screens/strategy_render/fleets.py` | Fleet icon + shield flag + selected-ring + path projection. | `draw_fleets(screen, ctx)`, `draw_fleet_path(screen, ctx, fleet, start_screen)`. | ~110 | `hex_math`, `colors`, `pygame` |
| 11 | `game/ui/screens/strategy_render/cursor.py` | Live-cursor overlays: move preview, ghost-hex, hover hex. | `draw_move_preview(screen, ctx)`, `draw_ghost_hex(screen, ctx, ghost_hex)`, `draw_hover_hex(screen, ctx)`. | ~60 | `hex_math`, `cargo_transfer_service.project_fleet_position`, `pygame` |
| 12 | `game/ui/screens/strategy_render/overlay.py` | Modal "processing turn" overlay. | `draw_processing_overlay(screen, font_provider)`. | ~20 | `colors`, `fonts`, `pygame` |
| 13 | `game/ui/screens/strategy_render/context.py` | `RenderContext` value-class threading per-frame derived state (camera, galaxy, empires, hex_size, screen dims, empire_assets, font provider, asset manager, hex_radius_to_screen helper). | `@dataclass(frozen=True) RenderContext` + the `hex_radius_to_screen(radius)` static helper / curried function. | ~70 | `pygame`, `AssetManager` |
| 14 | `game/ui/screens/strategy_renderer.py` (rewritten) | Composer / state holder. Owns: `BackgroundLayer`, `HexOutlineLayer`, `_elapsed_time`, the `RenderContext` factory, and `draw()` orchestration. Re-exports `StrategyRenderer`. | `StrategyRenderer` class only. | ~120 | every sub-module |

**Total estimated:** ~1340 LOC including new package-level docstrings, `__init__`, and `RenderContext` boilerplate (~10 % overhead vs. the original 1208). Every file is well under 500.

### Why a `RenderContext` rather than passing the whole `StrategyRenderer`?

Pure functions taking a frozen context have one reason to change (the layer they paint). Passing the renderer object would let any layer reach back into private renderer state, which is exactly the rebloat vector this project is fighting. The two layers that *do* need persistent state (`BackgroundLayer`, `HexOutlineLayer`) own their own state explicitly and are constructed once.

---

## Public API surface

External callers of `strategy_renderer.py` (production):

| Caller | Symbol used | Line |
|--------|-------------|------|
| `game/ui/screens/strategy_screen.py` | `StrategyRenderer` (class) — constructed at L 122 | 36 |
| `game/ui/screens/strategy_screen.py` | `self._renderer.update(dt)` | 190 |
| `game/ui/screens/strategy_screen.py` | `self._renderer.draw(screen)` | 198 |
| `game/ui/screens/strategy_screen.py` | `self._renderer.draw_processing_overlay(screen)` | 201 |

Test callers:
- `tests/unit/ui/screens/test_strategy_renderer.py` — imports `StrategyRenderer`
- `tests/unit/ui/screens/test_strategy_renderer_animation.py` — imports `StrategyRenderer`

The **only public surface** is `StrategyRenderer` with `__init__(scene)`, `update(dt)`, `draw(screen)`, and `draw_processing_overlay(screen)`.

Internal `_draw_*` and `_load_*` helpers are NOT part of the public API. They become module-private functions in their respective sub-modules.

The string `# Angles for smaller planets (must match strategy_renderer.py Rev 5 values)` in `strategy_click_dispatcher.py:448` is a comment, not an import — but it does flag that the polar-layout math is duplicated. **Out of scope for this decomposition** but worth a follow-up ticket: the angle table belongs in `strategy_render/planets.py` and `strategy_click_dispatcher` should import it.

---

## Caller-update strategy

**Choice:** **Option A** — re-export shim, but trivially. The original path `game/ui/screens/strategy_renderer.py` continues to expose `StrategyRenderer`. The class is rewritten as the thin composer described above (row 14).

**Justification:**

1. There is exactly **one production caller** (`strategy_screen.py`) and **two test files** — strictly this is borderline Option-B-eligible.
2. *However*, the public API `StrategyRenderer(scene)` is genuinely the right contract for the composer — moving it would not buy clarity.
3. Existing tests build `StrategyRenderer(mock_scene)` and assert on internal attributes (`_elapsed_time`, `_bg_image`, etc.). Keeping the class at the same path means tests stay green without rewrites; only tests that drilled into now-extracted helpers (e.g. asserting on `_draw_grid`) would need to be redirected to the new module path. Inspection of `test_strategy_renderer.py` shows it primarily tests init / properties / coordinate-conversion / mocked draw — most tests will not need to move.
4. This is **not a graveyard shim** — `strategy_renderer.py` retains real composer logic. The Migration-Policy concern about lingering shims doesn't apply.

In short: Option A here is "the original file becomes the composer" rather than "the original file becomes nothing but `from … import *`." That is the cleanest of all worlds.

---

## Test plan

### Existing tests affected
- `tests/unit/ui/screens/test_strategy_renderer.py` — primary affected. Initialization tests, animation tests, property accessors all stay valid (composer keeps them). Any test that patched / asserted on the **internal** `_draw_grid`, `_draw_systems`, `_draw_warp_lanes`, `_build_hex_outline_data`, `_draw_planet_sprite`, etc. needs its patch target redirected to the new module path (e.g. `game.ui.screens.strategy_render.grid.draw_grid`). Audit pass during phase implementation.
- `tests/unit/ui/screens/test_strategy_renderer_animation.py` — unchanged. Tests `update(dt)` and `WARP_POINT_ROTATION_SPEED` constant. The constant moves to `strategy_render/systems.py` (since it's used during warp-point rendering); test should import from there. Two-line change.

### New tests required (Phase-3 TDD)
- `tests/unit/ui/screens/strategy_render/test_context.py` — `RenderContext` is a frozen dataclass; verify it carries the expected fields and `hex_radius_to_screen` math (BUG-94 anchor at radius-2). 4-6 cases.
- `tests/unit/ui/screens/strategy_render/test_background_layer.py` — verify scaled-surface cache invalidation on size change and brightness change (currently untested behavior). 3-4 cases.
- `tests/unit/ui/screens/strategy_render/test_hex_outlines.py` — verify `HexOutlineLayer` cache rebuilds on turn change but not on no-op call; verify dual-outline (player + enemy) selection logic. 4-6 cases.
- `tests/unit/ui/screens/strategy_render/test_planets.py` — verify polar angle table for 1-6 planet groups (this is a regression of the duplication noted with `strategy_click_dispatcher`). 6 cases — one per `smaller_count` branch.
- Smoke: `test_strategy_renderer.py::test_draw_dispatches_all_layers` — patch each layer function and verify `StrategyRenderer.draw()` calls them in the documented order with the expected zoom gates (zoom < 0.4 skips grid; zoom < 0.5 skips outlines/hover).

### Regression guard
After split, run full sharded suite. Baseline: 15405 passed. Any drop is a faulty split — investigate before phase exit (per design.md Risk #4).

---

## Risks

### Import cycles
**Low risk.** The dependency graph forms a DAG: `context` (leaf) ← `{background, grid, hex_outlines, warp_lanes, planets, storms, dyson_spheres, cursor, fleets, overlay}` ← `systems` (composes planets/storms/dyson) ← `strategy_renderer` (composer). No layer references another peer layer except `systems` consuming `planets`/`storms`/`dyson_spheres` — which is one-way. The package `__init__.py` is intentionally empty (no convenience re-exports) to prevent accidental circular imports.

### Shared mutable rendering state
**Two real cases, both encapsulated:**

1. `_elapsed_time` (animation clock). Lives on `StrategyRenderer`. Passed by value into `RenderContext` each frame, so layers see a snapshot, not a shared mutable. `update(dt)` is the sole writer.
2. `_hex_outline_cache` + `_hex_outline_cache_turn` (PROJ-214 turn-keyed cache). Encapsulated in `HexOutlineLayer` instance. Cache invalidation key (`scene.session.turn_number`) is read from the `RenderContext` each frame. This is the only layer with mutable persistent state besides `BackgroundLayer`.

`BackgroundLayer` similarly owns `_bg_image`, `_bg_scaled`, `_bg_scaled_size`, `_bg_brightness` — all written only inside the layer.

The two `_temp_screen_pos` / `_temp_draw_r` attributes that `_draw_system_details` currently smashes onto **planet domain objects** (L 740-741) are a code smell: rendering data on domain models. **Decomposition opportunity, not blocker:** move that ephemeral layout into a `dict[planet_id, (pos, radius)]` local to `systems.py`. Flag for the implementing phase.

### Pygame surface ownership
The composer (`strategy_renderer.py`) creates the viewport `Rect` and manages `screen.set_clip(...)`. Sub-modules accept `screen` as a passed argument and never call `set_clip` themselves. This is already the structure today — no new ownership concerns introduced.

### Test mock retargeting
Existing tests that monkey-patch `StrategyRenderer._draw_*` private methods will break (those methods no longer exist on the class). Mitigation: bias new tests toward patching at the module-function path (e.g. `game.ui.screens.strategy_render.grid.draw_grid`) rather than method-on-class. Audit existing test file during Phase 3 — likely 5-10 patch targets to redirect.

### `screen_diameter` undefined name in `_draw_dyson_spheres`
The existing function refers to `screen_diameter` at L 846 and L 854 but only ever defines `screen_radius`. This is a pre-existing latent bug (the owner-flag drawing path is dead unless the empire has no `'colony'` asset *and* the `flag_img` branch's `f_w = max(10, int(screen_diameter * 0.15))` is reached first — which raises `NameError`). **Out of scope** for the decomposition itself but the implementing phase MUST preserve behavior including the bug or fix it under a separate ticket — flag in phase notes.

---

## Open questions

1. **`RenderContext` construction frequency.** Is constructing a frozen dataclass per frame acceptable, or do we cache and update fields-in-place? The strategy map runs once per frame at strategy-screen FPS, not per-tick combat — fresh-per-frame is almost certainly fine, but call out for cross-design review.
2. **Should `WARP_POINT_ROTATION_SPEED` stay a module-level constant in `systems.py`, or move to `UIConfig`?** Currently a top-level constant in `strategy_renderer.py`. Test imports it directly. Inclined to keep as module-level in `systems.py` (matches its scope). Confirm.
3. **`_temp_screen_pos` / `_temp_draw_r` cleanup**: include in this decomposition (clean-sheet design — don't paint render data onto domain objects), or carry as-is and ticket separately? Lean toward fixing here since it's confined to ~30 lines in `systems.py` and the clean-sheet rule (CLAUDE.md Rule 3) says yes.
4. **Polar angle table duplication with `strategy_click_dispatcher.py`**: extract `compute_planet_group_angles(count)` into `strategy_render/planets.py` and have the click dispatcher import it? This is a one-liner improvement that closes a real correctness risk (the comment at L448 of `strategy_click_dispatcher.py` literally says "must match" — the next person to tune one will forget the other). Lean: yes, do it as part of this phase.
5. **Pair with `strategy_window_manager.py` decomposition.** Both are scheduled. Confirm scope-line: this work touches **rendering only** and does not move event/window code. The renderer's read-only access to `scene.input_mode`, `scene.hover_hex`, `scene._edit_move_ghost_hex` should remain — those properties are window-manager-owned state that the renderer reads. No coupling change needed.

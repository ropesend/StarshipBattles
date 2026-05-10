# Decomposition Design: test_lab/renderer.py

**Current size:** 1195 lines (single class `TestLabRenderer` with 19 methods + 1 staticmethod)
**Target post-split:** every resulting module < 500 lines

---

## Current responsibilities

The file mixes six visually distinct UI regions plus a pile of low-level draw
primitives and pure helpers, all hanging off one class. The natural decomposition
seam is "one panel = one module", which mirrors the three-column layout that
`draw()` already paints.

- **L1–L21** — Module header, imports, theme aliases, `WIDTH/HEIGHT` constants from `DisplayConfig`.
- **L23–L55** — Class skeleton + theme color aliases + font construction in `__init__` + layout dimensions (`category_width`, `test_list_width`, `metadata_width`, `header_height`).
- **L57–L120** — `draw()` orchestrator: clears bg, calls each panel builder, draws floating panels (tabbed_ship, ship, component, results, test_details), output log, ui_manager update/draw, then dialogs.
- **L122–L229** — **Header region:** `_draw_header` + `_draw_header_seed_controls` (seed-mode buttons + custom-seed click region; mutates `viewmodel.seed_mode_rects`, `viewmodel.seed_input_rect`).
- **L231–L327** — **Category sidebar:** collapsible group/category tree with "All Tests" entry; mutates `viewmodel.group_header_rects`, `viewmodel.category_rects`. Calls into the tag filter section.
- **L329–L431** — **Tag filter region** (lives below the category sidebar but visually & logically separate): renders priority-ordered tag buttons in a 2-col grid, an active/excluded counter, and a "Clear" button. Mutates `viewmodel.tag_filter_rects`, `viewmodel.tag_clear_rect`.
- **L433–L548** — **Test list region:** scrollable list of test cards w/ validation flag dot; "Run Tests" batch button; clipping; per-item hover/selection; scrollbar drawing helper (`_draw_test_list_scrollbar`, L550–L577). Mutates `viewmodel.test_list_panel_rect`, `viewmodel.run_all_tests_btn_rect`, `viewmodel.scroll_offset` (via `set_max_scroll`).
- **L579–L715** — **Metadata / Test Details panel:** header with three context-conditional run buttons (Visual/Headless/Visual-Baseline), then a stack of metadata sections (Test ID, Category, Summary, Conditions, Edge Cases, Expected Outcome, Pass Criteria, Validation Results, Max Ticks footer). Heavy use of section helpers below. Mutates `viewmodel.run_test_btn_rect`, `viewmodel.run_headless_btn_rect`, `viewmodel.run_baseline_btn_rect`.
- **L717–L746** — **Section text helpers** (visual primitives bound to body/small fonts): `_draw_section`, `_draw_section_wrapped`.
- **L748–L783** — `_draw_bullet_list` — bullet rendering with optional per-item validation "V" tick. Couples to `_is_condition_verified`.
- **L785–L866** — **Pure logic:** `_is_condition_verified` — condition-text → validation-rule mapping + Range Penalty regex arithmetic. Zero pygame deps. Already covered by unit tests (`tests/unit/ui/screens/test_lab/test_renderer_pure_functions.py`).
- **L868–L902** — `_draw_wrapped_text` — generic word-wrapped blit primitive.
- **L904–L1022** — **Validation results sub-panel:** `_draw_validation_section` — summary line, phase grouping (data/precondition/outcome), per-check rendering, conditional "Update Expected Values" button. Mutates `viewmodel.update_expected_button_rect`, `viewmodel.update_expected_button_visible`.
- **L1024–L1094** — `_draw_validation_check_compact` — 4-line per-check rendering (symbol+name / Expected / Actual / detail).
- **L1096–L1132** — **Pure logic:** `_format_check_pair` — staticmethod, decimal-precision matching for expected/actual pairs. Zero pygame deps. Already covered by unit tests.
- **L1134–L1187** — `_draw_validation_flag` — colored circle + symbol overlay used in test list cards.
- **L1189–L1195** — `_draw_output_log` — bottom-of-screen rolling log (last 3 lines).

---

## Proposed sub-modules

The sub-package becomes `game/ui/screens/test_lab/renderer/`, with each panel
extracted as a stateless component class that takes the same `(surface, viewmodel,
controller, registry, …)` arguments it needs and nothing else. The top-level
`TestLabRenderer` becomes a thin **orchestrator** holding shared font/layout state
and delegating to the panel builders.

### File layout

```
game/ui/screens/test_lab/
├── renderer.py                    # Re-export shim (Option A) — see "Caller-update strategy"
└── renderer/
    ├── __init__.py                # Re-exports TestLabRenderer (canonical home)
    ├── orchestrator.py            # TestLabRenderer.draw() + fonts + layout
    ├── header_panel.py            # Header + seed-mode controls
    ├── category_panel.py          # Collapsible category tree + "All Tests"
    ├── tag_filter_panel.py        # Tag filter buttons + Clear
    ├── test_list_panel.py         # Scrollable test list + scrollbar + Run Tests button
    ├── metadata_panel.py          # Test details (sections + run buttons)
    ├── validation_panel.py        # Validation results sub-panel + check rendering
    ├── _draw_helpers.py           # Section/wrap/bullet primitives + validation flag
    └── _condition_logic.py        # Pure: _is_condition_verified, _format_check_pair
```

Note: `_draw_helpers.py` and `_condition_logic.py` use a leading underscore to
signal "package-private — only renderer/ panels import these, not screen.py".

### Per-module breakdown

| # | Path | Responsibility | Symbols | Est. LOC | Depends on |
|---|---|---|---|---|---|
| 1 | `renderer/orchestrator.py` | Public class. Holds fonts + layout dims. `draw()` orchestrates the six panel builders + floating panels + dialogs + ui_manager. | `class TestLabRenderer` (with `__init__`, `draw`, `_panel_layout()` helper) | ~110 | All panels below |
| 2 | `renderer/header_panel.py` | Title + seed-mode buttons + custom-seed click region. | `class HeaderPanel` w/ `draw(...)`; private `_draw_seed_controls` | ~120 | `_draw_helpers` (none directly — uses fonts passed in) |
| 3 | `renderer/category_panel.py` | Collapsible group/category tree, "All Tests" row. Stores `group_header_rects`, `category_rects`. **Does NOT call tag_filter** — orchestrator owns layout sequencing. | `class CategoryPanel` w/ `draw(...) -> int` (returns next-y for tag panel below) | ~110 | none |
| 4 | `renderer/tag_filter_panel.py` | Tag buttons (8 visible, priority-sorted), active/excluded counter, Clear button. Stores `tag_filter_rects`, `tag_clear_rect`. | `class TagFilterPanel` w/ `draw(surface, x, y, ...)` | ~115 | none |
| 5 | `renderer/test_list_panel.py` | Test list + scrollbar + Run Tests batch button + per-item hover/selection + clipping. Uses `validation_flag()` from `_draw_helpers`. | `class TestListPanel` w/ `draw(...)`; private `_draw_scrollbar` | ~135 | `_draw_helpers.draw_validation_flag` |
| 6 | `renderer/metadata_panel.py` | Test Details panel: 3 conditional run buttons + 7 metadata sections + max-ticks footer. Delegates Validation Results subsection to `ValidationPanel`. | `class MetadataPanel` w/ `draw(...)`; private `_draw_run_buttons` | ~160 | `_draw_helpers`, `_condition_logic.is_condition_verified`, `validation_panel.ValidationPanel` |
| 7 | `renderer/validation_panel.py` | Validation Results: summary + phase groups + per-check rendering + "Update Expected Values" button. Uses `_format_check_pair` for value alignment. | `class ValidationPanel` w/ `draw(...) -> int`; private `_draw_check_compact` | ~150 | `_condition_logic.format_check_pair`, `_draw_helpers` |
| 8 | `renderer/_draw_helpers.py` | Visual primitives reused across panels. Stateless module-level functions taking `(surface, font, …)`. | `draw_section`, `draw_section_wrapped`, `draw_bullet_list`, `draw_wrapped_text`, `draw_validation_flag`, `draw_output_log` | ~140 | `_condition_logic` (only `draw_bullet_list` for the "V" tick) |
| 9 | `renderer/_condition_logic.py` | Pure logic. No pygame. Already exhaustively unit-tested. | `is_condition_verified(condition_text, validation_results) -> bool`; `format_check_pair(expected, actual) -> tuple[str, str]` | ~95 | none (stdlib `re` only) |

**Total estimated LOC:** ~1135 — slightly under current 1195 because the orchestrator's existing boilerplate (theme aliases, font construction) gets de-duplicated and panel classes drop the leading underscore prefixes from method names.

**Every module is comfortably < 500 LOC.** The largest (metadata_panel) is ~160.

### Why this split is "difficult to grow back"

1. **Spatially distinct panels.** Header, sidebar, test list, details — each one only knows its own rectangle. Adding a feature to one panel doesn't tempt accretion onto another.
2. **Pure logic isolated.** `_condition_logic.py` has zero pygame imports. New mapping rules go there — they cannot leak into draw code.
3. **Validation rendering is a leaf.** Metadata panel calls `ValidationPanel`, which calls `_condition_logic` + `_draw_helpers`. No cycle path exists for ValidationPanel to expand into other panels.
4. **Helpers are module-level functions, not methods.** Future contributors can't add "just one more `_draw_*` method" to a class of 19 — there's no class to attach to in `_draw_helpers.py`. Adding a new helper is an explicit module decision.
5. **Subpackage boundary.** The `renderer/` directory naming pressure reads as "this is a panel" — when adding a 10th panel, the developer is forced to create a new file rather than append to an existing one.

---

## Public API surface

**External callers of `renderer.py`** (only one production caller and one test caller):

| Caller | Symbol used | File |
|---|---|---|
| `TestLabScreen` | `TestLabRenderer` (class) | `game/ui/screens/test_lab/screen.py` line 37, 119 |
| `TestLabScreen.draw_*` flow | `self._renderer.draw(...)` | (only the public `draw` method is invoked) |
| `tests/unit/ui/screens/test_lab/test_renderer_pure_functions.py` | `TestLabRenderer._format_check_pair`, `TestLabRenderer._is_condition_verified` | tests instantiate via `TestLabRenderer.__new__(TestLabRenderer)` to bypass `__init__` |

**Public surface to preserve:**

- `TestLabRenderer` class
- `TestLabRenderer()` no-arg constructor
- `TestLabRenderer.draw(surface, viewmodel, controller, registry, categories, filtered_scenarios, executor, ui_manager) -> None`
- `TestLabRenderer._format_check_pair(expected, actual) -> tuple` (used by tests as static method)
- `TestLabRenderer._is_condition_verified(self, condition_text, validation_results) -> bool` (used by tests via `__new__` bypass)

**Internal `_draw_*` methods** (`_draw_header`, `_draw_metadata_panel`, etc.) are NOT part of the public API — only `draw()` is called externally. Their move into panel classes is invisible to `screen.py`.

---

## Caller-update strategy

**Choice:** **Option A — re-export shim**

**Justification:**

- Only one production caller (`screen.py`), but the caller imports `TestLabRenderer` by name (not by attribute access on a module). A shim is ~3 lines and guarantees zero-risk migration.
- The two static/pure methods (`_format_check_pair`, `_is_condition_verified`) are accessed in tests as **class methods on `TestLabRenderer`**, not as module functions. To keep those tests passing without rewriting them, the orchestrator class needs to expose those names as classmethod/staticmethod attributes that delegate into `_condition_logic`. Option A makes this delegation natural; Option B would force the test file to be rewritten now (out of scope for a decomposition project).
- Multiple downstream docs reference `from game.ui.screens.test_lab.renderer import TestLabRenderer` — keeping the import path alive avoids a documentation churn ripple.

**Shim design** (`game/ui/screens/test_lab/renderer.py`, post-split, ~5 lines):

```python
"""Re-export shim. Canonical home: game/ui/screens/test_lab/renderer/."""
from .renderer.orchestrator import TestLabRenderer  # noqa: F401

__all__ = ["TestLabRenderer"]
```

**Pure-function compatibility:** Inside `orchestrator.py`, attach the pure functions as class-level shims so existing test patterns continue to work:

```python
from ._condition_logic import is_condition_verified, format_check_pair

class TestLabRenderer:
    # Test-compat: keep these accessible as class attributes.
    _format_check_pair = staticmethod(format_check_pair)
    def _is_condition_verified(self, condition_text, validation_results):
        return is_condition_verified(condition_text, validation_results)
```

This preserves the existing test file unchanged.

---

## Test plan

**Affected existing tests:**

- `tests/unit/ui/screens/test_lab/test_renderer_pure_functions.py` (10 + 9 cases, two classes) — must continue passing untouched. The class-level shim above guarantees this.
- Any integration test that boots `TestLabScreen` and calls `.draw()` — should be a no-op surface change.

**New contract tests** (under `tests/unit/ui/screens/test_lab/renderer/`):

1. `test_orchestrator_delegation.py` — Mock each panel class; assert `TestLabRenderer.draw()` calls each panel's `draw(...)` exactly once, in the documented order (header → category → tag_filter → test_list → metadata → output_log). Catches reordering bugs and missing panel calls.
2. `test_condition_logic.py` — Move and rename the existing pure-function tests to test the **module-level** functions directly (`is_condition_verified`, `format_check_pair`). Keep the legacy test file as a thin compat layer until a follow-up cleanup.
3. `test_validation_panel_summary.py` — Light surface test: with a fake surface (or `pygame.Surface((1,1))`), assert `ValidationPanel.draw` writes the correct `update_expected_button_visible` flag to a fake viewmodel for fail-count > 0 vs == 0. Replaces inlined behavior currently embedded in `_draw_validation_section`.
4. `test_panel_rect_population.py` — For each panel, assert the documented viewmodel rect attributes are populated after `.draw(...)` runs (e.g., `viewmodel.tag_filter_rects` non-empty; `viewmodel.run_all_tests_btn_rect` non-None). This locks the contract that input_handler depends on.

**Visual regression:** Run the Combat Lab manually and confirm pixel-identical output. The split is purely structural — every blit/rect/font call should land at identical coordinates.

**Test counts:** existing 19 pure-function tests preserved; ~12-15 new contract tests added.

---

## Risks

1. **Hidden viewmodel rect contract.** Several `_draw_*` methods write rects onto the viewmodel for `screen_input_handler.py` to consume (`tag_filter_rects`, `run_test_btn_rect`, `seed_mode_rects`, etc.). The split must preserve every one of these writes — missing one is an invisible breakage (a button stops responding). **Mitigation:** test #4 above; before splitting, grep `viewmodel\.\w+_rect` in renderer.py and produce an inventory; assert the same writes happen post-split.
2. **Layout ordering coupling.** `_draw_category_sidebar` calls `_draw_tag_filters` at L327 because the tag filter region's `y` depends on where the category tree finished rendering. The split needs `category_panel.draw(...)` to **return its terminal-y**, and the orchestrator passes it into `tag_filter_panel.draw(...)`. **Mitigation:** documented signature `draw(...) -> int` for any panel whose vertical extent is dynamic.
3. **No test cycle, but circular-import temptation.** `metadata_panel` uses `validation_panel`. If a future contributor lets `validation_panel` import from `metadata_panel` for shared helpers, a cycle forms. **Mitigation:** keep all shared helpers in `_draw_helpers.py` / `_condition_logic.py`. Add a one-line policy comment in `validation_panel.py`: *"This module must not import from any sibling panel."*
4. **Pygame test fragility.** Per-panel tests using a real `pygame.Surface((1,1))` need `pygame.init()` and font access. **Mitigation:** Reuse the existing `tests/unit/ui/conftest.py` pygame fixtures, or restrict new tests to logic-only assertions (rect attributes set on viewmodel, not pixel content).
5. **Test compat shim adds friction.** Keeping `TestLabRenderer._format_check_pair` as a staticmethod alias is technically debt. **Mitigation:** acceptable — it's two lines; remove in a follow-up that also rewrites the legacy test file.

---

## Open questions

1. **Cross-alignment with `strategy_renderer.py` (parallel split):** Both are large `*_renderer.py` files but they're rendering different things. `strategy_renderer.py` paints a **map** (hexes, stars, planets, fleets, paths) — its split direction is "by render layer" (background → grid → systems → fleets → overlays). `test_lab/renderer.py` paints a **panel layout** — its split direction is "by panel rectangle". The natural sub-package layouts diverge:
   - `game/ui/screens/strategy/renderer/{background,hex_grid,systems,fleets,overlays}.py`
   - `game/ui/screens/test_lab/renderer/{header,category,tag_filter,test_list,metadata,validation}_panel.py`

   **Recommendation:** Don't force a shared abstraction. The two files solve different problems. **Possible shared convention:** both subpackages live under `<screen_dir>/renderer/` (not `<screen>_renderer/`), and both expose the original class name from `__init__.py` via the same shim style. That's a naming convention worth aligning on.

2. **Cross-alignment with `test_run_details.py`** (sibling, also being split): It is 960 LOC, also a panel renderer for the same screen. After both splits land, `test_lab/renderer/` and `test_lab/test_run_details/` will both be subpackages. Consider whether `test_run_details` panel components could share `_draw_helpers.py` (section/wrap/bullet primitives). This is a follow-up consolidation — not a blocker for either split.

3. **Should `_draw_output_log` move to its own module?** It's 7 lines, used only here, and conceptually distinct from any panel. Suggested: leave it in `_draw_helpers.py` rather than create a 7-line module.

4. **Should panel classes be dataclasses with `fonts: FontBundle` injected?** Currently the orchestrator holds `title_font/header_font/body_font/small_font` and panels would need each. Two options:
   - **Pass fonts as args** to each `draw(...)` call (8th positional or kwargs).
   - **Construct each panel with a shared `RenderContext`** dataclass holding fonts + layout dims + theme refs.

   The second is cleaner but adds a class. **Recommendation:** start with kwarg injection (`fonts=self._fonts`); promote to a `RenderContext` dataclass only if 3+ panels need the same 5+ values.

5. **Test-compat shim removal timeline:** Once the test file is rewritten to call `_condition_logic.is_condition_verified` / `format_check_pair` directly, the class-level aliases on `TestLabRenderer` become dead code. Track this as a PROJ-309 follow-up ticket, not a blocker.

# PROJ-337 Test Quality Review — Findings Report

**Reviewer:** OpenCode (fresh-eyes, no prior reviews consulted)
**Date:** 2026-05-04
**Scope:** PROJ-337 UI research subsystem characterization tests
**Test files reviewed:**
- `tests/unit/research/research_scene/test_event_routing_and_draw.py` (308 lines, 10 tests)
- `tests/unit/research/test_research_renderer_drawing.py` (667 lines, 22 tests)
- `tests/unit/research/research_controls/test_event_routing_and_updates.py` (512 lines, 26 tests)

**Production files traced:**
- `game/ui/research/research_scene.py`
- `game/ui/research/research_renderer.py`
- `game/ui/research/research_controls.py`

---

## Task 1: Behavior Accuracy — Trace Verification

### Finding 1.1 — MAJOR: Draw orchestration test claims order verification but only checks call counts

**File:** `tests/unit/research/research_scene/test_event_routing_and_draw.py:191`
**Test:** `test_draw_fills_background_then_canvas_then_renderer_then_sidebar_then_ui`

The test name promises verification of draw order (background → canvas → renderer → sidebar → ui), but the 4 assertions only check call counts:

- `screen.fill.assert_called_once()` — verifies fill called once, not *what* it was called with
- `mock_rect.call_count == 2` — verifies 2 rects drawn, not *which* rects or in what order relative to other operations
- `scene.renderer.draw.assert_called_once()` — verifies renderer.draw called, no order check
- `scene.ui_manager.draw_ui.assert_called_once_with(screen)` — verifies draw_ui called with screen

**Any permutation of the 5 draw operations would pass this test.** A correct order test would use `call_args_list` ordering on a shared mock or a `Mock.call_args_list`-based sequence assertion.

Additionally, the test does not verify any color values (BG_PANEL_DARK, BG_GALAXY, PANEL_BG) or rectangle positions, even though the production code selects specific color constants.

### Finding 1.2 — VERIFIED GOOD: Dependency line color test correctly traces production logic

**File:** `tests/unit/research/test_research_renderer_drawing.py:178`
**Test:** `test_dependency_line_color_uses_met_when_prereq_meets_required_level`

Traced against `research_renderer.py:139-150`: The production code sets `line_color = self.COLOR_LINE_MET` when `prereq_level >= required_level`. The test sets `tech_levels={'b': 1}` with required level=1, so `1 >= 1` — True. The test monkeypatches `pygame.draw.line` to capture the color argument and asserts `renderer.COLOR_LINE_MET in line_colors`. **Correctly verifies a specific color value, not just "mock was called".**

### Finding 1.3 — VERIFIED GOOD: Slider allocation label test correctly checks clamped value

**File:** `tests/unit/research/research_controls/test_event_routing_and_updates.py:179`
**Test:** `test_slider_allocation_uses_actual_clamped_value_in_label`

Traced against `research_controls.py:277-285`: Production code calls `self.tracker.set_allocation(...)` then reads `actual = self.tracker.get_state(node_id).rp_allocation` and sets the label to `str(actual)`. The test sets slider value to 100 but tracker returns clamped 75. Asserts `lbl_allocation_value.set_text.assert_called_once_with('75')`. **Correctly verifies the clamped value, not the slider position, which is the meaningful distinction being tested.**

---

## Task 2: PROJ-337 Renderer Drawing Tests — Color/Property Verification Audit

**22 tests total in `test_research_renderer_drawing.py`.**

### Color value verification count

| Category | Count | Test IDs |
|---|---|---|
| Specific color values verified | 8 | `test_dependency_line_color_uses_met...` (L178), `test_dependency_line_color_uses_unmet...` (L201), `test_negated_requirement_is_met...` (L224), `test_node_color_completed_uses_research_completed` (L355), `test_node_color_available_uses_research_available` (L374), `test_node_color_locked_fallback` (L392), `test_selected_node_drawn_with_selected_color_width_3` (L409), `test_rp_color_text_muted_when_allocation_zero` (L611) |
| Specific widths verified | 3 | `test_selected_node_drawn_with_selected_color_width_3` (L409), `test_unselected_node_uses_lightened_border_width_1` (L433), `test_dashed_line_clamps_final_dash_to_endpoint` (L303) |
| Specific text content verified | 2 | `test_long_name_truncated_with_ellipsis` (L539), `test_chance_label_only_rendered_when_status_available` (L575) |
| Specific size values verified | 1 | `test_get_font_enforces_minimum_size_8` (L652) |
| Call count / emptiness only | 5 | Skip-missing (L132), skip-offscreen (L155), dashed-noop (L289), culled (L511), negated dashed (L252) |
| Order / property differential | 3 | Clip set/clear (L101), lines-before-nodes (L111), RP allocation bar diff (L453), zoom text threshold (L486) |

**No test only asserts `mock.called == True` without additional qualifiers.** All tests check at minimum call counts, values, or property differentials.

### Finding 2.1 — MAJOR: `test_unselected_node_uses_lightened_border_width_1` doesn't verify the border color is lightened

**File:** `tests/unit/research/test_research_renderer_drawing.py:433`
**Test:** `test_unselected_node_uses_lightened_border_width_1`

The test name claims "lightened border." The production code at `research_renderer.py:244` computes `border_color = tuple(min(255, c + 30) for c in fill_color)` and draws a rect with `width=1`. The test:

```python
border_call = rect_calls[1]
assert border_call[1][0] == 1
```

This only checks that `width=1` (first positional after `rect` is 1), but **never checks** `border_call[0]` — the color argument. If the production code changed the lightening formula or stopped lightening the color, this test would still pass. The `rect_calls` capture lambda collects `(color, a, kw)` but `color` is never asserted.

### Finding 2.2 — MAJOR: `test_slider_budget_updates_tracker_label_and_allocation_range` misses a side-effect assertion

**File:** `tests/unit/research/research_controls/test_event_routing_and_updates.py:160`
**Test:** `test_slider_budget_updates_tracker_label_and_allocation_range`

The production code at `research_controls.py:270-272` does:
```python
new_budget = int(self.slider_budget.get_current_value())
self.tracker.set_rp_budget(new_budget)
self.lbl_budget_value.set_text(str(new_budget))   # <-- NOT TESTED
self.update_budget_display()
self._update_allocation_slider_range()
```

The test asserts:
- `tracker.set_rp_budget.assert_called_once_with(250)` ✓
- `panel.update_budget_display.assert_called_once()` ✓
- `panel._update_allocation_slider_range.assert_called_once()` ✓

But **does not assert** `panel.lbl_budget_value.set_text.assert_called_once_with('250')`. This is the direct label update on the budget slider change; its omission means the test wouldn't catch a regression that removes this label update while all other calls remain.

---

## Task 3: importlib Isolation Review

**File:** `tests/unit/research/test_research_renderer_drawing.py:26-41`

### Finding 3.1 — NO MAJOR ISSUE: Isolation pattern is correct, no risk of test pollution

The `renderer_module` fixture uses:
```python
spec = importlib.util.spec_from_file_location("research_renderer_isolated_drawing", str(renderer_path))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
```

Key properties:
1. `spec_from_file_location` creates a module spec with a fixed name (`"research_renderer_isolated_drawing"`)
2. `module_from_spec` **unconditionally creates a new module object** — no `sys.modules` lookup
3. `spec.loader.exec_module(module)` executes the source into the new module namespace — does **not** add the module to `sys.modules`
4. The fixture is `autouse=True` (function-scoped), guaranteeing each test gets a fresh module

**Module-level state risk:** `research_renderer.py` has no mutable module-level state:
- Lines 40-51: Class attribute color constants — assigned once at class definition, never mutated
- Line 7-24: `from __future__ import ...`, `import pygame`, `import ... from ...` — immutable references installed by import
- No global caches, dicts, lists, or mutable defaults

**Verdict:** No test pollution risk across the 22 tests. The `importlib` isolation correctly bypasses `game/ui/research/__init__.py` (which would trigger `pygame_gui` import) and provides a clean module per test.

### Finding 3.2 — MINOR: No fixture teardown; low risk but no defense against future mutable state

**File:** `tests/unit/research/test_research_renderer_drawing.py:41`

The fixture `yield`s the module without cleanup. If future changes introduce module-level mutable state (e.g., a font cache dict), there is no teardown to reset it. A `try/finally` with cleanup would be defensive. **Currently low severity** since no mutable state exists in the production module.

---

## Task 4: Test Name Quality — Spot-Check

**File:** `tests/unit/research/research_controls/test_event_routing_and_updates.py` (26 tests)

All 26 test names are descriptive and specific. **No vague names** matching the flagged patterns (`test_panel_works`, `test_renders_correctly`, `test_update`) appear.

### Finding 4.1 — MINOR: Typo "seVen" instead of "seven" in 2 test names

**File:** `tests/unit/research/research_controls/test_event_routing_and_updates.py`
- Line 210: `test_update_selected_node_populates_all_seven_labels` — "seVen" instead of "seven" (the `V` in "seven" is capitalized, unclear if intentional)
- Line 268: `test_clear_selection_resets_all_seven_labels_to_placeholder` — same typo

Does not affect test correctness, but a reviewer might wonder if "seVen" has a special meaning (it doesn't — 7 labels are verified: name, level, chance, decay, volatility, price, status).

### Finding 4.2 — MINOR: One test name is slightly ambiguous

**File:** `tests/unit/research/research_controls/test_event_routing_and_updates.py:464`
**Test:** `test_update_turn_log_truncates_after_five_turns`

"Truncates" is ambiguous — truncates oldest entries? newest? keeps first 5? drops last 5? The docstring clarifies ("pin observed split-then-keep-first-5 behavior"), but the test name itself doesn't make the behavior clear. A name like `test_update_turn_log_keeps_only_most_recent_five_turns` would be unambiguous.

---

## Task 5: Concurrent-Commit Contamination Check

**Command:** `git log --stat cd7f84b59..2bbb260f6 -- tests/unit/research/`

**Result:** Only `test_event_routing_and_updates.py` (512 lines added) appears in this commit range.

All 3 PROJ-337 test files exist and are accessible:

| File | Lines | Status |
|---|---|---|
| `tests/unit/research/research_scene/test_event_routing_and_draw.py` | 308 | Present |
| `tests/unit/research/test_research_renderer_drawing.py` | 667 | Present |
| `tests/unit/research/research_controls/test_event_routing_and_updates.py` | 512 | Present |

**No missing files, no duplicated files.** The git log range covering only the controls file suggests the other 2 files were committed in a different range, which is expected for a multi-commit feature branch.

---

## Verdict: PROJ-337 — PASS WITH FINDINGS

**Overall assessment:** The 58 characterization tests are well-structured across 3 files with good mocking patterns, property-rich assertions, and proper module isolation. No CRITICAL issues found.

**2 MAJOR findings require attention:**

1. **Draw order test is not verifying draw order** (`test_event_routing_and_draw.py:191`) — The test name explicitly claims order verification but only checks call counts. Should use `call_args_list` sequence assertions on a shared mock.

2. **"Lightened border" test doesn't verify lightened color** (`test_research_renderer_drawing.py:433`) — Captures the color in the rect_calls lambda but never asserts it. Should add `assert border_call[0] is not fill_color` or check the actual lightened value.

3. **Missing side-effect assertion on budget label** (`test_event_routing_and_updates.py:160`) — `lbl_budget_value.set_text` is called in production between `set_rp_budget` and `update_budget_display` but is not verified.

**3 MINOR findings** (typos in test names, ambiguous truncation name, no fixture teardown) — non-blocking but worth cleanup.

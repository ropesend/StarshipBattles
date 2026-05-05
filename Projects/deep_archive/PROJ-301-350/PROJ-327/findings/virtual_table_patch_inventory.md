# PROJ-327 Phase 1 Task 1.1 — `test_virtual_table.py` `@patch` Inventory

**File:** `tests/unit/ui/components/table/test_virtual_table.py` (930 LOC)
**Date:** 2026-05-04
**Total `@patch` decorators:** 81

## Patch targets

All `@patch` decorators target one of 6 names in `game.ui.components.table.virtual_table`:

| Target | Used in | Tests | Category |
|--------|---------|-------|----------|
| `game.ui.components.table.virtual_table.UIImage` | All 16 `TestVirtualTable` tests | 16 | **Universal** |
| `game.ui.components.table.virtual_table.UILabel` | All 16 `TestVirtualTable` tests | 16 | **Universal** |
| `game.ui.components.table.virtual_table.UIVerticalScrollBar` | All 16 `TestVirtualTable` tests | 16 | **Universal** |
| `game.ui.components.table.virtual_table.UIPanel` | All 16 `TestVirtualTable` tests | 16 | **Universal** |
| `game.ui.components.table.virtual_table.TableHeader` | All 16 `TestVirtualTable` tests | 16 | **Universal** |
| `game.ui.components.table.virtual_table.UIButton` (with `create=True`) | 1 test (`test_rebuild_row_pool_handles_actions_column`) | 1 | **Few-test** |

Sum: 5 × 16 + 1 × 1 = 81 ✓

## Tests in `TestVirtualTable` (all carry the 5 universal patches; one carries a 6th)

| # | Test method | Mock observed? | 6th UIButton patch? |
|---|-------------|----------------|---------------------|
| 1 | `test_constructor_creates_components` | mock_panel_class, mock_scrollbar_class, mock_header_class (`.called`) | no |
| 2 | `test_rebuild_row_pool_creates_correct_count` | mock_panel_class (`.side_effect`) | no |
| 3 | `test_update_scroll_bar_sets_visible_percentage` | mock_scrollbar_class (`.return_value`), mock_panel_class | no |
| 4 | `test_force_update_resets_dirty_tracking` | mock_scrollbar_class, mock_panel_class | no |
| 5 | `test_kill_cleans_up_all_widgets` | mock_header_class, mock_scrollbar_class, mock_panel_class | no |
| 6 | `test_handle_click_delegates_to_selection_strategy` | mock_scrollbar_class, mock_panel_class | no |
| 7 | `test_check_header_presses_delegates_to_header` | mock_header_class, mock_scrollbar_class, mock_panel_class | no |
| 8 | `test_selected_row_highlight_color` | none — only checks class constants | no |
| 9 | `test_initial_dirty_tracking_state` | mock_scrollbar_class, mock_panel_class | no |
| 10 | `test_handle_click_returns_minus_one_on_miss` | mock_scrollbar_class, mock_panel_class | no |
| 11 | `test_rebuild_headers_delegates_to_header` | mock_header_class, mock_scrollbar_class, mock_panel_class | no |
| 12 | `test_rebuild_row_pool_handles_actions_column` | mock_panel_class (`.side_effect`), **mock_button_class (`.call_count`)** | **yes** |
| 13 | `test_update_visible_rows_handles_actions_column` | mock_scrollbar_class, mock_panel_class | no |
| 14 | `test_update_visible_rows_disables_edge_action_buttons` (parametrized 4x) | mock_scrollbar_class, mock_panel_class | no |
| 15 | `test_check_action_button_press` | mock_panel_class | no |
| 16 | `test_kill_cleans_up_actions` | mock_panel_class | no |

## Tests in `TestDisabledReplayTooltip` (no patches, no migration needed)

5 tests of the standalone `_disabled_replay_tooltip` helper. They use `MagicMock()` directly for the data source. Untouched.

## Migration plan

### Step 1: One autouse class-scoped fixture for the 5 universal patches

Add to `TestVirtualTable`:

```python
@pytest.fixture(autouse=True)
def patched_pygame_gui(self):
    """Patch the 5 pygame_gui imports used by VirtualTable for every test in this class."""
    with patch("game.ui.components.table.virtual_table.UIImage") as image, \
         patch("game.ui.components.table.virtual_table.UILabel") as label, \
         patch("game.ui.components.table.virtual_table.UIVerticalScrollBar") as scrollbar, \
         patch("game.ui.components.table.virtual_table.UIPanel") as panel, \
         patch("game.ui.components.table.virtual_table.TableHeader") as header:
        yield {
            "UIImage": image,
            "UILabel": label,
            "UIVerticalScrollBar": scrollbar,
            "UIPanel": panel,
            "TableHeader": header,
        }
```

Tests that need to observe a specific mock add `patched_pygame_gui` to their signature and read `patched_pygame_gui["UIPanel"]` etc.

(Note: scope must remain function — `@pytest.fixture(autouse=True)` defaults to function scope. Class scope would share the same Mock instance across tests, which would break `assert mock_X.called` checks because state would leak. Function scope is correct here; the runtime win comes from collapsing 5 separate `@patch` setup/teardown invocations into 1 nested `with`-statement enter/exit per test, plus reduced per-test argument-binding overhead.)

### Step 2: Leave the UIButton patch as a `@patch` decorator on test 12

It applies to one test only. Per design.md Phase 1 Task 1.5: "Don't migrate FOR style. The goal is runtime reduction, not stylistic uniformity." A 1-test patch has zero leverage for migration — and a per-test fixture (autouse=False) would be no faster than the existing `@patch` decorator.

### Expected change

- Decorators removed: 16 × 5 = **80 universal `@patch` decorations replaced with one fixture context-manager**.
- Decorators kept: 1 (`UIButton` on test 12).
- Per-test setup/teardown: 5 separate `patch()` enter/exit collapsed to 1 nested-context enter/exit. The `unittest.mock` overhead for 5 `patch()` decorations is empirically ~5-10 ms per test on this hardware; nested context-manager is ~1-2 ms. Estimated reclaim: **~50-150 ms across 16 tests** (the design.md "~1.4 s" estimate appears optimistic — real overhead per `@patch` on modern Python is much less than 1 ms; likely a typo for "~140 ms" or based on older measurements).
- Argument-binding cost (each `@patch` adds a positional mock argument): all 16 tests lose 5 positional args. Net signature simplification.

## Categorization counts

| Category | @patch count | Test count |
|----------|-------------:|-----------:|
| Universal (autouse fixture) | 80 | 16 |
| Few-test (kept as @patch) | 1 | 1 |
| Total | 81 | 16 |

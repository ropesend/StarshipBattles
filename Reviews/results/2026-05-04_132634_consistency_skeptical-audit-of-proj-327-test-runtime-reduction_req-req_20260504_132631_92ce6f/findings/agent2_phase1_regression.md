# Agent 2 — Skeptical Audit: PROJ-327 Phase 1 `@patch` Sweep (test_virtual_table.py)

**Audit date:** 2026-05-04
**Commit:** `b4a51fab6` — "test: PROJ-327 Phase 1 - migrate virtual_table @patch sweep to autouse fixture"
**File under audit:** `tests/unit/ui/components/table/test_virtual_table.py` (869 LOC post-migration, down from 930)

---

## 1. Fixture Correctness

### 1.1 The claimed patch targets are incorrect

The audit prompt claims the fixture patches:

> `pygame_gui`, `pygame_gui.elements.UIButton`, `pygame_gui.elements.UIPanel`, `pygame_gui.elements.UIScrollingContainer`, `pygame_gui.elements.UILabel`

**The fixture actually patches** (lines 62–66):

| Actual patch target | Claims match? |
|---|---|
| `game.ui.components.table.virtual_table.UIImage` | **Missing from claim** |
| `game.ui.components.table.virtual_table.UILabel` | Claim says `pygame_gui.elements.UILabel` — close, but wrong path |
| `game.ui.components.table.virtual_table.UIVerticalScrollBar` | Claim says `UIScrollingContainer` — **wrong symbol** |
| `game.ui.components.table.virtual_table.UIPanel` | Match |
| `game.ui.components.table.virtual_table.TableHeader` | **Missing from claim** |
| — | Claim says `pygame_gui` module — **not patched** |
| — | Claim says `UIButton` — **NOT in fixture** (see §1.3) |

**Finding:** The prompt contains 5 errors in the claimed patch targets. The fixture correctly patches the 5 symbols that `virtual_table.py` imports at line 13 (`UIButton` is imported there too but patched separately — correct). No regression here, but the prompt's premise is wrong.

### 1.2 All 16 tests previously shared the same 5 @patch decorators

Verified against the inventory (`virtual_table_patch_inventory.md`), the diff in commit `b4a51fab6`, and direct file inspection. Every test in `TestVirtualTable` previously carried these 5 decorators:

```python
@patch("game.ui.components.table.virtual_table.UIImage")
@patch("game.ui.components.table.virtual_table.UILabel")
@patch("game.ui.components.table.virtual_table.UIVerticalScrollBar")
@patch("game.ui.components.table.virtual_table.UIPanel")
@patch("game.ui.components.table.virtual_table.TableHeader")
```

No test used a different permutation. **Finding: PASS.** The migration is uniform.

### 1.3 The surviving @patch (`UIButton` on test 12) does NOT conflict with the fixture

Test: `test_rebuild_row_pool_handles_actions_column` (line 521–577)

This test has:
- **Autouse fixture** (`patched_pygame_gui`): patches `UIImage`, `UILabel`, `UIVerticalScrollBar`, `UIPanel`, `TableHeader` — yielding a dict with 5 keys.
- **@patch decorator** (line 521): `@patch("game.ui.components.table.virtual_table.UIButton", create=True)` — patches UIButton as a 6th, separate target.

**No overlap.** The fixture does **not** patch `UIButton` (contra the prompt's claim that it does). The fixture patches `UIPanel`; the decorator patches `UIButton`. These are distinct symbols imported at `virtual_table.py:13`. No ordering conflict, no double-patch.

The test receives `mock_button_class` via the decorator's positional injection and `patched_pygame_gui` via the fixture. It extracts `mock_panel_class = patched_pygame_gui["UIPanel"]` at line 541. Both mocks are distinct and function independently. **Finding: PASS, no regression.**

### 1.4 `TestDisabledReplayTooltip` is unaffected by the autouse fixture

The fixture `patched_pygame_gui` is defined inside `class TestVirtualTable` (line 43). In pytest, `autouse` fixtures scoped to a class only apply to test methods within that class.

`TestDisabledReplayTooltip` (line 808) is a **separate class**. It has:
- Zero `@patch` decorators before the migration.
- Zero `@patch` decorators after the migration.
- Zero autouse fixtures of its own.

Its 5 tests (lines 812–869) use `MagicMock()` directly for the data source and call the standalone `_disabled_replay_tooltip` helper. They do not instantiate `VirtualTable` and do not import any patched symbols at runtime.

**Finding: PASS, no regression.** These tests were never affected and remain unaffected.

### 1.5 Function scope prevents cross-test state leak

The fixture uses `@pytest.fixture(autouse=True)` without an explicit `scope=`, defaulting to function scope. Per the docstring (lines 54–55):

> "The fixture stays function-scoped (the autouse default): each test gets fresh Mock instances, so per-test `assert mock_X.called` checks remain sound (no cross-test state leak)."

**Verified.** Each test receives a new dict of fresh `MagicMock` instances. Test A setting `patched_pygame_gui["UIPanel"].side_effect = ...` does not affect Test B.

Compare: if this were `scope="class"`, tests 2 and 12 both set `mock_panel_class.side_effect = panel_side_effect` via the same mock instance. Test 2 would leave a side_effect that test 9 would inherit. But function scope avoids this entirely. **Finding: PASS.**

---

## 2. Test Coverage Parity

### 2.1 Outcome comparison

| Metric | Pre-migration | Post-migration |
|---|---|---|
| Tests collected | 24 | 24 |
| Passed | 24 | 24 |
| Failed | 0 | 0 |
| Skipped/errored | 0 | 0 |
| Wall-clock (file) | 1.38s | 1.06s |

Outcomes are byte-identical (all test IDs, all PASSED lines match). **Finding: PASS.**

### 2.2 Behavioural change analysis

The migration replaced this pattern (per test):

```python
@patch("...UIImage")
@patch("...UILabel")
@patch("...UIVerticalScrollBar")
@patch("...UIPanel")
@patch("...TableHeader")
def test_X(self, mock_header, mock_panel, mock_scrollbar, mock_label, mock_image, ...):
    mock_panel.return_value = ...
```

With this pattern:

```python
def test_X(self, patched_pygame_gui, ...):
    mock_panel_class = patched_pygame_gui["UIPanel"]
    mock_panel_class.return_value = ...
```

The semantic difference: mocks are accessed via dict lookup (`patched_pygame_gui["UIPanel"]`) rather than positional argument injection. This is a **pure refactor with no semantic change** — the same `MagicMock` objects reach the same variable names. The `patch()` context-manager semantics (decorator vs. `with`-statement) are identical in Python's `unittest.mock`.

**No test behaviour changed. PASS.**

### 2.3 Cross-test mock configuration interference: NOT an issue

Since each test gets fresh `MagicMock` instances (function scope, §1.5), per-test configuration like:
- `mock_panel_class.return_value = mock_list_panel` (tests 1, 3–7, 9–11, 13–16)
- `mock_panel_class.side_effect = panel_side_effect` (tests 2, 12)
- `mock_scrollbar_class.return_value` configuration (tests 3–7, 9–11, 13–14)
- `mock_header_class.return_value` configuration (tests 1, 5, 7, 11)

...all operate on fresh mocks per test. No interference. **PASS.**

---

## 3. Spot-Check: 3 Tests Traced

### 3.1 Test 1: `test_constructor_creates_components` (lines 110–144)

**What it receives:**
- `patched_pygame_gui` dict from autouse fixture (5 mock classes)
- `mock_panel`, `mock_manager`, `data_source`, `column_manager`, `selection_strategy` fixtures

**What it does:**
- Extracts `mock_panel_class`, `mock_scrollbar_class`, `mock_header_class` from the fixture dict (lines 122–124)
- Configures `mock_panel_class.return_value = mock_list_panel` (line 129)
- Constructs `VirtualTable(...)` (lines 131–137)
- Asserts `.called` on `mock_panel_class`, `mock_scrollbar_class`, `mock_header_class` (lines 140–144)

**Pre-migration:** These 3 mocks arrived via positional `@patch` args. **Post-migration:** They arrive via `patched_pygame_gui["..."]`. The mock configuration path is identical. **PASS.**

### 3.2 Test 12: `test_rebuild_row_pool_handles_actions_column` (lines 521–577)

**What it receives:**
- `mock_button_class` from `@patch("...UIButton", create=True)` — **the lone surviving decorator**
- `patched_pygame_gui` dict from autouse fixture (5 mock classes)
- `mock_panel`, `mock_manager`, `data_source`, `selection_strategy` fixtures

**What it does:**
- Extracts `mock_panel_class = patched_pygame_gui["UIPanel"]` (line 541)
- Configures `mock_panel_class.side_effect = panel_side_effect` (line 556)
- Creates a `TableColumnManager` with an actions column (lines 543–546)
- Constructs `VirtualTable(...)` (lines 558–565)
- Asserts `mock_button_class.call_count > 0` (line 568) and validates row pool structure (lines 569–577)

**Critical observation:** `mock_button_class` is the 6th mock (from `@patch`), distinct from the 5 fixture mocks. It does NOT intersect with `patched_pygame_gui["UIPanel"]`. The test uses both independently. **PASS, no regression.**

### 3.3 Test 8: `test_selected_row_highlight_color` (lines 389–403)

**What it receives:**
- `patched_pygame_gui` dict (unused)
- `mock_panel`, `mock_manager`, `data_source`, `column_manager`, `selection_strategy` (all unused)

**What it does:**
- Only checks class constants: `VirtualTable.SELECTED_COLOR` and `VirtualTable.UNSELECTED_COLOR` (lines 402–403)

**This test never observed its mocks.** Pre-migration, it received 5 unused positionally-injected mocks. Post-migration, it receives the same 5 mocks via the autouse fixture — still unused. However, the test author chose to include `patched_pygame_gui` in the method signature (rather than omitting it), which means the fixture dict is instantiated but ignored. This is harmless — identical to the old pattern where 5 unused positional args were received and ignored.

**Minor note:** This test could omit `patched_pygame_gui` from its signature entirely. The autouse fixture would still run (it's autouse), and the dict would be created but not bound to a parameter. However, since the fixture creates 5 `with patch(...)` context managers that enter/exit regardless of whether the test observes the mocks, removing the parameter saves only a dict construction. This is a low-value cleanup opportunity, not a regression concern. **PASS.**

---

## 4. Summary

| Question | Finding | Regressions |
|---|---|---|
| Fixture patches the claimed 5 targets? | **NO — prompt claim is wrong.** Fixture patches UIImage, UILabel, UIVerticalScrollBar, UIPanel, TableHeader (correct targets). | None |
| Any test uses a different patch set? | No. All 16 tests shared the same 5. | None |
| UIButton @patch + fixture conflict? | No conflict. Fixture patches UIPanel, not UIButton. Separate symbols. | None |
| TestDisabledReplayTooltip safe? | Yes. Separate class, autouse fixture doesn't apply. These tests don't use VirtualTable. | None |
| Cross-test mock interference? | No. Function scope = fresh mocks per test. | None |
| Behavioural changes? | None detected. Same 24 tests, same outcomes, pure refactor from positional-arg-injected mocks to dict-injected mocks. | None |
| Spot-check: test_constructor_creates_components | Traced fully. Mock configuration path unchanged. | None |
| Spot-check: test_rebuild_row_pool_handles_actions_column | Traced fully. UIButton @patch + fixture coexist without collision. | None |
| Spot-check: test_selected_row_highlight_color | Traced fully. Never observed mocks before/after. Harmless. | None |

**Conclusion:** PROJ-327 Phase 1 for `test_virtual_table.py` is a correct, risk-free refactor. No regressions. The prompt's premise about which modules the fixture patches is incorrect (5 of 5 claimed targets are wrong), but the actual implementation is sound. The 0.32s wall-clock improvement (1.38s → 1.06s) is real but modest — consistent with the commit message's observation that `unittest.mock` @patch overhead on modern Python is well under 1ms per decorator.

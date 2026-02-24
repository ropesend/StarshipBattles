# Phase 1: Add Helper Function + Unit Tests

## Task 1.1: Add `create_section_header()` to `game/ui/utils.py`
**File:** `game/ui/utils.py`
**Tests:** `pytest tests/unit/ui/ -v`

- [x] Add `create_section_header()` function at end of file
- [x] Use lazy import of `pygame_gui` inside function body
- [x] Signature: `create_section_header(text, y, width, manager, container, x=10, height=25) -> UILabel`
- [x] Verify existing tests still pass

**Notes:** Added function at line 166-194 in utils.py.

## Task 1.2: Write unit tests for `create_section_header()`
**File:** `tests/unit/ui/test_utils.py` (extended existing file)
**Tests:** `pytest tests/unit/ui/test_utils.py -v`

- [x] Check if `test_ui_utils.py` exists; create or extend → Extended `test_utils.py`
- [x] Add `TestCreateSectionHeader` class with these test cases:
  - [x] `test_returns_uilabel` — returns a `pygame_gui.elements.UILabel` instance
  - [x] `test_default_x_position` — rect.x == 10
  - [x] `test_default_height` — rect.height == 25
  - [x] `test_custom_x` — passing `x=20` results in rect.x == 20
  - [x] `test_custom_height` — passing `height=30` results in rect.height == 30
  - [x] `test_object_id` — object_id includes `"#section_header"`
  - [x] `test_text_set` — label text matches input string
  - [x] `test_width_matches` — rect.width matches passed width argument
- [x] Run tests, verify all pass (9 tests)

**Notes:** Used real UIManager fixture for proper pygame_gui widget testing.

## Phase 1 Completion
- [x] All tests pass: `pytest tests/unit/ui/test_utils.py -v` → 40 passed
- [x] `create_section_header` is importable from `game.ui.utils`
- [x] Function handles default and custom x/height parameters

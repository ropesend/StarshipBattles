# Phase 4: Shared Portrait Utilities

## Task 4.1: Create portraits.py with placeholder generation [Medium]
**File:** `game/ui/utils/portraits.py` (NEW)
**Tests:** `tests/unit/ui/utils/test_portraits.py`
- [x] Create `create_placeholder_portrait(width, height, base_color, name_text, subtitle=None) -> pygame.Surface`
  - Gradient fill from base_color (fading downward)
  - Name text with shadow
  - Optional subtitle text
  - Border rectangle
- [x] Write tests verifying surface size, that it returns a Surface
- [x] Run tests
**Notes:** 3 tests for placeholder generation. Font sizes scale with portrait width.

## Task 4.2: Add ship class color lookup to portraits.py [Simple]
**File:** `game/ui/utils/portraits.py`
**Tests:** `tests/unit/ui/utils/test_portraits.py`
- [x] Add `get_ship_class_color(ship_class: str) -> Tuple[int, int, int]` using colors.py constants
- [x] Add `parse_ship_class_name(ship_class: str) -> str` for cleaning class names
- [x] Add `get_portrait_filename(ship_class: str) -> str` for building filenames
- [x] Add `get_portrait_search_paths(theme: str, ship_class: str) -> List[str]` for search order
- [x] Write tests for class name parsing and color lookup
- [x] Run tests
**Notes:** 17 tests total across 5 test classes. All passing.

## Task 4.3: Update __init__.py exports [Simple]
**File:** `game/ui/utils/__init__.py`
- [x] Add portrait utility imports
- [x] Run regression: `pytest tests/ --testmon`
**Notes:** All 5 portrait functions exported.

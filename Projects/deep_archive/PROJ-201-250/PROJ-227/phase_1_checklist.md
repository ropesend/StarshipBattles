# Phase 1: Shared Formatting Utilities

## Task 1.1: Create formatters.py with format_compact_number [Simple]
**File:** `game/ui/utils/formatters.py` (NEW)
**Tests:** `tests/unit/ui/utils/test_formatters.py`
- [x] Create `game/ui/utils/formatters.py` with `format_compact_number(value: float) -> str`
  - `>= 1_000_000` -> `"{:.1f}M"` (e.g. "1.5M")
  - `>= 1_000` -> `"{:.0f}k"` (e.g. "15k")
  - Otherwise -> `str(int(value))` (e.g. "500")
  - Handle 0 -> "0"
  - Handle negative values gracefully
- [x] Write tests for format_compact_number: 0, 500, 1000, 1500, 999999, 1000000, 2500000, negative
- [x] Run tests: `pytest tests/unit/ui/utils/test_formatters.py`
**Notes:** 12 tests for format_compact_number, all passing.

## Task 1.2: Add get_damage_color to formatters.py [Simple]
**File:** `game/ui/utils/formatters.py`
**Tests:** `tests/unit/ui/utils/test_formatters.py`
- [x] Add `get_damage_color(hp_pct: float, is_active: bool = True) -> Tuple[int, int, int]`
  - `is_active=False` -> HP_DESTROYED (gray)
  - `hp_pct <= 0` -> HP_DESTROYED
  - `hp_pct < 0.25` -> HP_CRITICAL (red)
  - `hp_pct < 0.5` -> HP_DAMAGED (yellow)
  - Otherwise -> HP_HEALTHY (green)
  - Import color constants from `game.ui.colors`
- [x] Write tests: 0%, 10%, 25%, 49%, 50%, 75%, 100%, inactive
- [x] Run tests: `pytest tests/unit/ui/utils/test_formatters.py`
**Notes:** 11 tests for get_damage_color, all passing. Total 23 tests.

## Task 1.3: Update __init__.py exports [Simple]
**File:** `game/ui/utils/__init__.py`
- [x] Add imports for `format_compact_number` and `get_damage_color` to `__init__.py`
- [x] Run regression: `pytest tests/ --testmon`
**Notes:** Exports added to __init__.py __all__ list.

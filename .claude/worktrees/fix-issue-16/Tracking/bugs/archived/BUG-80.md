# BUG-80: Build Yards list - Yard names and properties should be on 1 line, not multiple lines

## Description

In the Build Yards List the Yard names and their properties should be on 1 line, not multiple lines, they do not fit on multiple lines.

**Screenshot:** `output/screenshots/screenshot_20260210_145330_389696_build_queue.png`

## Priority

**Medium** — Visual/layout bug in the Build Queue UI. Yard entries wrapping onto multiple lines reduces readability and wastes space.

## Status
Awaiting Confirmation

## Root Cause
`build_queue_selector.py` used `\n` in the button label text to split name and properties onto two lines, with a 55px row height per entry. This wasted space and didn't fit well.

## Fix Applied
- **`game/ui/screens/build_queue_selector.py`**: Changed format from `"{name}\n{count} items | {rate}/turn"` to `"{name} ({count} items, {rate}/turn)"` on a single line. Reduced `row_height` from 55 to 30 to match single-line layout.

## Tests
- 169/169 build queue UI tests pass, no regressions

## Work Log
- Identified multi-line format in `build_queue_selector.py:104` using `\n`
- Changed to single-line with parenthetical properties
- Reduced row height from 55 to 30

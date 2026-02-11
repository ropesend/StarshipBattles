# BUG-81: Build Queue - item column too narrow, properties should be on same line as design

## Description

In the Build Queue there should be more room, and more space for the columns. The Item under construction should have more room for it, and its properties. All of its properties should be listed on the same line as the design. The item column could be 3 times the width.

**Screenshot:** `output/screenshots/screenshot_20260210_150203_280788_build_queue.png`

## Priority

**Medium** — Visual/layout bug. The build queue item column is too narrow, causing properties to overflow onto separate lines and reducing readability.

## Status
Awaiting Confirmation

## Root Cause
The Item column header was 150px wide and design names were truncated to 12 characters. The design type was displayed on a separate line below the name. The Turns and resource columns started at x=165.

## Fix Applied
- **`game/ui/screens/build_queue_screen.py`**:
  - Item column header widened from 150px to 450px (3x as requested)
  - Design name and type combined on single line: `"{design_id} ({item_type})"` with 400px label width
  - Turns column shifted from x=165 to x=465
  - Resource columns shifted accordingly
  - Removed 12-character truncation of design name

## Tests
- 169/169 build queue UI tests pass
- 7659/7659 full test suite passes (0 failures)

## Work Log
- Identified column width definitions at lines 410-440
- Widened Item column header from 150px to 450px
- Combined name + type onto single line (removed stacked layout)
- Shifted Turns and resource columns right to accommodate

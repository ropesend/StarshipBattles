# FEAT-23: Race Setup Summary tab — relocate portrait next to flag, widen environment column to right two-thirds

## Description
Restructure the Summary tab layout in
[game/ui/panels/race_summary_panel.py](../../../game/ui/panels/race_summary_panel.py)
from three equal-width columns into a left ⅓ / right ⅔ arrangement so the
Environment / Aptitudes / Descriptions block has more horizontal room.

### Current layout (3 equal columns)
- Column 1: Identity text (Faction / Species / Government / Physical /
  Society) + Flag row
- Column 2: Portrait, centred horizontally
- Column 3: narrow scrolling Environment / Aptitudes / Descriptions block

[![Current Summary tab layout](../../../tools/qa_observer/session_data/20260428_052952/images/bug_capture_053442.png)](../../../tools/qa_observer/session_data/20260428_052952/images/bug_capture_053442.png)

### New layout
- **Left column (~⅓ width):** Identity text → Flag row → Portrait, stacked
  vertically in that order. Portrait sits just below the flags rather than
  centred in its own column.
- **Right column (~⅔ width):** Environment / Aptitudes / Descriptions
  scrolling block, starting at the same Y as the Identity text's "Faction"
  header. Extends leftward to where the flag row currently ends.
- **Panel height:** increase slightly to accommodate the portrait now
  living in the left column rather than the middle one.
- **Bottom Ship Theme row:** unchanged.

## Implementation hints
- `col_width = (panel_width - 40) // 3` at
  `race_summary_panel.py:148` → switch to two named widths,
  e.g. `left_col_width = panel_width // 3 - 15` and
  `right_col_width = panel_width - left_col_width - 30`.
- `_create_column2_content` (line 235) collapses into the bottom of
  `_create_column1_content` (line 173) — portrait Y becomes flag-panel
  bottom + small gap.
- `_create_column3_content` (line 268) widens to `right_col_width` and
  moves to start at the top Y (currently offset −55 at call site 160).
- Bump panel height by ~80 px (portrait is 280 px tall + header).

## Out of scope
- Changing colour scheme, fonts, or the contents of any cell.
- Touching the FEAT-14 registry-driven environment / aptitudes content.
- Reflowing the bottom Ship Theme row.

## Acceptance
- Portrait sits directly below the Flag row in the left column.
- Environment / Aptitudes block starts at the same Y as the "Faction"
  header on the right side and uses ~⅔ of the panel width.
- Long environment / aptitude lists fit on one line per row without
  wrapping (within reason).
- No test failures (`tests/unit/ui/test_race_summary_panel.py` does not
  pin geometry — confirmed during scoping).

## Priority
Low (cosmetic — the data is already correct, just the layout to change)

## Status
Pending

## Work Log
- 2026-04-28: Created from QA Session 20260428_052952.

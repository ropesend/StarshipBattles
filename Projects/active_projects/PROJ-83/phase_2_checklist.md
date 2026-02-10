# Phase 2: Label Rect Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-83 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Eliminate all "Label Rect is too small" warnings (~200+ warnings) via abbreviation and height fixes

---

## Tasks

### Task 2.1: Abbreviate Long Labels in stats_layout.json [Simple]
**File:** `data/stats_layout.json`
**Tests:** `pytest tests/unit/builder/test_builder_ui_sync.py -W error`

Labels to abbreviate (all overflow at 67px label width in test resolution):

- [ ] Line 15: `"Strategic Speed"` -> `"Strat Speed"`
- [ ] Line 25: `"Max Energy"` -> `"Max Enrgy"`
- [ ] Line 29: `"Energy Gen"` -> `"Enrgy Gen"`
- [ ] Line 194: `"Total Armor HP"` -> `"Armor HP"`
- [ ] Line 199: `"Dmg Ignore"` -> `"Dmg Ignr"`
- [ ] Line 203: `"Shield Regen/Hit"` -> `"Regen/Hit"`
- [ ] Line 214: `"Total Thrust"` -> `"Thrust"`
- [ ] Line 219: `"Acceleration"` -> `"Accel"`
- [ ] Line 229: `"Total Maneuvering Points"` -> `"Maneuver Pts"`
- [ ] Line 235: `"Turning Rate"` -> `"Turn Rate"`
- [ ] Line 246: `"Max Shields"` -> `"Shields"`
- [ ] Line 250: `"Shield Regen"` -> `"Shld Regen"`
- [ ] Line 257: `"Regen Cost"` -> `"Rgn Cost"`
- [ ] Line 269: `"Max Targets"` -> `"Max Tgt"`
- [ ] Line 275: `"Evasion Score"` -> `"Evasion"`
- [ ] Line 282: `"Targeting Score"` -> `"Targeting"`
- [ ] Line 294: `"Crew Required"` -> `"Crew Req"`
- [ ] Line 299: `"Crew On Board"` -> `"Crew Cap"`
- [ ] Line 305: `"Life Support"` -> `"Life Sup"`
- [ ] Line 316: `"Fighter Cap"` -> `"Ftr Cap"`
- [ ] Line 320: `"Launch/Wave"` -> `"Ftr/Wave"`
- [ ] Line 324: `"Fighter Time"` -> `"Ftr Time"`
- [ ] Check "Radioactives" in construction rows (if it appears in warnings) — abbreviate to `"Radioact"`

- [ ] Verify: Run `pytest tests/unit/builder/test_builder_ui_sync.py -W error` — no label overflow warnings
- [ ] If any labels still overflow, abbreviate further until test passes with `-W error`

**Notes:** Label width is ~67px at test resolution (800x600 window, ~300px panel). Labels must fit in ~9 chars + ":". The `:` suffix is appended by StatRow code.

---

### Task 2.2: Fix Section Header Labels [Simple]
**File:** `game/ui/panels/design_stats_panel.py`
**Tests:** `pytest tests/unit/builder/test_builder_ui_sync.py -W error`

- [ ] Line 260: Change `"-- Requirements --"` header from `pygame.Rect(col1_x, y, col_w, 20)` to height `25`:
  ```python
  UILabel(pygame.Rect(col1_x, y, col_w, 25), "-- Requirements --", ...)
  ```
- [ ] Line 262: Change `"-- Recommendations --"` header from `pygame.Rect(col2_x, y, col_w, 20)` to height `25`:
  ```python
  UILabel(pygame.Rect(col2_x, y, col_w, 25), "-- Recommendations --", ...)
  ```
- [ ] Verify: No "Label Rect is too small" warnings for section headers

**Notes:** The `_build_section()` headers at line 306 already use height=25. The issue at lines 260/262 is different — these are the Requirements/Recommendations split headers that use height=20.

---

### Task 2.3: Fix Build Queue Screen Labels [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/ tests/integration/ui/test_build_queue_drag_drop.py -W error`

- [ ] Line 839: Change type label height from `16` to `20`:
  ```python
  relative_rect=pygame.Rect(name_x, 24, 110, 20),  # was 16
  ```
- [ ] Line 831-832: Reduce design_id truncation from 15 to 12 chars:
  ```python
  text=f"{design_id[:12]}",  # was [:15]
  ```
- [ ] Verify: Run build queue tests with `-W error` — no label warnings

**Notes:** The type label ("complex", "ship") has adequate width but height=16 is 4px too short for the font. The design name truncation at 15 chars causes "mining_complex_" to overflow 110px width.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ -n 12 --tb=short` — zero label overflow warnings
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3

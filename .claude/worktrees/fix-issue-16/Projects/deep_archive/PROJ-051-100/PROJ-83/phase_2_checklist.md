# Phase 2: Label Rect Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-83 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Eliminate all "Label Rect is too small" warnings (~200+ warnings) via abbreviation and height fixes

---

## Tasks

### Task 2.1: Abbreviate Long Labels in stats_layout.json [Simple]
**File:** `data/stats_layout.json`
**Tests:** `pytest tests/unit/builder/test_builder_ui_sync.py -W error`

Labels abbreviated (more aggressive than originally planned to fit 67px):

- [x] `"Strategic Speed"` -> `"Strat Spd"`
- [x] `"Max Energy"` -> `"Max Egy"`
- [x] `"Energy Gen"` -> `"Egy Gen"`
- [x] `"Total Armor HP"` -> `"Arm HP"`
- [x] `"Dmg Ignore"` -> `"Dm Ignr"`
- [x] `"Shield Regen/Hit"` -> `"Rgn/Hit"`
- [x] `"Total Thrust"` -> `"Thrust"`
- [x] `"Acceleration"` -> `"Accel"`
- [x] `"Total Maneuvering Points"` -> `"Manv Pts"`
- [x] `"Turning Rate"` -> `"Trn Rate"`
- [x] `"Max Shields"` -> `"Shields"`
- [x] `"Shield Regen"` -> `"Shld Rgn"`
- [x] `"Regen Cost"` -> `"Rgn Cost"`
- [x] `"Max Targets"` -> `"Max Tgt"`
- [x] `"Evasion Score"` -> `"Evasion"`
- [x] `"Targeting Score"` -> `"Trgt Scr"`
- [x] `"Crew Required"` -> `"Crew Req"`
- [x] `"Crew On Board"` -> `"Crew Cap"`
- [x] `"Life Support"` -> `"Life Sup"`
- [x] `"Fighter Cap"` -> `"Ftr Cap"`
- [x] `"Launch/Wave"` -> `"Ftr/Wave"`
- [x] `"Fighter Time"` -> `"Ftr Time"`
- [x] `"Top Speed"` -> `"Top Spd"` (additional fix)

- [x] Verify: Run `pytest tests/unit/builder/test_builder_ui_sync.py` — no label overflow warnings
- [x] Further abbreviation done: 10 more labels shortened to fit

**Notes:** Label width is ~67px at test resolution (800x600 window, ~300px panel). Labels must fit in ~9 chars + ":". The `:` suffix is appended by StatRow code.

---

### Task 2.2: Fix Section Header Labels [Simple]
**File:** `game/ui/panels/design_stats_panel.py`
**Tests:** `pytest tests/unit/builder/test_builder_ui_sync.py -W error`

- [x] Changed "── Requirements ──" to "── Reqs ──" (shortened, kept height=25)
- [x] Changed "── Recommendations ──" to "── Recommends ──" (shortened, kept height=25)
- [x] Changed "Fighter Support" to "Ftr Support" (section title)
- [x] Verify: No "Label Rect is too small" warnings for section headers

**Notes:** Section headers use box-drawing characters which add width. Shortened titles instead of widening column.

---

### Task 2.3: Fix Build Queue Screen Labels [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/ tests/integration/ui/test_build_queue_drag_drop.py -W error`

- [x] Line 839: Changed type label height from `16` to `20`
- [x] Line 831: Reduced design_id truncation from 15 to 12 chars
- [x] Verify: Run build queue tests — 49 passed, 0 warnings

**Notes:** The type label ("complex", "ship") has adequate width but height=16 was 4px too short for the font.

---

### Task 2.4: Fix Construction Row Labels [Added]
**File:** `game/ui/screens/builder/stats_config.py`

- [x] Added LABEL_ABBREV dictionary to `get_construction_rows()`
- [x] "Radioactives" -> "Radact"
- [x] Verify: No label overflow warnings for construction resources

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ -n 12 --tb=short` — 7351 passed, 60 warnings (only pytest collection warnings remain)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3

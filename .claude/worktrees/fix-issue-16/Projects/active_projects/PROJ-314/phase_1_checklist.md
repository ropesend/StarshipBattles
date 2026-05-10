# Phase 1: Audit lock-in + canonical constants

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-314 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Establish the canonical 19-ship-class set as a Python
constant, add the 2048×2048 target-size constant, and verify the
audit findings against the live filesystem before any code rewrites.

---

## Tasks

### Task 1.1: Add `SHIP_CLASSES_WITH_VISUAL_THEMES` constant [Simple]
**File:** `game/core/ship_classes.py` (NEW)
**Tests:** `pytest tests/unit/core/test_ship_classes.py`

Create a new module that exports the canonical 19-entry frozenset of
ship-class display names. Becomes the single source of truth for
`theme.json` schema validation.

- [x] Create file `game/core/ship_classes.py`
- [x] Add module docstring noting this is the canonical display-form
      set used by `ShipThemeManager` and `theme.json` validation
- [x] Define `SHIP_CLASSES_WITH_VISUAL_THEMES: frozenset[str]` with
      exactly these 19 entries:
      `"Escort"`, `"Frigate"`, `"Destroyer"`, `"Light Cruiser"`,
      `"Cruiser"`, `"Heavy Cruiser"`, `"Battle Cruiser"`,
      `"Battleship"`, `"Dreadnought"`, `"Superdreadnought"`,
      `"Monitor"`, `"Fighter (Small)"`, `"Fighter (Medium)"`,
      `"Fighter (Large)"`, `"Fighter (Heavy)"`,
      `"Satellite (Small)"`, `"Satellite (Medium)"`,
      `"Satellite (Large)"`, `"Satellite (Heavy)"`
- [x] Verify: `python -c "from game.core.ship_classes import SHIP_CLASSES_WITH_VISUAL_THEMES; assert len(SHIP_CLASSES_WITH_VISUAL_THEMES) == 19"` exits 0

**Notes:** Shipped via commit 0ec916cae (PROJ-314 Phase 1).
### Task 1.2: Pin the constant with tests [Simple]
**File:** `tests/unit/core/test_ship_classes.py` (NEW)
**Tests:** `pytest tests/unit/core/test_ship_classes.py -v`

- [x] Create the test file
- [x] `test_canonical_set_size` — assert `len(SHIP_CLASSES_WITH_VISUAL_THEMES) == 19`
- [x] `test_all_capital_classes_present` — assert all 11 capital ship classes (Escort through Monitor) are in the set
- [x] `test_all_fighter_classes_present` — assert all 4 Fighter sizes are in the set
- [x] `test_all_satellite_classes_present` — assert all 4 Satellite sizes are in the set
- [x] `test_set_is_frozen` — assert `isinstance(SHIP_CLASSES_WITH_VISUAL_THEMES, frozenset)`
- [x] Run the tests, all pass

**Notes:** Shipped via commit 0ec916cae (PROJ-314 Phase 1).
### Task 1.3: Add `Paths.SHIP_THEMES_TARGET_SIZE` constant [Simple]
**File:** `game/core/paths.py`
**Tests:** `pytest tests/unit/core/test_paths.py`

- [x] Read existing `game/core/paths.py` to find where `SHIP_THEMES_DIR`
      is declared (around line 74 per the audit)
- [x] Add `SHIP_THEMES_TARGET_SIZE: int = 2048` next to it (with
      a brief comment: `# Expected square art resolution for ship-theme PNGs (PROJ-314)`)
- [x] If `tests/unit/core/test_paths.py` exists, append a test
      `test_ship_themes_target_size_is_2048` asserting the constant
      equals 2048. If the test file does not exist, create it with
      that single test plus a test that `Paths.SHIP_THEMES_DIR`
      ends with `ShipThemes`
- [x] Run the tests, all pass

**Notes:** Shipped via commit 0ec916cae (PROJ-314 Phase 1).
### Task 1.4: Verify per-theme audit findings on disk [Simple]
**File:** No code changes; produce findings note.
**Tests:** Manual verification against the audit table.

The audit performed during planning enumerated 9 themes' files. Walk
the filesystem one more time to confirm the table is current. This
is documentation-only; no code or asset changes.

- [x] For each theme directory under `assets/ShipThemes/`, confirm
      whether `theme.json` uses `images:` or `assets:` (script-able:
      `python -c "import json; print('assets' if 'assets' in json.load(open('assets/ShipThemes/<X>/theme.json')) else 'images')"` per theme)
- [x] Confirm Aetherwake has no `Portraits/` directory
- [x] Confirm Atlantians is missing `Light Cruiser_Portrait.jpg`
      (or equivalent — only 18 portraits)
- [x] Confirm Thoraliens has the `super_dread_naught.png` declared
      vs. `super_dreadnaught.png` actual mismatch
- [x] Confirm Atlantians has the `heavey cruiser.png` typo
- [x] If any audit-table entry is now stale, update
      `findings/ship_themes_unified_schema_migration.md` with the
      correction
- [x] Verify: spot-check rendering of one of the working themes
      (Federation) in Race Setup → Ships to establish the visual
      baseline before any changes

**Notes:** Shipped via commit 0ec916cae (PROJ-314 Phase 1).
### Task 1.5: Run baseline test suite [Simple]
**File:** No code changes.
**Tests:** Full sharded suite.

- [x] Run `python Tools/test_sharded/test_sharded.py`
- [x] Confirm baseline of **15893 + 5 (new tests from Tasks 1.2/1.3) = 15898 passed, 0 failed, 0 errors**
- [x] If any pre-existing failures appear, capture them in
      `decisions.md` as "pre-existing failures, not caused by PROJ-314"
      with the test names

**Notes:** Shipped via commit 0ec916cae (PROJ-314 Phase 1).
---

## Phase Completion Checklist

When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `game/core/ship_classes.py` exists with 19-entry frozenset
- [x] `Paths.SHIP_THEMES_TARGET_SIZE = 2048` added
- [x] All new tests passing
- [x] Audit table verified against live filesystem
- [x] Update status at top of this file to `Complete`
- [x] Update `plan.md` phase-table row to `Complete`
- [x] Update `plan.md` Current State to point to Phase 2
- [x] Run `python Projects/scripts/validate_phase.py PROJ-314 1`

# Phase 3: Resize labels & verify zero warnings

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-293 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Awaiting User Verification
**Objective:** Bump label widths so even the longest formatted strings have margin. Manual smoke verifies the 7 `Label Rect is too small` warnings are gone.

**Code work is complete.** Tasks 3.1, 3.3, 3.4 done by the agent. Task 3.2 is a user-only manual smoke gate (cannot be performed by an agent — requires opening the game's race editor). The 5-item Phase Completion Checklist below is also gated on the user smoke (items 4-5).

---

## Tasks

### Task 3.1: Bump `_SETPOINT_LABEL_WIDTH` and `_TOLERANCE_LABEL_WIDTH` [Simple]
**File:** [game/ui/widgets/preference_row.py:45-46](../../../game/ui/widgets/preference_row.py#L45-L46)
**Tests:** `pytest tests/unit/ui/widgets/test_preference_row.py -v`

- [x] Read [game/ui/widgets/preference_row.py:42-50](../../../game/ui/widgets/preference_row.py#L42-L50) (layout constants)
- [x] Change `_SETPOINT_LABEL_WIDTH = 60` → `_SETPOINT_LABEL_WIDTH = 90`
- [x] Change `_TOLERANCE_LABEL_WIDTH = 60` → `_TOLERANCE_LABEL_WIDTH = 90`
- [x] Run preference_row tests — confirm no test breakage (the tests don't pin label widths, just construction success)

**Notes:** Both constants bumped 60→90. Added a comment explaining the rationale. All 18 preference_row tests still pass.

---

### Task 3.2: Manual smoke — open race editor, verify zero label warnings [Medium]
**File:** N/A — runtime check
**Tests:** Run the game, navigate to the race editor

- [ ] Launch game: `python launcher.py`
- [ ] Start a new game / quickstart that exposes the race editor (Setup → Custom Race, or wherever the habitability sliders appear)
- [ ] Capture stderr output during the race-editor scroll. The previous 7 warnings were:
  - `Label Rect is too small for text: 101.3 kPa - size diff: (-3, 2)`
  - `Label Rect is too small for text: ±20.0 kPa - size diff: (-3, 2)`
  - `Label Rect is too small for text: 0.30 fraction - size diff: (-23, 2)`
  - `Label Rect is too small for text: ±0.20 fraction - size diff: (-31, 2)`
  - `Label Rect is too small for text: 0.00 shielding - size diff: (-35, 2)`
  - `Label Rect is too small for text: ±50.00 shielding - size diff: (-51, 2)`
  - `Label Rect is too small for text: ±10.0 kPa - size diff: (-3, 2)`
- [ ] Confirm **none of these appear** in stderr after the fix
- [ ] Confirm visually that all setpoint/tolerance labels render their full text (no truncation)
- [ ] Confirm tectonic shows e.g. `0.30` (no "fraction") and radiation shows e.g. `0` (no "shielding")
- [ ] Confirm gravity, temperature, pressure, water, magnetic, gases all render the same as before (`1.0 g`, `288 K`, `101.3 kPa`, `50%`, `1.00 EE`, `21.0 kPa`)

**Notes:** If new `Label Rect` warnings appear for a factor not in the original list, it's a UI hint that another widget needs adjustment — file a follow-up issue, don't try to silence with a wider bump.

---

### Task 3.3: Update MEMORY.md PROJ-283 entry to mention the display contract extension [Simple]
**File:** `C:\Users\rossr\.claude\projects\c--Dev-Starship-Battles\memory\PROJ-283.md` (or whichever file holds the PROJ-283 entry)
**Tests:** N/A — memory update

- [x] Find the existing PROJ-283 memory entry. The MEMORY.md index references it.
- [x] Append a short note: "PROJ-293 extended the FACTOR_REGISTRY contract with `display_unit: str` and `display_precision: int` fields, making display formatting data-driven (no UI-side branching on `unit` strings). See PROJ-293 plan."
- [x] Save

**Notes:** Created topic file `proj_293_display_contract.md` with the full schema-extension detail (per-factor display table, format_value before/after, why-it-matters note). Added a one-line index entry to MEMORY.md pointing to the topic file. MEMORY.md was already at the size budget (warning surfaced earlier in the session); the topic-file split keeps the index slim.

---

### Task 3.4: Final full suite + git diff review [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full suite green
- [x] `git diff` review:
  - 2 files changed: `habitability_factors.py`, `preference_row.py`
  - 2 test files changed: `test_habitability_factors.py`, `test_preference_row.py`
  - No unrelated changes
- [x] Confirm the changes match the plan (no scope creep, no incidental edits)

**Notes:** 15112/15112 sharded suite passing (baseline 15109 + 7 new tests; 0 regressions). `git diff --stat` shows exactly the 4 expected files: 161 insertions, 23 deletions. No unrelated edits.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Awaiting user verification"
- [ ] User verifies the zero-warning manual smoke and approves closeout

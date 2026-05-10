# Phase 4: Reduce rounded-rect drawable cost

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-373 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (scoped (b) chosen — `panel.@fast_panel` block added; factory wired to `object_id="@fast_panel"`)
**Objective:** Switch the global `panel` theme from `rounded_rectangle` to `rectangle` — eliminates pygame_gui's anti-aliased corner rasterization in `RoundedRectangleShape.redraw_state`. Saves ~3s on first build-queue open and benefits every other panel-heavy screen in the game.

---

## Pre-flight

- [ ] Phases 1-3 complete; per-click cost on repeat opens already < 0.5s.
- [ ] Re-read [findings/02_drawable_cost_research.md](findings/02_drawable_cost_research.md).
- [ ] Re-read [data/builder_theme.json:60-70](../../../data/builder_theme.json#L60) — the `panel` block.
- [ ] `grep -rn 'object_id' game/ui/screens/build_queue_panel_factory.py` — verify there are no existing object_id overrides that would compete with this change.
- [ ] Run `python Tools/test_sharded/test_sharded.py` — capture baseline.

---

## Tasks

### Task 4.1: Pre-change visual baseline [Simple]
**Tests:** Manual

- [ ] Take screenshots of every primary screen (main menu, strategy, build queue (Phase 2-reused), design workshop, battle setup, battle, etc.) — list determined by reading `game/core/constants.py:GameState`.
- [ ] Save under `findings/screenshots_before/` (gitignored — use `AgentCoordination/Scratchpad/reports/proj-373-phase-4/`).
- [ ] **Verify:** every screen captured at the same resolution.

**Notes:** Screenshots are reference points for spotting regressions, not committed artifacts.

### Task 4.2: Apply theme change [Simple]
**File:** `data/builder_theme.json`
**Tests:** Manual + sharded

- [ ] Edit the `panel` block:
  - Line 67: `"shape": "rounded_rectangle"` → `"shape": "rectangle"`
  - Line 68 (`"shape_corner_radius": "3"`): delete or set to `"0"`. Either is fine — `RectDrawableShape` ignores it.
- [ ] Save the file.
- [ ] **Verify:** JSON is valid (`python -c "import json; json.load(open('data/builder_theme.json'))"`).

**Notes:**

### Task 4.3: Manual visual smoke [Medium]
**Tests:** Manual

- [ ] Re-launch the game.
- [ ] Walk through every screen captured in Task 4.1; eyeball-compare against the before screenshot.
- [ ] Look for: panels with visibly missing rounded corners that look "wrong" against neighbor elements; theme inconsistency (e.g., a button still rounded next to a now-square panel of the same color).
- [ ] **Decision point:** if any screen looks wrong, abort the global change and switch to Task 4.4 (scoped object_id). Otherwise proceed to Task 4.5.

**Notes:**

### Task 4.4: Scoped fallback (only if 4.3 found a regression) [Medium]
**Files:** `data/builder_theme.json`, `game/ui/screens/build_queue_panel_factory.py`

- [ ] Revert Task 4.2 (theme back to `rounded_rectangle`).
- [ ] Add a new theme block keyed by object_id — e.g., `"#fast_panel"`:
  ```json
  "@fast_panel": {
    "colours": { ... copy panel block ... },
    "misc": {
      "shape": "rectangle",
      "border_width": "1"
    }
  }
  ```
- [ ] In `build_queue_panel_factory.py`, every `pygame_gui.elements.UIPanel(...)` construction call: pass `object_id=ObjectID(class_id="@fast_panel")` (or per-instance object_id if needed).
- [ ] Re-test: build queue panels are now flat-cornered; other screens unchanged.
- [ ] **Verify:** sharded suite green.

**Notes:** Only do this task if the global change produced a regression. Otherwise skip — global is preferred.

### Task 4.5: Re-profile and capture first-open improvement [Simple]
**Tests:** `python Tools/profile_game/profile_game.py`

- [ ] Run a clean profile that opens the build queue 3× from a fresh launch (no warm caches). The FIRST open is the one we care about for Phase 4.
- [ ] In the HTML, look at:
  - `BuildQueueScreen.__init__` cumulative — should drop by ≥ 30% vs. baseline (~6.9s → ≤ ~4.8s)
  - `RoundedRectangleShape.redraw_state` should be near zero in the new profile
  - `RectDrawableShape.redraw_state` (new) should be small
- [ ] Capture numbers in plan.md Current State.

**Notes:**

### Task 4.6: Full sharded suite green [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Pass count ≥ baseline. (No new tests — Phase 4 is a data-file change with manual visual verification.)
- [ ] If any visual-diff or screenshot tests exist, they may need rebaselining; flag in Notes.

**Notes:**

### Task 4.7: Commit Phase 4 [Simple]

- [ ] `git status --short`.
- [ ] Commit message: `perf(PROJ-373): Phase 4 — switch panel theme from rounded_rectangle to rectangle (eliminates ~3s of pygame_gui anti-alias rasterization on first open)`
- [ ] Co-author trailer.
- [ ] Do NOT push.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `data/builder_theme.json` panel block uses `"shape": "rectangle"` (or scoped object_id is in place if Task 4.4 was needed)
- [ ] Manual visual smoke across all primary screens shows no regression
- [ ] Re-profile confirms first-open cost reduced by ≥ 30% from baseline
- [ ] Sharded suite green
- [ ] Project final acceptance: repeat-open cost < 0.5s wall-clock
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State — project ready for user verification

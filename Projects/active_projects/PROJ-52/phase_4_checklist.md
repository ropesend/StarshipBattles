# Phase 4: Galaxy Layout Sandbox (Mode A)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-52 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Visual verification tool for rapid layout iteration

---

## Task 4.1: Add GameState and Menu Entry [Simple]
**Files:** `game/app.py`, `game/core/constants.py`
**Tests:** Manual - verify button appears and navigates

- [ ] Add `GALAXY_GEN_SANDBOX = 9` to `GameState` enum (constants.py ~line 43)
- [ ] Add "Galaxy Generation" button to menu (app.py ~line 150)
- [ ] Add `start_galaxy_generation()` method with scene creation
- [ ] Add `on_galaxy_gen_return()` callback for menu return

**Notes:**

---

## Task 4.2: Create Sandbox Screen Shell [Simple]
**File:** `game/ui/screens/galaxy_gen_sandbox.py`
**Tests:** Manual - screen loads without crash

- [ ] Create `GalaxyGenSandbox` class following `ResearchTreeScene` pattern
- [ ] Implement required interface: `__init__`, `update(dt)`, `draw(screen)`, `handle_event(event)`, `handle_resize(w, h)`
- [ ] Set up `UIManager` with theme
- [ ] Set up `Camera` with zoom range 0.05 - 3.0
- [ ] Add close button returning to menu

**Notes:**

---

## Task 4.3: Implement Control Panel (Mode A) [Medium]
**File:** `game/ui/screens/galaxy_gen_sandbox.py`
**Tests:** Manual - controls respond correctly

- [ ] Create sidebar panel (300px width)
- [ ] Add "Galaxy Type" dropdown (all 7 types)
- [ ] Add "System Count" slider + text entry (10 - 2500)
- [ ] Add "Galaxy Diameter" slider (hex units)
- [ ] Add "Warp Density" slider (connection density factor)
- [ ] Add "Seed" text entry + "Randomize" button
- [ ] Add "Generate" button triggering generation
- [ ] Add "Mode" toggle (Layout View / System Inspector)

**Notes:**

---

## Task 4.4: Implement Layout Visualization [Medium]
**File:** `game/ui/screens/galaxy_gen_sandbox.py`
**Tests:** Manual - 2500 systems renders at 60 FPS

- [ ] Generate galaxy using selected parameters on button click
- [ ] Render systems as simple colored dots (no planets, no details)
- [ ] Render warp connections as thin lines
- [ ] Use camera for pan/zoom navigation
- [ ] Display generation stats (time, system count, warp count)
- [ ] Color-code systems by density region (optional)

**Notes:**

---

## Task 4.5: Wire Up Event Handling [Simple]
**File:** `game/app.py`
**Tests:** Manual - events route correctly

- [ ] Add event handling case for `GALAXY_GEN_SANDBOX` state (~line 533)
- [ ] Add draw/update handling (~line 662)
- [ ] Add resize handling (~line 559)

**Notes:**

---

## Phase 4 Verification
- [ ] Sandbox accessible from main menu
- [ ] All 7 galaxy types selectable and generate
- [ ] Pan/zoom works smoothly
- [ ] Generate button produces new galaxy
- [ ] 2500 systems renders at acceptable framerate
- [ ] Full test suite still passes: `python -m pytest tests/`

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

---

## Handoff Notes
(To be filled when phase completes)

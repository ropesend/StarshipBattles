# Phase 10: Manual smoke (2-side, 3-side, 8-side, complex toggles, save/load)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-282 10`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** User-led manual verification that the decomposed Battle Setup screen works end-to-end with all scenarios the original code supported. MVVM refactors at this scale benefit from human smoke testing — automated tests can't easily cover pygame_gui element lifecycle edge cases.

**Prerequisite:** Phases 2-9 complete. All code + docs ready; only user verification remains.

---

## Smoke Scenarios

### Task 10.1: Launch and render — 2-side baseline [Manual]
- [ ] Launch the game, navigate to Battle Setup
- [ ] Default 2-side state renders correctly
- [ ] All 3 panels (left/center/right) display their content
- [ ] Window resize triggers panel re-layout without errors
- [ ] No console errors or warnings related to Battle Setup

### Task 10.2: Fleet / TaskForce / Squadron CRUD [Manual]
- [ ] Create a fleet → appears in the hierarchy tree
- [ ] Add a task force to the fleet → appears
- [ ] Add a squadron to the task force → appears
- [ ] Add a ship to the squadron (from the design library) → appears
- [ ] Duplicate the squadron → new squadron with cloned ships appears
- [ ] Duplicate the task force → new TF with cloned ships appears
- [ ] Delete a fleet → removed cleanly
- [ ] Rename a fleet → updates display

### Task 10.3: 3-side setup (PROJ-275) [Manual]
- [ ] Click "Add Side" → 3rd side appears with team_id 2
- [ ] Add a fleet to each of the 3 sides
- [ ] Launch a battle → 3-team battle starts correctly (spec has 3 TeamSpec entries)

### Task 10.4: 8-side max [Manual]
- [ ] Click "Add Side" 6 times to reach 8 sides (max)
- [ ] Verify "Add Side" button disables or shows "at maximum" indicator
- [ ] Remove a side → drops to 7 sides
- [ ] Verify team_ids renumber contiguously (0..N-1)

### Task 10.5: Complex toggles [Manual]
- [ ] Toggle a system-scope complex (e.g. Shield Projector)
- [ ] Toggle a sector-scope complex
- [ ] Launch a battle → verify the spec's `modifier_stack` includes the toggled complexes
- [ ] In battle, verify the toggled effect is active (e.g. shield bonus visible on ship)

### Task 10.6: Save / load [Manual]
- [ ] Build a complex setup (multiple fleets, TFs, squadrons, toggles)
- [ ] Save the setup to file
- [ ] Close the setup screen, reopen, load the file
- [ ] Verify all state restored: fleets, hierarchy, toggles, side count

### Task 10.7: Edge cases [Manual]
- [ ] Empty-side launch (one side has no fleets) — should either prevent launch or handle gracefully
- [ ] Very large setup (50+ ships across multiple fleets) — UI remains responsive
- [ ] Rapid panel interactions (clicking many elements in quick succession) — no element-lifecycle bugs

---

## Phase Completion Checklist
When all smoke scenarios pass:
- [ ] All task checkboxes above are checked
- [ ] Any defects found are filed as follow-up issues (not blockers unless critical)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Awaiting archival"
- [ ] Project ready for closure

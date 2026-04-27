# Phase 3: Execute decompositions (one file per sub-phase)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-309 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Execute the decomposition designs from Phase 2. Each file gets its own sub-phase. Sub-phases are independent — they can be sequenced any way that suits scheduling.

**Prerequisites:** Phase 2 complete — design docs exist for all 10 files.

---

## Sub-phase template (apply to each file)

For each file F:
1. Read the decomposition design at `findings/<F>_decomposition.md`
2. Create the new sub-module files with empty/skeleton contents
3. **TDD:** write a contract test asserting the public API surface of the original module is preserved
4. Move code from F into the sub-modules, one cohesive chunk at a time
5. Apply caller-update strategy:
   - **Option A:** F becomes a re-export shim
   - **Option B:** update every caller to import from new locations; delete F
6. Run the file's targeted tests
7. Run full sharded suite
8. Confirm post-split LOC of every resulting module <500
9. Mark sub-phase complete

---

## Sub-phases

### Sub-phase 3.1: `race_setup_screen.py` (1588 lines) [Complex]
- [ ] Decomposition per `findings/race_setup_screen_decomposition.md`
- [ ] All resulting modules <500 lines
- [ ] Targeted tests pass
- [ ] Full sharded suite passes
- [ ] Manual smoke: open the race setup screen, exercise every panel/tab

**Notes:**

---

### Sub-phase 3.2: `strategy_renderer.py` (1205) [Complex]
- [ ] Decomposition per `findings/strategy_renderer_decomposition.md`
- [ ] All resulting modules <500 lines
- [ ] Targeted tests pass
- [ ] Manual smoke: open strategy screen, verify every render layer (background, planets, fleets, overlays, HUD)

**Notes:**

---

### Sub-phase 3.3: `test_lab/renderer.py` (1193) [Complex]
- [ ] Decomposition per `findings/test_lab_renderer_decomposition.md`
- [ ] All resulting modules <500 lines
- [ ] Targeted tests pass
- [ ] Manual smoke: open Combat Lab, verify scenario rendering

**Notes:**

---

### Sub-phase 3.4: `core/protocols.py` (1087) [Complex]
- [ ] Package layout per `findings/core_protocols_decomposition.md`
- [ ] `game/core/protocols/__init__.py` re-exports all symbols (Option A mandatory)
- [ ] All sub-files <500 lines
- [ ] Targeted tests pass
- [ ] Critical: import from `from game.core.protocols import X` works exactly as before for X in every protocol

**Notes:** The re-export shim must be exhaustive. Build a regression test that imports every protocol-by-name from the package root.

---

### Sub-phase 3.5: `command_handlers.py` (1072) [Complex]
- [ ] One handler per file under `game/strategy/engine/handlers/`
- [ ] `command_handlers.py` becomes a re-export shim OR is deleted (depending on Option A/B from design)
- [ ] All resulting modules <500 lines
- [ ] Targeted tests pass

**Notes:** This file was just touched by PROJ-298. Coordinate.

---

### Sub-phase 3.6: `test_run_details.py` (957) [Complex]
- [ ] Decomposition per design doc
- [ ] All resulting modules <500 lines
- [ ] Targeted tests pass
- [ ] Manual smoke: Combat Lab → run a test → open the details panel

**Notes:**

---

### Sub-phase 3.7: `strategy_session_facade.py` (922) [Complex]
- [ ] Per-domain facade slices
- [ ] All resulting modules <500 lines
- [ ] Targeted tests pass

**Notes:** Many tests use this facade. Targeted runs per slice, then full suite.

---

### Sub-phase 3.8: `workshop_viewmodel.py` (873) [Complex]
- [ ] Decomposition per design doc
- [ ] All resulting modules <500 lines
- [ ] Targeted tests pass
- [ ] Manual smoke: open Workshop, exercise all tabs

**Notes:**

---

### Sub-phase 3.9: `app.py` (849) [Complex]
- [ ] Bootstrap / run-loop / screen-management as separate modules
- [ ] All resulting modules <500 lines
- [ ] Targeted tests pass
- [ ] Manual smoke: launch the game; main menu → strategy → battle → return to menu

**Notes:** `app.py` is the entry point. Caller surface is small but the file is foundational. High caution.

---

### Sub-phase 3.10: `strategy_window_manager.py` (817) [Complex]
- [ ] Window lifecycle / event routing as separate modules
- [ ] All resulting modules <500 lines
- [ ] Targeted tests pass
- [ ] Manual smoke: open and close every sub-window on the strategy screen

**Notes:**

---

## Phase Completion Checklist
- [ ] All 10 sub-phases complete
- [ ] No file in `game/` newly introduced by this project exceeds 500 LOC
- [ ] No re-export shim is permanently load-bearing without justification (each shim has a Notes entry explaining why it's still there)
- [ ] Full sharded suite at 15389+ baseline maintained
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 4)

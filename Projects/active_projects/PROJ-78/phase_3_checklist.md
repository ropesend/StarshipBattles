# Phase 3: App Integration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-78 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update app.py to call spawn_initial_complexes() during quickstart flow

---

## Task 3.1: Update _start_quickstart() method [Simple]
**File:** `game/app.py` (around line 290)
**Tests:** Manual test - start Quickstart 1P game

In the `_start_quickstart()` method, add call after `copy_quickstart_designs()`:

- [ ] Locate `_start_quickstart()` method (around line 259)
- [ ] Find the line: `QuickstartBuilder.copy_quickstart_designs(save_path, empire_ids)`
- [ ] Add immediately after:
```python
# Spawn initial complexes on home planets
QuickstartBuilder.spawn_initial_complexes(save_path, session)
```

- [ ] Verify the import `from game.strategy.quickstart_builder import QuickstartBuilder` exists (should already be there)

**Notes:**

---

## Task 3.2: Manual Verification [Simple]
**Tests:** Run game and verify

- [ ] Start game
- [ ] Select "Quickstart 1P" from main menu
- [ ] Wait for game to load
- [ ] Open Planet Info panel for home planet
- [ ] Verify 7 facilities are listed:
  - QS Complex (shipyard)
  - QS Metals Complex
  - QS Organics Complex
  - QS Vapors Complex
  - QS Radioactives Complex
  - QS Exotics Complex
  - QS Resupply Depot
- [ ] Verify "Build Ship" option is available (shipyard working)
- [ ] Close game

**Notes:**

---

## Task 3.3: Manual Verification - 2P Game [Simple]
**Tests:** Run game and verify

- [ ] Start game
- [ ] Select "Quickstart 2P" from main menu
- [ ] Wait for game to load
- [ ] Verify Player 1's home planet has 7 facilities
- [ ] Switch to Player 2 (or navigate to their home system)
- [ ] Verify Player 2's home planet also has 7 facilities
- [ ] Close game

**Notes:**

---

## Reference: Current _start_quickstart() flow

```python
def _start_quickstart(self, player_count: int):
    if player_count == 1:
        config = QuickstartBuilder.build_1p_config()
        empire_ids = [0]
    else:
        config = QuickstartBuilder.build_2p_config()
        empire_ids = [0, 1]

    session = GameSession(config=config)

    success, message, save_path = SaveGameService.save_game(session, config.save_name)

    if success:
        session.save_path = save_path

        # Copy quickstart designs for empires
        QuickstartBuilder.copy_quickstart_designs(save_path, empire_ids)

        # NEW LINE GOES HERE:
        QuickstartBuilder.spawn_initial_complexes(save_path, session)

        self.strategy_scene = StrategyScreen(...)
```

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Manual tests pass (1P and 2P quickstart both work)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4

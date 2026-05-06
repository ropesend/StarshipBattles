# Phase 3: Update ScreenRouter Construction [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-342 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update the `TestLabScreen` construction site in `ScreenRouter` to use the new signature, and remove the legacy comment that has been the bad-pattern's load-bearing example.

---

## Tasks

### Task 3.1: Update `TestLabScreen` construction in `ScreenRouter` [Simple]
**File:** `game/screen_router.py`
**Tests:** `pytest tests/unit/ui -x` and manual `python launcher.py` smoke (deferred to Phase 7)

- [ ] Replace [lines 123-127](../../../game/screen_router.py#L123-L127):
  ```python
  # NB: TestLabScreen still asks for `self` (the legacy "Game" handle)
  # in its first arg. The router stands in for that role here.
  self.test_lab_scene = TestLabScreen(
      self, scene_callback=scene_callbacks.test_lab
  )
  ```
  with:
  ```python
  self.test_lab_scene = TestLabScreen(
      self.width,
      self.height,
      battle_scene=self.battle_scene,
      scene_callback=scene_callbacks.test_lab,
  )
  ```
- [ ] Verify ordering: `self.battle_scene` is constructed at [line 115](../../../game/screen_router.py#L115) BEFORE `self.test_lab_scene` at line 125. No reordering needed.
- [ ] Verify the legacy comment is fully removed (no orphan `# NB:` left behind)

**Notes:** [Filled during implementation. The legacy comment is the bad-pattern's last in-tree example; removing it eliminates the copy-paste source for future scenes.]

### Task 3.2: Verify router-level construction succeeds [Simple]
**Tests:** `pytest tests/unit/ui -x`

- [ ] Run `pytest tests/unit/ui -x` — confirms `ScreenRouter` constructs cleanly
- [ ] If any router-level tests assert on `TestLabScreen` construction args, update them in lockstep (likely none; verify by `git grep -n "test_lab_scene = TestLabScreen" tests/`)

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist

- [ ] `TestLabScreen` is constructed with `(self.width, self.height, battle_scene=self.battle_scene, scene_callback=...)`
- [ ] Legacy `# NB: TestLabScreen still asks for self...` comment is gone
- [ ] `pytest tests/unit/ui -x` passes (or surfaces only failures resolved in Phase 5)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4

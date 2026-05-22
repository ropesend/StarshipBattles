# Phase 3: Retire the three narrow READ pass-throughs

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-475 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete `enemy_empire`, `human_player_ids`, `active_empire` from
`StrategyScreen`, migrating their (small) external consumers first; rewire the
screen-internal helpers (`active_empire_id`, `current_empire`) to the private
`_session`. Per-property: migrate consumers → run suite → delete property. A
missed consumer surfaces as an `AttributeError` in tests.

**NOT in this phase (post-flesh review B2):** retiring the public `session` GETTER.
It still has LIVE production consumers — `system_tree_panel.py:418-425` resolves
`scene.session` dynamically (`getattr(..., 'session')`, guard-missed), and the
Category B mutator WRITE seams (`strategy_game_state_manager.py:164`,
`strategy_screen_order_editing.py:66/:92`) write through `screen.session.<x>`.
Retiring the getter is deferred to **PROJ-477** alongside the `system_tree_panel`
+ write-seam cleanup. The setter STAYS (facade split-brain guard).

---

## Tasks

### Task 3.1: Delete `enemy_empire` [Simple]
**File:** `game/ui/screens/strategy_screen.py:184-185`
**Tests:** full suite (no consumers expected)

- [ ] Confirm zero consumers (verified 2026-05-22: none in `game/ui`). Re-grep at exec time.
- [ ] Delete the `enemy_empire` property + its session-guard Category A allowlist
      entry `('...strategy_screen.py', '_session.enemy_empire')`.
- [ ] Verify: suite green; session guard green.

**Notes:**

---

### Task 3.2: Migrate `human_player_ids` consumers, then delete [Medium]
**Files (consumers):** `strategy_click_dispatcher.py`, `strategy_game_state_manager.py`,
`strategy_screen_selection.py`. **Property:** `strategy_screen.py:188`.
**Tests:** consumer tests + session guard

- [ ] FAILING TEST(s): each consumer reads human-player ids via
      `screen.facade.session_meta.human_player_ids()` (or a thin scene accessor).
- [ ] Migrate each consumer off `screen.human_player_ids`.
- [ ] `current_empire` (`strategy_screen.py:205`) reads `self.human_player_ids`
      internally — rewire it to read `self._session.human_player_ids` (composition root)
      in Task 3.4, so deleting the public property is safe.
- [ ] Delete the `human_player_ids` property + its allowlist entry
      `('...strategy_screen.py', '_session.human_player_ids')`.
- [ ] Verify: suite green; session guard green.

**Notes:**

---

### Task 3.3: Migrate `active_empire` external consumers [Medium]
**Files (consumers):** `strategy_screen_assets.py:29-52` (startup focus/asset bootstrap),
any other `screen.active_empire` reader (re-grep). BUG-125 gates already moved to
`active_empire_id` in Phase 2.
**Tests:** asset-bootstrap + startup-focus tests; session guard

- [ ] Re-grep `screen.active_empire` / `scene.active_empire` consumers (exclude the
      screen-internal `active_empire_id`/`current_empire`, handled in 3.4).
- [ ] Migrate asset/startup consumers to `screen.active_empire_id` (id is sufficient)
      or a facade empire query if the live object is genuinely needed.
- [ ] Verify: tests green.

**Notes:**

---

### Task 3.4: Rewire screen-internal helpers to `_session`, then delete `active_empire` [Medium]
**File:** `game/ui/screens/strategy_screen.py` (`active_empire_id` :225-235,
`current_empire` :191-210, `active_empire` :173-181)
**Tests:** screen unit tests; session guard

- [ ] Rewire `active_empire_id` to read `self._session.active_empire` directly
      (composition root owns the only legitimate `_session` handle) instead of the
      public `active_empire` property.
- [ ] Rewire `current_empire` to read `self._session.active_empire` /
      `self._session.empires` / `self._session.human_player_ids` directly.
- [ ] Delete the public `active_empire` property + its allowlist entry
      `('...strategy_screen.py', '_session.active_empire')`. Keep the new
      `_session.active_empire` reads allowlisted as Category A (composition-root
      self-reads) — adjust the allowlist comment.
- [ ] Verify: suite green; session guard green.

**Notes:** The `_session.active_empire` read inside `active_empire_id`/`current_empire`
is still a Category A composition-root pass-through (the screen IS the boundary);
keep it allowlisted-with-reason, do not try to facade-route the screen's own helpers.
The `session` getter + its `_session.__extract__` Category A allowlist entry STAY
(deferred to PROJ-477) — do NOT remove them here.

---

## Phase Completion Checklist
- [ ] `enemy_empire` / `human_player_ids` / `active_empire` properties deleted;
      no consumers reference them (grep clean)
- [ ] `active_empire_id` / `current_empire` read `_session` directly
- [ ] `session` getter + setter UNTOUCHED (its retirement is PROJ-477)
- [ ] Session guard green; the three removed pass-through allowlist entries gone
      (`_session.enemy_empire` / `_session.human_player_ids` / `_session.active_empire`)
- [ ] `python Tools/test_sharded/test_sharded.py` green
- [ ] Update status to `Complete`; update plan.md phase table + Current State

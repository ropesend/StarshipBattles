# Phase 3: Retire the three narrow READ pass-throughs

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-475 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
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

- [x] Confirm zero consumers (verified 2026-05-22: none in `game/ui`). Re-grep at exec time.
- [x] Delete the `enemy_empire` property + its session-guard Category A allowlist
      entry `('...strategy_screen.py', '_session.enemy_empire')`.
- [x] Verify: suite green; session guard green.

**Notes:** Re-grep confirmed zero `game/ui` consumers (only `game_session.py` engine
attr + the property body). Deleted property + allowlist entry. Guards GREEN.

---

### Task 3.2: Migrate `human_player_ids` consumers, then delete [Medium]
**Files (consumers):** `strategy_click_dispatcher.py`, `strategy_game_state_manager.py`,
`strategy_screen_selection.py`. **Property:** `strategy_screen.py:188`.
**Tests:** consumer tests + session guard

- [x] FAILING TEST(s): each consumer reads human-player ids via
      `screen.facade.session_meta.human_player_ids()` (or a thin scene accessor).
- [x] Migrate each consumer off `screen.human_player_ids`.
- [x] `current_empire` (`strategy_screen.py:205`) reads `self.human_player_ids`
      internally — rewire it to read `self._session.human_player_ids` (composition root)
      in Task 3.4, so deleting the public property is safe.
- [x] Delete the `human_player_ids` property + its allowlist entry
      `('...strategy_screen.py', '_session.human_player_ids')`.
- [x] Verify: suite green; session guard green.

**Notes:** Migrated 3 external consumers to `facade.session_meta.human_player_ids()`:
`strategy_click_dispatcher.py:387` (RMB owner gate), `strategy_screen_selection.py:41`,
`strategy_game_state_manager.py` (4 sites: :88/:136/:159/:194). `current_empire`
rewired to `_session` (Task 3.4). Public property deleted; the public-pass-through
allowlist entry removed, but a Category-A `_session.human_player_ids` entry was
RE-ADDED for the `current_empire` composition-root self-read. Test fixtures wired
facade.session_meta.human_player_ids (dispatcher/RMB/selection/game-state).

---

### Task 3.3: Migrate `active_empire` external consumers [Medium]
**Files (consumers):** `strategy_screen_assets.py:29-52` (startup focus/asset bootstrap),
any other `screen.active_empire` reader (re-grep). BUG-125 gates already moved to
`active_empire_id` in Phase 2.
**Tests:** asset-bootstrap + startup-focus tests; session guard

- [x] Re-grep `screen.active_empire` / `scene.active_empire` consumers (exclude the
      screen-internal `active_empire_id`/`current_empire`, handled in 3.4).
- [x] Migrate asset/startup consumers to `screen.active_empire_id` (id is sufficient)
      or a facade empire query if the live object is genuinely needed.
- [x] Verify: tests green.

**Notes:** Only external consumer was `strategy_screen_assets.focus_on_player_home`
(:31-32), which needs the LIVE empire's `.colonies` (identity-matched against
`screen.systems[].planets`). Rewired to resolve the live empire from the raw
`screen.empires` bus keyed by `screen.active_empire_id`. `empires`/`systems` remain
the broad pass-through deferred to PROJ-477 — consistent with the rest of this
asset-bootstrap module. Added a `test_no_active_empire_does_nothing` guard test.

---

### Task 3.4: Rewire screen-internal helpers to `_session`, then delete `active_empire` [Medium]
**File:** `game/ui/screens/strategy_screen.py` (`active_empire_id` :225-235,
`current_empire` :191-210, `active_empire` :173-181)
**Tests:** screen unit tests; session guard

- [x] Rewire `active_empire_id` to read `self._session.active_empire` directly
      (composition root owns the only legitimate `_session` handle) instead of the
      public `active_empire` property.
- [x] Rewire `current_empire` to read `self._session.active_empire` /
      `self._session.empires` / `self._session.human_player_ids` directly.
- [x] Delete the public `active_empire` property. The PUBLIC pass-through allowlist
      entry is unchanged in spelling (`_session.active_empire`) because the same
      attribute-path now backs the Category-A composition-root self-reads in
      `active_empire_id`/`current_empire`; the allowlist COMMENT was updated to say so.
- [x] Verify: suite green; session guard green.

**Notes:** The `_session.active_empire` read inside `active_empire_id`/`current_empire`
is still a Category A composition-root pass-through (the screen IS the boundary);
keep it allowlisted-with-reason, do not try to facade-route the screen's own helpers.
The `session` getter + its `_session.__extract__` Category A allowlist entry STAY
(deferred to PROJ-477) — do NOT remove them here.

---

## Phase Completion Checklist
- [x] `enemy_empire` / `human_player_ids` / `active_empire` properties deleted;
      no consumers reference them (grep clean)
- [x] `active_empire_id` / `current_empire` read `_session` directly
- [x] `session` getter + setter UNTOUCHED (its retirement is PROJ-477)
- [x] Session guard green; `_session.enemy_empire` allowlist entry GONE.
      `_session.human_player_ids` + `_session.active_empire` were RE-PURPOSED from
      public-pass-through entries to Category-A composition-root self-read entries
      (backing `current_empire`/`active_empire_id`), per Task 3.4 / decisions.md.
- [x] `python Tools/test_sharded/test_sharded.py` green (run at project end)
- [x] Update status to `Complete`; update plan.md phase table + Current State

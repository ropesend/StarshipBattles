# Phase 3: Retire the `StrategyScreen.session` GETTER (keep SETTER)

> **BEFORE MARKING COMPLETE:** `python Projects/scripts/validate_phase.py PROJ-477 3`; update plan.md.

**Status:** Complete
**Objective:** Migrate every live `session`-getter reader and the Category B WRITE seams off the
getter, then make the getter raise `AttributeError`. Keep the SETTER (split-brain guard;
`screen.session = mock` for tests).

> **RE-SCAN FIRST:** confirm the live getter-reader set against post-475 code (PROJ-475 migrates
> event_router/lifecycle/transfer_controller/empire_panel_ctrl — those may already be off the getter).

---

## Tasks

### Task 3.1: `system_tree_panel` off dynamic `getattr(scene,'session')` [Medium]
**File:** `game/ui/panels/system_tree_panel.py`
**Tests:** `pytest tests/ -k system_tree`

- [x] Failing test: `_get_empire_context` returns (empire_id, registries) WITHOUT reading `scene.session`.
- [x] Rewire `_get_empire_context` (`:414-426`): read `scene.active_empire_id` (`strategy_screen.py:225-235`) and `scene.registries` (`:213-222`) instead of `getattr(scene,'session')`.
- [x] Remove the `system_tree_panel` `getattr.session` allowlist entry added in Phase 1 Task 1.2.
- [x] Verify: test GREEN; session guard GREEN with the entry removed.

**Notes:**

---

### Task 3.2: Route Category B WRITE seams through the write handle [Medium]
**File:** `strategy_game_state_manager.py`, `strategy_screen_order_editing.py`
**Tests:** `pytest tests/ -k "state_manager or order_editing"`

- [x] Failing test: turn rotation + fleet path-set/pop work without `screen.session.<x>` writes.
- [x] `strategy_game_state_manager.py:164` `screen.session.active_empire = ...` → `screen.order_writes.set_active_empire(...)`.
- [x] `strategy_screen_order_editing.py:66` `set_path` / `:92` `pop_order` → write handle; `:42` `session.active_empire` READ → `screen.active_empire_id`.
- [x] `strategy_screen_selection.py:93` `session.active_empire` READ → `screen.active_empire_id`.
- [x] Remove the corresponding Category B/C session-guard allowlist entries.
- [x] Verify: tests GREEN; session guard GREEN.

**Notes:** `:42`/`:93` are id-compare-only BUG-125 gates — `active_empire_id` is the exact substitute.

---

### Task 3.3: Migrate any remaining live getter readers (post-475 re-scan) [Simple/Medium]
**File:** as found by re-scan (event_router/lifecycle/transfer_controller/empire_panel_ctrl if still present)
**Tests:** targeted per site

- [x] Re-grep `game/ui` for `.session` getter reads still resolving through `StrategyScreen.session`.
- [x] For each survivor, route through the appropriate facade query (`facade.empires.race_config`, `facade.session_meta.*`) or scene accessor — these surfaces are PROJ-475 deliverables.
- [x] Verify: no live reader of the getter remains.

**Notes:** Confirmed no-op. Re-scan found the ONLY live `screen.session.<x>` getter reads were the
3 Category B writes (migrated in 3.2) + the `system_tree_panel` getattr (migrated in 3.1). PROJ-475
already migrated event_router/lifecycle/transfer_controller/empire_panel_ctrl off the getter.
Remaining `.session` matches are comments/docstrings, the kept setter, or engine-internal
`facade_state.session` (already privatized). Several `test_strategy_screen.py` /
`test_viewing_empire_anchor.py` bypass-init tests that wrote `screen.session.X` to configure their
mock session were updated to `screen._session.X` (the composition-root private handle they own).

---

### Task 3.4: Retire the getter; keep the setter [Medium]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/ -k "session_getter or strategy_screen"`

- [x] Failing test: `screen.session` getter raises `AttributeError` (message points to `screen.facade`/`screen.registries`/`screen.active_empire_id`/`screen.order_writes`); `screen.session = mock` STILL works and rebuilds the facade (split-brain guard, `:294-311`).
- [x] Make the getter (`:277-292`) raise `AttributeError`; leave the setter unchanged.
- [x] Remove the `_session.__extract__` Category A allowlist entry (getter body) from the session guard.
- [x] Verify: tests GREEN; session guard GREEN; full suite green (a missed reader surfaces as `AttributeError`).

**Notes:**

---

## Phase Completion Checklist
- [x] All task checkboxes checked
- [x] `screen.session` getter raises; setter works; no live getter reader remains
- [x] Session guard green with the migrated entries removed; sharded suite green
- [x] Update status `Complete`; update plan.md table + Current State → Phase 4

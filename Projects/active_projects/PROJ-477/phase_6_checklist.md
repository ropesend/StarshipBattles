# Phase 6: Delete the pass-throughs + renderer re-exporters; ratchet guard #3 to end-state

> **BEFORE MARKING COMPLETE:** `python Projects/scripts/validate_phase.py PROJ-477 6`; update plan.md.

**Status:** Complete
**Objective:** With all consumers migrated (Phases 3-5), DELETE the three broad pass-throughs and
the renderer re-exporters, and shrink guard #3 to its intentional end-state. This CLOSES the
facade read-path boundary.

> **DELETION ORDER (consult §5):** delete each property LAST, only after the suite is green with it
> present-but-unused. Order: `empires` → `systems` → `galaxy` (widest fan-out last). A removed
> property surfaces any missed caller as an `AttributeError` in tests immediately.

---

## Tasks

### Task 6.1: Delete the renderer re-exporters [Simple]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** `pytest tests/ -k "renderer or strategy_render"`

- [x] Confirm no render module reads `r.galaxy`/`r.systems`/`r.empires` (all on `r.world` after Phase 5).
- [x] Delete the `galaxy`/`systems`/`empires` re-exporter properties (`:124-134`).
- [x] Verify: render/animation tests GREEN.

**Notes:**

---

### Task 6.2: Delete `StrategyScreen.empires` then `.systems` then `.galaxy` [Medium]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Delete `empires` property (`:165-166`); run suite — fix any `AttributeError` survivor (should be none).
- [x] Delete `systems` property (`:168-170`); run suite.
- [x] Delete `galaxy` property (`:160-162`); run suite. Keep the pathfinder helpers (`:547-555`) — repoint them to `self._session.galaxy._pathfinder` (composition root) or `self.world` if exposed.
- [x] Verify: full sharded suite GREEN after each deletion.

**Notes:** `current_empire` (Phase 4 Task 4.6) must already read `_session.empires`, not `self.empires`, or it breaks when `empires` is deleted.

---

### Task 6.3: Ratchet guard #3 to end-state [Simple]
**File:** `tests/static_guards/test_facade_read_path_property_guard.py`
**Tests:** `pytest tests/static_guards/test_facade_read_path_property_guard.py`

- [x] Shrink `_PROPERTY_READ_ALLOWLIST` to ONLY: the `StrategyWorldAccess` internals (if it reads `_session.galaxy` etc.) and the `strategy_screen.py` pathfinder helpers (`:547-555`).
- [x] Confirm zero `scene.galaxy`/`empires`/`systems`/`r.*` reads remain anywhere else under `game/ui/`.
- [x] Verify: guard GREEN with the minimal allowlist; positive controls still pin the matcher.

**Notes:** Most `StrategyWorldAccess` `_session` reads are caught by the SESSION guard, not the property guard — coordinate which allowlist owns them.

---

### Task 6.4: Final validation [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] All THREE read-path guards green (property, session, import).
- [x] No `AttributeError` anywhere; pass-throughs + re-exporters gone; getter raises, setter works.
- [x] Render-perf spot-check: `draw_systems`/`draw_fleets`/`hex_outlines` iteration shape unchanged.
- [x] Run `python Projects/scripts/validate_phase.py PROJ-477 6`.

**Notes:**

---

## Phase Completion Checklist
- [x] All task checkboxes checked
- [x] Pass-throughs + re-exporters deleted; guard #3 at end-state; all guards green; sharded suite green
- [x] Update status `Complete`; update plan.md table + all Verification boxes
- [x] Update plan.md Current State → project complete (await user verification)

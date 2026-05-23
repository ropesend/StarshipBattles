# Phase 7: Codex-consult polish (lightweight)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-430 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_6
**Review Mode:** lightweight
**Files (planned):**
- `docs/systems/strategy_layer.md`
- `game/strategy/facade/grouped_namespaces.py`
- `game/strategy/facade/strategy_session_facade.py`
- `game/ui/screens/build_queue_screen.py`
- `game/ui/screens/build_queue_panel_factory.py`
- `game/ui/screens/empire_build_queue_window.py`
- `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py`
- `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py`
- `tests/integration/ui/test_build_queue_formatting.py`
- `tests/integration/ui/test_build_queue_drag_drop.py`
- `tests/integration/ui/build_queue_screen/conftest.py`
- `tests/integration/ui/build_queue_screen/test_basics.py`
- `tests/integration/ui/build_queue_screen/test_portrait_logging.py`
- `tests/integration/ui/build_queue_screen/test_queue_selector.py`

**Objective:** Action two findings surfaced by a post-Phase-6 Codex consult: (1) align the facade accessor-count phrasing in `docs/systems/strategy_layer.md` with the canonical phrasing elsewhere; (2) move the cross-concern `economy.registries()` accessor onto the `session_meta` group where generic session-level DI belongs.

---

## Tasks

### Task 7.1: Align doc phrasing in `docs/systems/strategy_layer.md` [Simple]
**File:** `docs/systems/strategy_layer.md`
**Tests:** none — docs
**Commit:** `PROJ-430 phase_7 (docs): align strategy_layer.md accessor count phrasing`

- [x] Locate the line that reads "only two callables and ten grouped namespace accessors" (currently `docs/systems/strategy_layer.md:20`).
- [x] Re-word to match the canonical phrasing used in `docs/03_CONVENTIONS.md:420` and the PROJ-309 findings: "two callables (`handle_command`, `process_turn`) plus `facade_state` and 9 grouped namespace accessors".
- [x] Commit as a standalone docs-only commit.

**Notes:** Single sentence rewritten. The "Top-level surface" table in the same section was already correct (already lists `facade_state` separately from the 9 grouped accessors); only the introductory sentence needed alignment. Committed at 811575d90.

### Task 7.2: Move `registries()` off the `economy` group onto `session_meta` [Simple]
**Files:**
- `game/strategy/facade/grouped_namespaces.py`
- `game/strategy/facade/strategy_session_facade.py`
- `docs/systems/strategy_layer.md`
- `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py`
- 3 production caller files + 6 test files
**Tests:** focused facade + build-queue suites + sharded suite
**Commit:** `PROJ-430 phase_7 (group leak): move registries() off economy group`

- [x] Update the public-API contract test `test_strategy_session_facade_public_api.py` GROUP_CONTRACT: move `registries` from the `economy` frozenset to the `session_meta` frozenset. Confirm red against current code.
- [x] In `grouped_namespaces.py`: add `registries()` to `FacadeSessionInfo` (with `session` injected via constructor); remove `registries()` from `FacadeEconomyQueries` (drop the now-unused `session` parameter and `_session` slot). Update class docstrings.
- [x] In `strategy_session_facade.py`: update `FacadeSessionInfo` and `FacadeEconomyQueries` instantiation; update the `economy` property docstring.
- [x] In `docs/systems/strategy_layer.md`: update the Grouped namespaces verb table so `session_meta` lists `registries()` and `economy` drops it.
- [x] Migrate production callers: `rg "\.economy\.registries\("` → 8 production hits across 3 files (`build_queue_screen.py`, `build_queue_panel_factory.py`, `empire_build_queue_window.py`). All rewritten to `.session_meta.registries()`.
- [x] Migrate test mock conftest + 5 mock-session test files: move the `registries()` helper from the inline `_EconomyNS` to the inline `_SessionMetaNS` so production code calls keep resolving on test doubles.
- [x] Run focused tests: `pytest tests/unit/strategy/facade/ tests/unit/ui/screens/test_build_queue_screen_lifecycle.py tests/integration/ui/test_build_queue_formatting.py tests/integration/ui/test_build_queue_drag_drop.py tests/integration/ui/build_queue_screen/` — 459 passed.
- [x] Run sharded suite: `python Tools/test_sharded/test_sharded.py` — 21122/21122 passed.
- [x] Commit.

**Notes:** Top-level facade public-name budget unchanged (still 12: 2 callables + 10 attrs); the move stays inside the grouped layer. `session_meta` now hosts 4 verbs (`turn_number`, `save_path`, `human_player_ids`, `registries`); `economy` drops to 3 (`race_registry`, `colony_demographic_view`, `resolve_config`). The contract test's GROUP_CONTRACT dict pins the new shape; the `LEGACY_FLAT_METHODS` block (which still lists `get_registries` from the pre-TD-08 surface) remains correct — `get_registries` is still gone from the top level. No new `__init__` parameter ordering changes leak out of `grouped_namespaces.py`.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `docs/systems/strategy_layer.md` introductory sentence aligns with `docs/03_CONVENTIONS.md` phrasing
- [x] `economy.registries()` is gone; `session_meta.registries()` is the new path
- [x] Public-API contract test pins the new group memberships
- [x] All production + test callers migrated; `rg "economy\.registries\("` returns zero hits
- [x] Focused tests pass; sharded suite 21122/21122 green
- [x] `python Projects/scripts/validate_phase.py PROJ-430 7` passes (run after committing)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State

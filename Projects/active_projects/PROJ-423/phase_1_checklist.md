# Phase 1: Add `SessionRuntimeServices` and `SessionBootstrapState`

**Status:** Complete
**Depends on:** none
**Review Mode:** standard
**Files (planned):** game/strategy/engine/session/__init__.py, game/strategy/engine/session/runtime_services.py, game/strategy/engine/game_session.py, tests/unit/strategy/engine/session/test_runtime_services.py
**Objective:** Introduce the internal value objects (`SessionRuntimeServices` and `SessionBootstrapState`) first, with no caller-visible change. `GameSession.__init__` still uses the old construction path but assembles `self._services` and exposes a `services` property.

> Phase 0 (preflight grep + behavioral inventory) is a lightweight prerequisite. If Phase 0 has not yet been performed, do it as the first action of this phase.

---

## Tasks

### Task 1.1: Create the `session/` package [Simple]
**File:** `game/strategy/engine/session/__init__.py`

- [x] Add an empty package init (or one that re-exports the public names of the new dataclasses once Task 1.2 lands).

### Task 1.2: Define `SessionRuntimeServices` and `SessionBootstrapState` [Medium]
**File:** `game/strategy/engine/session/runtime_services.py`
**Tests:** `pytest tests/unit/strategy/engine/session/test_runtime_services.py -x`

- [x] Define `SessionRuntimeServices` as `@dataclass(frozen=True)` with fields: `registries`, `event_log`, `event_bus`, `fleet_mutator`, `planet_mutator`, `empire_mutator`, `ship_mutator`, `turn_engine`, `command_registry`.
- [x] Define `SessionBootstrapState` as `@dataclass(frozen=True)` with fields: `config`, `services`, `galaxy`, `empires`, `turn_number`, `save_path`, `human_player_ids`.
- [x] Confirm `race_registry` is **not** on `SessionRuntimeServices` (it stays lazy on `GameSession`).
- [x] **Cross-plan check:** if PROJ-427 (TD-05) has already merged to `main`, add `design_repository` to `SessionRuntimeServices` and per-empire `design_catalog`s to `SessionBootstrapState` per the cross-plan note in `design.md`. Otherwise skip this sub-task.

### Task 1.3: Author the red tests first [Medium]
**File:** `tests/unit/strategy/engine/session/test_runtime_services.py`

- [x] `test_runtime_services_is_frozen_dataclass` — attempting to reassign a field on a constructed instance must raise.
- [x] `test_runtime_services_exposes_current_service_members` — every public service currently on `GameSession` is present on `SessionRuntimeServices` (use `dataclasses.fields(...)`).
- [x] `test_bootstrap_state_captures_session_owned_state` — the dataclass fields match the seven owned-state attributes.
- [x] `test_game_session_services_property_returns_runtime_services` — after Task 1.4, `GameSession(...).services` returns a `SessionRuntimeServices`.
- [x] Run the file; confirm all four tests fail in the expected ways.

### Task 1.4: Wire `GameSession.services` without changing construction [Medium]
**File:** `game/strategy/engine/game_session.py`

- [x] At the end of `__init__` (after all five mutators, turn engine, and command registry are constructed), assemble `self._services = SessionRuntimeServices(...)` from the already-constructed objects.
- [x] At the end of `from_dict` (after the hand-mirrored construction block), do the same so loaded sessions also have `self._services` set.
- [x] Add a `services` property returning `self._services`.
- [x] Do **not** change any existing private attributes or service properties in this phase — they continue to be set directly as today.

### Task 1.5: Verify regression coverage [Simple]
**Tests:**

- [x] `pytest tests/unit/strategy/engine/session/test_runtime_services.py -x` — all green.
- [x] `pytest tests/unit/strategy/test_game_session.py tests/unit/strategy/test_game_session_events.py tests/unit/strategy/test_game_session_save_load_registries.py -x` — no regressions.

---

## Exit criteria

- [x] `SessionRuntimeServices` and `SessionBootstrapState` exist and are covered by tests.
- [x] `GameSession` exposes `services` without behavior drift.
- [x] All Phase 1 tests pass; cited regression tests remain green.

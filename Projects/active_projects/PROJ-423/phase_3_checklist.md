# Phase 3: Extract `SessionPersistenceAdapter`

**Status:** Not Started
**Depends on:** phase_2
**Review Mode:** standard
**Files (planned):** game/strategy/engine/session/persistence_adapter.py, game/strategy/engine/game_session.py, game/strategy/systems/save_game_service.py, tests/unit/strategy/engine/session/test_persistence_adapter.py
**Objective:** Move save/load serialization and rehydration logic out of `GameSession.from_dict`. After this phase, `to_dict()` and `from_dict()` are thin delegates and the load-only steps (galaxy back-refs, fleet registration, order reference resolution, pursuer-tracker rebuild) live in the adapter.

---

## Tasks

### Task 3.1: Author the red tests first [Complex]
**File:** `tests/unit/strategy/engine/session/test_persistence_adapter.py`

- [ ] `test_serialize_preserves_existing_save_schema` — pin the dict shape `{turn_number, save_path, config, galaxy, empires, human_player_ids, event_log}` exactly. Compare key-set equality plus type of each value against the current `to_dict()` output.
- [ ] `test_rehydrate_wires_galaxy_back_refs` — galaxy back-references (`game_session.py` lines 566-567) are reapplied on rehydrate.
- [ ] `test_rehydrate_registers_loaded_fleets` — fleet registration loop (lines 570-573, PROJ-219) executes.
- [ ] `test_rehydrate_resolves_order_references` — `resolve_order_references` (lines 579-581, PROJ-207) executes.
- [ ] `test_rehydrate_rebuilds_pursuer_trackers` — pursuer-tracker rebuild (lines 586-592, PROJ-222) executes.
- [ ] Run the file; confirm all five tests fail in the expected ways.

### Task 3.2: Implement `SessionPersistenceAdapter.serialize(session)` [Medium]
**File:** `game/strategy/engine/session/persistence_adapter.py`

- [ ] Implement `serialize(session) -> dict` that returns the same dict shape `GameSession.to_dict()` currently produces, byte-for-byte.
- [ ] No new fields, no renames, no reorderings — the test in Task 3.1 pins this.

### Task 3.3: Implement `SessionPersistenceAdapter.rehydrate_state(...)` [Complex]
**File:** `game/strategy/engine/session/persistence_adapter.py`

- [ ] Implement `rehydrate_state(data, *, ai_factory=None) -> SessionBootstrapState`.
- [ ] Inside, call `_resolve_registries`, build services via `SessionBootstrap._build_services(event_log=EventLog.from_dict(data.get('event_log', {'events': []})), ...)`.
- [ ] Perform the two-phase galaxy/empire deserialisation (current `from_dict` lines 538-560).
- [ ] Wire galaxy back-references (lines 566-567).
- [ ] Run the fleet registration loop (lines 570-573).
- [ ] Call `resolve_order_references` (lines 579-581).
- [ ] Rebuild pursuer trackers (lines 586-592).
- [ ] Compute `human_player_ids` from `data` — **preserve the current `[0, 1]` fallback exactly**.
- [ ] Return a `SessionBootstrapState` carrying all of the above.
- [ ] Returns `SessionBootstrapState`, **not** `GameSession`.

### Task 3.4: Make `to_dict` / `from_dict` thin delegates [Medium]
**File:** `game/strategy/engine/game_session.py`

- [ ] `GameSession.to_dict()` returns `SessionPersistenceAdapter.serialize(self)`.
- [ ] `GameSession.from_dict(data, ai_factory=None)`:
  1. `state = SessionPersistenceAdapter.rehydrate_state(data, ai_factory=ai_factory)`
  2. Construct a new `GameSession` and apply the state (provisional assignment — Phase 4 introduces the canonical `_apply_bootstrap_state(...)` method).
- [ ] Remove the now-dead hand-mirrored service-construction block from `from_dict`. After this task, `from_dict` is small.

### Task 3.5: Save-game service surface [Simple]
**File:** `game/strategy/systems/save_game_service.py`

- [ ] If `from_dict` delegation changes require a docstring or tiny call-site adjustment, make it. Do **not** change the API shape.

### Task 3.6: Validate [Medium]
**Tests:**

- [ ] `pytest tests/unit/strategy/engine/session/test_persistence_adapter.py -x` — all green.
- [ ] `pytest tests/integration/save_load/ -x` — no regressions.
- [ ] `pytest tests/integration/strategy/test_event_log_integration.py tests/integration/strategy/test_fleet_registration_wiring.py tests/integration/strategy/test_fleet_registration_lifecycle.py -x` — no regressions.
- [ ] `python Tools/test_sharded/test_sharded.py` — full sharded run after this phase per the source plan's final gates.

---

## Exit criteria

- [ ] `GameSession.from_dict()` no longer reconstructs services inline.
- [ ] Save/load integration coverage stays green.
- [ ] Sharded test run after this phase passes.

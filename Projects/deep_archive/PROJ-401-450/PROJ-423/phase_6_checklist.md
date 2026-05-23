# Phase 6: Codex consult follow-ups (underscore-alias migration + frozen schema fixture)

**Status:** Complete
**Depends on:** phase_5
**Review Mode:** standard
**Files (planned):**
- `game/strategy/engine/session/persistence_adapter.py`
- `game/strategy/engine/turn_state_snapshot.py`
- `tests/unit/strategy/engine/session/test_persistence_adapter.py`

**Objective:** Address the two actionable Codex-consult findings against shipped PROJ-423: (1) migrate the two remaining production underscore-alias readers to the public `services` accessor, and (2) replace the self-delegating `test_serialize_matches_to_dict_output` companion with a frozen reference-dict assertion that pins the save schema's exact shape. The third Codex finding (TurnStateSnapshot rehydrate-path asymmetry) is tracked separately as PROJ-432 per Codex's explicit recommendation.

---

## Tasks

### Task 6.1: Migrate `persistence_adapter.py` to the public services accessor [Simple]
**File:** `game/strategy/engine/session/persistence_adapter.py`

- [x] Replace the `session._event_log.to_dict()` read at the `serialize()` body with `session.services.event_log.to_dict()`. Mechanical, no behavior change.

### Task 6.2: Migrate `turn_state_snapshot.py` to the public services accessor [Simple]
**File:** `game/strategy/engine/turn_state_snapshot.py`

- [x] Replace the `session._registries` read inside `TurnStateSnapshot.restore()` with `session.services.registries`. Update the docstring's Args section accordingly.

### Task 6.3: Pin the frozen save-schema fixture [Standard]
**File:** `tests/unit/strategy/engine/session/test_persistence_adapter.py`

- [x] Add a `_frozen_fixture_session()` helper that builds a deterministic minimal `GameSession` (empty `Galaxy(radius=100)`, no empires, `asset_base_path=""`, `galaxy_seed=42`).
- [x] Add `TestSerialize.test_serialize_matches_frozen_schema_fixture` asserting `SessionPersistenceAdapter.serialize(session)` equals a hardcoded reference-dict literal capturing every top-level and nested key.
- [x] Retain the existing `test_serialize_matches_to_dict_output` as documentation that the `to_dict()` delegate stays a one-to-one wrapper.

### Task 6.4: Validate [Simple]
**Tests:**

- [x] `pytest tests/unit/strategy/engine/session/test_persistence_adapter.py -x` — 10 passed, including the new frozen-fixture test.
- [x] `pytest tests/unit/strategy/turn_engine/test_turn_state_snapshot.py -x` — 10 passed.
- [x] `pytest tests/integration/ -k "save_load or save or load" -x` — 319 passed (no save/load integration regressions from the migration).

---

## Exit criteria

- [x] No production reader inside `game/strategy/engine/session/persistence_adapter.py` or `game/strategy/engine/turn_state_snapshot.py` accesses `session._event_log` or `session._registries` directly; both go through `session.services.<accessor>`.
- [x] `test_serialize_matches_frozen_schema_fixture` exists and asserts the serialize output equals a hardcoded reference dict literal.
- [x] Underscore-aliased properties remain on `GameSession` itself (tests still depend on them; broader cleanup deliberately deferred).
- [x] Focused tests pass.

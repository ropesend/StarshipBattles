# Phase 5: Docs update

**Status:** Not Started
**Depends on:** phase_4
**Review Mode:** lightweight
**Files (planned):** docs/01_ARCHITECTURE.md, docs/02_PATTERNS.md, docs/systems/strategy_layer.md, docs/systems/save_load.md
**Objective:** Document `SessionRuntimeServices`, `SessionBootstrap`, and `SessionPersistenceAdapter` as internal collaborators. Explicitly state that the public API and save schema are unchanged.

---

## Tasks

### Task 5.1: Update `docs/01_ARCHITECTURE.md` [Simple]
**File:** `docs/01_ARCHITECTURE.md`

- [ ] Add (or update) a section describing the session lifecycle split: `SessionRuntimeServices` (frozen dataclass), `SessionBootstrap` (canonical construction), `SessionPersistenceAdapter` (serialize + rehydrate).
- [ ] Explicitly state the public API remains `GameSession(...)` / `GameSession.from_dict(...)` / `GameSession.to_dict()`.

### Task 5.2: Update `docs/02_PATTERNS.md` [Simple]
**File:** `docs/02_PATTERNS.md`

- [ ] Capture the bootstrap-state pattern: a single internal frozen-dataclass payload backs both the construction and rehydration paths; one private `_apply_bootstrap_state(...)` method is the only assignment path.
- [ ] Reference `SessionBootstrapState` as the canonical example.

### Task 5.3: Update `docs/systems/strategy_layer.md` [Simple]
**File:** `docs/systems/strategy_layer.md`

- [ ] Update the session lifecycle section: `GameSession` is now a thin shell; service ownership lives in `SessionRuntimeServices`; construction lives in `SessionBootstrap`.

### Task 5.4: Update `docs/systems/save_load.md` [Simple]
**File:** `docs/systems/save_load.md`

- [ ] Document that the save schema is unchanged (`{turn_number, save_path, config, galaxy, empires, human_player_ids, event_log}`).
- [ ] Note that `to_dict()` / `from_dict()` delegate to `SessionPersistenceAdapter`.
- [ ] Note that the current `human_player_ids` `[0, 1]` fallback is preserved for backwards compatibility.

### Task 5.5: Validate [Simple]
**Tests:**

- [ ] `pytest tests/unit/strategy/engine/test_game_session_shape.py -x` — should still pass; this is a doc-only phase.
- [ ] `python Tools/test_sharded/test_sharded.py` — final clean run.

---

## Exit criteria

- [ ] Docs match the new lifecycle split.
- [ ] No code changes in this phase.

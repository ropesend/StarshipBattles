# Phase 2: GameSession Integration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-77 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Wire event collection into GameSession with persistence

---

## Tasks

### Task 2.1: Add EventLog to GameSession [Medium]
**File:** `game/strategy/engine/game_session.py`

**Tests:** `pytest tests/unit/strategy/test_game_session_events.py -v`

- [x] Add import: `from game.strategy.events import Event, EventLog`
- [x] Add import: `from game.core.logger import set_event_handler`
- [x] Add `self._event_log = EventLog()` in `__init__`
- [x] Create `_create_event_handler()` method (with enum value coercion)
- [x] Call `set_event_handler(self._create_event_handler())` in `__init__`
- [x] Add property `event_log` to expose `self._event_log`
- [x] Verify: GameSession creates EventLog on initialization

**Notes:** Handler also coerces enum values to strings via `.value` for consistent storage.

---

### Task 2.2: Add Event Persistence [Medium]
**File:** `game/strategy/engine/game_session.py`

**Tests:** `pytest tests/unit/strategy/test_game_session_events.py::TestGameSessionEventPersistence -v`

- [x] In `to_dict()` method, add `'event_log': self._event_log.to_dict()`
- [x] In `from_dict()` classmethod, restore event log + register handler
- [x] Verify: save game, load game, events are preserved

**Notes:** from_dict also registers event handler so new events can be logged after load.

---

### Task 2.3: Add Facade Query Methods [Simple]
**File:** `game/strategy/facade/strategy_session_facade.py`

**Tests:** `pytest tests/unit/strategy/facade/test_event_queries.py -v`

- [x] Add method `get_turn_events(turn: int = None) -> List[dict]`
- [x] Add method `get_all_events() -> List[dict]`
- [x] Add method `get_events_by_category(category: str) -> List[dict]`
- [x] Verify: facade methods return list of dicts (immutable for UI)

**Notes:** All methods return plain dicts, never domain Event objects.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/strategy/ -v` passes
- [x] `pytest tests/integration/save_load/ -v` passes
- [x] Events persist through save/load cycle
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3

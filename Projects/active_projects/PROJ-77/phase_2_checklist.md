# Phase 2: GameSession Integration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-77 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Wire event collection into GameSession with persistence

---

## Tasks

### Task 2.1: Add EventLog to GameSession [Medium]
**File:** `game/strategy/engine/game_session.py`

**Tests:** `pytest tests/unit/strategy/test_game_session.py -v`

- [ ] Add import: `from game.strategy.events import Event, EventLog`
- [ ] Add import: `from game.core.logger import set_event_handler, log_event`
- [ ] Add `self._event_log = EventLog()` in `__init__` (~line 96)
- [ ] Create `_create_event_handler()` method:
  ```python
  def _create_event_handler(self):
      def handler(event_type: str, **kwargs):
          category = kwargs.pop('category', 'other')
          message = kwargs.pop('message', '')
          empire_id = kwargs.pop('empire_id', -1)
          event = Event(
              event_type=event_type,
              category=category,
              turn=self.turn_number,
              empire_id=empire_id,
              message=message,
              details=kwargs
          )
          self._event_log.append(event)
      return handler
  ```
- [ ] Call `set_event_handler(self._create_event_handler())` in `__init__`
- [ ] Add property `event_log` to expose `self._event_log`
- [ ] Verify: GameSession creates EventLog on initialization

**Notes:**

---

### Task 2.2: Add Event Persistence [Medium]
**File:** `game/strategy/engine/game_session.py`

**Tests:** `pytest tests/integration/save_load/ -v`

- [ ] In `to_dict()` method, add:
  ```python
  'event_log': self._event_log.to_dict()
  ```
- [ ] In `from_dict()` classmethod, after session creation:
  ```python
  session._event_log = EventLog.from_dict(data.get('event_log', {'events': []}))
  ```
- [ ] Verify: save game, load game, events are preserved

**Notes:**

---

### Task 2.3: Add Facade Query Methods [Simple]
**File:** `game/strategy/facade/strategy_session_facade.py`

**Tests:** `pytest tests/unit/strategy/facade/ -v`

- [ ] Add method `get_turn_events(turn: int = None) -> List[Dict]`:
  ```python
  def get_turn_events(self, turn: int = None) -> List[Dict]:
      """Get events for a specific turn (or current turn if None)."""
      if turn is None:
          turn = self._session.turn_number
      events = self._session.event_log.get_events_for_turn(turn)
      return [e.to_dict() for e in events]
  ```
- [ ] Add method `get_all_events() -> List[Dict]`:
  ```python
  def get_all_events(self) -> List[Dict]:
      """Get all events from the event log."""
      return [e.to_dict() for e in self._session.event_log.get_all_events()]
  ```
- [ ] Add method `get_events_by_category(category: str) -> List[Dict]`:
  ```python
  def get_events_by_category(self, category: str) -> List[Dict]:
      """Get events filtered by category."""
      events = self._session.event_log.get_events_by_category(category)
      return [e.to_dict() for e in events]
  ```
- [ ] Verify: facade methods return list of dicts (immutable for UI)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/ -v` passes
- [ ] `pytest tests/integration/save_load/ -v` passes
- [ ] Events persist through save/load cycle
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3

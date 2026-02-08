# Phase 1: Event Infrastructure

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-77 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create the core event data model and collection system

---

## Tasks

### Task 1.1: Create Event Types Enum [Simple]
**Files:**
- `game/strategy/events/__init__.py` (NEW)
- `game/strategy/events/event_types.py` (NEW)

**Tests:** `pytest tests/unit/strategy/events/test_event_types.py`

- [ ] Create `game/strategy/events/` directory
- [ ] Create `__init__.py` with exports:
  ```python
  from .event_types import EventType, EventCategory
  from .event_log import Event, EventLog
  ```
- [ ] Create `event_types.py` with EventType enum:
  - `SHIP_BUILT = "ship_built"`
  - `COMPLEX_BUILT = "complex_built"`
  - `COLONY_FOUNDED = "colony_founded"`
  - `COMBAT_RESOLVED = "combat_resolved"`
- [ ] Create EventCategory enum:
  - `PRODUCTION = "production"`
  - `COLONIES = "colonies"`
  - `COMBAT = "combat"`
  - `ALL = "all"`

**Notes:**

---

### Task 1.2: Create Event Dataclass [Medium]
**File:** `game/strategy/events/event_log.py` (NEW)

**Tests:** `pytest tests/unit/strategy/events/test_event_log.py`

- [ ] Create `@dataclass Event` with fields:
  - `event_type: str`
  - `category: str`
  - `turn: int`
  - `empire_id: int`
  - `message: str`
  - `details: Dict[str, Any]` (default_factory=dict)
- [ ] Add `to_dict()` method returning all fields as dict
- [ ] Add `@classmethod from_dict(cls, data)` to reconstruct Event
- [ ] Verify: serialization roundtrip preserves all fields

**Notes:**

---

### Task 1.3: Create EventLog Class [Medium]
**File:** `game/strategy/events/event_log.py`

**Tests:** `pytest tests/unit/strategy/events/test_event_log.py`

- [ ] Create `EventLog` class with `_events: List[Event]`
- [ ] Add `append(event: Event)` method
- [ ] Add `get_events_for_turn(turn: int) -> List[Event]`
- [ ] Add `get_events_by_category(category: str) -> List[Event]`
  - If category == "all", return all events
- [ ] Add `get_all_events() -> List[Event]`
- [ ] Add `to_dict()` returning `{'events': [e.to_dict() for e in self._events]}`
- [ ] Add `@classmethod from_dict(cls, data)` to restore EventLog
- [ ] Verify: serialization roundtrip preserves all events

**Notes:**

---

### Task 1.4: Create Event Tests [Simple]
**Files:**
- `tests/unit/strategy/events/__init__.py` (NEW)
- `tests/unit/strategy/events/test_event_types.py` (NEW)
- `tests/unit/strategy/events/test_event_log.py` (NEW)

**Tests:** `pytest tests/unit/strategy/events/ -v`

- [ ] Create test directory with `__init__.py`
- [ ] Test EventType enum values exist and are strings
- [ ] Test EventCategory enum values exist
- [ ] Test Event creation with all fields
- [ ] Test Event.to_dict() produces correct structure
- [ ] Test Event.from_dict() reconstructs correctly
- [ ] Test Event serialization roundtrip equality
- [ ] Test EventLog.append() adds events
- [ ] Test EventLog.get_events_for_turn() filters correctly
- [ ] Test EventLog.get_events_by_category() filters correctly
- [ ] Test EventLog.get_events_by_category("all") returns all
- [ ] Test EventLog.to_dict() serializes all events
- [ ] Test EventLog.from_dict() restores all events
- [ ] Verify: `pytest tests/unit/strategy/events/ -v` all pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/events/ -v` passes
- [ ] Event and EventLog can be imported from `game.strategy.events`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2

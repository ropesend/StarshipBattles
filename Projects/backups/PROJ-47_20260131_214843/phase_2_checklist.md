# Phase 2: Core Infrastructure Documentation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-47 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add type hints and documentation to core infrastructure modules

---

## Tasks

### Task 2.1: Logger Type Hints (CORE-001) [Simple]
**File:** `game/core/logger.py`
**Tests:** `python -m py_compile game/core/logger.py`

- [x] Add `-> None` to `log(self, msg: str)` (line 48)
- [x] Add `-> None` to `info(self, msg: str)` (line 52)
- [x] Add `-> None` to `warning(self, msg: str)` (line 56)
- [x] Add `-> None` to `error(self, msg: str)` (line 60)
- [x] Add `-> None` to `set_enabled(self, enabled: bool)` (line 64)
- [x] Add `-> None` to `log_debug(msg: str)` (line 70)
- [x] Add `-> None` to `log_info(msg: str)` (line 73)
- [x] Add `-> None` to `log_warning(msg: str)` (line 76)
- [x] Add `-> None` to `log_error(msg: str)` (line 79)
- [x] Add `-> None` to `set_logging(enabled: bool)` (line 82)
- [x] Add `-> None` to `set_event_handler(handler: Optional[Callable])` (line 88)
- [x] Add `-> None` to `log_event(event_type: str, **kwargs)` (line 93)
- [x] Verify: Run py_compile, check type hints in IDE

**Notes:** Added typing imports, all type hints applied.

---

### Task 2.2: Registry Type Hints & PROJ-38 Docs (CORE-002, CORE-011) [Simple]
**File:** `game/core/registry.py`
**Tests:** `python -m py_compile game/core/registry.py`

- [x] Add type hint to `get_validator(self) -> Any` (line 276)
- [x] Add type hint to `set_validator(self, validator: Any) -> None` (line 280)
- [x] Add type hint to `_check_frozen(self) -> None` (line 293)
- [x] Expand module docstring (around line 31) with PROJ-38 migration timeline:
  ```
  PROJ-38: Deprecation Timeline
  - v0.9.0: Deprecation warnings added
  - v1.0.0 (Target): Remove deprecated utility functions
  - Migration: Replace get_component_registry() with GameRegistries via DI
  ```
- [x] Verify: Run py_compile

**Notes:** Type hints and deprecation timeline added.

---

### Task 2.3: Paths Backward Compatibility Docs (CORE-005) [Simple]
**File:** `game/core/paths.py`
**Tests:** `python -m py_compile game/core/paths.py`

- [x] Add comment block before backward compatibility exports (around line 102):
  ```python
  # Backward compatibility exports - Deprecated in favor of Paths class access
  # New code should use: from game.core.paths import Paths; Paths.ROOT_DIR
  ```
- [x] Verify: Run py_compile

**Notes:** Deprecation comment added.

---

### Task 2.4: InputHandler Documentation (DOC-03) [Simple]
**File:** `game/core/input_handler.py`
**Tests:** `python -m py_compile game/core/input_handler.py`

- [x] Add inline comments for speed constants (lines 8-11)
- [x] Add docstring to `handle_keydown()` (line 21) - document state-based dispatch
- [x] Add docstring to `_handle_battle_keydown()` (line 27) - document all keybindings:
  - O = overlay toggle
  - SPACE = pause/unpause
  - COMMA = slow down
  - PERIOD = speed up
  - M = normal speed
  - SLASH = UI pause speed
- [x] Verify: Run py_compile

**Notes:** Module docstring, constant comments, method docstrings with keybindings all added.

---

### Task 2.5: Camera Zoom Documentation (DOC-05) [Simple]
**File:** `game/ui/renderer/camera.py`
**Tests:** `python -m py_compile game/ui/renderer/camera.py`

- [x] Add docstring to `update()` (line 24) - explain zoom anchor logic for smooth interpolation
- [x] Add docstring to `update_input()` (line 47) - document mouse wheel zoom, middle-click pan, keyboard movement
- [x] Verify: Run py_compile

**Notes:** Detailed docstrings with zoom anchor explanation and control reference.

---

### Task 2.6: Protocol Property Documentation (DC-011) [Simple]
**File:** `game/core/protocols.py`
**Tests:** `python -m py_compile game/core/protocols.py`

- [x] Add docstring to `ILocatable.location` property - "Entity's position (HexCoord for strategy, Vector2 for simulation)"
- [x] Add docstring to `INamed.name` property - "Human-readable display name, always non-empty"
- [x] Add docstring to `IOwnable.owner_id` property - "Player ID of owner, None for unowned/neutral"
- [x] Add docstring to `ICombatant.is_alive` property - "True if entity can participate in combat"
- [x] Add docstring to `IDamageable.is_derelict` property - "True if destroyed but still present (hulk)"
- [x] Verify: Run py_compile

**Notes:** All protocol property docstrings added.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ --testmon` - affected tests pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3

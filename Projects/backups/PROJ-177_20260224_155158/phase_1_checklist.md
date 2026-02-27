# Phase 1: Remove Redundant Generic Exceptions from Tuple Catches

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-177 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove provably-redundant generic exception types from 9 except blocks where
the try-block code only calls domain methods that raise domain exceptions.

---

## Tasks

### Task 1.1: Clean ship_io.py save path [Simple]
**File:** `game/ui/services/ship_io.py`
**Tests:** `pytest tests/unit/ui/services/ -k ship_io`

- [x] Line 98: Change `except (TypeError, ValueError, ValidationException) as e:` to `except ValidationException as e:`
- [x] Verify: `ship.to_dict()` only raises `ValidationException`; `save_json()` catches internally

**Notes:**

### Task 1.2: Clean battle_controller.py reinforcement path [Simple]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/ -k battle_controller`

- [x] Line 390: Change `except (TypeError, ValueError, AttributeError, ValidationException) as e:` to `except ValidationException as e:`
- [x] Verify: only property assignments and `engine.add_ship_mid_battle()` in try block

**Notes:**

### Task 1.3: Clean save_game_service.py save path [Simple]
**File:** `game/strategy/systems/save_game_service.py`
**Tests:** `pytest tests/unit/strategy/systems/ -k save_game`

- [x] Line 108: Change `except (TypeError, ValueError, ValidationException) as e:` to `except ValidationException as e:`
- [x] Line 111: Remove entire `except (KeyError, AttributeError, ImportError) as e:` block (dead code)
- [x] Verify: `save_json()` returns bool, does not propagate exceptions

**Notes:**

### Task 1.4: Clean race_library.py save path [Simple]
**File:** `game/strategy/systems/race_library.py`
**Tests:** `pytest tests/unit/strategy/systems/ -k race_library`

- [x] Line 197: Change `except (TypeError, ValueError, ValidationException) as e:` to `except ValidationException as e:`
- [x] Verify: `config.to_dict()` domain call + `save_json()` catches internally

**Notes:**

### Task 1.5: Clean design_library.py load and save paths [Simple]
**File:** `game/strategy/systems/design_library.py`
**Tests:** `pytest tests/unit/strategy/systems/ -k design_library`

- [x] Line 102: Change `except (AttributeError, TypeError, ValueError, ValidationException) as e:` to `except ValidationException as e:`
- [x] Line 185: Change `except (TypeError, ValueError, ValidationException) as e:` to `except ValidationException as e:`
- [x] Verify: JSON errors caught separately above; domain calls only raise `ValidationException`

**Notes:**

### Task 1.6: Clean formation_editor.py save and load [Simple]
**File:** `game/ui/screens/formation_editor.py`
**Tests:** `pytest tests/unit/ui/ -k formation`

- [x] Line 209: Change `except (TypeError, ValueError, ValidationException) as e:` to `except ValidationException as e:`
- [x] Line 236: Change `except (KeyError, ValueError, ValidationException) as e:` to `except ValidationException as e:`
- [x] Verify: `save_json()` catches internally; `load_json()` returns None on error

**Notes:**

### Task 1.7: Clean battle_service.py creation path [Simple]
**File:** `game/simulation/services/battle_service.py`
**Tests:** `pytest tests/unit/simulation/services/ -k battle_service`

- [x] Line 91: Change `except (TypeError, ValueError, AttributeError, ValidationException, StateException) as e:` to `except (ValidationException, StateException) as e:`
- [x] Verify: `BattleEngine()` constructor only raises domain exceptions

**Notes:**

### Task 1.8: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] All 12338 tests pass
- [x] No new warnings related to exception handling

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

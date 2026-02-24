# Phase 5: Caller Catch Updates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-170 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update 36 except blocks in game/ that catch generic exceptions from game code. Most complex phase — broad tuple catches in persistence tier.
**Estimated Effort:** 3 hours

**Strategy:** After Phases 2-4, all `raise` statements have been migrated. Now update catches.
- For tuples like `except (TypeError, ValueError, KeyError)`: replace with domain exceptions
- The generic types may still be needed for stdlib exceptions caught in the same block — audit each
- If a block catches BOTH stdlib and game exceptions: use `except (ValidationException, ComponentException, ValueError, KeyError)` keeping only the stdlib types needed

---

## Tasks

### Task 5.1: Persistence Tier Catches [Medium]
**Files:** `save_game_service.py`, `design_library.py`, `race_library.py`, `ship_io.py`
**Tests:** `pytest tests/unit/strategy/systems/ tests/unit/ui/services/ -k "save or design_lib or race_lib or ship_io"`

**save_game_service.py** (4 blocks):
- [ ] Lines ~106,202: `except (TypeError, ValueError)` from GameSession.from_dict() — After migration, game code raises ValidationException. But JSON parsing may still raise ValueError. → `except (ValidationException, PersistenceException, ValueError)` (keep ValueError for JSON)
- [ ] Line ~221: Very broad catch (11 types) — Narrow to `except (ValidationException, PersistenceException, OSError, PermissionError)` + log others
- [ ] Line ~409: Audit and update similarly

**design_library.py** (4 blocks):
- [ ] Lines ~182,222,261,302: `except (TypeError, ValueError)` and broader — Replace TypeError/ValueError with `ValidationException, ComponentException` where game code is the source, keep generic for stdlib JSON
- [ ] Each block: identify which raises come from game code vs stdlib

**race_library.py** (2 blocks):
- [ ] Lines ~194,227: Update catch tuples for game exceptions

**ship_io.py** (2 blocks):
- [ ] Lines ~95,158: `except (TypeError, ValueError)` from Ship serialization → `except (ValidationException, ComponentException, ValueError)` (keep ValueError for JSON)

- [ ] Verify: `pytest tests/unit/strategy/systems/ tests/unit/ui/services/ -n 4`

**Notes:** This is the highest-risk task. Test thoroughly after each file change.

### Task 5.2: Component Loading Chain Catches [Medium]
**Files:** `component.py`, `design_loader.py`, `vehicle_design_service.py`, `battle_service.py`, `battle_controller.py`
**Tests:** `pytest tests/unit/simulation/ -n 4`

**component.py** (2 blocks):
- [ ] Line ~525: `except (KeyError, TypeError, ValueError)` from Component/Modifier constructor → `except (ValidationException, ComponentException, KeyError)` (keep KeyError for dict access)
- [ ] Line ~629: Similar update

**design_loader.py** (2 blocks):
- [ ] Lines ~75,122: `except (KeyError, TypeError, ValueError)` from Ship init → `except (ValidationException, ComponentException, KeyError)`

**vehicle_design_service.py** (1 block):
- [ ] Line ~121: `except (TypeError, ValueError, KeyError, AttributeError)` → `except (ValidationException, ComponentException, KeyError, AttributeError)` (keep AttributeError for edge cases)

**battle_service.py** (1 block):
- [ ] Line ~88: `except (TypeError, ValueError, AttributeError)` → `except (ValidationException, ComponentException, AttributeError)`

**battle_controller.py** (3 blocks):
- [ ] Lines ~172,389,516: `except (TypeError, ValueError, KeyError, AttributeError)` → `except (ValidationException, ComponentException, StateException, KeyError, AttributeError)`

- [ ] Verify: `pytest tests/unit/simulation/ -n 4`

**Notes:** Component loading chain is heavily tested. Run full simulation tests after.

### Task 5.3: Other Game Code Catches [Simple]
**Files:** `formation_editor.py`, `new_game_setup_screen.py`, `abilities/__init__.py`
**Tests:** `pytest tests/unit/ui/ tests/unit/simulation/components/abilities/`

**formation_editor.py** (2 blocks):
- [ ] Line ~202: `except (TypeError, ValueError)` → `except (ValidationException, TypeError, ValueError)` (or just `except (ValidationException, TypeError)` if no stdlib ValueError here)
- [ ] Line ~227: Already updated in Phase 4 Task 4.6

**new_game_setup_screen.py** (1 block):
- [ ] Line ~508: `except ValueError` from GalaxyGenerationService → `except (ValidationException, ValueError)` (keep ValueError for fallback)

**abilities/__init__.py** (1 block):
- [ ] Line ~118: `except (TypeError, ValueError, KeyError, AttributeError)` → `except (ValidationException, ComponentException, KeyError, AttributeError)` (ABILITY_REGISTRY instantiation)

- [ ] Verify: `pytest tests/unit/ui/ tests/unit/simulation/components/abilities/`

**Notes:**

### Task 5.4: Mixed-Source Review [Medium]
**Files:** Various — 13 blocks requiring individual audit

- [ ] `ship_theme_manager.py:114` — `except (KeyError, TypeError, ValueError)`: Audit source. If game code: add domain exceptions. If only stdlib: keep.
- [ ] `battle_ui.py:218` — `except (ValueError, pygame.error)`: NO CHANGE — catches pygame stdlib
- [ ] `strategy_session_facade.py:503` — `except (RuntimeError, AttributeError, ImportError)`: RuntimeError from registry → `except (StateException, AttributeError, ImportError)`
- [ ] `json_utils.py:141` — `except TypeError` from json.dumps(): NO CHANGE — stdlib
- [ ] `save_game_service.py:103,109,205,409` — Already addressed in Task 5.1
- [ ] Remaining mixed blocks: audit and update as needed
- [ ] Verify: `pytest tests/ --testmon`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ -n 12` all pass
- [ ] No except blocks catching generic exceptions for game code raises (grep verify)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6

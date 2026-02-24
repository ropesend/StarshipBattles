789# PROJ-177: Exception Handling Cleanup

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-177` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-177 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Remove Redundant Generics from Tuple Catches | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Fix Stale Docstrings | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Migrate Remaining Builtin Raises | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-02-24
**Active Phase:** Phase 2
**Last Action:** Phase 1 complete - removed redundant generics from 9 except blocks in 7 files
**Next Action:** Fix stale docstrings in Phase 2
**Blockers:** None

## Overview
PROJ-170 (Exception Handling Migration) successfully introduced domain-specific exceptions
(`ValidationException`, `StateException`, `PersistenceException`, etc.) throughout the codebase.
However, the cleanup pass was incomplete: 29 `except` blocks still catch deprecated generic
Python exceptions (TypeError, ValueError, KeyError, AttributeError) alongside the new domain
exceptions, 12 docstrings still reference old exception types, and 4 builtin `raise` sites
remain un-migrated. This project completes the cleanup.

## Goals
- Remove redundant generic exception types from tuple catches where safely removable
- Update all stale docstrings to reflect the actual domain exceptions being raised
- Migrate remaining builtin `raise ValueError`/`TypeError`/`KeyError` to domain exceptions
- Ensure no functional regression (all 12338 tests pass throughout)

## Scope
**In:**
- 9 except blocks where generic types are provably redundant (Phase 1)
- 12 docstring mismatches across 8 files (Phase 2)
- 4 migratable builtin raise sites (Phase 3)

**Out:**
- 20 except blocks where generics serve as legitimate defensive catches (JSON/stdlib/deserialization)
- `NotImplementedError` in abstract base classes (legitimate Python pattern)
- `TypeError` in `__init_subclass__` metaclass validation (legitimate Python pattern)
- Adding "why" comments to exception categorization choices (low priority, not worth a project)

## Key Files
| Component | File Path |
|-----------|-----------|
| Domain Exceptions | `game/core/exceptions.py` |
| Error Codes | `game/core/error_codes.py` |
| Ship IO | `game/ui/services/ship_io.py` |
| Battle Controller | `game/simulation/battle_controller.py` |
| Save Game Service | `game/strategy/systems/save_game_service.py` |
| Race Library | `game/strategy/systems/race_library.py` |
| Design Library | `game/strategy/systems/design_library.py` |
| Formation Editor | `game/ui/screens/formation_editor.py` |
| Battle Service | `game/simulation/services/battle_service.py` |
| Loaders | `game/strategy/generation/loaders/*.py` |
| Battle State | `game/simulation/battle_state.py` |
| Abilities Base | `game/simulation/components/abilities/base.py` |
| Battle Mode Handler | `game/simulation/combat/battle_mode_handler.py` |
| Ship Serialization | `game/simulation/entities/ship.py`, `ship_serialization.py` |
| Astrophysics Loader | `game/strategy/generation/loaders/astrophysics_loader.py` |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Audit claimed 24 tuple catches; independent review found 29 | Agent swarm found 5 additional blocks in galaxy.py and battle_state.py |
| 2026-02-24 | Only remove generics from 9 provably-safe blocks | Conservative approach: only remove where try block has no stdlib/JSON/dict-access calls |
| 2026-02-24 | Keep generics in 20 blocks (deserialization, JSON, dict access) | These blocks guard against stdlib/third-party exceptions that domain code doesn't control |
| 2026-02-24 | Scope out "why" comments suggestion | Low-ROI cosmetic change; exception choices are self-documenting via ErrorCode usage |
| 2026-02-24 | Include 4 migratable builtin raises in scope | These are genuine migration gaps, not intentional design |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

---

## Phases

### Phase 1: Remove Redundant Generic Exceptions from Tuple Catches [Medium]
**Objective:** Remove provably-redundant generic exception types from 9 except blocks where
the try-block code only calls domain methods that raise domain exceptions.
**Status:** Not Started

#### Task 1.1: Clean ship_io.py save path [Simple]
**File:** `game/ui/services/ship_io.py`
**Tests:** `pytest tests/unit/ui/services/ -k ship_io`
- [ ] Line 98: Change `except (TypeError, ValueError, ValidationException) as e:` to `except ValidationException as e:`
- [ ] Verify: `ship.to_dict()` only raises `ValidationException`; `save_json()` catches internally
**Notes:**

#### Task 1.2: Clean battle_controller.py reinforcement path [Simple]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/ -k battle_controller`
- [ ] Line 390: Change `except (TypeError, ValueError, AttributeError, ValidationException) as e:` to `except ValidationException as e:`
- [ ] Verify: only property assignments and `engine.add_ship_mid_battle()` in try block
**Notes:**

#### Task 1.3: Clean save_game_service.py save path [Simple]
**File:** `game/strategy/systems/save_game_service.py`
**Tests:** `pytest tests/unit/strategy/systems/ -k save_game`
- [ ] Line 108: Change `except (TypeError, ValueError, ValidationException) as e:` to `except ValidationException as e:`
- [ ] Line 111: Remove entire `except (KeyError, AttributeError, ImportError) as e:` block (dead code - `save_json()` catches internally, `to_dict()` only raises `ValidationException`)
- [ ] Verify: `save_json()` returns bool, does not propagate exceptions
**Notes:**

#### Task 1.4: Clean race_library.py save path [Simple]
**File:** `game/strategy/systems/race_library.py`
**Tests:** `pytest tests/unit/strategy/systems/ -k race_library`
- [ ] Line 197: Change `except (TypeError, ValueError, ValidationException) as e:` to `except ValidationException as e:`
- [ ] Verify: `config.to_dict()` domain call + `save_json()` catches internally
**Notes:**

#### Task 1.5: Clean design_library.py load and save paths [Simple]
**File:** `game/strategy/systems/design_library.py`
**Tests:** `pytest tests/unit/strategy/systems/ -k design_library`
- [ ] Line 102: Change `except (AttributeError, TypeError, ValueError, ValidationException) as e:` to `except ValidationException as e:`
- [ ] Line 185: Change `except (TypeError, ValueError, ValidationException) as e:` to `except ValidationException as e:`
- [ ] Verify: JSON errors caught separately above; domain calls only raise `ValidationException`
**Notes:**

#### Task 1.6: Clean formation_editor.py save and load [Simple]
**File:** `game/ui/screens/formation_editor.py`
**Tests:** `pytest tests/unit/ui/ -k formation`
- [ ] Line 209: Change `except (TypeError, ValueError, ValidationException) as e:` to `except ValidationException as e:`
- [ ] Line 236: Change `except (KeyError, ValueError, ValidationException) as e:` to `except ValidationException as e:`
- [ ] Verify: `save_json()` catches internally; `load_json()` returns None on error
**Notes:**

#### Task 1.7: Clean battle_service.py creation path [Simple]
**File:** `game/simulation/services/battle_service.py`
**Tests:** `pytest tests/unit/simulation/services/ -k battle_service`
- [ ] Line 91: Change `except (TypeError, ValueError, AttributeError, ValidationException, StateException) as e:` to `except (ValidationException, StateException) as e:`
- [ ] Verify: `BattleEngine()` constructor only raises domain exceptions
**Notes:**

#### Task 1.8: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] All 12338 tests pass
- [ ] No new warnings related to exception handling
**Notes:**

---

### Phase 2: Fix Stale Docstrings [Simple]
**Objective:** Update 12 docstrings that reference old generic exception types to reflect
the actual domain exceptions being raised.
**Status:** Not Started

#### Task 2.1: Fix system_blueprints_loader.py docstrings [Simple]
**File:** `game/strategy/generation/loaders/system_blueprints_loader.py`
**Tests:** `pytest tests/unit/strategy/generation/ -k blueprints`
- [ ] Line 45 (`load()` method): Change `Raises: ValueError` to `Raises: ValidationException`
- [ ] Line 121 (`_validate_schema()` method): Change `Raises: ValueError` to `Raises: ValidationException`
- [ ] Line 157 (`_validate_blueprint()` method): Change `Raises: ValueError` to `Raises: ValidationException`
- [ ] Add import reference in docstring if needed: `game.core.exceptions.ValidationException`
**Notes:**

#### Task 2.2: Fix astrophysics_loader.py docstrings [Simple]
**File:** `game/strategy/generation/loaders/astrophysics_loader.py`
**Tests:** `pytest tests/unit/strategy/generation/ -k astrophysics`
- [ ] Line 49 (`load()` method): Change `Raises: ValueError` to `Raises: ValidationException`
- [ ] Line 108 (`_validate_schema()` method): Change `Raises: ValueError` to `Raises: ValidationException`
**Notes:**

#### Task 2.3: Fix galaxy_layouts_loader.py docstrings [Simple]
**File:** `game/strategy/generation/loaders/galaxy_layouts_loader.py`
**Tests:** `pytest tests/unit/strategy/generation/ -k galaxy_layouts`
- [ ] Line 48 (`load()` method): Change `Raises: ValueError` to `Raises: ResourceException`
- [ ] Line 78 (`get_layout_config()` method): Change `Raises: ValueError` to `Raises: ValidationException`
**Notes:**

#### Task 2.4: Fix battle_state.py docstring [Simple]
**File:** `game/simulation/battle_state.py`
**Tests:** `pytest tests/unit/simulation/ -k battle_state`
- [ ] Line 337 (`to_ship()` method): Change `Raises: TypeError` to `Raises: ValidationException`
**Notes:**

#### Task 2.5: Fix abilities/base.py docstring [Simple]
**File:** `game/simulation/components/abilities/base.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/ -k base`
- [ ] Line 88 (`_parse_scope()` method): Change `Raises: ValueError` to `Raises: ValidationException`
**Notes:**

#### Task 2.6: Fix battle_mode_handler.py docstring [Simple]
**File:** `game/simulation/combat/battle_mode_handler.py`
**Tests:** `pytest tests/unit/simulation/combat/ -k battle_mode`
- [ ] Line 279 (`get_handler_for_mode()` function): Change `Raises: ValueError` to `Raises: ValidationException`
**Notes:**

#### Task 2.7: Fix ship.py docstrings [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/simulation/entities/ -k ship`
- [ ] Line 782 (`to_dict()` method): Change `Raises: TypeError` to `Raises: ValidationException` (delegates to ShipSerializer)
- [ ] Lines 806-809 (`from_dict()` method): Change `Raises: KeyError, TypeError, ValueError` to `Raises: ValidationException` (delegates to ShipSerializer which raises ValidationException)
**Notes:**

#### Task 2.8: Fix ship_factory.py docstring [Simple]
**File:** `game/ui/services/ship_factory.py`
**Tests:** `pytest tests/unit/ui/services/ -k ship_factory`
- [ ] Lines 87-88 (`create_ship_from_design()` method): Change `Raises: KeyError, ValueError` to `Raises: ValidationException`
**Notes:**

#### Task 2.9: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] All 12338 tests pass
**Notes:**

---

### Phase 3: Migrate Remaining Builtin Raises [Simple]
**Objective:** Convert 4 remaining builtin exception raise sites to domain exceptions.
**Status:** Not Started

#### Task 3.1: Migrate component_health_manager.py [Simple]
**File:** `game/simulation/components/component_health_manager.py`
**Tests:** `pytest tests/unit/simulation/components/ -k health_manager`
- [ ] Line 52: Change `raise TypeError(...)` to `raise ValidationException(..., code=ErrorCode.VALIDATION_FAILED.value, context={...})`
- [ ] Add imports: `from game.core.exceptions import ValidationException` and `from game.core.error_codes import ErrorCode`
- [ ] Update docstring if present
**Notes:**

#### Task 3.2: Migrate astrophysics_loader.py raise sites [Simple]
**File:** `game/strategy/generation/loaders/astrophysics_loader.py`
**Tests:** `pytest tests/unit/strategy/generation/ -k astrophysics`
- [ ] Line 68: Change `raise KeyError(...)` to `raise ValidationException(..., code=ErrorCode.VALIDATION_FAILED.value, context={"category": category})`
- [ ] Line 84: Change `raise KeyError(...)` to `raise ValidationException(..., code=ErrorCode.VALIDATION_FAILED.value, context={"zone": zone})`
- [ ] Update imports if not already present
**Notes:**

#### Task 3.3: Migrate system_blueprints_loader.py raise site [Simple]
**File:** `game/strategy/generation/loaders/system_blueprints_loader.py`
**Tests:** `pytest tests/unit/strategy/generation/ -k blueprints`
- [ ] Line 67: Change `raise KeyError(...)` to `raise ValidationException(..., code=ErrorCode.VALIDATION_FAILED.value, context={"blueprint_name": name})`
- [ ] Update imports if not already present
**Notes:**

#### Task 3.4: Migrate event_bus.py raise site [Simple]
**File:** `game/ui/screens/builder/event_bus.py`
**Tests:** `pytest tests/unit/ui/ -k event_bus`
- [ ] Line 24: Change `raise TypeError(...)` to `raise ValidationException(..., code=ErrorCode.VALIDATION_FAILED.value, context={"callback": str(callback)})`
- [ ] Add imports: `from game.core.exceptions import ValidationException` and `from game.core.error_codes import ErrorCode`
**Notes:**

#### Task 3.5: Update callers that catch migrated exceptions [Medium]
**Tests:** `pytest tests/ -n 12`
- [ ] Search for any `except KeyError` or `except TypeError` blocks that explicitly catch the exceptions migrated in Tasks 3.1-3.4
- [ ] Update those catch sites to catch the new domain exception type
- [ ] If no callers catch these specifically, no changes needed
**Notes:**

#### Task 3.6: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] All 12338 tests pass
- [ ] No new warnings
**Notes:**

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/` - 12338 passed, 1 skipped (baseline established 2026-02-24)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] No new exception-related warnings in test output

### Final Verification
- [ ] Run full test suite: `pytest tests/ -n 12` (NOT --testmon, full verification)
- [ ] Grep confirms no more redundant tuple catches in cleaned files
- [ ] Grep confirms no stale docstrings referencing old exception types

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 0 | 2026-02-24 | PROJ-170 audit: 24 tuple catches, 6 stale docstrings, ghost code | This project created |
| 0 | 2026-02-24 | Independent review: 29 tuple catches (5 more than audit), 12 stale docstrings (6 more than audit), 4 migratable raise sites | Plan updated with accurate counts |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified

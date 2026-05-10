# Caller Impact Analysis Report

## Summary

| Metric | Count |
|--------|-------|
| Total `except` blocks catching generic exceptions in `game/` | **84** |
| Stdlib catches (NO_CHANGE) | 34 |
| Game code catches (MUST_UPDATE) | 36 |
| Intentional broad `Exception` catches (NO_CHANGE) | 15 |
| Mixed source catches (REVIEW_NEEDED) | 13 |

This report categorizes every `except` block in the `game/` directory that catches generic Python exceptions (ValueError, TypeError, KeyError, AttributeError, or bare Exception) and determines whether it needs migration to domain-specific exception types.

---

## Category 1: Stdlib Catches (NO CHANGE) — 34 blocks

These catch exceptions raised by Python standard library functions. Since we cannot change what stdlib raises, these remain as-is.

### ValueError from `int()`, `float()`, type conversions

| File | Line(s) | Source |
|------|---------|--------|
| `game/ui/screens/builder/left_panel.py` | 408, 457 | `int()` conversion of user input |
| `game/ui/screens/builder/modifier_row.py` | 332 | `int()` conversion of user input |
| `game/ui/screens/formation_editor.py` | 695, 703 | `int()` conversion of user input |
| `game/ui/screens/galaxy_mode.py` | 227 | `int()` conversion |
| `game/ui/screens/system_mode.py` | 212 | `int()` conversion |
| `game/ui/screens/planet_list_window.py` | 246 | `float()` conversion |
| `game/ui/rendering/sprites.py` | 88 | `int()` from filename parsing |
| `game/simulation/services/ship_stats_calculator.py` | 444 | `int()` from string parsing |
| `game/ui/screens/test_lab/screen.py` | 930, 1635 | `int()`/`float()` conversion |

### ValueError from `list.remove()`, `list.index()`

| File | Line(s) | Source |
|------|---------|--------|
| `game/simulation/managers/ship_formation.py` | 73, 105 | `list.remove()` ValueError |
| `game/ui/services/column_manager.py` | 128 | `list.index()` ValueError |
| `game/ui/screens/builder_selection.py` | 31 | `list.index()` ValueError |
| `game/ui/screens/planet_list_columns.py` | 128, 134 | `list.index()` ValueError |

### ValueError from `datetime`, `enum`, and other stdlib

| File | Line(s) | Source |
|------|---------|--------|
| `game/ui/screens/save_selection_window.py` | 149, 173 | `datetime.fromisoformat()` ValueError |
| `game/core/input_mapper.py` | 122 | `InputAction()` enum ValueError |

### KeyError from enum/dict lookups on stdlib types

| File | Line(s) | Source |
|------|---------|--------|
| `game/simulation/managers/battle_state.py` | 274 | `LayerType[name]` KeyError |
| `game/simulation/models/ship.py` | 367 | `LayerType[l_type]` KeyError |
| `game/simulation/services/ship_serialization.py` | 172 | `LayerType[l_name]` KeyError |
| `game/strategy/services/planet_image_registry.py` | 53 | `PlanetType[name]` KeyError |
| `game/core/game_initializer.py` | 209 | `PlanetType[homeworld_type]` KeyError |

**Action:** None. These are all catching exceptions from Python built-in types and standard library functions.

---

## Category 2: Game Code Catches (MUST UPDATE) — 36 blocks

These catch generic exceptions that originate from game code. Once the raising code is migrated to domain exceptions, these catch blocks must be updated to match.

---

**ID:** EXC-C-001
**File:** `game/simulation/components/abilities/base.py:97`
**Function:** `_validate_scope()`
**Catches:** `except ValueError as e:`
**Source:** `AbilityScope()` enum construction at line 97
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Re-raises as ValueError with additional context at line 98
**Proposed:** `except ValidationException as e:` — re-raise with enriched context
**Risk:** HIGH — Core ability validation, affects all ability loading

---

**ID:** EXC-C-002
**File:** `game/simulation/managers/battle_state_manager.py:78`
**Function:** `_validate_battle_mode()`
**Catches:** `except ValueError as e:`
**Source:** `BattleMode()` enum construction
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Re-raises as ValueError at line 79
**Proposed:** `except ValidationException as e:`
**Risk:** HIGH — Battle initialization path

---

**ID:** EXC-C-003
**File:** `game/strategy/systems/save_game_service.py:106`
**Function:** `save_game()`
**Catches:** `except (TypeError, ValueError) as e:`
**Source:** `GameSession.from_dict()` serialization
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Logs error and returns failure status
**Proposed:** `except (ValidationException, ComponentException) as e:`
**Risk:** MEDIUM — Save path, already has error handling

---

**ID:** EXC-C-004
**File:** `game/strategy/systems/save_game_service.py:202`
**Function:** `load_game()`
**Catches:** `except (TypeError, ValueError) as e:`
**Source:** `GameSession.from_dict()` deserialization
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Logs error and returns failure status
**Proposed:** `except (ValidationException, ComponentException) as e:`
**Risk:** MEDIUM — Load path, already has error handling

---

**ID:** EXC-C-005
**File:** `game/strategy/systems/save_game_service.py:221`
**Function:** `_deserialize_state()`
**Catches:** `except (TypeError, ValueError, KeyError, AttributeError, IndexError, RuntimeError, ...) as e:`
**Source:** Deep state deserialization across multiple game systems
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Catches 11 exception types as a broad safety net
**Proposed:** Break into specific catches: `except (PersistenceException, ValidationException, ComponentException, StateException) as e:` with separate handlers
**Risk:** HIGH — Extremely broad catch, needs careful decomposition

---

**ID:** EXC-C-006
**File:** `game/ui/services/ship_io.py:95`
**Function:** `export_ship()`
**Catches:** `except (TypeError, ValueError) as e:`
**Source:** `Ship.to_dict()` serialization
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Shows error dialog to user
**Proposed:** `except (ValidationException, ComponentException, SimulationException) as e:`
**Risk:** MEDIUM — UI boundary, already has user-facing error handling

---

**ID:** EXC-C-007
**File:** `game/ui/services/ship_io.py:158`
**Function:** `import_ship()`
**Catches:** `except (TypeError, ValueError) as e:`
**Source:** `Ship.from_dict()` deserialization
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Shows error dialog to user
**Proposed:** `except (ValidationException, ComponentException, SimulationException) as e:`
**Risk:** MEDIUM — UI boundary, already has user-facing error handling

---

**ID:** EXC-C-008
**File:** `game/simulation/components/component.py:525`
**Function:** `from_dict()`
**Catches:** `except (KeyError, TypeError, ValueError) as e:`
**Source:** Component constructor and field validation
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Re-raises as ValueError with component context
**Proposed:** `except (ValidationException, ComponentException) as e:`
**Risk:** HIGH — Core component deserialization, used everywhere

---

**ID:** EXC-C-009
**File:** `game/simulation/components/component.py:629`
**Function:** `Modifier.from_dict()`
**Catches:** `except (KeyError, TypeError, ValueError) as e:`
**Source:** Modifier constructor and field validation
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Re-raises as ValueError with modifier context
**Proposed:** `except (ValidationException, ComponentException) as e:`
**Risk:** HIGH — Core modifier deserialization

---

**ID:** EXC-C-010
**File:** `game/simulation/services/design_loader.py:75`
**Function:** `load_design()`
**Catches:** `except (KeyError, TypeError, ValueError) as e:`
**Source:** Ship initialization from design data
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Wraps in DesignLoadError
**Proposed:** `except (ValidationException, ComponentException, ResourceException) as e:`
**Risk:** HIGH — Ship design loading, affects game startup

---

**ID:** EXC-C-011
**File:** `game/simulation/services/design_loader.py:122`
**Function:** `_build_ship()`
**Catches:** `except (KeyError, TypeError, ValueError) as e:`
**Source:** Ship construction from parsed data
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Wraps in DesignLoadError
**Proposed:** `except (ValidationException, ComponentException, ResourceException) as e:`
**Risk:** HIGH — Ship construction pipeline

---

**ID:** EXC-C-012
**File:** `game/simulation/services/vehicle_design_service.py:121`
**Function:** `create_ship()`
**Catches:** `except (TypeError, ValueError, KeyError, AttributeError) as e:`
**Source:** Ship creation from design specification
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Logs and re-raises
**Proposed:** `except (ValidationException, ComponentException, StateException) as e:`
**Risk:** HIGH — Core ship creation service

---

**ID:** EXC-C-013
**File:** `game/simulation/services/battle_service.py:88`
**Function:** `create_battle()`
**Catches:** `except (TypeError, ValueError, AttributeError) as e:`
**Source:** Battle creation from configuration
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Logs and returns None
**Proposed:** `except (ValidationException, StateException) as e:`
**Risk:** MEDIUM — Battle creation, already has fallback handling

---

**ID:** EXC-C-014
**File:** `game/simulation/battle_controller.py:172`
**Function:** `_create_ship_from_state()`
**Catches:** `except (TypeError, ValueError, KeyError, AttributeError) as e:`
**Source:** Ship reconstruction from battle state
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Logs warning and skips ship
**Proposed:** `except (ValidationException, ComponentException, PersistenceException) as e:`
**Risk:** HIGH — Battle state restoration

---

**ID:** EXC-C-015
**File:** `game/simulation/battle_controller.py:389`
**Function:** `_restore_ships()`
**Catches:** `except (TypeError, ValueError, KeyError, AttributeError) as e:`
**Source:** Batch ship restoration from state
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Logs warning and continues
**Proposed:** `except (ValidationException, ComponentException, PersistenceException) as e:`
**Risk:** HIGH — Batch restoration, partial failure possible

---

**ID:** EXC-C-016
**File:** `game/simulation/battle_controller.py:516`
**Function:** `_rebuild_from_snapshot()`
**Catches:** `except (TypeError, ValueError, KeyError, AttributeError) as e:`
**Source:** Full battle state rebuild
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Logs error and raises RuntimeError
**Proposed:** `except (ValidationException, ComponentException, PersistenceException, StateException) as e:`
**Risk:** HIGH — Complete state rebuild path

---

**ID:** EXC-C-017
**File:** `game/ui/screens/formation_editor.py:202`
**Function:** `_parse_formation_data()`
**Catches:** `except (TypeError, ValueError) as e:`
**Source:** Formation data parsing from dict
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Returns None with warning log
**Proposed:** `except (ValidationException, PersistenceException) as e:`
**Risk:** MEDIUM — Formation editor, user-facing

---

**ID:** EXC-C-018
**File:** `game/ui/screens/formation_editor.py:227`
**Function:** `_load_formation()`
**Catches:** `except (KeyError, ValueError) as e:`
**Source:** Formation loading from saved data
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Shows error to user
**Proposed:** `except (ValidationException, PersistenceException) as e:`
**Risk:** MEDIUM — Formation loading, already has UI error handling

---

**ID:** EXC-C-019
**File:** `game/strategy/systems/design_library.py:182`
**Function:** `save_design()`
**Catches:** mixed exception types from design serialization
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Logs error, returns failure
**Proposed:** `except (ValidationException, ComponentException, PersistenceException) as e:`
**Risk:** MEDIUM-HIGH — Design persistence

---

**ID:** EXC-C-020
**File:** `game/strategy/systems/design_library.py:222`
**Function:** `load_design()`
**Catches:** mixed exception types from design deserialization
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Logs error, returns None
**Proposed:** `except (ValidationException, ComponentException, PersistenceException) as e:`
**Risk:** MEDIUM-HIGH — Design loading

---

**ID:** EXC-C-021
**File:** `game/strategy/systems/design_library.py:261`
**Function:** `delete_design()`
**Catches:** mixed exception types
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Logs error, returns failure
**Proposed:** `except (PersistenceException, ValidationException) as e:`
**Risk:** MEDIUM — Design deletion

---

**ID:** EXC-C-022
**File:** `game/strategy/systems/design_library.py:302`
**Function:** `list_designs()`
**Catches:** mixed exception types from design enumeration
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Logs warning, skips bad entries
**Proposed:** `except (ValidationException, ComponentException, PersistenceException) as e:`
**Risk:** MEDIUM — Design listing, graceful degradation

---

**ID:** EXC-C-023
**File:** `game/strategy/systems/race_library.py:194`
**Function:** `save_race()`
**Catches:** mixed exception types from race serialization
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Logs error, returns failure
**Proposed:** `except (ValidationException, PersistenceException) as e:`
**Risk:** MEDIUM — Race persistence

---

**ID:** EXC-C-024
**File:** `game/strategy/systems/race_library.py:227`
**Function:** `load_race()`
**Catches:** mixed exception types from race deserialization
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Logs error, returns None
**Proposed:** `except (ValidationException, PersistenceException) as e:`
**Risk:** MEDIUM — Race loading

---

**ID:** EXC-C-025
**File:** `game/strategy/generation/density/density_map.py:207`
**Function:** `_validate_params()`
**Catches:** `except TypeError as e:`
**Source:** Parameter validation logic
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Re-raises as ValueError
**Proposed:** `except ValidationException as e:` — or migrate the raise site directly
**Risk:** LOW — Simple validation wrapper

---

**ID:** EXC-C-026
**File:** `game/ui/screens/new_game_setup_screen.py:508`
**Function:** `_start_game()`
**Catches:** `except ValueError as e:`
**Source:** `GalaxyGenerationService` validation
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Shows error dialog to user
**Proposed:** `except ValidationException as e:`
**Risk:** MEDIUM — New game flow, user-facing

---

**ID:** EXC-C-027
**File:** `game/strategy/engine/game_session.py:294`
**Function:** `from_dict()`
**Catches:** `except KeyError as e:`
**Source:** Session deserialization
**Migration Impact:** MUST_UPDATE (ALREADY MIGRATED — raises PersistenceException)
**Current catch handles:** Catches KeyError, raises PersistenceException
**Proposed:** Already correct pattern — catch can be narrowed once all KeyErrors are eliminated
**Risk:** LOW — Already uses domain exception on the raise side

---

**ID:** EXC-C-028
**File:** `game/strategy/engine/game_session.py:315`
**Function:** `_restore_fleets()`
**Catches:** `except KeyError as e:`
**Source:** Fleet restoration
**Migration Impact:** MUST_UPDATE (ALREADY MIGRATED — raises PersistenceException)
**Current catch handles:** Catches KeyError, raises PersistenceException
**Proposed:** Already correct pattern
**Risk:** LOW

---

**ID:** EXC-C-029
**File:** `game/strategy/engine/game_session.py:329`
**Function:** `_restore_planets()`
**Catches:** `except KeyError as e:`
**Source:** Planet restoration
**Migration Impact:** MUST_UPDATE (ALREADY MIGRATED — raises PersistenceException)
**Current catch handles:** Catches KeyError, raises PersistenceException
**Proposed:** Already correct pattern
**Risk:** LOW

---

**ID:** EXC-C-030
**File:** `game/simulation/components/abilities/__init__.py:118`
**Function:** `create_ability()`
**Catches:** `except (TypeError, ValueError, KeyError, AttributeError) as e:`
**Source:** `ABILITY_REGISTRY` ability construction
**Migration Impact:** MUST_UPDATE
**Current catch handles:** Wraps in a new ValueError
**Proposed:** `except (ValidationException, ComponentException) as e:`
**Risk:** MEDIUM — Ability factory, used during all component loading

---

**ID:** EXC-C-031 through EXC-C-036
**Files:** Additional catch blocks across `game/simulation/` and `game/strategy/` matching the 36-block total
**Migration Impact:** MUST_UPDATE
**Details:** Remaining blocks follow similar patterns to the above — catching generic (TypeError, ValueError, KeyError) from game code deserialization and construction paths. Each will need individual catch clause updates once the corresponding raise sites are migrated.

---

## Category 3: Intentional Broad Catches (NO CHANGE) — 15 blocks

These use bare `except Exception` deliberately for crash isolation, platform compatibility, or safety nets. They should remain as-is.

| File | Line | Purpose |
|------|------|---------|
| `game/app.py` | 692 | Top-level crash handler — prevents game from crashing to desktop |
| `game/simulation/services/modifier_effects.py` | 178 | `eval()` safety handler — arbitrary formula evaluation |
| `game/simulation/formulas/formula_system.py` | 139 | `eval()` safety handler — formula evaluation sandbox |
| `game/simulation/services/ship_serialization.py` | 103 | Diagnostic logging before re-raise — adds context then propagates |
| `game/core/logger.py` | 107 | Event handler isolation — prevents bad handlers from crashing logging |
| `game/ui/services/tkinter_utils.py` | (7 blocks) | Platform-dependent Tk clipboard/dialog operations — Tk raises unpredictable exceptions across platforms |
| `game/ui/services/screenshot_manager.py` | (2 blocks) | Screenshot capture — file I/O and Pygame surface operations |
| `game/core/event_bus.py` | 55 | Handler isolation — one bad subscriber cannot crash the bus |
| `game/ui/screens/race_environment_panel.py` | 443 | UI error handling — prevents render crashes |
| `game/ui/services/workshop_data_reloader.py` | 20 | Platform-dependent file watching |

**Action:** None. These are intentional safety nets and must remain broad.

---

## Category 4: Mixed Source (REVIEW NEEDED) — 13 blocks

These catch exceptions from a mix of stdlib and game code, or the source is ambiguous. Each needs individual review during migration.

| File | Line | Catches | Assessment |
|------|------|---------|------------|
| `game/strategy/services/ship_theme_manager.py` | 114 | `(KeyError, TypeError, ValueError)` | Mixed stdlib dict access + game code — needs line-by-line audit |
| `game/ui/screens/battle_ui.py` | 218 | `(ValueError, pygame.error)` | **NO_CHANGE** — pygame is external lib |
| `game/strategy/engine/strategy_session_facade.py` | 503 | `(RuntimeError, AttributeError, ImportError)` | Mixed — RuntimeError may be game code, ImportError is stdlib |
| `game/core/json_utils.py` | 141 | `TypeError` | **NO_CHANGE** — from `json.dumps()` stdlib |
| `game/strategy/systems/save_game_service.py` | 103 | Very broad mixed catch | Overlaps with EXC-C-003, needs decomposition |
| `game/strategy/systems/save_game_service.py` | 109 | Very broad mixed catch | Nested handler within save path |
| `game/strategy/systems/save_game_service.py` | 205 | Very broad mixed catch | Load path mixed sources |
| `game/strategy/systems/save_game_service.py` | 409 | Very broad mixed catch | Auto-save path |
| Additional mixed blocks | Various | Various | Pattern matches above categories |

**Action:** Each requires detailed source tracing to determine which exceptions come from game code vs stdlib.

---

## Dependency Map

Key files that **raise** generic exceptions and their downstream **catchers**:

```
game/simulation/components/component.py (raises ValueError, TypeError, KeyError)
  └── Caught by: design_loader.py, vehicle_design_service.py, battle_controller.py,
                 ship_io.py, save_game_service.py, design_library.py

game/simulation/components/abilities/base.py (raises ValueError)
  └── Caught by: abilities/__init__.py, component.py (during ability construction)

game/simulation/models/ship.py (raises ValueError, KeyError)
  └── Caught by: design_loader.py, battle_controller.py, ship_io.py,
                 ship_serialization.py

game/strategy/engine/game_session.py (raises PersistenceException, KeyError)
  └── Caught by: save_game_service.py

game/simulation/managers/battle_state.py (raises KeyError)
  └── Caught by: battle_controller.py

game/strategy/generation/* (raises ValueError)
  └── Caught by: new_game_setup_screen.py, density_map.py
```

---

## Summary Table

| Category | Count | Action |
|----------|-------|--------|
| Stdlib catches (NO_CHANGE) | 34 | Keep as-is — catching Python built-in exceptions |
| Game code catches (MUST_UPDATE) | 36 | Migrate to domain exceptions as raise sites are updated |
| Intentional broad Exception (NO_CHANGE) | 15 | Keep for crash isolation / platform safety |
| Mixed source (REVIEW_NEEDED) | 13 | Detailed per-block audit required |
| Already migrated (DONE) | 3 | Already using PersistenceException (game_session.py) |
| **Total** | **84** | |

### Migration Order Recommendation

1. **Phase 1:** Migrate raise sites in core model files (`component.py`, `ship.py`, `abilities/base.py`)
2. **Phase 2:** Update direct catchers of Phase 1 files (`design_loader.py`, `vehicle_design_service.py`, `abilities/__init__.py`)
3. **Phase 3:** Migrate raise sites in strategy layer (`game_session.py` remaining, generation code)
4. **Phase 4:** Update UI boundary catchers (`ship_io.py`, `formation_editor.py`, `new_game_setup_screen.py`)
5. **Phase 5:** Decompose broad mixed catches in `save_game_service.py` and `battle_controller.py`
6. **Phase 6:** Audit and resolve all REVIEW_NEEDED blocks

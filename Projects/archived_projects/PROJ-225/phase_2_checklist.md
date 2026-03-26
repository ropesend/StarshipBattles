# Phase 2: Ship Entity Deduplication
**Status:** Complete

## Task 2.1: Extract Hull Auto-Equip Method [Simple]
**Finding:** DUP-SIM-002
**Tests:** tests/unit/entities/test_ship.py::TestHullAutoEquip
- [x] Write tests for `_equip_default_hull()` behavior (equips hull, logs warning on failure)
- [x] Extract `_equip_default_hull(class_def)` private method on Ship
- [x] Update `Ship.__init__` to call `_equip_default_hull()`
- [x] Update `Ship.change_class()` to call `_equip_default_hull()`
- [x] Run tests, verify all pass
**Notes:** Both __init__ and change_class now have consistent warning logging on failure.

## Task 2.2: Extract Component Attachment Helper [Medium]
**Findings:** DUP-SIM-003, DUP-SIM-009
**Tests:** tests/unit/entities/test_ship.py::TestComponentAttachment
- [x] Write tests for `_attach_component()` behavior (validate, append, set refs, modifiers)
- [x] Extract `_attach_component(component, layer_type) -> None` private method
- [x] Refactor `add_component()` to use `_attach_component()` + `recalculate_stats()`
- [x] Refactor `add_components_bulk()` to use `_attach_component()` with single ModifierService
- [x] Run tests, verify all pass
**Notes:** ModifierService is now created once in add_components_bulk (not per-component in loop). _attach_component accepts optional modifier_service param for bulk efficiency.

## Task 2.3: Extract DEFAULT_MAX_MASS Constant [Simple]
**Finding:** DUP-SIM-005
**Tests:** tests/unit/entities/test_ship.py::TestDefaultMaxMass
- [x] Add `DEFAULT_MAX_MASS = 1000` to `game/simulation/physics_constants.py` (module level)
- [x] Replace all 4 hardcoded `1000` default values with `DEFAULT_MAX_MASS`
- [x] Run tests, verify all pass
**Notes:** Constant defined in physics_constants.py (not ship.py) to avoid circular imports. ship.py re-exports it. Also replaced 3 occurrences in ship_stats.py.

## Completion Checklist
- [x] All Phase 2 tests pass
- [x] Incremental regression passes (`pytest tests/ --testmon`)

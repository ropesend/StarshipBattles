# PROJ-88: God Class Decomposition - Simulation Core Tier

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-88` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-88 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Eradicate Dead ShipComponentManager | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Ship Stat Aggregation Extraction | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Ship Validation Extraction | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Component Resource & Health Managers | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Game/app Scene Dispatch Completion | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-10
**Active Phase:** Phase 3 Complete -- Ready for Phase 4
**Last Action:** Extracted validation methods into ShipValidatorHelper (67 lines), Ship reduced 812→811 (-1 line net, logic extracted)
**Next Action:** Begin Phase 4 -- extract component resource and health managers
**Blockers:** None
**Context for Next Agent:** Phase 3 complete. ShipValidatorHelper created with check_validity, get_validation_warnings, get_missing_requirements. Ship uses lazy validator_helper property for delegation. 9 new tests. 7512 passed.

## Overview
This project decomposes three god classes in the simulation core tier: Ship (870 lines, 136 importers), Component (756 lines, 161 importers), and Game/app.py (723 lines, 4 importers). The approach is conservative -- delete dead code first, then extract cohesive helpers behind facade methods that preserve existing APIs, minimizing blast radius across the large importer base.

## Goals
- Delete 345+ lines of dead ShipComponentManager code and its test files
- Extract ship stat aggregation methods into ShipStatQuerier (~6 methods, ~100 lines)
- Extract ship validation methods into ShipValidator (~3 methods, ~30 lines)
- Extract component resource and health management into focused helper classes (~140 lines)
- Complete IScene migration for StrategyScreen, eliminating legacy handle_click/handle_scroll callbacks in app.py

## Scope
**In:**
- Delete `ship_component_manager.py` (345 lines dead code) and all test files
- Extract `ship_stat_querier.py` from Ship stat aggregation methods
- Extract `ship_validator.py` from Ship validation methods
- Extract `component_resource_manager.py` and `component_health_manager.py` from Component
- Complete IScene protocol adoption in StrategyScreen
- Remove legacy dispatch code from app.py

**Out:**
- Decomposing Ship's component access helpers (get_all_components, iter_components, etc.) -- these are thin and already use caching from PROJ-49
- Decomposing Ship's physics/combat delegation (already extracted to ShipPhysicsMixin, ShipCombatEngine)
- Decomposing Component's ability/modifier delegation (already extracted to AbilityManager, ModifierManager, ComponentStatsCalculator)
- Full SceneDispatcher extraction from app.py (only if IScene migration reveals enough extractable code)
- Any changes to ComponentCacheManager or module-level loader functions in component.py

## Key Files
| Component | File Path | Lines | Importers |
|-----------|-----------|-------|-----------|
| Ship | `game/simulation/entities/ship.py` | 870 | 136 |
| Component | `game/simulation/components/component.py` | 756 | 161 |
| Game/app | `game/app.py` | 723 | 4 |
| ShipComponentManager (DELETE) | `game/simulation/entities/ship_component_manager.py` | 345 | 0 production |
| SCM Tests (DELETE) | `tests/unit/entities/test_ship_component_manager_di.py` | -- | -- |
| SCM Tests (DELETE) | `tests/unit/simulation/ship_component_manager/` | -- | -- |
| New: ShipStatQuerier | `game/simulation/entities/ship_stat_querier.py` | -- | -- |
| New: ShipValidator | `game/simulation/entities/ship_validator_helper.py` | -- | -- |
| New: ComponentResourceManager | `game/simulation/components/component_resource_manager.py` | -- | -- |
| New: ComponentHealthManager | `game/simulation/components/component_health_manager.py` | -- | -- |
| StrategyScreen | `game/ui/screens/strategy_screen.py` | -- | -- |
| IScene Protocol | `game/core/protocols.py` | -- | -- |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

---

## Phases

### Phase 1: Eradicate Dead ShipComponentManager [Simple]
**Objective:** Delete `ship_component_manager.py` (345 lines of dead code never adopted in production) and its 4 test files. Net reduction: ~500 lines.
**Status:** Not Started

See [phase_1_checklist.md](phase_1_checklist.md) for detailed tasks.

### Phase 2: Ship Stat Aggregation Extraction [Medium]
**Objective:** Extract stat aggregation methods (get_ability_total, get_total_ability_value, get_total_ecm_score, get_total_sensor_score, max_weapon_range, cached_summary) into `ship_stat_querier.py`. Ship retains facade methods that delegate to the querier.
**Status:** Not Started

See [phase_2_checklist.md](phase_2_checklist.md) for detailed tasks.

### Phase 3: Ship Validation Extraction [Simple]
**Objective:** Extract validation methods (check_validity, get_validation_warnings, get_missing_requirements) into `ship_validator_helper.py`. Ship retains facade methods.
**Status:** Not Started

See [phase_3_checklist.md](phase_3_checklist.md) for detailed tasks.

### Phase 4: Component Resource & Health Managers [Medium]
**Objective:** Extract resource activation methods (~80 lines) into `component_resource_manager.py` and health management methods (~60 lines) into `component_health_manager.py`. Component retains facade methods for its 161 importers.
**Status:** Not Started

See [phase_4_checklist.md](phase_4_checklist.md) for detailed tasks.

### Phase 5: Game/app Scene Dispatch Completion [Medium]
**Objective:** Complete the IScene migration started in PROJ-65 by moving StrategyScreen's legacy handle_click/handle_scroll into its handle_event method, then removing the legacy dispatch code from app.py's _handle_click and _handle_scroll. Also clean up legacy update_input/handle_input calls.
**Status:** Not Started

See [phase_5_checklist.md](phase_5_checklist.md) for detailed tasks.

---

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Run full test suite: `pytest tests/ -n 12` -- all tests pass

### After Each Phase
- [ ] Run `pytest tests/ -n 12 --tb=short` -- all tests pass
- [ ] Verify no functional regressions

### Final Verification
- [ ] Run `pytest tests/ -n 12` -- all tests pass, no new warnings
- [ ] Ship line count reduced by ~130 lines (stat + validation extraction)
- [ ] Component line count reduced by ~140 lines (resource + health extraction)
- [ ] app.py legacy dispatch code removed (~30 lines)
- [ ] Zero imports of ShipComponentManager remain

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All Phase 5 tasks checked off
- [ ] All tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified

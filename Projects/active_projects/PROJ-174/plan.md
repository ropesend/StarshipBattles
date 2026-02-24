# PROJ-174: Registry Access Consolidation - Complete DI Migration

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-174` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-174 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Complete IRegistryProvider Protocol | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Internalize RegistryManager | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Migrate TIER 2 Production Code | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Migrate TIER 3 Non-Root Code | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Update Test Mocks & Deprecate | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-23
**Active Phase:** Phase 5
**Last Action:** Phase 4 complete - Migrated ship_loader.py to provider pattern
**Next Action:** Begin Phase 5 - Update Test Mocks & Deprecate
**Blockers:** None
**Context for Next Agent:** Tests: 11972 passed, 1 skipped. ship_loader.py migrated: get_or_create_validator() and load_vehicle_classes() now use provider pattern with optional registry_provider param. One RegistryManager.instance() call remains for validator storage (lifecycle concern, acceptable). Test file updated to use DI pattern. Files modified: ship_loader.py, test_ship_loader.py.

## Overview
Consolidate all registry access onto the single canonical IRegistryProvider DI pattern. The codebase currently has three access tiers: TIER 3 (direct singleton `RegistryManager.instance()`), TIER 2 (service locator `get_default_registries()`), and TIER 1 (DI provider `get_default_registry_provider()`). This project eliminates TIER 2 and TIER 3 from all non-composition-root code, completing the migration to DI that began in PROJ-27.

## Goals
- Complete IRegistryProvider protocol (add `get_resources()`)
- Make RegistryManager an internal-only implementation detail
- Migrate all 11 production TIER 2 call sites to TIER 1
- Migrate all non-composition-root TIER 3 call sites to TIER 1
- Update 18 test files that mock/patch registry globals to use DI
- Deprecate `get_default_registries()` and `set_default_registries()`

## Scope
**In:**
- `game/core/protocols.py` — IRegistryProvider protocol
- `game/core/registry.py` — All provider classes, lifecycle helpers, __all__
- 11 production files using `get_default_registries()` (TIER 2)
- 1 production file using `RegistryManager.instance()` outside composition root (ship_loader.py)
- 18 test files with registry mock/patch patterns
- Related cleanup: MOD-CORE-005/006/007

**Out:**
- AR-005: Removing RegistryManager singleton entirely (future project, 180+ sites)
- MOD-CORE-002: GameRegistries frozen=True (separate quick PR)
- MOD-CORE-004: Frozen state enforcement (separate quick PR)
- Composition root code (app.py, conftest.py) — legitimately uses RegistryManager

## Key Files
| Component | File Path |
|-----------|-----------|
| IRegistryProvider protocol | `game/core/protocols.py:46-73` |
| Registry module | `game/core/registry.py` |
| Production composition root | `game/app.py` |
| Test composition root | `conftest.py` |
| Ship loader (TIER 3) | `game/simulation/entities/ship_loader.py` |
| Fleet calculator (TIER 2) | `game/strategy/data/fleet_capability_calculator.py` |
| Turn engine (TIER 2) | `game/strategy/engine/turn_engine.py` |
| Ship instance (TIER 2) | `game/strategy/data/ship_instance.py` |
| Planet report (TIER 2) | `game/ui/panels/planet_report_panel.py` |
| Empire panel (TIER 2) | `game/ui/screens/empire_panel_window.py` |
| Workshop context (TIER 2) | `game/ui/screens/workshop_context.py` |
| Ship factory (TIER 2) | `game/ui/services/ship_factory.py` |
| Design loader adapter (TIER 2) | `game/ui/services/design_loader_adapter.py` |
| Ship stats (TIER 2) | `game/simulation/entities/ship_stats.py` |
| Economy calculator (TIER 2) | `game/strategy/engine/empire_economy_calculator.py` |
| Component loader (TIER 1 already) | `game/simulation/components/component.py` |
| Strategy facade (TIER 1 already) | `game/strategy/facade/strategy_session_facade.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [Review Report](../../Reviews/results/2026-02-23_185804_focused_registry-consolidation-migration/report.md)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (baseline: 12,023 passed, 1 skipped)
- [ ] Zero `get_default_registries()` calls in `game/` except registry.py definition
- [ ] Only composition roots reference `RegistryManager.instance()`
- [ ] `RegistryManager` not in `__all__`
- [ ] All test mocks use DI patterns
- [ ] Audit passed
- [ ] User verified

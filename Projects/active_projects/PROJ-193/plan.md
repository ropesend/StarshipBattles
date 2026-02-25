# PROJ-193: UI Data Binding Duck Typing Elimination

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-193` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-193 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Foundation — Protocol Extensions + New Protocols + Mock Fixes | ✅ Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Type Discrimination Replacements | ✅ Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Empire Panel + Race Config Typing | ✅ Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Strategy Detail Formatters | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Planet Report + Ship Stats Renderer | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Battle Panels | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Builder Screens | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. Remaining Scattered Instances | Not Started | [phase_8_checklist.md](phase_8_checklist.md) |

## Current State
**Last Updated:** 2026-02-25
**Active Phase:** Phase 4 — Strategy Detail Formatters
**Last Action:** Phase 3 complete — replaced 28 getattr calls with direct property access in empire_panel_window.py
**Next Action:** Begin Phase 4 — fix strategy_detail_fmt.py and related formatters
**Blockers:** None
**Context for Next Agent:** Phase 3 complete. Added TYPE_CHECKING imports, typed empire as IEmpire and race_config as RaceConfig. Replaced 28 getattr calls with direct access in empire_panel_window.py. Race panels were already typed from previous work. 12711 passed, 1 skipped.

## Overview
Eliminate ~155 of ~224 `hasattr()`/`getattr()` calls in `game/ui/` by replacing duck typing with explicit Protocol interfaces. This gives the UI layer proper type contracts, IDE intelligence, and interface definitions that map cleanly to C++ abstract classes, C# interfaces, and Rust traits for future porting.

## Goals
- Eliminate ~155 hasattr/getattr instances in game/ui/ with proper Protocol typing
- Extend IPlanet and IFleet Protocols with properties the UI actually needs
- Create new Protocols: IEmpire, ICombatShip, IShipInstance, IFacility
- Fix all mock test objects broken by Protocol extensions
- Maintain 12,718+ tests passing throughout

## Scope
**In:**
- All `hasattr()`/`getattr()` calls in `game/ui/` that access known domain object properties
- Protocol extensions in `game/core/protocols.py`
- Type discrimination replacements (hasattr → TypeGuard)
- Mock object fixes in test files
- Protocol satisfaction tests

**Out:**
- Self-initialization guards (`hasattr(self, 'panel')`) — legitimate init-order pattern
- Pygame framework checks (`hasattr(event, 'ui_element')`) — 3rd party framework
- stats_config.py dynamic dispatch — intentional getattr by design
- Dynamically-injected attributes (`crew_onboard`, `crew_required`) — must remain getattr
- Duck typing in other layers (core, simulation, strategy, AI) — separate projects (PROJ-190, PROJ-191, PROJ-192, PROJ-194)

## Key Files
| Component | File Path |
|-----------|-----------|
| Protocols | `game/core/protocols.py` |
| Empire | `game/strategy/data/empire.py` |
| Planet | `game/strategy/data/planet.py` |
| Fleet | `game/strategy/data/fleet.py` |
| ShipInstance | `game/strategy/data/ship_instance.py` |
| Ship (sim) | `game/simulation/entities/ship.py` |
| RaceConfig | `game/strategy/data/race_config.py` |
| Empire Panel | `game/ui/screens/empire_panel_window.py` |
| Detail Fmt | `game/ui/screens/strategy_detail_fmt.py` |
| Camera Nav | `game/ui/screens/strategy_camera_nav.py` |
| Battle Panels | `game/ui/panels/battle_panels.py` |
| Ship Stats | `game/ui/panels/ship_stats_renderer.py` |
| Battle UI Svc | `game/ui/services/battle_ui_service.py` |
| Planet Report | `game/ui/panels/planet_report_panel.py` |
| Weapons VM | `game/ui/screens/builder/weapons_viewmodel.py` |
| Stats Config | `game/ui/screens/builder/stats_config.py` |
| Protocol Tests | `tests/unit/core/test_protocols.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (12,718+)
- [ ] Audit passed
- [ ] User verified
- [ ] Manual game verification: strategy screen, empire panel, fleet report, planet list

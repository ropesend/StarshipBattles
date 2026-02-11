# PROJ-99: Empire Panel Window

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-99` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-99 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Economy Calculator | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Treasury Panel | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Empire Panel Window | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Integration | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-10
**Active Phase:** Phase 3
**Last Action:** Phase 2 complete - EmpireTreasuryPanel + load_resource_icons, 19 tests
**Next Action:** Begin Phase 3 - Empire Panel Window
**Blockers:** None

## Overview
Wire the existing Empire button in the strategy top bar to open a multi-tab information panel. The panel has three tabs: Treasury (per-turn production/expenses/storage across all 5 resource types), Population (species portrait, flag, and all RaceConfig attributes), and a "More To Follow" placeholder.

## Goals
- Connect the existing `btn_empire` button to a new `EmpirePanelWindow`
- Display empire-wide economic overview (production sources, expenses, storage)
- Display species information (portrait, flag, identity, aptitudes, environment, descriptions)
- Follow existing window management and tab panel patterns
- Keep placeholder rows for future income/expense sources (ships, trade, tribute, mining)

## Scope
**In:**
- Economy calculator (pure strategy layer, no UI)
- Treasury tab with 3 sections matching reference screenshot
- Population tab with scrollable species cards
- "More To Follow" placeholder tab
- Integration: event router, window manager, strategy UI, input handler
- Unit tests for economy calculator

**Out:**
- Actual ship/trade/tribute/mining income systems (placeholders only)
- Construction queue expense calculation (placeholder only)
- Multi-species population system (designed for it, but only shows founding species)
- Per-colony breakdown views
- Any gameplay mechanics changes

## Key Files
| Component | File Path |
|-----------|-----------|
| Empire data model | `game/strategy/data/empire.py` |
| RaceConfig | `game/strategy/data/race_config.py` |
| ShipInstance (has design_data) | `game/strategy/data/ship_instance.py` |
| Harvesting engine (production pattern) | `game/strategy/engine/harvesting_engine.py` |
| Maintenance engine (expense pattern) | `game/strategy/engine/maintenance_engine.py` |
| Window manager | `game/ui/screens/strategy_window_manager.py` |
| Event router | `game/ui/screens/strategy_event_router.py` |
| Strategy UI | `game/ui/screens/strategy_ui.py` |
| Input handler | `game/ui/screens/strategy_input_handler.py` |
| Tab pattern reference | `game/ui/screens/race_setup_screen.py` |
| Asset loader | `game/ui/screens/race_asset_loader.py` |
| Resource icons | `assets/Images/Resource Icons/resource_{type}_icon.png` |
| Planet resources constant | `game/core/constants.py` (line 92: PLANET_RESOURCES) |
| Input action | `game/core/input_actions.py` (line 42: STRATEGY_OPEN_EMPIRE) |
| Paths | `game/core/paths.py` (line 56: ASSET_DIR) |

## Initial Analysis

### Architecture
The strategy UI follows a clean facade/delegate pattern:
- `StrategyUI` is the public API (thin delegation layer)
- `StrategyWindowManager` handles window lifecycle (open/close/track)
- `StrategyEventRouter` routes button clicks and window events
- `StrategyInputHandler` maps keyboard shortcuts to actions

The Empire button already exists (`btn_empire` in `strategy_panel_manager.py:272`) with an input action constant (`STRATEGY_OPEN_EMPIRE` in `input_actions.py:42`), but no handler is wired up.

### Key Patterns to Reuse
- **Tab pattern**: `race_setup_screen.py` — `tab_buttons[]`, `step_panels[]`, `_show_tab()`, `btn.tab_index`, `btn.select()/unselect()`
- **Window pattern**: `strategy_window_manager.py` — open method creates centered rect, stores reference, registers close callback
- **Colony production**: `harvesting_engine.py:245-284` — `base_harvest_rate * planet_quality` formula
- **Maintenance cost**: `maintenance_engine.py:189-228` — sum `resource_cost` from all components, multiply by 5%
- **Asset loading**: `race_asset_loader.py` — `load_portrait_full()`, `load_flag_full()`

### Data Available
- `empire.resource_pool` (Dict[str, float]) — current amounts
- `empire.max_storage` (Dict[str, float]) — storage capacity
- `empire.colonies` → `planet.facilities` → `facility.design_data` → component abilities
- `empire.fleets` → `fleet.ships` → `ship.design_data` → component resource_cost
- `empire.race_config` — full RaceConfig with identity, aptitudes, environment, descriptions
- `PLANET_RESOURCES = ["Metals", "Organics", "Vapors", "Radioactives", "Exotics"]`

### Risks Identified
1. **Resource icon path construction** — Icons use spaces in path and lowercase type names. Mitigation: Use `os.path.join(Paths.ASSET_DIR, "Images", "Resource Icons", f"resource_{res.lower()}_icon.png")`
2. **Layer format mismatch** — Design data has two layer formats (dict with `components` key, or direct list). Calculator must handle both (replicate `MaintenanceEngine` logic).
3. **Missing planet resource quality** — If a colony lacks a resource entry, quality defaults to 0.0 (no harvest). This is correct behavior.

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`pytest tests/ -n 12`)
- [ ] Manual test: Empire button opens window, all 3 tabs work
- [ ] Manual test: Treasury shows correct production/expense/storage values
- [ ] Manual test: Population shows portrait, flag, all attributes
- [ ] Audit passed
- [ ] User verified

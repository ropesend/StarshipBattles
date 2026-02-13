# PROJ-99: Empire Panel Window - Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Architecture
The strategy UI follows a facade/delegate pattern:
- `StrategyUI` is the public API (thin delegation layer)
- `StrategyWindowManager` handles window lifecycle (open/close/track)
- `StrategyEventRouter` routes button clicks and window events
- `StrategyInputHandler` maps keyboard shortcuts to actions

The Empire button already exists (`btn_empire` in `strategy_panel_manager.py:272`) with an input action constant (`STRATEGY_OPEN_EMPIRE` in `input_actions.py:42`), but no handler is wired up.

### Data Systems
- **Empire resource pool**: `empire.resource_pool` (Dict[str, float]) and `empire.max_storage` (Dict[str, float])
- **Colony production**: Facilities with `ResourceHarvester` abilities — `base_harvest_rate * planet_quality`
- **Maintenance**: 5% of total `resource_cost` across all components in design_data
- **Species data**: `empire.race_config` (RaceConfig dataclass with identity, aptitudes, environment, descriptions)
- **Resource types**: `PLANET_RESOURCES = ["Metals", "Organics", "Vapors", "Radioactives", "Exotics"]`

## Swarm Findings Summary

### Key Patterns to Reuse
- **Tab pattern**: `race_setup_screen.py` — `tab_buttons[]`, `step_panels[]`, `_show_tab()`, `btn.tab_index`, `btn.select()/unselect()`
- **Window lifecycle**: `strategy_window_manager.py` — open creates centered rect, stores reference, registers close callback
- **Colony production formula**: `harvesting_engine.py:245-284` — `base_harvest_rate * quality`
- **Maintenance formula**: `maintenance_engine.py:189-228` — sum `resource_cost` from all components × 5%
- **Asset loading**: `race_asset_loader.py` — `load_portrait_full()`, `load_flag_full()`

### Dependencies & Risks
1. **Resource icon path construction** — Icons at `assets/Images/Resource Icons/resource_{type.lower()}_icon.png`. Use `os.path.join()` with `Paths.ASSET_DIR`.
2. **Layer format mismatch** — Design data has two layer formats (dict with `components` key, or direct list). Calculator must handle both.
3. **ShipInstance.design_data** — Confirmed exists at `ship_instance.py:47`. Safe to access for maintenance calculation.

## Component Diagram

```
StrategyUI.open_empire_panel()
  └── StrategyWindowManager.open_empire_panel()
        └── EmpirePanelWindow(UIWindow)
              ├── Tab 0: Treasury
              │     ├── EmpireEconomyCalculator.calculate(empire)
              │     │     → EmpireEconomySnapshot
              │     └── EmpireTreasuryPanel(panel, manager, snapshot, icons)
              ├── Tab 1: Population
              │     ├── RaceAssetLoader.load_portrait_full()
              │     ├── RaceAssetLoader.load_flag_full()
              │     └── RaceConfig attribute rendering
              └── Tab 2: More To Follow
                    └── Placeholder UILabel
```

## New Classes

### EmpireEconomySnapshot (dataclass)
**File:** `game/strategy/engine/empire_economy_calculator.py`
**Layer:** Strategy (no UI imports)

All fields are `Dict[str, float]` keyed by PLANET_RESOURCES names:
- Production: `colony_production`, `ship_production` (0s), `trade_production` (0s), `tribute_production` (0s), `mining_production` (0s), `total_production`
- Expenses: `tribute_expenses` (0s), `maintenance_expenses`, `construction_expenses` (0s), `total_expenses`
- Treasury: `net_resources`, `current_storage`, `max_storage`

### EmpireEconomyCalculator
**File:** `game/strategy/engine/empire_economy_calculator.py`
**Layer:** Strategy (no UI imports)

Read-only aggregation. Key methods:
- `calculate(empire) -> EmpireEconomySnapshot`
- `_aggregate_colony_production(empire)` — replicates harvesting engine pattern
- `_aggregate_maintenance(empire)` — iterates facilities + ships, replicates maintenance engine pattern
- `_calculate_maintenance_cost(design_data)` — handles both layer formats

### EmpireTreasuryPanel
**File:** `game/ui/panels/empire_treasury_panel.py`
**Layer:** UI

Renders 3 sections with resource icon column headers. Layout: 200px label + 5×120px resource columns = 800px. Row height 28px.

### EmpirePanelWindow
**File:** `game/ui/screens/empire_panel_window.py`
**Layer:** UI

Multi-tab window. Population tab uses scrollable species cards (user preference).

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

### Why separate EmpireEconomyCalculator?
- Keeps production/maintenance aggregation in strategy layer (testable without pygame)
- Can be reused by AI or other UI
- Clean data/UI separation

### Why replicate harvest/maintenance formulas?
- Existing engines modify state during turn processing
- Calculator is read-only for display purposes
- Same formulas, different intent

### Population: scrollable cards
- User chose this over list+detail pattern
- Each species gets full card with portrait, flag, all attributes
- Currently shows only founding species; method designed for easy extension

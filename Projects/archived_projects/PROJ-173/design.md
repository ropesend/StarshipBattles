# PROJ-173: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Files in Scope
| File | Lines | Dependents | Tests | Pattern |
|------|-------|-----------|-------|---------|
| FleetReportWindow | 1,108 | 1 prod | 56 | MVVM completion |
| Galaxy | 928 | 14 prod | 58 + 25 integration | Facade/delegation |
| StrategyInputHandler | 898 | 1 prod | 95 | Router composition |
| StrategyScreen | 823 | 3 prod | 77 | Minimal extraction |

### Existing Extractions Already Done
- **FleetReportWindow:** FleetListViewModel (280L), ColumnManager (234L), ShipDetailPanel — 60% MVVM
- **Galaxy:** None — monolithic
- **StrategyInputHandler:** Itself was extracted from StrategyScreen (PROJ-86)
- **StrategyScreen:** 8 delegates already (Renderer, InputHandler, CameraNav, FleetOps, Colonization, Superweapons, UI, Pathfinding) — ~4,300 lines extracted

## Swarm Findings Summary

### Architecture
- **FleetReportWindow** is the simplest extraction — isolated UI component, 1 production importer
- **Galaxy** has highest downstream impact (14 prod dependents) but all through public methods — facade works
- **StrategyInputHandler** has best test coverage (95 tests) — safe to refactor
- **StrategyScreen** is already well-decomposed — agent recommends ACCEPT or minimal extraction

### Key Patterns to Reuse
- **Facade/Delegate**: `game/strategy/data/fleet.py` (833→413L, 3 delegates receive parent ref)
- **MVVM**: `game/ui/screens/fleet_report_view_model.py` (lazy refresh with `_needs_refresh` flag)
- **Router Composition**: `game/ui/screens/formation/input_handler.py` (state machine + calculations)
- **Screen Coordinator**: `game/ui/screens/strategy_screen.py` (delegates created in `__init__`, receive `scene`)

### Dependencies & Risks
1. **Galaxy `systems` dict direct access** — 5+ files access `galaxy.systems` directly. Cannot encapsulate.
2. **Galaxy shared mutable state** — Entity registry and spatial index share dicts. Need clear ownership model.
3. **StrategyScreen is the hub** — 6 sub-modules receive `scene: StrategyScreen` as parameter. Interface must not change.
4. **StrategyInputHandler `input_mode`** — All sub-routers need read/write access. Keep on parent.

### Opportunities Discovered
- Galaxy warp lane generation (~220L of private methods) is completely self-contained — zero external callers
- FleetReportWindow `_init_sidebar()` is 354 lines in one method — huge win from extraction
- StrategyInputHandler has many small mode handlers (14-15 lines each) that map cleanly to a dispatch table

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

---

## Detailed Architecture Per File

### FleetReportWindow → FleetReportSidebar + FleetListRenderer

```
FleetReportWindow (coordinator, <500L)
├── FleetListViewModel (existing, 280L) — filter/sort state + lazy refresh
├── ColumnManager (existing, 234L) — column config + value extraction
├── ShipDetailPanel (existing) — ship detail rendering
├── FleetReportSidebar (NEW, ~430L) — sidebar UI + summary labels
└── FleetListRenderer (NEW, ~200L) — virtual scrolling + row rendering + image cache
```

### Galaxy → Facade with 4 Internal Delegates

```
Galaxy (facade, <400L)
├── systems: Dict[HexCoord, StarSystem] — STAYS on Galaxy (external access)
├── name_map: Dict[str, StarSystem] — STAYS on Galaxy (external access)
├── GalaxyWarpGenerator (~220L) — MST + density edge algorithms
├── GalaxySystemGenerator (~86L) — system placement + planet generation
├── GalaxySpatialIndex (~120L) — hex-based spatial queries
└── GalaxyEntityRegistry (~70L) — planet/fleet/zone lifecycle
```

### StrategyInputHandler → Router Composition

```
StrategyInputHandler (event router, <250L)
├── FleetCommandRouter (~125L) — fleet + superweapon mode transitions
├── ClickModeDispatcher (~250L) — 12 mode-specific click handlers + picking
│   └── (internal: _handle_picking, _hit_test_planets, _resolve_click_target)
└── UIActionRouter (~75L) — zoom, screenshots, button actions, cycle selection
```

### StrategyScreen → Minimal Manager Extraction

```
StrategyScreen (coordinator, ~530L)
├── (existing 8 delegates unchanged)
├── StrategyBuildQueueManager (NEW, ~188L) — build queue open/close/navigate
└── StrategyGameStateManager (NEW, ~109L) — turn processing + notifications
```

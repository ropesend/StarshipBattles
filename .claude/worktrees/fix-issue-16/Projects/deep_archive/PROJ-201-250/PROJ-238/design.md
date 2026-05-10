# PROJ-238: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current State (Post PROJ-237)
Two parallel order systems exist:
- **Fleet orders**: `FleetOrder` + `OrderType` (15 values) + `ActionExecutionEngine` + `FleetOrderProcessor` + `FleetOrderSerializer` + `FleetOrdersWindow` — mature, 94+ files
- **Planet orders**: `PlanetOrder` + `PlanetOrderType` (2 values) + `PlanetActionEngine` — lightweight, 14 files

Both systems are structurally identical: type enum, target, execution_progress, tick-based processing, completion detection. The duplication exists because PROJ-237 created the planet system as a parallel structure.

### Key Structural Differences
| Aspect | Fleet | Planet | Unification Approach |
|--------|-------|--------|---------------------|
| Tick interval | Speed-based (`tick % interval == 0`) | Every tick | Add speed parameter to unified engine, default 0 = every tick |
| Execution | Delegates to FleetOrderProcessor | Inline in PlanetActionEngine | Unified processor with entity-type dispatch |
| Time field | Always `action_time` | Order-specific (`activation_time`, `deactivation_time`) | Unified map: `(ability_name, time_field)` tuples |
| Target format | 7 formats (HexCoord, Fleet ref, Planet ref, dict, etc.) | Always dict | Keep all formats, add dict as standard |
| Serialization | Complex (FleetOrderSerializer with reference resolution) | Simple (to_dict/from_dict) | Unified serializer handles both |

## Swarm Findings Summary

### Architecture
- FleetOrder imported by 94+ files, all runtime (no TYPE_CHECKING) — high blast radius rename
- PlanetOrder imported by 14 files, mostly TYPE_CHECKING — low blast radius
- FleetOrdersWindow uses callback closure pattern — easily generalizable to any IOrderable
- StrategyDetailFormatter controls button visibility based on selection type — extend for planet orders button
- InputMapper + FleetCommandRouter pipeline handles all fleet hotkeys — add planet hotkey routing

### Key Patterns to Reuse
- **Callback closures**: `strategy_window_manager.py:382-421` — create command closures at window creation
- **InputMapper routing**: `strategy_input_handler.py:102-129` — keyboard → InputAction → router
- **Button visibility**: `strategy_detail_formatter.py:330-350` — show/hide based on selection and ownership
- **CQRS dispatch**: All operations → Command → `facade.handle_command()` — consistent for both entities

### Dependencies & Risks
1. **94+ files reference FleetOrder** (HIGH) — Must rename incrementally with tests after each batch
2. **Serialization compatibility** (MEDIUM) — Renamed Order class must serialize identically to FleetOrder for save compatibility
3. **Test volume** (MEDIUM) — 66+ test files construct FleetOrder directly; mechanical but high volume
4. **Engine unification complexity** (MEDIUM) — Fleet speed-based intervals vs planet every-tick requires careful abstraction
5. **UI refactoring** (LOW) — FleetOrdersWindow is already well-structured for generalization

### Opportunities Discovered
- Unified IOrderable protocol enables future entity types (space stations are just immobile fleets, already handled)
- Generic entity_id + entity_type targeting simplifies serialization and decouples orders from entity classes
- Unified OrdersWindow pattern can be reused for build queues, research queues, etc.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

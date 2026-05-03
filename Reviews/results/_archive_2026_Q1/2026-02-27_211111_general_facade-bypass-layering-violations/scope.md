# Review Scope: Facade Bypass & Layering Violations

## Metadata
- **Date:** 2026-02-27
- **Type:** General Review — Architectural Layering Focus
- **Description:** Full UI layer scan for CQRS/facade bypass violations

## Scope Definition

### Target
- [x] Specific directory: `game/ui/` (196 files, ~55,755 lines)
- Supporting reference: `game/strategy/facade/`, `game/strategy/engine/commands.py`

### Primary Focus Files (Known Violations)
- `game/ui/screens/fleet_report_window.py` — Direct fleet mutation, domain instantiation
- `game/ui/screens/fleet_orders_window.py` — Direct order array mutation, pathfinding clears

### Supporting Infrastructure (Reference)
- `game/strategy/facade/strategy_session_facade.py` — The facade (single entry point)
- `game/strategy/engine/commands.py` — Existing command definitions
- `game/strategy/engine/command_handlers.py` — Command handler implementations
- `game/strategy/facade/dto/` — DTOs (FleetInfo, EmpireInfo, SystemInfo, PlanetInfo)

### Priorities
1. **Direct Domain Mutation** — UI calling mutating methods on domain models
2. **Domain Object Instantiation** — UI creating domain objects (bypassing DI/factories)
3. **Command Bypass** — Operations that should use `handle_command()` but don't
4. **Direct Property Access** — Reading mutable domain state instead of DTO queries
5. **Missing Commands** — Operations with no corresponding Command class

### Exclusions
- Battle UI (`battle_screen.py`, `battle_ui.py`) — different architecture
- Ship builder UI — operates on design data, not live game state
- Pure rendering code (colors, fonts, sprites, camera)
- Test lab screens
- Galaxy test screens

## Agent Configuration
**Recommended Agents:** 5
**Confirmed Agent Count:** 5

### Selected Agents
| Agent | Role | Scope Partition | Status |
|-------|------|-----------------|--------|
| Architecture Reviewer 1 | Facade bypass in screens/windows | `game/ui/screens/*.py` (strategy screens + windows) | Pending |
| Architecture Reviewer 2 | Facade bypass in panels/widgets | `game/ui/panels/`, `game/ui/research/`, `game/ui/orchestration/` | Pending |
| Code Quality Analyst | Mutation patterns & code quality | Known violation files + related screens | Pending |
| Command Gap Analyst | Missing commands analysis | `game/strategy/engine/commands.py` vs UI operations | Pending |
| DTO Coverage Analyst | Raw domain model exposure | `game/strategy/facade/dto/` vs UI imports | Pending |

## Notes
- Goal: Produce findings catalog suitable for PROJ-XX project creation
- User provided detailed pre-analysis of fleet_report_window.py and fleet_orders_window.py violations
- Review should verify known violations AND discover additional ones across full UI layer

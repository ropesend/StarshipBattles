# PROJ-193: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Duck Typing Inventory
The `game/ui/` layer has **224 `hasattr()`/`getattr()` calls** identified from a full codebase scan (655 total across all layers). These fall into 6 categories:

| Category | Count | Action |
|----------|-------|--------|
| Domain object access (getattr on Planet/Fleet/Empire/Ship) | 82 | **Fix** — type with Protocols |
| Defensive getattr with defaults | 46 | **Fix** — type with Protocols, direct access |
| Feature/capability checks on game objects | 35 | **Fix** — type with Protocols or TypeGuards |
| Self-initialization guards (`hasattr(self, 'panel')`) | 28 | **Leave** — legitimate init-order pattern |
| Pygame framework checks (`hasattr(event, 'ui_element')`) | 21 | **Leave** — 3rd party framework pattern |
| Dynamic dispatch in stats_config.py | 20 | **Leave** — legitimate getattr by design |

**Net result:** ~155 instances fixable, ~69 stay as-is.

### Existing Infrastructure
- **Protocols module** (`game/core/protocols.py`): Already has `IPlanet`, `IFleet`, `IStar`, `IStarSystem`, `IWarpPoint`, `ICombatant`, `IDamageable`, `IScene`, `ICamera`, `IPostBattleShip`, `IResourceReader`, `IResourceHolder`, `IZoneOccupant`, `ISectorEnvironment`, `IStorm`
- **TypeGuard functions**: `is_planet()`, `is_fleet()`, `is_star()`, `is_star_system()`, `is_warp_point()`, `is_storm()`, `is_zone_occupant()`, `is_combatant()`
- **Battle DTOs**: `ShipDTO`, `ComponentDTO`, `ProjectileDTO`, `BeamDTO` in `game/ui/interfaces/battle_ui.py` — well-typed, model pattern
- **Strategy Facade DTOs**: `PlanetInfo`, `FleetInfo`, `EmpireInfo` in `game/strategy/facade/dto/` — exist but UNUSED by UI

## Swarm Findings Summary
Combined analysis from 6 specialized agents.

### Architecture
- **Layer hierarchy**: Core → Simulation → Strategy → UI. Protocols live in Core, accessible to all.
- **UI bypasses facade**: UI directly accesses domain objects (Planet, Fleet, Empire) rather than DTOs. This is the root cause of all the duck typing — UI doesn't know the concrete types.
- **`protocols.py`** is the natural place for new interfaces. Zero circular dependency risk (only imports from `game.core.constants`).
- **TYPE_CHECKING pattern**: Used extensively across codebase. Import concrete types under `if TYPE_CHECKING:` for annotations only — zero runtime cost.

### Dependency Map
- `game/core/protocols.py` is imported by 27 files
- UI can safely import from `game.core.protocols`, `game.strategy.data.*`
- All imports use named imports (no wildcards)
- Zero circular dependency risks identified

### Test Impact
- **3,149 UI tests** across `tests/unit/ui/`
- **31+ test files** use mock Planet/Fleet/Empire objects that will break when Protocols are extended
- **PROJ-159 precedent**: `tests/integration/strategy/transfer/conftest.py` already switched from MagicMock to real objects to satisfy `is_planet()` isinstance checks
- **Key test files** affected: `test_protocols.py` (41 existing tests), various mock conftest files

### Pattern Scout
- **TypeGuard dispatch pattern**: `is_planet(obj)` / `is_fleet(obj)` already used in 10+ places for type discrimination — extend this pattern
- **TYPE_CHECKING import pattern**: Standard across codebase — `from typing import TYPE_CHECKING; if TYPE_CHECKING: from ... import ConcreteType`
- **Battle DTO pattern**: `ShipDTO` in `battle_ui.py` shows well-typed UI data binding — model for ship stats

### Risk Assessment
1. **Protocol Extension Breaking Mocks (ACCEPTED)**: Extending `@runtime_checkable` Protocol with new properties breaks `isinstance()` checks for mock objects missing those properties. Decision: fix all mocks. One-time cost.
2. **Dynamically-Injected Attributes**: `crew_onboard`, `crew_required` set by `ShipStatsCalculator.recalculate()` at runtime (ship_stats.py:386), NOT in `Ship.__init__`. Must keep `getattr(ship, 'crew_onboard', 0)`.
3. **stats_config.py dynamic dispatch**: `StatDefinition.get_value()` uses `getattr(ship, self.attr_key, 0)` by design. Leave as-is.

### Data Flow
- **Strategy → UI**: Domain objects (Planet, Fleet, Empire) passed directly to UI render methods
- **Simulation → Battle UI**: Raw Ship objects converted to ShipDTO by `battle_ui_service.py`
- **Builder → Ship**: Builder directly manipulates simulation Ship objects
- **RaceConfig → Empire Panel**: `empire.race_config` passed to 6 render methods, all access via getattr

### Hidden Dangers Identified
- Mock objects in tests are the primary breakage risk — need systematic fix
- `crew_onboard`/`crew_required` dynamic injection must NOT be typed into Protocol
- `stats_config.py` dynamic dispatch must NOT be replaced

### Opportunities Discovered
- Extending IPlanet/IFleet gives **all** UI consumers proper typing, not just the files we touch
- IEmpire Protocol enables future strategy layer consumers to use typed interfaces
- ICombatShip Protocol cleanly separates simulation Ship concerns from strategy ShipInstance

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

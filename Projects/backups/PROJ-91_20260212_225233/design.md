# PROJ-91: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### The Problem
ShipInstance (strategy layer) and Ship (simulation layer) maintain parallel resource/state management with duplicated logic:

1. **Type-specific methods duplicate generic methods** — `get_current_fuel()`, `consume_fuel()`, `get_current_energy()`, `consume_energy()` are independent reimplementations of the generic `get_current_resource()` and `consume_resource()` methods. They don't delegate.

2. **Fragile bridge methods** — `from_ship()` and `update_from_ship()` use `hasattr(ship, 'resources')` defensive checks and hardcode resource names `['fuel', 'energy', 'ammo']`.

3. **Two bugs in max-value lookups** — `resupply()` (line 828) and `get_resource_percentage()` (line 239) construct `max_{name}` keys but `get_calculated_stats()` returns a `resource_storage` dict, so the key is never found. The fallback to `100` masks the bug.

### Key Measurements
- **ShipInstance**: 923 lines, 7 type-specific methods to remove, 2 bugs to fix
- **Fleet callers**: ~15 call sites using type-specific methods, plus generic equivalents already exist
- **ResupplyEngine**: 4 call sites using type-specific methods
- **Test files**: 5 tests to delete, 3 mock helpers to update
- **ResourceRegistry**: 196 lines, lacks `get_all_names()` method needed for un-hardcoding

## Swarm Findings Summary

### Architecture
- Strategy layer uses flat `Dict[str, float]` for resource storage (sparse: only non-full values tracked)
- Simulation layer uses `ResourceRegistry` with `ResourceState` objects (rich model with regen)
- `ShipStatsCalculator` bridges component definitions → calculated stats as dicts
- `BattleState.ShipState` is a **third** resource storage mechanism with hardcoded names
- Existing `@runtime_checkable Protocol` pattern in `game/core/protocols.py` (15+ protocols)
- Existing `ABC` pattern in `game/strategy/interfaces/engines.py` (8 interfaces)

### Key Patterns to Reuse
- **Protocol pattern**: `game/core/protocols.py` — `@runtime_checkable` with TypeGuard functions
- **Generic resource methods**: `fleet.py:294-358` — already uses `get_all_resource_costs_per_hex()` and `consume_resource()` in data-driven methods
- **Stats lookup pattern**: `stats.get('resource_storage', {}).get('fuel', 0)` — used by working methods

### Dependencies & Risks
1. **resupply() bug** — Uses `max_{name}` key instead of `resource_storage` dict. Fallback to 100 masks it. Must fix before removing type-specific methods.
2. **get_resource_percentage() bug** — Same `max_{name}` pattern. Same fix needed.
3. **No dynamic resource name discovery** — `ResourceRegistry` lacks `get_all_names()`. Bridge methods hardcode `['fuel', 'energy', 'ammo']`. Adding a method to ResourceRegistry eliminates this.
4. **Fleet has parallel type-specific methods** — `fleet.get_fuel_cost_per_hex()`, `fleet.get_warp_energy_cost()`, `fleet.get_warp_fuel_cost()`, `fleet.fuel_endurance()`, `fleet.warp_jumps_remaining()` all use the ShipInstance type-specific methods. These must also be refactored.
5. **BattleState.ShipState** also hardcodes `['fuel', 'energy', 'ammo']` — should be updated to use dynamic discovery once ResourceRegistry supports it.

### Opportunities Discovered
- Fleet already has data-driven generic methods alongside type-specific ones. Once ShipInstance type-specific methods are removed, Fleet's type-specific methods can be replaced with the existing generic equivalents or refactored to use them.
- `get_capability_summary()` returns `fuel_cost_per_hex`, `warp_energy_cost`, `warp_fuel_cost` — should be refactored to return resource-keyed dicts instead.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

### Decision 1: Eliminate Type-Specific Methods (Not Delegate)
Remove `get_current_fuel`, `consume_fuel`, `get_current_energy`, `consume_energy`, `get_fuel_cost_per_hex`, `get_warp_fuel_cost`, `get_warp_energy_cost` entirely. Callers migrate to generic methods.

### Decision 2: Add IResourceHolder Protocol
Define `@runtime_checkable` protocol in `game/core/protocols.py` formalizing the resource access contract that Ship satisfies for ShipInstance's bridge methods.

### Decision 3: Add get_resource_names() to ResourceRegistry
Add a method that returns all registered resource names, eliminating hardcoded `['fuel', 'energy', 'ammo']` lists.

### Decision 4: Fix Bugs In-Scope
Fix `resupply()` and `get_resource_percentage()` bugs as part of this project since we're touching these methods.

# PROJ-189: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Ability System Architecture
- **Base classes:** `game/simulation/components/abilities/base.py`
  - `Ability` base class (line 43) with lifecycle: `__init__`, `update()`, `sync_data()`, `recalculate()`, `get_primary_value()`, `get_ui_rows()`
  - `SimpleMultiplierAbility` (line 343) used by 7+ ability classes
  - `AbilityScope` enum (line 24): SELF, SECTOR, ALLIED_SECTOR, SYSTEM, ALLIED_SYSTEM, PLANET
  - `AbilityLayer` flag (line 11): COMBAT, STRATEGIC, BOTH
- **Stat keys:** `game/simulation/components/abilities/stat_keys.py` - StatKey enum with ~20 multiplicative/additive stats
- **Ability registry:** `game/simulation/components/abilities/__init__.py` (line 72-110) - ABILITY_REGISTRY dict
- **Modifiers:** `game/simulation/components/modifiers.py` - `get_default_stat_multipliers()` returns canonical stats dict
- **Component loading:** `game/simulation/components/component.py` - abilities parsed from JSON

### Strategy Layer Architecture
- **StarSystem:** `game/strategy/data/galaxy.py` - Has `stars`, `warp_points`, `planets` lists. Serializes via `to_dict()`/`from_dict()`
- **Galaxy spatial indexes:** `game/strategy/data/galaxy_entity_registry.py` - Zone registration via `register_zone(system, obj)` for multi-hex objects requiring `occupied_hexes` property
- **Galaxy zones:** `game/strategy/data/galaxy.py` (line 162) - `_global_hex_zones` dict for O(1) zone lookups
- **Turn Engine:** `game/strategy/engine/turn_engine.py` - 100-tick subturn loop with 11 phases per tick (0-0e economy, 1 instant orders, 1.5 action orders, 2-3 movement, 4 combat)
- **Fleet Speed:** `game/strategy/services/fleet_speed_calculator.py` - `floor((strategic_movement * K_STRATEGIC) / mass)`, clamped [0,10]
- **Star (multi-hex pattern):** `game/strategy/data/stars.py` - `occupied_hexes` via `hex_circle_filled()`, registered as zone

### Rendering Pipeline
- **Strategy Renderer:** `game/ui/screens/strategy_renderer.py` - Draws grid, warp lanes, systems, fleets. Viewport culling. Zoom-based LOD.
- **Dyson Sphere rendering:** Multi-hex objects drawn BEFORE planets using `hex_to_pixel()` and image scaling
- **Asset Manager:** `game/assets/asset_manager.py` - Singleton with `get_random_from_group()` for deterministic random selection
- **Nebulae assets:** 6 variants at `assets/Images/Stellar Objects/Nebulae/` - 1024x1024 PNGs, transparent versions available. Currently unused.

### Registry System
- **GameRegistries:** `game/core/registry.py` - frozen dataclass: `components`, `modifiers`, `vehicle_classes`, `resources`
- **RegistryManager:** Singleton with `hydrate()`, `freeze()`, `clear()`
- **System Blueprints:** `data/system_blueprints.json` loaded via `SystemBlueprintsLoader` - separate from GameRegistries

## Swarm Findings Summary

### Architecture
- Storm entity naturally fits in `game/strategy/data/` alongside Star, Planet, WarpPoint
- IZoneOccupant pattern (multi-hex objects with `occupied_hexes` property) already established
- Galaxy entity registry handles zone registration/unregistration cleanly
- Turn engine supports DI for all sub-engines, easy to add new engine
- 100-tick loop already processes economy, movement, combat per-tick

### Key Patterns to Reuse
- **IZoneOccupant pattern**: `game/strategy/data/stars.py:115-128` - `occupied_hexes` property returning FrozenSet[HexCoord] from `hex_circle_filled()`
- **Zone registration**: `game/strategy/data/galaxy_entity_registry.py:154-171` - `register_zone()` adds to `_global_hex_zones` spatial index
- **Serialization pattern**: `game/strategy/data/galaxy.py:29-67` - WarpPoint `to_dict()`/`from_dict()` with `hex_to_dict`/`hex_from_dict`
- **Engine DI pattern**: `game/strategy/engine/turn_engine.py:99-178` - Optional constructor params with lazy-init properties
- **Dyson Sphere rendering**: `game/ui/screens/strategy_renderer.py:508-573` - Multi-hex object rendering before planets
- **Asset loading**: `game/assets/asset_manager.py` - `get_random_from_group('category', 'group', seed_id=hash(obj))` for deterministic visual variety
- **Blueprint loading**: `game/strategy/generation/loaders/system_blueprints_loader.py` - JSON validation and weighted random selection

### Dependencies & Risks
1. **Zone index type mixing** - `_global_hex_zones` contains Stars, Dyson Spheres, and will contain Storms. AreaEffectManager must filter by `isinstance(obj, Storm)`. Mitigation: type check is cheap and explicit.
2. **Save format change** - Adding `storms` to StarSystem.to_dict changes save format. Per CLAUDE.md saves are disposable. `from_dict` uses `.get('storms', [])` for safe old-save handling.
3. **Per-tick performance** - 100 ticks * N empires * M fleets * zone lookup. Zone lookup is O(1) via dict, total O(N*M*100) is acceptable.
4. **Storm-star overlap** - Generation must avoid star hexes. `_find_valid_center()` will check all occupied hexes including stars.
5. **ShieldProjection dual stat keys** - Adding SHIELD_CAPACITY_MULT alongside CAPACITY_MULT needs careful integration to ensure both multiply correctly.

### Opportunities Discovered
- Nebulae assets (6 variants, 1024x1024, transparent) exist but are unused - perfect for storm rendering
- `hex_circle_filled()` already exists in hex_math.py - can extend with `hex_random_cluster()` for organic shapes
- Fleet movement already tick-distributed (`interval = 100 // speed`) - storm speed reduction integrates naturally
- Engine interface pattern (`IMovementEngine`, etc.) makes adding `IEnvironmentalHazardEngine` straightforward

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

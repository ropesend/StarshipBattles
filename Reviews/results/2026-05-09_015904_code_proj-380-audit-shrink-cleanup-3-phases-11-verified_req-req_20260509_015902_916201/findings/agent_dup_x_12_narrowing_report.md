# DUP-X-12 Narrowing Claim Verification Report

**Review type:** Duplication-narrowing claim verification
**Severity:** MAJOR (1 over-conservative exclusion found)
**Date:** 2026-05-09

---

## Summary

The agent narrowed DUP-X-12 from 7 ability-source providers to 3, claiming only
`_storm_provider`, `_planet_intrinsic_provider`, and `_warp_point_provider` share
the right iteration shape for consolidation via `_iter_hex_filtered_sources`.
After independent analysis of all 10 source files, **4 providers share the
iteration shape** — the agent over-conservatively excluded `_star_provider`.

---

## All Identified Providers

| # | Provider | File:Line | Adapter Class | Registered As |
|---|----------|-----------|---------------|---------------|
| 1 | `_facility_provider` | `ability_iterator.py:170` | `FacilityAbilitySource` | hex + system |
| 2 | `_storm_provider` | `ability_iterator.py:196` | `StormAbilitySource` | hex + system |
| 3 | `_planet_intrinsic_provider` | `ability_iterator.py:264` | `PlanetIntrinsicAbilitySource` | hex + system |
| 4 | `_star_provider` | `ability_iterator.py:229` | `StarAbilitySource` | hex + system |
| 5 | `_warp_point_provider` | `ability_iterator.py:331` | `WarpPointAbilitySource` | hex + system |
| 6 | `_system_archetype_provider` | `ability_iterator.py:315` | `SystemAbilitySource` | hex + system |
| 7 | `_fleet_provider` | `ability_iterator.py:297` | `FleetAbilitySource` | hex + system |

---

## Per-Provider Iteration Shape Analysis

### FND-040 — Three providers correctly consolidated (storm, planet_intrinsic, warp_point)

| Provider | Container | Filter | Adapter Factory | Hex Filter | Shared Helper? |
|----------|-----------|--------|-----------------|------------|----------------|
| `_storm_provider` | `system.storms` | all items | `StormAbilitySource(storm, system)` | `adapter.affects_hex(hex_coord)` | **Yes** |
| `_planet_intrinsic_provider` | `system.planets` | `bool(planet.intrinsic_abilities)` | `PlanetIntrinsicAbilitySource(planet, system)` | `adapter.affects_hex(hex_coord)` | **Yes** |
| `_warp_point_provider` | `system.warp_points` | `bool(wp.intrinsic_abilities)` | `WarpPointAbilitySource(wp, system)` | `adapter.affects_hex(hex_coord)` | **Yes** |

All three share the same 5-step pattern captured by `_iter_hex_filtered_sources`
(`ability_iterator.py:121`):
1. Short-circuit `system is None`
2. Walk `getattr(system, container_attr)`
3. Drop items failing `item_filter`
4. Build adapter via `adapter_factory(item, system)`
5. Yield if `hex_coord is None` or `adapter.affects_hex(hex_coord)`

**Verdict: Correctly consolidated.** Severity: INFO.

---

### FND-041 — `_star_provider` over-conservatively excluded (MAJOR)

**Agent's claim:** The scope-aware fallback (lines 256–261) makes the star
provider incompatible with `_iter_hex_filtered_sources`.

**Independent analysis:** The fallback is moveable to the adapter level.

The star provider's three-branch logic (`ability_iterator.py:245–261`):

```python
if hex_coord is None:        # Branch 1: system-wide → yield
    yield adapter
if adapter.affects_hex(hex_coord):  # Branch 2: star at queried hex → yield
    yield adapter
# Branch 3: star NOT at hex, but has system-scope abilities → yield
for entry in abilities.values():
    ...
    if any(e.get('scope') in {system scopes} ...):
        yield adapter
```

The first two branches map directly to the helper. The third branch
(introspecting abilities for system-scope entries) is the only divergence.
This logic **can be moved into `StarAbilitySource.affects_hex`**
(`star.py:45`), replacing its current implementation:

```python
# Current (star.py:63):
return hex_coord == star_global

# Could be:
def affects_hex(self, hex_coord) -> bool:
    star_global = sys_loc + star_loc
    if hex_coord == star_global:
        return True
    # System-scope abilities affect every hex in the system.
    abilities = getattr(self.star, 'intrinsic_abilities', None) or {}
    for entry in abilities.values():
        entries = entry if isinstance(entry, list) else [entry]
        if any(e.get('scope') in {'system', 'allied_system', 'player_system', 'enemy_system'}
               for e in entries if isinstance(e, dict)):
            return True
    return False
```

This preserves identical behaviour:
- Star at hex H queried for hex H: yields (sector + system scopes)
- Star at hex S queried for hex H (H ≠ S) with system-scope abilities: yields
- Star at hex S queried for hex H (H ≠ S) without system-scope abilities: skipped

After this change, `_star_provider` collapses to:
```python
def _star_provider(system, hex_coord, registries):
    return _iter_hex_filtered_sources(
        system, hex_coord, 'stars',
        lambda star, sys: StarAbilitySource(star=star, system=sys),
        item_filter=lambda star: bool(getattr(star, 'intrinsic_abilities', None)),
    )
```

**Verdict: Over-conservative exclusion.** The star provider CAN be consolidated
with a small adapter-level change. This is a MAJOR finding — the narrowing
should have been 7 → 4, not 7 → 3.

Severity: **MAJOR**.

---

### FND-042 — `_facility_provider` correctly excluded (nested iteration)

**Provider:** `ability_iterator.py:170`

Iteration shape:
1. Walk `system.planets` (outer loop)
2. For each planet, compute global hex for positional filter
3. Walk `planet.facilities` (inner loop — nested)
4. Filter by `facility.is_operational`
5. Construct `FacilityAbilitySource(facility=..., planet=..., registries=...)`

Three incompatibilities with `_iter_hex_filtered_sources`:
- **Nested iteration:** The helper does single-level `getattr(system, container_attr)`. There is no `system.facilities` attribute — facilities live under `planet.facilities`.
- **3-arg adapter constructor:** The helper calls `adapter_factory(item, system)` with 2 args. `FacilityAbilitySource` requires `facility`, `planet`, and `registries`.
- **Hex filtering at planet level:** The hex filter operates on the planet's global position (`_planet_global_hex`), not on the facility adapter.

**Verdict: Correctly excluded.** The nested iteration shape is genuinely
different. A different helper (e.g. `_iter_nested_filtered_sources`) could
consolidate this pattern, but that is a separate abstraction, not
`_iter_hex_filtered_sources`.

Severity: INFO.

---

### FND-043 — `_fleet_provider` correctly excluded (lookup callback pattern)

**Provider:** `ability_iterator.py:297`

Iteration shape:
1. Select lookup callback: `_FLEETS_AT_HEX_LOOKUP` or `_FLEETS_IN_SYSTEM_LOOKUP`
2. Call lookup to get fleet list
3. Construct `FleetAbilitySource(fleet=fleet, registries=registries)`
4. Filter by `adapter.get_abilities()` (post-construction, not pre-construction)

Incompatibilities:
- **Data source is not `system.<attr>`:** Fleets come from lookup callbacks set via `set_fleet_lookups()` (`ability_iterator.py:284`), not from an attribute on the system object.
- **Post-construction filter:** The `item_filter` in the helper runs on raw items BEFORE adapter construction. The fleet filter (`adapter.get_abilities()`) runs AFTER construction.
- **3-arg adapter constructor:** `FleetAbilitySource` takes `registries` as a constructor argument.

**Verdict: Correctly excluded.** The lookup-callback data source and
post-construction filtering pattern are genuinely different.

Severity: INFO.

---

### FND-044 — `_system_archetype_provider` correctly excluded (0-or-1 yield)

**Provider:** `ability_iterator.py:315`

Iteration shape:
1. Guard: `system is None`, `system.archetype` falsy, or `system.intrinsic_abilities` falsy → return
2. Yield single `SystemAbilitySource(system=system)`

There is no iteration — this is a conditional yield of at most 1 source. The
`_iter_hex_filtered_sources` helper iterates a list. Forcing this into the
helper would require a synthetic list and gain nothing (the provider is already
only 8 lines).

**Verdict: Correctly excluded.** This is a guard-then-yield pattern, not an
iteration pattern. It is already minimal and does not benefit from the helper.

Severity: INFO.

---

### FND-045 — `_iter_hex_filtered_sources` helper correctly implemented

**Helper:** `ability_iterator.py:121–167`

The helper's 5-step pattern:
1. `system is None` short-circuit → return
2. Walk `getattr(system, container_attr, None) or []`
3. Drop items failing `item_filter(item)` (default `bool`)
4. Build adapter via `adapter_factory(item, system)`
5. Yield if `hex_coord is None` or `adapter.affects_hex(hex_coord)`

Verification for the 3 consolidated providers:

| Step | `_storm_provider` | `_planet_intrinsic_provider` | `_warp_point_provider` |
|------|-------------------|------------------------------|------------------------|
| Step 1 | ✓ stubbed as `hex_coord` param ignored | ✓ | ✓ |
| Step 2 | `system.storms` | `system.planets` | `system.warp_points` |
| Step 3 | `lambda _: True` | `bool(planet.intrinsic_abilities)` | `bool(wp.intrinsic_abilities)` |
| Step 4 | `StormAbilitySource(storm, system)` | `PlanetIntrinsicAbilitySource(planet, system)` | `WarpPointAbilitySource(wp, system)` |
| Step 5 | `adapter.affects_hex(hex_coord)` | `adapter.affects_hex(hex_coord)` | `adapter.affects_hex(hex_coord)` |

All three `affects_hex` implementations correctly translate local entity
coordinates to global galaxy-map frame via `system.global_location`:
- `StormAbilitySource.affects_hex` — `storm.py:44` — iterates `storm.hex_offsets`
- `PlanetIntrinsicAbilitySource.affects_hex` — `planet_intrinsic.py:52` — handles multi-hex bodies
- `WarpPointAbilitySource.affects_hex` — `warp_point.py:45` — single-hex match

**Verdict: Correctly implemented.** The helper works correctly for all 3
consolidated providers in both hex and system-wide query modes.

Severity: INFO.

---

## Consolidation Scorecard

| Provider | Consolidatable? | Agent's Call | Verdict |
|----------|----------------|--------------|---------|
| `_storm_provider` | Yes | Yes | Correct |
| `_planet_intrinsic_provider` | Yes | Yes | Correct |
| `_warp_point_provider` | Yes | Yes | Correct |
| `_star_provider` | **Yes** (with minor adapter change) | **No** | **Over-conservative** |
| `_facility_provider` | No (nested iteration) | No | Correct |
| `_system_archetype_provider` | No (0-or-1 yield) | No | Correct |
| `_fleet_provider` | No (lookup callbacks) | No | Correct |

**Correctly identified:** 6/7
**Over-conservative exclusions:** 1 (`_star_provider`)
**Incorrectly included:** 0

---

## Recommendation

Change `StarAbilitySource.affects_hex` to return `True` when the star carries
system-scope intrinsic abilities, then consolidate `_star_provider` to use
`_iter_hex_filtered_sources`. This moves the scope-aware fallback from the
provider into the adapter, where it belongs semantically (the adapter answers
"does this source affect this hex?" — system-scope abilities affect every
hex, so the answer should be yes).

After this consolidation, the provider count drops from 4 custom bodies to
3 custom bodies (facility, fleet, system_archetype), with 4 providers using
the shared helper (storm, planet_intrinsic, warp_point, star).

Estimated savings: ~24 lines of provider code removed (the star provider body
shrinks from ~26 lines to 5-line delegation to the helper), offset by ~18
lines added to `StarAbilitySource.affects_hex`. Net: ~6 lines saved; primary
benefit is maintainability — one less provider that reimplements the
system-short-circuit + list-walk + adapter-construct pattern.

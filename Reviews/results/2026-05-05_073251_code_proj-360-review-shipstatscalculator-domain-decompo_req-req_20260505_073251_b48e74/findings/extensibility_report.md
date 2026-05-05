# PROJ-360 ShipStatsCalculator Domain Decomposition — Extensibility & API Review

**Reviewer:** OpenCode (Extensibility/API Review Agent)  
**Date:** 2026-05-05  
**Scope:** `game/simulation/entities/stat_contributors/`, `game/simulation/entities/ship_stats.py`

---

## Findings Summary

| Severity | Count |
|----------|-------|
| CRIT     | 2     |
| MAJ      | 4     |
| MIN      | 5     |
| NIT      | 3     |
| **Total**| **14** |

---

## 1. STAT_CONTRIBUTOR_REGISTRY Extension Surface

### [EXT-01]: [CRIT] Same ability in multiple domains causes silent double-counting at runtime

**File:** `game/simulation/entities/stat_contributors/registry.py:181-193`  
**Description:** `register_stat_contributor` deduplicates on the `(ability_name, domain)` pair, allowing the same ability to be registered in arbitrarily many domains. The dedup guard is per-domain, not per-ability. `apply_registered_contributors` unconditionally invokes *every* registered contributor whose ability name matches, with no dedup across domains. A mod registering `ShieldProjection` in domains `["a", "b", "c"]` gets three invocations of three different contributor functions for every shield component — the `domain` field is never consumed by the calculator to limit execution count.

The test `test_same_ability_different_domain_is_allowed` (`test_registry.py:121-130`) codifies this as intended behavior, but the test only validates registration, not runtime application. The acceptance test only registers one entry, so double-counting is never observed.

**Remediation:** Either (a) make dedup guard per-ability (unique by `ability_name` alone), or (b) make `domain` participate in runtime gating (e.g. `apply_registered_contributors` skips entries if another entry with the same ability already matched). Option (a) is simplest and matches the stated goal of "adding a new stat-affecting ability is registering it."

### [EXT-02]: [MAJ] Built-in contributors and registered contributors both process the same ability with no mutual exclusion

**File:** `game/simulation/entities/ship_stats.py:258-267`  
**Description:** The built-in defense contributor processes `ShieldProjection` by iterating `get_abilities("ShieldProjection")` and accumulating `acc["max_shields"] += ab.capacity` (defense.py:45-46). In the same loop, `apply_registered_contributors` runs for every registered entry whose ability gate matches. A user registering a `ShieldProjection` contributor would have BOTH the built-in and the registered contributor fire, double-counting shield capacity.

The acceptance test (`test_stat_contributor_extension.py:110-150`) registers its fake contributor against `ShieldProjection` — but the fake contributor writes a custom attribute (`fake_contributor_calls`), not a ship stat like `max_shields`. The test never asserts that real stats aren't corrupted.

The doc header in `registry.py` acknowledges this: "intentionally separate from the existing `game.simulation.combat.ability_stat_registry.ABILITY_STAT_REGISTRY`" but only refers to the modifier-emission pipeline. It does not warn that the stat-contributor registry runs *alongside* (not instead of) built-in contributors for the same abilities.

**Remediation:** Add an explicit rule: a registered contributor overrides (suppresses) the built-in handling for the same ability, OR document the double-fire risk and add a runtime check in `apply_registered_contributors` that skips registered contributors for abilities already handled by built-in domains. The former is more extensible.

### [EXT-03]: [MIN] `apply_registered_contributors` performs unbounded linear scan per component

**File:** `game/simulation/entities/stat_contributors/registry.py:181-193`  
**Description:** For each operational component, `apply_registered_contributors` iterates over *every* entry in `STAT_CONTRIBUTOR_REGISTRY`, calling `has_ability()` on each. With N components and M registered entries, this is O(N × M). Each `has_ability()` is an O(1) dict lookup, so the per-component cost is trivial for typical M (1–20 entries). However, the scan is unbounded — a mod adding 500 registered contributors would pay 500 `has_ability` checks per component with no shortcut. Contrast this with the built-in contributors, which are called unconditionally (O(1) dispatch per domain).

**Remediation:** Build a reverse index mapping `ability_name → [contributor_fn list]` on registration, so `apply_registered_contributors` only iterates the subset of entries actually relevant to the component's abilities. Not urgent given typical registry sizes.

### [EXT-04]: [NIT] `domain` field semantics are split between documentation and actual usage

**File:** `game/simulation/entities/stat_contributors/registry.py:137-138`  
**Description:** The docstring says `domain` is a "human-readable tag for diagnostics; not consumed by the calculator." In reality, `domain` IS consumed — it's part of the dedup key in `register_stat_contributor` and the filter key in `unregister_stat_contributor`. It's not purely diagnostic; it controls registration logic. A user relying on the docstring might change the domain freely, only to discover it affects dedup behavior.

**Remediation:** Correct the docstring to say "used for dedup grouping; not consumed by the calculator's aggregation phase."

---

## 2. `get_abilities('X')` and `comp.abilities.get('X')` Call Audit

### Complete Inventory

All calls across contributor modules and `ship_stats.py`:

| # | File | Line | Call | Attribute(s) Accessed | Typed Read? | Dispatch Check? |
|---|------|------|------|-----------------------|-------------|-----------------|
| 1 | `movement.py` | 39 | `comp.get_abilities("CombatPropulsion")` | `.thrust_force` | Yes (numeric) | No |
| 2 | `movement.py` | 43 | `comp.get_abilities("StrategicMovement")` | `.movement_points` | Yes (numeric) | No |
| 3 | `movement.py` | 47 | `comp.get_abilities("WarpJump")` | `.max_tonnage`, `.energy_cost` | Yes (numeric) | `is_warp_jump(ab)` structural typeguard at line 48 |
| 4 | `movement.py` | 55 | `comp.get_abilities("ManeuveringThruster")` | `.turn_rate` | Yes (numeric) | No |
| 5 | `defense.py` | 45 | `comp.get_abilities("ShieldProjection")` | `.capacity` | Yes (numeric) | No |
| 6 | `defense.py` | 49 | `comp.get_abilities("ShieldRegeneration")` | `.rate` | Yes (numeric) | No |
| 7 | `command.py` | 92 | `comp.get_abilities("CrewRequired")` | `.amount` | Yes (numeric) | No |
| 8 | `ship_stats.py` | 213 | `comp.get_abilities("CrewCapacity")` | `.amount` | Yes (numeric) | No |
| 9 | `ship_stats.py` | 215 | `comp.get_abilities("LifeSupportCapacity")` | `.amount` | Yes (numeric) | No |
| 10 | `ship_stats.py` | 303 | `comp.get_abilities("CargoStorage")` | `.cargo_type`, `.capacity` | Yes (typed) | No |

**Raw `comp.abilities.get()` calls (bypass typed system):**

| # | File | Line | Call | Reason |
|---|------|------|------|--------|
| 11 | `defense.py` | 40 | `comp.abilities.get("Armor", False)` | Marker ability (no typed class) |
| 12 | `ship_stats.py` | 201 | `comp.abilities.get("Armor", False)` | Marker ability (no typed class) |
| 13 | `ship_stats.py` | 207 | `comp.abilities.get("Armor", False)` | Marker ability (no typed class) |
| 14 | `command.py` | 49 | `comp.abilities.get("MultiplexTracking", 0)` | No typed ability class |
| 15 | `launch.py` | 35 | `comp.abilities.get("VehicleLaunch", {})` | No typed ability class (see PROJ-360 doc comment) |
| 16 | `launch.py` | 36 | `comp.abilities.get("VehicleStorage", 0)` | No typed ability class |
| 17 | `ship_stats.py` | 312 | `comp.abilities.get("PodStorage")` | No typed ability class |

**Dispatch-like check (protocol rather than `isinstance`):**

| # | File | Line | Call | Description |
|---|------|------|------|-------------|
| 18 | `defense.py` | 53-57 | `comp.has_ability("ShieldRegeneration")` + iterate `comp.ability_instances` + `is_resource_consumption(ab)` per instance | Iterates ALL ability instances on a shield-regen component looking for `ResourceConsumption` with `resource_type == "energy"`. Uses a structural protocol guard (`is_resource_consumption`), not `isinstance`. This is a mixed scan: `has_ability` gates by ability name, then a full linear sweep of *all* ability instances filters by resource type. |

### [EXT-05]: [MAJ] Shield energy cost extraction uses a full-scan of all ability instances after a valid gate

**File:** `game/simulation/entities/stat_contributors/defense.py:53-57`  
**Description:** After confirming `comp.has_ability("ShieldRegeneration")`, the code iterates `comp.ability_instances` — the **entire** ability list — searching for a `ResourceConsumption` ability with `resource_type == "energy"`. This conflates two concerns: the gate (`has_ability` by ability name) and the dispatch (filter by resource type across all instances). If a component has 20 ability instances but only one `ResourceConsumption(energy)`, this still scans all 20. The `break` on line 57 limits the damage but the scan is unbounded per component-and-ability-type.

The correct pattern (used by other contributors) would be: iterate `comp.get_abilities("ResourceConsumption")` and filter by `ab.resource_type == "energy"`. This avoids the O(all-instances) scan for a property only relevant to one ability type.

**Remediation:** Replace the `ability_instances` loop + `is_resource_consumption` check with `comp.get_abilities("ResourceConsumption")` followed by a filter on `.resource_type`.

### [EXT-06]: [MIN] `is_warp_jump()` structural guard may mask an ability indexing gap

**File:** `game/simulation/entities/stat_contributors/movement.py:47-48`  
**Description:** `comp.get_abilities("WarpJump")` returns ability objects via the pre-built MRO index. The returned abilities should always be `WarpJump` or its subclasses. Yet the code wraps the attribute accesses with `if is_warp_jump(ab):`, a structural typeguard that checks for `.max_tonnage` and `.energy_cost` attribute presence. If the index is correct, this guard is always satisfied and is dead logic. If the index can return non-warp abilities (e.g. due to polymorphic storage or reindex bugs), the guard silently swallows the error (no warning, no log). Either way, the guard is superfluous or masking a deeper issue.

**Remediation:** Remove the guard and assert that returned abilities have the expected attributes, OR add a warning log when the guard fires so indexing regressions are detectable.

### [EXT-07]: [MAJ] Five ability types bypass the typed system entirely via raw dict access

**File:** `launch.py:35-36`, `command.py:49`, `defense.py:40`, `ship_stats.py:201,207,312`  
**Description:** `Armor`, `MultiplexTracking`, `VehicleLaunch`, `VehicleStorage`, and `PodStorage` are all accessed via `comp.abilities.get(key)` rather than `get_abilities(key)`. `Armor` is a marker ability (acceptable — `has_ability` is also available at defense.py:40). The rest are ability types that carry numeric values but lack typed ability classes, so they cannot be registered via `STAT_CONTRIBUTOR_REGISTRY.register_stat_contributor` (the registry gating uses `has_ability`, which works, but the contributor function would receive the component with no typed attribute to read — it would need to fall back to `comp.abilities.get()` itself).

This creates two extension tiers: abilities with typed classes (extensible via registry) and abilities without (must copy the raw dict access pattern from the built-in contributor).

**Remediation:** Give `MultiplexTracking`, `VehicleLaunch`, `VehicleStorage`, and `PodStorage` typed ability classes (even lightweight ones with the single relevant attribute). This unifies the extension surface and eliminates the raw dict bypass.

### [EXT-08]: [NIT] All ability name strings are hardcoded literals with no centralized constant

**File:** All contributor files, `ship_stats.py`  
**Description:** Ability names like `"CombatPropulsion"`, `"ShieldProjection"`, `"CrewRequired"`, etc. appear as string literals in 10+ locations across 5 files. Renaming an ability (or typo-fixing) requires find-and-replace across all contributor modules, `ship_stats.py`, the registry defaults, and the combat endurance module.

**Remediation:** Centralize ability name constants (e.g. in `game/core/constants.py` or a dedicated `ability_names.py`). This is a non-breaking refactor since the strings themselves don't change.

---

## 3. Crew Priority Registry

### [EXT-09]: [MIN] `lookup_crew_priority` is O(n) in registry size with no index

**File:** `game/simulation/entities/stat_contributors/registry.py:101-113`  
**Description:** Every call to `lookup_crew_priority` iterates the full `CREW_PRIORITY_REGISTRY` list sequentially. The early exit at `priority == 0` (line 111) helps but does not change worst-case complexity. For a call frequency of once per component per recalculation (N components → N scans of M registry entries = O(N × M)), this is linear in both axes. With 4 built-in entries and dozens of registered entries, this is negligible. But `CREW_PRIORITY_REGISTRY` is a flat list — it could easily become 50+ entries in a heavily modded game, and `lookup_crew_priority` is called for `component_pool.sort(key=priority_sort_key)` which invokes it O(N log N) times (once per comparison in Python's Timsort).

**Remediation:** Build a `dict` index mapping `ability_name → priority` on registration, and consult the dict in `lookup_crew_priority`. The current list-based registry can remain as the source of truth; the dict is a derived cache.

### [EXT-10]: [MIN] `register_crew_priority` duplicates check by linear scan — consistent with `register_stat_contributor`, but both could use an index

**File:** `game/simulation/entities/stat_contributors/registry.py:79-86`  
**Description:** Both `register_crew_priority` and `register_stat_contributor` do O(n) duplicate checks by iterating the full list. This is consistent across both registries but means adding the 100th entry scans 99 existing entries. Acceptable for infrequent registration (startup-time only), but inconsistent with the module's stated goal of being a registry (registries typically provide O(1) dedup via internal indices).

**Remediation:** If registration happens only at startup, the O(n) scan is fine. Add a doc comment noting the assumption. If runtime registration (mod enable/disable) is expected, switch to `dict`-backed dedup.

---

## 4. Built-in vs. Registry Contributors

### [EXT-11]: [MAJ] Extension boundary is inconsistent: built-in domains require code edits to add new ability handling

**File:** `game/simulation/entities/ship_stats.py:258-266`  
**Description:** The `stat_contributors/registry.py` header states: "Adding a new stat-affecting ability now means *registering* it; no edits to `ship_stats.py` or the contributor modules are required for the extension points covered here." But only *new* abilities can be added via the registry. If a new ability needs to contribute to `thrust`, `max_shields`, `fighter_capacity`, or any other stat owned by the built-in domains, the developer must edit the corresponding built-in contributor module — or register a separate contributor that writes the same stat to `ship` (which then collides with [EXT-02]).

The built-in contributors are hardcoded in `_phase_stats_aggregation` and there is no `register_domain_contributor(domain, fn)` API. All five domains are fixed at code level.

**Remediation:** Register the built-in contributors through the same `STAT_CONTRIBUTOR_REGISTRY` as default entries, or add a secondary registry that allows replacing/overriding a built-in domain's aggregation function. The former is cleaner and validates that the registry is truly universal.

---

## 5. Accumulator Dictionary Pattern

### [EXT-12]: [CRIT] Registered contributors mutate `ship` directly while built-in contributors mutate `acc` dict — inconsistent mutation surface with no guardrails

**File:** `game/simulation/entities/ship_stats.py:258-267` (call site), `registry.py:191-193` (invocation)  
**Description:** Built-in contributors receive and mutate a shared `acc: Dict[str, Any]` dict. Registered contributors receive `(ship, comp)` and mutate `ship` directly. Both run in the same phase, for the same components. A registered contributor that accidentally writes to a key that `_apply_aggregated_stats` reads from `acc` (e.g. writing `ship.max_shields` during the aggregation loop) would be overwritten by `_apply_aggregated_stats` later, or worse, would interact with the built-in contributor's partial accumulation state.

The registered contributor contract gives access to the full `Ship` object, which includes `ship.resources`, `ship.layers`, `ship.max_speed`, `ship.turn_speed` — all mutable. A registered contributor is given the power to corrupt any ship stat, including stats that haven't been computed yet (they run in Phase 3, before Phase 4 physics and Phase 5 sensor scores).

The test `test_fake_contributor_runs_for_a_ship_with_matching_ability` only stamps a non-existent attribute (`fake_contributor_calls`) — it never tests that real ship stats survive the contributor call.

**Remediation:** (a) Pass `acc` to registered contributors so they can participate in the accumulated-then-committed pattern, or (b) document that registered contributors are responsible for their own stat domain and must not mutate `acc`-owned stats. Option (a) is safer and consistent with the built-in pattern.

### [EXT-13]: [MIN] `acc` dict has no key validation — a misspelled key silently produces zero output

**File:** `game/simulation/entities/ship_stats.py:236-243` (initialization), `_apply_aggregated_stats:318-355` (consumption)  
**Description:** The `acc` dict keys are string literals duplicated across three locations: `_phase_stats_aggregation` initialization, the built-in contributor writes (movement.py, defense.py), and `_apply_aggregated_stats` consumption. If a key is misspelled in any of these locations, the corresponding stat silently becomes 0 with no error. For example, writing `acc["shield_regen"]` (defense.py:50) but reading `acc["shield_regen_rate"]` (ship_stats.py:349) would silently discard shield regen data. Currently all keys are consistent, but there's no compile-time or runtime guard.

**Remediation:** Use `TypedDict` or a dataclass for the accumulator. At minimum, define key constants in a shared location so misspellings become `NameError` at import time.

---

## 6. Public API Documentation

### [EXT-14]: [NIT] "Not a stable API" disclaimer is ambiguous given the registry IS the public extension API

**File:** `game/simulation/entities/stat_contributors/__init__.py:13-15`  
**Description:** The disclaimer says "These modules are an internal decomposition; they are not a stable API." This applies correctly to the domain-specific modules (`movement.py`, `defense.py`, etc.) which are implementation details of `ShipStatsCalculator`. However, `registry.py` in the same package IS the public extension API — it has `register_stat_contributor`, `register_crew_priority`, and their unregister counterparts, all documented as extension points. The blanket "not a stable API" statement contradicts the registry's purpose and may discourage modders from using it.

**Remediation:** Split the disclaimer: "The domain modules (`movement`, `defense`, `weapons`, `command`, `launch`) are internal and not a stable API. The `registry` module IS the supported extension surface — use `register_stat_contributor` and `register_crew_priority` to extend ship-stat calculation."

---

## Cross-Cutting Observation

The PROJ-360 decomposition successfully isolated stat-domain logic into separate modules, but the extension story is incomplete. The registry mechanism is structurally sound (it works end-to-end as the acceptance test proves), but it lives alongside — not in place of — the built-in pipeline. This creates a two-tier system where:
- **Tier 1:** Built-in domains with hardcoded `get_abilities()` loops, `acc` dict accumulation, and guaranteed phase ordering. Requires code edits to extend.
- **Tier 2:** Registry contributors with `has_ability()` gating, direct `ship` mutation, and no phase-ordering guarantees. Extensible without code edits.

A registered contributor for an ability already handled by Tier 1 will double-fire. A registered contributor for a new ability must either mutate `ship` directly (risking overwrite by later phases) or be limited to stats that are read-only after Phase 3 (which is poorly documented). The acceptance test papercuts past this by only testing a non-stat-modifying contributor against an existing ability — it tests "does the hook fire?" not "does the hook fire correctly in a real scenario?"

---

## Finding Counts

| Severity | Count | IDs |
|----------|-------|-----|
| CRIT     | 2     | EXT-01, EXT-12 |
| MAJ      | 4     | EXT-02, EXT-05, EXT-07, EXT-11 |
| MIN      | 5     | EXT-03, EXT-06, EXT-09, EXT-10, EXT-13 |
| NIT      | 3     | EXT-04, EXT-08, EXT-14 |
| **Total**| **14** | |

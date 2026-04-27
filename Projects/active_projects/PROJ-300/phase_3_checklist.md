# Phase 3: `IAbilitySource` protocol + Facility/Storm adapters + iterator

**Status:** Not Started
**Objective:** Define the universal `IAbilitySource` protocol; build the two adapter classes that wrap existing entities; build the unified iterator that future projects extend. No behavior change yet — the collector still uses its current planet-walking path.

---

## Tasks

### Task 3.1: Define `IAbilitySource` protocol [Simple]
**File:** `game/core/protocols.py`
**Tests:** `pytest tests/unit/core/test_protocols.py`

- [ ] Read `game/core/protocols.py` to find the existing `IFleet`, `IPlanet`, `IStorm` definitions and their TypeGuard companions.
- [ ] Add `IAbilitySource` `@runtime_checkable` Protocol immediately after `IStorm`:
  ```python
  @runtime_checkable
  class IAbilitySource(Protocol):
      @property
      def source_kind(self) -> str: ...
      @property
      def source_label(self) -> str: ...
      @property
      def source_id(self) -> str: ...
      @property
      def owner_id(self) -> Optional[int]: ...
      def get_abilities(self) -> Dict[str, Any]: ...
      def affects_hex(self, hex_coord) -> bool: ...
      def affects_system(self, system) -> bool: ...
      def get_activation_state(self, ability_name: str) -> Optional[Any]: ...
  ```
- [ ] Add a TypeGuard `is_ability_source(obj)` checking `_has_attrs(obj, 'source_kind', 'source_label', 'get_abilities', 'affects_hex')`.
- [ ] Add tests confirming a duck-typed dict-with-the-right-attributes passes `isinstance(_, IAbilitySource)` and `is_ability_source(_)`.

**Notes:**

### Task 3.2: Create the adapter package [Simple]
**File:** `game/strategy/services/ability_sources/__init__.py` (NEW)

- [ ] Create the directory `game/strategy/services/ability_sources/`.
- [ ] Create `__init__.py` with re-exports:
  ```python
  from .facility import FacilityAbilitySource
  from .storm import StormAbilitySource

  __all__ = ['FacilityAbilitySource', 'StormAbilitySource']
  ```

**Notes:**

### Task 3.3: Implement `FacilityAbilitySource` [Medium]
**File:** `game/strategy/services/ability_sources/facility.py` (NEW)
**Tests:** `tests/unit/strategy/services/ability_sources/test_facility.py` (NEW)

- [ ] Write failing tests first:
  - [ ] `test_source_kind_is_facility`
  - [ ] `test_source_label_format` — e.g. `"Geologic Stabilizer (Tarsis IV)"` from facility.name + planet.name.
  - [ ] `test_source_id_stable` — same facility yields same id across calls.
  - [ ] `test_owner_id_from_planet`
  - [ ] `test_get_abilities_returns_aggregated_component_abilities` — walks all components on operational facility, merges their `abilities` blocks.
  - [ ] `test_get_abilities_skips_non_operational` — when `facility.is_operational=False`, returns `{}`.
  - [ ] `test_affects_hex_matches_planet_global_location`
  - [ ] `test_affects_system_matches_planet_system`
  - [ ] `test_get_activation_state_returns_facility_state_for_ability`
- [ ] Implement `FacilityAbilitySource(facility, planet, registries)` dataclass.
  - Reuse `iter_keyed_components` from `game/core/patterns/layer_iterator.py` and `extract_abilities_from_component` from `game/strategy/services/component_inspector.py` to build the merged abilities dict.
  - `get_activation_state(ability_name)` looks up the facility's component-state for the component owning that ability via `facility.get_activation_state(comp_key)`.
- [ ] Run tests — confirm green.

**Notes:** A facility with multiple components owning the same `ability_name` would collide on a flat dict. Existing collector handles this by emitting one effect per (component, ability) — for the adapter, return `Dict[str, List[Any]]` for those collisions (or always return list-valued and let the collector flatten). Pick the cleaner shape and document in decisions.md.

### Task 3.4: Implement `StormAbilitySource` [Simple]
**File:** `game/strategy/services/ability_sources/storm.py` (NEW)
**Tests:** `tests/unit/strategy/services/ability_sources/test_storm.py` (NEW)

- [ ] Write failing tests first:
  - [ ] `test_source_kind_is_storm`
  - [ ] `test_source_label_is_storm_name`
  - [ ] `test_source_id_stable`
  - [ ] `test_owner_id_is_none`
  - [ ] `test_get_abilities_returns_storm_abilities_dict` — uses Storm.abilities (note: this depends on Phase 5 dataclass change; until Phase 5 lands, this test reads `Storm.effects` and translates — see Phase 5 for the cleanup).
  - [ ] `test_affects_hex_true_for_occupied_hexes`
  - [ ] `test_affects_hex_false_outside_storm`
  - [ ] `test_affects_system_true_only_if_storm_in_system`
  - [ ] `test_get_activation_state_returns_none`
- [ ] Implement the dataclass.
- [ ] **Sequencing:** This task creates the adapter against the *current* `Storm.effects` shape if Phase 5 hasn't landed yet. Phase 5 will then update the adapter to read `Storm.abilities` directly. Mark in decisions.md if any temporary translation lives here briefly.

**Notes:**

### Task 3.5: Implement `iter_ability_sources_at_hex` and `iter_ability_sources_in_system` [Medium]
**File:** `game/strategy/services/ability_iterator.py` (NEW)
**Tests:** `tests/unit/strategy/services/test_ability_iterator.py` (NEW)

- [ ] Failing tests first:
  - [ ] `test_iter_at_hex_yields_facility_for_planet_at_hex`
  - [ ] `test_iter_at_hex_yields_storm_for_storm_at_hex`
  - [ ] `test_iter_at_hex_excludes_facility_for_distant_planet`
  - [ ] `test_iter_at_hex_includes_system_facilities_when_include_system_sources_true`
  - [ ] `test_iter_in_system_yields_all_facilities`
- [ ] Implement using a private `_SOURCE_PROVIDERS` list of `Callable[[StarSystem, HexCoord], Iterable[IAbilitySource]]`. Initial registrations:
  - `_planet_facility_provider` — walks `system.planets`, yields one `FacilityAbilitySource` per (operational facility, planet).
  - `_storm_provider` — walks `galaxy.get_zones_at_global_hex(hex_coord)` filtered to `Storm`, yields `StormAbilitySource`.
- [ ] Provide `register_source_provider(fn)` / `unregister_source_provider(fn)` so PROJ-301..305 can register their adapters.
- [ ] `iter_ability_sources_at_hex(system, hex_coord)` calls each provider and yields. Filter the *facility* provider's output by `affects_hex(hex_coord)` to scope to the queried hex.
- [ ] Run tests — green.

**Notes:** This file is the integration seam for PROJ-301..305. Document the registration API clearly so future projects don't have to guess.

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] New test files have ≥ the listed cases, all green
- [ ] `pytest tests/ --testmon` — no regressions
- [ ] Update status to `Complete`
- [ ] Update plan.md

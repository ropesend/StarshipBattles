# Phase 2: Built-in Phase-3 contributors as registry entries (collapse two-tier model)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-367 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Register the four **Phase-3** built-in domain contributors (`aggregate_propulsion`, `aggregate_defense`, `aggregate_hangar`, `track_multiplex`) split into per-ability `contribute_*` functions, as default `STAT_CONTRIBUTOR_REGISTRY` entries at module import. `_phase_stats_aggregation` becomes a single registry iteration. **Phase 5 helpers (`weapons.py:aggregate_targeting_scores`, `defense.py:apply_armor_and_repair_scores`, `defense.py:init_armor_pool`) untouched.** Add `RegistrationConflictPolicy`, `RegistrationHandle`, `phase_order`. Retire `BUILTIN_HANDLED_ABILITIES`. Replacement is implicit on conflict (replacement entries inherit modder default `phase_order=99`). Golden snapshot bit-identical.

---

## Pre-flight

- [ ] Phase 1 complete and committed
- [ ] Sharded suite green at end of Phase 1
- [ ] Capture today's call order in a golden test (Task 2.1) so the per-ability seeding can be verified to fire in the same order

---

## Tasks

### Task 2.1: Pin today's Phase-3 call order via a sequence test (TDD-first) [Medium]
**File:** `tests/unit/simulation/entities/stat_contributors/test_registry_pipeline.py` (new)
**Tests:** `pytest tests/unit/simulation/entities/stat_contributors/test_registry_pipeline.py::test_phase3_call_order -v`

- [ ] Write a test that monkeypatches each Phase-3 domain function (`movement.aggregate_propulsion`, `defense.aggregate_defense`, `launch.aggregate_hangar`, `command.track_multiplex`) and `apply_registered_contributors` with a recorder that appends its name to a list
- [ ] Recalculate stats on a representative ship; assert the recorded order matches the current hardcoded order in `_phase_stats_aggregation` at `ship_stats.py:258-269`
- [ ] **Phase 5 functions (`weapons.aggregate_targeting_scores`, `defense.apply_armor_and_repair_scores`, `defense.init_armor_pool`) are NOT in this test** — they're out-of-scope.
- [ ] **Verify:** test passes on current code

**Notes:** This test will need to evolve in Task 2.5 to monkeypatch per-ability `contribute_X` functions instead of domain functions. Keep both phases of the test until Phase 2 lands.

### Task 2.2: Add `RegistrationConflictPolicy`, `RegistrationHandle`, `phase_order` [Medium]
**File:** `game/simulation/entities/stat_contributors/registry.py`
**Tests:** `pytest tests/unit/simulation/entities/stat_contributors/test_registry_pipeline.py -v`

- [ ] Add enum `RegistrationConflictPolicy(Enum)` with values `REPLACE_WARN`, `REPLACE_SILENT`, `APPEND`, `ERROR`
- [ ] Add `@dataclass(frozen=True) class RegistrationHandle: ability_name: str; entry_id: int`
- [ ] Add monotonic `entry_id` counter (module-level or registry-state)
- [ ] Add exception `class CannotUnregisterDefaultError(Exception)`
- [ ] Extend `StatContributorEntry` with `phase_order: int = 99` and `is_default: bool = False`
- [ ] Extend `register_stat_contributor(...)` signature with `*, policy: RegistrationConflictPolicy = REPLACE_WARN, phase_order: int = 99, default: bool = False` (kwargs-only)
- [ ] Return `RegistrationHandle` from `register_stat_contributor`
- [ ] When `default=True`, set `phase_order` from a domain → order map (movement=10, defense=20, hangar=40, command=50)
- [ ] Behavior:
  - `REPLACE_WARN`: log a warning via `logging.getLogger(__name__).warning(...)`, replace
  - `REPLACE_SILENT`: replace, no log
  - `APPEND`: store as a tuple of contributors, dispatched in registration order
  - `ERROR`: raise `RegistrationConflictError` on conflict
- [ ] Add `iter_for(comp)` helper that yields entries in `phase_order` for abilities `comp.has_ability(...)` is true on
- [ ] Change `unregister_stat_contributor` to take a `RegistrationHandle` (not a string)
- [ ] On unregister of a `REPLACE_*` entry, restore the underlying default if any
- [ ] On unregister of a default entry by handle, raise `CannotUnregisterDefaultError`
- [ ] Add backward-compat shim `unregister_stat_contributor_by_name(ability_name)` that emits `DeprecationWarning` and removes ALL non-default entries for that name
- [ ] Unit tests for each policy + handle round-trip + shim deprecation
- [ ] **Verify:** new tests pass; existing tests untouched (if some test_registry.py tests fail, they migrate in Task 2.7a)

**Notes:**

### Task 2.3: Extract per-ability `contribute_*` functions in Phase-3 domain modules [Medium]
**Files:** `game/simulation/entities/stat_contributors/{movement,defense,launch,command}.py`
**Tests:** focused unit tests + golden snapshot

- [ ] In `movement.py`: split `aggregate_propulsion(comp, acc)` into per-ability functions covering `CombatPropulsion`, `ManeuveringThruster`, `WarpJump`, `StrategicMovement`. Each takes `(ship, comp, acc)`. Logic identical, just narrower scope.
- [ ] In `defense.py`: split `aggregate_defense(ship, comp, acc)` into per-ability functions. **Final list of contributor functions enumerated at Task 2.4.** Includes at least `ShieldProjection`, `ShieldRegeneration`, `Armor` (or its merged form), `EmissiveArmor`, `ShieldRegeneratingArmor`. The shield energy cost extraction (currently inline) becomes either part of `contribute_shield_regeneration` or a separate `contribute_shield_energy_cost` — **decide at Task 2.4.**
- [ ] In `launch.py`: split `aggregate_hangar(ship, comp)` into per-ability function(s) covering `VehicleLaunch`. Whether `VehicleStorage` becomes a separate default entry or remains gated under `VehicleLaunch` is **decided at Task 2.4.**
- [ ] In `command.py`: split `track_multiplex(ship, comp)` into a per-ability function covering `MultiplexTracking`.
- [ ] **DO NOT TOUCH `weapons.py`.** It is Phase 5; out-of-scope for PROJ-367.
- [ ] **DO NOT TOUCH `defense.py`'s `apply_armor_and_repair_scores` or `init_armor_pool`.** They are Phase 5; out-of-scope.
- [ ] Keep `aggregate_propulsion` / `aggregate_defense` / `aggregate_hangar` / `track_multiplex` as backward-compat wrappers that just call the per-ability functions in order — to be deleted in Task 2.6
- [ ] **Verify:** focused tests pass; golden snapshot bit-identical

**Notes:**

### Task 2.4: Seed default contributors at module import (and pin the final list) [Medium]
**File:** `game/simulation/entities/stat_contributors/__init__.py` (or new `_builtins.py`)
**Tests:** `pytest tests/unit/simulation/entities/stat_contributors/ -v`

- [ ] Add `_seed_builtin_contributors()` that registers every per-ability contributor from Task 2.3 with `default=True` and an explicit `phase_order` (movement=10, defense=20, hangar=40, command=50).
- [ ] **Decide and document:**
  - `Armor` handling — separate `contribute_armor` entry, or merged into another defense contributor?
  - `VehicleStorage` — separate default entry, or stays gated under `VehicleLaunch`?
  - Shield energy cost — part of `contribute_shield_regeneration` or separate `contribute_shield_energy_cost`?
- [ ] Each decision goes into `decisions.md` with a short rationale.
- [ ] Call `_seed_builtin_contributors()` once at module import (after the registry is constructed)
- [ ] **Add a registry-defaults regression test** that snapshots the full default-seeded entry set (ability_name + contributor + phase_order) and pins it. Future changes to the seed list MUST update this test deliberately.
- [ ] Update `reset_stat_contributor_registry()` to clear AND re-seed defaults (idempotent)
- [ ] Update root `conftest.py` if needed
- [ ] **Verify:** registry contains all default entries after a reset

**Notes:**

### Task 2.5: Replace `_phase_stats_aggregation` Phase-3 body with single registry iteration [Medium]
**File:** `game/simulation/entities/ship_stats.py`
**Tests:** golden snapshot + Task 2.1 sequence test (now updated for per-ability granularity)

- [ ] Replace the body of `_phase_stats_aggregation` (lines 258-269) with:
  ```python
  for layer in ship.layers.values():
      for comp in layer.components:
          if not comp.is_active:
              continue
          self._aggregate_resource_abilities(comp, acc)
          self._aggregate_cargo_and_pod_abilities(comp, acc)
          if not comp.is_operational:
              continue
          for entry in STAT_CONTRIBUTOR_REGISTRY.iter_for(comp):
              entry.contributor(ship, comp, acc)
  ```
- [ ] **DO NOT touch `_phase_post_physics_aggregation` or any Phase 5 code (lines 433-447).** Those stay imperative.
- [ ] Update Task 2.1's call-order assertion to check the per-ability function order
- [ ] **Verify:** golden snapshot bit-identical; Task 2.1's evolved test passes

**Notes:**

### Task 2.6: Retire deprecated symbols [Simple]
**File:** `game/simulation/entities/stat_contributors/registry.py`, `{movement,defense,launch,command}.py`
**Tests:** AST regression check

- [ ] Delete the `BUILTIN_HANDLED_ABILITIES` frozenset
- [ ] Delete `is_builtin_suppressed_for()` helper
- [ ] Delete `apply_registered_contributors()` (folded into Task 2.5 iteration)
- [ ] Delete the **four Phase-3** `aggregate_*` wrappers from Task 2.3 (now unused): `aggregate_propulsion`, `aggregate_defense`, `aggregate_hangar`, `track_multiplex`. **Phase 5 helpers stay.**
- [ ] Delete `unregister_stat_contributor_by_name` shim (after Task 2.7a migrates tests)
- [ ] Remove dead imports
- [ ] Add a test that asserts these symbols are NOT importable (pin the deletion)
- [ ] **Verify:** sharded suite green

**Notes:**

### Task 2.7: Replacement, append, and unregister acceptance tests [Medium]
**File:** `tests/unit/simulation/entities/stat_contributors/test_registry_pipeline.py`
**Tests:** `pytest tests/unit/simulation/entities/stat_contributors/test_registry_pipeline.py -v`

- [ ] **Replacement test:** register a contributor for `ShieldProjection` with `policy=REPLACE_SILENT` that sets `acc["max_shields"] = 999`. Recalculate. Assert `ship.max_shields == 999` (no double-add of the built-in's contribution, no need for a suppression frozenset).
- [ ] **Append test:** register a contributor for `ShieldProjection` with `policy=APPEND` that adds 100 to `acc["max_shields"]`. Recalculate. Assert `ship.max_shields == built_in_value + 100`.
- [ ] **Append unregister test:** register an APPEND, capture handle, recalculate (assert appended value lands), call `unregister_stat_contributor(handle)`, recalculate, assert only the default contribution lands (no leftover append).
- [ ] **Replace unregister test:** register a REPLACE, capture handle, unregister, recalculate, assert default is restored.
- [ ] **Default-cannot-be-unregistered test:** look up a default's handle (or call a test helper), attempt to unregister, assert `CannotUnregisterDefaultError`.
- [ ] **Phase-ordering test:** register a contributor with `phase_order=5` (before all built-ins) that sets a flag; register another with `phase_order=99` that asserts the flag is set. Recalculate. Assert no exception.
- [ ] **Replacement-vs-non-replaced ordering:** register a replacement for `ShieldProjection` (defense, phase 20); recalculate; assert movement (phase 10) fires before the replacement, and the replacement (now phase 99 by default) fires after non-replaced defense / hangar / command entries.
- [ ] **REPLACE_WARN log test:** register a contributor for an ability that has a default with default policy (`REPLACE_WARN`); assert `logging.warning` was called with a message naming the ability.
- [ ] **ERROR policy test:** register a contributor for an existing ability with `policy=ERROR`; assert `RegistrationConflictError` is raised.
- [ ] **Reset re-seeds test:** clear, register a modder entry, call `reset_stat_contributor_registry()`, assert defaults are present and modder entry is gone.
- [ ] **DeprecationWarning test:** call `unregister_stat_contributor_by_name("ShieldProjection")`; assert `DeprecationWarning` was emitted.
- [ ] **Verify:** all tests pass

**Notes:**

### Task 2.7a: Migrate existing test_registry.py to handle-based unregister [Medium]
**File:** `tests/unit/simulation/entities/stat_contributors/test_registry.py`
**Tests:** `pytest tests/unit/simulation/entities/stat_contributors/test_registry.py -v`

- [ ] Walk the file; replace any `unregister_stat_contributor("X")` (string-keyed) with handle-captured-from-registration form
- [ ] Delete any test asserting `BUILTIN_HANDLED_ABILITIES` contains a name (frozenset is gone)
- [ ] Flip "Registering for a built-in ability is rejected" to "Registering for a built-in ability with `policy=ERROR` raises; with `policy=REPLACE_WARN` (default) replaces and logs warning"
- [ ] Flip "Double registration raises" to "Double registration with `policy=ERROR` raises; default policy replaces"
- [ ] **Verify:** test_registry.py is fully migrated to handle-based; the `_by_name` shim is no longer used in this file

**Notes:**

### Task 2.8: Full sharded suite green [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run sharded suite; zero regressions; pass count grows with new tests
- [ ] **Acceptance:** golden snapshot bit-identical; all Task 2.7 acceptance tests pass; Task 2.7a migration complete

**Notes:**

### Task 2.9: Commit Phase 2 [Simple]

- [ ] `git add` only files in this phase's scope
- [ ] Commit message: `refactor(PROJ-367): Phase 2 — Phase-3 stat contributors as registry entries; retire suppression frozenset; introduce RegistrationHandle`
- [ ] Sign-off: `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`
- [ ] Do NOT push

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `_phase_stats_aggregation` is one iteration loop
- [ ] **Phase 5 helpers (`weapons.py:aggregate_targeting_scores`, `defense.py:apply_armor_and_repair_scores`, `defense.py:init_armor_pool`) are unchanged**
- [ ] `BUILTIN_HANDLED_ABILITIES`, `is_builtin_suppressed_for`, `apply_registered_contributors`, the four Phase-3 `aggregate_*` wrappers, and `unregister_stat_contributor_by_name` are deleted
- [ ] Replacement is implicit (no separate suppression mechanism); replacement entries inherit `phase_order=99`
- [ ] `RegistrationHandle` makes APPEND entries individually addressable
- [ ] Reset re-seeds defaults; unregister-after-replace restores default; unregister-of-default-by-handle raises
- [ ] Registry-defaults regression test pins the final seed list
- [ ] Golden snapshot bit-identical
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3

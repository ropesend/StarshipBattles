# PROJ-367: Design — Unified Stat Contributor Extension Surface

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.
>
> **This file reflects the post-Codex-consensus state** (r002 + r003 + r004
> corrections merged from `AgentCoordination/Scratchpad/Discussion/20260505T150915Z_proj-367-plan-review/`).

## Source: PROJ-360 review

PROJ-360 (`Reviews/results/2026-05-05_073251_code_proj-360-review-shipstatscalculator-domain-decompo_req-req_20260505_073251_b48e74/findings/extensibility_report.md`) flagged three findings that PROJ-360 remediation deferred as architectural:

- **EXT-07 [MAJ]:** Five ability types bypass the typed system via raw `comp.abilities.get(...)`.
- **EXT-11 [MAJ]:** Built-in domains require code edits to add new ability handling — the registry exists but is a second-tier system alongside hardcoded built-in contributors.
- **EXT-13 [MIN]:** `acc: Dict[str, Any]` has no key validation — misspellings silently produce zero output.

These are coupled. Solving them together yields a single coherent extension surface.

---

## Today's pipeline (post PROJ-360 remediation, commit `79e79d9e5`)

**Phase 3 (per-component, post-`is_operational`)** at `ship_stats.py:258-269`:

```
for layer in ship.layers.values():
  for comp in layer.components:
    if not comp.is_operational: continue
    _mov.aggregate_propulsion(comp, acc)              # built-in, hardcoded
    _def.aggregate_defense(ship, comp, acc)            # built-in, hardcoded
    _launch.aggregate_hangar(ship, comp)               # built-in, hardcoded (no acc)
    _cmd.track_multiplex(ship, comp)                   # built-in, hardcoded (no acc)
    apply_registered_contributors(ship, comp, acc)     # gated per-ability by BUILTIN_HANDLED_ABILITIES
```

**Phase 5 (whole-ship, post-physics)** at `ship_stats.py:433-447` — **out-of-scope for PROJ-367**:

```
ecm_score = _wep.aggregate_targeting_scores(ship, component_pool)
_def.apply_armor_and_repair_scores(ship, component_pool)
_def.init_armor_pool(ship)
```

Two control flows in Phase 3, two mutation surfaces, one suppression frozenset bridging them.

---

## Target pipeline (PROJ-367)

**Phase 3** becomes:

```
ship_stats.py:_phase_stats_aggregation(ship, accumulator: StatAccumulator)
  for layer in ship.layers.values():
    for comp in layer.components:
      if not comp.is_operational: continue
      for entry in STAT_CONTRIBUTOR_REGISTRY.iter_for(comp):  # ordered by phase_order
        entry.contributor(ship, comp, accumulator)
```

**Phase 5 unchanged** — Codex flagged that lumping `aggregate_targeting_scores` / `apply_armor_and_repair_scores` / `init_armor_pool` into Phase 2 was wrong because they run after Phase 4 physics and would require accumulator state to survive the physics boundary. Future project required if that work is wanted.

One Phase-3 iteration. One mutation surface (`StatAccumulator`). Built-ins are registry entries seeded at module import; modders register the same way; replacement is implicit (later registration for the same ability_name overwrites the prior entry, with a warning unless explicitly opted into).

---

## Phase 1 — Typed ability classes

### `MultiplexTrackingAbility`
- **New typed class** in `markers.py`.
- **Attribute:** `slots: int = 0`.
- **STAT_BINDINGS:** none — value is read directly by `track_multiplex` for `ship.max_targets`.
- **Loader:** ability factory in `ability_manager.py` already routes by class name; adding the class registers it.
- **Call site migration:** `command.py:58` — `mt = sum(getattr(ab, 'slots', 0) for ab in comp.get_abilities("MultiplexTracking"))`.

### `VehicleStorageAbility`
- **New typed class** in `markers.py`.
- **Attribute:** `capacity: int = 0`.
- **STAT_BINDINGS:** none — `ship.fighter_capacity` is summed.
- **Data shape:** accept both scalar `50` and dict `{"capacity": 50}`. Production data is scalar (`data/components.json:1241`).
- **Call site migration:** `launch.py:46`.

### `PodStorageAbility` (corrected — Codex C1)
- **New typed class** in `markers.py`.
- **Attribute:** `capacity_mass: float = 0.0`. **NOT** `capacity` + `pod_class`.
- **STAT_BINDINGS:** none.
- **Data shape:** verified `{"capacity_mass": 5000}` at `data/components.json:2396-2397`. Reference at `docs/systems/ability_reference.md:768-786` confirms single scalar attribute.
- **Call site migration:** `ship_stats.py:315-319` — accumulates into `acc["pod_storage_mass"]` (existing key); migrate to read `comp.get_abilities("PodStorage")[0].capacity_mass`.

### `VehicleLaunchAbility` — extend (corrected — Codex C2)
- **Existing typed class** at `markers.py:9-52`.
- **Add attribute:** `max_launch_mass: float = 0.0` parsed from `data.get("max_launch_mass", 0.0)`. The current hangar contributor (`launch.py:49`) reads `max_launch_mass` from the raw dict — required for the typed migration.
- **STAT_BINDINGS unchanged** — owns `CAPACITY_MULT` for `capacity`. `max_launch_mass` is additive and not modifier-scaled.
- **Call site migration:** `launch.py:45` — replace `comp.abilities.get("VehicleLaunch", {})` with `comp.get_abilities("VehicleLaunch")[0]` and read `.capacity`, `.fighter_class`, `.cycle_time`, `.max_launch_mass` typed attrs.

### `Armor` (marker only — no new class)
- **Call site migration:** `defense.py:52`, `ship_stats.py:201,207` — `comp.has_ability("Armor")` everywhere. Already partially the right idiom; finish the migration.

### Phase 1 success criteria
- Zero `comp.abilities.get(...)` in `stat_contributors/` and `ship_stats.py` Phase 3 path (grep verification — only allowed reads are typed-class attributes).
- Golden snapshot at `test_ship_stats_golden.py` bit-identical for the 7 existing designs; carrier + multiplex designs added (closes PROJ-360 review FIND-001 / FIND-005 incidentally).
- New unit tests for each new ability class (parse + recalculate + UI rows).

---

## Phase 2 — Built-in Phase-3 contributors as registry entries

### Registry seeding (corrected — Codex C4 + E1)

Phase 2 splits the four **Phase-3** domain contributors into per-ability `contribute_*` functions. **`weapons.py` is fully out-of-scope** — its functions run in Phase 5. The default-seed list is enumerated at Task 2.4 implementation time and pinned by a registry-defaults regression test; it is **not** pre-pinned in this plan because:
- Today `BUILTIN_HANDLED_ABILITIES` has 8 names (`registry.py:156-169`).
- `Armor` is currently handled inside `defense.aggregate_defense` without being in the suppression set (`defense.py:51-54`) — its seed status is a Phase 2 decision.
- `VehicleStorage` is currently gated under the `VehicleLaunch` block (`launch.py:40-55`) — whether it becomes a separate seed entry or stays gated is a Phase 2 decision.
- Shield energy cost (ResourceConsumption read) is attached to `ShieldRegeneration` via suppression today — its split into one or two seed entries is a Phase 2 decision.

```python
# stat_contributors/__init__.py (or _builtins.py)
def _seed_builtin_contributors() -> None:
    # movement.py — split from aggregate_propulsion
    register_stat_contributor("CombatPropulsion", movement.contribute_combat_propulsion, default=True, phase_order=10)
    register_stat_contributor("ManeuveringThruster", movement.contribute_maneuvering_thruster, default=True, phase_order=10)
    register_stat_contributor("WarpJump", movement.contribute_warp_jump, default=True, phase_order=10)
    register_stat_contributor("StrategicMovement", movement.contribute_strategic_movement, default=True, phase_order=10)
    # defense.py — split from aggregate_defense (final list pinned at Task 2.4)
    register_stat_contributor("ShieldProjection", defense.contribute_shield_projection, default=True, phase_order=20)
    register_stat_contributor("ShieldRegeneration", defense.contribute_shield_regeneration, default=True, phase_order=20)
    # ... etc — final enumeration in Task 2.4
    # launch.py — split from aggregate_hangar
    register_stat_contributor("VehicleLaunch", launch.contribute_vehicle_launch, default=True, phase_order=40)
    # command.py — split from track_multiplex
    register_stat_contributor("MultiplexTracking", command.contribute_multiplex_tracking, default=True, phase_order=50)
    # NO weapons.py entries — Phase 5 helper
```

### `RegistrationConflictPolicy` and `RegistrationHandle` (corrected — Codex C5 + D3)

```python
class RegistrationConflictPolicy(Enum):
    REPLACE_WARN = "replace_warn"     # default — log a warning, replace the entry
    REPLACE_SILENT = "replace_silent" # explicit modder opt-in
    APPEND = "append"                 # multiple contributors for one ability
    ERROR = "error"                   # legacy strict — raise on conflict

@dataclass(frozen=True)
class RegistrationHandle:
    ability_name: str
    entry_id: int   # monotonic, assigned at registration

def register_stat_contributor(
    ability_name: str,
    contributor: Callable,
    *,
    policy: RegistrationConflictPolicy = RegistrationConflictPolicy.REPLACE_WARN,
    phase_order: int = 99,   # modder default — runs after all built-ins (10..50)
    default: bool = False,   # only set by _seed_builtin_contributors()
) -> RegistrationHandle: ...

def unregister_stat_contributor(handle: RegistrationHandle) -> None: ...
```

Behavior:

- **REPLACE_WARN / REPLACE_SILENT:** the new entry takes the slot for that ability_name. The default (if any) is **suppressed** while the replacement lives. `unregister(handle)` removes the replacement and **restores the default** (if it existed before the replacement). The replacement entry inherits `phase_order=99` unless explicitly overridden, so it fires after non-replaced built-ins — mirroring today's `is_builtin_suppressed_for` + run-modder-last semantics.
- **APPEND:** entries are stored as a list under the ability_name. The default is the first entry; appended entries follow. `unregister(handle)` removes only that specific entry (matched by `entry_id`). If the handle refers to the default itself, raise `CannotUnregisterDefaultError` — defaults are managed via the seed/reset cycle, not via direct unregister.
- **ERROR:** raises on any conflict at registration. No new handle created. No-op for unregister.

### Backward-compat shim (transitional)

`unregister_stat_contributor_by_name(ability_name)` removes ALL non-default entries for that name (matching today's "unregister everything I registered" semantics for tests that do not capture handles). Marked deprecated, emits `DeprecationWarning`. **Deleted at Phase 2 close** — Task 2.7a migrates `tests/unit/simulation/entities/stat_contributors/test_registry.py` to handle-based unregister, and Task 2.6 deletes the shim.

### Reset / re-seed (corrected — Codex C8)

`reset_stat_contributor_registry()` is now **clear AND re-seed defaults** (idempotent). The root `conftest.py:31-47, 121-123` calls reset before/after every test; after Phase 2 lands, that helper restores the default-seeded registry rather than leaving it empty.

### Iteration order

Built-ins fire in domain order (movement=10, defense=20, hangar=40, command=50) so cross-phase reads still work. `phase_order` is part of `StatContributorEntry`. Modder entries default to `phase_order=99` (after all built-ins) unless overridden.

### Retirements
- `BUILTIN_HANDLED_ABILITIES` frozenset → DELETED.
- `is_builtin_suppressed_for()` helper → DELETED.
- `apply_registered_contributors` → DELETED (folded into the single iteration loop).
- The four `aggregate_*` Phase-3 wrappers (`aggregate_propulsion`, `aggregate_defense`, `aggregate_hangar`, `track_multiplex`) → DELETED after Task 2.3 splits them.
- `unregister_stat_contributor_by_name` shim → DELETED at Phase 2 close.

### Phase 2 success criteria
- `_phase_stats_aggregation` is one iteration loop; no direct calls to domain functions.
- Phase 5 helpers (`aggregate_targeting_scores`, `apply_armor_and_repair_scores`, `init_armor_pool`) untouched.
- Golden snapshot bit-identical (registration order = previous call order).
- Replacement test: register a contributor for `ShieldProjection`, recalculate, assert `max_shields` reflects ONLY the new contributor (no double-count, no suppression frozenset needed).
- Append test: register a contributor for `ShieldProjection` with `policy=APPEND`, recalculate, assert both contributions land. Then `unregister(handle)` and assert only the appended contribution is removed; default + other entries intact.
- Phase ordering test: register a contributor with `phase_order=5` (before all built-ins); register another with `phase_order=99` that asserts the flag is set. Recalculate. Assert no exception.
- Reset/re-seed test: clear, register a modder entry, call reset, assert defaults are present and modder entry is gone.

---

## Phase 3 — Typed accumulator (corrected — Codex C6 + D2)

### `StatAccumulator` shape

10 scalar fields + 4 named map fields = **14 total dataclass fields**. The current `acc[...]` initialization at `ship_stats.py:235-243` has 12 keys; promoting the two dict-shaped keys (`warp_resource_costs`, `cargo_storage`) to typed map fields means they are not also counted as scalars. Dynamic resource keys (`max_<resource>`, `gen_<resource>` synthesized by `_aggregate_resource_abilities`) live inside `resource_storage` / `resource_generation` map fields — they CANNOT be flat dataclass fields because resource types come from data files at runtime.

```python
@dataclass
class StatAccumulator:
    # Scalar fields (10)
    thrust: float = 0.0
    strategic_movement: int = 0
    turn_speed: float = 0.0
    maneuver_points: float = 0.0
    max_shields: float = 0.0
    shield_regen: float = 0.0
    shield_cost: float = 0.0
    warp_max_tonnage: float = 0.0
    warp_energy_cost: float = 0.0
    pod_storage_mass: float = 0.0

    # Named map fields (4)
    warp_resource_costs: Dict[str, float] = field(default_factory=dict)   # was acc["warp_resource_costs"]
    cargo_storage: Dict[str, float] = field(default_factory=dict)          # was acc["cargo_storage"]
    resource_storage: Dict[str, float] = field(default_factory=dict)       # was acc["max_<resource>"]
    resource_generation: Dict[str, float] = field(default_factory=dict)    # was acc["gen_<resource>"]
```

### Migration

- `_phase_stats_aggregation(ship)` constructs a fresh `StatAccumulator()` per call.
- All built-in `contribute_X` functions take `accumulator: StatAccumulator` and read/write fields by attribute access.
- `_aggregate_resource_abilities` writes into `accumulator.resource_storage[ability.resource_type]` instead of `acc[f"max_{ability.resource_type}"]`. Same for generation.
- `_apply_aggregated_stats(ship, accumulator)` reads `accumulator.thrust`, `accumulator.resource_storage.items()`, etc.
- Modder contributors get the same `StatAccumulator` reference. Misspelled scalar/map field names raise `AttributeError` at the modder's first test run. Misspelled resource types inside the maps still produce zero (same as today, but the surface area for typos is much smaller — the 14 named surfaces are validated, only resource-type strings flow through dicts).

### Combat endurance (corrected — Codex C7)

`calculate_combat_endurance(ship, component_pool)` (`ship_stats.py:449-451`, `combat_endurance.py:20-133`) reads **`ship.resources`**, not the accumulator. No `_phase_endurance` method exists. Phase 3's only requirement around endurance is that `_apply_aggregated_stats` continues to populate `ship.resources` correctly from `accumulator.resource_storage` and `accumulator.resource_generation`.

### Phase 3 success criteria
- `acc: Dict[str, Any]` is gone from the package.
- `dataclasses.fields(StatAccumulator)` returns exactly 14 fields.
- Misspelled-field test: assert `setattr(acc, "shield_regen_typo", 1.0)` raises `AttributeError` (or equivalent — `__slots__` if needed).
- Golden snapshot bit-identical.
- `docs/02_PATTERNS.md` § 35 updated to describe the unified extension surface (one registry, one typed accumulator, one mutation contract).
- PROJ-360 `decisions.md` cross-link backfilled.

---

## Alternatives considered

### A. TypedDict instead of dataclass
- Pro: less code change at write sites (still dict-syntax `acc["thrust"] = ...`).
- Con: TypedDict doesn't enforce at runtime — only mypy catches misspellings. EXT-13 wants runtime detection.
- **Rejected** in favor of dataclass for runtime safety.

### B. Keep two-tier model, just add `register_domain_contributor("defense", fn)`
- Pro: smaller change.
- Con: now there are *three* extension mechanisms. Compounds inconsistency.
- **Rejected** — the goal is one mechanism.

### C. Skip Phase 1 (leave 5 abilities untyped)
- Pro: smaller scope.
- Con: modder writing a contributor for `MultiplexTracking` still has to read `comp.abilities.get(...)`. Two-tier model persists at the API level even if it goes away in the runtime pipeline.
- **Rejected** — the typed gap is the user-visible expression of EXT-11.

### D. Drop `ship` parameter from contributors (keep only `comp` + `accumulator`)
- Pro: matches the registered-contributor surface; explicit.
- Con: command/launch contributors legitimately mutate `ship` directly (e.g., `ship.max_targets`, `ship.fighter_capacity`) for stats that aren't aggregations but assignments. Fighting that requires more invasive surgery.
- **Deferred** — keep `(ship, comp, accumulator)` triple. Future work could split "aggregator" from "ship-stat-setter" into two contributor types.

### E. Promote dynamic resource keys to flat dataclass fields
- Pro: full runtime safety on every resource type.
- Con: resource types come from data files at runtime; promoting them statically requires a code edit per new resource type, contradicting the data-driven invariant at `ship_stats.py:285-295`.
- **Rejected** — resource keys live inside `resource_storage` / `resource_generation` maps. Misspelled resource strings still produce zero (same as today), but the surface area for typos is much smaller (only resource-type strings, not all 14 stat surfaces).

### F. Pin a default-seed entry count in the design
- Pro: gives implementer a target number.
- Con: today `BUILTIN_HANDLED_ABILITIES` has 8 names; `Armor` / `VehicleStorage` / shield-energy-cost split decisions are deferred to Phase 2 implementation. Pinning a count forces those decisions before the implementer reads the code in context.
- **Rejected** — Task 2.4 enumerates the final list and pins it via a registry-defaults regression test.

### G. Fold Phase 5 helpers into the registry
- Pro: ultimate uniformity.
- Con: Phase 5 helpers run AFTER Phase 4 physics. Folding them requires accumulator state to survive the physics boundary, which is a real architectural concern not in scope for PROJ-367.
- **Rejected** — Phase 5 helpers (`aggregate_targeting_scores`, `apply_armor_and_repair_scores`, `init_armor_pool`) stay imperative. Future project required.

---

## Risks

- **R1: Loader for `MultiplexTracking` / `VehicleStorage` / `PodStorage`** may have a code path beyond the standard ability factory. Verify before assuming the new typed classes are sufficient. Phase 1 Task 1.2/1.3/1.4 explicitly verify factory routing.
- **R2: Phase 2 ordering subtlety.** Replacement entries default to `phase_order=99` to mirror today's modder-runs-last semantics. If a modder's replacement contributor depends on having reads from another modder's contribution, the `phase_order` parameter is the explicit knob. Risk that today's modder code (none in production) breaks under the new ordering — mitigated by the regression test for replacement-vs-non-replaced ordering.
- **R3: Combat endurance reads `ship.resources`, not the accumulator.** `_apply_aggregated_stats` must populate `ship.resources` from `accumulator.resource_storage` / `resource_generation` correctly. Verified by golden snapshot's combat endurance fields (12 fields added by PROJ-360 remediation).
- **R4: Reset re-seeds defaults; unregister-after-replace restores default.** Both behaviors are explicit in Phase 2 Task 2.4 and tested. Risk is that the `reset_stat_contributor_registry` change breaks existing tests that expected an empty registry post-reset — Task 2.7a migrates them.
- **R5: Backward-compat shim deletion timing.** `unregister_stat_contributor_by_name` is deprecated and emits `DeprecationWarning` during Phase 2 Task 2.7a; deleted at Phase 2 Task 2.6 (or close). Risk that some test forgot to migrate — caught by a final grep at Phase 2 close.
- **R6: Registry file size.** If `RegistrationConflictPolicy` + `RegistrationHandle` + `_seed_builtin_contributors` + `StatAccumulator` all land in `registry.py`, the file may push the 500 LOC ceiling. Mitigation: split `StatAccumulator` into a sibling `accumulator.py` if needed at Phase 3 implementation time.

---

## Out-of-band: PROJ-360 cross-link

When Phase 3 lands, update `Projects/active_projects/PROJ-360/decisions.md` to mark EXT-07/EXT-11/EXT-13 as **resolved by PROJ-367 commit `<sha>`** in the Audit Remediation table.

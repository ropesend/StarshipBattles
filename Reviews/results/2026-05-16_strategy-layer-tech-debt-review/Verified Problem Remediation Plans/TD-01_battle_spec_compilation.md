# TD-01: Battle Spec Compilation Is Still A Central Integration Knot

**Status:** VERIFIED
**Verified:** 2026-05-16
**Source review:** `Reviews/results/2026-05-16_strategy-layer-tech-debt-review/report.md` (TD-01, lines 84-104)

---

## Verification Findings

### Current file sizes (worse than report cited)

| File | LOC (now) | Report cited | Project ceiling |
|------|-----------|--------------|-----------------|
| `game/strategy/combat/spec_compiler.py` | **959** | 857 | 500 |
| `game/strategy/adapters/simulation_adapter.py` | **620** | 553 | 500 |

Both files have grown since the review; the spec compiler is now nearly 2x the project ceiling and the adapter is past it.

### Side-channel attributes confirmed (one more than report listed)

All set via `object.__setattr__(spec, ...)` because `BattleSpec` is a frozen dataclass — at `game/strategy/combat/spec_compiler.py:271-279`:

| Attribute | Set at | Read at | Purpose |
|-----------|--------|---------|---------|
| `_mine_groups` | `spec_compiler.py:271` | `simulation_adapter.py:315` | Filtered-out mine_group Fleets for tactical resolver wiring |
| `_owner_to_team_id` | `spec_compiler.py:272` | `simulation_adapter.py:316` | empire_id → team_id for `TacticalMineResolver._owner_team_id` |
| `_engine_ref` | `spec_compiler.py:278` | `simulation_adapter.py:335` | One-slot list the pre-tick callback fills with the `BattleEngine` instance so the post-battle hook can call `apply_reboard` |
| `_combat_fleets` | `spec_compiler.py:279` | `simulation_adapter.py:334` | Combat fleets (mine_groups filtered out) for the reboard setup builder |

The report listed three of these; `_combat_fleets` is a fourth, added in PROJ-FMS-C. Tests directly inspect these too (`tests/integration/test_fms_b_e2e.py:414, 415, 420, 493`).

### `build_strategy_battle_spec` does too many things

In the single 200-line function at `spec_compiler.py:78-280` it:

1. Filters mine_groups out of the fleet list (`_split_mine_groups_from_fleets`, lines 151, 430-451)
2. Groups remaining fleets by `owner_id` and builds team specs (lines 166-190, `_team_spec_for_fleet_group`)
3. Builds the empire→team_id map for downstream consumers (lines 196-198)
4. Translates environmental effects + per-team modifiers into a `ModifierStack` (lines 199-204, `_build_modifier_stack`, `_entries_from_sector_effects`, `_entries_from_fleet_combat_modifiers`)
5. Resolves boundary from settings (lines 206-210)
6. Picks end condition / absolute tick cap (lines 212-223)
7. Builds the post-battle hook closure (lines 245-251, `_build_strategy_post_battle_hook`)
8. Constructs the frozen `BattleSpec` and **then mutates it** with four side-channel attrs (lines 253-279)

In the same module file (`spec_compiler.py:454-549`) it *also* exposes two pre-tick setup builders:
- `build_fighter_reboard_setup` (lines 454-491)
- `build_mine_resolver_setup` (lines 494-549)

These are *imported by the adapter, not the spec compiler itself* (see `simulation_adapter.py:319-320, 337-338`). The spec compiler is acting as a kitchen-sink module for "anything related to strategy→battle assembly".

### Adapter complicity

The adapter at `simulation_adapter.py:309-346` has to:

1. Read `_mine_groups` and `_owner_to_team_id` side-channels off the spec
2. Conditionally import `build_mine_resolver_setup` and call it with side-channel data
3. Read `_combat_fleets` and `_engine_ref` side-channels off the spec
4. Conditionally import `build_fighter_reboard_setup` and call it
5. Compose the two pre-tick callbacks into one via `_compose_setup_callbacks`

This means every new "strategy state affects mid-battle behavior" feature touches both the spec compiler (to stash a new side-channel) and the adapter (to wire it through). Exactly the extension-friction the report flags.

### Existing tests pinning behavior

| Test file | LOC | Pins |
|-----------|-----|------|
| `tests/unit/strategy/combat/test_spec_compiler.py` | 831 | Team building, modifiers, boundary, components, multi-fleet grouping |
| `tests/unit/strategy/combat/test_spec_compiler_formation.py` | 173 | FormationResolver call site, per-fleet formation |
| `tests/unit/strategy/combat/test_post_battle_hook.py` | 640 | Outcome → ship-instance writeback |
| `tests/unit/strategy/combat/test_fighter_group_combat_join.py` | 145 | `_split_mine_groups_from_fleets` (private helper, treated as API) |
| `tests/unit/strategy/combat/test_satellite_group_combat_join.py` | 129 | Same |
| `tests/integration/test_fms_b_e2e.py` | 535 | Direct inspection of `spec._mine_groups`, `spec._owner_to_team_id` |

Total: **~2,450 LOC of test coverage** is good news — this gives strong behavioral pinning for a TDD-driven refactor. Bad news: two test files reach into the private `_split_mine_groups_from_fleets` helper and one integration test asserts on the side-channel attribute names directly. Those tests must be migrated to the new public seam in the same change.

### Verdict

**VERIFIED.** The report's description is accurate and conservative. The actual debt is slightly worse:
- Files have grown
- A fourth side-channel attribute exists
- Two unrelated pre-tick-setup builders (mine + reboard) co-habit the spec-compiler module

---

## Executor Guardrails

- Preserve the public import path `game.strategy.combat.spec_compiler.build_strategy_battle_spec` for this remediation. Many tests and docs import it directly; deleting or renaming the module adds churn without reducing the underlying debt.
- Do **not** add fields to `game/simulation/battle_spec.py::BattleSpec` unless an existing failing test proves the assembly DTO is insufficient. Extra strategy-only state belongs beside the spec, not on the frozen simulation DTO.
- The only verified production runtime caller is `game/strategy/adapters/simulation_adapter.py`. `game/strategy/engine/conflict_resolution_engine.py` currently mentions the compiler in comments only. Re-run grep before editing and do not touch non-callers unless a new runtime import appears.
- Keep battle behavior unchanged. This plan is a structural split only: same team grouping, same modifier translation, same tick-limit rules, same post-battle writeback, same mine/reboard behavior.
- Do not keep private-helper compatibility shims. When a new public seam exists, migrate tests in the same phase instead of re-exporting old private helpers.
- Before each phase, re-run:

```bash
rg -n "build_strategy_battle_spec|object\.__setattr__\(spec|_mine_groups|_owner_to_team_id|_combat_fleets|_engine_ref" game tests
rg -n "from game\.strategy\.combat\.spec_compiler import build_strategy_battle_spec|build_strategy_battle_spec\(" game tests docs
```

If parallel work adds new call sites, extend the touch list before editing code.

---

## Affected Code

### Production files to edit

- `game/strategy/combat/spec_compiler.py` — reduce to a thin public facade plus transitional internal wiring
- `game/strategy/adapters/simulation_adapter.py` — switch from spec side-channels to `StrategyBattleAssembly`
- `game/strategy/combat/post_battle_hook.py` — keep behavior intact; only adjust imports if extraction requires it

### New production files to add

- `game/strategy/combat/battle_assembly.py` — `BattleSpecExtensions`, `StrategyBattleAssembly`, `StrategyBattleAssembler`
- `game/strategy/combat/team_spec_builder.py` — fleet grouping, team construction, formation selection, mine-group split
- `game/strategy/combat/strategy_modifier_stack_builder.py` — environmental/team modifier translation
- `game/strategy/combat/post_battle_hook_builder.py` — closure construction for outcome writeback
- `game/strategy/combat/pre_tick_setup_registry.py` — named callback registry with deterministic composition
- `game/strategy/combat/pre_tick_setup/__init__.py`
- `game/strategy/combat/pre_tick_setup/mine_setup.py`
- `game/strategy/combat/pre_tick_setup/reboard_setup.py`

### Existing tests that must be migrated

- `tests/unit/strategy/combat/test_spec_compiler.py`
- `tests/unit/strategy/combat/test_spec_compiler_formation.py`
- `tests/unit/strategy/combat/test_post_battle_hook.py`
- `tests/unit/strategy/combat/test_fighter_group_combat_join.py`
- `tests/unit/strategy/combat/test_satellite_group_combat_join.py`
- `tests/unit/strategy/adapters/test_simulation_adapter.py`
- `tests/integration/strategy/combat/test_damage_persistence.py`
- `tests/integration/test_fms_b_e2e.py`

### New tests to add

- `tests/unit/strategy/combat/test_battle_assembly.py`
- `tests/unit/strategy/combat/test_team_spec_builder.py`
- `tests/unit/strategy/combat/test_strategy_modifier_stack_builder.py`
- `tests/unit/strategy/combat/test_post_battle_hook_builder.py`
- `tests/unit/strategy/combat/test_pre_tick_setup_registry.py`

### Docs to update after code is green

- `docs/systems/strategy_layer.md`
- `docs/01_ARCHITECTURE.md`
- `docs/02_PATTERNS.md`

---

## Goal / End State

The end state is a **thin public facade** plus typed assembly pipeline:

```text
build_strategy_battle_spec(...)      # stays as public entry point
    -> StrategyBattleAssembler.assemble(...)
        -> StrategyBattleAssembly(
               spec=BattleSpec,
               extensions=BattleSpecExtensions,
               pre_tick_setup=PreTickBattleSetupRegistry,
           )
```

### Required architecture outcomes

1. `BattleSpec` remains frozen and unmutated after construction.
2. Strategy-only side data moves to `BattleSpecExtensions`, stored on `StrategyBattleAssembly`, not on `BattleSpec`.
3. `simulation_adapter.py` consumes `StrategyBattleAssembly`, not `getattr(spec, "_...")`.
4. Mine and reboard setup builders live under `game/strategy/combat/pre_tick_setup/`, not inside `spec_compiler.py`.
5. `spec_compiler.py` remains as the public import path but shrinks to a thin orchestrator/facade. Target size: `<= 120 LOC`.

### Concrete contracts

```python
@dataclass(frozen=True)
class BattleSpecExtensions:
    mine_groups: tuple[Fleet, ...]
    owner_to_team_id: Mapping[Any, int]
    combat_fleets: tuple[Fleet, ...]
    engine_ref: list[Any]


@dataclass(frozen=True)
class StrategyBattleAssembly:
    spec: BattleSpec
    extensions: BattleSpecExtensions
    pre_tick_setup: PreTickBattleSetupRegistry
```

```python
class PreTickBattleSetupRegistry:
    def register(self, name: str, setup: Callable[[Any, BattleSpec], None]) -> None: ...
    def composed_callback(self) -> Callable[[Any, BattleSpec], None] | None: ...
```

---

## Remediation Plan

Strict TDD throughout. Every phase is independently mergeable and leaves the tree green.

### Phase 0 — Preflight and baseline capture

**Purpose:** freeze the current seam before moving code.

**Touch list:** none.

**Actions:**

1. Run the two `rg` commands from **Executor Guardrails**.
2. Confirm that the only production runtime caller is still `game/strategy/adapters/simulation_adapter.py`.
3. Record which tests directly inspect side-channel attributes; at minimum `tests/integration/test_fms_b_e2e.py` must be on the migration list before side-channels are removed.

**Exit criteria:**

- You have an updated call-site list.
- No code edited yet.

### Phase 1 — Introduce typed assembly DTOs

**Purpose:** create the new seam without changing runtime behavior.

**Touch list:**

- Add `game/strategy/combat/battle_assembly.py`
- Add `tests/unit/strategy/combat/test_battle_assembly.py`
- Edit `game/strategy/combat/spec_compiler.py`

**Red tests first:**

- `test_strategy_battle_assembly_holds_spec_extensions_and_setup_registry`
- `test_battle_spec_extensions_exposes_all_four_current_side_channel_fields`
- `test_build_strategy_battle_assembly_returns_typed_wrapper_around_existing_spec`

**Implementation rules:**

1. Add `BattleSpecExtensions` and `StrategyBattleAssembly`.
2. Add `build_strategy_battle_assembly(...)` in `spec_compiler.py`.
3. In this phase only, `build_strategy_battle_assembly(...)` may read the current side-channels from the already-built spec to populate `extensions`. Do **not** remove the side-channel writes yet.
4. Keep `build_strategy_battle_spec(...)` behavior unchanged.

**Validation:**

```bash
pytest tests/unit/strategy/combat/test_battle_assembly.py -x
pytest tests/unit/strategy/combat/test_spec_compiler.py tests/unit/strategy/combat/test_spec_compiler_formation.py -x
```

**Exit criteria:**

- `StrategyBattleAssembly` exists and is covered by dedicated tests.
- Existing compiler tests still pass.
- Side-channel writes still exist temporarily.

### Phase 2 — Extract pure builders out of `spec_compiler.py`

**Purpose:** move large cohesive helpers before changing the adapter.

**Touch list:**

- Add `game/strategy/combat/team_spec_builder.py`
- Add `game/strategy/combat/strategy_modifier_stack_builder.py`
- Add `game/strategy/combat/post_battle_hook_builder.py`
- Edit `game/strategy/combat/spec_compiler.py`
- Add three new unit-test files for the new builders
- Edit the two `*_combat_join.py` tests to target `TeamSpecBuilder`, not `_split_mine_groups_from_fleets`

**Red tests first:**

- `tests/unit/strategy/combat/test_team_spec_builder.py`
- `tests/unit/strategy/combat/test_strategy_modifier_stack_builder.py`
- `tests/unit/strategy/combat/test_post_battle_hook_builder.py`

**Implementation rules:**

1. Move `_team_spec_for_fleet_group`, `_pick_formation_for_fleet`, `_ship_spec_from_instance`, `_split_mine_groups_from_fleets` into `TeamSpecBuilder`.
2. Move modifier-stack helpers into `StrategyModifierStackBuilder`.
3. Move `_build_strategy_post_battle_hook` into `PostBattleHookBuilder`.
4. `spec_compiler.py` now delegates to those builders but still writes the four side-channels for compatibility.
5. Do **not** re-export `_split_mine_groups_from_fleets`. Migrate the tests in this phase.

**Validation:**

```bash
pytest tests/unit/strategy/combat/test_team_spec_builder.py -x
pytest tests/unit/strategy/combat/test_strategy_modifier_stack_builder.py -x
pytest tests/unit/strategy/combat/test_post_battle_hook_builder.py -x
pytest tests/unit/strategy/combat/test_fighter_group_combat_join.py tests/unit/strategy/combat/test_satellite_group_combat_join.py -x
pytest tests/unit/strategy/combat/ -x
```

**Exit criteria:**

- `spec_compiler.py` delegates team/modifier/hook work.
- No tests import `_split_mine_groups_from_fleets`.

### Phase 3 — Extract pre-tick setup registry and setup builders

**Purpose:** remove mine/reboard setup responsibilities from `spec_compiler.py`.

**Touch list:**

- Add `game/strategy/combat/pre_tick_setup_registry.py`
- Add `game/strategy/combat/pre_tick_setup/__init__.py`
- Add `game/strategy/combat/pre_tick_setup/mine_setup.py`
- Add `game/strategy/combat/pre_tick_setup/reboard_setup.py`
- Edit `game/strategy/combat/spec_compiler.py`
- Add `tests/unit/strategy/combat/test_pre_tick_setup_registry.py`

**Red tests first:**

- `test_registry_composes_callbacks_in_registration_order`
- `test_registry_returns_none_when_empty`
- `test_mine_and_reboard_setups_register_without_knowing_about_each_other`

**Implementation rules:**

1. Move `build_mine_resolver_setup` and `build_fighter_reboard_setup` out of `spec_compiler.py`.
2. `PreTickBattleSetupRegistry` owns registration order and callback composition.
3. `build_strategy_battle_assembly(...)` returns a populated registry instance alongside the spec and extensions.
4. `spec_compiler.py` must no longer define either setup builder.

**Validation:**

```bash
pytest tests/unit/strategy/combat/test_pre_tick_setup_registry.py -x
pytest tests/unit/strategy/combat/ -x
```

**Exit criteria:**

- `spec_compiler.py` no longer contains pre-tick setup helpers.
- A typed callback registry exists and is unit-tested.

### Phase 4 — Migrate the adapter to `StrategyBattleAssembly` and remove side-channels

**Purpose:** switch the runtime caller to the typed seam, then delete the legacy spec mutation.

**Touch list:**

- Edit `game/strategy/adapters/simulation_adapter.py`
- Edit `game/strategy/combat/spec_compiler.py`
- Edit `tests/unit/strategy/adapters/test_simulation_adapter.py`
- Edit `tests/integration/test_fms_b_e2e.py`
- Edit `tests/integration/strategy/combat/test_damage_persistence.py`

**Red tests first:**

- new adapter test asserting the adapter reads `assembly.extensions.mine_groups`
- new adapter test asserting the callback comes from `assembly.pre_tick_setup.composed_callback()`
- update the FMS integration test to fail unless side-channel inspection has been replaced

**Implementation rules:**

1. `simulation_adapter._build_spec` becomes `simulation_adapter._build_assembly` or equivalent.
2. `run_battle(...)` still receives `assembly.spec`; pre-tick setup comes from `assembly.pre_tick_setup.composed_callback()`.
3. Replace all runtime reads of `_mine_groups`, `_owner_to_team_id`, `_combat_fleets`, `_engine_ref`.
4. Only after tests are migrated, delete all four `object.__setattr__(spec, ...)` writes in `spec_compiler.py`.

**Validation:**

```bash
pytest tests/unit/strategy/adapters/test_simulation_adapter.py -x
pytest tests/integration/test_fms_b_e2e.py tests/integration/test_fms_c_carrier_ai_launch.py -x
python Tools/test_sharded/test_sharded.py
```

**Exit criteria:**

- Zero runtime side-channel reads remain.
- Zero side-channel writes remain.
- Full sharded suite passes once at this boundary.

### Phase 5 — Reduce `spec_compiler.py` to a thin public facade and update docs

**Purpose:** finish the maintainability payoff without breaking imports.

**Touch list:**

- Edit `game/strategy/combat/spec_compiler.py`
- Edit `docs/systems/strategy_layer.md`
- Edit `docs/01_ARCHITECTURE.md`
- Edit `docs/02_PATTERNS.md`

**Implementation rules:**

1. `spec_compiler.py` keeps `build_strategy_battle_spec(...)` and may optionally re-export `build_strategy_battle_assembly(...)`.
2. Its body should be orchestration only: instantiate `StrategyBattleAssembler`, call `assemble`, and return `assembly.spec`.
3. Remove now-dead imports and stale module doc text that still describes side-channels or embedded setup builders.

**Validation:**

```bash
pytest tests/unit/strategy/combat/ tests/unit/strategy/adapters/test_simulation_adapter.py -x
pytest tests/integration/strategy/combat/test_damage_persistence.py tests/integration/test_fms_b_e2e.py -x
python Tools/test_sharded/test_sharded.py
pytest tests/ --testmon
```

**Exit criteria:**

- `spec_compiler.py` is a thin facade.
- Docs describe the assembler pipeline rather than spec mutation.

---

## Test Strategy

### Always-run grep checks

```bash
rg -n "object\.__setattr__\(spec" game tests
rg -n "getattr\(spec, ['\"]_" game tests
```

Expected progression:

- After phases 1-3: first grep still returns the four writes; second grep may still return adapter/tests.
- After phase 4: both greps return zero hits.

### Phase-focused commands

```bash
pytest tests/unit/strategy/combat/test_battle_assembly.py -x
pytest tests/unit/strategy/combat/test_team_spec_builder.py -x
pytest tests/unit/strategy/combat/test_strategy_modifier_stack_builder.py -x
pytest tests/unit/strategy/combat/test_post_battle_hook_builder.py -x
pytest tests/unit/strategy/combat/test_pre_tick_setup_registry.py -x
pytest tests/unit/strategy/adapters/test_simulation_adapter.py -x
pytest tests/integration/test_fms_b_e2e.py tests/integration/test_fms_c_carrier_ai_launch.py -x
```

### Full validation gates

- End of phase 4: `python Tools/test_sharded/test_sharded.py`
- End of phase 5: `python Tools/test_sharded/test_sharded.py`

---

## Risks & Mitigations

| Risk | Likelihood | Required mitigation |
|------|------------|---------------------|
| Breaking the widely-imported `build_strategy_battle_spec` path while doing a structural split | High | Keep `spec_compiler.py` as the public facade for this remediation. Do not delete or rename the import path. |
| A weak executor removes side-channels before the adapter and tests are migrated | High | Phase 4 explicitly gates deletion on adapter/test migration. Do not remove any `object.__setattr__` call before the adapter reads the assembly DTO. |
| Hidden callers still read private spec attrs | Medium | Re-run the grep in Phase 0 and again immediately before side-channel deletion. |
| `_engine_ref` mutation is still required for reboard | Medium | Preserve the one-slot list contract inside `BattleSpecExtensions.engine_ref`; only its location changes. |
| New builders reintroduce behavior drift while splitting code | Medium | Keep existing tests as characterization coverage and add seam tests only around the extracted APIs. No rule changes belong in this refactor. |

---

## Dependencies / Order

### Verified cross-plan constraints

- **TD-10 depends on TD-01.** TD-10 redesigns deployables and should not be forced to preserve the current spec side-channels.
- **TD-01 is independent of TD-02 and TD-03.** No new constraint surfaced during validation.

### Impact on `EXECUTION_ORDER.md`

No required change. The current order document already keeps TD-01 ahead of TD-10, and nothing in this validation introduced a new hard dependency on TD-02 or TD-03.

---

## Estimated Scope

| Phase | Primary work | Validation cost |
|-------|--------------|-----------------|
| 0 | grep baseline only | negligible |
| 1 | add assembly DTOs and tests | focused unit tests |
| 2 | extract team/modifier/hook builders | focused unit suite |
| 3 | extract setup registry/package | focused unit suite |
| 4 | adapter migration + side-channel removal | one full sharded run |
| 5 | thin facade + docs | one full sharded run |

Expected wall-clock remains under one hour, dominated by the two sharded test runs.

---

## Completion Criteria

- [ ] `game/strategy/combat/spec_compiler.py` remains as the public entry point and is `<= 120 LOC`
- [ ] `game/strategy/adapters/simulation_adapter.py` no longer reads any private spec attribute
- [ ] `rg "object\.__setattr__\(spec" game tests` returns zero hits
- [ ] `rg "getattr\(spec, ['\"]_" game tests` returns zero hits
- [ ] No production file under `game/strategy/combat/` exceeds 500 LOC
- [ ] `python Tools/test_sharded/test_sharded.py` passes after phase 4 and again after phase 5
- [ ] `docs/systems/strategy_layer.md` describes the assembly pipeline, not spec side-channels

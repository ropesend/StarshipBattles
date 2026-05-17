# PROJ-426: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.
>
> **Canonical source:** [TD-01_battle_spec_compilation.md](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-01_battle_spec_compilation.md). This file distills that plan; if the two diverge, the TD plan wins.

## Verification Evidence (already verified before scaffold)

| Metric | Confirmed value | Source check |
|---|---|---|
| `game/strategy/combat/spec_compiler.py` LOC | **959** (report cited 857; file has grown — almost 2x the 500 ceiling) | `wc -l` |
| `game/strategy/adapters/simulation_adapter.py` LOC | **620** (report cited 553; over the ceiling) | `wc -l` |
| Side-channel attrs set via `object.__setattr__(spec, ...)` | **4** (report cited 3; verification found a fourth, `_combat_fleets`, added in PROJ-FMS-C) | `spec_compiler.py:271-279` |
| Production runtime callers of `build_strategy_battle_spec` | **1** (`simulation_adapter.py`; `conflict_resolution_engine.py` references in comments only) | `rg` sweep |
| Tests asserting on private side-channels by name | At least `tests/integration/test_fms_b_e2e.py:414, 415, 420, 493` | Verification line cites |
| Tests pinning on private `_split_mine_groups_from_fleets` helper | `test_fighter_group_combat_join.py`, `test_satellite_group_combat_join.py` | Verification line cites |
| Total relevant test LOC (behavioral pinning available) | **~2,450 LOC** across 6 test files | Verification inventory |

## Side-Channel Inventory (the four attrs to eliminate)

All four are written at `game/strategy/combat/spec_compiler.py:271-279` via `object.__setattr__(spec, ...)` because `BattleSpec` is a frozen dataclass. They are read by `game/strategy/adapters/simulation_adapter.py:309-346`.

| Attribute | Set at | Read at | Purpose | Maps to new field |
|-----------|--------|---------|---------|-------------------|
| `_mine_groups` | `spec_compiler.py:271` | `simulation_adapter.py:315` | Filtered-out mine_group Fleets so the tactical mine resolver can be wired | `BattleSpecExtensions.mine_groups: tuple[Fleet, ...]` |
| `_owner_to_team_id` | `spec_compiler.py:272` | `simulation_adapter.py:316` | `empire_id → team_id` map for `TacticalMineResolver._owner_team_id` | `BattleSpecExtensions.owner_to_team_id: Mapping[Any, int]` |
| `_engine_ref` | `spec_compiler.py:278` | `simulation_adapter.py:335` | One-slot list filled by pre-tick callback with the `BattleEngine` instance so the post-battle hook can call `apply_reboard`. **Mutation is required** — preserve the one-slot list contract; only the location changes | `BattleSpecExtensions.engine_ref: list[Any]` (must remain a mutable single-slot list) |
| `_combat_fleets` | `spec_compiler.py:279` | `simulation_adapter.py:334` | Combat fleets (mine_groups filtered out) for the reboard setup builder | `BattleSpecExtensions.combat_fleets: tuple[Fleet, ...]` |

## Goal / End State (target architecture)

```text
build_strategy_battle_spec(...)              # public entry point (preserved import path)
    -> StrategyBattleAssembler.assemble(...) # orchestrator
        -> StrategyBattleAssembly(
               spec=BattleSpec,              # frozen, NEVER mutated post-construction
               extensions=BattleSpecExtensions,  # frozen typed sidecar
               pre_tick_setup=PreTickBattleSetupRegistry,
           )
```

```python
@dataclass(frozen=True)
class BattleSpecExtensions:
    mine_groups: tuple[Fleet, ...]
    owner_to_team_id: Mapping[Any, int]
    combat_fleets: tuple[Fleet, ...]
    engine_ref: list[Any]                # mutable one-slot list — see row above


@dataclass(frozen=True)
class StrategyBattleAssembly:
    spec: BattleSpec
    extensions: BattleSpecExtensions
    pre_tick_setup: PreTickBattleSetupRegistry


class PreTickBattleSetupRegistry:
    def register(self, name: str, setup: Callable[[Any, BattleSpec], None]) -> None: ...
    def composed_callback(self) -> Callable[[Any, BattleSpec], None] | None: ...
```

### Module layout (production)

```
game/strategy/combat/
    spec_compiler.py                            # thin facade, <= 120 LOC, preserves public import path
    battle_assembly.py                          # BattleSpecExtensions, StrategyBattleAssembly, StrategyBattleAssembler
    team_spec_builder.py                        # TeamSpecBuilder (fleet grouping, team build, formation, mine split)
    strategy_modifier_stack_builder.py          # env + per-team modifier translation
    post_battle_hook_builder.py                 # PostBattleHookBuilder (closure construction)
    post_battle_hook.py                         # unchanged behavior; import paths may shift
    pre_tick_setup_registry.py                  # PreTickBattleSetupRegistry
    pre_tick_setup/
        __init__.py
        mine_setup.py                           # ex-build_mine_resolver_setup
        reboard_setup.py                        # ex-build_fighter_reboard_setup
```

### Hard architectural invariants

1. `BattleSpec` (in `game/simulation/battle_spec.py`) remains frozen and unmutated post-construction. **Do not add fields to `BattleSpec`** unless a failing test proves the assembly DTO is insufficient.
2. All strategy-only side data lives on `BattleSpecExtensions`, stored on `StrategyBattleAssembly`, not on `BattleSpec`.
3. `simulation_adapter.py` consumes `StrategyBattleAssembly`; **no `getattr(spec, "_...")` calls remain**.
4. Mine and reboard setup builders live under `game/strategy/combat/pre_tick_setup/`, not inside `spec_compiler.py`.
5. The public import path `game.strategy.combat.spec_compiler.build_strategy_battle_spec` is preserved for this remediation. Many tests and docs import it directly.
6. `StrategyBattleAssembler` will carry a `mine_group_filter` parameter throughout this project. **PROJ-431 Phase 2 owns its simplification** — do not pre-collapse it here.

## Test Migration Plan

Two classes of tests violate the new seam and **must be migrated in the same phase** as the seam change (no compatibility shims, no re-exporting private helpers — per AGENTS.md root-cause rule):

### Tests pinning the private `_split_mine_groups_from_fleets` helper (Phase 2)

| Test file | Current target | New target |
|---|---|---|
| `tests/unit/strategy/combat/test_fighter_group_combat_join.py` | imports `_split_mine_groups_from_fleets` from `spec_compiler` | calls `TeamSpecBuilder.split_mine_groups(...)` (or equivalent public method) from `team_spec_builder` |
| `tests/unit/strategy/combat/test_satellite_group_combat_join.py` | same | same |

Phase 2 must:
1. Move the helper into `TeamSpecBuilder` as a public method.
2. Edit both `*_combat_join.py` files to import the new method.
3. Do **not** re-export `_split_mine_groups_from_fleets` from `spec_compiler`.

### Tests pinning side-channel attribute names on the spec (Phase 4)

| Test file | Lines that fail when side-channels disappear | New target |
|---|---|---|
| `tests/integration/test_fms_b_e2e.py` | `:414, 415, 420, 493` — `spec._mine_groups`, `spec._owner_to_team_id` reads | read `assembly.extensions.mine_groups`, `assembly.extensions.owner_to_team_id` |
| `tests/unit/strategy/adapters/test_simulation_adapter.py` | adapter-side reads of `_mine_groups`, `_owner_to_team_id`, `_combat_fleets`, `_engine_ref` | adapter consumes `assembly.extensions.*`; pre-tick callback comes from `assembly.pre_tick_setup.composed_callback()` |
| `tests/integration/strategy/combat/test_damage_persistence.py` | indirect (via adapter integration) | re-run after Phase 4 migration; expected to pass without source edits if seam is correct |

Phase 4 must:
1. Land the adapter migration **first**.
2. Migrate the three test files in the same commit.
3. Only then delete the four `object.__setattr__(spec, ...)` writes in `spec_compiler.py`.

## Phase-by-Phase Architecture Summary

| Phase | Compiler state | Side-channels present? | Adapter reads | Setup builders live where |
|---|---|---|---|---|
| 0 (preflight) | unchanged | yes (4) | side-channels | inside `spec_compiler.py` |
| 1 (typed DTOs) | adds `build_strategy_battle_assembly` that reads its own side-channels | yes (4) — temporarily duplicated by the new wrapper | side-channels (unchanged) | inside `spec_compiler.py` |
| 2 (builder extraction) | delegates to `TeamSpecBuilder`, `StrategyModifierStackBuilder`, `PostBattleHookBuilder` | yes (4) — still written for compat | side-channels (unchanged) | inside `spec_compiler.py` |
| 3 (pre-tick extraction) | no longer defines setup builders; registry instance returned from assembly | yes (4) — still written for compat | side-channels (unchanged) | `pre_tick_setup/` package |
| 4 (adapter migration + side-channel deletion) | side-channel writes deleted | **no (0)** | `assembly.extensions.*` + `assembly.pre_tick_setup.composed_callback()` | `pre_tick_setup/` package |
| 5 (facade + docs) | `<= 120 LOC`; orchestrator only | no | unchanged from Phase 4 | unchanged from Phase 4 |

## Risks & Mitigations (per source plan)

| Risk | Likelihood | Mitigation |
|---|---|---|
| Breaking the widely-imported `build_strategy_battle_spec` path while doing a structural split | High | Keep `spec_compiler.py` as the public facade for this remediation. Do not delete or rename the import path. |
| A weak executor removes side-channels before the adapter and tests are migrated | High | Phase 4 explicitly gates deletion on adapter/test migration. Do not remove any `object.__setattr__` call before the adapter reads the assembly DTO. |
| Hidden callers still read private spec attrs | Medium | Re-run the grep in Phase 0 and again immediately before side-channel deletion. |
| `_engine_ref` mutation is still required for reboard | Medium | Preserve the one-slot mutable list contract inside `BattleSpecExtensions.engine_ref`; only its location changes — the field is intentionally mutable inside an otherwise frozen dataclass. |
| New builders reintroduce behavior drift while splitting code | Medium | Keep existing tests as characterization coverage and add seam tests only around the extracted APIs. No rule changes belong in this refactor. |
| Phase 4 deletion not coordinated with test migration | High | Test migration commits land in the same phase, ahead of the deletion. Phase 4 checklist enforces ordering. |

## Cross-Plan Coupling

- **TD-01 → TD-10 (HARD).** PROJ-431 (TD-10 deployable substrate redesign) cannot start its main redesign until this project completes. The deployable substrate redesign should not have to preserve the current spec side-channels. Confirmed by [EXECUTION_ORDER.md §"Recommended Linear Order #5"](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/EXECUTION_ORDER.md) and TD-01 plan §"Dependencies / Order".
- **Temporary state handed to PROJ-431:** `StrategyBattleAssembler.mine_group_filter` parameter. PROJ-431 Phase 2 simplifies it.
- **No hard prerequisites for TD-01 itself.** Independent of TD-02 and TD-03.
- **Out of scope (deliberate):** adding fields to `BattleSpec`, touching `conflict_resolution_engine.py`, behavioral changes to battle behavior, renaming the public import path.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

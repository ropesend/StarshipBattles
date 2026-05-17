# Strategy Layer Tech-Debt Remediation - Execution Order

**Date:** 2026-05-16  
**Scope:** Verified construction order for the 10 remediation plans in this directory.  
**Validation basis:** the original review report plus the independently validated per-plan dependency sections.

## How this order was chosen

Three rules govern the sequence:

1. Hard dependencies win over value ranking.
2. Mechanical, low-risk cleanup goes early when it simplifies later work.
3. When a plan only partially overlaps another, use a phase gate instead of inventing a false whole-plan dependency.

The last rule matters here: the original draft over-modeled several helpful preferences as hard blockers. The corrected order below keeps only the real hard edges and spells out the one important phase-level overlap explicitly.

## Dependency Graph

Hard edges:

```text
TD-03 -> TD-07
TD-01 -> TD-10
TD-10 Phase 1 -> TD-06 cargo/deployable forwarder-demolition batch
```

Soft preferences:

```text
TD-02 -> TD-08
TD-02 -> TD-05
TD-09 -> TD-04
```

No other plan-to-plan hard blockers were confirmed.

## Phase Gates

These gates are the part a weaker LLM must follow literally.

1. `TD-06` may start immediately, but stop after Phases 0-4 if the work is about to delete or migrate cargo/deployable forwarders.
2. `TD-10` Phase 1 must land before the deferred `TD-06` cargo/deployable cleanup batch resumes.
3. `TD-10` main redesign work must not start before `TD-01` is complete.
4. `TD-07` must not start before `TD-03` is complete.
5. `TD-08` should wait for `TD-02`; it also benefits from `TD-03`, but that is not a blocker.

## Recommended Linear Order

### 1. TD-09 - Engine interface split

Run first because it is the lowest-risk, most mechanical change in the set, and it removes noise from later imports without changing behavior.

[TD-09_engine_interface_split.md](C:/Developer/StarshipBattles/Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-09_engine_interface_split.md)

### 2. TD-02 - GameSession lifecycle extraction

This has the highest downstream leverage of the soft-preference items. It stabilizes construction and rehydration before facade cleanup and before the runtime production/persistence split.

[TD-02_game_session_lifecycle.md](C:/Developer/StarshipBattles/Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-02_game_session_lifecycle.md)

### 3. TD-03 - Order metadata convergence

This is the only hard prerequisite for `TD-07`, and it provides a live-view pattern that later metadata work should mirror rather than reinvent.

[TD-03_order_metadata_convergence.md](C:/Developer/StarshipBattles/Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-03_order_metadata_convergence.md)

### 4. TD-06 - ShipInstance slimming (Phases 0-4 only)

Do the safe upstream slimming work now:

- Phase 0: characterization / baseline
- Phase 1: stats cache extraction
- Phase 2: component inspector extraction
- Phase 3: factory + activation-store extraction
- Phase 4: write-path cleanup

Do **not** execute the cargo/deployable forwarder-demolition batch yet.

[TD-06_ship_instance_slimming.md](C:/Developer/StarshipBattles/Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-06_ship_instance_slimming.md)

### 5. TD-01 - Battle spec assembly pipeline

This stays ahead of the deployable redesign. The validated plan explicitly assumes TD-10 should not have to preserve the current private battle-spec side channels.

[TD-01_battle_spec_compilation.md](C:/Developer/StarshipBattles/Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-01_battle_spec_compilation.md)

### 6. TD-05 - Production / persistence split

This no longer has a hard dependency on TD-02 or TD-06, but it is still cleaner to run after both the lifecycle extraction and the safe `ShipInstance` slimming phases.

[TD-05_production_persistence_split.md](C:/Developer/StarshipBattles/Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-05_production_persistence_split.md)

### 7. TD-04 - Phase registry hooks

This no longer hard-depends on `TD-09`, but it still benefits from the interface split having already removed the monolithic contract file from the path.

[TD-04_phase_registry_hooks.md](C:/Developer/StarshipBattles/Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-04_phase_registry_hooks.md)

### 8. TD-07 - Ability metadata unification

Run only after `TD-03`. Nothing else blocks it.

[TD-07_ability_metadata_unification.md](C:/Developer/StarshipBattles/Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-07_ability_metadata_unification.md)

### 9. TD-08 - Facade API reduction

Run late. It is a broad caller-migration project, and it is cleaner after the lifecycle extraction and after the heavier internal churn has already settled.

[TD-08_facade_api_reduction.md](C:/Developer/StarshipBattles/Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-08_facade_api_reduction.md)

### 10. TD-10 - Deployable substrate redesign

Run after `TD-01` and after the safe early `TD-06` phases. This plan is the largest blast-radius change and should execute against a cleaner battle boundary and a slimmer `ShipInstance`.

[TD-10_deployable_substrate.md](C:/Developer/StarshipBattles/Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-10_deployable_substrate.md)

### 11. Return to TD-06 if cargo/deployable forwarder cleanup still remains

Only after `TD-10` Phase 1 is complete.

This is not a new plan. It is the deferred tail of `TD-06` that overlaps the deployable substrate.

## Parallelization Note

If multiple isolated worktrees are available, the safest parallel batches are:

- Batch A: `TD-09`, `TD-02`, `TD-03`, `TD-06` Phases 0-4
- Batch B: `TD-01`, `TD-05`, `TD-04`
- Batch C: `TD-07`, `TD-08`
- Final isolated batch: `TD-10`, then the deferred `TD-06` cargo/deployable cleanup if anything remains

Do **not** parallelize `TD-10` with another large cross-cutting plan.

## Why this differs from the earlier draft

The validated plans downgraded several earlier draft edges:

- `TD-09 -> TD-04` is a preference, not a blocker.
- `TD-02 -> TD-05` is a preference, not a blocker.
- `TD-06 -> TD-05` is not a real dependency.

The earlier draft also treated `TD-06` and `TD-10` as if one whole plan had to precede the other. That was too coarse. The validated plans only require a phase gate around the cargo/deployable cleanup batch, so this document now models that overlap directly.

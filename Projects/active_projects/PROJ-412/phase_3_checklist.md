# Phase 3: Migrate Harvest Booster Scan to Universal `IAbilitySource` Pipeline

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-412 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Make fleet-carried `ResourceHarvestBooster` actually affect harvesting by routing the booster scan through the universal `IAbilitySource` pipeline (`ability_iterator.py` → `FleetAbilitySource` + `FacilityAbilitySource` + …) instead of the planet/facility-only `find_abilities_in_scope`. This is a behavior change (fleet boosters become functional) that the user approved (decisions.md 2026-05-12 entry, Option B).

**Why this lives before Phase 4 (caching):** Phase 4 caches the booster scan results. The cache must be built around the new pipeline so its invalidation hooks correctly include fleet movement / ship destruction. Caching the old planet-only path and then migrating would mean reworking Phase 4 invariants.

**This phase changes game behavior.** Surface to user before merging.

---

## Tasks

### Task 3.1: Read current state and design the migration [Simple]

**File:** scratch under `AgentCoordination/Scratchpad/reports/proj-412-phase3-migration-plan.md`
**Tests:** n/a (design)

- [ ] Read [`game/strategy/services/strategic_ability_scanner.py:64-99`](../../../game/strategy/services/strategic_ability_scanner.py#L64) — the current `find_abilities_in_scope` planet-only path
- [ ] Read [`game/strategy/services/ability_iterator.py:261-339`](../../../game/strategy/services/ability_iterator.py#L261) — the universal `IAbilitySource` iteration
- [ ] Read [`game/strategy/services/ability_sources/fleet.py`](../../../game/strategy/services/ability_sources/fleet.py) — how `FleetAbilitySource` exposes ship abilities
- [ ] Read [`game/strategy/services/effect_ability_metadata.py:116-118`](../../../game/strategy/services/effect_ability_metadata.py#L116) — confirm `ResourceHarvestBooster` is registered as a passive multiplier in the effect metadata registry
- [ ] Read [`game/strategy/engine/harvesting_engine.py:388-419`](../../../game/strategy/engine/harvesting_engine.py#L388) — current `_get_harvest_booster_mult`
- [ ] Document the migration plan in the scratch report:
  - Which function changes (likely a new helper or rewriting `_get_harvest_booster_mult`)
  - Which scopes the new path supports (must include the 4 current scopes: planet, sector, system, empire)
  - How `aggregate_multipliers` is reused with the new entry format
  - What `require_active=True` semantics mean for fleet sources (active-ability requirement may differ between facility and fleet sources — codex consult noted activation flag is currently NOT passed by harvest path; preserve that or fix it deliberately)
- [ ] User checkpoint: surface the migration plan + behavior change (fleet boosters becoming functional) for explicit approval

**Notes:**

### Task 3.2: Add a characterization test that pins the *new* behavior [Medium]

**Files:** `tests/integration/strategy/turn_engine/test_mid_turn_invariants.py` (extends Phase 1.5 Test C) and / or `tests/unit/strategy/services/test_ability_iterator.py`
**Tests:** the new test must **fail** against the current (pre-migration) code, **pass** after Task 3.3 lands — strict TDD

- [ ] Write Test C in its fleet-carried form: a fleet with `ResourceHarvestBooster`-emitting component enters the planet's scope at tick 25 via `move_apply`; harvest at tick 26+ is scaled by the booster
- [ ] Run the test against current `main` — it MUST fail (proves the migration is necessary and Test C exercises the new behavior)
- [ ] Mark the test `xfail` with a clear message referencing Phase 3, OR comment-out and re-enable in Task 3.3 (pick one TDD style consistent with the project)
- [ ] Also add a facility-based positive control (booster facility at tick 25, scales tick 26+) so we have parity coverage

**Notes:**

### Task 3.3: Implement the migration [Complex]

**Files:** `game/strategy/engine/harvesting_engine.py`, possibly a new helper in `game/strategy/services/strategic_ability_scanner.py` or in `game/strategy/services/system_effects_collector.py` (pick the right home in design Task 3.1)
**Tests:** Task 3.2's Test C transitions from xfail → pass; all existing harvesting tests stay green

- [ ] Replace `_get_harvest_booster_mult`'s internals so it iterates `IAbilitySource` providers (which include both `FacilityAbilitySource` and `FleetAbilitySource`) for the 4 scopes, filters by ability key `ResourceHarvestBooster`, and feeds the entries through `aggregate_multipliers`
- [ ] Preserve scope semantics: planet, sector, system, empire (and any allied / player / enemy variants if currently supported)
- [ ] Preserve resource_type filtering (entry must match `resource_type`)
- [ ] Preserve the existing `aggregate_multipliers` semantics (intra-group MAX, inter-group MULTIPLY)
- [ ] Decide on `require_active=True`: current harvest path does NOT pass it; if you keep that semantic, document it. If you change it, that's another behavior change — surface to user
- [ ] Confirm `ResourceHarvestBooster` entries from `FleetAbilitySource` carry `resource_type` / `multiplier` / `stack_group` fields in the same shape as facility entries; if not, normalize at the boundary
- [ ] Run Task 3.2's Test C — must pass; run existing harvesting tests — must pass; run boss tests for `ability_iterator` and `system_effects_collector` — must pass
- [ ] Verify: bench `bench_turn_processing.py` shows the harvesting bucket is **not regressed** (we expect a small regression here pre-cache; Phase 4's cache reclaims it)

**Notes:**

### Task 3.4: Update docs for the behavior change [Simple]

**Files:** `docs/systems/strategy_layer.md`, `docs/systems/production_system.md`
**Tests:** n/a (doc)

- [ ] Update the harvest-booster section to state that fleet-carried boosters are now in scope via the universal `IAbilitySource` pipeline
- [ ] Cross-reference the existing `IAbilitySource` framework section (`docs/systems/strategy_layer.md:836-849`)
- [ ] If `docs/systems/production_system.md` has a harvest-booster aside, update it too
- [ ] Note this is a deliberate game-behavior change shipped as part of PROJ-412 Phase 3

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] Task 3.2's fleet-booster Test C is green
- [ ] All facility-booster tests still green (no regression in legacy path)
- [ ] `bench_turn_processing.py` total time within ~5% of Phase 2 baseline (we expect a small regression here that Phase 4 reclaims; if regression > 5%, surface to user)
- [ ] User approved the behavior change (fleet boosters becoming functional)
- [ ] `docs/systems/strategy_layer.md` updated
- [ ] No new save migration / fallback / compatibility shim
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4

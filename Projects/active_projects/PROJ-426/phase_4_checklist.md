# Phase 4: Migrate the adapter to `StrategyBattleAssembly` and remove side-channels

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-426 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_3
**Review Mode:** standard
**Files (planned):**
- `game/strategy/adapters/simulation_adapter.py` (edit — switch to assembly DTO)
- `tests/unit/strategy/adapters/test_simulation_adapter.py` (MIGRATE)
- `tests/integration/test_fms_b_e2e.py` (MIGRATE — pins `spec._mine_groups`, `spec._owner_to_team_id` at `:414, 415, 420, 493`)
- `tests/integration/strategy/combat/test_damage_persistence.py` (MIGRATE if integration regresses)
- `game/strategy/combat/spec_compiler.py` (edit — DELETE four `object.__setattr__(spec, ...)` writes — **last**)

**Objective:** Switch the runtime caller to the typed seam, then delete the legacy spec mutation. Phase 4 has a strict order:
1. Migrate adapter source.
2. Migrate the three test files that pin on private side-channels.
3. **Only then** delete the four `object.__setattr__(spec, ...)` writes in `spec_compiler.py`.

This phase ends with a full sharded suite run.

---

## Reading

- [ ] Re-read [TD-01 source plan §"Phase 4"](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-01_battle_spec_compilation.md).
- [ ] Read [design.md §"Test Migration Plan" Phase 4 row](design.md).
- [ ] Read [decisions.md row "Phase 4 deletion of object.__setattr__..."](decisions.md).
- [ ] Read `game/strategy/adapters/simulation_adapter.py:309-346` carefully — every side-channel read needs migration.
- [ ] Read `tests/integration/test_fms_b_e2e.py:414, 415, 420, 493`.

---

## Tasks

### Task 4.1: Add red adapter tests targeting the assembly DTO [Medium]
**File:** `tests/unit/strategy/adapters/test_simulation_adapter.py` (edit)
**Tests:** `pytest tests/unit/strategy/adapters/test_simulation_adapter.py -x`

- [ ] Add a test asserting the adapter reads `assembly.extensions.mine_groups` (will fail until adapter migrates).
- [ ] Add a test asserting the adapter reads `assembly.extensions.owner_to_team_id`.
- [ ] Add a test asserting the pre-tick callback the adapter passes to `run_battle(...)` comes from `assembly.pre_tick_setup.composed_callback()`.
- [ ] Update `tests/integration/test_fms_b_e2e.py:414, 415, 420, 493` to read `assembly.extensions.mine_groups` / `assembly.extensions.owner_to_team_id` instead of `spec._mine_groups` / `spec._owner_to_team_id`. (The test will fail in this state because the adapter hasn't migrated yet — that is the TDD red signal.)
- [ ] Run; confirm red.

**Notes:**

### Task 4.2: Migrate `simulation_adapter.py` to consume `StrategyBattleAssembly` [Complex]
**File:** `game/strategy/adapters/simulation_adapter.py`
**Tests:** Task 4.1 tests + existing adapter tests + `tests/integration/test_fms_b_e2e.py` + `tests/integration/test_fms_c_carrier_ai_launch.py`

- [ ] Rename `_build_spec` → `_build_assembly` (or equivalent) — it now returns `StrategyBattleAssembly`, not raw `BattleSpec`.
- [ ] `run_battle(...)` still receives `assembly.spec` for the engine API; pre-tick callback comes from `assembly.pre_tick_setup.composed_callback()`.
- [ ] Replace every read of `_mine_groups`, `_owner_to_team_id`, `_combat_fleets`, `_engine_ref` with the corresponding `assembly.extensions.*` accessor.
- [ ] Remove the conditional imports of `build_mine_resolver_setup` / `build_fighter_reboard_setup` that used to wire side-channels — the registry now owns this.
- [ ] Remove the `_compose_setup_callbacks` helper if it is no longer needed (`PreTickBattleSetupRegistry.composed_callback` replaces it).
- [ ] Run Task 4.1 tests + existing adapter tests + the two FMS integration tests; confirm green.

**Notes:**

### Task 4.3: Delete the four `object.__setattr__(spec, ...)` writes [Simple]
**File:** `game/strategy/combat/spec_compiler.py`
**Tests:** Full sharded suite

- [ ] Confirm Tasks 4.1 and 4.2 are complete and green.
- [ ] Confirm `tests/integration/test_fms_b_e2e.py:414, 415, 420, 493` has been migrated (Task 4.1).
- [ ] Confirm `tests/integration/strategy/combat/test_damage_persistence.py` is green at HEAD.
- [ ] Delete the four lines at `spec_compiler.py:271, 272, 278, 279` (or current equivalents) — the writes for `_mine_groups`, `_owner_to_team_id`, `_engine_ref`, `_combat_fleets`.
- [ ] If `build_strategy_battle_assembly(...)` was previously reading the side-channels off the spec (Phase 1's compat path), refactor it to populate `BattleSpecExtensions` directly from the input/intermediate state — the spec mutation no longer happens.
- [ ] Run focused suite first; confirm green.

**Notes:**

### Task 4.4: Full sharded suite at the Phase 4 boundary [Complex]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run the full sharded suite.
- [ ] Confirm green.
- [ ] **Grep gates:**
  ```bash
  rg "object\.__setattr__\(spec" game tests   # expect zero hits
  rg "getattr\(spec, ['\"]_" game tests        # expect zero hits
  ```
- [ ] If either grep returns hits, stop and surface — the migration is incomplete.

**Notes:**

### Task 4.5: Commit Phase 4 [Simple]
**File:** N/A
**Tests:** N/A

- [ ] `git status --short` confirms only Phase 4 files dirty.
- [ ] Commit: `PROJ-426 phase 4: migrate adapter to StrategyBattleAssembly + remove BattleSpec side-channels`.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All Phase 4 task checkboxes checked.
- [ ] Adapter consumes `StrategyBattleAssembly`; no `getattr(spec, "_...")` calls remain.
- [ ] `rg "object\.__setattr__\(spec" game tests` returns zero hits.
- [ ] `rg "getattr\(spec, ['\"]_" game tests` returns zero hits.
- [ ] `tests/integration/test_fms_b_e2e.py` line 414/415/420/493 references migrated to `assembly.extensions.*`.
- [ ] Full sharded suite green.
- [ ] Update status at top of this file to `Complete`.
- [ ] Update plan.md phase table row to `Complete`.
- [ ] Update plan.md Current State to point to Phase 5.

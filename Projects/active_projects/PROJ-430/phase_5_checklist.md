# Phase 5: Delete the legacy surface (root-cause, no shims)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-430 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_4
**Review Mode:** standard
**Files (planned):**
- `game/strategy/facade/strategy_session_facade.py` (delete the flat surface, cache forwarders, legacy alias)
- `game/strategy/facade/slices/command_dispatch_slice.py` (only if the flat-helper installer is still embedded there)

**Objective:** Delete the 8 cache-forwarder `@property` blocks, the 32 flat read-method forwarders, the auto-installer's `dispatch_*` setattr loop, and the `_resolve_economy_config` legacy alias. After this phase, the two Phase-1 contract assertions (`test_no_legacy_flat_methods`, `test_legacy_cache_attrs_removed`) go green. Final validation: the full sharded suite.

---

## Tasks

### Task 5.1: Delete the cache-forwarder `@property` blocks [Medium]
**File:** `game/strategy/facade/strategy_session_facade.py`
**Tests:** `pytest tests/unit/strategy/facade -q` after the edit

- [ ] Delete the entire `# preserved for legacy tests` block at lines 114-164. That removes the 8 `@property` halves (get + set) on the 6 underlying fields:
  - `_planet_index`
  - `_all_stars_cache`
  - `_all_stars_cache_turn`
  - `_fleets_by_hex_cache`
  - `_fleets_by_hex_turn`
  - `_race_registry`
- [ ] Confirm no remaining callable also referenced these `@property` halves (`rg "self\._planet_index\b" game/strategy/facade/strategy_session_facade.py` etc.). The underlying fields on `FacadeSessionState` are unchanged — only the facade-level forwarders go away.
- [ ] Run the contract test:
  ```
  pytest tests/unit/strategy/facade/test_strategy_session_facade_public_api.py::test_legacy_cache_attrs_removed -q
  ```
  Expected: green.

**Notes:** [Filled during implementation. Per AGENTS.md rule 3: root-cause delete, no parallel old + new path.]

### Task 5.2: Delete the 32 flat read-method forwarders [Medium]
**File:** `game/strategy/facade/strategy_session_facade.py`
**Tests:** `pytest tests/unit/strategy/facade -q` + `pytest tests/unit/ui tests/integration -x`

- [ ] Delete each of the 32 flat read-method definitions on `StrategySessionFacade` (e.g. `get_fleet`, `get_fleets_at_hex`, `get_planet`, `get_star`, `get_empire`, `get_event`, `get_turn_number`, `get_save_path`, `get_human_player_ids`, `get_race_registry`, `get_colony_demographic_view`, `can_colonize`, `can_move_to`, and the rest of the 32).
- [ ] Source the exhaustive list from `LEGACY_FLAT_METHODS` (the frozen constant captured during Phase 1 Task 1.3 rewrite). Delete each name from the facade.
- [ ] After each batch of deletions, run:
  ```
  pytest tests/unit/ui tests/integration -x
  ```
  Any failure means a missed UI caller in Phase 3 — find it via the failure traceback, migrate it (per Phase 3's rename table), and retry. **Do not re-add the deleted method as a shim** — AGENTS.md rule 3.
- [ ] Run the contract test:
  ```
  pytest tests/unit/strategy/facade/test_strategy_session_facade_public_api.py::test_no_legacy_flat_methods -q
  ```
  Expected: green (or one step closer to green; finish all 32 deletions to fully clear).

**Notes:** [Filled during implementation. Per the TD-08 weak-LLM guardrail: no compat shims; the grouped API is transitional only until callers are migrated, and Phase 3 already migrated them.]

### Task 5.3: Delete the `dispatch_*` auto-installer setattr loop [Simple]
**File:** `game/strategy/facade/strategy_session_facade.py`
**Tests:** `pytest tests/unit/strategy/facade tests/unit/ui tests/integration -q`

- [ ] Delete the auto-installer block at `strategy_session_facade.py:448-477` (the `_install_dispatch_forwarders` loop that calls `setattr(self, 'dispatch_<verb>', ...)` for each registry entry).
- [ ] Keep `command_registry.specs_by_facade_helper()` intact — it now feeds `FacadeCommands` instead of the auto-installer. The registry itself does not change.
- [ ] If `command_dispatch_slice.py` still embeds flat-helper installer logic, delete that too. Otherwise leave the slice untouched.
- [ ] Run focused suites; expected: green except possibly the final Phase 1 assertion that this task helps satisfy.

**Notes:** [Filled during implementation]

### Task 5.4: Delete `_resolve_economy_config` legacy alias [Simple]
**File:** `game/strategy/facade/strategy_session_facade.py`
**Tests:** `rg "_resolve_economy_config" game/ tests/` -> expected zero hits

- [ ] Verify zero remaining external callers:
  ```
  rg -n "_resolve_economy_config" game/ tests/
  ```
  Expected: matches only inside `strategy_session_facade.py` itself (the soon-to-be-deleted alias) and possibly `economy_slice.py:75` (the warning-log fallback comment).
- [ ] Delete the `_resolve_economy_config` method at `strategy_session_facade.py:372-374`.
- [ ] **TD-02 coupling decision** — record in `decisions.md`:
  - If PROJ-423 (TD-02) has landed and the shared bootstrap/rehydration path means `economy_config` is always populated cleanly, also remove the warning-log fallback at `economy_slice.py:75`.
  - If TD-02 has not landed, keep the fallback inside `FacadeEconomyQueries.resolve_config()` as documented carried debt. Annotate with a `TODO(TD-02)` comment so it surfaces when TD-02 ships.
- [ ] Re-run:
  ```
  rg -n "_resolve_economy_config" game/ tests/
  ```
  Expected: zero hits.

**Notes:** [Filled during implementation]

### Task 5.5: Confirm the full Phase 1 contract test is green [Simple]
**Files:** none (verification)
**Tests:** the rewritten contract test

- [ ] Run:
  ```
  pytest tests/unit/strategy/facade/test_strategy_session_facade_public_api.py -q
  ```
  Expected: **all** Phase 1 assertions green now (`test_only_target_top_level_callables_exist`, `test_only_target_top_level_attrs_exist`, `test_no_legacy_flat_methods`, `test_grouped_namespaces_expose_expected_methods`, `test_legacy_cache_attrs_removed`).
- [ ] Compare against `findings/phase_1_red_baseline.md` — every documented red flips to green. Any failure left over is a missed deletion; investigate via the failure traceback.

**Notes:** [Filled during implementation]

### Task 5.6: Run focused facade + UI + integration suites [Simple]
**Files:** none (verification)
**Tests:** focused suites

- [ ] Run:
  ```
  pytest tests/unit/strategy/facade tests/unit/ui tests/integration/strategy -q
  ```
  Expected: fully green. Any failure here is a missed UI caller from Phase 3 or a missed test migration from Phase 4.

**Notes:** [Filled during implementation]

### Task 5.7: Run the canonical sharded suite [Complex — bound by suite runtime]
**Files:** none (verification)
**Tests:** full sharded suite

- [ ] Run:
  ```
  python Tools/test_sharded/test_sharded.py
  ```
- [ ] Expected: green. This is the canonical final validation per CLAUDE.md.
- [ ] If the sharded suite surfaces a regression not caught by focused suites, investigate via the failing shard's output. Root-cause fix per AGENTS.md — do not add a compat shim to make the test pass.

**Notes:** [Filled during implementation. Sharded-suite wall-clock runtime is a real bottleneck — minutes, not seconds. Plan accordingly.]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All 8 cache-forwarder property halves deleted
- [ ] All 32 flat read-method forwarders deleted
- [ ] `dispatch_*` auto-installer setattr loop deleted; `specs_by_facade_helper()` survives and feeds `FacadeCommands`
- [ ] `_resolve_economy_config` deleted; `rg` confirms zero remaining hits
- [ ] TD-02 coupling decision recorded in `decisions.md` (warning-log fallback removed vs. carried as documented debt)
- [ ] Phase 1 contract test fully green; compared against `findings/phase_1_red_baseline.md`
- [ ] Focused facade + UI + integration suites green
- [ ] `python Tools/test_sharded/test_sharded.py` green
- [ ] `python Projects/scripts/validate_phase.py PROJ-430 5` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6

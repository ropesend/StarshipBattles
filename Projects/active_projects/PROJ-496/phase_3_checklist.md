# Phase 3: Audit remediation (Codex consult 2026-05-23)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-496 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address verified in-scope findings from the Codex mid-project review. See `findings/audit_verification.md` for the full verification table and `AgentCoordination/Scratchpad/Consult/20260523T154936Z_audit-PROJ-496/response.md` for the raw audit.

---

## Tasks

### Task 3.1: Tighten persistence_adapter schema guard to match its docstring
**File:** `tests/unit/strategy/engine/session/test_persistence_adapter.py`
**Tests:** `pytest tests/unit/strategy/engine/session/test_persistence_adapter.py`

The test at lines 96-151 (`test_serialize_matches_frozen_schema_fixture`) advertises "top-level keys, nested key sets, and the intended values per slot" in its docstring (line 108) but the actual assertions only check (a) the top-level `_EXPECTED_SAVE_KEYS` exact set, (b) per-field individual `config[<key>] == <value>` asserts, (c) per-field individual `players[i][<key>] == <value>` asserts. Two gaps:
1. **`save_name` not asserted** despite `GameConfig.to_dict()` emitting it at `game/strategy/engine/game_config.py:243`. A rename or removal of `save_name` would pass silently.
2. **Nested key sets not asserted** — only individual keys are spot-checked. A new optional key added to `config` or `players[i]` would pass silently; a removed key would only fail if it happened to be one of the spot-checked ones.

PROJ-480 T4.1 (`Projects/archived_projects/PROJ-480/phase_4_checklist.md:15-20`) asked for "stable subset" relaxation against the previous 35-line literal dict — the goal was avoiding test churn from unrelated downstream defaults, NOT removing the schema guard's structural shape check.

- [x] Add `_EXPECTED_CONFIG_KEYS = {"asset_base_path", "galaxy_radius", "system_count", "galaxy_type", "galaxy_seed", "save_name", "players"}` near the existing `_EXPECTED_SAVE_KEYS`.
- [x] Add `_EXPECTED_PLAYER_KEYS` containing every key emitted by `PlayerConfig.to_dict()` — read `game/strategy/engine/game_config.py` to get the canonical set (likely `{"name", "theme", "color", "is_human"}` plus any optional fields).
- [x] In `test_serialize_matches_frozen_schema_fixture`, after the existing top-level key check, add `assert set(config.keys()) == _EXPECTED_CONFIG_KEYS`.
- [x] Add `assert config["save_name"] == <expected-value>` where the expected value comes from `_frozen_fixture_session()` (read the fixture and use whatever save_name it sets — likely `None` or a fixture-specific string).
- [x] After the existing players length check, add `assert set(players[0].keys()) == _EXPECTED_PLAYER_KEYS` and `assert set(players[1].keys()) == _EXPECTED_PLAYER_KEYS`.
- [x] Update the docstring at lines 96-112 to accurately describe the new contract: top-level key set, nested key sets (config, per-player), AND the intended values per spot-checked slot. Drift in *any* of those three layers fails the test; drift in *unnamed* leaf values (e.g., a new optional field defaulting to None) still passes by design.
- [x] Verify: tests pass; LOC delta ≈ +6.

### Task 3.2: T1.8 retry — replace happiness re-derivation with precomputed expected
**File:** `tests/unit/strategy/formulas/test_colony_output.py`
**Tests:** `pytest tests/unit/strategy/formulas/test_colony_output.py`

`test_high_happiness_scales_logistic_term` at lines 436-451 calls `projected_growth_rate(...)` twice (happiness=1.0 and happiness=2.0) and asserts `rate_giddy == pytest.approx(rate_normal * 2.0, rel=1e-9)`. This is the relational re-derivation PROJ-480 T5.17 (`Projects/archived_projects/PROJ-480/phase_5_checklist.md:127-132`) explicitly targeted: "Replace internal re-derivation of `happiness 2.0 → 2× rate` (lines 436-451, `rel=1e-9` tolerance) with pre-computed expected value from formula documentation. Test external value, not re-derived logic."

The implementer's Phase 0 drop ("relational scaling check, not formula re-derivation") doesn't match the task — calling production twice and comparing ratios is exactly re-derivation.

- [x] Read `game/strategy/formulas/colony_output.py` to confirm the formula. The docstring at the test's lines 437-439 says happiness scales the logistic term linearly, with `max(0, happiness)` defensive floor.
- [x] Compute the expected `rate_giddy` value offline for the fixture inputs (race human, pop count=10, happiness=2.0, max_pop=1_000_000, food_ratio=1.0). Document the derivation in a single comment block (similar style to PROJ-323 Task 5.18 derivation comments seen in `test_resupply_engine.py`).
- [x] Replace the assertion at line 451 with `assert rate_giddy == pytest.approx(<precomputed_value>, rel=1e-9)`. The precomputed value should NOT call `projected_growth_rate` — it should be a literal float.
- [x] Keep or remove the `rate_normal` computation as needed. If kept, demote it to a documentation aid (e.g., `# Sanity: rate_normal would be <expected_normal_value>`) but don't use it in the assertion.
- [x] Update the test docstring to reflect that the assertion now pins the external formula value, not a relational ratio.
- [x] Verify: tests pass; LOC delta ≈ +2-3.

### Task 3.3: T1.5 retry — consolidate hardcoded-count loop tests via parametrize
**File:** `tests/unit/simulation/systems/test_battle_engine_tick.py`
**Tests:** `pytest tests/unit/simulation/systems/test_battle_engine_tick.py`

PROJ-480 T5.4 (`Projects/archived_projects/PROJ-480/phase_5_checklist.md:36-41`) asked to consolidate the 2 loop-with-hardcoded-count tests at lines 610-617 (`test_multiple_ticks_increment_counter`, n=10) and lines 740-748 (`test_rapid_succession_ticks`, n=100) into `@pytest.mark.parametrize("n", [1, 10, 100])`. Both pin the same `tick_counter == n` contract; the second adds `engine.end_condition = TickLimitCondition(max_ticks=1000)` so the higher loop count terminates cleanly.

The implementer's Phase 0 drop ("different-class loop tests, intent diverges") is weak — Codex audit flagged it as a stylistic skip rather than a defensible architectural call. Low priority but mechanical.

- [x] Consolidate the 2 tests into one parametrized test. Recommend placing it in `TestMultipleTicks` class (where the first lives) and deleting the standalone second test.
- [x] Use `@pytest.mark.parametrize("n", [1, 10, 100])` and set `engine.end_condition = TickLimitCondition(max_ticks=n + 1)` (or a value safely above n) inside the test body so all three n values terminate cleanly. Verify the import of `TickLimitCondition` is already in scope or add it.
- [x] Preserve both docstrings' intent in a single one-liner.
- [x] Verify: tests pass; LOC delta ≈ -10.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Phases 0-3 Complete" (no Phase 4 planned)

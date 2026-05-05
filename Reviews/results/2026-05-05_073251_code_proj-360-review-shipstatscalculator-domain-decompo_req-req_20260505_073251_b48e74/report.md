# Review Report: PROJ-360 ShipStatsCalculator Domain Decomposition

**Review Type:** code (delegated by Claude Code)
**Request ID:** req_20260505_073251_b48e74
**Scope:** `game/simulation/entities/ship_stats.py`, `stat_contributors/` package, golden snapshot tests, contributor unit tests, `docs/02_PATTERNS.md` §35
**Review Mode:** normal (full code review)
**Limitations:** None. All scope files read in full. Four parallel review agents completed successfully.
**Date:** 2026-05-05

---

## Executive Summary

PROJ-360 successfully reduced `ship_stats.py` from 643 to 495 LOC (under the 500 LOC ceiling) by decomposing per-domain aggregation into a `stat_contributors/` package and adding a `STAT_CONTRIBUTOR_REGISTRY` extension point. The public `calculate()` API is unchanged, golden snapshot tests pass bit-for-bit, and the acceptance test proves the registry path works end-to-end.

**However, the extension story has a significant gap: the registry runs *alongside* built-in contributors rather than *instead of* them.** Registering a contributor for an ability already handled by a built-in domain (e.g., `ShieldProjection`) causes **double-counting** at runtime. The acceptance test papercuts past this by testing a non-stat-modifying contributor — it proves "does the hook fire?" but not "does the hook fire correctly?"

---

## Finding Totals

| Severity | Count |
|----------|-------|
| CRIT     | 2     |
| MAJ      | 11    |
| MIN      | 15    |
| NIT      | 11    |
| **Total**| **39** |

---

## Instruction-by-Instruction Response

### 1. Verify `ship_stats.py` is < 500 LOC and `calculate()` API is unchanged

**PASS.** Confirmed at 495 lines. The `ShipStatsCalculator.calculate(ship)` signature is `(self, ship: "Ship") -> None`, unchanged. Legacy passthroughs `calculate_ability_totals` and `_priority_sort_key` are preserved.

### 2. Confirm golden snapshot covers all 7 designs and floats are deterministically normalized

**PARTIAL PASS.** The 7 designs (`qs_escort`, `qs_general_purpose`, `qs_frigate_gc`, `qs_heavy_cruiser`, `qs_battleship`, `qs_missile_cruiser`, `qs_warp_gate_opener`) are parametrized and compared with `math.isclose(abs_tol=1e-9)`. Float normalization uses `round(value, 12)` — adequate.

**Gaps found:**
- Launch/hangar domain is entirely uncovered (all 7 designs have `fighter_capacity: 0`) — **MAJ**
- Combat endurance fields (12 fields from `calculate_combat_endurance`) are not captured in the snapshot — **MAJ**
- MultiplexTracking is not exercised by any golden design — MIN
- `baseline_to_hit_offense` is 0 for 6 of 7 designs — NIT

### 3. Audit the STAT_CONTRIBUTOR_REGISTRY extension surface

**FAIL (CRIT).** The registry works mechanically but has two critical design issues:

- **EXT-01 [CRIT]:** Same ability registered in multiple domains causes silent double-counting at runtime. The `domain` field gates dedup but not execution.
- **EXT-12 [CRIT]:** Registered contributors mutate `ship` directly while built-in contributors use the `acc` dict — inconsistent mutation surface with no guardrails.

Additionally:
- **EXT-02 [MAJ]:** Built-in and registered contributors both fire for the same ability with no mutual exclusion.
- **EXT-11 [MAJ]:** Built-in domains cannot be extended without code edits — the pipeline is a two-tier system.

### 4. Confirm acceptance test really exercises the registry path

**PASS (with MIN note).** `test_fake_contributor_runs_for_a_ship_with_matching_ability` registers via `register_stat_contributor("ShieldProjection", ...)`, runs `ship.recalculate_stats()`, and verifies invocations. The `test_contributor_only_runs_on_operational_components` test correctly verifies the `is_operational` gating.

**However:** The test has docstring/code/assertion-message mismatches (ShieldProjection vs ShieldRegeneration) — **MIN**. It tests on `ShieldProjection` which is also handled by the built-in `defense` contributor, meaning it tests the double-fire path without checking stat integrity.

### 5. PROJ-359 AttackRequest contract rationale

**PASS.** The rationale in `weapons.py:17-23` is sound:
- `AttackRequest` describes a single weapon firing event (per-shot inputs: `source`, `component`, `weapon_ability`, `target`, `aim_pos`, `aim_vec`).
- `aggregate_targeting_scores` computes ship-wide totals (ECM/sensor) across all components — these are pre-fire aggregates.
- ECM/sensor scores are inputs to hit-probability calculation, not outputs of resolution.
- `AttackRequest` carries no field for `ToHitDefenseModifier` or `ToHitAttackModifier` totals — it carries a single component, not a component pool.

### 6. Hidden coupling between contributors

**PASS (no hidden coupling found).** All contributors write to independent domains:
- `movement` → `acc` only (thrust, turn_speed, warp, strategic_movement)
- `defense` → `acc` (shields) + `ship.layers[ARMOR]` (armor pool side-channel)
- `command` → `ship.max_targets` + component status
- `launch` → `ship.fighter_capacity`, `fighters_per_wave`, `fighter_size_cap`, `launch_cycle`
- `weapons` → `ship.baseline_to_hit_offense` + returns ECM score

No contributor reads state written by another contributor in the same pass. The accumulator (`acc`) isolates built-in contributors from each other. The phase ordering (movement/defense in Phase 3, weapons in Phase 5) mirrors the legacy structure.

**Architectural concerns (not coupling bugs):**
- Mixed mutation surfaces (some use `acc`, some use `ship` directly) — NIT
- Asymmetric invocation points (Phase 3 vs Phase 5) — NIT

### 7. Audit `get_abilities('X')` calls in contributors

**PASS (with MAJ findings).** All 10 `get_abilities('X')` calls are typed-attribute reads (`.thrust_force`, `.capacity`, `.rate`, `.amount`, `.movement_points`, `.turn_rate`, `.max_tonnage`, `.energy_cost`, `.cargo_type`, `.capacity`). No dispatch checks (i.e., no `isinstance` class checks against ability types).

**Issues found:**
- **EXT-05 [MAJ]:** Shield energy cost extraction scans ALL ability instances via `comp.ability_instances` after confirming `has_ability("ShieldRegeneration")` — should use `get_abilities("ResourceConsumption")` instead.
- **EXT-07 [MAJ]:** Five ability types (`Armor`, `MultiplexTracking`, `VehicleLaunch`, `VehicleStorage`, `PodStorage`) bypass the typed system entirely via raw `comp.abilities.get()` dict access.
- `is_warp_jump()` structural guard in `movement.py` may mask an indexing gap — MIN.

---

## All Findings

### Critical

| ID | Title | File | Line | Agent |
|----|-------|------|------|-------|
| EXT-01 | Same ability in multiple domains causes silent double-counting | `registry.py` | 181-193 | Extensibility |
| EXT-12 | Registered contributors mutate `ship` directly vs built-in `acc` dict — inconsistent mutation surface | `ship_stats.py` | 258-267, `registry.py` 191-193 | Extensibility |

### Major

| ID | Title | File | Line | Agent |
|----|-------|------|------|-------|
| FM-01 | `aggregate_targeting_scores` return type annotated `-> None` but returns float | `weapons.py` | 36 | Code Quality |
| A1 | Registry mutable state has no root conftest reset (test-leak risk on crash) | `registry.py` | 57, 146 | Architecture |
| C1 | `STAT_CONTRIBUTOR_REGISTRY` uses list (O(n)) vs dict-based registry pattern | `registry.py` | 146, 181-193 | Architecture |
| EXT-02 | Built-in and registered contributors both fire for same ability with no mutual exclusion | `ship_stats.py` | 258-267 | Extensibility |
| EXT-05 | Shield energy cost scans all ability instances instead of using `get_abilities("ResourceConsumption")` | `defense.py` | 53-57 | Extensibility |
| EXT-07 | Five ability types bypass typed system via raw dict access | `launch.py`, `command.py`, `defense.py`, `ship_stats.py` | 35-36, 49, 40, 201,207,312 | Extensibility |
| EXT-11 | Built-in domains require code edits for new ability handling — not a unified extension model | `ship_stats.py` | 258-266 | Extensibility |
| FIND-001 | Launch/hangar domain not exercised by any golden design | `test_ship_stats_golden.py` | 46-54 | Test Quality |
| FIND-002 | Combat endurance fields (12 fields) not captured by snapshot | `test_ship_stats_golden.py` | 94-177 | Test Quality |
| FIND-003 | No dedicated unit test for `_phase_damage_check_and_supply` edge cases | `ship_stats.py` | 187-220 | Test Quality |
| FIND-004 | No unit test for `_initialize_resources` delta-update path | `ship_stats.py` | 450-483 | Test Quality |

Note: Some findings overlap across agents (A1 ≈ EXT registry mutability concern, C1 ≈ EXT-03 registry performance).

### Minor

| ID | Agent |
|----|-------|
| FM-02 — Unused imports `Dict`/`Optional` in `registry.py` | Code Quality |
| FM-03 — Redundant `max_mass_budget` computation (Phase 2 + Phase 4) | Code Quality |
| FM-04 — Module-level mutable list with `global` keyword for cleanup | Code Quality |
| FM-05 — `_get_or_resolve_planetary_ids` returns bare `list` | Code Quality |
| A2 — Registered contributors can't read `acc` dict | Architecture |
| EXT-03 — `apply_registered_contributors` unbounded linear scan per component | Extensibility |
| EXT-06 — `is_warp_jump()` guard may mask indexing gap | Extensibility |
| EXT-09 — `lookup_crew_priority` O(n) with no index | Extensibility |
| EXT-10 — Both registries use O(n) duplicate checks | Extensibility |
| EXT-13 — `acc` dict keys are string literals with no validation | Extensibility |
| FIND-005 — MultiplexTracking not exercised by golden designs | Test Quality |
| FIND-006 — Acceptance test docstring/code mismatch (ShieldProjection vs ShieldRegeneration) | Test Quality |
| FIND-007 — `test_unregister_returns_to_default` leaks on assertion failure | Test Quality |
| FIND-008 — No unit test for `_aggregate_cargo_and_pod_abilities` | Test Quality |
| FIND-009 — No unit test for `_phase_physics_and_limits` zero-mass branch | Test Quality |

### Nit

| ID | Agent |
|----|-------|
| FM-06 — `__init__.py` uses absolute self-import | Code Quality |
| FM-07 — `_check_mass_limits` missing docstring | Code Quality |
| A3 — Asymmetric invocation points (Phase 3 vs Phase 5) | Architecture |
| A4 — Mixed mutation scope across contributors | Architecture |
| C3 — No `reset_all()` helper for registries | Architecture |
| E1 — Ambiguous comment about reverted `capacity_mult` read | Architecture |
| E2 — `isinstance(dict)` guard skips legit non-dict `external_stats` | Architecture |
| EXT-04 — `domain` field semantics split between documentation and usage | Extensibility |
| EXT-08 — All ability name strings are hardcoded literals | Extensibility |
| EXT-14 — "Not a stable API" disclaimer contradicts registry's public API role | Extensibility |
| FIND-010 — ECM sensor offense exercised by only 1 golden design | Test Quality |

---

## Suggested Remediation Priority

1. **EXT-01 + EXT-02 [CRIT + MAJ]:** Fix the double-counting risk. Either:
   - Make dedup per-ability (not per-domain), or
   - Have a registered contributor suppress the built-in handler for the same ability.
   - Add a test that registers a contributor for `ShieldProjection`, recalculates, and asserts `max_shields` is NOT double-counted.

2. **EXT-12 [CRIT]:** Pass `acc` to registered contributors so they participate in the accumulate-then-commit pattern, consistent with built-in contributors.

3. **FM-01 [MAJ]:** Fix `aggregate_targeting_scores` return type (`-> float`).

4. **FIND-001 + FIND-002 [MAJ]:** Add a carrier design to golden snapshots and capture endurance fields.

5. **EXT-07 [MAJ]:** Give `MultiplexTracking`, `VehicleLaunch`, `VehicleStorage`, `PodStorage` typed ability classes.

6. **A1 [MAJ]:** Add registry reset to root conftest to prevent test pollution.

---

## Verdict

The decomposition is structurally sound: layer boundaries are clean, the golden baseline is preserved, and the registry mechanism works mechanically. The critical issues are in the **extension boundary semantics** (double-counting, inconsistent mutation surfaces) — the registry exists but doesn't safely compose with the built-in pipeline. These are fixable with targeted changes to `registry.py` and `ship_stats.py` without restructuring the decomposition.

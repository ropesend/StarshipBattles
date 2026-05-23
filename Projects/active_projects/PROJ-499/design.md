# PROJ-499: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

The snapshot harness at `tests/regression/modifier_ability_snapshots/conftest.py:147-173` defines `compare_snapshots(actual, expected)`. The body iterates `for key in expected_val` and never reports keys present only in `actual`. This means the only signal the harness emits is:

- a key the baseline expects but is missing from live output
- a leaf-value mismatch where the key is present in both

It is asymmetric. The actual-only direction is silent. PROJ-489 exploited this (unintentionally) when it re-shot 7 baselines that picked up 4 new `StatKey` enum members (`launch_rate_mult`, `recovery_rate_mult`, `bay_capacity_mult`, `shield_bonus_add`); the comparator did not fire on the other 58 baselines because their expected JSON does not mention those keys, so the iteration never reached them.

### Spot evidence
- `tests/regression/snapshots/crew_quarters_automation_0.25.json` (PROJ-489 reshot, contains 4 new keys at the `component.stats` level)
- `tests/regression/snapshots/crew_quarters_automation_0.00.json` (unchanged sibling, does NOT contain those keys)
- `tests/regression/snapshots/railgun_no_modifiers.json` (unchanged, also missing the 4 keys, confirming this is not crew-quarters-specific)
- `game/simulation/components/abilities/stat_keys.py:103-114` `create_default_stats_dict()` iterates every enum member, so live output emits these keys for every component snapshot regardless of family.

### Survey of other harnesses
Per Codex finding 1-2 in `AgentCoordination/Scratchpad/Consult/20260523T125809Z_plan-snapshot-harness-fix/response.md`:

| Harness | Symmetric? | Evidence |
|---------|-----------|----------|
| `tests/regression/modifier_ability_snapshots/conftest.py` | **NO** (the gap) | lines 147-156 |
| `tests/infrastructure/deep_compare.py` | yes (unions key sets) | lines 77-106 |
| `tests/infrastructure/state_snapshot.py` | yes (delegates to deep_compare) | lines 38-66 |
| `tests/integration/save_load/conftest.py` + `test_full_roundtrip.py` | yes (deep_compare) | lines 68-108, 81-100 |
| `tests/integration/strategy/test_save_round_trip.py` | yes (strict dict equality) | lines 222-231 |
| `tests/integration/strategy/test_galaxy_reproducibility.py` | yes | lines 40-45 |
| `tests/unit/simulation/entities/test_ship_stats_golden.py` | yes (explicit key-set equality) | lines 261-275, 315-325 |
| `tests/integration/strategy/test_golden_fixture_field_coverage.py` | yes | lines 65-86 |

Only the modifier-ability snapshot harness has the gap. No propagation needed.

## Fix Strategy

### Considered options (Codex consult)

1. **Strict set-equality (chosen)** — make `compare_snapshots()` walk the union of `actual.keys() | expected.keys()` at every dict level. Extra-in-actual → diff like "extra key in actual". One-time pain: every existing baseline that does not match the current live schema fails. Long-term: future schema additions become deliberate, reviewed re-baseline events.

2. **Configurable allowlist (rejected)** — per-snapshot opt-in list of keys allowed to be missing from baseline. Pros: no bulk re-shoot. Cons: re-encodes the exact escape hatch that let PROJ-489's drift survive; turns schema drift into config churn; allowlist sprawl over time. (Codex response.md:31.)

3. **Schema-versioned snapshots (rejected)** — baseline declares a schema version; harness refuses to compare across versions. Pros: explicit. Cons: still does not solve the immediate stale-baseline problem; mostly formalizes future bulk rewrites; adds writer/loader metadata. (Codex response.md:32.)

4. **Hybrid: narrowed snapshot projection (rejected for this project)** — snapshot only behaviorally-relevant fields instead of the raw `component.stats` dict; then strict equality on the projection. Pros: no bulk re-shoot. Cons: changes the snapshot CONTRACT (what we are actually pinning). Decided in decisions.md to keep the existing contract and accept the one-time cleanup. (Codex response.md:34.)

### Re-baseline impact estimate

65 baselines under `tests/regression/snapshots/`. Categories (file-name prefix):
- `capital_missile_*` (18 files)
- `crew_quarters_automation_*` (5 files)
- `generator_efficiency_*` (4 files)
- `laser_cannon_*` (7 files)
- `railgun_*` (24 files)
- `standard_engine_*` (6 files)
- `thruster_*` (1 file)

After Phase 2's tightening, essentially all of these will fail because live output now emits the 4 new `StatKey` keys that none of the 58 unchanged baselines contain. (Phase 0 verifies exact count.) Phase 3 deletes all 65 and lets `fail_missing_baseline()` regenerate them, then commits after spot-checking ~5-7 representatives (one per category).

The re-baseline diff is BOUNDED: it should add the 4 default-valued keys to `component.stats` and nothing else. Any structural change beyond that is a real regression and must be investigated, not bulk-accepted.

## Tests
- **Phase 1 (TDD)** — `tests/regression/modifier_ability_snapshots/test_compare_snapshots_strictness.py` (new) — comparator-level unit test. Two cases: (a) extra key at top-level dict, (b) extra key inside nested `abilities[i]`. Must FAIL against current `compare_snapshots()`; must PASS after Phase 2.
- **Phase 4** — Same test file gains a negative guard: load a real baseline file, add an extra key in memory, run `compare_snapshots()`, and assert it returns a diff describing the extra key. Pins comparator strictness against future regressions.

## Risks
- **Risk: more than the 4 known keys are missing from baselines.** Mitigation: Phase 0 prototypes the symmetric comparator and runs the full suite once; the failure log enumerates EVERY missing key. If categories beyond `stat_keys.py` enum additions surface (e.g., new ability classes), Phase 3 widens its spot-check.
- **Risk: a true semantic regression hides inside the re-baseline diff.** Mitigation: spot-check one file per category (7 categories, ~5-7 files). Diffs MUST be additive default-value keys only; any other delta is investigated.
- **Risk: snapshot writer subtly changes between Phase 0 prototype and Phase 3 re-baseline.** Mitigation: keep Phases 2-3 to a single working session, or note the baseline-shooting commit SHA in `Phase 3 notes`.

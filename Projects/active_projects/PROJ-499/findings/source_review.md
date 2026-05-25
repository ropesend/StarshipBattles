# PROJ-499: Source Review (Baseline-Drift Census)

**Date:** 2026-05-23
**Reviewer:** Claude orchestrator — Phase 0 execution
**Method:** Read-only walk of all 65 `.json` files under
`tests/regression/snapshots/`, comparing against live `StatKey` enum at
`game/simulation/components/abilities/stat_keys.py:24-70`.
Census driver: `c:/tmp/proj499_census.py` (one-shot read-only script,
not committed).

---

## Section 1: The Gap

`tests/regression/modifier_ability_snapshots/conftest.py:147-173` defines
`compare_snapshots()`. The dict branch (lines 148-156) is:

```python
if isinstance(expected_val, dict):
    if not isinstance(actual_val, dict):
        differences.append(f"{path}: expected dict, got {type(actual_val).__name__}")
        return
    for key in expected_val:
        if key not in actual_val:
            differences.append(f"{path}.{key}: missing in actual")
        else:
            compare_values(f"{path}.{key}", actual_val[key], expected_val[key])
```

It iterates `for key in expected_val` only. Any key in `actual_val` that is
not in `expected_val` is silently ignored. The list branch (lines 157-164)
walks `zip(actual_val, expected_val)` and reports length mismatch, but
inside each pair recurses to the same `compare_values()` and inherits the
same gap for dict elements.

## Section 2: How PROJ-489 surfaced this

PROJ-489 re-shot 7 baselines after a behaviorally-correct change to
`Component.add_modifier()` and the `allow_abilities` enforcement. The 7
reshots picked up 4 new `StatKey` enum members in the `component.stats`
dict (`launch_rate_mult`, `recovery_rate_mult`, `bay_capacity_mult`,
`shield_bonus_add`). The other 58 baselines were not re-shot and still
lack those keys. Under the asymmetric comparator, those 58 stay GREEN —
because the comparator never iterates over actual's extra keys.

PROJ-489 audit verification logged this as F4 INFORMATIONAL with "No
action — harness masks; pre-existing schema-drift behavior unrelated to
PROJ-489." Reference: `Projects/active_projects/PROJ-489/findings/audit_verification.md`.

## Section 3: Baseline-drift census — VERIFIED (Phase 0)

### 3.1 Headline numbers

| Metric | Count | Files |
|--------|-------|-------|
| Baselines walked | 65 | (full directory) |
| Stale baselines (missing >=1 live `StatKey`) | **58** | every other baseline |
| Fresh baselines (all live `StatKey`s present) | **7** | the PROJ-489 reshots (see 3.2) |

Census exactly matches the Codex-prediction-and-Read-only-spot-check
inference recorded in design.md / planning source_review predictions.
**Stale count: 58/65** — no surprises.

### 3.2 The 7 fresh baselines

These are the only baselines that contain the four new `StatKey` enum
members at `component.stats`:

- `crew_quarters_automation_0.25.json`
- `crew_quarters_automation_0.50.json`
- `crew_quarters_automation_0.75.json`
- `crew_quarters_automation_0.99.json`
- `generator_efficiency_0.10.json`
- `generator_efficiency_0.25.json`
- `generator_efficiency_0.50.json`

These are PROJ-489's re-shoots. The unchanged siblings
(`crew_quarters_automation_0.00.json`, `generator_efficiency_1.00.json`)
are stale.

### 3.3 Stats key-set variants

Exactly **2** variants observed across all 65 files:

| Variant | Key count | Files | Missing vs live StatKey | Extra vs live |
|---------|-----------|-------|------------------------|---------------|
| Stale | 25 keys | 58 files | `launch_rate_mult`, `recovery_rate_mult`, `bay_capacity_mult`, `shield_bonus_add` | none |
| Fresh | 29 keys | 7 files | none | none |

Difference is exactly the 4 new `StatKey` enum members added since the
58 stale baselines were captured. No other schema drift.

### 3.4 Structural shape (top-level / component subkeys)

- **Top-level keys**: 1 variant across all 65 files — `{"abilities", "component"}`.
- **`component` subkeys**: 1 variant across all 65 files —
  `{"base_mass", "base_max_hp", "cost", "id", "mass", "max_hp", "modifiers", "name", "stats", "type_str"}`.

No structural drift in either dimension.

### 3.5 Ability class-name sequences

7 variants, mapping cleanly onto the 7 component families:

| Sequence | Files | Component family |
|----------|-------|------------------|
| `(RequiresMaintenance, ResourceConsumption, SeekerWeaponAbility, RequiresCommandAndControl)` | 18 | capital_missile_* |
| `(RequiresMaintenance, ResourceConsumption, BeamWeaponAbility, RequiresCommandAndControl)` | 7 | laser_cannon_* |
| `(RequiresMaintenance, ResourceConsumption, ProjectileWeaponAbility, RequiresCommandAndControl)` | 24 | railgun_* |
| `(CrewCapacity, ProvidesMaintenance)` | 5 | crew_quarters_automation_* |
| `(ResourceGeneration, StrategicResourceGenerationAbility, RequiresMaintenance, RequiresCommandAndControl)` | 4 | generator_efficiency_* |
| `(CombatPropulsion, StrategicMovement, ResourceConsumption, ResourceConsumption, RequiresCommandAndControl)` | 6 | standard_engine_* |
| `(ManeuveringThruster, RequiresCommandAndControl)` | 1 | thruster_no_modifiers |

No within-family drift in ability sequence.

### 3.6 Per-ability key-set variants

**1 variant per ability class.** No within-class drift. Snapshot
counts:

| Ability class | Key count | Occurrences | Key set |
|---|---|---|---|
| `BeamWeaponAbility` | 12 | 7 | `_base_accuracy, base_accuracy, base_damage, base_firing_arc, base_range, base_reload, class_name, damage, firing_arc, range, reload_time, tags` |
| `CombatPropulsion` | 4 | 6 | `base_thrust, class_name, tags, thrust_force` |
| `CrewCapacity` | 4 | 5 | `amount, base_amount, class_name, tags` |
| `ManeuveringThruster` | 4 | 1 | `base_turn_rate, class_name, tags, turn_rate` |
| `ProjectileWeaponAbility` | 10 | 24 | `base_damage, base_firing_arc, base_range, base_reload, class_name, damage, firing_arc, range, reload_time, tags` |
| `ProvidesMaintenance` | 4 | 5 | `amount, base_amount, class_name, tags` |
| `RequiresCommandAndControl` | 2 | 60 | `class_name, tags` |
| `RequiresMaintenance` | 4 | 53 | `amount, base_amount, class_name, tags` |
| `ResourceConsumption` | 4 | 61 | `amount, base_amount, class_name, tags` |
| `ResourceGeneration` | 3 | 4 | `class_name, rate, tags` |
| `SeekerWeaponAbility` | 15 | 18 | `base_damage, base_endurance, base_firing_arc, base_range, base_reload, class_name, damage, endurance, firing_arc, projectile_damage, projectile_hp, range, reload_time, tags, turn_rate` |
| `StrategicMovement` | 4 | 6 | `base_movement_points, class_name, movement_points, tags` |
| `StrategicResourceGenerationAbility` | 2 | 4 | `class_name, tags` |

All single-variant. Phase 3 re-shoots will not surface any
within-class ability-shape drift; if they do, escalate.

### 3.7 Cross-check: `mini_capital_missile` retype convergence (PROJ-497)

Per orchestrator constraint #7: PROJ-497 retyped `mini_capital_missile`
from `BeamWeaponAbility` to `SeekerWeaponAbility` (endurance 3.0 → 0.05,
effective range 240). Re-verified at Phase 0 via grep:

```
Grep "mini_capital_missile" tests/regression/snapshots/  → No files found
```

**No baseline references `mini_capital_missile`.** All 18 baselines in
the `capital_missile_*` family are based on the `capital_missile`
component (`SeekerWeaponAbility`), not `mini_capital_missile`. PROJ-497's
data edit is invisible to the Phase 3 re-shoot. Confirmed.

### 3.8 Cross-check: `efficient_engines` deletion (PROJ-497)

PROJ-497 deleted the `efficient_engines` modifier. None of the snapshot
filenames suggest dependence on that modifier (no `*efficient_engines*`
or `*standard_engine_efficient*` pattern); all engine baselines are
either `standard_engine_no_modifiers` or `standard_engine_size_N` (which
is the `simple_size_mount` modifier, not the deleted one). Re-shoot
should not surface any drift sourced from that deletion.

## Section 4: Implications for Phase 3

- 58 of 65 baselines need re-shooting to add the 4 new
  `StatKey` entries at `component.stats`
  (`launch_rate_mult, recovery_rate_mult, bay_capacity_mult,
  shield_bonus_add`).
- **Per-file diff bounded to additive `component.stats` keys; values
  follow the modifier's stat-key derivation rules.** For baselines
  where no modifier touches the newly-added keys, the values come from
  `create_default_stats_dict()` (the `_mult` keys default to 1.0; the
  `_add` key `shield_bonus_add` defaults to 0.0). For baselines whose
  active modifier DOES multiply the newly-added keys, the values are
  scaled accordingly — the most visible case is the
  `standard_engine_size_*` family, where `simple_size_mount` multiplies
  all `_mult` stats by the size factor, so `launch_rate_mult,
  recovery_rate_mult, bay_capacity_mult` land at the size factor
  (size_16 → 16.0, size_8 → 8.0, etc.), not 1.0. `shield_bonus_add`
  remains 0.0 across all 58 modified baselines because no modifier in
  the suite touches that `_add` key. The "additive" property is about
  key-set growth (no pre-existing keys mutate, none are removed, no
  shape changes); the per-value content reflects whatever the live
  modifier system produces — that's the whole point of the
  re-baseline.
- 7 PROJ-489 baselines should be IDENTICAL after re-shoot (already
  fresh). The two-pass discipline still re-writes them via
  `fail_missing_baseline()` after deletion; the second pass should diff
  to no content delta vs HEAD for these 7.
- No within-family or within-ability shape drift. Spot-checking one file
  per family (7 categories) is sufficient.
- If Phase 3's second-pass diff contains anything beyond additive
  `component.stats` keys (e.g., a value change on a pre-existing key,
  a removed key, a new ability class), **STOP**. That is the
  orchestrator-attention trigger from constraint #1.

## Section 5: Why the stale count was high

`game/simulation/components/abilities/stat_keys.py:103-114`
`create_default_stats_dict()`:

```python
stats = {}
for key in cls:
    stats[key.value] = cls.get_default(key)
stats['properties'] = {}
return stats
```

It iterates EVERY enum member. The 4 new keys
(`LAUNCH_RATE_MULT = "launch_rate_mult"` etc. at `stat_keys.py:61-63,70`)
are part of the enum. Therefore live `Component.stats` for every
component family contains those keys. The on-disk baselines that predate
the keys' addition are all stale.

This is the basis for the "re-shoot all 65" Phase 3 decision.

## Section 6: Codex independent confirmation

Codex planning consult at
`AgentCoordination/Scratchpad/Consult/20260523T125809Z_plan-snapshot-harness-fix/response.md`
finding 4 (response.md:28) predicted exactly this — 58 stale of 65,
4 missing keys, no other drift. Phase 0 converts that inference to a
verified count. Match.

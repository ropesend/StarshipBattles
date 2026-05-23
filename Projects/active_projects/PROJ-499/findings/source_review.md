# PROJ-499: Source Review

**Date:** 2026-05-23
**Reviewer:** Claude orchestrator (Batch 1, PROJ-499 planning)

## The Gap

`tests/regression/modifier_ability_snapshots/conftest.py:147-173` defines `compare_snapshots()`. The dict branch (lines 148-156) is:

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

It iterates `for key in expected_val` only. Any key in `actual_val` that is not in `expected_val` is silently ignored. The list branch (lines 157-164) walks `zip(actual_val, expected_val)` and reports length mismatch, but inside each pair recurses to the same `compare_values()` and inherits the same gap for dict elements.

## How PROJ-489 surfaced this

PROJ-489 re-shot 7 baselines after a behaviorally-correct change to `Component.add_modifier()` and the `allow_abilities` enforcement. The 7 reshots picked up 4 new `StatKey` enum members in the `component.stats` dict (`launch_rate_mult`, `recovery_rate_mult`, `bay_capacity_mult`, `shield_bonus_add`). The other 58 baselines were not re-shot and still lack those keys. Under the asymmetric comparator, those 58 stay GREEN — because the comparator never iterates over actual's extra keys.

PROJ-489 audit verification logged this as F4 INFORMATIONAL with "No action — harness masks; pre-existing schema-drift behavior unrelated to PROJ-489." Reference: `Projects/active_projects/PROJ-489/findings/audit_verification.md`.

## Baseline-drift census (predicted)

Phase 0 will produce the actual census. Predictions from Read-only inspection:

| Baseline file | Has 4 new keys? | Stale? |
|---|---|---|
| `crew_quarters_automation_0.00.json` | NO (verified by Read) | YES |
| `crew_quarters_automation_{0.25,0.50,0.75,0.99}.json` | YES (PROJ-489 reshots) | NO |
| `generator_efficiency_{0.10,0.25,0.50}.json` | YES (PROJ-489 reshots) | NO |
| `generator_efficiency_1.00.json` | NO (sibling, not reshot) | YES |
| `railgun_no_modifiers.json` | NO (verified by Read) | YES |
| All other 56 baselines | NO (inferred from same code path) | YES |

**Predicted stale count: 58 of 65.** Phase 0 verifies this exactly. If the count is off by more than ~5, escalate — that suggests additional schema drift Codex's survey did not surface.

## Why the predicted stale count is high

`game/simulation/components/abilities/stat_keys.py:103-114` `create_default_stats_dict()`:

```python
stats = {}
for key in cls:
    stats[key.value] = cls.get_default(key)
stats['properties'] = {}
return stats
```

It iterates EVERY enum member. The 4 new keys (`LAUNCH_RATE_MULT = "launch_rate_mult"` etc. at `stat_keys.py:61-63,70`) are part of the enum. Therefore live `Component.stats` for every component family contains those keys. The on-disk baselines that predate the keys' addition are all stale.

This is the basis for the "re-shoot all 65" Phase 3 decision.

## Codex independent confirmation

Codex planning consult at `AgentCoordination/Scratchpad/Consult/20260523T125809Z_plan-snapshot-harness-fix/response.md` finding 4 (response.md:28):

> "The current runtime modifier snapshot path likely emits those four keys for every component snapshot, not only the 7 re-shot baselines. ... If that reading is correct, strict raw key-set equality will likely fail many more than 7 currently committed baselines once someone actually runs the modifier snapshot suite."

Codex flagged this `[inference from code; not runtime-verified because allow_tests=false]`. Phase 0's job is to convert the inference into a verified count.

# PROJ-391 — Verification Report

**Source audit:** `Reviews/results/2026-05-07_220621_legacy-audit/`
**Run date:** 2026-05-08
**Cluster:** Underscore-prefixed legacy pair consolidations
**Batch summary:** 2 verified / 0 rejected / 1 uncertain (included) / 0 INFO / 0 out-of-scope (within this bundle)

## Verified

| ID | File | Symbol | Replaces | Call sites | Recommendation | Severity |
|---|---|---|---|---|---|---|
| LEG-04-007 | `game/strategy/services/planet_economy_projector.py:234` | `_get_harvester_info` | `get_harvester_info` (`game/strategy/engine/harvesting_engine.py:94`) | 1 prod (line 224 same file) | consolidate_with | MINOR |
| LEG-01-011 / LEG-04-008 (dedup) | `game/ui/screens/battle_setup/spec_compiler.py:419-427` | `_iter_components` | `iter_components` (`game/core/patterns/layer_iterator.py:42`) | 1 prod (line 359 same file) + 1 secondary site at `planet_economy_projector.py:220-231` | consolidate_with | MINOR |

## Rejected

None.

## Uncertain (resolved)

| ID | Symbol | Question | User decision |
|---|---|---|---|
| LEG-01-017 | `_formation_to_dict/_formation_from_dict` duplicated in `task_force.py` and `replay_serialization.py` | Different layers need own serialization (Sonnet's batch-2 verdict said "keep") OR move to `FormationSpec.to_dict/from_dict` per Pattern 17? | **Include** — move to `FormationSpec.to_dict/from_dict` per Pattern 17 (Serializable Protocol) |

## INFO (resolved)

None for this bundle.

## Out of Scope

| ID | Reason |
|---|---|
| Cross-system Pair 3 (`ModifierManager` vs `ModifierService`) | Audit's own cross-system verifier marked INTENTIONAL SPLIT — different responsibilities, different layers |

# PROJ-391: Design Document

## Source Audit

This project was created from the legacy-audit at `Reviews/results/2026-05-07_220621_legacy-audit/`.

- **Audit verified:** 32 items overall (across 11 sibling projects)
- **This bundle:** 2 verified, 1 uncertain (resolved — included), 0 INFO, 0 deferred
- **Project siblings:** PROJ-383..PROJ-390, PROJ-392, PROJ-393

## Cluster Identity

**Removal cluster:** Underscore-prefixed legacy pair consolidations. Three name-pair-drift findings where a private `_foo` exists alongside a canonical `foo` that does the same thing better:

1. `_get_harvester_info` (planet_economy_projector) → `get_harvester_info` (harvesting_engine)
2. `_iter_components` (battle_setup/spec_compiler) → `iter_components` (core/patterns/layer_iterator)
3. `_formation_to_dict/from_dict` duplicated in two layers → `FormationSpec.to_dict/from_dict` per Pattern 17 (Serializable Protocol)

LEG-01-011 (Shard 01) and LEG-04-008 (Shard 04) are the same `_iter_components` finding from two shards' perspectives — treated as one item.

## Severity Breakdown

| Severity | Count |
|----------|-------|
| MINOR | 3 (all small, low-call-site) |

## Risk Notes

- LEG-04-007: `_get_harvester_info` returns `Optional[dict]`; canonical returns `dict | list | None`. Existing call site at `planet_economy_projector.py:224` treats result as `dict` — `ResourceHarvester` is single-dict in practice, so consolidation is safe with an `isinstance` guard.
- LEG-01-011: Canonical `iter_components` handles list + dict layer formats; legacy `_iter_components` only handles list. Real layer data has so far been list-only at the call site, so widening is non-disruptive.
- LEG-01-017: User opted in during Phase D Step 3, choosing the Pattern-17 (`Serializable Protocol`) shape over keeping duplicates. Two existing implementations diverge slightly (`float(p[0])` vs `_vec_to_list`) — reconcile into one canonical serialization.

## Quick Wins

All three are single-call-site or low-call-site fixes. Whole project ships as one small PR (~50 LOC delta).

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

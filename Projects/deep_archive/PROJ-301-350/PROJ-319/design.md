# PROJ-319: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Audit

- **Audit directory:** `Reviews/results/2026-05-02_184210_audit_shrink/`
- **Audit date:** 2026-05-02
- **Item counts:**
  - Audit verified-safe candidates: **30**
  - Independently verified: **30**
  - Rejected: **0**
  - Uncertain: **0**
- **Claimed reclaimable LOC (verified-only):** ~733 LOC
  - Tier 4 dead imports/params/unreachable: 19 LOC
  - Dead functions: 57 LOC
  - Duplication consolidation: 657 LOC

> **Note on the zero-rejection rate:** The independent verifier returned zero
> REJECTED and zero UNCERTAIN verdicts across all 30 items. The source audit's
> own internal verifier flagged false positives in this same run (e.g.
> `IControllableShip` and `RegionClassifier` TYPE_CHECKING annotations
> correctly identified as live), so a downstream skeptical pass that finds
> zero additional issues is unusual. Implementation should still treat each
> deletion / extraction as the first chance to surface a missed reference,
> e.g. by running the focused pytest path before and after each task.

## Initial Analysis

The audit was run against 675 production files (~150,422 LOC). It used
deterministic tooling (vulture, radon, AST clone detection) plus four
shard-level deep-review agents and a verification pass.

The verified-safe portion entering this project covers three categories:

1. **Tier 4 surface cleanup** — single-line dead imports, unused parameters,
   and unreachable assignments scattered across `game/strategy/data`,
   `game/strategy/services`, `game/ui/panels`, `game/ui/screens`, and
   `game/ui/services`. Lowest blast radius.

2. **Two dead helper functions** — `_extract_weapon_summaries` (battle_runner)
   and `_planet_has_shield_facility` (strategy_detail_fmt). Both have
   superseding implementations in their own files.

3. **Duplication consolidation across UI + strategy layers** — race-config
   resolution, superweapon dispatch, planet/star list windows, planet target
   editors, sidebar widgets, validation helpers, intrinsic ability rolling,
   and circle-formation positioning. Several of these are CRITICAL because
   silent divergence would corrupt gameplay (multi-species colony stats,
   superweapon validation).

## Swarm Findings Summary

Combined analysis from individual verification reports in `.agent_reports/2026-05-02_184210_audit_shrink/`.

### Architecture

#### Layer boundaries touched

- **`game/strategy/services/`** — gains `race_resolver.py` (new). Already
  hosts `action_time_resolver.py` and similar service-grade resolvers.
- **`game/ui/widgets/`** — gains `range_slider_builder.py` (new). Existing
  home for cross-screen widget builders.
- **`game/ai/spatial_behaviors/`** — gains `_formation_utils.py` (new). Sits
  alongside `escort.py`, `screen.py`, etc.
- Remaining work edits existing files in place; no other new modules.

### Key Patterns to Reuse

- **`StrategyModalWindow` (Pattern #31)** — already the base for all four
  planet target editors. The new `PlanetTargetEditor` base class (DUP-X-05)
  layers on top of it, not replaces it.
- **`species_selector_mixin.py:111`** already exposes `load_race_config`. The
  new `RaceConfigResolverMixin` (DUP-X-04) hosts `_get_active_race_config`
  alongside it.
- **`__init_subclass__` registries** — keep the existing pattern; do not
  introduce a parallel registration mechanism for `SuperweaponOrderHandler`
  (DUP-X-02). Mirror the existing handler registry.

### Dependencies & Risks

1. **Multi-species colony correctness (DUP-X-01, DUP-X-04)** — once
   `resolve_race_config` is extracted, both engines will share a single
   resolution function. Run population/happiness sim regression tests before
   shipping. Concretely: any test under `tests/strategy/engine/` that
   exercises happiness or population growth on a multi-race colony.
2. **Superweapon end-to-end flow (DUP-X-02)** — the click → designation →
   command-handler path is a 3-file refactor with a dispatch table change.
   Touch-test each superweapon manually (stellerate, dyson, warp open/close,
   self-destruct) plus run any existing superweapon pytest coverage.
3. **Planet/Star list windows (DUP-X-03)** — the most invasive duplication
   refactor. Drift already exists between the two trees (planet has effect
   filters, star has type filters). The new `DataListWindow` base must
   parameterize over those differences without forcing a unified column set.
4. **Verifier zero-rejection rate** — flagged above. Each task in Phases 2
   and 4 should run the focused test path immediately after deletion or
   extraction so a missed reference surfaces quickly.

### Opportunities Discovered

- Once `_lazy_load_json_cache` is extracted (DUP-X-11), a follow-up could
  generalize it into a class-based `LazyJsonLoader` if a fourth lazy-loaded
  JSON cache is added. Out of scope for this project.
- `BackgroundCall` (LLM/Image) shape duplication (DUP-X-23/24) was correctly
  classified INFO and downrated by the audit; revisit if a third background
  service type is introduced.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

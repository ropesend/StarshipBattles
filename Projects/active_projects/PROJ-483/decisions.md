# PROJ-483: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-22 | Project initialized | Starting point for Type cleanup — Foundation + strict quick wins (2026-05-20) |
| 2026-05-22 | Bundled Foundation layers (core/sim/ai/engine/services/assets/research) into one project | Each layer had <10 per-finding items and would have made a thin project; bundling preserves coherence with the Protocol-narrowing cluster (which cross-cuts core/sim) and the strict-mode adoption (which is naturally per-layer). Code locality via architectural proximity per Protocol 13 Phase D Step 1 |
| 2026-05-22 | Included 16 Protocol-narrowing items via TYPE_CHECKING string annotations | User opted in via `AskUserQuestion`. Original shard reviewers rated these as INFO/duck-typing — but the cross-layer audit explicitly recommended narrowing because type erosion at the Protocol layer propagates through every consumer. Zero runtime cost via TYPE_CHECKING imports |
| 2026-05-22 | Included 5 AI controllable/protocols narrowings | User opted in. Coupled with the bulk Protocol decision; same TYPE_CHECKING pattern |
| 2026-05-22 | Excluded mypy `--strict` adoption for `game/simulation/` (622 errors), `game/strategy/` (1,070), `game/ui/` (2,571) | Verifier counts substantially exceed audit estimates (4.9×–5.7× heavier). Adoption is genuinely multi-week work for each layer and should be its own dedicated project after this per-finding cleanup lands |
| 2026-05-22 | Included mypy `--strict` adoption for the 6 bounded layers (research, services, assets, engine, ai, core) | Verifier counts are bounded (0/1/15/14/60/116). These layers are reachable in one project without drowning the per-finding work. Phase 3 narrowings should drop ai/core counts before Phase 4 measures |
| 2026-05-22 | Excluded `formula_evaluator._eval_node` narrowing, `json_utils.load_json` family, `ILocatable.location`, `IResourceHolder.resources` | User-deferred or genuine OOS: JSON inherently returns `Any`; `ILocatable.location` is the explicit cross-coordinate-system duck-typing seam (HexCoord in strategy, Vector2 in simulation); `IResourceHolder.resources` documented as cross-layer seam |
| 2026-05-22 | `pop_construction_item` Protocol-side narrowing is bundled here even though one finding (the Strategy-layer implementation) is in PROJ-482 | The Protocol lives in `game/core/protocols/strategy_mutators.py` (foundation) so the narrowing belongs here; the consumer-side narrowing belongs to its layer. Both ends must land together for consistency |

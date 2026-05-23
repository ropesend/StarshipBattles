# PROJ-482: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-22 | Project initialized | Starting point for Type cleanup — Strategy per-finding (2026-05-20) |
| 2026-05-22 | Bundled Strategy-only findings from `2026-05-20_210540_type-audit` by layer (`game/strategy/`) per user direction in Phase D | Strategy has the most missing return types (69.8% of all) and the single highest-impact cluster (GameSession 10-property fix). Isolating it from UI/Foundation keeps the per-file edits coherent. Full bundling discussion in `findings/bundling_decisions.md` |
| 2026-05-22 | GameSession cluster (10 properties) bundled as ONE combined task | All 10 share file, share fix mechanic (add annotation + remove ignore), and depend on the same TYPE_CHECKING imports. Splitting into per-property tasks would be ceremony without insight |
| 2026-05-22 | Included `_build_capture_context` UNCERTAIN item with new `ReplayCaptureContext` type | User opted in via `AskUserQuestion`. ~10 LOC: define type + apply annotation |
| 2026-05-22 | Excluded mypy `--strict` adoption for `game/strategy/` from this project | Verifier measured 1,070 strict errors (2.85× audit's `~375` estimate). Adoption requires multi-week dedicated effort; bundling it here would drown the per-finding cleanup |
| 2026-05-22 | Excluded `strategic_ability_scanner.find_*` TypedDict refactor, `formula_evaluator._eval_node` narrowing, and `battle_assembly.py:81` cast alternative | All UNCERTAIN; user chose to defer. Each is small but introduces design noise out of proportion to value at this stage |
| 2026-05-22 | One Strategy item (`game/app_bootstrap.py` `_replay_combat_lab_fallback`) lives outside `game/strategy/` but is bundled here | The closure is conceptually a strategy fallback and is the only non-strategy finding in this layer's audit slice — folding it in avoids creating a fourth project for one item |

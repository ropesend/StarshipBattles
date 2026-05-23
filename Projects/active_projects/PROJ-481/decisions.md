# PROJ-481: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-22 | Project initialized | Starting point for Type cleanup — UI per-finding (2026-05-20) |
| 2026-05-22 | Bundled UI-only findings from `2026-05-20_210540_type-audit` by layer (`game/ui/`) per user direction in Phase D | UI accounts for 76.7% of all `-> Any` returns and the largest single layer in the audit; isolating it from Strategy/Foundation keeps each project's checklist focused. Bundling driven by code relatedness, not severity — full bundling discussion in `findings/bundling_decisions.md` |
| 2026-05-22 | Excluded mypy `--strict` adoption for `game/ui/` from this project | Verifier measured 2,571 strict errors (5.7× the audit's `~452` estimate). Adoption requires multi-week dedicated effort; bundling it here would drown the per-finding cleanup. Suggest a follow-up project once Phases 1–3 land |
| 2026-05-22 | Excluded `builder/stat_getters.py` 47 `-> Any` functions | Audit's INFO ruling — JSON-config dispatch contract. Narrowing requires refactoring the registry + JSON system, out of scope here |
| 2026-05-22 | Included two test-bypass dialog ignore cleanups (defeat_dialog + turn_failed_dialog) together | Cross-shard consistency: audit verifier flagged `turn_failed_dialog.py:99` as identical pattern to `defeat_dialog.py:83`; both must be fixed together to keep test-bypass init paths consistent |

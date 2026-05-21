# PROJ-473: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-20 | Project initialized | Starting point for Thread per-instance RNG through planet/star generation to enable global random.seed removal (deferred from PROJ-471) |
| 2026-05-20 | Scope populated from PROJ-471 deferral (Protocol 07) | PROJ-471 (state-hygiene) findings ST-04-010 / ST-04-011 flagged two global `random.seed()` calls as Pattern #18 violations, but dual independent + Codex review (re-verified inline against live code) found them LOAD-BEARING: `star_generator.py` (26 bare `random.*` draws) and planet/atmosphere/naming/warp generation use the bare global `random` API, and placement strategies fall back to global random when `rng` is None. Removing the seed without first threading an explicit `rng` breaks galaxy reproducibility. The seed removal therefore depends on this project's rng-threading work and was moved here. |
| 2026-05-20 | Removal of the two `random.seed()` calls stays at the END of Phase 1, gated on rng-threading | The seed delete is only safe once NO generation code reads global `random` state. Sequencing the delete last, behind the threading + a before/after reproducibility characterization test, prevents a silent determinism regression. |
| 2026-05-20 | Generation output must remain reproducible byte-for-byte for a fixed seed; this is a "where randomness comes from" change, not a "what is generated" change | Moving `random.X(...)` → `rng.X(...)` with an identically-seeded `rng` draws the same sequence, so a fixed `galaxy_seed` must yield the same galaxy before and after. Any divergence indicates a draw-order error, not an intended balance change. No save-format change. |

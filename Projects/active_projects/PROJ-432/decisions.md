# PROJ-432: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-17 | Project initialized from PROJ-423 Codex consult | Codex flagged the asymmetry between `TurnStateSnapshot.restore()` and `SessionPersistenceAdapter.rehydrate_state()` as a real risk; see [design.md](design.md) for the file:line evidence. |
| 2026-05-17 | Land turn-state-snapshot alignment as a separate project (not a PROJ-423 phase) per Codex's explicit recommendation | The asymmetry is a behavioral fix with its own characterization-test surface, not a structural follow-up to the PROJ-423 lifecycle extraction. Keeping the scopes separate keeps each project's blast radius and review surface coherent, and PROJ-423's Phase 6 stays focused on the two purely mechanical follow-ups (underscore-alias migration + frozen schema fixture). |
| 2026-05-17 | **In scope:** add `empire.set_galaxy(...)` and pursuer-tracker rebuild blocks inside `TurnStateSnapshot.restore()`, mirroring `SessionPersistenceAdapter.rehydrate_state()`'s sequencing. | These are the two missing wiring steps; the rest of the rehydrate sequence already matches. See `design.md` §"Target shape" for the ordered steps. |
| 2026-05-17 | **Out of scope:** refactoring `restore()` to call into `SessionPersistenceAdapter.rehydrate_state()` directly (unification refactor). | The two paths still differ on input shape — snapshot owns dicts; adapter owns the full save dict + `ai_factory` + provider callbacks. Unifying them is a larger structural project of its own. |
| 2026-05-17 | **Out of scope:** save-schema or snapshot-capture format changes. | The asymmetry is purely on the restore wiring, not on the captured state. Saves stay disposable per CLAUDE.md. |
| 2026-05-17 | Phase 0 (characterization) precedes Phase 1 (implementation). | Strict TDD: write the focused tests that today fail (empire `_galaxy` back-reference identity post-restore; pursuer-tracker membership post-restore), watch them fail, then add the Phase 1 wiring to make them pass. Mirrors the assertion shape already used in `test_rehydrate_wires_galaxy_back_refs` and `test_rehydrate_rebuilds_pursuer_trackers`. |

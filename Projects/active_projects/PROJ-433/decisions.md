# PROJ-433: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-17 | Project initialized | Spun out from PROJ-425 Codex consult on 2026-05-17. `game/strategy/services/component_inspector.py` is 537 LOC after PROJ-425 Phase 2 added the per-instance layer-view helpers, exceeding the 500-LOC convention. |
| 2026-05-17 | Land component_inspector split as a separate small project (not a PROJ-425 phase) per Codex's explicit recommendation | Size 537 LOC > 500 LOC convention. Codex recommended the split but explicitly recommended a new project rather than reopening PROJ-425: "Not large enough to reopen PROJ-425; small follow-up project." Keeping PROJ-425's scope closed (Phases 0-5 + 7 done, Phase 6 gated on PROJ-431) is cleaner than reopening it for a comment-and-split follow-up. |
| 2026-05-17 | Adopt 03c-phase-aware-execution protocol | Matches the project-system default and lets `validate_phase.py` / `phase_complete.py` enforce intra-project gates. |
| 2026-05-17 | Three-phase shape: 0 = characterization, 1 = split, 2 = verification + docs | Mirrors the PROJ-432 three-phase template (the most recent small follow-up project). Phase 0 pins the public surface before any moves so the split lands on top of explicit characterization coverage. Phase 1 is the mechanical move. Phase 2 catches anything Phase 1 missed and updates docs. |
| 2026-05-17 | Phase 0 grep decides Option A (re-export shim) vs. Option B (caller migration) for the legacy `component_inspector.py` module | Both options are valid; the choice is dominated by caller count. If the import surface is widely consumed (estimated dozens of sites — `ship_instance.py`, plus various validators), Option A's ~20-LOC shim is cheaper than parallel caller migration in one phase. If it is sparse, Option B avoids shim debt. Phase 0's last task locks the choice. |
| 2026-05-17 | **Option A locked** — `component_inspector.py` becomes a re-export shim | Phase 0 grep found ~50 import statements across ~33 files (production + tests). Most are inline lazy imports inside engine / UI / validator hot paths. The ~25-LOC re-export shim is materially cheaper than parallel caller migration and keeps the diff small. |
| 2026-05-17 | `lookup_design_max_hp` placed in `component_layers.py` | Phase 0 grep confirmed its only consumer is `iter_components_by_layer` (which lives in `component_layers.py`). Keeping the helper next to its caller avoids cross-module coupling between the two new modules. |

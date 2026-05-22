# PROJ-475: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source / gating
Deferred tail of **PROJ-472**. GATED on PROJ-472's two guards + first migration
slice landing. This project migrates the REMAINING live strategy-screen / render
readers and deprecates the transitional surfaces PROJ-472 deliberately left.
See `Projects/active_projects/PROJ-472/plan.md` and the consult at
`AgentCoordination/Scratchpad/Consult/proj472_preflesh/advice.md` §3, §4, Risks.

## Initial Analysis
PROJ-472 honestly does NOT close the read path — it tightens it and blocks
net-new bypasses. Two documented transitional surfaces remain (verified live
2026-05-21):
- `StrategyScreen` pass-through properties `galaxy` / `empires` / `systems` /
  `active_empire` / `human_player_ids` (`strategy_screen.py:160-189`) — allowlisted
  with reason in the PROJ-472 session-read guard.
- `FacadeSessionState` publicly holds `session` (`_facade_state.py:63-86`), still
  reachable via `facade.facade_state.session`.

Plus the remaining live readers not in PROJ-472's first slice (render-hot
`strategy_render/fleets.py`, `system_tree_panel.py` raw-content walk, etc.).

### Dependencies & Risks
1. **Render/perf churn** — `strategy_render/hex_outlines.py` and `fleets.py` sit
   on render/cache hot paths; do NOT invent per-frame projections. The
   `FacadeSessionState` cache holder is a kept-by-design performance boundary
   (`_facade_state.py:48-60`, pinned by
   `tests/unit/strategy/engine/test_game_session_projection_boundary.py`).
2. **Deprecating pass-throughs is behavioral** — removing `StrategyScreen.galaxy`
   etc. touches many call sites; sequence carefully under the guard.
3. **Determinism/save-compat** — projection-only, as in PROJ-472.

## Swarm Findings Summary
Combined analysis from individual agent reports in `findings/`.

### Architecture
[Key architecture points relevant to implementation]

### Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

### Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

### Opportunities Discovered
- [Opportunity 1]

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

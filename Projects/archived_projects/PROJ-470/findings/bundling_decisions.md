# PROJ-470: Bundling Decisions

Records Phase D of Protocol 18. The autonomous-override contract replaced the protocol's `AskUserQuestion` steps with a single Codex planning consult; I (Claude) weighed Codex's advice and own the final decisions below.

## Default proposal (Protocol 18 Step 1)

V (verified) = 15. Protocol 18: `V < 30` → **ONE project**, all (layer, pattern_area) cells in one bundle, phased by severity.

| # | Title | Layers/Areas | Verified | Uncertain | Phases (severities) |
|---|-------|--------------|----------|-----------|---------------------|
| 1 | Pattern conformance — facade read-path, modal, event-bus + doc/hygiene drift | ui, strategy, core · facade, strategy_modal, event_bus, protocol_typeguard, ability_stat, doc_drift, loc, undocumented | 15 | 3 | Critical, Major, Minor, Strategic |

Totals: VERIFIED 15 / UNCERTAIN 3 / REJECTED 0 / OUT_OF_SCOPE 3 (excluded)

## Codex consult (single, autonomous-override)

Artifact: `AgentCoordination/Scratchpad/Consult/20260521T032218Z_pat-audit-bundling/response.md`

Codex's advice (exit_status ok):
- **Bundling:** single project is the correct default; matches Protocol 18 `V<30` rule; Note 2 prefers keeping doc-drift beside related code work rather than a separate docs project.
- **UNCERTAIN exclusions:** agreed excluding UP-003, UP-004, UP-005 — Pattern #11 already documents both PerPlayerUiState and FacadeSessionState (docs validator rates #11 ACCURATE); UP-004 recurs in only 2 registries and is a Pattern #4 variant.
- **Re-scope flag:** LOC-001 (69 files) should NOT be treated as one cleanup — cap at top-N or split files already touched by higher-severity fixes; full remediation = its own project.
- **Risk flag:** FAC-001 (135+ sites) is structurally different and will dominate the project unless Phase 1 is scoped as "policy + first migration slice" rather than "remove every direct UI read now."

## Final decisions (Claude owns the call)

1. **ONE project, 4 phases by severity** — accepted Codex's confirmation; matches Protocol 18.
2. **Defer all 3 UNCERTAIN items** (UP-003, UP-004, UP-005) — accepted Codex's reasoning; recorded in verification_report.md for a future audit.
3. **FAC-001 scoped as policy + read-path static guard + first migration slice** (Phase 1) — accepted Codex's risk flag; full 135-site migration proceeds incrementally under the guard, decomposed into its own project if large.
4. **LOC-001 scoped as triage + top-10 split** (Phase 3); remaining 59 files recorded as a separate future decomposition project — accepted Codex's re-scope flag while keeping the single-project shape Protocol 18 mandates for V<30.
5. **EVT-001 kept narrow** — fix the stale path + doc class-name; EventBus unification treated as optional/documented-divergence, not mandatory.

## Per-UNCERTAIN-item resolutions (Step 3)

| ID | Decision | Note |
|----|----------|------|
| UP-003 PerPlayerUiState | Defer | Already documented under Pattern #11 |
| UP-004 Declarative Dispatch Table | Defer | Below the 3+ promotion bar; Pattern #4 variant |
| UP-005 FacadeSessionState | Defer | Already documented under Pattern #11 |

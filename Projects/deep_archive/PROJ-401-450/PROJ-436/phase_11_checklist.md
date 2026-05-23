# Phase 11: Codex consult + verified-finding remediation

**Status:** Complete
**Depends on:** phase_10
**Review Mode:** standard

**Objective:** Run a project-wide end-of-PROJ-436 Codex consult per
`feedback_consult_at_project_end.md`; verify each finding against
current code; verified+actionable findings become added phases
(12+, 13+, …); unverified or out-of-scope findings logged in
`decisions.md`.

## What landed

Consult artifact:
`AgentCoordination/Scratchpad/Consult/20260518T145950Z_proj436-phase11-end-of-project/response.md`.
Codex `pre-final-check` `--allow-tests`, exit_status: ok. Scoped to
full PROJ-436 delta from charter `f34a60c71` to HEAD `622e63055`
(~555 files / +15913/-1591 LOC across Phases 0–10).

**Findings (all verified against current code before disposition):**

- **Finding 1 — Fleet fractional resource-cost contract drift:**
  VERIFIED+ACTIONABLE. The `IProductionResourceSource.production_consume_resource(amount: float)`
  Protocol contract is silently violated by Fleet's implementation
  which `int(round(amount))`s before unloading. Bug predates
  PROJ-436 but Phase 8 declared the Protocol that exposes it.
  **Disposition:** authored as **Phase 12** with 4 design options
  (A/B/C/D); awaits user pick before execution. Recommendation:
  Option C (engine reads-back actually-consumed via
  `production_get_resource` diff, ~15 LOC + new pinning tests).
  See `phase_12_checklist.md` and the 2026-05-18 Phase 11 decisions
  row for the full evidence chain.
- **Finding 2 — Phase 10 doc drift in `docs/02_PATTERNS.md`:**
  VERIFIED+ACTIONABLE → patched in-Phase-11. Three stale claims
  overstated `bay_inventory.resources` / `bay_inventory.population`
  as the live fleet-cargo write surface (the slots EXIST from
  Phase 2 widening but production fleet-cargo still routes through
  the Phase 3 `ShipCargoManager._cargo_contents` substrate),
  plus a contradictory "`Container.accepts()` taking over" line
  on Pattern #43's Last-verified marker that contradicted the
  body's correct wording. All three rewritten to honest
  "BayInventory has these slots from Phase 2 but production cargo
  has not been migrated into them."
- **Risk — `Container.remove()` does not enforce non-negative
  quantities:** VERIFIED+OUT-OF-SCOPE → decisions.md row only.
  `Container.add()` rejects `quantity < 0` (`container.py:191,213`)
  but `Container.remove()` does not (`container.py:225-256`). Codex
  reproduced: `remove(..., -3.0)` grows stored value 10.0 → 13.0.
  No production caller passes negative removals; cosmetic safety
  hardening for a post-PROJ-436 hygiene pass.

## Phase Completion Checklist

- [x] Codex consult run; response read; verdicts logged in decisions.md
- [x] All verified-finding remediation phases authored (Phase 12)
- [x] In-phase doc-drift patch applied (3 lines in `02_PATTERNS.md`)
- [x] Full sharded suite still green (23209/23211 — doc-only changes in this phase)
- [x] Update status to Complete; update plan.md + phase_state.json
- [x] Notify user that Phase 12 awaits design pick

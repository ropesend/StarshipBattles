# PROJ-343: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project initialized | Starting point for Closeout Sprint 1 — production behavior bug fixes from PROJ-321..341 review |
| 2026-05-04 | Tier-1 findings firsthand-verified before scaffolding | Codex-unique CRITICALs were not cross-validated by the other 12 reviewers; planning instance read live source for T1.1/T1.2/T1.3/T1.4/T1.5 to confirm each defect is real before committing to fixes. All five confirmed. See [design.md](design.md) for line-by-line evidence. |
| 2026-05-04 | TDD-first per defect | Each defect gets a public-API failing test in Phase 1 before any production change. The prior arc's pinning tests (which encode the bugs as required) are wrong and will be DELETED or REWRITTEN alongside the fix in their respective Phase 2-7. |
| 2026-05-04 | Per-bug commit discipline | Each defect lands in its own commit with `fix(<area>): <summary> (PROJ-343 T1.X)`. NO `git add -A` style sweeps. NO `--no-verify`. PROJ-329A `concurrent_commit_audit.md` documents the prior arc's contamination incidents — do not add to that count. |
| 2026-05-04 | Phase B swarm reserved for PROJ-343 only | Master arc plan recommends 3 parallel Explore agents at the start of Phase 1 to enumerate (a) all `patch.object(dialog, "kill")` tests, (b) every other `collect_sector_effects(..., empire_id=None)` call site, (c) every test pinning raw-exception propagation for end-of-turn engines. Skip for PROJ-344..349 (those are mechanical). |
| 2026-05-04 | T1.4 fix shape: controller-result contract change (Option A) | Selecting Option A (controller returns `ConfirmResult(orders_issued, aborted_for_correction)`) over Option B (dialog re-checks conditions) — single source of truth in controller, easier to test, no duplicated logic. May ripple into `confirm_pending` callers; Phase 6 includes the grep step. |
| 2026-05-04 | T1.5 fix shape: TransferDialog audit-S1.2 pattern verbatim | CargoQuickDialog has no validation-abort path that should keep the dialog open (per controller read in design.md). Plain `try/finally: self.kill()` matches TransferDialog's fix. If Phase 7 verification finds an abort path, escalate to T1.4-style selective-close. |

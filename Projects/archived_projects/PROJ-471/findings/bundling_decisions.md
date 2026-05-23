# Bundling Decisions — PROJ-471

Source audit: `Reviews/results/2026-05-20_082533_state-audit/`. This run created a single project; no siblings.

## Autonomous-override note

This skill ran fully autonomously. Wherever Protocol 19 calls for `AskUserQuestion` (bundling choice, scope, borderline VERIFIED/UNCERTAIN findings), the autonomous-override contract substituted a single Codex consult for a second opinion, after which Claude (the initiator) owned the final decision. The consult and its synthesis are recorded below and in `decisions.md`.

## Default proposal (Protocol Phase D Step 1)

19 VERIFIED items. Phase D math: V < 30 → ONE project, all singletons/mechanisms in one bundle, phases ordered by severity.

| # | Title | Singletons / Mechanisms | Verified | Uncertain | Phases (severities) |
|---|-------|-------------------------|----------|-----------|---------------------|
| 1 | State hygiene — singleton-divergence consolidation + collection/RNG hygiene | 8 singleton-divergence + 3 stale/dead bridge + 6 module-mutable/class-state/global + 2 random_seed | 19 | 0 | Critical, Major, Minor |

Totals: VERIFIED 19 / UNCERTAIN 0 / REJECTED 0 / OUT_OF_SCOPE 8 (excluded).

## Codex consult (second opinion)

Consult leaf: `AgentCoordination/Scratchpad/Consult/20260521T033725Z_state-audit-bundling/` (mode: planning, read-only).

Codex `## Findings` (summarized):
- **One project is the right default**, with a hard Phase 1 gate around `_default_provider` rather than a separate foundation project — it is the same context-vs-module-default conversation as the other singletons, and the shared bridge hub is `create_production()` (`game/context.py:162-190`).
- The two proposed regression tests (`_default_provider` divergence; `ShipCombatEngine` shared subsystems) are the right Phase 1 sentries.
- **Borderline 1 (exit_dialog):** keep in scope but as opportunistic late work, first MAJOR to drop if trimming — verifier downgrade is correct.
- **Borderline 2 (density_map ST-02-003):** agreed OUT_OF_SCOPE; Pattern #18 targets module-level `random.*`, the guard test excludes strategy generation; only docstring drift remains.
- **Borderline 3 (stale bridges):** split the bucket — `_default_game_settings` and `_default_image_provider` are true production dead ends (cheap deletions); `_default_profiler` is NOT dead (`set_default_profiler()` still called in bootstrap; `profile_action`/`profile_block` depend on `_default_profiler`) → design cleanup, not deletion.

Codex `## Risks` (summarized): single-umbrella risk is execution sprawl, not architectural incoherence — `_default_provider`/`_default_manager` can churn many call sites while low-risk tails distract; separate "dead in production" from "still powering hooks"; honor strict TDD (name failing tests first) since `allow_tests:false` meant no tests were run.

## Final decisions (Claude owns)

1. **ONE project, 3 phases by severity.** Adopted. Mitigated Codex's execution-sprawl risk by making **Phase 1 an explicit exit gate** around `_default_provider` + `ShipCombatEngine` — tail cleanup (Phases 2–3) does not start until both pass.
2. **exit_dialog (ST-01-001):** INCLUDE as MAJOR, placed last in Phase 2 with a "drop first if trimming scope" note (Task 2.13).
3. **density_map (ST-02-003):** OUT_OF_SCOPE. Recorded in `verification_report.md` and forwarded to the refinement proposal as doc-drift.
4. **Stale bridges:** `_default_game_settings` + `_default_image_provider` → straightforward MINOR deletions (Task 3.1). `_default_profiler` → reframed as a **design cleanup with a verify-fallback-first step** (Task 3.2), correcting the audit's "removable bridge" framing.

## Final bundle

Single project PROJ-471. Phase 1: 2 items (1 CRITICAL + 1 MAJOR class-shared-state) with regression tests. Phase 2: 13 MAJOR items. Phase 3: 4 MINOR items (3 bridge/dead-code + 1 test seam). Total checkboxed findings ≈ 19 (matches verified count).

## Per-UNCERTAIN-item decisions

None — no UNCERTAIN items. The borderline calls were resolved via the consult above, not a per-item Include/Exclude/Defer pass.

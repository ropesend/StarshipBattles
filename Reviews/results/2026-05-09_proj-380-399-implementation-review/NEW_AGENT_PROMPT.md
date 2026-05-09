# Prompt for fresh agent — Remediate PROJ-380..399 review findings

Copy the section below as the entire opening user message to a fresh Claude Code session running on the same repository. The agent should treat this as its full mission brief and ground its work in the in-repo files referenced.

---

## Your mission

You are taking over a multi-week refactoring orchestration on the Starship Battles repository at `feat/03c-phase-aware-execution`. The previous orchestrator ran 11 implementation projects (PROJ-380..394, plus 5 remediation skeletons PROJ-395..399 that have already shipped their narrow code goals). An independent code-review pass on all 20 of those projects produced a per-project review report and a consolidated remediation plan. Your job is to **execute that remediation plan end-to-end** by creating new projects (PROJ-400..409), running each via subagent, delegating OpenCode reviews, and getting the branch to audit-clean.

You are NOT auditing whether the prior work was correct — that pass is done. The findings are recorded. You are implementing the fixes.

## Critical constraint

**The previous orchestrator already verified the 6 Tier-1 production behavior bugs live in source (B-01..B-06).** Trust the REMEDIATION_PLAN's call site/line numbers and implement directly. Do not re-verify in your own context — that would burn tokens for marginal added confidence. If a subagent reads the file at the cited line and finds the symptom is gone, that's a signal someone else fixed it concurrently — log "Already fixed by <SHA>" and move on.

## Read these files first, in this order, before you do anything else

1. **`CLAUDE.md`** — project rules. Especially Rule 3 (no save-migration code, no compatibility shims) and the "Estimate in LLM time" section.
2. **`AGENTS.md`** — test infrastructure (`python Tools/test_sharded/test_sharded.py`), conventions, review-delegation patterns.
3. **`docs/01_ARCHITECTURE.md`**, **`docs/02_PATTERNS.md`** (esp. patterns 1, 5, 10, 31, 36), **`docs/03_CONVENTIONS.md`** (esp. §LOC ceiling, §typing).
4. **`docs/05_ERROR_HANDLING.md`** — needed for B-03 and Tier-3 D-03.
5. **`Reviews/results/2026-05-09_proj-380-399-implementation-review/REMEDIATION_PLAN.md`** — your work definition. Read it cover-to-cover. Tiers 1-5 + execution waves are spelled out.
6. **`Reviews/results/2026-05-09_proj-380-399-implementation-review/consolidated_report.md`** — per-project verdict table.
7. The 6 individual review reports for the projects with verified production bugs (skim each, deep-read the Findings section):
   - `PROJ-381_report.md` (B-03)
   - `PROJ-382_report.md` (B-04 + B-06)
   - `PROJ-386_report.md` (B-05)
   - `PROJ-392_report.md` (B-01)
   - `PROJ-393_report.md` (B-02)
   - `PROJ-394_report.md` (B-04 follow-up)
8. Current state of the 5 existing remediation skeletons under `Projects/active_projects/PROJ-395/` through `PROJ-399/`. These contain real implementation work; their bookkeeping is what Wave 2 reconciles.

After this reading you should be able to answer: which file/line does each blocker live at, what is the canonical fix, and what's the existing project-system context.

## Branch + commit strategy

- Stay on `feat/03c-phase-aware-execution`. Do NOT branch off `main` — you'd lose 78 commits of in-flight work.
- Commit per task or per phase, not per project. Use commit message format: `PROJ-NNN phase N: <task summary>` and `PROJ-NNN: closeout — <project summary>`.
- The user has been pushing parallel work in their own session. **Expect at least one merge conflict** during your run — handle it the same way you'd handle any other: read both sides, take the canonical, document. The previous orchestrator hit two such events; both involved stale `_MockGalaxy`/`fleet_navigation_service` content.
- Never skip pre-commit hooks. Never `git push --force`. If a hook fails, fix the underlying issue.

## Project structure — 10 new projects

Create them via:

```bash
python Projects/scripts/create_project.py "<title>"
```

The script auto-assigns the next PROJ ID and creates the skeleton. Don't hand-populate — use the script, then overwrite the templates.

| New PROJ | Title | Source | Phases |
|----------|-------|--------|--------|
| PROJ-400 | Tier 1 B-01 — `NewGameSetupScreen._create_ui()` deleted-wrapper call | PROJ-392 | 1 phase |
| PROJ-401 | Tier 1 B-02 — Passenger-load validator missing-`species_id` rejection | PROJ-393 | 1 phase |
| PROJ-402 | Tier 1 B-03 — `SimulationBattleResolver` catch `ValidationException` | PROJ-381 | 1 phase |
| PROJ-403 | Tier 1 B-04 — Migrate stale `_MockGalaxy` test doubles to `GalaxyState` | PROJ-387/394 | 1 phase |
| PROJ-404 | Tier 1 B-05 — Eradicate save-format compatibility (Rule 3 follow-on) | PROJ-386 | 1 phase |
| PROJ-405 | Tier 1 B-06 — Wire EventBus injection through Projectile/Seeker construction | PROJ-382 | 1 phase |
| PROJ-406 | Tier 2 — Audit-readiness reconciliation across 14 projects | All Tier 2 | 1 phase |
| PROJ-407 | Tier 3 — Stale docs + architecture wording sweep (D-01..D-09) | All Tier 3 | 1 phase |
| PROJ-408 | Tier 4 — Coverage gaps + missing regression tests (C-01..C-06) | All Tier 4 | 1 phase |
| PROJ-409 | Tier 5 — Closure of orchestrator-deferred items (MAJ-013, MAJ-014) | PROJ-395 | 1 phase |

Each project's plan, manifest, design.md, decisions.md, and phase_1_checklist.md must be filled in before dispatching the subagent. Use the existing PROJ-395..399 plans as templates for shape — they have the right tone and section structure. Each project must end with a closeout commit and an updated `Projects/projects_index.md` entry.

## Workflow per project (the pattern that worked in the prior run)

1. **Create the skeleton** via `create_project.py`.
2. **Populate plan + checklist + manifest** referencing the REMEDIATION_PLAN's Tier item it closes. Cite file:line evidence so the subagent doesn't have to rediscover.
3. **Dispatch one general-purpose subagent** with a focused prompt (300-600 words) covering: required reading, the specific blocker(s), workflow, hard rules, deferred-finding policy, test infrastructure, reporting format. Use the Stage-1/2/3 dispatches in this transcript as templates.
4. **When the subagent returns**, scan for: any deferred items, any cross-project conflicts, working-tree state. Resolve before proceeding.
5. **Submit an OpenCode review** for projects with code/behavior changes (PROJ-400..405, 407, 408). Skip the review for purely-bookkeeping projects (PROJ-406, PROJ-409 if it's just a decision record).
6. **Move to the next project.** Don't wait for the review to come back.

For Wave 1 (PROJ-400..405): the 6 blockers touch mostly disjoint files. **You can run them in parallel via 6 separate subagent dispatches in a single message** — but only if your tools permit non-conflicting parallel writes. If your harness doesn't (no worktrees), run them serially. The previous orchestrator ran serially because of a worktree issue.

## OpenCode review delegation — pattern

The review daemon at `Tools/agent_coordination/review_daemon.py` watches `AgentCoordination/opencodereview/pending_review_requests/`. Submit reviews via:

1. Generate a unique payload path:
   ```bash
   PAYLOAD_PATH="AgentCoordination/opencodereview/local/request_payloads/payload_$(date +%Y%m%d_%H%M%S)_$(openssl rand -hex 3).json"
   ```
   (or PowerShell equivalent — see `.claude/skills/claude-delegate-review/SKILL.md`)

2. Write a JSON payload with `type`, `title`, `scope` (multiline markdown), `instructions` (multiline markdown), `context`, `expected_deliverable`, `requester: "claude-code"`. Specify which findings to verify and which severity guidance to apply.

3. Submit:
   ```bash
   python Tools/agent_coordination/create_review_request.py --payload-file "$PAYLOAD_PATH"
   rm -f "$PAYLOAD_PATH"
   ```
   The script prints a request ID; capture it.

4. Verify the daemon picked it up:
   ```bash
   ls AgentCoordination/opencodereview/in_progress_review_requests/ AgentCoordination/opencodereview/pending_review_requests/
   ```

5. **Don't wait for the review to complete.** Move to the next project. Reviews land in `Reviews/results/<date>_<title>_req-req_<id>/` whenever OpenCode finishes; you can read them at the end if you have time.

If the daemon isn't running, check `AgentCoordination/opencodereview/local/review_daemon.log`. The PID file convention is unreliable on Windows (`os.kill` returns "parameter incorrect" even for live processes); confirm with `tasklist | findstr <PID>` instead.

## Stage boundaries

Run `python Tools/test_sharded/test_sharded.py` in the background after each wave completes:

- After Wave 1 (PROJ-400..405): expect 0 failures, 0 errors. PROJ-399 already cleaned the pre-existing baseline. If failures remain, they're from Wave 1 — triage immediately.
- After Wave 2 (PROJ-406): no code change — skip the suite, just run `python Projects/scripts/validate_audit_ready.py PROJ-XXX` for each of the 14 reconciled projects. All should pass.
- After Wave 3 (PROJ-407): docs-only changes — light suite or skip.
- After Wave 4 (PROJ-408): suite again. New tests should all pass; no regressions allowed.
- After Wave 5 (PROJ-409): suite again. Final canary.

Output truncation note: `test_sharded.py` only prints FAILURES sections for shards that had failures, but TOTAL counts everything. If TOTAL says N failed but only M visible, look for hidden shards. The previous orchestrator hit this twice.

## Hard rules

- **CLAUDE.md Rule 3 strict:** No save-migration code. PROJ-404 (B-05) deletes legacy save-shape tolerance — do NOT replace with version-gates or "deprecated" annotations. Old saves are disposable.
- **No new shims.** Especially in PROJ-400 (NewGameSetupScreen) and PROJ-405 (Projectile EventBus): if you find yourself writing a wrapper to maintain a deleted call shape, stop and re-think.
- **Type-annotate every new public function/method** using modern syntax (`int | None`, native generics).
- **Strict TDD where new tests are required.** Phase 1 of B-04 (PROJ-403) involves replacing test fixtures — write the failing version first if the canonical doesn't exist, see it fail, then make it pass.
- **Read each cited file BEFORE editing.** This branch has 78+ commits since the original audit; line numbers may have shifted.
- **Don't revert unrelated user changes.** Check `git status --short` before editing. If you see UU files (merge conflicts you didn't create), surface to the user — do NOT auto-resolve.

## Deferred-finding policy

If a Tier-1 blocker turns out to be already-fixed (concurrent work) or non-trivially blocked:

1. Log "Already fixed by <SHA>" or "Deferred: <reason>" in the project's `findings/verification_report.md`.
2. Update the project's `plan.md` Current State.
3. Continue with the rest. Don't block.
4. Surface in your final report.

If a sharded-suite regression appears at a wave boundary that's NOT explained by your work:

1. Triage with `git stash && pytest <failing_test>` to confirm pre-existing.
2. If pre-existing: log to PROJ-409's verification report as "wave-boundary observation."
3. If introduced by your work: send the responsible subagent (via the agent ID it returned) a SendMessage with the failure details and ask it to fix in a closeout commit.

The previous orchestrator hit this pattern twice (PROJ-393 transfer_order siblings, PROJ-380 colonization_facade) — the closeout-round mechanism worked.

## Audit-readiness validators

After each project's closeout, run:

```bash
python Projects/scripts/validate_audit_ready.py PROJ-NNN
python Projects/scripts/validate_phase.py PROJ-NNN 1
```

Both should PASS. The most common failure is leaving phase status as `Not Started` after marking the project complete in `plan.md`'s Quick Status — the validators read both. Update both consistently.

After Wave 2 closes, run `validate_audit_ready.py` against ALL of PROJ-380..399. **All 20 should pass.** That's the audit-clean signal.

## Skill usage logging

The harness has hooks in `.claude/settings.json` that auto-log skill invocations. Don't disable them. If you invoke a skill via the `Skill` tool or via `/skill-name` syntax, the hook fires automatically.

## Final hand-off expectations

When all 5 waves complete, write a final summary at `Reviews/results/2026-05-09_proj-380-399-implementation-review/REMEDIATION_COMPLETE.md` containing:

1. Per-project commit SHAs (PROJ-400..409).
2. Final sharded-suite result (test count, failed, errors).
3. Audit-readiness status for all 20 projects in `projects_index.md`.
4. Any deferrals you logged.
5. Any review findings that came back during the run (and whether they were addressed in-loop or deferred).

Then: print a 500-word hand-off in the chat summarizing the work and outstanding items.

## Useful prior-session context

Recent commit range that's relevant:
- `2a0dc2877` was the start of the remediation skeletons (PROJ-395..399 created).
- `fd4a23068` was the most recent prior-session commit (PROJ-399 closeout).
- Look at `git log --oneline 2a0dc2877..HEAD` for the full remediation arc.

Test count baseline: **19799 passing, 0 failed, 0 errors** as of the final stage-3 sharded suite run (commit `fd4a23068`). Your Wave 1 fixes should add coverage but should NOT introduce regressions.

## Why I'm trusting you to figure things out

The previous orchestrator made dozens of judgment calls during the original PROJ-380..394 run — bundling, sequencing, deferral, conflict resolution. The patterns are documented in the existing project verification reports under `Projects/active_projects/PROJ-3{80..99}/findings/verification_report.md`. When you hit a fork, look there first for precedent. When the precedent isn't a clean match, use your own judgment and document the call in `decisions.md`.

Begin with the reading list above. After you finish reading, post a brief acknowledgment summarizing what you learned and your planned dispatch order, then start Wave 1.

---

End of prompt.

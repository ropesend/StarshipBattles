# Plan Review: Phase-aware project execution with cumulative delegated reviews

**Request ID:** req_20260503_141601_20579d
**Review Type:** plan
**Requester:** claude-code
**Reviewed:** 2026-05-03

---

## Findings Summary

| Severity | Count |
|----------|-------|
| CRIT | 0 |
| MAJ | 6 |
| MIN | 5 |
| NIT | 4 |

**Overall Recommendation:** Proceed with revisions (address MAJ findings before implementation; MIN findings as quality improvements; NIT findings at discretion).

---

## MAJ Findings

### MAJ-1: Findings Ledger enables indefinite issue hiding (§E, §Pushback #2, §G)

**Location:** Plan §E (cumulative review instructions), §Pushback #2, §G.1

**Concern:** The cumulative review instructions explicitly instruct the reviewer to "Skip findings already recorded in findings_ledger.md as acknowledged-deferred or wontfix." Combined with the plan's design that no follow-up reviews fire after remediation (§G.3: remediation commits "do not dispatch a new review"), a finding marked `acknowledged-deferred` at phase 2 will be permanently excluded from all subsequent cumulative reviews (phases 3, 4, ..., N).

The only re-check opportunity after deferral is:
- The post-completion audit (claude-proj-audit), which §H says is now "lighter scope than today" since cumulative reviews already ran.
- A future agent manually choosing to revisit it.

There is no mechanism for "re-check at phase N+1" or "auto-revisit after N phases." The lifecycle of a deferred finding is: deferred → never checked again.

**Suggested resolution:** Add a fourth status to the ledger: `deferred-to-phase-N` with a target phase number. The cumulative review of phase N (and all subsequent) would re-check deferred findings whose target phase has been reached. The `phase_dag.py status` subcommand could flag overdue deferred findings. This preserves the noise-reduction goal while ensuring findings don't evaporate.

---

### MAJ-2: Last-phase findings have no verification path (§G.3, constraint #6)

**Location:** Plan §G.3, constraint #6

**Concern:** The cumulative-review-only model has a structural gap at the final phase. Constraint #6 says "the next cumulative review re-checks the remediated work." But if the final phase (phase N) of a project has findings:
- Remediation is committed without triggering a new review (§G.3)
- There IS no phase N+1 to fire a cumulative review
- The project completion merges to `main` with unverified remediations

The plan says (§H) `claude-proj-audit` becomes a "final integration check on top of cumulative reviews" with a lighter scope, but this is undefined — does it re-verify remediations? The plan doesn't specify.

The same gap exists for any phase whose child has already completed and whose review returns findings (depth-1 buffer means the child started while the parent was only committed, not verified). The child's cumulative review covers the parent, but if the parent's review returns findings *after* the child's review is already done, those findings have no pending review to pick them up.

**Suggested resolution:** Add a requirement: before project completion, `phase_complete.py` (or a new `verify_all_remediated.py`) checks that ALL completed reviews have zero outstanding findings (only `acknowledged-deferred`/`wontfix` remain in the ledger from completed phases). If unresolved findings exist, block the merge to main and require a final "remediation verification review" — a one-shot cumulative review covering all remediated phases.

---

### MAJ-3: Concurrent-write race on Findings Ledger (§D, §Q11 item 1)

**Location:** Plan §D — findings_ledger.md, Q11 item 1

**Concern:** The Findings Ledger is a single markdown file at `Projects/active_projects/PROJ-XX/findings_ledger.md`. When two phase agents complete simultaneously in a fan-out (e.g., phase B and C are independent and run in parallel), both will attempt to append findings to the same file. The plan has no file-locking, atomic-write, or conflict-resolution mechanism.

The plan's §D description of `phase_complete.py` mentions the review dispatch references the ledger — if both agents read the ledger before either writes, one agent's additions will be silently overwritten when the other writes. This can:
- Lose findings (new entries written by agent A are clobbered by agent B's write)
- Corrupt the markdown table format (partial append during concurrent write)

The `manifest.md` file in 03b has a similar problem, but 03b avoids it by using `FILES_IN_USE` to prevent parallel workers from touching the same project. 03c has no equivalent locking — phase agents within the same project can run concurrently.

**Suggested resolution:** Add file-level locking using `fcntl.lockf` (Unix) / `msvcrt.locking` (Windows) or a `.lock` sidecar file with retry. Alternatively, have `phase_complete.py` write per-phase ledger files (e.g., `findings_ledger_phase_3.md`) and provide a merge script that produces the unified ledger at the coordinator level.

---

### MAJ-4: Partial state after review dispatch failure (§D, phase_complete.py)

**Location:** Plan §D — phase_complete.py description, Q11 item 3

**Concern:** `phase_complete.py` performs this sequence atomically up to the commit:
1. validate_phase.py
2. pytest --testmon (focused)
3. pytest tests/ --testmon (regression)
4. auto-update manifest from diff
5. commit on phase branch
6. merge phase branch into project branch

Then it dispatches the review. If steps 1-6 succeed but review dispatch fails (e.g., `create_review_request.py` crashes, filesystem full, daemon not running), the phase is committed to the project branch but no review was requested. Consequences:

- **Single-parent chains:** The depth-1 buffer says the child can start when parent is committed. The child starts, unaware the review was never dispatched. Downstream grandchild phases block waiting for the grandparent to be verified — which can never happen because the review was never filed.
- **Multi-parent phases:** The multi-parent rule requires all parents to be `verified` — which requires a completed review. The dependent phase blocks indefinitely.
- **Detection:** `pending_reviews.py` would show the phase as "committed" but with no in-flight or completed review — this could be detected as an anomaly, but the plan doesn't describe this case.

**Suggested resolution:** Either (a) make review dispatch part of the atomic block — commit only after the review request file is successfully written, or (b) have `phase_dag.py status` and `pending_reviews.py` explicitly detect the "committed-but-never-reviewed" state and flag it as an anomaly requiring manual intervention. Option (a) is preferred but harder (can't un-commit). Option (b) is pragmatic.

---

### MAJ-5: Depth-1 buffer builds child phases on unverified parent code (§F, constraint #4)

**Location:** Plan §F — eligibility rules, constraint #4, Q2

**Concern:** The single-parent rule allows a child to start when its parent is `committed` (not `verified`). This means:
1. Phase 1 completes and triggers a cumulative review.
2. Phase 2 starts on phase 1's code while phase 1's review is still pending (~2–9 minutes).
3. Phase 1's review returns with findings — phase 1 needs remediation.
4. Phase 2 is already partially or fully built on buggy phase-1 code.

The plan handles this with the scrap-and-restart escape hatch (§G.5), but there's a subtlety: the depth-1 buffer makes this the *normal* operating mode, not an exceptional case. Every phase in a chain starts building before its parent is verified. The scrap path is the safety net, but it's positioned as an "escape hatch" for "large changes" — not for the routine case where the parent's review finds issues.

The user approved this design (constraint #4), but the trade-off should be made explicit: **throughput is prioritized over correctness, with the expectation that reviews rarely find issues requiring remediation of already-built descendant code.** If review findings are frequent, the scrap-and-restart overhead could exceed the throughput gain of the buffer.

**Suggested resolution:** Add an explicit statement in §F about this trade-off. Consider adding a `phase_dag.py` metric: "phases built on unverified parents" count, visible to the user. If the count trends high, the user can tighten the rule (make single-parent also require verified). Keep the depth-1 buffer as a tunable parameter: `BUFFER_DEPTH = 1` with the understanding it can be set to 0 (no buffer — all phases wait for parent verification) if reliability trumps throughput.

---

### MAJ-6: Independent phases lack explicit file-disjointness requirement

**Location:** Plan §B (branch lifecycle), §C (03c protocol), constraint #3

**Concern:** Constraint #3 says "Independent phases (no shared dependency chain) execute in parallel worktrees." But the plan does not require that independent phases modify disjoint files. If phases B and C are both children of A and modify the same file, they will conflict when merged into the project branch.

Protocol 03b enforces this via `manifest.md` — the coordinator refuses to launch two workers whose manifests share any file. Protocol 03c has no equivalent check. The plan's `phase_*_checklist.md` files contain `**Depends on:**` but no file manifest. The `manifest.md` is a project-level file, not per-phase.

Without file-level conflict detection, two parallel phase agents could:
- Both modify the same file on their respective phase branches
- Both merge to the project branch — the second merge produces a conflict
- The second merge fails, leaving the project in a broken state (one phase merged, the other stuck)

**Suggested resolution:** Add a `**Files:**` field to the phase checklist template (analogous to manifest.md) listing files the phase will modify. Have `spawn_phase_worker.py` check for file overlap between eligible parallel phases before launching. If overlap exists, serialize them (mark one as blocked by the other) — or flag it as a planning error and refuse to proceed.

---

## MIN Findings

### MIN-1: No lightweight-phase escape hatch (§G, Q11 item 4)

**Location:** Plan §G, §D (phase_complete.py), Q11 item 4

**Concern:** Every phase fires a full cumulative review + worktree lifecycle, even if the phase is a single trivial task (e.g., update one constant in config.py). The user identified this risk in Q11. For a project with 10 phases each containing 1 small task, the overhead (10 reviews × 2–9 min each = 20–90 min of review latency) could triple wall-clock time.

The plan has no mechanism to designate a phase as "review-exempt" or "inline-only."

**Suggested resolution:** Add a `**Review:** skip` field to the phase checklist template. Phases marked `skip` would still complete normally through `phase_complete.py` but the review dispatch step would be omitted. The Findings Ledger entry for that phase would show no review. The next non-skipped phase's cumulative review would cover the skipped phase's files. Intent is: trivial, mechanical, or single-file changes with no downstream impact can skip the gate.

---

### MIN-2: Hybrid main+branch creates stale plan data on main (§Pushback #3, Q5)

**Location:** Plan §Pushback #3, §B, Q5

**Concern:** The plan keeps planning artifacts on `main` (initial commit from `claude-proj-start`) but moves in-progress updates (Current State, decisions, manifest deltas) to the project branch. During project execution, the plan files on `main` show the pre-execution state. Anyone viewing the project from `main` (other worktrees, the user checking status, parallel project workers reading for context) sees stale data.

The plan acknowledges this trade-off but proposes binary options (all on main vs. all on branch). There's a third option: keep the canonical plan files on `main` and have `claude-proj-continue` commit plan updates to `main` while code changes remain on the project branch. This separates "what is happening" (plan) from "how it's implemented" (code).

**Suggested resolution:** Consider having plan-file updates (Current State, decisions, checkboxes) committed to `main` by `claude-proj-continue` even during project execution. Code changes remain on the project branch. This keeps `main` as the single source of truth for project status without the merge-conflict risk of code on main.

---

### MIN-3: No single "resume project" entry point (§D, Q9)

**Location:** Plan §D — script list, Q9

**Concern:** The plan adds 7 scripts but no single entry point for "resume project PROJ-XX." The agent's workflow on resumption would be:
1. Run `phase_dag.py PROJ-XX eligible` to find what to work on
2. Run `spawn_phase_worker.py PROJ-XX <phase>` to set up the worktree
3. Execute TDD work (03a inner loop)
4. Run `phase_complete.py PROJ-XX <phase>` at phase end
5. Run `pending_reviews.py PROJ-XX` for lookback

This is 5 script invocations per phase, plus understanding the DAG structure each time. A single `phase_lifecycle.py PROJ-XX` entry point with subcommands (`status`, `start-phase`, `complete-phase`, `lookback`) would reduce cognitive load and ensure the agent follows the correct sequence.

**Suggested resolution:** Consider a `phase_lifecycle.py` (or extend `phase_dag.py`) with an orchestrating subcommand that: (a) shows eligible phases, (b) prompts for phase selection, (c) spawns the worktree, (d) runs the TDD inner loop (delegated to 03a), (e) calls phase_complete. This isn't about merging scripts — it's about providing a "happy path" wrapper so the agent doesn't need to remember the full sequence.

---

### MIN-4: 03c document missing structural elements from 03b template (§C, Q8)

**Location:** Plan §C — proposed 03c structure, Q8

**Concern:** The plan sketches 03c's structure and claims it mirrors 03b. Comparing to 03b, the following 03b sections are absent from the 03c sketch:
- **Worker Prompt Template** — 03b has a detailed worker launch template (§Worker Prompt Template). 03c should have an equivalent for phase workers.
- **Error Handling** — 03b has an explicit error-handling table. 03c should describe error scenarios unique to its domain (merge conflicts between parallel phases, review daemon failure, ledger corruption).
- **Concurrency Limits** — 03b explicitly limits to 3 concurrent project workers. 03c should state its intra-project parallelism limits (if any beyond what the DAG enforces).
- **Dashboard Format** — 03b has a dashboard. 03c could benefit from a per-project phase dashboard.

**Suggested resolution:** Add these sections to the final 03c document. The Worker Prompt Template is particularly important — phase workers need to know: their isolated branch, which phases are co-executing (siblings), that they must update the Findings Ledger, and their role in the cumulative review lifecycle.

---

### MIN-5: `.agent_reports/` session directory may conflict with Scratchpad convention (§C, Q7)

**Location:** Plan §C — SESSION_DIR configuration, Q7

**Concern:** The plan uses `.agent_reports/proj-phase-session/{PROJ-ID}` for session state. `AgentCoordination/SCRATCHPAD.md` establishes `AgentCoordination/Scratchpad/` as "the single shared scratch directory for all agents." The plan's `SESSION_DIR` is outside the Scratchpad tree.

Mitigating factors: `.agent_reports/` is already used by 03b (`SESSION_DIR = .agent_reports/proj-session`) and is gitignored, so it's within the repo. CLAUDE.md mentions `.agent_reports/` as an accepted location. However, if multiple systems independently create directories at the repo root, the root-level `.directories/` proliferate over time.

**Suggested resolution:** This is acceptable given existing precedent (03b), but consider whether the session directory should move to `AgentCoordination/Scratchpad/phase_sessions/{PROJ-ID}` for consistency with the Scratchpad convention. The name `proj-phase-session` in `.agent_reports/` is clear and distinguishable from 03b's `proj-session`, so collision is unlikely. Decision: flag for user awareness, not a required change.

---

## NIT Findings

### NIT-1: Windows path handling not addressed in plan (§D, Q11 item 5)

**Location:** Plan §D — script descriptions, Q11 item 5

**Concern:** The plan uses Unix-style path separators throughout (`.worktrees/PROJ-XX/phase-N/`). The user is on Windows. `git worktree` handles path conversion, but Python scripts using string concatenation for paths (`f".worktrees/{PROJ-ID}/phase-{N}"`) would break on Windows. The plan says scripts use `pathlib.Path` (implied by "Each is short glue around git + existing scripts") but doesn't explicitly state it.

**Suggested resolution:** Add a Windows compatibility note to the plan: all scripts must use `pathlib.Path` for path construction, `subprocess.run` with `shell=False`, and `os.replace()` for atomic file writes (already used by `create_review_request.py`). Test on Windows from the start.

---

### NIT-2: Orphaned worktree cleanup is manual-only (§D, cleanup_phase_worktrees.py)

**Location:** Plan §D — cleanup_phase_worktrees.py

**Concern:** `cleanup_phase_worktrees.py` is described as manual — the user or agent must run it. If an agent crashes mid-phase, the worktree persists indefinitely. `git worktree list` would show orphaned entries. The plan mentions no automated cleanup on agent exit or at project completion.

**Suggested resolution:** Have `spawn_phase_worker.py` check for orphaned worktrees before creating a new one — if the previous worktree for the same phase exists but has no active agent, offer to clean it up. Additionally, `phase_dag.py status` should list orphaned worktrees as a warning.

---

### NIT-3: 03c filename naming convention inconsistency (§C)

**Location:** Plan §C — filename

**Concern:** The proposed filename is `03c_phase_review_dag.md`. The other protocols use concise names: `03a_continue_working.md`, `03b_parallel_projects.md`. The compound `phase_review_dag` is harder to parse — is this about "phase review" of a "DAG" or "phase" of a "review DAG"? The plan's own title says "Phase-aware project execution," not "phase review DAG."

**Suggested resolution:** Consider `03c_phase_aware_execution.md` or `03c_cumulative_review_dag.md` for consistency with existing naming patterns. Not a functional concern.

---

### NIT-4: Phase worktree `.gitignore` entry not in the new-files list (§D + new files)

**Location:** Plan new files list

**Concern:** The plan mentions adding `.worktrees/` to `.gitignore` in the "Modified files" list (§Modified files), but the 7 new scripts list doesn't include a `.gitignore` entry for the phase-specific worktree pattern (e.g., `.worktrees/PROJ-XX/phase-*/`). Since the plan says worktrees are gitignored at the top level, this is covered. But any artifact files written by phase agents (temp files, logs) might end up untracked.

**Suggested resolution:** Add `.agent_reports/proj-phase-session/` to `.gitignore` (the plan mentions it as SESSION_DIR but doesn't list it in the .gitignore modification). This is likely already covered by `.agent_reports/` being globally gitignored, but worth verifying.

---

## Additional Observations

### O-1: Well-designed elements worth preserving

The plan has several strong design elements that should survive any revisions:

1. **Cumulative review scope disclosure** (§E) — telling the reviewer "these files are new in phase N, these are context" focuses attention without limiting scope. This is creative and practical.
2. **Depth-1 buffer** — the concept itself is sound for throughput. The concern is about making the trade-off explicit (MAJ-5).
3. **Scrap-and-restart cascade rule** (Pushback #4) — inspecting grand-descendants before scrapping and requiring `--cascade` for full teardown is good safety design.
4. **Phase status derivation from review state** (§D — phase_dag.py status) — tying verification to actual review completion (via `pending_reviews.py`) is more reliable than manual status updates.
5. **Non-migration of 17 active projects** — the explicit non-goal prevents scope creep and avoids breaking working workflow.

### O-2: Test plan adequacy (§Verification)

The verification plan (§Verification) covers the right scenarios (chains, fan-outs, multi-parent merges, remediation, scrap-and-restart, backward compatibility). The synthetic project (`PROJ-TEST-001`) with 4 phases in a specific DAG shape is a good integration test. Suggest adding one more shape: a project with 1-2 phases only (minimal stress test) and a project with a single multi-parent phase (edge case: phases B, C, D all converge on E).

---

## Overall Recommendation

**Proceed with revisions.** Address MAJ-1 through MAJ-6 before implementation begins. MIN findings can be addressed during implementation or deferred to post-implementation polish. NIT findings are at the user's discretion.

**Priority order (blockers first):**

1. **MAJ-4** (partial state after dispatch failure) — simplest to fix, highest operational risk
2. **MAJ-3** (ledger concurrent-write race) — data-loss bug in the core coordination mechanism
3. **MAJ-2** (last-phase verification gap) — structural defect in the review coverage model
4. **MAJ-1** (ledger enables indefinite deferral) — design choice with long-term quality implications
5. **MAJ-6** (file-disjointness for parallel phases) — operational correctness for parallelism
6. **MAJ-5** (depth-1 buffer trade-off) — user-awareness, not a correctness issue; make the trade-off visible

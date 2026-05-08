---
name: claude-proj-from-state-audit
description: Skeptically verify the findings in an ocode-state-audit review and create one or more Projects from the verified set. Bundles by singleton-or-mechanism (not severity); includes all severities. Interactive bundling — proposes a project breakdown then lets the user adjust before creating anything. Surfaces CRITICAL singleton-divergence and shared-state-bug callouts.
disable-model-invocation: true
argument-hint: <path-to-Reviews/results/*_state-audit/ directory>
---

# Project(s) from OpenCode State Audit

**Protocol:** `Projects/protocols/19_create_from_state_audit.md`

Read and follow the full protocol file `Projects/protocols/19_create_from_state_audit.md`.

## Your Role

You are a **skeptical verifier** first and a **Project Architect** second. The `ocode-state-audit` skill (run by OpenCode) has already produced a report with CRITICAL/MAJOR/MINOR findings (`ST-NN-NNN` IDs) covering singleton divergence (a module-level singleton has both `ctx.X` and `get_default_X()` accessors used in different layers), module-level mutable collections, global keyword usages, class-level mutable defaults, `random.seed()` outside the per-battle RNG pattern, and stale `set_default_*` bridge functions whose only caller is `ApplicationContext.create_production()`. It ran an internal verifier over its CRITICAL findings.

Your job is a **third skeptical pass**:

1. Read the cited code at `file:line` for every audit finding (CRITICAL, MAJOR, MINOR). Re-classify each one as VERIFIED, REJECTED, UNCERTAIN, or OUT_OF_SCOPE. Pay special attention to `singleton_divergence` findings — they are the highest-impact category and the verifier must read both `game/context.py` and the consuming layers to confirm `ctx.X` and `get_default_X()` really diverge.
2. **Bundle the VERIFIED set by singleton-or-mechanism, not severity.** Findings that touch the same singleton (e.g. all `RaceRegistry` access-pattern issues) or the same mechanism (e.g. all class-level mutable defaults in the strategy layer) stay together regardless of severity, so implementation can proceed singleton-by-singleton or mechanism-by-mechanism rather than severity-by-severity. The user shapes the final bundling interactively.
3. Build one or more sibling Projects populated only with claims that pass — REJECTED and OUT_OF_SCOPE items are recorded in `findings/verification_report.md` for traceability and dropped from the plan.

**All severities are in scope.** The user has explicitly asked for every issue to be planned. CRITICAL items (singleton with no setter but multiple getters; class-level mutable defaults causing shared-state bugs) get a regression-test checkbox in their phase since they represent silent-corruption and shared-state-bug risk paths.

DISPUTED and INCONCLUSIVE items from OpenCode's own `findings/verification.md` stay **out of scope** — do not promote or re-litigate them. Module-level constants (ALL_CAPS convention) and lazy-loaded caches with proper invalidation are also out of scope per the audit's own scope rules — they are documented infrastructure, not state bugs.

## Argument

`$ARGUMENTS` is the path to a state-audit directory, e.g. `Reviews/results/2026-05-04_113022_state-audit/`. Accept absolute or relative, with or without a trailing slash.

**If `$ARGUMENTS` is empty, automatically pick the most recent `*_state-audit` directory under `Reviews/results/`** (newest by directory-name timestamp; fall back to mtime if names don't sort). Print the chosen path on its own line so the user sees which audit is being processed, then continue without prompting.

**If the resolved directory is the wrong audit type** (`*_error-audit`, `*_type-audit`, or `*_docs-audit`), abort with a clear error pointing to the correct skill.

## Execution (high level — full detail in the protocol file)

1. Resolve and validate the audit path; confirm it ends with `_state-audit` and that `report.md`, `findings/`, and `raw/manifest.json` exist.
2. Parse `report.md` §2 (State Hygiene Scorecard), §3 (Singleton Divergence Risk Map), §4 (ApplicationContext Access Pattern Progress), and §5 (Prioritized Remediation Plan). Hydrate every finding from `findings/state_review_NN.md`, `findings/state_divergence_cross_shard.md`, and `raw/*.json`. Mark items DISPUTED/INCONCLUSIVE in `findings/verification.md` as `OUT_OF_SCOPE`. Mark module-level constants and properly-invalidated lazy caches as `OUT_OF_SCOPE` per the audit's own classification.
3. Dispatch ~4 parallel `Explore` subagents — one per category batch (singleton divergence, module-level mutables + global keyword, class-level mutable defaults + random seed, stale bridge functions). Single message, multiple Agent tool uses. Each agent re-verifies every candidate against cited `file:line` and returns a verdict map. **Singleton-divergence verifiers must read `game/context.py` plus the producing and consuming layers**, not just the cited line.
4. Aggregate verdicts. Compute a default bundling proposal: group VERIFIED items by **singleton-or-mechanism**, then size projects by total volume:
   - V < 30 → ONE project, all singletons/mechanisms in one bundle.
   - 30–100 → 2–3 projects merged by mechanism family (singleton consolidation / collection hygiene / class-default + RNG cleanup).
   - V > 100 → one project per singleton-or-mechanism with ≥10 items.
   Findings touching the same singleton go into the same bundle as their setter/getter cluster (the fix conversation is local to that singleton).
5. Phase D — interactive bundling:
   - Show the proposed bundle table to the user.
   - Use `AskUserQuestion` to accept / merge / split / customize.
   - Walk every UNCERTAIN item with the user (Include / Exclude / Defer).
   - Final confirm before creation.
6. Phase E — for each finalized bundle, call:
   ```bash
   python Projects/scripts/create_project.py "State hygiene — <bundle-summary> (<YYYY-MM-DD of audit>)"
   ```
   Capture each `PROJ-NNN`. Skip any bundle that ended up with zero items.
7. Populate each project from VERIFIED + user-included UNCERTAIN items.
   **You MUST create a non-empty `phase_N_checklist.md` for every phase listed in `plan.md`.** Use `PHASE_TEMPLATE` from `Projects/scripts/create_project.py`. Phases inside each project: Critical → Major → Minor (drop empty). Every CRITICAL singleton-divergence or class-default finding gets a regression-test checkbox in its phase.
8. Write each project's `findings/verification_report.md`, `findings/source_audit.md`, and `findings/bundling_decisions.md` per the protocol.
9. **Refinement Feedback** — write a proposal back to the originating OpenCode skill per `Projects/protocols/15_refinement_feedback.md`. Inputs: `audit_dir`, `source_skill: "ocode-state-audit"`, `audit_name: "state"`, REJECTED findings (with reasons), UNCERTAIN items, audit-missed issues the user flagged during bundling, and the list of `PROJ-NNN` IDs created. Write to `.opencode/skills/ocode-state-audit/refinement_proposals/<today>_<basename(audit_dir)>.md`. If both REJECTED and user_flagged_misses are empty, write a minimal "no refinements suggested this run" proposal and exit. The proposal is for the user to read manually and decide what to merge into `SKILL.md` or `Tools/state_audit/`.

10. Print the hand-off summary: project IDs, project paths, per-bundle counts (`V verified, U_in user-included, R rejected, O out-of-scope`), bundling rationale, CRITICAL singleton-divergence callouts, and one `/claude-proj-continue PROJ-NNN` line per created project.

## Forbidden in this skill

- Modifying production code, tests, docs, or data.
- Acting on any state-audit finding directly (no singletons consolidated, no class-level defaults rewritten, no `set_default_*` functions removed, no `global` keywords stripped). The output is *plans*; implementation happens later in `/claude-proj-continue PROJ-NNN`.
- Promoting DISPUTED or INCONCLUSIVE items from the audit's own `findings/verification.md`.
- Promoting items the audit's own scope rules already exclude (module-level ALL_CAPS constants; lazy caches with documented invalidation; `random.Random(seed)` per-instance pattern).
- Dropping findings on the basis of severity. All severities enter the candidate set; severity drives phase ordering inside a project, not project boundaries.
- Leaving a phase listed in any project's `plan.md` without a populated `phase_N_checklist.md`. A skipped phase is fine; an empty checklist is not.
- Omitting regression-test checkboxes from phases containing CRITICAL singleton-divergence or class-mutable-default findings — these are the highest-impact items and need test coverage.
- Consuming an `*_error-audit/`, `*_type-audit/`, or `*_docs-audit/` directory. Abort cleanly if pointed at one.

## Audit Path

$ARGUMENTS

---
name: claude-proj-from-type-audit
description: Skeptically verify the findings in an ocode-type-audit review and create one or more Projects from the verified set. Bundles by code relatedness (not severity); includes all severities plus the mypy strict-mode migration plan. Interactive bundling — proposes a project breakdown then lets the user adjust before creating anything.
disable-model-invocation: true
argument-hint: <path-to-Reviews/results/*_type-audit/ directory>
---

# Project(s) from OpenCode Type Audit

**Protocol:** `Projects/protocols/13_create_from_type_audit.md`

Read and follow the full protocol file `Projects/protocols/13_create_from_type_audit.md`.

## Your Role

You are a **skeptical verifier** first and a **Project Architect** second. The `ocode-type-audit` skill (run by OpenCode) has already produced a report with CRITICAL/MAJOR/MINOR findings (`TYP-NN-NNN` IDs) plus a 9-layer mypy strict-mode migration plan, and ran an internal verifier over its CRITICAL findings.

Your job is a **third skeptical pass**:

1. Read the cited code at `file:line` for every audit finding (CRITICAL, MAJOR, MINOR, plus the per-layer strict-migration entries). Re-classify each one as VERIFIED, REJECTED, UNCERTAIN, or OUT_OF_SCOPE.
2. **Bundle the VERIFIED set by code relatedness, not severity.** Findings touching the same layer/area stay together regardless of severity, so implementation can proceed file-by-file rather than severity-by-severity. The user shapes the final bundling interactively.
3. Build one or more sibling Projects populated only with claims that pass — REJECTED and OUT_OF_SCOPE items are recorded in `findings/verification_report.md` for traceability and dropped from the plan.

**All severities are in scope.** The user has explicitly asked for every issue to be planned, including the long-tail strict-mode migration. The strategic mypy migration items are bundled into the layer projects they target rather than living in their own separate project.

DISPUTED and INCONCLUSIVE items from OpenCode's own `findings/verification.md` stay **out of scope** — do not promote or re-litigate them.

## Argument

`$ARGUMENTS` is the path to a type-audit directory, e.g. `Reviews/results/2026-05-04_090402_type-audit/`. Accept absolute or relative, with or without a trailing slash.

**If `$ARGUMENTS` is empty, automatically pick the most recent `*_type-audit` directory under `Reviews/results/`** (newest by directory-name timestamp; fall back to mtime if names don't sort). Print the chosen path on its own line so the user sees which audit is being processed, then continue without prompting.

**If the resolved directory is the wrong audit type** (`*_error-audit` or `*_docs-audit`), abort with a clear error pointing to the correct skill.

## Execution (high level — full detail in the protocol file)

1. Resolve and validate the audit path; confirm it ends with `_type-audit` and that `report.md`, `findings/`, and `raw/manifest.json` exist.
2. Parse `report.md` §3 (Critical/Major/Minor findings) and §4 (Mypy Strict-Mode Migration Path). Hydrate every finding from `findings/type_review_NN.md`, `findings/type_flow_cross_layer.md`, and `raw/*.json`. Mark items DISPUTED/INCONCLUSIVE in `findings/verification.md` as `OUT_OF_SCOPE`.
3. Dispatch ~4 parallel `Explore` subagents — one per category batch (narrowable Any returns, missing returns + wrong annotations, type ignores + casts, strict-mode migration). Single message, multiple Agent tool uses. Each agent re-verifies every candidate against cited `file:line` and returns a verdict map.
4. Aggregate verdicts. Compute a default bundling proposal: group VERIFIED items by `layer`, then size projects by total volume:
   - V < 30 → ONE project, all layers in one bundle.
   - 30–100 → 2–3 projects merged by architectural proximity (foundation / domain / presentation).
   - V > 100 → one project per layer with ≥10 items.
5. Phase D — interactive bundling:
   - Show the proposed bundle table to the user.
   - Use `AskUserQuestion` to accept / merge / split / customize.
   - Walk every UNCERTAIN item with the user (Include / Exclude / Defer).
   - Final confirm before creation.
6. Phase E — for each finalized bundle, call:
   ```bash
   python Projects/scripts/create_project.py "Type cleanup — <bundle-summary> (<YYYY-MM-DD of audit>)"
   ```
   Capture each `PROJ-NNN`. Skip any bundle that ended up with zero items.
7. Populate each project from VERIFIED + user-included UNCERTAIN items.
   **You MUST create a non-empty `phase_N_checklist.md` for every phase listed in `plan.md`.** Use `PHASE_TEMPLATE` from `Projects/scripts/create_project.py`. Phases inside each project: Critical → Major → Minor → Strategic (drop empty).
8. Write each project's `findings/verification_report.md`, `findings/source_audit.md`, and `findings/bundling_decisions.md` per the protocol.
9. **Refinement Feedback** — write a proposal back to the originating OpenCode skill per `Projects/protocols/15_refinement_feedback.md`. Inputs: `audit_dir`, `source_skill: "ocode-type-audit"`, `audit_name: "type"`, REJECTED findings (with reasons), UNCERTAIN items, audit-missed type-safety issues the user flagged during bundling, and the list of `PROJ-NNN` IDs created. Write to `.opencode/skills/ocode-type-audit/refinement_proposals/<today>_<basename(audit_dir)>.md`. If both REJECTED and user_flagged_misses are empty, write a minimal "no refinements suggested this run" proposal and exit. The proposal is for the user to read manually and decide what to merge into `SKILL.md` or `Tools/type_audit/`.

10. Print the hand-off summary: project IDs, project paths, per-bundle counts (`V verified, U_in user-included, R rejected, O out-of-scope`), bundling rationale, and one `/claude-proj-continue PROJ-NNN` line per created project.

## Forbidden in this skill

- Modifying production code, tests, docs, or data.
- Acting on any type-audit finding directly (no annotations, no narrowing, no mypy fixes). The output is *plans*; implementation happens later in `/claude-proj-continue PROJ-NNN`.
- Promoting DISPUTED or INCONCLUSIVE items from the audit's own `findings/verification.md`.
- Dropping findings on the basis of severity. All severities (including STRATEGIC strict-mode entries) enter the candidate set; severity drives phase ordering inside a project, not project boundaries.
- Leaving a phase listed in any project's `plan.md` without a populated `phase_N_checklist.md`. A skipped phase is fine; an empty checklist is not.
- Consuming an `*_error-audit/` or `*_docs-audit/` directory. Abort cleanly if pointed at one.

## Audit Path

$ARGUMENTS

---
name: claude-proj-from-docs-audit
description: Skeptically verify the findings in an ocode-docs-audit review and create one or more Projects from the verified set. Bundles by doc-file-cluster (not severity); includes all severities. Interactive bundling — proposes a project breakdown then lets the user adjust before creating anything. Surfaces dead references and content-accuracy errors with mislead-risk callouts.
disable-model-invocation: true
argument-hint: <path-to-Reviews/results/*_docs-audit/ directory>
---

# Project(s) from OpenCode Docs Audit

**Protocol:** `Projects/protocols/17_create_from_docs_audit.md`

Read and follow the full protocol file `Projects/protocols/17_create_from_docs_audit.md`.

## Your Role

You are a **skeptical verifier** first and a **Project Architect** second. The `ocode-docs-audit` skill (run by OpenCode) has already produced a report with CRITICAL/MAJOR/MINOR findings (`DOC-GN-NNN` IDs) covering dead file references, stale PROJ references, content-accuracy errors against live code, missing documentation, doc staleness, and cross-doc terminology drift / consistency issues. It ran an internal Code-Base Accuracy Validator over its content-accuracy claims (`findings/docs_accuracy_code.md`).

Your job is a **third skeptical pass**:

1. Read the cited doc at `doc_file:line` for every audit finding (CRITICAL, MAJOR, MINOR). For dead-reference findings, also stat the referenced path. For content-accuracy findings, also read the corresponding code under `game/` (or wherever the doc claim points). Re-classify each one as VERIFIED, REJECTED, UNCERTAIN, or OUT_OF_SCOPE. Pay special attention to `content_error` findings — they are the highest-mislead-risk category and the verifier must read enough of both the doc section and the live code to confirm the doc is genuinely wrong.
2. **Bundle the VERIFIED set by doc-file-cluster, not severity.** Findings touching the same doc file (or tightly coupled set of doc files) stay together regardless of severity, so a single editing pass can sweep one document end-to-end. Cross-doc consistency findings get their own bundle. The user shapes the final bundling interactively.
3. Build one or more sibling Projects populated only with claims that pass — REJECTED and OUT_OF_SCOPE items are recorded in `findings/verification_report.md` for traceability and dropped from the plan.

**All severities are in scope.** The user has explicitly asked for every issue to be planned. CRITICAL dead-reference and content-error findings get a regression callout in their phase since they actively mislead developers reading current docs.

DISPUTED and INCONCLUSIVE items from OpenCode's own `findings/docs_accuracy_code.md` stay **out of scope** — do not promote or re-litigate them. Minor typos, formatting preferences, and "this doc should be split" suggestions are also out of scope per the audit's own guidance.

## Argument

`$ARGUMENTS` is the path to a docs-audit directory, e.g. `Reviews/results/2026-05-04_090436_docs-audit/`. Accept absolute or relative, with or without a trailing slash.

**If `$ARGUMENTS` is empty, automatically pick the most recent `*_docs-audit` directory under `Reviews/results/`** (newest by directory-name timestamp; fall back to mtime if names don't sort). Print the chosen path on its own line so the user sees which audit is being processed, then continue without prompting.

**If the resolved directory is the wrong audit type** (`*_type-audit`, `*_error-audit`, or `*_audit-shrink`), abort with a clear error pointing to the correct skill.

## Execution (high level — full detail in the protocol file)

1. Resolve and validate the audit path; confirm it ends with `_docs-audit` and that `report.md`, `findings/`, and `raw/` (with `doc_file_refs.json`, `stale_proj_refs.json`, `doc_staleness.json`, `undocumented_modules.json`, `doc_inventory.json`) exist.
2. Parse `report.md` §2 (Doc Health Scorecard), §3 (Dead Reference Register), §4 (Stale PROJ Reference Register), §5 (Doc Staleness Register), §6 (Undocumented Modules), §7 (Cross-Doc Consistency Issues), and §8 (Prioritized Documentation Update Plan). Hydrate every finding from `findings/docs_review_G1.md` through `docs_review_G6.md`, `findings/docs_consistency_cross.md`, `findings/docs_accuracy_code.md`, and `raw/*.json`. Mark items DISPUTED/INCONCLUSIVE in `findings/docs_accuracy_code.md` as `OUT_OF_SCOPE`. Mark out-of-scope categories (typos, formatting, "split this doc") as `OUT_OF_SCOPE` per the audit's own classification.
3. Dispatch ~4 parallel `Explore` subagents — one per category batch (dead refs + stale PROJs, content-accuracy errors, missing docs + staleness, terminology drift + cross-doc consistency). Single message, multiple Agent tool uses. Each agent re-verifies every candidate against the cited `doc_file:line` AND, for content-accuracy claims, reads the corresponding code under `game/`. Returns a verdict map. **Content-accuracy verifiers must read both the doc section and the live code**, not just the cited line.
4. Aggregate verdicts. Compute a default bundling proposal: group VERIFIED items by `doc_file` (or doc-file-cluster), then size projects by total volume:
   - V < 30 → ONE project, all doc clusters in one bundle.
   - 30–100 → 2–3 projects merged by doc tier (root agent docs + architecture / systems + guides / protocols).
   - V > 100 → one project per doc cluster with ≥10 items.
   Cross-doc consistency findings go into their own dedicated bundle (terminology + cross-references touch many files at once).
5. Phase D — interactive bundling:
   - Show the proposed bundle table to the user.
   - Use `AskUserQuestion` to accept / merge / split / customize.
   - Walk every UNCERTAIN item with the user (Include / Exclude / Defer).
   - Final confirm before creation.
6. Phase E — for each finalized bundle, call:
   ```bash
   python Projects/scripts/create_project.py "Docs cleanup — <bundle-summary> (<YYYY-MM-DD of audit>)"
   ```
   Capture each `PROJ-NNN`. Skip any bundle that ended up with zero items.
7. Populate each project from VERIFIED + user-included UNCERTAIN items.
   **You MUST create a non-empty `phase_N_checklist.md` for every phase listed in `plan.md`.** Use `PHASE_TEMPLATE` from `Projects/scripts/create_project.py`. Phases inside each project: Critical (dead refs, content errors that mislead) → Major (stale PROJ, missing major docs) → Minor (terminology, doc staleness) — drop empty. Every CRITICAL dead-reference or content-error finding gets a verification checkbox in its phase to confirm the fix lands.
8. Write each project's `findings/verification_report.md`, `findings/source_audit.md`, and `findings/bundling_decisions.md` per the protocol.
9. **Refinement Feedback** — write a proposal back to the originating OpenCode skill per `Projects/protocols/15_refinement_feedback.md`. Inputs: `audit_dir`, `source_skill: "ocode-docs-audit"`, `audit_name: "docs"`, REJECTED findings (with reasons), UNCERTAIN items, audit-missed issues the user flagged during bundling, and the list of `PROJ-NNN` IDs created. Write to `.opencode/skills/ocode-docs-audit/refinement_proposals/<today>_<basename(audit_dir)>.md`. If both REJECTED and user_flagged_misses are empty, write a minimal "no refinements suggested this run" proposal and exit. The proposal is for the user to read manually and decide what to merge into `SKILL.md` or `Tools/docs_audit/`.

10. Print the hand-off summary: project IDs, project paths, per-bundle counts (`V verified, U_in user-included, R rejected, O out-of-scope`), bundling rationale, CRITICAL dead-ref / content-error callouts, and one `/claude-proj-continue PROJ-NNN` line per created project.

## Forbidden in this skill

- Modifying any doc, production code, test, or data file. The output is *plans*; doc edits happen later in `/claude-proj-continue PROJ-NNN`.
- Acting on any docs-audit finding directly (no path corrections written, no PROJ statuses updated, no terminology normalizations applied).
- Promoting DISPUTED or INCONCLUSIVE items from the audit's own `findings/docs_accuracy_code.md`.
- Dropping findings on the basis of severity. All severities enter the candidate set; severity drives phase ordering inside a project, not project boundaries.
- Leaving a phase listed in any project's `plan.md` without a populated `phase_N_checklist.md`. A skipped phase is fine; an empty checklist is not.
- Omitting verification checkboxes from phases containing CRITICAL dead-reference or content-error findings — these actively mislead developers and need confirmation that the fix lands.
- Consuming a `*_type-audit/`, `*_error-audit/`, or `*_audit-shrink/` directory. Abort cleanly if pointed at one.

## Audit Path

$ARGUMENTS

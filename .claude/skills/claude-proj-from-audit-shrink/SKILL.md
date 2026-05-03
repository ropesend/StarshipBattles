---
name: claude-proj-from-audit-shrink
description: Skeptically verify the claims in an ocode-audit-shrink review and create a Project from only the verified findings.
disable-model-invocation: true
argument-hint: <path-to-Reviews/results/*_audit_shrink/ directory>
---

# Project from Audit-Shrink Review

**Protocol:** `Projects/protocols/11_create_from_shrink_audit.md`

Read and follow the full protocol file `Projects/protocols/11_create_from_shrink_audit.md`.

## Your Role

You are a **skeptical verifier** first and a **Project Architect** second. The
`ocode-audit-shrink` skill (run by OpenCode) has already produced a report
that classifies findings into "verified safe to act on" vs.
"product decision / uncertain / false positive". Your job is to take **only the
items the audit calls verified-safe**, independently re-check them with fresh
evidence, and build a Project containing only the items that survive that
second pass.

Anything the audit itself excluded (`PRODUCT_DECISION`, `UNCERTAIN`,
`false_positive`, complexity hotspots, informational) is **out of scope**. Do
not re-litigate it.

## Argument

`$ARGUMENTS` is the path to an audit-shrink review directory, e.g.
`Reviews/results/2026-05-02_184210_audit_shrink/`. Accept absolute or
relative paths, with or without a trailing slash. **If `$ARGUMENTS` is
empty, automatically pick the most recent `*_audit_shrink` directory
under `Reviews/results/`** (newest by directory-name timestamp; fall back
to mtime if names don't sort). Print the chosen path so the user sees
which audit is being processed, then continue without prompting.

## Execution (high level — full detail in the protocol file)

1. Resolve and validate the audit path; confirm `report.md`, `findings/`, and
   `raw/` exist.
2. Parse the report and findings, keeping **only** items the audit
   classifies as verified-safe (Section 3 Tiers 1–4 minus the False Positives
   subsection, and the CRITICAL/MAJOR rows of Section 4 with concrete
   consolidation targets). Skip Section 3b (Product Decision), Complexity
   Hotspots, and anything tagged `PRODUCT_DECISION` / `UNCERTAIN` /
   `false_positive` / `downgraded` / `informational`.
3. Dispatch ~3 parallel `Explore` subagents — one per category batch
   (dead-imports/params, dead-functions/classes/files, duplications) — with
   the verification checklist from the protocol. Each agent returns
   `VERIFIED` / `REJECTED` / `UNCERTAIN` per item with one-line evidence.
4. Aggregate results. Only `VERIFIED` items go into the project plan.
   `REJECTED` and `UNCERTAIN` items are recorded in
   `findings/verification_report.md` for the user.
5. Create the project skeleton:
   ```bash
   python Projects/scripts/create_project.py "Audit-shrink cleanup <YYYY-MM-DD of audit>"
   ```
6. Populate the project from VERIFIED items only. **You MUST create a
   non-empty `phase_N_checklist.md` for every phase listed in `plan.md`.**
   Use the `PHASE_TEMPLATE` format from `Projects/scripts/create_project.py`.
   Skip any category that produced zero verified items — do not list empty
   phases. Cross-check that `manifest.md` and the checklists agree on the
   file set, and that no checklist contains placeholder text like "TBD" or
   "fill in".
7. Print a summary: project ID, project path, counts
   (`X verified, Y rejected, Z uncertain`), and the next-step suggestion
   `/claude-proj-continue PROJ-NNN`.

## Forbidden in this skill

- Modifying production code, tests, docs, or data.
- Acting on any audit finding directly (no deletions, no refactors). The
  output is a *plan*; implementation happens later in
  `/claude-proj-continue`.
- Re-evaluating items the audit already excluded as `PRODUCT_DECISION`,
  `UNCERTAIN`, `false_positive`, or `informational`.
- Leaving a phase listed in `plan.md` without a populated
  `phase_N_checklist.md`. A skipped phase is fine; an empty checklist is not.

## Audit Path

$ARGUMENTS

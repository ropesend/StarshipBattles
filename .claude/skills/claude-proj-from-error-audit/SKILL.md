---
name: claude-proj-from-error-audit
description: Skeptically verify the findings in an ocode-error-audit review and create one or more Projects from the verified set. Bundles by code relatedness (not severity); includes all severities. Interactive bundling — proposes a project breakdown then lets the user adjust before creating anything. Surfaces CRITICAL boundary failures with crash-risk callouts.
disable-model-invocation: true
argument-hint: <path-to-Reviews/results/*_error-audit/ directory>
---

# Project(s) from OpenCode Error Audit

**Protocol:** `Projects/protocols/14_create_from_error_audit.md`

Read and follow the full protocol file `Projects/protocols/14_create_from_error_audit.md`.

## Your Role

You are a **skeptical verifier** first and a **Project Architect** second. The `ocode-error-audit` skill (run by OpenCode) has already produced a report with CRITICAL/MAJOR/MINOR findings (`ERR-NN-NNN` IDs) covering broad except hygiene, JSON bypass, generic raise, print/traceback debug, cross-layer error boundaries, LLM context security, and resource cleanup. It ran an internal verifier over its CRITICAL findings.

Your job is a **third skeptical pass**:

1. Read the cited code at `file:line` for every audit finding (CRITICAL, MAJOR, MINOR). Re-classify each one as VERIFIED, REJECTED, UNCERTAIN, or OUT_OF_SCOPE. Pay special attention to `cross_layer_boundary` findings — they are the highest-impact category and the verifier must read enough surrounding code to trace the failure path the audit describes.
2. **Bundle the VERIFIED set by code relatedness, not severity.** Findings touching the same layer/area stay together regardless of severity, so implementation can proceed file-by-file rather than severity-by-severity. The user shapes the final bundling interactively.
3. Build one or more sibling Projects populated only with claims that pass — REJECTED and OUT_OF_SCOPE items are recorded in `findings/verification_report.md` for traceability and dropped from the plan.

**All severities are in scope.** The user has explicitly asked for every issue to be planned. CRITICAL boundary findings get a regression-test checkbox in their phase since they represent crash-and-corruption risk paths.

DISPUTED and INCONCLUSIVE items from OpenCode's own `findings/verification.md` stay **out of scope** — do not promote or re-litigate them. In-memory `json.loads`/`json.dumps` calls (no file I/O) are also out of scope per the audit's own guidance — `json_utils` does not offer in-memory equivalents.

## Argument

`$ARGUMENTS` is the path to an error-audit directory, e.g. `Reviews/results/2026-05-04_090436_error-audit/`. Accept absolute or relative, with or without a trailing slash.

**If `$ARGUMENTS` is empty, automatically pick the most recent `*_error-audit` directory under `Reviews/results/`** (newest by directory-name timestamp; fall back to mtime if names don't sort). Print the chosen path on its own line so the user sees which audit is being processed, then continue without prompting.

**If the resolved directory is the wrong audit type** (`*_type-audit` or `*_docs-audit`), abort with a clear error pointing to the correct skill.

## Execution (high level — full detail in the protocol file)

1. Resolve and validate the audit path; confirm it ends with `_error-audit` and that `report.md`, `findings/`, and `raw/manifest.json` exist.
2. Parse `report.md` §4 (Deterministic Scan Results), §5 (Cross-Layer Error Propagation), and §6 (Prioritized Remediation Plan). Hydrate every finding from `findings/error_review_NN.md`, `findings/error_propagation_cross_layer.md`, and `raw/*.json`. Mark items DISPUTED/INCONCLUSIVE in `findings/verification.md` as `OUT_OF_SCOPE`. Mark in-memory JSON calls and false-positive scanner hits as `OUT_OF_SCOPE` per the audit's own classification.
3. Dispatch ~4 parallel `Explore` subagents — one per category batch (exception hygiene, JSON/IO patterns, cross-layer boundaries, security + miscellaneous). Single message, multiple Agent tool uses. Each agent re-verifies every candidate against cited `file:line` and returns a verdict map. **Cross-layer boundary verifiers must read the full boundary region**, not just the cited line.
4. Aggregate verdicts. Compute a default bundling proposal: group VERIFIED items by `layer`, then size projects by total volume:
   - V < 30 → ONE project, all layers in one bundle.
   - 30–100 → 2–3 projects merged by architectural proximity (foundation / domain / presentation).
   - V > 100 → one project per layer with ≥10 items.
   Cross-layer boundary findings go into the bundle owning the **upstream end** of the boundary (the layer that detects the error).
5. Phase D — interactive bundling:
   - Show the proposed bundle table to the user.
   - Use `AskUserQuestion` to accept / merge / split / customize.
   - Walk every UNCERTAIN item with the user (Include / Exclude / Defer).
   - Final confirm before creation.
6. Phase E — for each finalized bundle, call:
   ```bash
   python Projects/scripts/create_project.py "Error handling cleanup — <bundle-summary> (<YYYY-MM-DD of audit>)"
   ```
   Capture each `PROJ-NNN`. Skip any bundle that ended up with zero items.
7. Populate each project from VERIFIED + user-included UNCERTAIN items.
   **You MUST create a non-empty `phase_N_checklist.md` for every phase listed in `plan.md`.** Use `PHASE_TEMPLATE` from `Projects/scripts/create_project.py`. Phases inside each project: Critical → Major → Minor (drop empty). Every CRITICAL boundary finding gets a regression-test checkbox in its phase.
8. Write each project's `findings/verification_report.md`, `findings/source_audit.md`, and `findings/bundling_decisions.md` per the protocol.
9. Print the hand-off summary: project IDs, project paths, per-bundle counts (`V verified, U_in user-included, R rejected, O out-of-scope`), bundling rationale, CRITICAL boundary callouts, and one `/claude-proj-continue PROJ-NNN` line per created project.

## Forbidden in this skill

- Modifying production code, tests, docs, or data.
- Acting on any error-audit finding directly (no `# Intentional` comments added, no exception handlers wrapped, no JSON calls swapped). The output is *plans*; implementation happens later in `/claude-proj-continue PROJ-NNN`.
- Promoting DISPUTED or INCONCLUSIVE items from the audit's own `findings/verification.md`.
- Dropping findings on the basis of severity. All severities enter the candidate set; severity drives phase ordering inside a project, not project boundaries.
- Leaving a phase listed in any project's `plan.md` without a populated `phase_N_checklist.md`. A skipped phase is fine; an empty checklist is not.
- Omitting regression-test checkboxes from phases containing CRITICAL boundary findings — these are the highest-impact items and need test coverage.
- Consuming a `*_type-audit/` or `*_docs-audit/` directory. Abort cleanly if pointed at one.

## Audit Path

$ARGUMENTS

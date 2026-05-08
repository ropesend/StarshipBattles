---
name: claude-proj-from-pattern-audit
description: Skeptically verify the findings in an ocode-pattern-audit review and create one or more Projects from the verified set. Bundles by code relatedness (layer + pattern-area, not severity); includes all severities. Interactive bundling — proposes a project breakdown then lets the user adjust before creating anything. Surfaces CRITICAL pattern-bypass findings (Registry DI, Facade, layer violations) with architectural-risk callouts.
disable-model-invocation: true
argument-hint: <path-to-Reviews/results/*_pattern-audit/ directory>
---

# Project(s) from OpenCode Pattern Audit

**Protocol:** `Projects/protocols/18_create_from_pattern_audit.md`

Read and follow the full protocol file `Projects/protocols/18_create_from_pattern_audit.md`.

## Your Role

You are a **skeptical verifier** first and a **Project Architect** second. The `ocode-pattern-audit` skill (run by OpenCode) has already produced a report with CRITICAL/MAJOR/MINOR findings (`PAT-NN-NNN` IDs) covering layer dependency violations, pattern bypass (Registry DI #3, Facade #5, CQRS-lite #6, Protocol+TypeGuard #2, CommandHandlerRegistry #7, Ability aggregation #14, Scope-Driven Team Routing #25, Ability-Stat Registry #26, Strategy Modal Window #31, etc.), naming collisions, configuration class deviations, undocumented patterns observed in code, pattern documentation drift, and LOC ceiling violations. It ran an internal verifier over its CRITICAL findings.

Your job is a **third skeptical pass**:

1. Read the cited code at `file:line` for every audit finding (CRITICAL, MAJOR, MINOR). For each one, **also read the cited pattern in `docs/02_PATTERNS.md`** — the audit's claim only makes sense against the documented contract. Re-classify each item as VERIFIED, REJECTED, UNCERTAIN, or OUT_OF_SCOPE. Pay special attention to layer-violation findings — confirm whether the import is a TYPE_CHECKING / documented bridge (benign) or a genuine cross-layer leak.
2. **Bundle the VERIFIED set by layer + pattern-area, not severity.** Findings touching the same layer and pattern stay together (e.g. "Registry DI cleanup in simulation" is one bundle; "Facade integrity in UI" is another), so implementation can proceed file-by-file rather than severity-by-severity. The user shapes the final bundling interactively.
3. Build one or more sibling Projects populated only with claims that pass — REJECTED and OUT_OF_SCOPE items are recorded in `findings/verification_report.md` for traceability and dropped from the plan.

**All severities are in scope**, including STRATEGIC items (undocumented patterns worth documenting). The user has explicitly asked for every issue to be planned. CRITICAL pattern-bypass findings (Registry DI bypass, Facade bypass, real layer violations) get a regression-test or static-guard checkbox in their phase since they represent architectural-decay paths that re-introduce themselves silently.

DISPUTED and INCONCLUSIVE items from OpenCode's own `findings/verification.md` stay **out of scope** — do not promote or re-litigate them. Pattern #30 usage is **out of scope** (documented as superseded by #31; the audit's own guide already excludes it). TYPE_CHECKING imports flagged as layer violations are out of scope (benign by convention). Pattern doc-drift findings where the doc is correct and the code is correct but the verifier merely disagrees with the documented design are out of scope — this protocol fixes drift, not re-litigates pattern decisions.

## Argument

`$ARGUMENTS` is the path to a pattern-audit directory, e.g. `Reviews/results/2026-05-04_090501_pattern-audit/`. Accept absolute or relative, with or without a trailing slash.

**If `$ARGUMENTS` is empty, automatically pick the most recent `*_pattern-audit` directory under `Reviews/results/`** (newest by directory-name timestamp; fall back to mtime if names don't sort). Print the chosen path on its own line so the user sees which audit is being processed, then continue without prompting.

**If the resolved directory is the wrong audit type** (`*_error-audit`, `*_type-audit`, or `*_docs-audit`), abort with a clear error pointing to the correct skill.

## Execution (high level — full detail in the protocol file)

1. Resolve and validate the audit path; confirm it ends with `_pattern-audit` and that `report.md`, `findings/`, and `raw/manifest.json` exist.
2. Parse `report.md` §2 (Layer Dependency Violations), §3 (Pattern Adherence Scorecard), §4 (Architecture Drift Findings), §5 (Documentation Accuracy), §6 (Naming Collision Register), §7 (LOC Ceiling Violations), and §8 (Prioritized Architecture Remediation Plan). Hydrate every finding from `findings/pattern_review_01.md`–`04.md`, `findings/pattern_hunter_cross_shard.md`, `findings/pattern_docs_validator.md`, and `raw/*.json` (`layer_violations.json`, `layer_violations_01..04.json`, `patterns_toc.json`, `protocol_registry.json`, `file_size_violations.txt`). Mark items DISPUTED/INCONCLUSIVE in `findings/verification.md` as `OUT_OF_SCOPE`. Mark Pattern #30 usage and TYPE_CHECKING-only layer crossings as `OUT_OF_SCOPE` per the audit's own classification.
3. Dispatch ~4 parallel `Explore` subagents — one per category batch (layer violations, pattern bypass [Registry DI / Facade / Protocol / CQRS-lite], naming + config + LOC, doc drift + undocumented patterns). Single message, multiple Agent tool uses. **Each agent reads `docs/02_PATTERNS.md` for the pattern numbers cited in its batch before opening any code.** Each agent re-verifies every candidate against cited `file:line` and returns a verdict map.
4. Aggregate verdicts. Compute a default bundling proposal: group VERIFIED items by `(layer, pattern_area)`, then size projects by total volume:
   - V < 30 → ONE project, all (layer, pattern) cells in one bundle.
   - 30–100 → 2–3 projects merged by architectural proximity (e.g. `Registry DI + Facade in simulation/strategy`; `UI pattern bypass + naming collisions`; `Doc drift + undocumented patterns`).
   - V > 100 → one project per (layer, pattern-area) cell with ≥10 items.
   Cross-shard pattern-hunter findings go into the bundle owning the **layer that hosts the bypass site** (UI for Facade bypass, simulation/strategy for Registry DI bypass).
5. Phase D — interactive bundling:
   - Show the proposed bundle table to the user.
   - Use `AskUserQuestion` to accept / merge / split / customize.
   - Walk every UNCERTAIN item with the user (Include / Exclude / Defer).
   - Final confirm before creation.
6. Phase E — for each finalized bundle, call:
   ```bash
   python Projects/scripts/create_project.py "Pattern conformance — <bundle-summary> (<YYYY-MM-DD of audit>)"
   ```
   Capture each `PROJ-NNN`. Skip any bundle that ended up with zero items.
7. Populate each project from VERIFIED + user-included UNCERTAIN items.
   **You MUST create a non-empty `phase_N_checklist.md` for every phase listed in `plan.md`.** Use `PHASE_TEMPLATE` from `Projects/scripts/create_project.py`. Phases inside each project, in order:
   - **Critical** — Registry DI bypass, Facade bypass, layer violations that are NOT TYPE_CHECKING.
   - **Major** — CQRS-lite mutations, Protocol bypass with isinstance(), naming collisions, undocumented patterns recurring in 3+ places.
   - **Minor** — Configuration class convention deviations, pattern documentation drift (small fixes), LOC ceiling violations.
   - **Strategic** — Undocumented patterns worth promoting into `docs/02_PATTERNS.md`, dead pattern-doc cleanup.

   Drop empty phases. Every CRITICAL pattern-bypass finding gets a regression-test or AST static-guard checkbox in its phase (Registry DI bypass especially — PROJ-306 shipped exactly this kind of guard and it's the canonical reference).
8. Write each project's `findings/verification_report.md`, `findings/source_audit.md`, and `findings/bundling_decisions.md` per the protocol.
9. **Refinement Feedback** — write a proposal back to the originating OpenCode skill per `Projects/protocols/15_refinement_feedback.md`. Inputs: `audit_dir`, `source_skill: "ocode-pattern-audit"`, `audit_name: "pattern"`, REJECTED findings (with reasons), UNCERTAIN items, audit-missed pattern issues the user flagged during bundling, and the list of `PROJ-NNN` IDs created. Write to `.opencode/skills/ocode-pattern-audit/refinement_proposals/<today>_<basename(audit_dir)>.md`. If both REJECTED and user_flagged_misses are empty, write a minimal "no refinements suggested this run" proposal and exit. The proposal is for the user to read manually and decide what to merge into `SKILL.md` or `Tools/pattern_audit/`.

10. Print the hand-off summary: project IDs, project paths, per-bundle counts (`V verified, U_in user-included, R rejected, O out-of-scope`), bundling rationale, CRITICAL pattern-bypass callouts, and one `/claude-proj-continue PROJ-NNN` line per created project.

## Forbidden in this skill

- Modifying production code, tests, docs, or data.
- Acting on any pattern-audit finding directly (no imports rewired, no Facade calls inserted, no `get_default_registry_provider()` call sites edited, no doc-drift fixes applied to `docs/02_PATTERNS.md`). The output is *plans*; implementation happens later in `/claude-proj-continue PROJ-NNN`.
- Promoting DISPUTED or INCONCLUSIVE items from the audit's own `findings/verification.md`.
- Promoting Pattern #30 usage as a violation — the docs explicitly mark it superseded by #31, and the audit excludes it.
- Promoting TYPE_CHECKING-only imports as layer violations — they are benign by convention.
- Dropping findings on the basis of severity. All severities (including STRATEGIC undocumented-pattern entries) enter the candidate set; severity drives phase ordering inside a project, not project boundaries.
- Leaving a phase listed in any project's `plan.md` without a populated `phase_N_checklist.md`. A skipped phase is fine; an empty checklist is not.
- Omitting regression-test or static-guard checkboxes from phases containing CRITICAL pattern-bypass findings — these decay silently without enforcement.
- Consuming a `*_error-audit/`, `*_type-audit/`, or `*_docs-audit/` directory. Abort cleanly if pointed at one.

## Audit Path

$ARGUMENTS

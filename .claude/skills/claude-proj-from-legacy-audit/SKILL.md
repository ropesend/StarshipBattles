---
name: claude-proj-from-legacy-audit
description: Skeptically verify the findings in an ocode-legacy-audit review and create one or more Projects from the verified set. Bundles by removal cluster (one project per system being eradicated). Includes all severities. Interactive bundling — proposes a project breakdown then lets the user adjust before creating anything. Surfaces save-migration-code findings as banned-by-CLAUDE.md callouts and zero-call-site aliases as single-PR deletions.
disable-model-invocation: true
argument-hint: <path-to-Reviews/results/*_legacy-audit/ directory>
---

# Project(s) from OpenCode Legacy Audit

**Protocol:** `Projects/protocols/16_create_from_legacy_audit.md`

Read and follow the full protocol file `Projects/protocols/16_create_from_legacy_audit.md`.

## Your Role

You are a **skeptical verifier** first and a **Project Architect** second. The `ocode-legacy-audit` skill (run by OpenCode) has already produced a report with CRITICAL/MAJOR/MINOR/INFO findings (`LEG-NN-NNN` IDs) covering module aliases, `__init__` re-export shims, deprecation markers, wrapper-delegate functions, name-pair drift, save-file migration code, superseded-pattern usage, TYPE_CHECKING-only re-exports, partial protocol implementations, and duplicate systems. It ran an internal verifier over its CRITICAL findings.

Your job is a **third skeptical pass**:

1. Read the cited code at `file:line` for every audit finding (CRITICAL, MAJOR, MINOR — INFO items are explicitly "suspected legacy but unclear" and require user confirmation before they enter any plan). Re-classify each one as VERIFIED, REJECTED, UNCERTAIN, or OUT_OF_SCOPE. Pay special attention to `save_migration_code` findings — these are banned by `CLAUDE.md` ("old saves are disposable") and should always survive verification unless the cited code is provably not migration logic.
2. **Bundle the VERIFIED set by removal cluster, not severity.** Findings touching the same system being eradicated stay together regardless of severity, so deletion can proceed as one coherent removal PR rather than scattered cleanups. The user shapes the final bundling interactively.
3. Build one or more sibling Projects populated only with claims that pass — REJECTED and OUT_OF_SCOPE items are recorded in `findings/verification_report.md` for traceability and dropped from the plan.

**All severities except INFO are in scope by default.** INFO items are surfaced to the user during Phase D and only enter a project if the user explicitly opts them in. Save-migration-code findings get a banned-by-CLAUDE.md callout in their phase since they violate Rule 3 ("Root Cause Fixes — Old saves are disposable").

DISPUTED and INCONCLUSIVE items from OpenCode's own `findings/verification.md` stay **out of scope** — do not promote or re-litigate them.

**Special framing — delete-or-consolidate, not fix-in-place.** Legacy-audit findings are about *removing* code, not extending or wrapping it. Every project this skill creates is a removal/consolidation project. Phases are titled `Delete <symbol>` or `Migrate callers of <symbol> then delete` or `Consolidate <system A> with <system B>`. If a finding cannot be framed as a deletion or consolidation, it is probably a wrong-skill finding and belongs to error-audit or state-audit instead — abort that finding and surface it to the user.

## Argument

`$ARGUMENTS` is the path to a legacy-audit directory, e.g. `Reviews/results/2026-05-04_120000_legacy-audit/`. Accept absolute or relative, with or without a trailing slash.

**If `$ARGUMENTS` is empty, automatically pick the most recent `*_legacy-audit` directory under `Reviews/results/`** (newest by directory-name timestamp; fall back to mtime if names don't sort). Print the chosen path on its own line so the user sees which audit is being processed, then continue without prompting.

**If the resolved directory is the wrong audit type** (`*_error-audit`, `*_type-audit`, `*_state-audit`, or `*_docs-audit`), abort with a clear error pointing to the correct skill.

## Execution (high level — full detail in the protocol file)

1. Resolve and validate the audit path; confirm it ends with `_legacy-audit` and that `report.md`, `findings/`, and `raw/manifest.json` exist.
2. Parse `report.md` (Legacy Inventory by Category, Removal Scorecard, Prioritized Removal Plan). Hydrate every finding from `findings/legacy_review_NN.md`, `findings/legacy_duplicate_systems_cross.md`, and `raw/{module_aliases, init_reexports, deprecation_markers, wrapper_delegates, name_pair_drift, save_migration_code, superseded_pattern_uses, type_checking_only_reexports, optional_protocol_methods}.json`. Mark items DISPUTED/INCONCLUSIVE in `findings/verification.md` as `OUT_OF_SCOPE`. Hold INFO-severity items in a separate "needs user opt-in" bucket — they are not promoted automatically.
3. Dispatch ~4 parallel `Explore` subagents — one per category batch (file-deletion candidates: module_alias + init_reexport_shim + type_checking_only_reexport; wrapper functions: wrapper_delegate + name_pair_drift + partial_protocol_impl; flagged-for-removal: deprecation_marker + superseded_pattern_use; banned-by-policy: save_migration_code + duplicate_system). Single message, multiple Agent tool uses. Each agent re-verifies every candidate against cited `file:line` and returns a verdict map. Verifiers must (a) confirm the symbol is genuinely legacy by reading both the legacy and the replacement code, (b) verify the call-site count by grepping for usages across `game/`, `tests/`, `combat_lab/`, `Tools/`, and (c) for save_migration_code findings, verify the migration handles a save format the codebase no longer supports.
4. Aggregate verdicts. Compute a default bundling proposal: group VERIFIED items by **removal cluster** (the system being eradicated). Each cluster contains the alias + the wrapper functions + the implementation files + the call-sites needing migration for ONE legacy system. Examples: "Remove `LegacyFooManager`", "Eradicate save migration v3→v4", "Consolidate duplicate `AmmoTracker` / `AmmunitionLedger`". A cluster is one project; multiple clusters become sibling projects.
5. Phase D — interactive bundling:
   - Show the proposed bundle table (one row per removal cluster) to the user.
   - Use `AskUserQuestion` to accept / merge / split / customize.
   - Walk every UNCERTAIN item with the user (Include / Exclude / Defer).
   - Walk every INFO item separately with the user (Include / Exclude only — INFO does not get a "Defer" since the audit already deferred it once).
   - Final confirm before creation.
6. Phase E — for each finalized bundle, call:
   ```bash
   python Projects/scripts/create_project.py "Legacy removal — <bundle-summary> (<YYYY-MM-DD of audit>)"
   ```
   Capture each `PROJ-NNN`. Skip any bundle that ended up with zero items.
7. Populate each project from VERIFIED + user-included UNCERTAIN + user-included INFO items.
   **You MUST create a non-empty `phase_N_checklist.md` for every phase listed in `plan.md`.** Use `PHASE_TEMPLATE` from `Projects/scripts/create_project.py`. Phases inside each project are ordered by removal-risk:
   - **Phase 1 — Critical:** save-migration-code (banned by CLAUDE.md) + module aliases / wrapper files with **zero call sites** (single-PR deletion, no migration needed).
   - **Phase 2 — Major:** wrapper functions with non-trivial call sites needing migration; duplicate systems requiring consolidation.
   - **Phase 3 — Minor:** orphan deprecation markers; superseded-pattern uses; stale `set_default_*` bridges; TYPE_CHECKING-only re-exports with low risk.
   Drop empty phases. Every save_migration_code finding gets a `[banned by CLAUDE.md Rule 3]` callout in its checkbox.
8. Write each project's `findings/verification_report.md`, `findings/source_audit.md`, and `findings/bundling_decisions.md` per the protocol.
9. **Refinement Feedback per `Projects/protocols/15_refinement_feedback.md`** — write a proposal back to the originating OpenCode skill. Inputs: `audit_dir`, `source_skill: "ocode-legacy-audit"`, `audit_name: "legacy"`, REJECTED findings (with reasons), UNCERTAIN items, INFO items the user excluded (signals over-eager INFO classification), audit-missed legacy systems the user flagged during bundling, and the list of `PROJ-NNN` IDs created. Write to `.opencode/skills/ocode-legacy-audit/refinement_proposals/<today>_<basename(audit_dir)>.md`. If both REJECTED and user_flagged_misses are empty, write a minimal "no refinements suggested this run" proposal and exit. The proposal is for the user to read manually and decide what to merge into `SKILL.md` or `Tools/legacy_audit/`.
10. Print the hand-off summary: project IDs, project paths, per-bundle counts (`V verified, U_in user-included, I_in INFO-included, R rejected, O out-of-scope`), bundling rationale, save-migration-code callouts, zero-call-site quick-deletion callouts, and one `/claude-proj-continue PROJ-NNN` line per created project.

## Forbidden in this skill

- Modifying production code, tests, docs, or data.
- Acting on any legacy-audit finding directly (no deletions, no inlinings, no caller migrations, no consolidations). The output is *plans*; implementation happens later in `/claude-proj-continue PROJ-NNN`.
- Promoting DISPUTED or INCONCLUSIVE items from the audit's own `findings/verification.md`.
- Treating an INFO-severity finding as actionable without first asking the user. INFO items are explicitly "suspected legacy but unclear" per the source skill's severity guide and require explicit user opt-in during Phase D.
- Dropping findings on the basis of severity (other than INFO opt-in). All non-INFO severities enter the candidate set; severity drives phase ordering inside a project, not project boundaries.
- Leaving a phase listed in any project's `plan.md` without a populated `phase_N_checklist.md`. A skipped phase is fine; an empty checklist is not.
- Omitting the `[banned by CLAUDE.md Rule 3]` callout from any save_migration_code checkbox — this signals to the implementer that the finding is non-negotiable and cannot be downgraded to a "fix in place" alternative.
- Reframing a removal finding as a fix-in-place. Legacy-audit projects are *delete-or-consolidate*. If a finding genuinely belongs to error-audit / state-audit / type-audit, surface it to the user and exclude it.
- Consuming a `*_error-audit/`, `*_type-audit/`, `*_state-audit/`, or `*_docs-audit/` directory. Abort cleanly if pointed at one.

## Audit Path

$ARGUMENTS

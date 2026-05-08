---
name: claude-proj-from-testcoverage-audit
description: Skeptically verify the CONFIRMED gaps in an ocode-testcoverage-audit review and create one or more Projects from the verified set. Bundles by layer + module cluster (not severity); ADVISORY UI items are tracked separately rather than driving new test work. Surfaces Tier 0 zero-coverage modules in non-UI layers as the highest-impact category.
disable-model-invocation: true
argument-hint: <path-to-Reviews/results/*_testcoverage-audit/ directory>
---

# Project(s) from OpenCode Test Coverage Audit

**Protocol:** `Projects/protocols/20_create_from_testcoverage_audit.md`

Read and follow the full protocol file `Projects/protocols/20_create_from_testcoverage_audit.md`.

## Your Role

You are a **skeptical verifier** first and a **Project Architect** second. The
`ocode-testcoverage-audit` skill (run by OpenCode) has already done two passes:
shard discovery agents read every production file in their shard and identified
coverage gaps (Phase 2), and one-per-shard skeptical verification agents
re-read the cited code and emitted CONFIRMED / DISPUTED / INCONCLUSIVE
verdicts (Phase 3). The `SUMMARY.md`, `SUMMARY.json`, and
`VERIFIED_SHARD_*.md` files contain only the CONFIRMED set.

Your job is a **third skeptical pass**:

1. Read the cited production code at `file:line` (and any candidate test files
   that might exercise it indirectly) for every CONFIRMED claim. Re-classify
   each one as VERIFIED, REJECTED, UNCERTAIN, or OUT_OF_SCOPE. Watch
   especially for **indirect coverage** — a higher-level test that exercises
   the cited path through a wrapper without naming the symbol directly.
2. **Bundle the VERIFIED set by layer + module cluster, not severity.**
   Findings in related modules stay together so each project produces tests
   for a coherent slice of the codebase (e.g. "Core math test coverage" is
   one bundle; "Strategy treasury test coverage" is another). Tier 0 modules
   with substantial untested surface get their own bundle.
3. Build one or more sibling Projects populated only with claims that pass —
   REJECTED and OUT_OF_SCOPE items are recorded in
   `findings/verification_report.md` for traceability and dropped from the
   plan.

**ADVISORY items are not in scope by default.** UI rendering and event
handlers are conventionally exercised through manual / integration testing,
not unit tests. They are recorded in a single "UI coverage advisory" tracking
section in the appropriate project's `findings/` directory, not promoted into
phase checklists. The user may explicitly request ADVISORY-in-scope during
interactive bundling; otherwise the default holds.

DISPUTED and INCONCLUSIVE items from OpenCode's own
`VERIFIED_SHARD_*.md` transparency tables stay **out of scope** — do not
promote or re-litigate them.

## Argument

`$ARGUMENTS` is the path to a testcoverage-audit directory, e.g.
`Reviews/results/2026-05-04_175101_testcoverage-audit/`. Accept absolute or
relative, with or without a trailing slash.

**If `$ARGUMENTS` is empty, automatically pick the most recent
`*_testcoverage-audit` directory under `Reviews/results/`** (newest by
directory-name timestamp; fall back to mtime if names don't sort). Print the
chosen path on its own line so the user sees which audit is being processed,
then continue without prompting.

**If the resolved directory is the wrong audit type** (`*_test-review`,
`*_error-audit`, `*_type-audit`, `*_docs-audit`), abort with a clear error
pointing to the correct skill.

## Execution (high level — full detail in the protocol file)

1. Resolve and validate the audit path; confirm it ends with
   `_testcoverage-audit` and that `SUMMARY.md`, `SUMMARY.json`,
   `findings/VERIFIED_SHARD_*.md`, and `raw/manifest.json` exist. Read the
   actual `shard_count` from `manifest.json` — do not assume 18.
2. Parse `SUMMARY.json` for structured findings (the authoritative source)
   and cross-check against `findings/VERIFIED_SHARD_*.md` for the per-shard
   prose detail. Read `raw/coverage_matrix.json` (wrapped as
   `{coverage_source, files: {...}}`), `raw/layer_summary.json`,
   `raw/file_inventory.json`, and `raw/manifest.json` to hydrate any finding
   missing precise location data. Skip every DISPUTED and INCONCLUSIVE row
   in the verified shard reports — those are already filtered. Hold ADVISORY
   items aside in a separate buffer (default: tracking section, not phase
   work).
3. Dispatch **one `Explore` subagent per category cluster in parallel**
   (single message, multiple Agent tool uses). Suggested grouping:
   - **Batch 1 — Tier 0 modules in core / engine / services / assets**
     (foundation layers; highest-impact zero-coverage).
   - **Batch 2 — Tier 0 modules in simulation / strategy / ai / research**
     (domain layers).
   - **Batch 3 — Tier 1 modules + missing error-path / boundary / branch
     gaps** (partial-coverage findings across all non-UI layers).
   - **Batch 4 — UI advisory items** (only verify the audit's classification
     of "rendering vs business logic"; do not promote these into phase
     work unless the user later requests it).

   Each agent re-verifies every CONFIRMED claim against the cited
   production file plus any candidate test files in `coverage_matrix.json`'s
   `candidate_test_files` list, looking for indirect coverage that the
   discovery agent may have missed. Returns a verdict map.
4. Aggregate verdicts. Compute a default bundling proposal: group VERIFIED
   items by `layer + module cluster` (e.g., `core/math`,
   `strategy/treasury`, `simulation/combat/formation`) so each bundle covers
   related code that can be tested file-by-file. Tier 0 modules with ≥10
   untested symbols form their own bundle when standalone makes sense.
   - V < 30 → ONE project, all clusters in one bundle.
   - 30–100 → 2–3 projects merged by layer adjacency
     (foundation / domain / cross-cutting).
   - V > 100 → one project per layer with ≥10 items; smaller layers attach
     to the most adjacent larger one.
5. **Phase D — interactive bundling:**
   - Show the proposed bundle table to the user.
   - Use `AskUserQuestion` to accept / merge / split / customize.
   - Walk every UNCERTAIN item with the user (Include / Exclude / Defer).
   - Ask whether to include ADVISORY items (default: No — tracking only).
   - Final confirm before creation.
6. **Phase E — for each finalized bundle:**
   ```bash
   python Projects/scripts/create_project.py "Test coverage — <bundle> (<YYYY-MM-DD of audit>)"
   ```
   Capture each `PROJ-NNN`. Skip any bundle that ended up with zero items.
7. Populate each project from VERIFIED + user-included UNCERTAIN items.
   **You MUST create a non-empty `phase_N_checklist.md` for every phase
   listed in `plan.md`.** Use `PHASE_TEMPLATE` from
   `Projects/scripts/create_project.py`. Phases inside each project follow
   the default ordering:
   - **Phase 1 — Critical:** Tier 0 modules in core / engine / simulation /
     strategy / services / research / ai / assets (zero unit tests; highest
     impact).
   - **Phase 2 — Major:** Tier 1 modules (imported but no symbols actually
     tested) + missing error-path tests in non-UI layers.
   - **Phase 3 — Minor:** Missing boundary / edge-case / branch-coverage
     gaps in already-tested functions.
   - **Phase 4 — Advisory tracking (optional):** UI rendering / event
     items, listed as a single tracking checklist rather than per-symbol
     test work. Drop the phase entirely if the user did not opt ADVISORY
     into scope; otherwise list as a tracking phase, not a unit-test
     phase.
   Drop empty phases entirely.
8. Each phase checklist contains `Add unit test for <symbol>` items grouped
   by file. The final checkbox per task verifies the new tests pass and run
   in <5s under the standard pytest invocation.
9. **Refinement Feedback** — write a proposal back to the originating
   OpenCode skill per `Projects/protocols/15_refinement_feedback.md`.
   Inputs: `audit_dir` (the testcoverage-audit directory),
   `source_skill: "ocode-testcoverage-audit"`, `audit_name: "testcoverage"`,
   REJECTED findings (with reasons), UNCERTAIN items, audit-missed coverage
   gaps the user flagged during bundling, and the list of `PROJ-NNN` IDs
   created. Write to
   `.opencode/skills/ocode-testcoverage-audit/refinement_proposals/<today>_<basename(audit_dir)>.md`.
   If both REJECTED and user_flagged_misses are empty, write a minimal
   "no refinements suggested this run" proposal and exit. The proposal is
   for the user to read manually and decide what to merge into `SKILL.md`
   or `Tools/testcoverage_audit/`.
10. Print the hand-off summary: project IDs, project paths, per-bundle
    counts (`V verified, U_in user-included, R rejected, O out-of-scope`),
    bundling rationale, Tier 0 module callouts, ADVISORY tracking item
    count (separate from the per-project totals), and one
    `/claude-proj-continue PROJ-NNN` line per created project.

## Forbidden in this skill

- Modifying production code, tests, docs, or data.
- Acting on any testcoverage-audit finding directly (no new test files
  written, no test fixtures added). The output is *plans*; implementation
  happens later in `/claude-proj-continue PROJ-NNN`.
- Promoting DISPUTED or INCONCLUSIVE items from the audit's own
  `VERIFIED_SHARD_*.md` transparency tables — they stay excluded.
- Reading the unverified `SHARD_XX.md` files except where a verified claim
  cites one. Phase-2 raw findings are superseded by Phase-3 verdicts.
- Leaving a phase listed in any project's `plan.md` without a populated
  `phase_N_checklist.md`. A skipped phase is fine; an empty checklist is
  not.
- Promoting ADVISORY UI rendering items into phase checklists by default —
  these stay in the tracking section unless the user explicitly opted them
  into scope during interactive bundling.
- Consuming a `*_test-review/`, `*_error-audit/`, `*_type-audit/`, or
  `*_docs-audit/` directory. Abort cleanly if pointed at one.

## Audit Path

$ARGUMENTS

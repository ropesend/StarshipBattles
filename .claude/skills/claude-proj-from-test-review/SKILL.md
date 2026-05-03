---
name: claude-proj-from-test-review
description: Independently re-verify the CONFIRMED claims in an ocode-test-review report and create three priority-tiered Projects (P0/P1/P2) from only the items that survive the second pass.
disable-model-invocation: true
argument-hint: <path-to-Reviews/results/*_test-review/ directory>
---

# Projects from OpenCode Test Review

**Protocol:** `Projects/protocols/12_create_from_test_review.md`

Read and follow the full protocol file `Projects/protocols/12_create_from_test_review.md`.

## Your Role

You are a **skeptical verifier** first and a **Project Architect** second. The
`ocode-test-review` skill (run by OpenCode) has already done two passes:
shard reviewers found findings (Phase 1), and an independent verifier
re-read each cited file:line and emitted CONFIRMED / DISPUTED / INCONCLUSIVE
verdicts (Phase 3). The `SUMMARY.md` and `VERIFIED_SHARD_*.md` files contain
only the CONFIRMED set.

Your job is a **third skeptical pass**. Read the cited code at `file:line` for
every CONFIRMED claim and re-classify each one as VERIFIED, REJECTED,
NEEDS_REWORK, or OUT_OF_SCOPE. Then build three sibling Projects (one per
priority tier P0/P1/P2 from `SUMMARY.md`) populated only with claims that
pass — REJECTED and OUT_OF_SCOPE items are recorded in
`findings/verification_report.md` for traceability and dropped from the
plan.

DISPUTED and INCONCLUSIVE items from OpenCode's transparency tables stay
**out of scope** — do not promote or re-litigate them.

## Argument

`$ARGUMENTS` is the path to a test-review directory, e.g.
`Reviews/results/2026-05-02_204633_test-review/`. Accept absolute or
relative, with or without a trailing slash. **If `$ARGUMENTS` is empty,
automatically pick the most recent `*_test-review` directory under
`Reviews/results/`** (newest by directory-name timestamp; fall back to
mtime if names don't sort). Print the chosen path on its own line so the
user sees which review is being processed, then continue without prompting.

## Execution (high level — full detail in the protocol file)

1. Resolve and validate the test-review path; confirm `SUMMARY.md`,
   `CROSS_SHARD.md`, all 12 `VERIFIED_SHARD_XX.md`, and `SHARD_CONFIG.json`
   exist.
2. Parse `SUMMARY.md` for category/severity tallies, top-20 highest-impact,
   and the P0/P1/P2 action plan. Parse `VERIFIED_SHARD_XX.md` for full
   per-claim detail. Parse `CROSS_SHARD.md` for APC/DUP/HLP cluster items.
3. Dispatch **3 parallel `Explore` subagents per wave, 5 waves total**
   (one wave per group of shards, plus one wave for cross-shard items).
   Single message per wave with three concurrent Agent calls. Each agent
   re-verifies every CONFIRMED claim in its assigned shard against the
   cited `file:line` and returns a verdict map.
4. Aggregate all verdicts. Group VERIFIED + NEEDS_REWORK items by priority
   tier (CAT-1/2/3 → P0; CAT-4/5/6/7 + APC/DUP/HLP → P1; CAT-8..12 → P2).
5. Create **three sibling projects** by calling
   `python Projects/scripts/create_project.py` three times in sequence:
   ```bash
   python Projects/scripts/create_project.py "Test review P0 dead-trivial cleanup <YYYY-MM-DD of review>"
   python Projects/scripts/create_project.py "Test review P1 brittle-bloated remediation <YYYY-MM-DD>"
   python Projects/scripts/create_project.py "Test review P2 opportunistic polish <YYYY-MM-DD>"
   ```
   Capture each assigned `PROJ-NNN` from the script's stdout. Skip any
   project whose tier ended up with zero items.
6. Populate each project from VERIFIED + NEEDS_REWORK items only.
   **You MUST create a non-empty `phase_N_checklist.md` for every phase
   listed in `plan.md`.** Use the `PHASE_TEMPLATE` format from
   `Projects/scripts/create_project.py`. Skip any category that produced
   zero items — do not list empty phases. Cross-check that `manifest.md`
   and the checklists agree on the file set, and that no checklist
   contains placeholder text like "TBD" or "fill in".
7. Write each project's `findings/verification_report.md` and
   `findings/source_review.md` per the protocol.
8. Print a summary: project IDs, project paths, per-tier counts
   (`X verified, Y needs-rework, Z rejected, W out-of-scope`), and the
   next-step suggestion (one `/claude-proj-continue PROJ-NNN` line per
   created project).

## Forbidden in this skill

- Modifying production code, tests, docs, or data.
- Acting on any test-review finding directly (no deletions, no refactors,
  no parametrize rewrites). The output is *plans*; implementation happens
  later in `/claude-proj-continue PROJ-NNN`.
- Promoting DISPUTED or INCONCLUSIVE items from
  `VERIFIED_SHARD_*.md`'s transparency tables — they stay excluded.
- Reading the unverified `SHARD_XX.md` files except where a verified claim
  cites one. Phase-1 raw findings are superseded by Phase-3 verdicts.
- Leaving a phase listed in any project's `plan.md` without a populated
  `phase_N_checklist.md`. A skipped phase is fine; an empty checklist is
  not.

## Test Review Path

$ARGUMENTS

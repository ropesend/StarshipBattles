---
name: claude-gp-from-audit
description: Create GitHub-backed project(s) from a verified audit/review. Thin dispatcher across audit types. Mandatory blocking codex consult.
disable-model-invocation: true
argument-hint: --type <kind> <path-to-Reviews/results/*/ directory>
---

# Create GP Project(s) from Audit

Skeptically verify the findings in an OpenCode review (or test review) and
create one or more GitHub-backed projects from only the verified set. This
is the GP equivalent of the `claude-proj-from-*` skill family — one
dispatcher across all nine audit types, routing to the existing per-type
protocol for verification + bundling, then to Protocol 01 for GitHub
creation.

## Your Role

**Skeptical Reviewer + Project Manager.** Re-verify the audit's CONFIRMED
claims; bundle the survivors per the type-specific protocol; produce one
or more draft project plans; hand each to Protocol 01.

## Arguments

Parse `$ARGUMENTS`:
- `--type <kind>` — required. One of:
  - `shrink` — ocode-audit-shrink reviews
  - `docs` — ocode-docs-audit reviews
  - `error` — ocode-error-audit reviews
  - `legacy` — ocode-legacy-audit reviews
  - `pattern` — ocode-pattern-audit reviews
  - `state` — ocode-state-audit reviews
  - `test-review` — ocode-test-review reports
  - `testcoverage` — ocode-testcoverage-audit reviews
  - `type` — ocode-type-audit reviews
- `<path>` — required. Path to the review directory under `Reviews/results/`.

**Input:** $ARGUMENTS

## Authority

Same as `/claude-gp-add`.

## Procedure

### Phase A: Type dispatch

Read `--type` and route to the existing per-audit-type protocol for the
verification + bundling logic. This logic is identical to today's local
`claude-proj-from-*` skills and does not need duplication:

| `--type` | Per-type protocol |
|---|---|
| `shrink` | [Projects/protocols/11_create_from_shrink_audit.md](../../../Projects/protocols/11_create_from_shrink_audit.md) |
| `test-review` | [Projects/protocols/12_create_from_test_review.md](../../../Projects/protocols/12_create_from_test_review.md) |
| `type` | [Projects/protocols/13_create_from_type_audit.md](../../../Projects/protocols/13_create_from_type_audit.md) |
| `error` | [Projects/protocols/14_create_from_error_audit.md](../../../Projects/protocols/14_create_from_error_audit.md) |
| `legacy` | [Projects/protocols/16_create_from_legacy_audit.md](../../../Projects/protocols/16_create_from_legacy_audit.md) |
| `docs` | [Projects/protocols/17_create_from_docs_audit.md](../../../Projects/protocols/17_create_from_docs_audit.md) |
| `pattern` | [Projects/protocols/18_create_from_pattern_audit.md](../../../Projects/protocols/18_create_from_pattern_audit.md) |
| `state` | [Projects/protocols/19_create_from_state_audit.md](../../../Projects/protocols/19_create_from_state_audit.md) |
| `testcoverage` | [Projects/protocols/20_create_from_testcoverage_audit.md](../../../Projects/protocols/20_create_from_testcoverage_audit.md) |

**Follow that protocol through verification and bundling** with the
following GP-specific overrides:

- Where the per-type protocol says "create a project at
  `Projects/active_projects/PROJ-NNN/`", STOP at the draft-plan stage. Do NOT
  create the local directory. Capture the draft plan (Goals, Scope, Phases,
  Key Files, design analysis, planned manifest) in memory.
- Where the per-type protocol describes "interactive bundling — proposes a
  project breakdown then lets the user adjust before creating anything",
  keep that interactive step verbatim. The user's approved bundles are the
  inputs to Phase B.

### Phase B: For each verified bundle, delegate to Protocol 01

For each bundle the user approved (often more than one, since audits
typically yield 2-4 parallel projects):

1. Set inputs for Protocol 01:
   - `source = audit-<type>` (e.g., `audit-shrink`, `audit-test-review`)
   - `proj_type` derived from the bundle's character
   - `priority` from the bundle's severity / urgency
   - `draft_plan_body`, `phases`, `design_md`, `manifest_md`, `findings`
     from the bundling output
2. Follow [Projects/gp_protocols/01_create_gp_project.md](../../../Projects/gp_protocols/01_create_gp_project.md)
   end-to-end. Each project gets its own blocking codex consult, its own
   fingerprint, its own asset commit.

The codex consult's bundling question (#4 in Protocol 01 Step 3) asks:
"are the verified findings grouped correctly? Should any be split into a
separate project or merged with an adjacent draft?" — which is the
audit-driven extra-question codex has explicitly endorsed.

### Phase C: Report

After all bundles are processed:

- List each created GP-<n> with its URL and sub-issue URLs
- Total commits (one asset commit per project)
- Any bundles the user rejected during interactive bundling (so the audit
  trail is complete)
- Suggested next: `/claude-gp-continue <first-gp-number>`

## Constraints

- **Re-verify everything.** The audit's CONFIRMED claims are not taken on
  faith — Phase A's per-type protocol drives a skeptical re-verification.
- **Bundle per the per-type protocol.** Don't invent new bundling logic;
  the per-type protocols encode the right groupings (shrink: fixed category;
  test-review: P0/P1/P2; type: strict-mode migration; state:
  singleton-or-mechanism; etc.).
- **Blocking codex consult applies PER PROJECT.** Each bundle is its own
  project and gets its own consult.
- **Sequential execution only in v1** (per Protocol 01).
- **New IDs use `GP-<issue-number>`** (not `PROJ-NNN`).

## Related skills

- `/claude-gp-add` — direct (non-audit-driven) project creation
- `/claude-gp-continue <gp_number>` — start work on a created project
- The legacy `/claude-proj-from-*` family (still active for the existing
  local PROJ-NNN system, but new work should go through this skill)

# Reviews

Code review system for the Starship Battles codebase. Reviews complement
the project (`Projects/`) and ticket (`Tracking/`) workflows: they
identify issues across the code that may or may not become projects.

## Layout

| Path | Purpose |
|------|---------|
| `protocols/` | Numbered protocol files defining each review type's workflow (10 files: general, test-coverage, focused-question, migration, security, performance, technical-debt, consistency, update, review-to-project) |
| `prompts/` | Prompt text files used to drive reviews. One prompt per documented type, plus a couple for specific past migrations (Logger-JSON, Protocol Gap, Architecture Drift). |
| `results/` | Per-review result folders, named `{date}_{type}_{scope}/`. Findings, validated_findings, and any prospective project drafts live here. |
| `scripts/` | Python utilities for creating reviews, compiling findings, validating findings, generating prospective projects, and converting reviews to projects. |
| `reviews_index.md` | The live state file. Every review's date, type, scope, status, and link to its result folder. **Source of truth** for "what's open." |
| `Review_Report_2026_01_27.md` | Historical top-level report from the audit pass on that date; not a template. |

## Status lifecycle

```
In Progress ─┬─► Completed
             ├─► Led to Project (PROJ-XX)
             ├─► Archived
             └─► Abandoned (>60d)   ◄── auto-applied to entries idle >60 days
```

**SLA:** an `In Progress` review must be updated or transitioned to a
terminal state within **60 days**. The validator's `reviews_sla` check
flags violations.

## Naming conventions

- Directory case: **lowercase** — `prompts/`, `protocols/`, `results/`,
  `scripts/`. (Aligns with `Projects/` and `Tracking/`.)
- Result folder name: `{YYYY-MM-DD}[_{HHMMSS}]_{type}_{scope-with-dashes}/`.

## Retired sub-systems

- **Sweep Reviews** (Feb 2026): an experimental codebase-wide
  multi-agent review type that was never paired with a formal protocol.
  The 8 Sweep prompts and the runner are staged at
  `_marked_for_deletion_2026-05-29/Reviews/prompts/`. Existing Sweep
  rows in `reviews_index.md` are kept as historical record but no new
  Sweep reviews should be started. Use the documented review types
  instead.

## Running a review

1. Pick a type from `protocols/` (e.g. `01_general_review.md`,
   `05_security_review.md`).
2. Run the corresponding prompt from `prompts/` (e.g.
   `General Review.txt`, `Security Review.txt`).
3. Results land in `results/{date}_{type}_{scope}/`; add an entry to
   `reviews_index.md` with status `In Progress`.
4. When the review reaches a terminal state, update the row's status.

For converting a review's findings into a project, see
`protocols/10_review_to_project.md`.

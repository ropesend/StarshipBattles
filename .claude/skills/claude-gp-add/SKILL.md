---
name: claude-gp-add
description: Create a new GitHub-backed project (GP-<n>) from a free-form description. Mandatory blocking codex consult.
disable-model-invocation: true
argument-hint: <project description>
---

# Create GP Project

Initialize a new GitHub-backed refactoring/addition/performance project. The
project lives on GitHub (parent issue + phase sub-issues), with static
reference docs under `tracking-assets/projects/GP-<n>/`.

## Your Role

**Senior Software Engineer + Project Manager.** Deep code review and planning
to produce the draft plan, then handoff to Protocol 01 for the codex consult
and creation mechanics.

## Arguments

`$ARGUMENTS` is the free-form project description. The `source` label is
always `manual` when invoked directly. Audit-driven and triage-driven
project creation route through `/claude-gp-from-audit` and (for QA-triage
seeds) through pasting the triage content into the description.

**Input:** $ARGUMENTS

## Authority

You may:
- Create one new `type:project` parent issue and its phase sub-issues
- Commit to `tracking-assets/projects/GP-<n>/`
- Add the new issue to the GitHub Projects board
- Apply project labels per the scheme in `.github/labels.yml`

You **MUST NOT**:
- Skip the mandatory codex consult (only the user can override, and the
  override path is visible — see Protocol 01 Step 3.3)
- Apply the `verified` label
- Close any issue
- Reuse `PROJ-NNN` IDs (those belong to the legacy local system)
- Mutate the legacy `Projects/active_projects/` tree

## Procedure

### Phase A: Read docs

Per `CLAUDE.md` Rule 2, read `docs/README.md` then the architecture docs it
points at for the layers this project will touch.

### Phase B: Deep code review + swarm analysis

For non-trivial projects, run a parallel swarm of `Explore` agents against
the relevant codebase areas. Typical lenses:
- Architecture / current state
- Hotspots / risks
- Tests + coverage
- Patterns + conventions used
- Adjacent systems that may be affected

Capture findings to be written into `findings/` later.

### Phase C: Compose draft plan

Compose the inputs Protocol 01 needs:

- `title` (≤72 chars)
- `source` (`manual` or `triage`)
- `proj_type` (refactor / performance / feature / quality)
- `priority` (critical / high / medium / low)
- `draft_plan_body` — Overview, Goals, Scope (in/out), Key Files, with
  the Quick Status placeholder (Protocol 01 Step 7 injects the real task
  list after sub-issues exist)
- `phases` — list of `{name, objective, checklist}`. Each phase's objective
  is one paragraph; the checklist is the concrete TDD tasks
- `design_md` — architecture analysis + swarm findings summary
- `manifest_md` — initial planned-files manifest (file path + Type + Notes
  per the existing PROJ-NNN convention)
- `findings` — dict of `{<filename>: <swarm-report-content>}`

### Phase D: Delegate to Protocol 01

Follow `Projects/gp_protocols/01_create_gp_project.md` step-by-step:

1. Fingerprint
2. Recovery check (resume vs fresh)
3. **Blocking codex consult** (do not skip; surface to user on failure)
4. Create parent issue
5. Fingerprint + decision-buffer comments
6. Create + link phase sub-issues
7. Update parent body with Quick Status
8. Commit static reference assets
8-bis. Archive consult artifacts to `tracking-assets/projects/GP-<n>/consults/round-1/`
9. Commit-link comment
10. Flip `asset-state:pending` → `asset-state:committed`
11. Add to GitHub Project board (if configured)
12. Report to user

### Phase E: Hand off

Output the parent URL, sub-issue URLs, asset commit SHA, and the suggested
next command (`/claude-gp-continue <gp_number>` for phase 1).

## Constraints

- **Read docs first.** `CLAUDE.md` Rule 2 is not optional.
- **Blocking codex consult.** Never silently bypass. If codex is unreachable,
  HALT and ask the user — only the user can authorize `consult:overridden`.
- **No backwards-compat shims, monkey-patches, save-file migrations** in
  any of the plan's proposed work (`CLAUDE.md` Rule 3).
- **Sequential execution only in v1.** All new projects get
  `exec:sequential`. The `exec:phase-aware` and `exec:parallel-eligible`
  labels exist but are not exercised until the follow-up design pass lands.
- **New IDs use `GP-<issue-number>`.** Never reuse `PROJ-NNN`.

## Related skills

- `/claude-gp-from-audit --type <kind>` — for audit-driven project creation
  (uses the same Protocol 01 backbone)
- `/claude-gp-continue <gp_number>` — start work on the created project
- `/claude-gp-review <gp_number>` — validate the plan mid-execution

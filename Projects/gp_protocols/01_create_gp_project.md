# Protocol 01: Create GP Project

Shared creation procedure for the `claude-gp-*` skill family. Invoked by
`claude-gp-add`, `claude-gp-from-audit`, `claude-gp-revise`, and
`claude-gp-extract-phase`.

The caller composes a draft project plan and passes it through this protocol.
The protocol handles: blocking codex consult, fingerprint idempotency,
GitHub issue + sub-issues creation, asset commit, board write, and the
post-creation `consult:passed` (or `consult:overridden`) state flip.

## Required inputs from the caller

| Input | Type | Description |
|---|---|---|
| `title` | string | Project title (≤72 chars) |
| `source` | enum | One of `manual`, `triage`, `audit-shrink`, `audit-docs`, `audit-error`, `audit-legacy`, `audit-pattern`, `audit-state`, `audit-test-review`, `audit-testcoverage`, `audit-type`, `extract`, `revise` |
| `proj_type` | enum | One of `refactor`, `performance`, `feature`, `quality` |
| `priority` | enum | One of `critical`, `high`, `medium`, `low` |
| `draft_plan_body` | string | The full plan body (Overview, Goals, Scope, Key Files) — becomes the parent issue body. ≤60 KB to leave headroom under GitHub's 65,536-char limit |
| `phases` | list of `{name, objective, checklist}` | Phase breakdown. Each phase becomes a sub-issue. `checklist` is the list of `- [ ]` task items |
| `design_md` | string | Architecture analysis, swarm findings summary — written to `tracking-assets/projects/GP-<n>/design.md` |
| `manifest_md` | string | Initial planned-files manifest — written to `tracking-assets/projects/GP-<n>/manifest.md` |
| `findings` | dict of `{filename: content}` | Optional. Written to `tracking-assets/projects/GP-<n>/findings/<filename>` |
| `extract_parent_gp` | int or null | Set only when `source == extract`. Parent project's GP number for the cross-reference comment |
| `revise_parent_gp` | int or null | Set only when `source == revise`. The closed project whose revision this is |

## Procedure

### Step 1 — Compute draft fingerprint

```python
import hashlib
parts = [
    title.strip(),
    *sorted(line.strip() for line in scope_in_section.splitlines() if line.strip()),
    *sorted(line.strip() for line in scope_out_section.splitlines() if line.strip()),
    *[phase['objective'].strip() for phase in phases],
]
fingerprint = hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()[:16]
```

The fingerprint is short (16 hex chars) and stable across reruns when the
title, scope, and phase objectives haven't changed.

### Step 2 — Recovery check: search for existing fingerprint

Before any new mutation, check whether a previous run already created the
parent issue:

```bash
gh issue list --label "type:project" --state all --search "Fingerprint $fingerprint in:comments" --json number,title,labels
```

If exactly one match returns:
- **Resume mode.** Read its labels and decide which downstream steps still
  need to run. If `asset-state:pending` is set, the issue exists but assets
  weren't committed — continue from Step 6. If `consult:overridden` is set,
  the user already authorized override on a prior attempt — do not re-prompt.
- Skip ahead to the first step whose post-condition isn't satisfied.

If zero matches: proceed to Step 3 (fresh creation).

If multiple matches: HALT and surface to the user. Multiple fingerprint hits
mean a duplicate was created somehow; the user picks which to keep.

### Step 3 — Codex consult (BLOCKING)

3.1. Compose the consult request body at
`AgentCoordination/Scratchpad/Consult/<UTC-timestamp>_gp-create-<slug>/request.md`:

```markdown
# Consult request: review draft project plan

## Project meta
- Title: <title>
- Source: <source>
- Type: <proj_type>
- Priority: <priority>

## Draft plan
<draft_plan_body verbatim>

## Phase breakdown
<phases summarized: name + objective per phase, plus the checklist for each>

## What I'm asking

1. Scope sanity — is the in/out scope coherent? Anything obviously missing, oversized, or belonging in a separate project?
2. Phase ordering — does the sequence make sense given dependencies and the project's TDD / "measure before optimizing" rules?
3. Risks not yet listed — what could go wrong that the draft doesn't acknowledge?
<if source is audit-* or triage:>
4. Bundling — are the verified findings grouped correctly? Should any be split or merged with an adjacent draft?
</if>
```

3.2. Invoke `claude-consult` targeting codex. Wait for `response.md`.

3.3. On timeout / transport failure: do NOT proceed. HALT and surface to the
user:

```
Codex consult timed out / failed.
Options:
  (a) wait and retry — I'll re-invoke the consult
  (b) proceed without consult — requires your explicit confirmation; logs as
      consult:overridden + visible parent comment + board field
  (c) abandon project creation
```

The user picks. Skills CANNOT select option (b) autonomously.

3.4. On success: read `response.md`. For each piece of feedback:
- Incorporate into the draft (edit in place — `draft_plan_body`, `phases`,
  `design_md`, etc.), OR
- Record an explicit `### Rejected feedback — <topic>` block in a **draft
  decision buffer** (in-memory or scratch file) that becomes the first
  parent-issue comment after Step 4.

3.5. Decide whether a second round is warranted. Round 2 triggers when codex
asks for re-review OR when incorporation materially changed scope/phases/risk.
Otherwise stop at round 1. Hard cap: 2 rounds. Beyond that, surface to user.

### Step 4 — Create parent issue

```bash
gh issue create \
  --title "<title>" \
  --body-file <draft_plan_body.md> \
  --label "type:project" \
  --label "priority:<priority>" \
  --label "status:planning" \
  --label "proj-type:<proj_type>" \
  --label "source:<source>" \
  --label "consult:<passed|overridden>" \
  --label "exec:sequential" \
  --label "asset-state:pending"
```

Capture the issue number printed to stdout. From here on, the project is
`GP-<n>`.

### Step 5 — Post fingerprint comment + decision-buffer comment

5.1. Fingerprint comment (the recovery anchor):

```markdown
### Fingerprint <fingerprint>

- Consult leaf: `AgentCoordination/Scratchpad/Consult/<leaf-id>/` (repo-relative)
- Intended assets: `tracking-assets/projects/GP-<n>/`
- Source: <source>
- Created: <UTC ISO 8601>
```

Never publish absolute machine-local paths.

5.2. If the decision buffer is non-empty, post it as the next comment:

```markdown
### Initial decisions

<each "### Rejected feedback — <topic>" block from the consult phase>
```

If the buffer is empty, skip this comment.

5.3. For `source == extract`: post a cross-reference comment:

```markdown
### Extracted from GP-<extract_parent_gp>

Original phase: phase <N> of GP-<extract_parent_gp>. Parent's
phase sub-issue has been closed with a link back here.
```

For `source == revise`: post:

```markdown
### Revision of GP-<revise_parent_gp>

This project adds phases <list> to the closed project GP-<revise_parent_gp>.
```

### Step 6 — Create phase sub-issues and link them

For each phase in `phases` (zero-indexed `i`):

6.1. Create the sub-issue:

```bash
gh issue create \
  --title "GP-<n> Phase <i+1>: <phase.name>" \
  --body-file <phase_body.md> \
  --label "type:project-phase" \
  --label "priority:<priority>" \
  --label "status:pending" \
  --label "phase:<i+1>"
```

Phase body format:

```markdown
> Sub-issue of #<n>. Phase <i+1> of <total>.

## Objective

<phase.objective>

## Tasks

<checklist items as `- [ ]` task list>

## Verification

- [ ] All tasks above complete
- [ ] Tests passing (full sharded suite where the phase's scope warrants)
- [ ] No regression in adjacent areas
- [ ] Status flipped to `status:awaiting-confirmation` by the worker skill

## Decisions

Phase-implementation-only decisions go here as comments. Project-wide
decisions go on the parent issue (#<n>).
```

6.2. Capture the sub-issue number. Link it as a sub-issue of the parent via
REST (the `gh issue create` CLI has no `--parent` flag):

```bash
gh api -X POST "/repos/<owner>/<repo>/issues/<n>/sub_issues" \
  --field "sub_issue_id=<sub_issue_internal_id>"
```

Note: the REST endpoint requires the sub-issue's **internal node ID**, not its
number. Fetch via `gh issue view <sub_number> --json id -q .id` first.

### Step 7 — Update parent body with the phase task list

Edit the parent issue body to inject (or refresh, on a resume) a "Quick
Status" task list at the top, just below the Overview:

```markdown
## Quick Status

- [ ] #<sub_1> — Phase 1: <phase 1 name>
- [ ] #<sub_2> — Phase 2: <phase 2 name>
- ...
```

GitHub renders these as native task-list items linked to sub-issues; closing
a sub-issue auto-checks its box, and the board's native sub-issue progress
field uses these for `% Complete`.

```bash
gh issue edit <n> --body-file <updated_parent_body.md>
```

### Step 8 — Commit static reference assets

Create the directory tree:

```
tracking-assets/projects/GP-<n>/
├── design.md          # from caller
├── manifest.md        # from caller (initial planned-files manifest)
└── findings/          # from caller (optional)
    └── <files>
```

Then commit:

```bash
git add tracking-assets/projects/GP-<n>/
git commit -m "chore(gp): add assets for GP-<n>

Initial design + manifest + findings for project GP-<n>.
See https://github.com/<owner>/<repo>/issues/<n>"
```

Capture the commit SHA for Step 9.

### Step 8-bis — Archive consult artifacts

Copy (do **not** move) `request.md` and `response.md` from the Scratchpad
leaf to the project's asset directory:

```
tracking-assets/projects/GP-<n>/consults/round-1/
├── request.md     # copy from AgentCoordination/Scratchpad/Consult/<leaf>/
└── response.md    # copy from AgentCoordination/Scratchpad/Consult/<leaf>/
```

Do NOT copy `log.txt` unless the consult had a failure the user needs to
inspect. Logs may contain machine-local paths.

Amend the asset commit from Step 8 (it's the same logical commit):

```bash
git add tracking-assets/projects/GP-<n>/consults/
git commit --amend --no-edit
```

If skipped because consult was overridden: skip 8-bis entirely. The
`consult:overridden` label and parent comment carry the audit trail.

### Step 9 — Post commit-link comment

```markdown
### Assets committed

Commit: <sha>
Path: `tracking-assets/projects/GP-<n>/`
Consult archive: `tracking-assets/projects/GP-<n>/consults/round-1/` (or "skipped — see consult:overridden")
```

### Step 10 — Flip asset-state label (atomic)

```bash
gh issue edit <n> \
  --remove-label "asset-state:pending" \
  --add-label "asset-state:committed"
```

Two-flag atomic invocation prevents a window where neither label is set.

### Step 11 — Add to GitHub Project board

If the board is configured (see `SETUP.md`):

```bash
gh project item-add <project-number> --owner <owner> --url <parent-issue-url>
```

Set the custom fields explicitly (do not rely on board automation rules):
- Status = `Planning`
- Phase = `1` (project starts at phase 1)
- Priority = mapped from priority label
- Type = mapped from proj-type label
- Source = mapped from source label
- Consult = mapped from consult label
- Execution = `sequential`

Field-setting commands depend on the field IDs captured during board setup;
see `SETUP.md` for the lookup pattern (`gh project field-list`).

If the board is not configured: log a warning to the user and continue.
The issue still exists with the right labels; board membership can be
added later.

### Step 12 — Report to user

Output:

- Parent issue URL
- All sub-issue URLs
- Asset commit SHA
- Consult outcome (`passed` round-1, `passed` round-2, or `overridden`)
- Board membership (added / skipped if board not configured)
- Next step suggestion: `/claude-gp-continue <n>` to start work on phase 1

## Idempotency invariants

After successful completion, the following must all be true. If any is false
on a resume, redo from the first failing step:

| Invariant | Check |
|---|---|
| Parent issue exists | `gh issue view <n>` returns a `type:project` issue |
| Fingerprint comment posted | search comments for `### Fingerprint <hash>` |
| All N sub-issues exist | `gh api /repos/<owner>/<repo>/issues/<n>/sub_issues` returns N entries |
| Parent body has Quick Status task list | parsed from parent body |
| Asset commit landed | `tracking-assets/projects/GP-<n>/design.md` exists, in HEAD |
| Consult archive present | `tracking-assets/projects/GP-<n>/consults/round-1/response.md` exists (skip if overridden) |
| Commit-link comment posted | search for `### Assets committed` |
| `asset-state:committed` label set | label check |
| Board membership (if configured) | `gh project item-list` finds the issue |

## Failure modes

| Failure | Recovery |
|---|---|
| Codex consult timeout | HALT, surface to user (Step 3.3) |
| `gh issue create` fails | retry once; on second failure HALT and surface |
| Sub-issue REST link fails after `gh issue create` succeeds | retry the REST call only; sub-issue exists, just needs linking |
| Asset commit fails (e.g., hook failure) | fix issue, re-run from Step 8; fingerprint search finds the existing parent |
| Board membership fails | log warning, continue. User can re-add later |

## Constraint reminders

- Never select consult override autonomously.
- Never publish absolute machine-local paths in issue comments.
- Never apply `verified` (user-only).
- Never close any issue (user-only).
- Decisions live as comments. There is no project-local `decisions.md`.
- v1 always uses `exec:sequential`. Do not set `exec:phase-aware` or
  `exec:parallel-eligible` on any new project until the follow-up design
  pass lands.

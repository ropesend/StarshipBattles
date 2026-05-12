# Protocol 02: Continue GP Project (sequential)

Sequential TDD work loop on the active phase of a GP project. Invoked by
`claude-gp-continue`.

**v1 scope:** sequential execution only. Phase-aware (`03c` equivalent) and
inter-project parallelism are deferred to the follow-up design pass.

## Required inputs

| Input | Type | Description |
|---|---|---|
| `gp_number` | int | The parent issue number (e.g., `512` for GP-512) |
| `consult_flag` | bool | Optional `--consult` from the caller; default false |

## Procedure

### Step 1 — Load context

```bash
gh issue view <gp_number> --json title,body,labels,comments
```

Read:
- Parent body (Overview, Goals, Scope, Key Files, Quick Status task list)
- All comments, especially `### Decision N` and `### Status YYYY-MM-DD` entries
- Labels — verify exactly one `status:*`, one `priority:*`, one `proj-type:*`,
  one `source:*`, one `consult:*`, one `exec:*`, one `asset-state:*`

If any invariant is violated: HALT, surface to the user. Don't repair label
state without authorization.

Read the static reference docs:
- `tracking-assets/projects/GP-<n>/design.md`
- `tracking-assets/projects/GP-<n>/manifest.md`
- `tracking-assets/projects/GP-<n>/findings/*.md`

Per `CLAUDE.md` Rule 2 (Documentation First), also read `docs/README.md` and
the architecture docs it points at for the layers this project touches.

### Step 2 — Identify active phase sub-issue

Find the sub-issue with `status:in-progress` if one exists. Otherwise the
lowest-numbered phase sub-issue still in `status:pending` is the active one.

```bash
gh api "/repos/<owner>/<repo>/issues/<gp_number>/sub_issues" --jq '.[] | {number, state, labels: [.labels[].name]}'
```

If all sub-issues are closed: HALT — project is ready for `/claude-gp-audit`.

### Step 3 — Transition active phase to in-progress (atomic)

```bash
gh issue edit <phase_sub_issue> \
  --remove-label "status:pending" \
  --add-label "status:in-progress"
```

Post the start comment on the **phase sub-issue** (not parent):

```bash
gh issue comment <phase_sub_issue> --body "### Phase context loaded — starting work."
```

If this is a resume mid-phase (status was already `status:in-progress`),
skip the transition; just post a `### Resuming work` comment instead.

### Step 4 — Scope drift check (gates the optional per-phase consult)

Before working any tasks, compare the phase's task list (in the sub-issue
body) against what's actually required given the current codebase state.
Material scope changes that trigger an automatic consult:

- A new phase needs to be added to the project to reach the goal
- An existing phase must be removed or reordered
- File scope expands beyond `tracking-assets/projects/GP-<n>/manifest.md`'s
  planned set in a way that materially changes the project's character
- The work converts to an extract / revise scenario (better to spin off a
  new GP)

If any of the above are true OR if `consult_flag == true`:
- Compose a consult per `01_create_gp_project.md` Step 3 (BLOCKING).
- Round number is `current_max_round + 1`.
- Archive to `tracking-assets/projects/GP-<n>/consults/round-<N>/` after.
- Post `### Consult round <N>` comment on parent summarizing changes.

If no scope drift and `consult_flag == false`: skip consult.

### Step 5 — TDD execution loop

For each task in the phase's checklist:

5.1. **Write or identify the failing test first.** Per `CLAUDE.md` Rule 1
(Strict TDD). Run it; confirm it fails.

5.2. Implement the code change.

5.3. Re-run the focused test; confirm it passes.

5.4. Run adjacent tests:
```bash
pytest tests/path/to/relevant/ --testmon
```

5.5. **Update docs in the same change** when behavior, architecture,
workflow, or conventions change. Per `CLAUDE.md` Rule 2.

5.6. Commit:
```bash
git add <files>
git commit -m "<conventional commit> (GP-<gp_number>)

<description>"
```

5.7. Edit the sub-issue body to flip the task's `- [ ]` to `- [x]`:
```bash
gh issue edit <phase_sub_issue> --body-file <updated_body.md>
```

Each task completion is a separate commit. Do not batch.

### Step 6 — Phase verification

After all checklist items are checked:

6.1. Run the full sharded suite where the phase's scope warrants:
```bash
python Tools/test_sharded/test_sharded.py
```
For tiny-scope phases (single file, no architecture change), targeted tests
plus `--testmon` are sufficient. Use judgment.

6.2. Post a phase-complete summary comment on the **phase sub-issue**:
```markdown
### Phase complete

- Tasks: <N>/<N>
- Tests: <suite result>
- Files touched: <list>
- Commits: <list of short SHAs>
- Decisions made: <list, with sub-issue comment links if any>
```

6.3. Cross-reference on parent:
```bash
gh issue comment <gp_number> --body "### Phase <i> complete — see #<phase_sub_issue>"
```

### Step 7 — Phase status transition

```bash
gh issue edit <phase_sub_issue> \
  --remove-label "status:in-progress" \
  --add-label "status:awaiting-confirmation"
```

Then update parent's Quick Status task list to check off the completed phase
(GitHub auto-checks sub-issue boxes when the sub-issue closes — but here we
don't close, we flip to awaiting-confirmation, so update the parent body
explicitly):

```bash
gh issue edit <gp_number> --body-file <updated_parent_body.md>
```

### Step 8 — Update parent Current State

Post a `### Status YYYY-MM-DD` comment on the parent:

```markdown
### Status <UTC date>

- Active Phase: <i> — `status:awaiting-confirmation`
- Last Action: completed all tasks in phase <i>
- Next Action: user verification of phase <i>, then `/claude-gp-continue <gp_number>` for phase <i+1>
- Blockers: <list or "None">
```

### Step 9 — Decide whether to continue or stop

If there are remaining phases AND user hasn't asked you to stop AND context
budget is healthy (~< 80%):
- Loop back to Step 2 for the next phase.

Otherwise:
- Stop. Final status comment on parent should clearly indicate where the
  next session resumes.

### Step 10 — End-of-run report

Output:
- Parent issue URL
- Phases worked this run (numbers)
- Status of each (awaiting-confirmation / still in-progress / pending)
- Files touched (deduped)
- Test results
- Outstanding decisions
- Suggested next command

## Invariants

- Never edit the parent issue body except to refresh the Quick Status task list.
- Never close any issue (user-only).
- Never apply `verified` (user-only).
- One sub-issue in `status:in-progress` at a time (sequential mode).
- One commit per checklist task; no batching.
- TDD discipline: failing test FIRST, then implementation.
- No backwards-compat shims, monkey-patches, save-file migrations
  (per `CLAUDE.md` Rule 3).

## Blocked paths

- **Need clarification:** flip phase sub-issue to `status:needs-clarification`,
  post a question comment, stop the loop. User runs `/claude-gp-answer` (or
  responds in conversation).
- **Material scope drift discovered mid-phase:** flip phase to `status:blocked`,
  surface to user, invoke the consult flow from Step 4 if appropriate, do not
  proceed silently.
- **Pre-existing test failure unrelated to phase:** note in the phase comment,
  do NOT fix as part of this phase (root-cause rule — different problem,
  different ticket), surface to user.

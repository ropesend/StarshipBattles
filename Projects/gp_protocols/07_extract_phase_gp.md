# Protocol 07: Extract Phase from GP Project

Split a phase from an existing GP project into its own project. Invoked by
`claude-gp-extract-phase` when a phase has grown beyond what fits in the
parent project's scope.

The extracted phase becomes a new GP project. The original parent's phase
sub-issue is closed with a link to the new project, and the parent's
remaining phases are renumbered to keep continuity.

## Required inputs

| Input | Type | Description |
|---|---|---|
| `parent_gp_number` | int | The GP whose phase is being extracted |
| `phase_number` | int | Which phase to extract (1-indexed) |

## Procedure

### Step 1 — Load parent context

```bash
gh issue view <parent_gp_number> --json title,body,labels
gh api "/repos/<owner>/<repo>/issues/<parent_gp_number>/sub_issues"
```

Verify:
- Parent exists and is `type:project`
- Phase <phase_number> sub-issue exists and is `status:pending` or
  `status:in-progress` (not closed — closed phases shouldn't be retroactively
  extracted; that's revision territory)
- Parent is not closed

If preconditions fail: HALT and surface.

### Step 2 — Compose extracted project's draft

The new GP inherits scope from the phase being extracted:

- **Title:** `<short description from phase title>` (drop the `GP-N Phase M:` prefix)
- **Source:** `extract`
- **Type:** inherit from parent's `proj-type:*` (override if the extracted
  scope changes character)
- **Priority:** judge from the phase's importance and current pressure
- **Body:** include
  - **Overview** referencing why the phase grew too large for the original
  - **Goals** from the extracted phase's objective
  - **Scope** — what the phase covered, plus any additional sub-phases now
    needed because the work is bigger than originally scoped
  - **Key Files** from the phase's planned touches + new discoveries
- **Phases:** the extracted work re-decomposed into its own phases. The
  original single phase typically becomes 2-5 new phases when it warrants
  extraction. If it would only become 1 phase, the extraction isn't
  justified — push back to the user.
- **design_md:** reference the parent's design + explain the extracted scope
- **manifest_md:** the extracted phase's planned files plus any additions
- **extract_parent_gp:** `<parent_gp_number>`

### Step 3 — Delegate to protocol 01

Pass the draft and `source=extract`, `extract_parent_gp=<parent>` to
`01_create_gp_project.md`. Blocking consult, fingerprint, issue/sub-issue
creation, asset commit all proceed as normal.

The consult's bundling question (#4) becomes "are the extracted phases the
right decomposition of the original single phase, or has it been over-split
/ under-split?"

### Step 4 — Update parent

After GP-<new> is created:

4.1. Close the extracted phase sub-issue on the parent:
```bash
gh issue comment <parent_phase_sub_issue> --body "### Extracted to GP-<new>

This phase grew beyond the parent project's scope and was extracted.
See GP-<new> for the implementation."

gh issue edit <parent_phase_sub_issue> \
  --remove-label "status:pending" \
  --add-label "phase:closed"
# (or remove "status:in-progress" instead if that was the state)

gh issue close <parent_phase_sub_issue> --reason "not planned"
```

4.2. Renumber remaining phase sub-issues. For each phase numbered higher
than the extracted one:
- Update sub-issue title from `GP-<n> Phase <i>: ...` to
  `GP-<n> Phase <i-1>: ...`
- Update `phase:<i>` label to `phase:<i-1>`
- Update parent body's Quick Status task list to reflect the new numbers

4.3. Post a cross-reference comment on the parent:
```markdown
### Phase <extracted_phase_number> extracted to GP-<new> on <UTC date>

Phase grew beyond this project's scope. Remaining phases renumbered.
```

### Step 5 — Report

- New GP-<new> URL with sub-issue URLs
- Parent's updated phase numbering
- Closed parent phase sub-issue link
- Cross-reference comments

## Invariants

- Extraction only applies to `status:pending` or `status:in-progress` phases.
  Closed phases use revision instead.
- If the extracted phase would become a single-phase new project, refuse —
  extraction is for phases that have grown into multi-phase work.
- Blocking codex consult applies (via protocol 01).
- Parent's remaining phases are renumbered atomically. Sub-issue title +
  `phase:*` label + parent body Quick Status must all align.

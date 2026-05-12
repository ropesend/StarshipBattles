# Protocol 05: Close GP Project

Archive a confirmed project. Invoked by `claude-gp-close` after the user
has verified the implementation.

## Required inputs

| Input | Type | Description |
|---|---|---|
| `gp_number` | int | The parent issue number |

## Procedure

### Step 1 — Preflight

Verify the project is in `status:awaiting-confirmation` and that the user
has explicitly authorized closure (the user invoked `/claude-gp-close`).

If status is not `awaiting-confirmation`: HALT and surface — closing is
user-only, and the protocol shouldn't fast-track from in-progress.

If the parent issue has the `verified` label: confirmed user authorization.
If not, but the user is invoking the close skill explicitly, that counts as
explicit authorization; proceed.

### Step 2 — Move assets to archive

```bash
git mv tracking-assets/projects/GP-<n>/ tracking-assets/projects/archived/GP-<n>/
git commit -m "chore(gp): archive assets for GP-<n>

Project verified by user; moving assets to archived/."
```

### Step 3 — Update issue with archive link

Post final comment on parent:

```markdown
### Closed and archived <UTC date>

Assets moved to `tracking-assets/projects/archived/GP-<n>/`.
Commit: <sha>
```

### Step 4 — Atomic label transition to closed terminal

```bash
gh issue edit <gp_number> \
  --remove-label "status:awaiting-confirmation" \
  --add-label "phase:closed"
```

The parent issue is closed by the user (not the skill) via
`gh issue close <gp_number>`. If the user prefers automatic close, they can
delegate that with explicit confirmation in the invoking conversation.

For each sub-issue:
```bash
gh issue edit <phase_sub_issue> \
  --remove-label "status:awaiting-confirmation" \
  --add-label "phase:closed"
gh issue close <phase_sub_issue> --reason "completed"
```

Sub-issues are closed by the skill (they're implementation details of the
parent's authorized closure).

### Step 5 — Board update

Move the parent's board item to the `Closed` view:
```bash
gh project item-edit --id <item-id> --project-id <project-id> --field-id <status-field-id> --single-select-option-id <closed-option-id>
```

### Step 6 — Report

- Parent issue URL
- Archive commit SHA
- Sub-issues closed: <count>
- Parent state: `phase:closed`, ready for user to `gh issue close`

## Invariants

- The user, not the skill, performs the final `gh issue close` on the parent.
- Assets are moved, not deleted. Closed-project history stays readable.
- Sub-issues are closed by the skill since their lifecycle is parent-bound.

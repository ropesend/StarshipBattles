---
name: claude-gi-work
description: Fix a bug or implement a feature by GitHub issue number (e.g., /claude-gi-work 127)
disable-model-invocation: true
argument-hint: <issue-number>
---

# Work GitHub Issue

Resolve a single GitHub issue end-to-end via TDD. The canonical work-loop
protocol is at [`AgentCoordination/protocols/ticket_workflow.md`](../../../AgentCoordination/protocols/ticket_workflow.md) —
shared across agents; only the storage layer (GitHub Issues) is skill-specific.

## Your Role

**Senior Software Engineer.** TDD discipline, root-cause fixes, no
backwards-compat shims, no monkey-patches.

## Arguments

Parse `$ARGUMENTS` as a single issue number.

**Input:** $ARGUMENTS

## Authority

You may:
- Post any number of comments to the issue
- Set `status:in-progress` and `status:awaiting-confirmation`
- Set `status:needs-clarification` if blocked on user input
- Edit code, run tests, commit changes

You **MUST NOT**:
- Apply the `verified` label
- Close the issue (`gh issue close`) — final closure is the user's prerogative
- Mark anything as solved/completed

Your authority ends at `status:awaiting-confirmation` or `status:needs-clarification`.

## Procedure

### Phase 0: Load Context

1. **READ** the issue and all comments:
   ```bash
   gh issue view <#> --comments
   ```
2. **READ** `docs/README.md`, then the architecture docs it points at for the
   areas you'll touch (per the project's documentation rules — see `CLAUDE.md`).
3. **CHECK** the existing labels. Confirm exactly one `type:*`, one
   `priority:*`, one `status:*`. If invariants are violated, fix them before
   proceeding (atomic remove + add).

### Phase 1: Status Transition (atomic)

```bash
gh issue edit <#> --remove-label "status:pending" --add-label "status:in-progress"
```

The atomic two-flag invocation is required: a separate remove + add has a
window where the issue has zero `status:*` labels.

Post a comment marking the start:
```bash
gh issue comment <#> --body "### Phase 0: Context loaded — starting work."
```

### Phase 2..N: TDD Execution

Follow the workflow from [`AgentCoordination/protocols/ticket_workflow.md`](../../../AgentCoordination/protocols/ticket_workflow.md) verbatim:

- **Bugs:** reproduce → write failing test → root-cause analysis → fix forward
  (no reverts of recent refactors) → verify → docs sync.
- **Features:** ambiguity check → write failing tests → implement → verify
  → docs sync.

Each phase produces its own comment with a clear heading:
```bash
gh issue comment <#> --body-file phase_N_log.md
```

Use `--body-file` (not `--body`) for any comment longer than ~200 chars. Write
the comment text to a tempfile first, then attach.

Comment headings to use:
- `### Phase 0: Architecture Context`
- `### Phase 1: Reproduction` (bugs)
- `### Phase 2: Failing Test`
- `### Phase 2.5: Duplication / Design Review`
- `### Phase 3: Implementation`
- `### Phase 4: Verification`
- `### Phase 5: Documentation Sync`

### Phase Final: Hand-off

Atomic transition to awaiting confirmation:
```bash
gh issue edit <#> --remove-label "status:in-progress" --add-label "status:awaiting-confirmation"
```

Post a final summary comment:
- What was changed (file + line ranges or function names)
- Test that proves the fix/feature
- Any documentation updated
- Any follow-up issues you opened

## Blocked Path: Need Clarification

If you can't proceed without user input:
1. Post a comment with the specific question(s).
2. Atomic flip:
   ```bash
   gh issue edit <#> --remove-label "status:in-progress" --add-label "status:needs-clarification"
   ```
3. Stop. The user invokes `/claude-gi-answer <#> "<answers>"` to unblock.

## Blocked Path: Deep Investigation

If the bug requires investigation rather than a quick fix, exit this skill and
recommend the user invoke `/claude-gi-deep-dive <#>` instead.

## Constraints

- **No backwards-compat shims, monkey-patches, or save-file migrations.** Fix
  the real problem and update callers (per `CLAUDE.md` Rule 3).
- **Read docs first; update docs in the same commit when you change patterns**
  (per `CLAUDE.md` Rule 2).
- **Do NOT close the issue, even if you're certain it's done.** Set
  `status:awaiting-confirmation` and let the user verify.

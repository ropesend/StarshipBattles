# Protocol 06: Revise GP Project

Add new phases to a closed (or `awaiting-confirmation`) project based on
real-world usage feedback. Invoked by `claude-gp-revise`.

The revision creates a **new** GP project that references the original via
`source:revise`. The original is left as-is (closed or archived); the
revision carries the new phases and the targeted improvements.

This is structurally different from "add a phase to an open project" (which
is just `/claude-gp-continue` discovering new work). Revision is explicitly
for completed projects whose users found gaps after acceptance.

## Required inputs

| Input | Type | Description |
|---|---|---|
| `original_gp_number` | int | The closed/awaiting-confirmation project this revises |
| `feedback` | string | User-supplied description of what the revision addresses |

## Procedure

### Step 1 — Load original project context

```bash
gh issue view <original_gp_number> --json title,body,labels,comments,state
```

Verify the original is `phase:closed` OR `status:awaiting-confirmation`. If
the original is mid-implementation, refuse — the right action is to extend
that project's phases via `/claude-gp-continue` discovering new work, not
revision.

Read the original's static assets:
- `tracking-assets/projects/GP-<original>/` or
- `tracking-assets/projects/archived/GP-<original>/`

### Step 2 — Compose revision draft

Compose a draft plan for the new project:

- **Title:** `Revise GP-<original>: <short description from feedback>`
- **Source:** `revise`
- **Type:** inherit from original's `proj-type:*` (override if feedback
  changes character — e.g., performance revision of a refactor project)
- **Priority:** judge from feedback severity
- **Body:** include
  - **Overview** referencing the original and what didn't get addressed there
  - **Goals** focused only on the revision's incremental scope
  - **Scope** (in / out) — explicitly out: anything the original already
    completed
  - **Key Files** drawn from the feedback + original's manifest
- **Phases:** new phases addressing the feedback; numbering starts at 1 (the
  revision is its own project, not a continuation)
- **design_md:** reference original's design + what the revision adds
- **manifest_md:** new manifest of files this revision touches
- **revise_parent_gp:** `<original_gp_number>`

### Step 3 — Delegate to protocol 01

Pass the draft and `source=revise`, `revise_parent_gp=<original>` to
`01_create_gp_project.md`. The blocking codex consult, fingerprint
idempotency, issue creation, asset commit, and board write all proceed as
normal.

The consult sees the revision's character explicitly — codex's bundling
question (#4) becomes "are these revision phases the right slice, or should
some belong in the original's history instead?"

### Step 4 — Cross-link on original

After the new GP-<new> is created, post a back-reference comment on
GP-<original>:

```markdown
### Revised by GP-<new> on <UTC date>

User feedback after acceptance led to revision GP-<new>, which adds phases
addressing: <one-line summary from `feedback`>.
```

If GP-<original> is closed: the comment is purely historical (closed issues
still accept comments).

### Step 5 — Report

- New GP-<new> URL
- All sub-issue URLs
- Asset commit SHA
- Cross-reference comment URL on GP-<original>
- Suggested next: `/claude-gp-continue <new>` to start phase 1 of the revision

## Invariants

- Revision is always a new project, never re-opens the original.
- Original's assets stay intact (and remain archived if they were).
- Blocking codex consult applies (via protocol 01).
- `source:revise` label set on the new project for board filtering.

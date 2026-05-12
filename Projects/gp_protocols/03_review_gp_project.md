# Protocol 03: Review GP Project

Mid-project plan validation. Invoked by `claude-gp-review` to surface
plan/codebase drift before more implementation lands.

This protocol does not modify the plan — it produces a findings comment on
the parent issue. The user decides whether to revise.

## Required inputs

| Input | Type | Description |
|---|---|---|
| `gp_number` | int | The parent issue number |

## Procedure

### Step 1 — Load context

Same as `02_continue_gp_project.md` Step 1: parent body, comments, labels,
static assets, relevant docs.

### Step 2 — Spawn five parallel review agents

Use the `Explore` agent in parallel (single message, multiple tool calls).
Each agent gets:
- The parent issue body
- A specific review lens
- An instruction to report findings concisely (< 200 words each)
- The `.agent_reports/<gp-N-review>/` output directory

Lens assignments:

1. **Plan-vs-codebase alignment** — does the plan still describe reality?
   Reference `tracking-assets/projects/GP-<n>/design.md` and verify
   architecturally-sensitive claims against current code.
2. **Phase ordering / dependencies** — are the phases still in the right
   order given completed work? Did completed phases discover anything that
   reorders the remainder?
3. **Scope drift** — has the actual file touch list expanded beyond
   `tracking-assets/projects/GP-<n>/manifest.md`? By how much, and is that
   drift principled or symptomatic?
4. **Test coverage** — are the tests written so far sufficient to guard
   against regression in the touched areas? Note gaps that need backfill.
5. **Risk surface** — what could still go wrong that the plan didn't
   anticipate? What's the highest-risk remaining phase?

### Step 3 — Aggregate findings

Read all five reports. Categorize each finding as:
- **BLOCKER** — plan is materially wrong, project should pause for revision
- **ADVISORY** — plan should be updated but work can continue
- **OBSERVATION** — informational, no action required

### Step 4 — Post review comment on parent

```markdown
### Plan review <UTC date>

Five-agent review run via `/claude-gp-review`. Findings:

#### BLOCKER (<count>)
<list with one-paragraph each>

#### ADVISORY (<count>)
<list>

#### OBSERVATION (<count>)
<list>

#### Recommendation

<one paragraph: continue / revise / surface-to-user>
```

### Step 5 — Optional follow-up

If BLOCKER count > 0: HALT, do not proceed to more work. Suggest user runs
`/claude-gp-revise <gp_number>` or addresses blockers manually.

If only ADVISORY findings: report to user, default to continuing work.

If only OBSERVATIONS: continue.

### Step 6 — Clean up

Delete `.agent_reports/<gp-N-review>/` after the review comment is posted.

### Step 7 — Report to user

- Parent issue URL
- Review comment URL
- Counts per severity
- Recommendation

## Invariants

- Does not modify plan, sub-issues, labels, or assets.
- Does not invoke `claude-consult` (this is a Claude-internal review).
- Does not close any issue.

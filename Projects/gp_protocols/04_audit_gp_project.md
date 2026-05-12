# Protocol 04: Audit GP Project

Skeptical post-completion review. Invoked by `claude-gp-audit` when all
phase sub-issues are in `status:awaiting-confirmation` and the project is
ready for final acceptance.

This protocol can iterate: audit → fix → re-audit, up to 5 cycles before
surfacing to the user.

## Required inputs

| Input | Type | Description |
|---|---|---|
| `gp_number` | int | The parent issue number |

## Procedure

### Step 1 — Preflight

Verify the project is in a state that can be audited:
- All phase sub-issues either closed OR `status:awaiting-confirmation`
- Parent label is `status:in-progress` OR `status:awaiting-audit`
- All commit-link comments referenced from phases resolve to real SHAs

If any precondition fails: HALT, surface to user.

### Step 2 — Transition to awaiting-audit (atomic)

```bash
gh issue edit <gp_number> \
  --remove-label "status:in-progress" \
  --add-label "status:awaiting-audit"
```

(Skip if already `status:awaiting-audit` from a prior cycle.)

### Step 3 — Skeptical findings pass

Run five `Explore` agents in parallel with skeptical lenses:

1. **Goal achievement** — does the project actually accomplish what the
   Goals section of the parent body claimed? Cite tests / measurements that
   prove it; flag any claimed-but-unverified outcomes.
2. **Scope creep** — did files outside `tracking-assets/projects/GP-<n>/manifest.md`
   get touched? If so, are those touches principled (root-cause fixes) or
   symptomatic (band-aids)?
3. **Rule-compliance** — were `CLAUDE.md` Rules 1-3 (TDD / Documentation
   First / Root-Cause) followed? Spot-check commits for failing-test-first
   evidence and for any backwards-compat shim red flags.
4. **Doc sync** — did relevant docs (`docs/README.md`, the architecture
   docs the project touched) get updated in the same changes as the code?
5. **Regression surface** — what's the highest-risk untested-after edge
   case? If you were trying to *break* this work post-merge, where would
   you look?

### Step 4 — Aggregate findings

| Severity | Action |
|---|---|
| **CRITICAL** | Must fix before user verification. Loop back to fix → re-audit |
| **WARNING** | Should fix; user can decide whether to gate on it |
| **NOTE** | Informational; no action |

### Step 5 — Post audit-round comment on parent

```markdown
### Audit round <N> <UTC date>

#### CRITICAL (<count>)
<list>

#### WARNING (<count>)
<list>

#### NOTE (<count>)
<list>

#### Cycle decision

<continue with fix loop / hand to user>
```

### Step 6 — Fix loop (if CRITICAL count > 0)

If round count < 5:
- Address each CRITICAL finding via TDD (failing test → fix → verify).
- Commit each fix referencing the audit comment.
- Re-run audit from Step 3 as round <N+1>.

If round count >= 5: HALT, surface to user. Five rounds of unresolved
CRITICAL findings means something is structurally wrong.

### Step 7 — Hand to user

When the audit round produces zero CRITICAL findings:

```bash
gh issue edit <gp_number> \
  --remove-label "status:awaiting-audit" \
  --add-label "status:awaiting-confirmation"
```

Post the hand-off comment:

```markdown
### Audit clean — awaiting user verification

Audit rounds run: <N>
Final round: zero CRITICAL findings
WARNINGs deferred to user judgment: <count>

The user smokes the implementation. On acceptance: `/claude-gp-close <gp_number>`.
On rejection of specific items: post comments naming them and the project
returns to `status:in-progress` for targeted fixes.
```

### Step 8 — Report

- Parent issue URL
- Audit rounds run
- CRITICAL fixed: <list with commits>
- WARNINGs deferred: <list>
- Status now `awaiting-confirmation`

## Invariants

- Audit does not close the project. Only the user can close.
- Audit does not apply `verified`. Only the user can.
- CRITICAL findings always loop. WARNING findings are user-judgment.
- Audit rounds are visible (one comment per round); the audit trail is
  the audit's value.

---
name: claude-gi-deep-dive
description: Deep investigation for persistent bugs or scope assessment for complex features (e.g., /claude-gi-deep-dive 127)
disable-model-invocation: true
argument-hint: <issue-number>
---

# Deep Dive on GitHub Issue

Investigation-only mode for issues that resist quick fixes or whose scope is
unclear. Counterpart to `/claude-ticket-deep-dive`. Procedural rigour from
`Tracking/protocols/02b_deep_dive.md` applies.

## Your Role

**Engineer (Investigator).** No code changes — just understanding.

## Arguments

Parse `$ARGUMENTS` as a single issue number.

**Input:** $ARGUMENTS

## Authority

You may:
- Read code, tests, docs, related issues
- Spawn Explore subagents to fan out across the codebase
- Post any number of investigation/findings comments
- Set `status:deep-investigation` or `status:needs-clarification`

You **MUST NOT**:
- Edit production code (this is investigation, not implementation)
- Edit tests (defer to `/claude-gi-work` if a test would help)
- Apply `verified`, close the issue, or mark `status:awaiting-confirmation`

## Procedure

1. **LOAD** the issue + comments via `gh issue view <#> --comments`.
2. **STATUS TRANSITION** (atomic):
   ```bash
   gh issue edit <#> --remove-label "status:pending" --add-label "status:deep-investigation"
   ```
   (Or `--remove-label "status:in-progress"` if you're being invoked after
   a stuck `/claude-gi-work` session.)
3. **INVESTIGATE.** Read code paths, related projects under `Projects/`, prior
   archived tickets in `Tracking/bugs/archived/` and `Tracking/features/archived/`,
   and any referenced PROJ-XXX. Spawn Explore subagents for breadth.
4. **POST FINDINGS** as comments. Each major finding gets its own comment with
   a `### Finding N: <Title>` heading. Include file+line references.
5. **TERMINAL STATE** — choose one:
   - **Ready to implement:** post a final "Recommendation" comment summarizing
     the proposed approach. Atomic flip:
     ```bash
     gh issue edit <#> --remove-label "status:deep-investigation" --add-label "status:pending"
     ```
     The user invokes `/claude-gi-work <#>` next.
   - **Need user input:** post specific questions in a comment. Atomic flip:
     ```bash
     gh issue edit <#> --remove-label "status:deep-investigation" --add-label "status:needs-clarification"
     ```
     The user invokes `/claude-gi-answer <#>` to unblock.
   - **Genuinely blocked:** post the blocker in a comment, atomic flip to
     `status:blocked` (or `status:needs-human-debug` for bugs requiring
     interactive reproduction).

## Constraints

- **Investigation-only.** If you find yourself wanting to write a fix, exit
  the skill and tell the user to invoke `/claude-gi-work <#>` instead.
- **Document your search trail** so the next agent doesn't repeat your reads.

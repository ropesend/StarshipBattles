# PROTOCOL 15: Refinement Feedback to OpenCode Audit Skills
**Role:** Sub-protocol invoked by every `claude-proj-from-*` bridge after project creation completes.

**Goal:** Close the feedback loop between Claude's third-pass verification and the OpenCode audit skill that produced the review. After Claude has skeptically verified findings and bundled them into projects, write a structured refinement proposal back to the originating skill so the user can decide what tunings to merge.

This protocol does **not** automatically modify any skill or tool — it produces a proposal file for human review. Skill drift caused by auto-applied refinements is exactly what this manual gate prevents.

---

## When This Protocol Runs

Invoked as the final step of any `claude-proj-from-*` skill (Protocols 11, 12, 13, 14, 16, 17, 18, 19, 20). The bridge skill calls this protocol after:

- Skeptical verification has classified every finding as VERIFIED, REJECTED, UNCERTAIN, or OUT_OF_SCOPE.
- The user has confirmed the project bundling.
- All `Projects/active_projects/PROJ-NNN/` directories have been written.

Skip this protocol only when:

- Zero findings were REJECTED **and** the user did not flag any missing checks during bundling. (No useful signal to feed back.)
- The user explicitly says "skip refinements."

---

## Inputs

The bridge skill passes the following to this protocol:

| Field | Source | Example |
|-------|--------|---------|
| `audit_dir` | The original review directory | `Reviews/results/2026-05-04_090436_error-audit/` |
| `source_skill` | The OpenCode skill name | `ocode-error-audit` |
| `audit_name` | Short audit identifier | `error` |
| `verified_findings` | List of VERIFIED findings | (from bridge's working memory) |
| `rejected_findings` | List of REJECTED findings with rejection reason | (from bridge's working memory) |
| `uncertain_findings` | List of UNCERTAIN findings with the question | (from bridge's working memory) |
| `user_flagged_misses` | Issues the user spotted that the audit didn't | (collected during interactive bundling) |
| `created_projects` | List of `PROJ-NNN` IDs created | `["PROJ-312", "PROJ-313"]` |

If `user_flagged_misses` is empty and `rejected_findings` is empty, write only a minimal proposal noting "no refinements suggested this run" and exit.

---

## Output

Write a single proposal file to:

```
.opencode/skills/<source_skill>/refinement_proposals/<YYYY-MM-DD>_<reviewdir>.md
```

Where:
- `<YYYY-MM-DD>` is the date the proposal is written (today, not the audit date).
- `<reviewdir>` is the basename of `audit_dir` (e.g. `2026-05-04_090436_error-audit`).

If the directory does not exist, create it. Do not move or modify any other file in the OpenCode skill folder — this is the only path this protocol writes to.

---

## Proposal Structure

The file is Markdown with a strict schema. The `claude-proj-from-*` bridge populates it; the user reads it and manually merges actionable items into `SKILL.md`.

```markdown
---
source_skill: <source_skill>
audit_dir: <audit_dir>
generated_by: <bridge_skill>
generated_at: <YYYY-MM-DD>
created_projects: [PROJ-NNN, PROJ-NNN]
verified_count: N
rejected_count: N
user_flagged_misses_count: N
status: pending_review
---

# Refinement Proposal — <audit_name> audit

Generated after `<bridge_skill>` processed `<audit_dir>` and created
<created_projects>.

This proposal is **suggestions only**. The user decides which items, if any,
to merge into `.opencode/skills/<source_skill>/SKILL.md` or its underlying
`Tools/<audit_name>_audit/` scripts.

## 1. False-Positive Patterns

For each REJECTED finding, propose a concrete rule the audit could use to
avoid raising it next time. One section per pattern; consolidate repeated
patterns across multiple findings into a single proposal.

### FP-1: <short pattern name>

- **Examples (rejected findings):**
  - `<finding_id>` — `<file>:<line>` — rejected because: `<reason>`
  - (additional findings sharing this pattern)
- **Proposed filter:**
  - **Phase 1 deterministic** (preferred when possible): `<concrete check the
    Tools/<audit_name>_audit/ scanner could perform to suppress this case>`
  - **Phase 2 prompt guidance** (when the check needs human-like judgment):
    `<text to add to the agent's "What NOT to Report" section>`
- **Risk of filtering:** `<what legitimate findings might also be suppressed>`
- **Recommendation:** ADD_TO_TOOL | ADD_TO_PROMPT | DISCUSS

(Repeat for each distinct false-positive pattern.)

## 2. Missing Checks

For each item in `user_flagged_misses` (and any pattern the bridge noticed
the audit systematically missed), propose a check to add.

### MC-1: <short check name>

- **What was missed:** `<the issue category>`
- **Examples (user-flagged):**
  - `<file>:<line>` — `<description>`
- **Why the audit missed it:**
  - `<honest analysis: was this beyond the audit's scope, or a gap in coverage?>`
- **Proposed addition:**
  - **Phase 1 deterministic:** `<scanner check to add, with rough heuristic>`
  - **Phase 2 prompt:** `<methodology bullet to add to agent template>`
- **Estimated false-positive rate:** LOW | MEDIUM | HIGH
- **Recommendation:** ADD_TO_TOOL | ADD_TO_PROMPT | DISCUSS

(Repeat for each missing check.)

## 3. Severity Calibration

If a category of findings was systematically over- or under-classified during
verification, propose a severity adjustment. Only include this section when
the calibration error is consistent across 3+ findings.

### SC-1: <category>

- **Audit assigned:** CRITICAL (N findings)
- **Verifier reclassified:** MAJOR (N), MINOR (N)
- **Pattern:** `<what makes this category often less severe than the audit thinks>`
- **Proposed change:** Update the severity guide in the agent template:
  ```
  CURRENT: <quoted current text>
  PROPOSED: <quoted replacement>
  ```
- **Recommendation:** ADD_TO_PROMPT | DISCUSS

## 4. Phase 1 Tool Bugs

Anything that suggests the deterministic scanner produced bad raw data —
files missed, false patterns matched, schema drift. These items often have
higher leverage than prompt tweaks because they fix the input the agents see.

### TB-1: <short bug name>

- **Symptom:** `<what went wrong in the raw output>`
- **Reproduction:** `<minimal command + expected vs actual>`
- **Likely fix location:** `Tools/<audit_name>_audit/<file>.py`
- **Recommendation:** ADD_TO_TOOL | DISCUSS

## 5. UNCERTAIN Items Worth Skill Attention

UNCERTAIN findings that the verifier couldn't decide on — list any that
suggest the audit is operating in a genuinely ambiguous zone. These are
candidates for either tighter audit guidance or broader scope.

| Finding ID | File:Line | Category | Why uncertain | Suggestion |
|------------|-----------|----------|---------------|------------|

## 6. Disposition Notes (free-form)

Any additional observations that don't fit the categories above — patterns
the user noticed, suggestions for the next audit run, scope changes worth
considering. Keep brief.

---

**Next step (for the user):**

1. Read this proposal end-to-end.
2. For each `ADD_TO_PROMPT` item: edit the relevant section in
   `.opencode/skills/<source_skill>/SKILL.md`.
3. For each `ADD_TO_TOOL` item: edit the corresponding script under
   `Tools/<audit_name>_audit/`.
4. For `DISCUSS` items: raise with the team or in a tracking ticket.
5. Once merged or rejected, update the frontmatter `status:` to `merged`,
   `rejected`, or `partial` — or just delete the proposal file.
```

---

## Authoring Rules for the Bridge Skill

1. **Be honest about uncertainty.** If a REJECTED finding was rejected for a reason that's hard to encode as a rule, mark it `DISCUSS` rather than inventing a brittle filter.
2. **Prefer Phase 1 (tool) fixes over Phase 2 (prompt) fixes** when both are feasible. Tools are deterministic and cheap; prompts grow over time.
3. **Don't propose changes that would conflict with the skill's stated scope.** If the audit explicitly excludes UI rendering code (per its severity guide), don't propose adding UI-rendering checks via this protocol — the user already decided that's out of scope.
4. **Quote concrete code/text** when proposing prompt edits. Avoid hand-waving.
5. **Cap each proposal section at 5 items.** If the bridge has more than 5 false-positive patterns to surface, consolidate or take the top 5 by impact. The proposal is for human review — long lists go unread.
6. **Single proposal file per run.** Do not split into multiple files even when the audit produces multiple projects.

---

## What This Protocol Does NOT Do

- Does not edit `SKILL.md` or any tool source.
- Does not delete or modify previous proposals (each run produces a new dated file; the user manages cleanup).
- Does not gate project creation. If proposal generation fails, log the failure and continue — project creation has already happened by the time this protocol runs.
- Does not promote `OUT_OF_SCOPE` items to refinements. Out-of-scope means out-of-scope.
- Does not enforce a refinement cadence. The user decides when to read pending proposals.

---
name: claude-qa-triage
description: Process QA session logs into GitHub issues (bugs/features) and Projects/Triage/ files (prospective projects), through interactive triage.
disable-model-invocation: true
argument-hint: [session_directory_name] (e.g., 20260314_074413, or omit for latest)
---

# QA Session Triage

Process a QA Observer session log interactively, categorising each observation as a Bug, Feature, Prospective Project, or acting on existing bug fixes (reject/approve).

Bugs and features become GitHub issues; prospective projects become `Projects/Triage/<name>.md` files on disk.

## Your Role

Adopt the **QA Analyst / Technical Investigator** persona. You walk through each observation with the user, perform code review to understand context, check for duplicates against existing GitHub issues, and create issues in the appropriate system.

**Be conversational and collaborative** — explain your findings, ask clarifying questions, and confirm decisions with the user before creating anything.

## Authority Constraints (inherited from `/claude-gi-add`)

- You **MUST NOT** call `gh issue close`.
- You **MUST NOT** add the `verified` label to any issue.
- Final closure is reserved for the user via `/claude-gi-close`.

If during triage the user signals "this fix is confirmed," you DO NOT close the issue. You post a comment recording the confirmation and tell the user the close command.

---

## Phase 1: Session Loading

### Step 1: Locate the Session

The session argument is: **$ARGUMENTS**

1. If the argument is empty or omitted:
   - List directories in `Tools/qa_observer/session_data/`
   - Sort by name (they are `YYYYMMDD_HHMMSS` format)
   - Select the most recent directory that contains a `QA_Session_Log.md`
   - Report which session was auto-selected
2. Otherwise:
   - Strip any path prefix; use just the directory name
   - Construct path: `Tools/qa_observer/session_data/<argument>/QA_Session_Log.md`
   - Verify the file exists. If not, list available sessions and **STOP**.

### Step 1b: Check for Prior Triage

After selecting a session:

1. Check if `Tools/qa_observer/session_data/<session_id>/triage_summary.md` exists.
2. If it exists:
   - Read it and display the summary table to the user
   - Use **AskUserQuestion** with options:
     - **Re-triage** — process the session again from scratch (proceed normally)
     - **Pick another** — list all untriaged sessions and let the user choose, or STOP if none remain
   - If no untriaged sessions exist for "Pick another", report: "All sessions have been triaged. Nothing to do." and **STOP**.
3. If it does not exist, proceed normally.

### Step 2: Read and Parse the Session Log

1. Read the full `QA_Session_Log.md` file.
2. Parse into a list of **observations**. An observation is a logical unit consisting of:
   - One or more timestamped spoken commentary blocks
   - Zero or more screenshot references that appear between or after the commentary
3. **Group by topic:**
   - Consecutive commentary about the same subject forms one observation.
   - A topic change starts a new observation.
4. **Cross-session merging:** Scan the ENTIRE log for observations that return to the same issue later in the session. Users often mention something, move on, then come back to it. Merge all mentions of the same issue into a single observation, preserving:
   - All timestamps from each mention
   - All spoken commentary in chronological order
   - All associated screenshots
   - Note which parts came from separate mentions (e.g., "First mentioned at 07:44, revisited at 07:52")
5. Present the grouped observations to the user for confirmation:
   - Number each observation
   - Show a one-line summary
   - Flag any that were merged from multiple mentions
   - **Ask the user** if the grouping is correct — they may want to split or merge items

---

## Phase 1.5: Parallel Investigation Fan-Out

After Phase 1's grouping is confirmed, every **actionable** observation (anything you'd carry into Phase 2 — i.e. not a pre-classified Skip such as a retracted observation or a greeting) is investigated **in parallel** by a pool of general-purpose subagents before Phase 2 begins. Phase 2 then reads pre-generated findings instead of pausing to run code review and GitHub-duplicate searches inline.

### Step 1: Set up the team and output directory

1. Create the team: `TeamCreate({ name: "qa-triage-<session_id>", ... })`. Keep its members alive for the duration of the triage so each one can be reused via `SendMessage` when it finishes its first observation.
2. Create the report directory: `mkdir -p .agent_reports/triage-<session_id>/`.

### Step 2: Build the work queue

1. From the grouped observations, drop the pre-classified Skips.
2. The remaining observations form the **work queue**, numbered to match the Phase 1 grouping table. Track `pending` (not yet dispatched) and `in_flight` (assigned to a subagent, no report file yet).

### Step 3: Worker-pool dispatch (sliding window of 5)

Maintain at most **5 concurrent subagents**. The initial spawn launches `min(5, len(work_queue))` general-purpose subagents in a single Agent message block (parallel tool calls). Each is named `triage-obs-<idx>` and assigned the observation at that index.

After initial spawn, **enter Phase 2 immediately** — do not wait for any subagent to finish. Phase 2 processes observations in order 1..N. Before working on observation `idx`, check whether `.agent_reports/triage-<sid>/obs-<idx>.md` exists. If not, wait (no `Monitor` needed — each report finishes in ~1-3 minutes, and the user-facing back-and-forth in Phase 2 naturally absorbs this latency).

**As soon as any `obs-<idx>.md` appears AND `pending` is non-empty,** immediately `SendMessage` to the freed subagent to take the next pending observation. Subagent warm context (CLAUDE.md, gh CLI, repo familiarity) makes the second-and-later observations faster than cold spawns. Continue until `pending` is empty.

### Step 4: Subagent report schema

Each `obs-<idx>.md` MUST follow this template exactly so Phase 2 can read it deterministically. The subagent writes to `obs-<idx>.md.partial` first, then atomically renames to `obs-<idx>.md` so the main thread never sees a half-written file:

```markdown
---
observation_index: <N>
session_id: <YYYYMMDD_HHMMSS>
timestamps: ["HH:MM:SS", ...]
screenshots: ["bug_capture_xxx.png", ...]
suggested_category: <bug | feature | project | reject_fix | approve_fix | skip>
suggested_priority: <critical | high | medium | low | N/A>
duplicate_candidate: <github_issue_number_or_null>
duplicate_state: <open | closed | null>
duplicate_status_label: <pending | in-progress | awaiting-confirmation | null>
duplicate_confidence: <high | medium | low | none>
---

## Cleaned Commentary

[Speech-to-text cleaned up: punctuation, fillers removed, false-starts dropped — original meaning preserved.]

## Code Investigation Findings

[File:line references, what the code does today vs. what the user said, key call sites.]

## Log Excerpts

[Relevant lines from battle.log around the time window, OR "none relevant".]

## Duplicate Analysis

[The gh issue list / gh issue view findings. Why each candidate matches or doesn't. If `duplicate_candidate` is set, explain the match and why the recommended category (Reject Fix / Approve Fix / Add Context / New Issue) follows.]

## Recommendation

[One paragraph: why this category, why this priority, anything the main thread should flag to the user.]

## Draft Title

[≤72 chars, plain English, no [BUG]/[FEAT] prefix.]

## Draft Body

[Full markdown body matching .github/ISSUE_TEMPLATE/bug.yml or feature.yml structure. Use `[SCREENSHOT_PLACEHOLDER]` (or `[SCREENSHOTS_PLACEHOLDER]` for multiple) where images will go. The main thread substitutes the image link after creating the issue and copying assets.]
```

### Step 5: Subagent prompt template

Each subagent (initial spawn AND re-tasking via SendMessage) is given a prompt of this shape:

```
You are investigating observation #<N> from QA session <sid>. Write a structured report to `.agent_reports/triage-<sid>/obs-<N>.md` following the schema in `.claude/skills/claude-qa-triage/SKILL.md` Phase 1.5 Step 4.

**Observation block:**
<timestamps + raw commentary + screenshot filenames pasted in>

**Tasks:**
1. Read the session log (`Tools/qa_observer/session_data/<sid>/QA_Session_Log.md`) to confirm context.
2. Read each referenced screenshot to understand what the user is pointing to.
3. Investigate the relevant code starting from the user's words → file/function references. Use Grep/Read.
4. If `Tools/qa_observer/session_data/<sid>/word_timestamps.jsonl` exists, use it to narrow the log time window. Grep `Tools/qa_observer/session_data/<sid>/logs/battle.log` (and `battle_log.txt`, `crash_log.txt` if relevant) in that window for errors or state changes.
5. Run `gh issue list --state all --limit 50 --json number,title,state,labels --search "<2-4 high-signal keywords>"` to find duplicates. For plausible matches, run `gh issue view <#> --json number,title,state,labels,body,comments`.
6. Decide on `suggested_category` and `suggested_priority`. If you find an open issue with `status:awaiting-confirmation` that matches the observation, the category is almost always `reject_fix` (user observed the symptom again) or `approve_fix` (observation confirms the fix is working) — let the analysis decide.
7. Write the full report to `.agent_reports/triage-<sid>/obs-<N>.md.partial`, then rename to `.agent_reports/triage-<sid>/obs-<N>.md`.
8. Return one line: `obs-<N> ready (category: <X>, dup: #<Y or none>)`.

**Constraints:**
- READ-ONLY investigation. DO NOT create, modify, comment on, or label any GitHub issue.
- DO NOT copy screenshots or commit assets. The main thread handles the asset workflow.
- DO NOT edit any files outside `.agent_reports/triage-<sid>/`.
- If a critical error makes the investigation incomplete, write a partial report with an `## Errors` section explaining what went wrong and what the main thread needs to do manually.
```

When re-tasking an existing subagent via `SendMessage`, the prompt can be much shorter — the agent already knows the schema and the session — typically just: `Next observation: #<M>. Block: <…>. Write to obs-<M>.md.`

---

## Phase 2: Interactive Observation Review

Process each observation **ONE AT A TIME**, sequentially. Each observation's investigation is already done (or in flight) — your job is to walk the user through the findings, get their decisions, and execute the GitHub write actions. For each observation:

### Step A: Present the Observation

Display to the user:
- The timestamp range (or multiple timestamp ranges if merged)
- The full spoken commentary text (all mentions, in chronological order)
- Any associated screenshots — **read the image files** so the user can see them in the conversation
- A brief restatement: "It sounds like you're describing [X]. Is that right?"

### Step B: Read the Pre-Generated Findings

Before working on observation `idx`:
1. Check that `.agent_reports/triage-<session_id>/obs-<idx>.md` exists. If not, wait — the subagent is still working. (Phase 2 always processes observations in order; out-of-order reports are fine, just wait for the one you need.)
2. Read the report file. Extract from the frontmatter: `suggested_category`, `suggested_priority`, `duplicate_candidate`, `duplicate_status_label`, `duplicate_confidence`.
3. Summarise the findings to the user — Code Investigation Findings, Log Excerpts, Duplicate Analysis sections in a few sentences each. **Do not** redo the Read/Grep/gh queries yourself; the subagent has already done them and the results are in the report.
4. If the report's findings look incomplete or you need a follow-up (e.g. a deeper look at a specific function), **`SendMessage`** to `triage-obs-<idx>` with the follow-up question rather than spawning a fresh agent — the subagent has warm context.
5. If the report's `## Errors` section is populated, surface that to the user and decide together whether to push through manually or skip.

### Step C: Confirm Duplicate Treatment (against GitHub Issues)

The subagent's report has already searched `gh issue list` / `gh issue view` and populated `duplicate_candidate` in the frontmatter plus a `## Duplicate Analysis` section. Your job is to present that analysis to the user and confirm the treatment:

1. **If `duplicate_candidate` is null:** no duplicate found, proceed straight to Step D.
2. **If `duplicate_candidate` is set AND `duplicate_status_label == awaiting-confirmation`,** present the match and the subagent's reasoning, then use **AskUserQuestion** with these options:
   - **Approve Fix** — the bug is confirmed fixed during this QA session (proceed to Step E: Approve Bug Fix)
   - **Reject Fix** — the bug is NOT fixed, user observed it again (proceed to Step E: Reject Bug Fix)
   - **Add Context** — related observation but not directly about the fix status (post a comment with new info)
   - **New Issue** — distinct issue, proceed to Step D
3. **For all other matches** (open with another status, closed, etc.), present and use **AskUserQuestion** with:
   - **Duplicate** — skip this observation entirely (note in session summary)
   - **Add Context** — post a comment to the existing issue with the new information and screenshots, then move on
   - **New Issue** — this is a distinct issue, proceed to Step D

When posting a comment for "Add Context", use the same screenshot-commit pipeline as for new issues (see Step E asset workflow), but skip body editing — the screenshots go in the comment body itself.

### Step D: Categorize

The subagent's report proposes `suggested_category` and `suggested_priority` in its frontmatter. Present those (plus the rationale from `## Recommendation`) and confirm with the user via **AskUserQuestion**:

1. **Bug** — something is broken or behaving incorrectly
2. **Feature** — a new capability or enhancement request
3. **Prospective Project** — a large-scope item requiring architecture review and multi-phase planning
4. **Reject Bug Fix** — an existing issue with `status:awaiting-confirmation` was NOT actually fixed; the user observed the same problem during this QA session. Only valid when the observation matched an existing awaiting-confirmation issue (typically offered during Step C).
5. **Approve Bug Fix** — an existing issue with `status:awaiting-confirmation` IS confirmed fixed. Only valid when the observation matched an existing awaiting-confirmation issue (typically offered during Step C). **You will NOT close the issue** — you post a confirmation comment and tell the user to run `/claude-gi-close <#>` themselves.
6. **Skip** — not actionable, or user changed their mind

### Step E: Create / Update Issue

Based on the confirmed category:

---

#### For Bugs and Features

The two flows are nearly identical; only the label set and template fields differ.

1. **Pull the draft from the report.** The subagent has already written `## Draft Title` and `## Draft Body` sections in `.agent_reports/triage-<sid>/obs-<idx>.md`, matching the bug.yml / feature.yml template structure with a `[SCREENSHOT_PLACEHOLDER]` token where images will go. You typically just present that draft as-is. Only re-draft from scratch if the report's `## Errors` section indicates the subagent failed.
   - **Bug body sections** per [`.github/ISSUE_TEMPLATE/bug.yml`](../../../.github/ISSUE_TEMPLATE/bug.yml): Description, Steps to Reproduce, Expected vs Actual, Acceptance Criteria, Screenshot/Logs (placeholder), Priority.
   - **Feature body sections** per [`.github/ISSUE_TEMPLATE/feature.yml`](../../../.github/ISSUE_TEMPLATE/feature.yml): Description, Motivation, Acceptance Criteria, Priority.
   - Title: ≤72 chars, plain English, no `[BUG]`/`[FEAT]` prefix (labels carry that).
   - Speech-to-text artifacts (missing punctuation, fillers, repetition, false starts) should already be cleaned in the report.
2. **Present** the draft to the user for approval or edits. If they want changes, edit the draft in place before creating the issue.
3. **Determine priority.** The report proposes `suggested_priority` in its frontmatter. Confirm with user via AskUserQuestion.
4. **Create the issue** with type/priority/status labels:
   ```bash
   # Write the body (without image link yet) to a temp file
   gh issue create \
     --title "<derived title>" \
     --body-file "<tmp-body.md>" \
     --label "type:<bug|feature>" \
     --label "priority:<P>" \
     --label "status:pending"
   ```
   Capture the issue number `N` from stdout (URL ends `…/issues/N`). Delete the temp body file after creation.
5. **Derive a slug** from the title:
   - Lowercase
   - Replace any non-alphanumeric run with a single `-`
   - Trim leading/trailing `-`
   - Truncate to 30 characters at a word boundary
6. **Copy assets** (only if the observation had screenshots and/or session logs):
   - **Screenshots:** for each relevant image in `Tools/qa_observer/session_data/<sid>/images/`, copy to `tracking-assets/screenshots/<YYYY-MM>/issue-<N>-<slug>-<idx>.png` (1-based `idx`; `<YYYY-MM>` = current month).
   - **Logs:** copy any of `battle.log`, `battle_log.txt`, `crash_log.txt`, `combat_lab.log`, `profiling_history.json`, `word_timestamps.jsonl` from `Tools/qa_observer/session_data/<sid>/logs/` (and the session root for `word_timestamps.jsonl`) to `tracking-assets/logs/issue-<N>/`.
7. **Commit and push assets** (skip if step 6 produced no files):
   ```bash
   git add tracking-assets/screenshots/<YYYY-MM>/issue-<N>-* \
           tracking-assets/logs/issue-<N>/
   git commit -m "chore(qa): add assets for #<N>"
   git push origin main
   ```
8. **Edit the issue body** to insert the rendered image link(s) into the Screenshot/Logs section (Bug) or append a Screenshots section (Feature). Use the `?raw=1` query so it renders inline:
   ```markdown
   ![<short alt text>](https://github.com/ropesend/StarshipBattles/blob/main/tracking-assets/screenshots/<YYYY-MM>/issue-<N>-<slug>-1.png?raw=1)
   ```
   Apply via `gh issue edit <N> --body-file <updated-body.md>`.
9. **Post a logs comment** if any log files were copied:
   ```bash
   gh issue comment <N> --body-file <logs-comment.md>
   ```
   The comment body links each log file by its raw GitHub URL plus a one-line description of the time window.
10. **Report:** "Created #<N> ([title]) — <URL>".

---

#### For Prospective Projects (unchanged from the legacy skill)

Projects stay 100% on disk. **Do NOT create a GitHub issue.**

1. **Pull the draft from the report.** The subagent's `## Draft Body` for a `project`-category observation should already contain the Context / Code Investigation Findings / Scope Notes sections. If it instead drafted in the bug/feature shape (because the categorization wasn't obvious until you saw the screenshots), reshape it for the project template below.
   - Speech-to-text artifacts should already be cleaned in the report.
   - Replace any `[SCREENSHOT_PLACEHOLDER]` tokens with `./assets/<filename>.png` references (see Image Handling below).
   - The "why this is project-sized" reasoning belongs in **Scope Notes** — pull from the report's `## Recommendation` or write fresh if needed.
2. **Present** the draft to the user for approval or edits.
3. **Choose a descriptive filename** (e.g., `star_rendering_overhaul.md`) — confirm with user.
4. **Copy** associated screenshots to `Projects/Triage/assets/` (do NOT copy to `tracking-assets/`).
5. **Create** the triage file `Projects/Triage/<descriptive_name>.md`:

```markdown
# [Title]

## Context
[What was observed during QA session, cleaned commentary]

## Screenshots
[./assets/ image references with descriptions]

## Code Investigation Findings
[What the agent found during exploration — files, functions, current behavior]

## Scope Notes
[Why this warrants a full project rather than a bug fix or feature]
```

6. Report: "Created triage item: `Projects/Triage/<filename>.md` — use `/claude-triage-to-proj <filename>` to convert to a full project."

---

#### For Reject Bug Fix

Apply the rejection to the existing GitHub issue (whose number was identified in Step C):

1. **Ask the user** for their rejection explanation — clean up speech-to-text artifacts but preserve meaning.
2. **Run the asset workflow** (steps 5–7 of the Bugs/Features flow) for any screenshots from this QA session, using the existing issue's `<N>` and the issue's existing slug (re-derived from its current title).
3. **Post a rejection comment** with the asset image link(s):

   ```bash
   gh issue comment <N> --body-file <rejection-comment.md>
   ```

   Body template:
   ```markdown
   ### ❌ Fix Rejected — QA session `<sid>` (YYYY-MM-DD HH:MM)

   **Reason:** [User's explanation, cleaned up.]

   **New observations:**
   ![…](https://github.com/ropesend/StarshipBattles/blob/main/tracking-assets/screenshots/<YYYY-MM>/issue-<N>-<slug>-1.png?raw=1)
   ```
4. **Flip the status label atomically** (single `gh issue edit` invocation, both flags):
   ```bash
   gh issue edit <N> --remove-label "status:awaiting-confirmation" --add-label "status:in-progress"
   ```
5. Report: "#<N> fix rejected and reverted to `status:in-progress`."

---

#### For Approve Bug Fix

You DO NOT close the issue. You record confirmation and ask the user to close.

1. **Post a confirmation comment** on the existing issue:
   ```bash
   gh issue comment <N> --body "✅ Fix confirmed by user during QA session \`<sid>\` (YYYY-MM-DD). Ready for closure."
   ```
2. **Tell the user** in the conversation: "#<N> looks fixed. Run `/claude-gi-close <N>` to close it."
3. **Do NOT** add the `verified` label. **Do NOT** call `gh issue close`. Both are forbidden by Authority Constraints.
4. Report: "#<N> confirmation logged. Awaiting user `/claude-gi-close`."

---

#### For Skip

Note in the session summary; no GitHub action.

---

## Phase 3: Session Summary

After all observations have been processed, present a final summary table:

```markdown
## QA Triage Summary — Session <session_id>

| # | Observation | Category | Issue / File | Notes |
|---|-------------|----------|--------------|-------|
| 1 | Star display too small | Bug | #127 | New issue |
| 2 | Want fleet auto-routing | Feature | #128 | New issue |
| 3 | Combat UI needs overhaul | Project | combat_ui_overhaul.md | Triage created |
| 4 | Shield flicker | Reject Fix | #69 | Fix rejected, reverted to status:in-progress |
| 5 | Fleet display correct now | Approve Fix | #85 | Confirmed; user must run /claude-gi-close 85 |
| 6 | Minor comment | Skip | — | Not actionable |

**Created:** X issues (bugs+features), Z project triage items
**Bug fixes rejected:** R
**Bug fixes confirmed (awaiting user close):** A
**Duplicates / context added:** D
**Skipped:** M
```

### Write Triage Summary to Session

Write the summary table above (the full markdown block including the stats lines) to:
`Tools/qa_observer/session_data/<session_id>/triage_summary.md`

This file marks the session as triaged and is checked in Phase 1 to prevent redundant processing.

### Tear Down the Investigation Team

After the summary is written:

1. Call `TeamDelete` on the `qa-triage-<session_id>` team to free the subagent slots.
2. Optionally clean up `.agent_reports/triage-<session_id>/` if you want to keep the workspace tidy — but the reports are read-only artifacts and harmless to leave around. The `.agent_reports/` directory is already gitignored.

---

## Image Handling

### Source

All session images are in: `Tools/qa_observer/session_data/<session_id>/images/`

### For GitHub Issues (Bugs / Features)

**COPY** images to `tracking-assets/screenshots/<YYYY-MM>/issue-<N>-<slug>-<idx>.png`. Reference them via the `?raw=1` URL pattern so they render inline on github.com:

```markdown
![<alt>](https://github.com/ropesend/StarshipBattles/blob/main/tracking-assets/screenshots/<YYYY-MM>/issue-<N>-<slug>-1.png?raw=1)
```

Conventions per [`tracking-assets/README.md`](../../../tracking-assets/README.md):
- `<YYYY-MM>` = month the asset was first attached
- `<slug>` = lowercased title, alphanum-and-hyphens, ≤30 chars
- `<idx>` = 1-based index when multiple images for one issue
- Auto-commit and push the assets (single commit per issue): `chore(qa): add assets for #<N>`

### For Project Triage Files (`Projects/Triage/<name>.md`)

**COPY** images to `Projects/Triage/assets/` (NOT `tracking-assets/`). Reference as `./assets/<filename>.png`. The `/claude-triage-to-proj` skill expects this path during conversion.

---

## Constraints

- **INTERACTIVE PHASE 2:** Investigation runs in parallel (Phase 1.5), but Phase 2 walks through observations with the user **one at a time** — never batch-create issues silently.
- **CODE REVIEW:** Always investigate relevant code before categorizing. Subagents do this in parallel via the Phase 1.5 fan-out; don't skip the investigation step, and don't guess from the user's words alone.
- **USER APPROVAL:** Always present drafts and get confirmation before creating any issue or file. Subagents draft; the user approves; the main thread executes.
- **CLEAN TEXT:** Speech-to-text output has no punctuation, contains filler words, repetition, and false starts. Subagents should clean it into proper sentences for the report's `## Cleaned Commentary` and `## Draft Body`. Preserve the original meaning faithfully.
- **NO IMPLEMENTATION:** Do not start fixing bugs or implementing features. This is triage and data entry only.
- **AUTHORITY:** Never call `gh issue close`. Never add the `verified` label. Final closure belongs to the user.
- **ATOMIC LABEL FLIPS:** Use a single `gh issue edit --remove-label X --add-label Y` invocation for status transitions; never two separate commands.
- **IMAGE CONTEXT:** Every screenshot referenced in an issue must have a text description explaining what it shows and why it's relevant.
- **NO BULK COMMITS:** One asset commit per issue, so `git log` shows clean per-issue history.
- **CHECK STAGED FILES BEFORE COMMITTING ASSETS:** Before `git commit -m "chore(qa): add assets for #<N>"`, run `git diff --cached --name-only` and confirm only your intended asset files (`tracking-assets/screenshots/<YYYY-MM>/issue-<N>-*` and `tracking-assets/logs/issue-<N>/*`) are staged. If unrelated files are staged from the user's pre-existing index state, `git restore --staged <file>` them first — do NOT bundle unrelated changes into an asset commit. (This protects the user's in-progress work and keeps `git log` interpretable.)
- **PARALLEL/MAIN-THREAD SPLIT:** Subagents are **read-only** investigators (file reads, Grep, `gh issue list/view`). They never create, comment on, or label GitHub issues; never copy screenshots into `tracking-assets/`; never commit or push. All write actions (gh create/comment/edit, asset copy, git commit, git push) stay on the main thread to keep shared state (GitHub, git history, tracking-assets/) sequential and reviewable.

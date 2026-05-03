---
name: claude-qa-triage-gh
description: Process QA session logs into GitHub issues (bugs/features) and Projects/Triage/ files (prospective projects), through interactive triage.
disable-model-invocation: true
argument-hint: [session_directory_name] (e.g., 20260314_074413, or omit for latest)
---

# QA Session Triage — GitHub Issues edition

Process a QA Observer session log interactively, categorising each observation as a Bug, Feature, Prospective Project, or acting on existing bug fixes (reject/approve).

This is the GitHub Issues counterpart of `/claude-qa-triage`. The legacy skill writes to `Tracking/bugs/active/` etc.; this one routes bugs and features to **GitHub Issues** while still routing prospective projects to `Projects/Triage/<name>.md` on disk.

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

## Phase 2: Interactive Observation Review

Process each observation **ONE AT A TIME**, sequentially. For each observation:

### Step A: Present the Observation

Display to the user:
- The timestamp range (or multiple timestamp ranges if merged)
- The full spoken commentary text (all mentions, in chronological order)
- Any associated screenshots — **read the image files** so the user can see them in the conversation
- A brief restatement: "It sounds like you're describing [X]. Is that right?"

### Step B: Code & Log Investigation

Launch Explore agent(s) to understand the relevant code:
- Search for code related to the described behavior
- Identify the specific files, classes, and functions involved
- Determine whether the described behavior matches what the code actually does
- Present findings to the user: "I looked at [file:function] and here is what I found..."

**Log cross-referencing:** If `Tools/qa_observer/session_data/<session_id>/logs/` exists:
1. Read `word_timestamps.jsonl` from the session root to identify the precise time window for this observation. Each line is `{"time": <unix>, "ts": "HH:MM:SS", "word": "..."}`. Find the words corresponding to this observation's timestamps to narrow the window.
2. Search `logs/battle.log` (format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`) around that time window for errors, warnings, or relevant state changes.
3. Also check `logs/battle_log.txt` (combat events) and `logs/crash_log.txt` (crash tracebacks) if they exist.
4. Include pertinent log excerpts in your investigation findings.

### Step C: Duplicate Check (against GitHub Issues)

Query existing GitHub issues for overlap:

```bash
gh issue list --state all --limit 50 \
  --json number,title,state,labels \
  --search "<keywords from observation>"
```

Pick 2–4 high-signal keywords from the observation (subject + verb of the symptom). If `--search` returns candidates, fetch the body of each plausible match:

```bash
gh issue view <#> --json number,title,state,labels,body,comments
```

If a potential match is found:

1. Present the match: "This may overlap with #N: [title]"
2. **If the matching issue is open AND has `status:awaiting-confirmation`**, use **AskUserQuestion** with these options:
   - **Approve Fix** — the bug is confirmed fixed during this QA session (proceed to Step E: Approve Bug Fix)
   - **Reject Fix** — the bug is NOT fixed, user observed it again (proceed to Step E: Reject Bug Fix)
   - **Add Context** — related observation but not directly about the fix status (post a comment with new info)
   - **New Issue** — distinct issue, proceed to Step D
3. **For all other matches** (open, closed, or different status), use **AskUserQuestion** with:
   - **Duplicate** — skip this observation entirely (note in session summary)
   - **Add Context** — post a comment to the existing issue with the new information and screenshots, then move on
   - **New Issue** — this is a distinct issue, proceed to Step D

When posting a comment for "Add Context", use the same screenshot-commit pipeline as for new issues (see Step E asset workflow), but skip body editing — the screenshots go in the comment body itself.

### Step D: Categorize

Propose a category based on code investigation findings, and confirm with the user via **AskUserQuestion**:

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

1. **Draft** the title and body:
   - Clean up speech-to-text artifacts (missing punctuation, filler words, repetition, false starts)
   - Title: ≤72 chars, plain English, no `[BUG]`/`[FEAT]` prefix (labels carry that)
   - Body sections per [`.github/ISSUE_TEMPLATE/bug.yml`](../../../.github/ISSUE_TEMPLATE/bug.yml) / [`feature.yml`](../../../.github/ISSUE_TEMPLATE/feature.yml):
     - **Bug:** Description, Steps to Reproduce, Expected vs Actual, Acceptance Criteria, Screenshot/Logs (placeholder — added in step 5), Priority
     - **Feature:** Description, Motivation, Acceptance Criteria, Priority
   - Include relevant findings from code investigation in the Description.
2. **Present** the draft to the user for approval or edits.
3. **Determine priority** (`critical` / `high` / `medium` / `low`) — propose one based on severity, confirm with user.
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

1. **Draft** a triage document:
   - Clean up speech-to-text artifacts
   - Include screenshot references using `./assets/` paths (see Image Handling below)
   - Include code investigation findings
   - Explain why this is project-sized (scope, architectural implications)
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

- **INTERACTIVE:** Do NOT batch-process all observations silently. Walk through each one with the user, one at a time.
- **CODE REVIEW:** Always investigate relevant code before categorizing. Use Explore agents. Don't guess — look at the actual code.
- **USER APPROVAL:** Always present drafts and get confirmation before creating any issue or file.
- **CLEAN TEXT:** Speech-to-text output has no punctuation, contains filler words, repetition, and false starts. Clean it up into proper sentences when writing descriptions. Preserve the original meaning faithfully.
- **NO IMPLEMENTATION:** Do not start fixing bugs or implementing features. This is triage and data entry only.
- **AUTHORITY:** Never call `gh issue close`. Never add the `verified` label. Final closure belongs to the user.
- **ATOMIC LABEL FLIPS:** Use a single `gh issue edit --remove-label X --add-label Y` invocation for status transitions; never two separate commands.
- **IMAGE CONTEXT:** Every screenshot referenced in an issue must have a text description explaining what it shows and why it's relevant.
- **NO BULK COMMITS:** One asset commit per issue (steps 6–7), so `git log` shows clean per-issue history.

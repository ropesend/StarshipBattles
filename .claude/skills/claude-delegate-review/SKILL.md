---
name: claude-delegate-review
description: Delegate a code review, plan review, follow-up review, or analysis task to OpenCode. Writes a structured request file that the review daemon picks up and dispatches to OpenCode. Use when you want OpenCode to review something while you continue working.
argument-hint: [brief description of what to review]
---

# Delegate Review to OpenCode

Write a structured review request for OpenCode to process asynchronously. The
review daemon watches `AgentCoordination/opencodereview/pending_review_requests/` and
dispatches requests automatically. OpenCode produces a report in
`Reviews/results/` while you continue working.

## When to Use

- You just made changes and want an independent code review
- You want a second opinion on a design, architecture, or plan document
- You want a follow-up verification that issues from a prior review were fixed
- You want a test coverage or security audit of a specific area
- You need a focused analysis of anything — code, docs, configs, plans
- You're about to make changes elsewhere and want parallel review work

## Pre-Flight: Check Daemon

The review daemon (`Tools/agent_coordination/review_daemon.py`) watches
`AgentCoordination/opencodereview/pending_review_requests/` and dispatches requests to
OpenCode. Check if it's running:

```bash
python -c "
import os, sys
from pathlib import Path
pid_file = Path('AgentCoordination/opencodereview/local/review_daemon.pid')
if not pid_file.exists():
    sys.exit(1)
try:
    pid = int(pid_file.read_text().strip())
    os.kill(pid, 0)
except (OSError, ProcessLookupError, ValueError):
    sys.exit(1)
"
echo $?
```

If the daemon is NOT running, tell the user to start it in a separate terminal:
```
.\Tools\agent_coordination\Start-ReviewDaemon.ps1
```
Do not write the request file until the daemon is running.

## Pre-Flight: Scope Must Be Inside The Project

**Every path referenced in the review scope must live inside the project
root** — the directory the OpenCode worker is launched from. That is the
current working directory you observe when the daemon is running (the
`PROJECT_ROOT` value used by `Tools/agent_coordination/review_daemon.py`),
not a hard-coded absolute path. OpenCode does not have reliable access to
paths outside its working tree.

Do NOT include any of the following in scope:

- Absolute paths under the user's home directory (e.g. `~/.claude/...`,
  `C:\Users\<name>\...`, `/home/<name>/...`)
- System paths (`C:\Windows\...`, `/etc/...`, `/usr/...`)
- Paths in sibling repositories or scratch directories outside this repo

Prefer **repo-relative paths** in scope (e.g. `game/foo.py`,
`docs/01_ARCHITECTURE.md`). If you must use absolute paths, verify they
resolve under the project root before submitting. A quick check:

```bash
python -c "
from pathlib import Path
import sys
root = Path.cwd().resolve()
for p in sys.argv[1:]:
    rp = Path(p).resolve()
    inside = root == rp or root in rp.parents
    print(('OK ' if inside else 'OUTSIDE '), rp)
" "<path1>" "<path2>"
```

If the user wants OpenCode to review a document that lives outside the project
(e.g. a plan file under `~/.claude/plans/`), **copy the document into the repo
first** (a sensible target is `Projects/active_projects/<PROJ-XX>/` or a temp
path under `Reviews/results/<date>_<scope>/`), reference the in-repo copy in
scope, and tell the user you did so they can clean up afterwards.

A previously-failed request (`req_20260502_204250_1944dc`) timed out at 30
minutes after pointing OpenCode at a plan file under the user's home dir.
The worker hung attempting to read a path outside its working tree. Avoid
that footgun.

## Follow-Up Reviews

If the user wants to verify that issues from a prior review were fixed,
write a follow-up request. A follow-up is a normal request with a
`**Parent:**` field pointing at the prior request:

```markdown
**Parent:** req_20260502_063000
```

Required fields for a follow-up:

- `**Parent:** req_<id>` — points at the prior completed request
- `## Scope` — narrower than the parent (the files that changed in
  response to the findings, not the original full scope)
- `## Instructions` — explicitly list the finding IDs to verify, e.g.
  "Confirm CRIT-001 and MAJ-003 from the parent report are resolved.
   Note any regressions introduced by the fixes."

Follow-ups go in `pending_review_requests/` like any other request.
When you read a completed follow-up, you may chain another follow-up
against *it* (parent points at the follow-up's request_id, not the
original).

## Step 1: Gather Review Requirements

Ask the user (or infer from context) what to review. You need:

| Field | Description |
|-------|-------------|
| **Review type** | One of: `code`, `plan`, `architecture`, `tests`, `security`, `performance`, `consistency`, `general`, `custom` |
| **Title** | Short descriptive title (e.g., "Combat engine refactor review") |
| **Scope** | What files/directories/concepts to review (paths, patterns) |
| **Instructions** | What to look for, specific questions, evaluation criteria |
| **Context** | Why this review, what changed, related PRs/projects |

If the user didn't provide details, ask these questions:
1. What specifically should OpenCode review? (files, dirs, docs, concepts)
2. What kind of review? (code quality, test coverage, architecture, etc.)
3. Any specific concerns or things to look for?
4. How deep should the review be? (quick scan, deep analysis, exhaustive)

For follow-up reviews, also determine:
- The parent request ID (from the completed request)
- Which specific findings to verify

## Step 2: Write the Request File

**Use a unique payload path.** Multiple Claude agents can delegate
concurrently; a fixed filename like `review_payload.json` would race.
Generate a unique path under `AgentCoordination/opencodereview/local/request_payloads/`
using a timestamp and random suffix:

```bash
PAYLOAD_PATH="AgentCoordination/opencodereview/local/request_payloads/payload_$(date +%Y%m%d_%H%M%S)_$(openssl rand -hex 3).json"
mkdir -p "$(dirname "$PAYLOAD_PATH")"
```

On Windows PowerShell:
```powershell
$PayloadPath = "AgentCoordination/opencodereview/local/request_payloads/payload_$(Get-Date -Format yyyyMMdd_HHmmss)_$(-join ((48..57)+(97..102) | Get-Random -Count 6 | ForEach-Object {[char]$_})).json"
New-Item -ItemType Directory -Force -Path (Split-Path $PayloadPath) | Out-Null
```

Write the payload to that path:

```json
{
  "type": "{code|plan|architecture|tests|security|performance|consistency|general|custom}",
  "title": "{TITLE}",
  "scope": "{SCOPE — multiline OK, Markdown OK, backticks OK, Windows paths OK}",
  "instructions": "{INSTRUCTIONS — multiline OK, Markdown OK}",
  "context": "{CONTEXT (optional)}",
  "expected_deliverable": "{DELIVERABLE (optional)}",
  "parent": "req_<id> (optional — for follow-ups only)",
  "requester": "claude-code (default)"
}
```

Then call the helper:

```bash
python Tools/agent_coordination/create_review_request.py --payload-file "$PAYLOAD_PATH"
rm -f "$PAYLOAD_PATH"   # delete on success; helper does not auto-clean
```

The script prints the request ID to stdout. The request file is written to
`AgentCoordination/opencodereview/pending_review_requests/` atomically with a
collision-resistant ID (`req_<YYYYMMDD>_<HHMMSS>_<6hex>`). On failure, the
payload is preserved under `AgentCoordination/opencodereview/local/failed_payloads/` for
debugging — do not delete it manually in that case.

**For follow-ups**, add `"parent": "req_<parent_id>"` to the payload JSON.

### Scope Formatting

For file/directory-based reviews, list explicit paths:
```markdown
## Scope
- `game/simulation/combat/` — all files
- `game/engine/collision.py` — specific file
- `tests/unit/simulation/test_combat.py` — corresponding tests
```

For document/plan reviews, list the documents:
```markdown
## Scope
- `Projects/active_projects/PROJ-42/plan.md`
- `Projects/active_projects/PROJ-42/design.md`
```

For conceptual reviews, describe the area:
```markdown
## Scope
The error handling patterns across the simulation layer.
Focus on consistency, exception chain preservation, and logging.
```

### Instruction Examples

**Code review:**
```markdown
## Instructions
- Check for layer violations (simulation importing from UI)
- Verify error handling follows project conventions  
- Look for duplicated logic that could be consolidated
- Assess test coverage of changed files
- Check for 500-line ceiling violations
```

**Plan review:**
```markdown
## Instructions
- Is the design compatible with the hexagonal grid system?
- Does the plan respect the existing registry pattern?
- Are there any performance concerns with the proposed approach?
- Are there missing edge cases or failure modes?
```

**Architecture review:**
```markdown
## Instructions
- Evaluate against docs/01_ARCHITECTURE.md conventions
- Check for circular dependencies in proposed changes
- Assess impact on existing subsystems
- Identify any layering violations
```

## Step 3: Report to User

Tell the user:
- Request ID: `req_{TIMESTAMP}`
- Location: `AgentCoordination/opencodereview/pending_review_requests/req_{TIMESTAMP}.md`
- The daemon will dispatch it to OpenCode automatically
- Results will appear in `AgentCoordination/opencodereview/completed_review_requests/`
  with a link to the report in `Reviews/results/`

## Step 4: Check Results Later

When you need to see if the review is done, check:
```bash
ls AgentCoordination/opencodereview/completed_review_requests/
```

Read the completed request file — it will contain a `## Results` section
with a link to the report and a findings summary. If the request isn't
completed yet, the file will still be in `pending_review_requests/` or
`in_progress_review_requests/`.

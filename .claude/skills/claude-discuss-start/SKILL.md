---
name: claude-discuss-start
description: Open an inter-agent discussion with Codex via a shared folder. Claude writes message 001 (with cold-start context plus any user-supplied focus), then alternates with Codex up to 10 messages (extendable once to 20). Use when you want Claude and Codex to refine a plan, design, or code path directly without the user copy-pasting between sessions.
argument-hint: <folder> [context...]
---

# Inter-Agent Discussion — Claude Starts (v2 spec)

You are opening a multi-turn discussion with Codex. The user invokes
`/codex-discuss-respond <same folder>` on the Codex side. You exchange
messages through files in the shared folder until you reach consensus, agree
the user needs to weigh in, or hit the active message cap (10 by default,
extendable once to 20 in-band).

This is a peer-to-peer dialogue, not a delegation. Codex is your equal here.
Push back, propose alternatives, agree where you actually agree.

## Protocol — interagent-discussion/v1 (v2 spec)

| Field | Value |
|-------|-------|
| Folder | `$args[0]`; absolute or repo-relative; quote if it contains spaces |
| Inline context | tokens after the folder, joined and forwarded verbatim |
| `topic.md` | optional `<folder>/topic.md`, read at start, forwarded verbatim |
| Filename pattern | `NNN_<from>_to_<to>.md` (zero-padded) |
| Default cap | 10 messages (one in-band extension to 20 allowed) |
| Message format | YAML frontmatter (line 1 = `---`) + markdown body |
| Termination | Two consecutive matching terminal statuses, OR cap reached, OR pre-existing `outcome.md` |
| Atomicity | `.tmp_<guid>` then `Move-Item` to final name |
| Shared plans | `<folder>/plans/<name>.md` — current-turn agent only may edit |

## Step 1 — Parse arguments

First token = folder. All remaining tokens, joined with spaces = inline
context. If the folder path contains spaces, the user must wrap it in double
quotes; recommend no spaces in discussion-folder names.

```powershell
$Folder = $args[0]
if (-not [System.IO.Path]::IsPathRooted($Folder)) {
  $Folder = Join-Path 'c:\Dev\StarshipBattles' $Folder
}
$InlineContext = if ($args.Length -gt 1) { ($args[1..($args.Length - 1)] -join ' ') } else { '' }
New-Item -ItemType Directory -Force -Path $Folder | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $Folder 'plans') | Out-Null
```

Recommended (not enforced) location: `AgentCoordination/Scratchpad/discussions/<topic>/`
per the CLAUDE.md scratchpad rule.

## Step 2 — Pre-flight: refuse to clobber an existing discussion

If the folder already contains any `???_*_to_*.md` file or `outcome.md`,
**abort** and tell the user to pick a different folder. (`plans/`, `topic.md`,
heartbeat files are inputs and may pre-exist.)

```powershell
$existing = Get-ChildItem -Path $Folder -File -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -match '^\d{3}_(claude|codex)_to_(claude|codex)\.md$' -or $_.Name -eq 'outcome.md' }
if ($existing) {
  Write-Output "ABORT: discussion files already exist in $Folder"
  $existing | ForEach-Object { Write-Output "  - $($_.Name)" }
  exit 1
}
```

## Step 3 — Read optional `topic.md`

If the user pre-created `<folder>/topic.md`, read its contents. This is an
alternative or supplement to inline context (useful when the focus brief is
long enough to make command-line quoting painful).

```powershell
$TopicMd = ''
$topicPath = Join-Path $Folder 'topic.md'
if (Test-Path $topicPath) { $TopicMd = Get-Content $topicPath -Raw }
```

## Step 4 — Compose and write message 001

Body must include, in order:

1. **`## User-supplied context`** — only if inline context or `topic.md` is
   non-empty. Each goes into a separate fenced block, **verbatim**. You
   **MUST NOT** summarize, paraphrase, or modify these blocks. You may add
   your own synthesis below them in the same section if useful.

2. **Cold-start context** — Codex has no shared memory with you. Convey:
   - The user's underlying request or problem.
   - The current state (what's been proposed, tried, decided).
   - Relevant files/constraints/conventions Codex needs to know.
   - What you specifically want from Codex (critique, alternative, code, plan
     refinement, etc.).

### Message file format

Frontmatter is the **first thing in the file** (line 1 = `---`). Heading goes
inside the body — never above frontmatter. Use the actual current UTC time
in `created_at_utc`, not the placeholder.

```markdown
---
protocol: interagent-discussion/v1
message_index: 1
from: claude
to: codex
status: continue
reply_to: null
created_at_utc: <ISO 8601 UTC, e.g. 2026-05-03T20:00:00Z>
---

# Claude → Codex, message 001

## User-supplied context

Inline context (verbatim):
~~~
<exact inline context, do not modify>
~~~

topic.md (verbatim):
~~~
<exact topic.md content, do not modify>
~~~

[optional synthesis below the verbatim blocks]

## [your cold-start brief — current state, what's been tried, what you want from Codex]

...
```

### Frontmatter schema (v2)

**Required:** `protocol`, `message_index`, `from`, `to`, `status`, `reply_to`, `created_at_utc`.

**Optional:**
- `agent_turn: <int>` — informational only; receivers do not validate.
- `message_cap: <int>` — omit unless an extension was accepted (then `20`).
- `extension_requested_cap: 20` — set to propose extension.
- `extension_accepted: true` — set when accepting a proposed extension.

### Status values

- `continue` — keep discussing.
- `consensus` — agents have converged. **Does not end the discussion alone**;
  receiver must reply `consensus` for two-confirmation termination.
- `needs-user` — only the user can answer. Same two-confirmation rule.

### Atomic write helpers

```powershell
function Write-MessageAtomic {
  param([string]$Folder, [string]$FinalName, [string]$Content)
  $tmp = Join-Path $Folder ('.tmp_' + [guid]::NewGuid().ToString('N') + '.md')
  Set-Content -Path $tmp -Value $Content -Encoding utf8
  Move-Item -Path $tmp -Destination (Join-Path $Folder $FinalName)
}

function Write-PlanAtomic {
  param([string]$Folder, [string]$PlanName, [string]$Content)
  $plansDir = Join-Path $Folder 'plans'
  $tmp = Join-Path $plansDir ('.tmp_' + [guid]::NewGuid().ToString('N') + '.md')
  Set-Content -Path $tmp -Value $Content -Encoding utf8
  Move-Item -Path $tmp -Destination (Join-Path $plansDir $PlanName) -Force
}
```

Final filename for message 1: `001_claude_to_codex.md`.

## Step 5 — Discussion loop

Repeat until terminal. The active cap starts at 10; if an extension is
accepted, it becomes 20 for the rest of the discussion.

1. **Wait for Codex's next message.** Codex writes even indexes
   (`002`, `004`, ..., `010`; post-extension `012`, ..., `020`). Filename:
   `<NNN>_codex_to_claude.md`. Use the polling helper below.

2. **Read and validate.** `protocol == interagent-discussion/v1`,
   `from == codex`, `to == claude`, `message_index` = expected next even
   number. If anything is off, surface to the user.

3. **Apply termination rules** (in order):
   - `outcome.md` already exists → done; read it, summarize, exit.
   - Incoming `status: consensus` AND your previous outgoing `status` was
     `consensus` → write `outcome.md`, summarize, exit.
   - Same for `needs-user`.
   - Incoming `message_index == active_cap` → cap reached. Write
     `outcome.md`, summarize, exit. (No reply after the final message.)

4. **Re-read any plans listed in `## Plans touched`.** If the incoming
   message has that section, re-read each listed `<folder>/plans/<name>.md`
   before composing your reply.

5. **Handle extension request, if any.** If incoming has
   `extension_requested_cap: 20` and the discussion has not yet been extended:
   - **Accept** by setting `message_cap: 20` and `extension_accepted: true`
     in your reply's frontmatter, plus a one-line body acknowledgement.
     After acceptance, **every subsequent message must include
     `message_cap: 20`** so the latest message is self-describing.
   - **Decline** by omitting both fields and explaining in body.
   - Acceptance may happen at message 10; if accepted at 10, that message
     may use `status: continue` because the cap is now 20.
   - At most one extension per discussion (10 → 20, no further).

6. **Handle handover proposal, if any.** If incoming body has
   `## Handover proposal`, either accept or decline in your reply's body
   markdown (no frontmatter ceremony). If accepted, the eventual
   `outcome.md` records `user_facing_agent: codex` plus rationale.
   Per the user's rule: handover only via explicit proposal, never silent.

7. **Compose your reply.** Status:
   - `continue` — more to discuss.
   - `consensus` — you actually agree with Codex's position.
   - `needs-user` — a question only the user can answer.
   - **At the active cap**: must use `consensus` or `needs-user`, not
     `continue`. After writing the final message, write `outcome.md` directly
     without waiting for a reply (none is coming).

8. **Edit shared plans this turn (if appropriate).** Plan files live at
   `<folder>/plans/<name>.md`. Only the agent currently composing a reply
   may edit. Plan frontmatter:
   ```yaml
   ---
   protocol: interagent-discussion/v1
   last_edited_by: claude
   last_edited_at_utc: <UTC ISO 8601>
   revision: <int, increment on each edit>
   ---
   ```
   Optional `## Revision log` body section appending one line per edit.
   If you edit, include a `## Plans touched` section in your message listing
   each path + one-line reason. (Required only when you actually edited.)

9. **Atomic-write the message** via `Write-MessageAtomic` to
   `<NNN>_claude_to_codex.md` (odd index).

10. Loop back to step 1.

### Polling helper (5-min wait, retry once on TIMEOUT)

```powershell
$target = Join-Path $Folder ('{0:D3}_codex_to_claude.md' -f $expectedIndex)
$start = Get-Date
$deadline = $start.AddMinutes(5)
while (-not (Test-Path $target) -and (Get-Date) -lt $deadline) {
  $elapsed = [int]((Get-Date) - $start).TotalSeconds
  Write-Output "waiting... ${elapsed}s elapsed, target=$target"
  Set-Content -Path (Join-Path $Folder 'heartbeat_claude.txt') -Value (Get-Date -Format o) -Encoding utf8
  Start-Sleep -Seconds 60
}
if (-not (Test-Path $target)) { Write-Output 'TIMEOUT'; exit 1 }
Write-Output 'READY'
```

Run via PowerShell tool with `timeout: 320000` (~5.3 min). On `TIMEOUT`,
retry once (~10 min total wall clock). If still no file, surface to user:

> Codex hasn't responded after ~10 minutes. Invoke
> `/codex-discuss-respond <folder>` (or `start`) on the Codex side, or tell
> me to keep waiting.

**Do not write `outcome.md` on timeout.** Timeout means the discussion is
paused, not concluded.

## Step 6 — Write outcome.md (exactly once, race-safe)

When a terminal condition fires:

```powershell
$outcomePath = Join-Path $Folder 'outcome.md'
if (-not (Test-Path $outcomePath)) {
  Write-MessageAtomic -Folder $Folder -FinalName 'outcome.md' -Content $outcomeBody
} else {
  # Codex got there first — read theirs, do not overwrite.
  Get-Content $outcomePath
}
```

Format:

```markdown
---
protocol: interagent-discussion/v1
ended_at_message: <int>
ended_by: claude
status: consensus               # consensus | needs-user
user_facing_agent: claude       # claude | codex
---

## Summary

[2–4 paragraphs: what was discussed, what was agreed, unresolved questions,
recommended next action.]

## Handover (only if applicable)

[1-line rationale for why `user_facing_agent` is set to the accepting agent,
if a handover was proposed and accepted during the discussion.]
```

- `status: consensus` — both sides confirmed agreement.
- `status: needs-user` — both sides confirmed user input is needed, OR
  active cap hit without consensus.
- `user_facing_agent` — default = starter (`claude` here); changes only via
  accepted handover proposal.

## Step 7 — Report to the user

Tell the user:

- Folder path.
- Number of messages exchanged (and whether an extension was used).
- Terminal status (`consensus` / `needs-user`) and `user_facing_agent`.
- 1–2 sentence summary of the outcome.
- If `needs-user`: what specifically the user must decide.
- File listing so they can review the transcript and any plans.

Per the agreed v2 default: **the starter is the user-facing agent** unless
a handover was proposed and accepted during the discussion. Since you
(`claude-discuss-start`) are the starter, you are the user-facing agent by
default — you handle this report.

## Notes & gotchas

- **Filename parity (starter).** Claude writes odd indexes; Codex writes even.
  Reversed when Claude is responding (`claude-discuss-respond`).
- **Frontmatter on line 1.** No prefix above the `---`. Strict YAML parsers
  require it.
- **Heartbeat files** (`heartbeat_claude.txt`) are best-effort liveness hints,
  not load-bearing.
- **Temp files** matching `.tmp_*` are ignored by readers.
- **Folder paths with spaces** must be double-quoted by the user. Recommend
  no spaces.
- **Plans are working artifacts**; `outcome.md` is authoritative.
- **Plan write rule:** only the current-turn agent may edit `plans/`. The
  waiting agent treats `plans/` as read-only.
- **Scratchpad is gitignored.** Don't rely on git for plan history; use the
  `revision: <int>` field and an optional `## Revision log`.
- **Verbatim user context** must not be paraphrased. The starter's job is to
  forward, not summarize.

---
name: claude-discuss-respond
description: Join an inter-agent discussion that Codex opened. Claude waits for Codex's message 001, then alternates with Codex up to 10 messages (extendable once to 20). Use when the user has invoked /codex-discuss-start on the Codex side and wants Claude to participate.
argument-hint: <folder>
---

# Inter-Agent Discussion — Claude Responds (v2 spec)

You are joining a multi-turn discussion that Codex opened. The user has
invoked `/codex-discuss-start <same folder> [context...]` on the Codex side;
Codex's opening message will appear (or has appeared) at
`<folder>/001_codex_to_claude.md`. You read it, reply, and alternate until
you reach consensus, agree the user needs to weigh in, or hit the active
message cap (10 by default, extendable once to 20 in-band).

This is a peer-to-peer dialogue, not a delegation. Codex is your equal here.
Push back, propose alternatives, agree where you actually agree.

## Protocol — interagent-discussion/v1 (v2 spec)

| Field | Value |
|-------|-------|
| Folder | `$args[0]`; absolute or repo-relative; quote if it contains spaces |
| Filename pattern | `NNN_<from>_to_<to>.md` (zero-padded) |
| Default cap | 10 messages (one in-band extension to 20 allowed) |
| Message format | YAML frontmatter (line 1 = `---`) + markdown body |
| Termination | Two consecutive matching terminal statuses, OR cap reached, OR pre-existing `outcome.md` |
| Atomicity | `.tmp_<guid>` then `Move-Item` to final name |
| Shared plans | `<folder>/plans/<name>.md` — current-turn agent only may edit |

The responder does not take inline context — context arrives forwarded in
Codex's message 001.

## Step 1 — Resolve the folder

```powershell
$Folder = $args[0]
if (-not [System.IO.Path]::IsPathRooted($Folder)) {
  $Folder = Join-Path 'c:\Dev\StarshipBattles' $Folder
}
if (-not (Test-Path $Folder)) {
  Write-Output "ABORT: folder does not exist: $Folder"
  exit 1
}
New-Item -ItemType Directory -Force -Path (Join-Path $Folder 'plans') | Out-Null
```

The responder does not create the discussion folder — the starter does. If
the folder doesn't exist, the user likely hasn't invoked the start skill on
the Codex side yet, or supplied the wrong path.

## Step 2 — Pre-flight: refuse to join a finished discussion

If `outcome.md` already exists, don't replay it. Read it, summarize to the
user, exit.

```powershell
$outcome = Join-Path $Folder 'outcome.md'
if (Test-Path $outcome) {
  Write-Output "EXISTING_OUTCOME"
  Get-Content $outcome
  exit 0
}
```

If the folder contains `claude_to_codex` files but no matching
`codex_to_claude` reply, that means a prior Claude session was the starter
and was waiting for Codex. `claude-discuss-respond` is for joining a
discussion **Codex started**. If the parity is wrong, abort and tell the user.

## Step 3 — Wait for Codex's opening message

Filename: `001_codex_to_claude.md`.

```powershell
$target = Join-Path $Folder '001_codex_to_claude.md'
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

Run via PowerShell tool with `timeout: 320000`. On `TIMEOUT`, retry once
(~10 min total). If still nothing, surface to the user:

> Codex hasn't started after ~10 minutes. Make sure you invoked
> `/codex-discuss-start <folder>` on the Codex side, or tell me to keep
> waiting.

## Step 4 — Read message 001 and validate

Parse the frontmatter. Required:

- `protocol: interagent-discussion/v1`
- `message_index: 1`
- `from: codex`
- `to: claude`

If any field is wrong, surface to the user — don't recover silently.

Codex's message 001 will include a `## User-supplied context` section if the
user provided inline context or `topic.md` to Codex. **Treat the verbatim
fenced blocks in that section as authoritative user intent.** Do not
paraphrase or override them when forming your reply.

## Step 5 — Discussion loop

You are alternating with Codex. **Claude writes even indexes** (`002`, `004`,
..., `010`; post-extension `012`, ..., `020`). Codex writes odd indexes
(`001`, `003`, ..., `009`; post-extension `011`, ..., `019`).

The active cap starts at 10; if an extension is accepted, it becomes 20.

Repeat until terminal:

1. **Apply termination rules** (against the just-read incoming message, in
   order):
   - `outcome.md` already exists → done; read it, summarize, exit.
   - Incoming `status: consensus` AND your previous outgoing `status` was
     `consensus` → write `outcome.md`, summarize, exit. (For the very first
     reply, you have no previous outgoing message, so this rule cannot fire
     yet.)
   - Same for `needs-user`.
   - Incoming `message_index == active_cap` → cap reached. Write
     `outcome.md`, summarize, exit. (No reply after the final message.)

2. **Re-read any plans listed in `## Plans touched`.** If the incoming
   message has that section, re-read each listed `<folder>/plans/<name>.md`
   before composing your reply.

3. **Handle extension request, if any.** If incoming has
   `extension_requested_cap: 20` and the discussion has not yet been extended:
   - **Accept** by setting `message_cap: 20` and `extension_accepted: true`
     in your reply's frontmatter, plus a one-line body acknowledgement.
     After acceptance, **every subsequent message must include
     `message_cap: 20`** so the latest message is self-describing.
   - **Decline** by omitting both fields and explaining in body.
   - Acceptance may happen at message 10; that message may use
     `status: continue` because the cap is now 20.
   - At most one extension per discussion (10 → 20, no further).

4. **Handle handover proposal, if any.** If incoming body has
   `## Handover proposal`, either accept or decline in your reply's body
   markdown (no frontmatter ceremony). If accepted, the eventual
   `outcome.md` records `user_facing_agent: claude` plus rationale.
   Per the user's rule: handover only via explicit proposal, never silent.

5. **Compose your reply.** Status:
   - `continue` — more to discuss.
   - `consensus` — you actually agree with Codex's position.
   - `needs-user` — a question only the user can answer.
   - **At the active cap**: must use `consensus` or `needs-user`, not
     `continue`. After writing the final message, write `outcome.md` directly
     without waiting for a reply.

6. **Edit shared plans this turn (if appropriate).** Plan files live at
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
   If you edit, include a `## Plans touched` section in your message listing
   each path + one-line reason.

7. **Atomic-write the message** via `Write-MessageAtomic` to
   `<NNN>_claude_to_codex.md` (even index).

8. **Wait for Codex's next message** at `<NNN+1>_codex_to_claude.md` using
   the polling helper. Validate. Loop back to step 1.

### Message file format

Frontmatter is the **first thing in the file** (line 1 = `---`). Heading
goes inside the body — never above frontmatter. Use the actual current UTC
time in `created_at_utc`.

```markdown
---
protocol: interagent-discussion/v1
message_index: 2
from: claude
to: codex
status: continue
reply_to: 1
created_at_utc: <ISO 8601 UTC>
---

# Claude → Codex, message 002

[reply / counterpoint / agreement]

## Plans touched

(Only when you created or edited plan files this turn.)
```

### Frontmatter schema (v2)

**Required:** `protocol`, `message_index`, `from`, `to`, `status`, `reply_to`, `created_at_utc`.

**Optional:**
- `agent_turn: <int>` — informational only; receivers do not validate.
- `message_cap: <int>` — omit unless an extension was accepted (then `20`).
- `extension_requested_cap: 20` — set to propose an extension.
- `extension_accepted: true` — set when accepting a proposed extension.

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

Run with `timeout: 320000`. Retry once on TIMEOUT. **No `outcome.md` on
timeout** — paused, not concluded.

## Step 6 — Write outcome.md (exactly once, race-safe)

```powershell
$outcomePath = Join-Path $Folder 'outcome.md'
if (-not (Test-Path $outcomePath)) {
  Write-MessageAtomic -Folder $Folder -FinalName 'outcome.md' -Content $outcomeBody
} else {
  Get-Content $outcomePath
}
```

```markdown
---
protocol: interagent-discussion/v1
ended_at_message: <int>
ended_by: claude
status: consensus               # consensus | needs-user
user_facing_agent: codex        # default = starter (codex here); changes via accepted handover
---

## Summary

[2–4 paragraphs: what was discussed, what was agreed, unresolved questions,
recommended next action.]

## Handover (only if applicable)

[1-line rationale for why `user_facing_agent` is the accepting agent.]
```

`user_facing_agent` defaults to **the starter** (so `codex` when Claude is
responding). Changes only via accepted handover proposal during the
discussion.

## Step 7 — Report to the user (only if you are the user-facing agent)

Per the agreed v2 default: **the starter is the user-facing agent** unless
a handover was proposed and accepted. As `claude-discuss-respond`, the
starter is Codex. **You are NOT the default user-facing agent**.

- If `outcome.md.user_facing_agent == codex`: do a minimal acknowledgement
  to the user — one line that the discussion is closed and the folder path —
  then stop. Codex will deliver the substantive summary on its side.
- If a handover was accepted to `claude` during the discussion (i.e.
  `outcome.md.user_facing_agent == claude`): you are now the user-facing
  agent. Deliver the full report:
  - Folder path.
  - Number of messages exchanged (and whether an extension was used).
  - Terminal status and 1–2 sentence summary.
  - If `needs-user`: what specifically the user must decide.
  - File listing.

## Notes & gotchas

- **Filename parity (responder).** Codex writes odd indexes; Claude writes
  even. Reversed when Claude is the starter (`claude-discuss-start`).
- **Frontmatter on line 1.** No prefix above the `---`.
- **Heartbeat files** are best-effort liveness hints, not load-bearing.
- **Temp files** matching `.tmp_*` are ignored by readers.
- **Folder paths with spaces** must be double-quoted by the user. Recommend
  no spaces.
- **Plans are working artifacts**; `outcome.md` is authoritative.
- **Plan write rule:** only the current-turn agent may edit `plans/`.
- **Scratchpad is gitignored.** Use `revision: <int>` for plan history.
- **Don't paraphrase user-supplied context** that arrives in Codex's message
  001. The starter forwards it verbatim and you should treat it the same
  way when you reason about your reply.
- **Default user-facing agent is the starter** (Codex when you are
  responding). You only deliver the substantive user report if a handover
  to Claude was proposed and accepted.

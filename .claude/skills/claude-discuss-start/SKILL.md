---
name: claude-discuss-start
description: Open an inter-agent discussion with Codex. The user supplies a parent folder; this skill creates a timestamped child sub-folder (optionally `--slug`-suffixed) for the discussion, writes message 001 with optional user-supplied focus context, and alternates with Codex up to 10 messages per arc (extendable once to 20). Use when you want Claude and Codex to refine a plan, design, or code path directly without the user copy-pasting between sessions.
argument-hint: <parent> [--slug <kebab-case>] [context...]
---

# Inter-Agent Discussion — Claude Starts (v2.3)

You are opening a multi-turn discussion with Codex. The user supplies a
**parent** folder; you create a timestamped child sub-folder for this
discussion. The user invokes the Codex-side `codex-discuss-respond` skill
(which can take either the parent or the exact child leaf — it discovers via
parent scan).

This is a peer-to-peer dialogue, not a delegation. Codex is your equal here.
Push back, propose alternatives, agree where you actually agree.

## Protocol — interagent-discussion/v1 (v2.3 spec)

| Field | Value |
|-------|-------|
| Parent | `$args[0]`; absolute or repo-relative; quote if it contains spaces |
| Discussion leaf | child of parent: `YYYYMMDDTHHMMSSZ[_<slug>]/` (created by this skill) |
| Slug flag | optional `--slug <kebab-case>` (separate flag arg, NOT positional context) |
| Inline context | tokens after the optional `--slug <slug>` pair, joined and forwarded verbatim |
| `topic.md` | optional `<leaf>/topic.md`, read at start, forwarded verbatim |
| Filename pattern | `arc<NN>_<MMM>_<from>_to_<to>.md` (zero-padded; arc resets `message_index`) |
| Default per-arc cap | 10 messages (one in-band extension to 20 allowed per arc) |
| Message format | YAML frontmatter (line 1 = `---`) + markdown body |
| Termination | Two consecutive matching terminal statuses, OR cap reached, OR pre-existing `outcome.md` (per arc) |
| Atomicity | `.tmp_<guid>.md` then `Move-Item` to final name |
| Shared plans | `<leaf>/plans/<name>_r<NNN>.md` — versioned siblings, never overwrite |

## Step 1 — Parse arguments

```powershell
$Parent = $args[0]
if (-not [System.IO.Path]::IsPathRooted($Parent)) {
  $Parent = Join-Path 'c:\Dev\StarshipBattles' $Parent
}

# Look for an optional --slug <slug> flag immediately after the parent
$Slug = ''
$ContextStartIdx = 1
if ($args.Length -ge 3 -and $args[1] -eq '--slug') {
  $Slug = $args[2]
  $ContextStartIdx = 3
  if ($Slug -match '\s' -or $Slug -notmatch '^[a-z0-9][a-z0-9-]*$') {
    Write-Output "ABORT: --slug must be lowercase kebab-case (a-z, 0-9, '-'), got '$Slug'"
    exit 1
  }
}
$InlineContext = if ($args.Length -gt $ContextStartIdx) {
  ($args[$ContextStartIdx..($args.Length - 1)] -join ' ')
} else { '' }
```

**Slug parsing is flag-based**, not positional. Inline context never gets confused with a slug.

## Step 2 — Whitespace warning on the parent leaf

```powershell
$parentLeaf = Split-Path -Path $Parent -Leaf
if ($parentLeaf -match '\s') {
  $suggestion = ($parentLeaf -replace '\s+', '-')
  Write-Warning "Parent folder leaf '$parentLeaf' contains whitespace. Recommended: rename to '$suggestion'. The generated child folder will use no spaces regardless."
}
```

Warning only — the user may genuinely want a parent name with spaces. The
generated child uses timestamps and never has spaces.

## Step 3 — Pre-flight: refuse to clobber a leaf-shaped path

The parent must not itself look like a discussion leaf. If it has discussion
files at the top level, the user passed a leaf when they meant a parent:

```powershell
if (Test-Path -LiteralPath $Parent) {
  $leafFiles = Get-ChildItem -LiteralPath $Parent -File -ErrorAction SilentlyContinue |
    Where-Object {
      $_.Name -match '^arc\d{2}_\d{3}_(claude|codex)_to_(claude|codex)\.md$' -or
      $_.Name -eq 'outcome.md' -or
      $_.Name -match '^outcome_arc\d{2}\.md$'
    }
  if ($leafFiles) {
    Write-Output "ABORT: '$Parent' looks like an existing discussion leaf (contains discussion files), not a parent."
    Write-Output "Pick a parent folder that contains discussion sub-folders, or a fresh path."
    $leafFiles | Select-Object -First 5 | ForEach-Object { Write-Output "  - $($_.Name)" }
    exit 1
  }
}
```

**Pre-flight before any mutation.** Don't create the child folder until the parent has been accepted.

## Step 4 — Generate the child leaf name and create folder structure

```powershell
$timestamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
$ChildLeaf = if ($Slug) { "${timestamp}_${Slug}" } else { $timestamp }
$Folder = Join-Path $Parent $ChildLeaf

# Now safe to create — parent passed pre-flight
New-Item -ItemType Directory -Force -Path $Parent | Out-Null
New-Item -ItemType Directory -Force -Path $Folder | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $Folder 'plans') | Out-Null

Write-Output "Discussion leaf: $Folder"
```

The leaf path is what you'll report to the user later. Codex's responder
side can find it via parent scan, so the user usually doesn't need to copy
it manually.

Recommended (not enforced) parent location: `AgentCoordination/Scratchpad/discussions/`
per the CLAUDE.md scratchpad rule.

## Step 5 — Read optional `<leaf>/topic.md`

```powershell
$TopicMd = ''
$topicPath = Join-Path $Folder 'topic.md'
if (Test-Path -LiteralPath $topicPath) { $TopicMd = Get-Content -LiteralPath $topicPath -Raw }
```

The user usually won't pre-create `topic.md` because the leaf is generated;
but the option is preserved for explicit-leaf invocations or seeded folders.

## Step 6 — Compose and write `arc01_001_claude_to_codex.md`

Body must include, in order:

1. **`## User-supplied context`** — only if inline context or `topic.md` is
   non-empty. Each in a separate fenced block, **verbatim**. **MUST NOT**
   summarize, paraphrase, or modify these blocks. Synthesis below them is OK.

   **Fence-collision rule:** if verbatim content contains `~~~`, use a longer
   fence (`~~~~` etc.) so the inner text doesn't terminate the outer block.

2. **Cold-start context** — Codex has no shared memory with you. Convey:
   - The user's underlying request or problem.
   - The current state (what's been proposed, tried, decided).
   - Relevant files/constraints/conventions Codex needs to know.
   - What you want from Codex (critique, alternative, code, plan refinement).

### Message file format (note `arc:` field, arc-prefixed filename)

Frontmatter is the **first thing in the file** (line 1 = `---`). Heading goes
inside the body. Use the actual current UTC time, not the placeholder.

```markdown
---
protocol: interagent-discussion/v1
arc: 1
message_index: 1
from: claude
to: codex
status: continue
reply_to: null
created_at_utc: <ISO 8601 UTC>
---

# Claude → Codex, message arc01-001

## User-supplied context

Inline context (verbatim):
~~~
<exact inline context, do not modify; use ~~~~ if content has ~~~ inside>
~~~

topic.md (verbatim):
~~~
<exact topic.md content, do not modify; longer fence if content has ~~~>
~~~

[optional synthesis below the verbatim blocks]

## [your cold-start brief]

...
```

### Frontmatter schema

**Required:** `protocol`, `arc`, `message_index`, `from`, `to`, `status`, `reply_to`, `created_at_utc`.

**Optional:**
- `agent_turn: <int>` — informational only.
- `message_cap: <int>` — omit unless extension accepted (then `20`).
- `extension_requested_cap: 20` — set to propose extension.
- `extension_accepted: true` — set when accepting extension.

`arc` is per-arc-numbered. `message_index` is per-arc and resets each arc to 1.

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
  Set-Content -LiteralPath $tmp -Value $Content -Encoding utf8
  Move-Item -LiteralPath $tmp -Destination (Join-Path $Folder $FinalName)
}

function Write-PlanRevision {
  param([string]$Folder, [string]$PlanBaseName, [int]$Revision, [string]$Content)
  $plansDir = Join-Path $Folder 'plans'
  New-Item -ItemType Directory -Force -Path $plansDir | Out-Null
  $finalName = "{0}_r{1:D3}.md" -f $PlanBaseName, $Revision
  $finalPath = Join-Path $plansDir $finalName
  if (Test-Path -LiteralPath $finalPath) {
    throw "Plan revision file '$finalName' already exists. Plan revisions are immutable; bump to revision $($Revision + 1)."
  }
  $tmp = Join-Path $plansDir ('.tmp_' + [guid]::NewGuid().ToString('N') + '.md')
  Set-Content -LiteralPath $tmp -Value $Content -Encoding utf8
  Move-Item -LiteralPath $tmp -Destination $finalPath
}
```

Final filename for arc 1 message 1: `arc01_001_claude_to_codex.md`.

## Step 7 — Discussion loop

The active per-arc cap starts at 10; if an extension is accepted, it becomes
20 for the rest of the arc.

1. **Wait for Codex's next message.** Codex writes even per-arc indexes
   (`arc01_002_codex_to_claude.md`, etc.). Use the polling helper — it
   watches both the target file AND `outcome.md`.

2. **Branch on what appeared:**
   - `outcome.md` appeared → done; read it, summarize to user, exit.
   - Target message appeared → read and validate (`protocol`, `arc`, `from`,
     `to`, `message_index` = expected next even). Surface mismatch to user.

3. **Apply termination rules** (against the just-read incoming message):
   - Incoming `status: consensus` AND your previous outgoing `status` was
     `consensus` → write `outcome.md`, summarize, exit.
   - Same for `needs-user`.
   - Incoming `message_index == active_cap` → cap reached. Write
     `outcome.md`, summarize, exit.

4. **Re-read any plans listed in `## Plans touched`.** If the incoming
   message has that section, re-read each listed `<leaf>/plans/<name>_r<NNN>.md`
   before composing your reply. The references are to specific revisions.

5. **Handle extension request, if any.** If incoming has
   `extension_requested_cap: 20` and this arc has not yet been extended:
   - **Accept** by setting `message_cap: 20` and `extension_accepted: true`,
     plus a one-line body acknowledgement. After acceptance, **every
     subsequent message in this arc must include `message_cap: 20`**.
   - **Decline** by omitting both fields and explaining in body.
   - Acceptance may happen at message 10; that message may use
     `status: continue` because the cap is now 20.
   - At most one extension per arc.

6. **Handle handover proposal, if any.** If incoming body has
   `## Handover proposal`, accept or decline in your reply's body. If
   accepted, eventual `outcome.md` records `user_facing_agent: codex`.

7. **Compose your reply.** Status:
   - `continue` — more to discuss.
   - `consensus` — you actually agree.
   - `needs-user` — only the user can answer.
   - **At the active cap**: must be `consensus` or `needs-user`. Write
     `outcome.md` directly without waiting (no reply coming).

8. **Edit shared plans this turn (if appropriate).** Plan files live at
   `<leaf>/plans/<name>_r<NNN>.md`. **Never overwrite an existing revision
   file.** Each edit is a new file with bumped revision number. Plan
   frontmatter:
   ```yaml
   ---
   protocol: interagent-discussion/v1
   last_edited_by: claude
   last_edited_at_utc: <UTC ISO 8601>
   revision: <int matching filename suffix>
   ---
   ```
   Optional `## Revision log` body section appending one line per revision.
   If you edit, include a `## Plans touched` section listing each new
   revision file path + one-line reason. Use `Write-PlanRevision`.

9. **Atomic-write the message** via `Write-MessageAtomic` to
   `arc01_<MMM>_claude_to_codex.md` (odd index per arc).

10. **Writer-detects-match termination rule.** After atomic-writing your
    reply, check: did your outgoing `status` match the just-read incoming
    `status` AND is that status terminal?
    - **Yes** → two consecutive matching terminal messages from different
      agents. Write `outcome.md` race-safely (Step 8) and exit. Do NOT
      loop back.
    - **No** → continue to step 11.

11. Loop back to step 1.

### Polling helper (30s sleep, 5-min wait, retry once on TIMEOUT)

```powershell
$arc = 1
$target = Join-Path $Folder ("arc{0:D2}_{1:D3}_codex_to_claude.md" -f $arc, $expectedIndex)
$outcomePath = Join-Path $Folder 'outcome.md'
$start = Get-Date
$deadline = $start.AddMinutes(5)
while (-not (Test-Path -LiteralPath $target) -and -not (Test-Path -LiteralPath $outcomePath) -and (Get-Date) -lt $deadline) {
  $elapsed = [int]((Get-Date) - $start).TotalSeconds
  Write-Output "waiting... ${elapsed}s elapsed"
  Set-Content -LiteralPath (Join-Path $Folder 'heartbeat_claude.txt') -Value (Get-Date -Format o) -Encoding utf8
  Start-Sleep -Seconds 30
}
if (Test-Path -LiteralPath $outcomePath) { Write-Output 'OUTCOME' }
elseif (Test-Path -LiteralPath $target) { Write-Output 'READY' }
else { Write-Output 'TIMEOUT' }
```

Run via PowerShell tool with `timeout: 320000`. On TIMEOUT, retry once
(~10 min total). If still no file, surface to user:

> Codex hasn't responded after ~10 minutes. Invoke the Codex-side
> `codex-discuss-respond` skill (it can find the discussion via parent
> scan), or tell me to keep waiting.

**Do not write `outcome.md` on timeout.**

## Step 8 — Write outcome.md (exactly once, race-safe)

`outcome.md` requires all seven fields below. `ended_at_arc` (an integer)
is required so readers know which arc terminated without filename
inference.

```powershell
$outcomePath = Join-Path $Folder 'outcome.md'
if (-not (Test-Path -LiteralPath $outcomePath)) {
  Write-MessageAtomic -Folder $Folder -FinalName 'outcome.md' -Content $outcomeBody
} else {
  Get-Content -LiteralPath $outcomePath
}
```

Format:

```markdown
---
protocol: interagent-discussion/v1
ended_at_message: <int>
ended_at_arc: 1
ended_by: claude
status: consensus               # consensus | needs-user
user_facing_agent: claude       # claude | codex
implementation_owner: claude    # claude | codex | both
---

## Summary

[2–4 paragraphs.]

## Handover (only if applicable)

[1-line rationale for `user_facing_agent` if handover was proposed and accepted.]

## Implementation responsibility (only if non-default)

[1-line rationale if `implementation_owner` is not the starter, or if `both`.]
```

`implementation_owner` defaults to the starter (`claude` for this skill).
Use `both` for coordinated work where each agent updates their own files
(e.g. updating both sides of this discussion-skill family). The agent that
writes `outcome.md` records the value based on whether anyone proposed a
non-default owner during the discussion.

## Step 9 — Report to the user

Tell the user:

- Generated leaf path (under the parent they supplied).
- Number of messages exchanged (and whether an extension was used).
- Terminal status, `user_facing_agent`, `implementation_owner`.
- 1–2 sentence summary.
- If `needs-user`: what the user must decide.
- File listing.

You (`claude-discuss-start`) are the starter, so by default you are the
user-facing agent.

## Notes & gotchas

- **Filename parity (starter, per arc).** Claude writes odd `message_index`;
  Codex writes even. Resets each arc.
- **Frontmatter on line 1.** No prefix above `---`.
- **Heartbeat files** are best-effort liveness hints, not load-bearing.
- **Temp files** matching `.tmp_*` are ignored by readers.
- **Parent paths with spaces** generate a warning. The generated child leaf
  uses no spaces regardless.
- **Pre-flight before mutation.** No directory creation until parent passes
  pre-flight.
- **Plans never overwrite.** Each edit is a new revision file
  (`<name>_r<NNN>.md`).
- **Use `-LiteralPath`** on path cmdlets for safety with special characters.
- **Cross-host invocation wording.** "Invoke the Codex-side
  `codex-discuss-respond` skill" rather than slash-prefixed examples.
- **`argument-hint` asymmetry.** Claude exposes the argument surface
  through `argument-hint` (in the frontmatter above). Codex skills cannot
  use that frontmatter key (validator constraint) and instead document the
  argument surface in the body and `agents/openai.yaml`.
- **No legacy compatibility.** v2.3 active skills use arc-prefixed filenames
  exclusively. Unprefixed `001_..._md` files belong to retired pre-v2.3
  transcripts and are NOT continuation targets — the most-recent-leaf scan
  in `claude-discuss-continue` ignores folders that lack arc-prefixed
  message files.

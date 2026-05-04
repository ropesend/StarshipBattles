---
name: claude-discuss-continue
description: Continue a previously concluded v2.6 inter-agent discussion with new user-supplied focus context. No-args by default resolves to the most-recent discussion leaf under the default parent. Role-aware self-dispatch: if Claude is the authorized continuation starter (per `outcome.md.continuation_starter`, defaulting to the original arc-1 starter), archives the latest outcome and opens arc N+1; otherwise waits for the authorized agent to write the new arc's first message and joins the respond loop. Use after a discussion has reached a terminal `outcome.md`. Per-arc cap is `5 * len(participants)` messages (extendable once to `10 * n`).
argument-hint: [--folder <path>] [context...]
---

# Inter-Agent Discussion â€” Claude Continues (v2.6)

You are re-opening a previously concluded discussion with new user input.
The skill is **no-args by default**: it resolves to the most-recent
discussion leaf under
`<repo-root>/AgentCoordination/Scratchpad/Discussion/`. The
optional `--folder <path>` flag overrides the target (path may be a parent
or an exact leaf).

Reference: `AgentCoordination/protocols/interagent_discussion.md`.

This is a peer-to-peer dialogue, not a delegation. Other agents are equals.
Push back, propose alternatives, agree only where you have independently
verified or have clearly marked uncertainty.

Evidence rule: Material claims about the codebase, protocol, file contents,
prior transcript, or another agent's behavior must cite `file:line`, a specific
transcript message, or a command/result summary. Label unchecked claims
`[unverified]`. Consensus is blocked while an unverified claim is load-bearing
for the conclusion, plan, or implementation assignment.

The skill is **role-aware** and self-dispatches based on
`outcome.md.continuation_starter` (defaulting to the original arc-1 starter):

- **Claude is the continuation starter** â†’ start arc N+1 (archive outcome,
  write `arc(N+1)_001_claude_to_<P[1]>.md`, enter discussion loop).
- **Another agent is the continuation starter** â†’ wait for the authorized
  agent to write `arc(N+1)_001_*_to_*.md`, then enter the respond loop.

The user's mental model: invoke `claude-discuss-continue` on the Claude
side and the matching skill on the other agent(s) with the same new
context; the right thing happens regardless of who started.

## v2.6 Reliability Rules

Canonical shared spec: `AgentCoordination/protocols/interagent_discussion.md`.
Canonical spec frontmatter includes `protocol_version: 2.6`.

- Publish final protocol artifacts through same-directory `.tmp_*` files and a final rename/move. This applies to message files, plan revisions, outcome files, and ack sidecar files. Direct writes to final protocol filenames are invalid; single-writer safety does not imply reader safety.
- Include `complete: true` in newly written message, plan, outcome, and ack files. If a consumed final file is otherwise valid but lacks `complete: true`, warn and proceed; record it under `## Protocol limitation observed` instead of halting.
- Ack sidecars use `ack_arc<NN>_<MMM>_<from>_to_<to>_<acker>.md`. They are excluded from `message_index`, `reply_to`, cap, consensus, and outcome termination.
- Mandatory observer acks: every participant other than the message author must ack each message before the recipient writes the next substantive reply. The recipient writes its own ack before drafting. If this agent is an observer for the latest message and its ack is missing, write only the observer ack sidecar and stop without writing a protocol message.
- If this agent is the recipient and mandatory observer ack files are missing for the incoming message, write this agent's recipient ack, report the missing observer ack(s), and wait instead of drafting the substantive reply.
- During polling, keep heartbeats as liveness hints with `state: polling | reading | drafting | idle`, `waiting_for`, `last_seen_message`, and `updated_at_utc` when practical.

## Protocol â€” interagent-discussion/v1 (v2.6 spec)

| Field | Value |
|-------|-------|
| Argument surface | `[--folder <path>] [context...]` |
| Default parent | `<repo-root>/AgentCoordination/Scratchpad/Discussion/` |
| Filename pattern | `arc<NN>_<MMM>_<from>_to_<to>.md` |
| Per-arc cap | `5 Ã— n` messages (one in-band extension to `10 Ã— n` per arc) |
| Outcome archiving | move latest `outcome.md` â†’ `outcome_arc<NN>.md` before writing new arc |

## Step 1 â€” Parse arguments

```powershell
function Get-RepoRoot {
  $root = (git rev-parse --show-toplevel 2>$null)
  if ($LASTEXITCODE -eq 0 -and $root) { return $root.Trim() }
  $dir = Get-Location
  while ($dir) {
    if ((Test-Path -LiteralPath (Join-Path $dir 'AGENTS.md')) -and
        (Test-Path -LiteralPath (Join-Path $dir 'game')) -and
        (Test-Path -LiteralPath (Join-Path $dir 'data'))) {
      return $dir.FullName
    }
    $dir = $dir.Parent
  }
  throw 'Unable to discover repository root.'
}

$RepoRoot = Get-RepoRoot
$DefaultParent = Join-Path $RepoRoot 'AgentCoordination\Scratchpad\Discussion'

$FolderArg = ''
$ContextStartIdx = 0
if ($args.Length -ge 2 -and $args[0] -eq '--folder') {
  $FolderArg = $args[1]
  $ContextStartIdx = 2
}
$InlineContext = if ($args.Length -gt $ContextStartIdx) {
  ($args[$ContextStartIdx..($args.Length - 1)] -join ' ')
} else { '' }
```

## Step 2 â€” Resolve the discussion leaf

If `--folder <path>` was given: the path may be a parent or an exact leaf.
If no `--folder`: scan the default parent for the most-recent leaf.

```powershell
function Test-IsLeaf {
  param([string]$P)
  $files = Get-ChildItem -LiteralPath $P -File -ErrorAction SilentlyContinue
  return [bool]($files | Where-Object {
    $_.Name -match '^arc\d{2}_\d{3}_(claude|codex|opencode)_to_(claude|codex|opencode)\.md$' -or
    $_.Name -eq 'outcome.md' -or
    $_.Name -match '^outcome_arc\d{2}\.md$'
  })
}

function Find-MostRecentLeaf {
  param([string]$Parent)
  $candidates = Get-ChildItem -LiteralPath $Parent -Directory -ErrorAction SilentlyContinue |
    Where-Object { Test-IsLeaf -P $_.FullName }
  if (-not $candidates) { return $null }
  $scored = foreach ($c in $candidates) {
    $protocolFiles = Get-ChildItem -LiteralPath $c.FullName -File -ErrorAction SilentlyContinue |
      Where-Object {
        $_.Name -match '^arc\d{2}_\d{3}_(claude|codex|opencode)_to_(claude|codex|opencode)\.md$' -or
        $_.Name -eq 'outcome.md' -or
        $_.Name -match '^outcome_arc\d{2}\.md$'
      }
    $latest = ($protocolFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime
    [PSCustomObject]@{ Path = $c.FullName; Name = $c.Name; LatestProtocolMtime = $latest }
  }
  $best = $scored | Sort-Object @{Expression='LatestProtocolMtime';Descending=$true}, @{Expression='Name';Descending=$true} | Select-Object -First 1
  return $best.Path
}

if ($FolderArg) {
  if (-not [System.IO.Path]::IsPathRooted($FolderArg)) {
    $FolderArg = Join-Path $RepoRoot $FolderArg
  }
  if (-not (Test-Path -LiteralPath $FolderArg)) {
    Write-Output "ABORT: --folder path does not exist: $FolderArg"
    exit 1
  }
  if (Test-IsLeaf -P $FolderArg) {
    $Folder = $FolderArg
  } else {
    $Folder = Find-MostRecentLeaf -Parent $FolderArg
    if (-not $Folder) {
      Write-Output "ABORT: no discussion leaf found in $FolderArg"
      exit 1
    }
    Write-Output "Resolved discussion leaf: $Folder"
  }
} else {
  if (-not (Test-Path -LiteralPath $DefaultParent)) {
    Write-Output "ABORT: default parent does not exist: $DefaultParent"
    exit 1
  }
  $Folder = Find-MostRecentLeaf -Parent $DefaultParent
  if (-not $Folder) {
    Write-Output "ABORT: no prior discussion found in $DefaultParent. Use claude-discuss-start to open a new one, or pass --folder to target a specific path."
    exit 1
  }
  Write-Output "Resolved most-recent discussion leaf: $Folder"
}
```

## Step 3 â€” Read original starter and `participants` from arc 1

```powershell
$arc1Files = Get-ChildItem -LiteralPath $Folder -File -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -match '^arc01_001_(claude|codex|opencode)_to_(claude|codex|opencode)\.md$' }
if (-not $arc1Files) {
  Write-Output "ABORT: leaf has no arc01_001_*_to_*.md file."
  exit 1
}

$starterFile = $arc1Files | Select-Object -First 1
if ($starterFile.Name -match '^arc01_001_(\w+)_to_(\w+)\.md$') {
  $originalStarter = $matches[1]
}
Write-Output "Original arc-1 starter: $originalStarter"

# Parse participants from arc01_001 frontmatter; fall back to v2.3 readback
$arc1Body = Get-Content -LiteralPath $starterFile.FullName -Raw
$Participants = @()
if ($arc1Body -match '(?s)^---\s*\n(.*?)\n---') {
  $fm = $matches[1]
  if ($fm -match '(?m)^participants:\s*\[([^\]]*)\]') {
    $Participants = @($matches[1] -split ',' | ForEach-Object { $_.Trim() })
  }
}
if (-not $Participants) {
  if ($starterFile.Name -match '^arc01_001_(\w+)_to_(\w+)\.md$') {
    $Participants = @($matches[1], $matches[2])
    Write-Output "v2.3 readback: derived participants = [$($Participants -join ', ')]"
  }
}
$N = $Participants.Count
```

## Step 4 â€” Determine next arc number and read continuation_starter

```powershell
$prefixedFiles = Get-ChildItem -LiteralPath $Folder -File -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -match '^arc(\d{2})_' }
$maxArc = ($prefixedFiles | ForEach-Object {
  if ($_.Name -match '^arc(\d{2})_') { [int]$matches[1] } else { 0 }
} | Measure-Object -Maximum).Maximum
if (-not $maxArc) {
  Write-Output "ABORT: leaf has no arc-prefixed protocol files."
  exit 1
}
$newArc = $maxArc + 1
$priorArc = $maxArc
$outcomePath = Join-Path $Folder 'outcome.md'

# Read continuation_starter from outcome.md (defaults to original starter)
$continuationStarter = $originalStarter
if (Test-Path -LiteralPath $outcomePath) {
  $outcomeBody = Get-Content -LiteralPath $outcomePath -Raw
  if ($outcomeBody -match '(?s)^---\s*\n(.*?)\n---') {
    if ($matches[1] -match '(?m)^continuation_starter:\s*(\w+)') {
      $continuationStarter = $matches[1]
    }
  }
}
Write-Output "Continuation starter (per outcome): $continuationStarter"
```

## Step 5 â€” Apply the dispatch table

| Caller role | `outcome.md` exists? | Next-arc starter file exists? | Action |
|---|---|---|---|
| starter (claude is continuation_starter) | yes | n/a | **Mode A**: archive outcome, write `arc<newArc>_001`, enter loop |
| starter | no | n/a | ABORT: latest arc still live |
| responder (someone else is continuation_starter) | yes | no | **Mode B-wait**: wait for starter to archive + write; validate; enter respond loop |
| responder | yes | yes | **Mode B-join**: validate `arc<newArc>_001`, enter respond loop |
| responder | no | yes | **Mode B-join**: validate `arc<newArc>_001`, enter respond loop |
| responder | no | no | ABORT: live/inconsistent state |

```powershell
$invokingAgent = 'claude'
$claudeRole = if ($continuationStarter -eq 'claude') { 'starter' } else { 'responder' }

# Look for any next-arc starter file (don't know which agent will start)
$nextArcStarterFiles = Get-ChildItem -LiteralPath $Folder -File -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -match ("^arc{0:D2}_001_(\w+)_to_(\w+)\.md$" -f $newArc) }
$nextStarterExists = [bool]$nextArcStarterFiles
$outcomeExists = Test-Path -LiteralPath $outcomePath

if ($claudeRole -eq 'starter') {
  if (-not $outcomeExists) {
    Write-Output "ABORT: latest arc still live (no outcome.md). Use claude-discuss-respond, or finish the current arc first."
    exit 1
  }
  $mode = 'A'
} else {
  if ($outcomeExists -and -not $nextStarterExists) {
    $mode = 'B-wait'
  } elseif ($nextStarterExists) {
    $mode = 'B-join'
  } else {
    Write-Output "ABORT: live/inconsistent state â€” no outcome.md and no next-arc starter."
    exit 1
  }
}
Write-Output "Continue mode: $mode"
```

## Step 6 â€” Mode A: claude is the continuation starter

### A.1 â€” Compose new arc message in memory

Per v2.3 ordering: compose first, archive second, write third. If composition
fails, the previous outcome stays in place.

Body must include:

1. **`## User-supplied context`** â€” verbatim fenced block of `$InlineContext`
   (longer fence if content has `~~~`). Do not paraphrase.
2. **`## Turn topology`** â€” per spec Â§3.4, required for arc starters.
3. **Prior arc summary** â€” read `outcome.md` (about to be archived) and
   summarize. Reference relevant prior plan revisions by versioned filename
   (`plans/<name>_r<NNN>.md`).
4. **What's new in this arc** â€” the user's new direction.

Recipient: `participants[1 mod n]` = `participants[1]` (since claude is at
index 0 only when claude was the original arc-1 starter; otherwise claude's
index in participants was set by arc 1 and the recipient is the next agent
in turn order from claude's index).

Wait â€” for continuation, claude is **not necessarily** at index 0 of
`participants`. The participants order was fixed at arc 1. The continuation
arc's message 1 still has `from = participants[(1-1) mod n] = participants[0]`.
But `continuation_starter` may have authorized claude (not at index 0) to
start arc N+1.

**This is a real conflict.** Â§1.2's turn formula says msg-1 author is
`participants[0]`. If `continuation_starter == claude` but claude isn't
`participants[0]`, the formula and the authorization disagree.

**Resolution**: continuation arc must rotate `participants` so that
`continuation_starter` is at index 0 for that arc. The set is the same; the
order rotates. Record this rotation explicitly in the new arc's `arc<NN>_001`
frontmatter as `participants: [<rotated>]`. The arc's local turn formula
uses the rotated order.

(This is the cleanest interpretation of "continuation_starter authorizes
the next arc.")

### A.2 â€” Compute rotated participants

```powershell
$claudeIdx = [Array]::IndexOf($Participants, 'claude')
$rotated = @($Participants[$claudeIdx..($N-1)]) + @($Participants[0..($claudeIdx-1)])
if ($claudeIdx -eq 0) { $rotated = $Participants }
$recipient = $rotated[1]
Write-Output "Rotated participants for new arc: [$($rotated -join ', ')]"
Write-Output "Recipient of arc${newArc}_001: $recipient"
```

### A.3 â€” Archive previous outcome.md

```powershell
$archiveName = "outcome_arc{0:D2}.md" -f $priorArc
$archivePath = Join-Path $Folder $archiveName
if (Test-Path -LiteralPath $archivePath) {
  Write-Output "ABORT: archive target $archiveName already exists. State inconsistent."
  exit 1
}
Move-Item -LiteralPath $outcomePath -Destination $archivePath
Write-Output "Archived previous outcome â†’ $archiveName"
```

### A.4 â€” Atomic-write the new arc's message 001

```powershell
$newName = "arc{0:D2}_001_claude_to_{1}.md" -f $newArc, $recipient
Write-MessageAtomic -Folder $Folder -FinalName $newName -Content $messageBody
Write-Output "Wrote $newName (arc $newArc message 001)"
```

The message frontmatter MUST include `participants: [<rotated>]` and
`turn_order: round-robin`.

### A.5 â€” Enter the standard discussion loop

Identical to `claude-discuss-respond`'s loop (Step 10), with `$activeArc =
$newArc` and the rotated `$Participants`. Use the polling helper, atomic
write helpers, and plan revision helper from this skill.

At terminal: write fresh `outcome.md` (latest is always at `outcome.md`;
archives are historical).

## Step 7 â€” Mode B: claude is responder for this continuation

### B.0 â€” Locally-typed context: warn-and-ignore

```powershell
if ($InlineContext) {
  $excerpt = if ($InlineContext.Length -gt 80) { $InlineContext.Substring(0, 80) + '...' } else { $InlineContext }
  Write-Warning "The starter's forwarded context is canonical; your locally-typed context will not be propagated: '$excerpt'"
}
```

### B.1 â€” Wait for next-arc starter message (if Mode B-wait)

If `mode == 'B-wait'`: poll for `arc<newArc>_001_<continuationStarter>_to_*.md`.

```powershell
$pattern = "arc{0:D2}_001_{1}_to_*.md" -f $newArc, $continuationStarter
$start = Get-Date
$deadline = $start.AddMinutes(5)
while ((@(Get-ChildItem -LiteralPath $Folder -File -Filter $pattern -ErrorAction SilentlyContinue)).Count -eq 0 -and (Get-Date) -lt $deadline) {
  $elapsed = [int]((Get-Date) - $start).TotalSeconds
  Write-Output "waiting for $continuationStarter to write arc $newArc message 001... ${elapsed}s elapsed"
  Set-Content -LiteralPath (Join-Path $Folder 'heartbeat_claude.txt') -Value (Get-Date -Format o) -Encoding utf8
  Start-Sleep -Seconds 30
}
$matches = @(Get-ChildItem -LiteralPath $Folder -File -Filter $pattern -ErrorAction SilentlyContinue)
if ($matches.Count -eq 0) { Write-Output 'TIMEOUT' } else { Write-Output 'READY' }
```

Run with `timeout: 320000`. Retry once.

### B.2 â€” Read and validate the new arc's message 001

Required: `protocol == interagent-discussion/v1`, `arc == newArc`,
`message_index == 1`, `from == continuationStarter`,
`participants` and `turn_order` present (rotated ring with
`continuationStarter` at index 0).

If validation fails, write your scheduled message with `status: needs-user`
and a `## Validation failure` body. If no safe write target exists, abort.

### B.3 â€” Compute claude's incoming wait target on the new arc

Use the rotated `$Participants` from arc N+1's frontmatter. Apply Step 6
of `claude-discuss-respond`'s loop logic to compute `i_in` and enter the
respond loop.

## Step 8 â€” Atomic write helpers

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
    throw "Plan revision '$finalName' already exists. Bump to revision $($Revision + 1)."
  }
  $tmp = Join-Path $plansDir ('.tmp_' + [guid]::NewGuid().ToString('N') + '.md')
  Set-Content -LiteralPath $tmp -Value $Content -Encoding utf8
  Move-Item -LiteralPath $tmp -Destination $finalPath
}
```

## Step 9 â€” Polling helper

Same shape as start/respond: 30s sleep, 5-min wait, watches both target
glob and `outcome.md` (during the loop). Retry once on TIMEOUT, no
`outcome.md` on timeout.

## Protocol self-improvement

- Use `## Protocol limitation observed` in a `status: continue` message for non-blocking protocol friction.
- Use `## Protocol amendment proposal` in a `status: needs-user` message when a protocol limitation blocks progress, risks invalid consensus, or needs user approval.
- Blocking amendments use normal immutable plan revisions under `plans/`; do not create new frontmatter fields or a separate amendment directory.

## Step 10 â€” Write outcome.md at end of arc

When the arc terminates, write fresh `outcome.md` per the spec Â§7 schema.

```markdown
---
protocol: interagent-discussion/v1
ended_at_message: <int>
ended_at_arc: <newArc>
ended_by: <claude|codex|opencode>
status: consensus              # consensus | needs-user
user_facing_agent: <agent>     # default = original arc-1 starter
implementation_owner: <agent>  # default = original starter
implementation_owners: [<a>, <a>]   # required iff owner == multiple
continuation_starter: <agent>       # optional; default = original starter
---

## Summary
## Handover (only if applicable)
## Implementation responsibility (only if non-default)
```

`user_facing_agent` defaults to the **original arc-1 starter** â€”
continuation does not change that identity unless a handover is accepted.
Same for `implementation_owner`.

## Step 11 â€” Report to the user

You only deliver the substantive user-facing report if you are the
user-facing agent (default = original arc-1 starter):

- **If Claude is the original arc-1 starter**: deliver the full report.
- **Otherwise**: minimal acknowledgement (one line: discussion closed,
  leaf path) unless a handover to Claude was accepted.

## Notes & gotchas

- **Compose before archive before write.** Don't archive the previous
  outcome until the new message body is fully composed.
- **Self-dispatch via `continuation_starter`.** Don't run Mode A logic if
  `continuation_starter` (or default = original starter) is not Claude.
- **Continuation arc rotates participants.** The set is preserved, but
  the order rotates so `continuation_starter` is at index 0 for the new
  arc. The new arc's `arc<NN>_001` frontmatter records the rotated
  `participants` explicitly. Per spec Â§1, the original arc-1
  `participants` order is the canonical order for the discussion as a
  whole â€” but each arc's local turn formula uses its own rotation.
- **Per-arc reset.** `message_index` resets to 1 each arc. Cap state
  does NOT carry from arc N to arc N+1.
- **Latest outcome is always `outcome.md`.** Historical outcomes are
  `outcome_arc<NN>.md`. Don't write `outcome_arc<newArc>.md` yourself â€”
  reserved for archive of THIS arc's outcome by a future continuation.
- **Plan revisions persist across arcs.** Revisions accumulate in
  `plans/`. References use `<name>_r<NNN>.md`.
- **`implementation_owner` defaults to original arc-1 starter.**
- **Frontmatter on line 1.**
- **Use `-LiteralPath`** for safety with special characters.
- **Cross-host invocation wording.** Refer to "the Codex-side
  `codex-discuss-continue` skill" or "the OpenCode-side
  `ocode-discuss-continue` skill" rather than slash-prefixed examples.
- **`argument-hint` asymmetry.** Claude/OpenCode skills expose argument
  surface via `argument-hint`; Codex documents in body and `agents/openai.yaml`.
- **v2.3 readback.** When `participants` is missing from `arc01_001`,
  derive `[arc01_001.from, arc01_001.to]`. `turn_order = round-robin`.
  Legacy `implementation_owner: both` accepted only for v2.3 outcome
  readback.
- **`Find-MostRecentLeaf` ignores folders without arc-prefixed files.**
  Pre-v2.3 unprefixed transcripts are not continuation targets.

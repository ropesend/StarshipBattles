---
name: claude-discuss-respond
description: Join a v2.5 inter-agent discussion that Codex or OpenCode opened. Defaults to the shared discussion parent unless `--folder` is supplied; if a parent is given, this skill scans for exactly one pending discussion where the latest message is addressed to Claude. The skill is polymorphic across 2-party and 3-party discussions and does not care which agent opened the discussion.
argument-hint: [--folder <folder-or-parent>]
---

# Inter-Agent Discussion — Claude Responds (v2.5)

You are joining a multi-turn discussion. The folder defaults to
`<repo-root>/AgentCoordination/Scratchpad/Discussion`; `--folder` may point to
the exact discussion leaf OR a parent folder containing one or more discussion
leaves. This skill resolves the leaf via parent-folder discovery (latest-state
based, NOT pair-specific).

Reference: `AgentCoordination/protocols/interagent_discussion.md`.

This is a peer-to-peer dialogue, not a delegation. Other agents are your
equals. Push back, propose alternatives, agree only where you have independently
verified or have clearly marked uncertainty.

Evidence rule: Material claims about the codebase, protocol, file contents,
prior transcript, or another agent's behavior must cite `file:line`, a specific
transcript message, or a command/result summary. Label unchecked claims
`[unverified]`. Consensus is blocked while an unverified claim is load-bearing
for the conclusion, plan, or implementation assignment.

## Protocol — interagent-discussion/v1 (v2.5 spec)

| Field | Value |
|-------|-------|
| Argument | optional `--folder <folder-or-parent>`; defaults to `<repo-root>/AgentCoordination/Scratchpad/Discussion` |
| Filename pattern | `arc<NN>_<MMM>_<from>_to_<to>.md`, where from/to ∈ `{claude,codex,opencode}` |
| Turn formula | `from = P[(i-1) mod n]`, `to = P[i mod n]` where `P = participants`, `n = len(P)` |
| Default per-arc cap | `5 × n` messages (one in-band extension to `10 × n` per arc) |
| Termination | Last `n` messages all uniform terminal status, OR cap reached, OR pre-existing `outcome.md` |
| Atomicity | `.tmp_<guid>.md` then `Move-Item` to final name |
| Shared plans | `<leaf>/plans/<name>_r<NNN>.md` — versioned siblings, never overwrite |

Responder does not take inline context — context arrives forwarded in the
arc-starter message.

## Step 1 — Resolve the folder

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
$Path = Join-Path $RepoRoot 'AgentCoordination\Scratchpad\Discussion'
if ($args.Length -ge 2 -and $args[0] -eq '--folder') {
  $Path = $args[1]
} elseif ($args.Length -gt 0) {
  Write-Output 'ABORT: use --folder <folder-or-parent>; positional folders are not part of v2.5.'
  exit 1
}
if (-not [System.IO.Path]::IsPathRooted($Path)) {
  $Path = Join-Path $RepoRoot $Path
}
if (-not (Test-Path -LiteralPath $Path)) {
  Write-Output "ABORT: path does not exist: $Path"
  exit 1
}
```

## Step 2 — Whitespace warning (informational)

```powershell
$leaf = Split-Path -Path $Path -Leaf
if ($leaf -match '\s') {
  $suggestion = ($leaf -replace '\s+', '-')
  Write-Warning "Path leaf '$leaf' contains whitespace. Recommended: '$suggestion'."
}
```

## Step 3 — Latest-state parent-folder discovery

The argument may be the leaf or a parent.

**Resolution algorithm:**

1. **Try as leaf.** If `$Path` directly contains v2.5 protocol files
   matching `^arc\d{2}_\d{3}_(claude|codex|opencode)_to_(claude|codex|opencode)\.md$`,
   `^outcome\.md$`, or `^outcome_arc\d{2}\.md$`, treat it as a leaf and
   skip to Step 4.

2. **Otherwise scan children.** For each immediate sub-folder of `$Path`
   that is a leaf, skip those with `outcome.md` present (they are
   handled by `claude-discuss-continue`, not `respond`). For each
   remaining leaf:
   1. Find the highest-numbered arc with at least one message.
   2. Find the highest-indexed message in that arc (excluding `.tmp_*`).
   3. Parse its frontmatter.
   4. The leaf is a candidate iff `to == claude`.

3. Apply the count rule:
   - **Zero candidates** → keep polling for ~5 minutes (the starter may
     still be writing message 1). After timeout, retry once. If still
     nothing: "no pending discussion found in `<parent>`. Make sure the
     starter's `*-discuss-start` skill has been invoked."
   - **Exactly one candidate** → use it; log the resolved leaf for the user.
   - **Multiple candidates** → abort with an ambiguity message listing
     candidate child folder names. User must re-invoke with an explicit leaf.

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

function Get-LatestMessageMeta {
  param([string]$P)
  $msgs = Get-ChildItem -LiteralPath $P -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match '^arc(\d{2})_(\d{3})_(\w+)_to_(\w+)\.md$' }
  if (-not $msgs) { return $null }
  $best = $msgs | ForEach-Object {
    if ($_.Name -match '^arc(\d{2})_(\d{3})_(\w+)_to_(\w+)\.md$') {
      [PSCustomObject]@{
        Path = $_.FullName
        Arc = [int]$matches[1]
        Idx = [int]$matches[2]
        From = $matches[3]
        To = $matches[4]
      }
    }
  } | Sort-Object @{Expression='Arc';Descending=$true},@{Expression='Idx';Descending=$true} | Select-Object -First 1
  return $best
}

function Test-IsPendingForClaudeResponder {
  param([string]$P)
  if (-not (Test-IsLeaf -P $P)) { return $false }
  if (Test-Path -LiteralPath (Join-Path $P 'outcome.md')) { return $false }
  $meta = Get-LatestMessageMeta -P $P
  if (-not $meta) { return $false }
  return ($meta.To -eq 'claude')
}

if (Test-IsLeaf -P $Path) {
  $Folder = $Path
} else {
  $Folder = $null
  $start = Get-Date
  $deadline = $start.AddMinutes(5)
  while (-not $Folder -and (Get-Date) -lt $deadline) {
    $candidates = Get-ChildItem -LiteralPath $Path -Directory -ErrorAction SilentlyContinue |
      Where-Object { Test-IsPendingForClaudeResponder -P $_.FullName }
    if ($candidates -and $candidates.Count -eq 1) {
      $Folder = $candidates[0].FullName
      break
    } elseif ($candidates -and $candidates.Count -gt 1) {
      Write-Output "ABORT: multiple candidate discussions in $Path. Re-invoke with the explicit leaf."
      $candidates | ForEach-Object { Write-Output "  - $($_.Name)" }
      exit 1
    }
    Start-Sleep -Seconds 30
  }
  if (-not $Folder) {
    Write-Output "ABORT: no pending discussion found in $Path after 5 min."
    exit 1
  }
  Write-Output "Resolved discussion leaf: $Folder"
}
```

## Step 4 — Pre-flight non-mutation

The responder never creates `<leaf>/plans/`. Plan writers create it
immediately before their first plan write.

If `outcome.md` exists at the leaf, the latest arc is concluded — `respond`
is the wrong skill. Surface and exit.

```powershell
$outcomePath = Join-Path $Folder 'outcome.md'
if (Test-Path -LiteralPath $outcomePath) {
  Write-Output "EXISTING_OUTCOME — latest arc is concluded."
  Get-Content -LiteralPath $outcomePath
  Write-Output ""
  Write-Output "If you want to continue this discussion with new context, use claude-discuss-continue (when authorized by continuation_starter or as the original arc-1 starter)."
  exit 0
}
```

## Step 5 — Determine active arc and parse `participants`

The active arc is the highest arc-prefix found in the leaf's filenames.
The `participants` and `turn_order` come from the arc-1 starter message.

```powershell
$arcFiles = Get-ChildItem -LiteralPath $Folder -File -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -match '^arc(\d{2})_' }
if (-not $arcFiles) {
  Write-Output "ABORT: leaf has no arc-prefixed protocol files."
  exit 1
}
$activeArc = ($arcFiles | ForEach-Object { if ($_.Name -match '^arc(\d{2})_') { [int]$matches[1] } else { 0 } } | Measure-Object -Maximum).Maximum

# Read arc01 starter for participants
$arc1Starter = $arcFiles | Where-Object { $_.Name -match '^arc01_001_' } | Select-Object -First 1
if (-not $arc1Starter) {
  Write-Output "ABORT: leaf missing arc01_001_*.md"
  exit 1
}
$arc1Body = Get-Content -LiteralPath $arc1Starter.FullName -Raw
# Extract participants from frontmatter (parse YAML-ish first --- block)
if ($arc1Body -match '(?s)^---\s*\n(.*?)\n---') {
  $fm = $matches[1]
  if ($fm -match '(?m)^participants:\s*\[([^\]]*)\]') {
    $Participants = @($matches[1] -split ',' | ForEach-Object { $_.Trim() })
  } else {
    # v2.3 readback: derive from arc01_001 from/to
    if ($arc1Starter.Name -match '^arc01_001_(\w+)_to_(\w+)\.md$') {
      $Participants = @($matches[1], $matches[2])
      Write-Output "v2.3 readback: derived participants = [$($Participants -join ', ')]"
    }
  }
} else {
  Write-Output "ABORT: arc01_001 has no parseable frontmatter."
  exit 1
}
$N = $Participants.Count
if ('claude' -notin $Participants) {
  Write-Output "ABORT: claude is not in participants ($($Participants -join ', '))"
  exit 1
}
```

## Step 6 — Compute incoming wait target

`i_in` = smallest unused index in active arc where
`participants[i_in mod n] == 'claude'`.

```powershell
$existingIdxs = @($arcFiles | Where-Object { $_.Name -match ("^arc{0:D2}_(\d{3})_" -f $activeArc) } |
  ForEach-Object { if ($_.Name -match ("^arc{0:D2}_(\d{3})_" -f $activeArc)) { [int]$matches[1] } })
$i = 1
while ($true) {
  if ($i -notin $existingIdxs) {
    if ($Participants[$i % $N] -eq 'claude') { $i_in = $i; break }
  }
  $i++
  if ($i -gt 100) { Write-Output "ABORT: could not find next claude turn"; exit 1 }
}
Write-Output "Incoming wait target: arc$($activeArc.ToString('D2'))_$($i_in.ToString('D3'))_*_to_claude.md"
```

## Step 7 — Wait for the incoming message (poll)

```powershell
$pattern = "arc{0:D2}_{1:D3}_*_to_claude.md" -f $activeArc, $i_in
$start = Get-Date
$deadline = $start.AddMinutes(5)
while ((@(Get-ChildItem -LiteralPath $Folder -File -Filter $pattern -ErrorAction SilentlyContinue)).Count -eq 0 -and -not (Test-Path -LiteralPath $outcomePath) -and (Get-Date) -lt $deadline) {
  $elapsed = [int]((Get-Date) - $start).TotalSeconds
  Write-Output "waiting for $pattern... ${elapsed}s elapsed"
  Set-Content -LiteralPath (Join-Path $Folder 'heartbeat_claude.txt') -Value (Get-Date -Format o) -Encoding utf8
  Start-Sleep -Seconds 30
}
$matches = @(Get-ChildItem -LiteralPath $Folder -File -Filter $pattern -ErrorAction SilentlyContinue)
if (Test-Path -LiteralPath $outcomePath) { Write-Output 'OUTCOME' }
elseif ($matches.Count -eq 1) { Write-Output 'READY'; Write-Output $matches[0].Name }
elseif ($matches.Count -gt 1) { Write-Output 'FORK'; $matches | ForEach-Object { Write-Output $_.Name } }
else { Write-Output 'TIMEOUT' }
```

Run with `timeout: 320000`. Retry once on TIMEOUT.

On `FORK`: write your scheduled message at index `j_out = i_in + 1`
(if turn-aligned) with `status: needs-user` and `## Validation failure`
body. Otherwise abort.

## Step 8 — Read incoming and validate

Required validation per v2.5:

1. **Schema**: required fields present; `from != to`; `from`/`to` ∈ `{claude,codex,opencode}`.
2. **Turn alignment**: `from == participants[(message_index-1) mod n]` AND
   `to == participants[message_index mod n]` AND `to == claude`.
3. **Index continuity**: `reply_to == message_index - 1` for `i > 1`.

If validation fails, write your scheduled message with `status: needs-user`
and a `## Validation failure` body.

If the message is the arc-1 starter (i.e. you're responding immediately
without anyone else having spoken — only possible if `claude` is at
index 1 in a 2-party where someone else started): also confirm
`participants` matches the arc01_001 you parsed in Step 5.

If the incoming message has `## User-supplied context`, the verbatim fenced
blocks are authoritative user intent. Do not paraphrase.

## Step 9 — Apply termination rules (re-read last `n` messages)

- **Unanimous terminal**: last `n` messages all carry the same terminal
  status (uniform `consensus` xor `needs-user`) → write `outcome.md`,
  summarize, exit. (Note: if you arrived to find the last `n` messages
  already terminal and `outcome.md` not yet written, you write it.)
- **Cap reached**: if the just-read message has `message_index == active_cap`,
  it should be the cap message. Read its `status` (must be `needs-user`),
  write `outcome.md`, summarize, exit.

If neither terminates, proceed to Step 10.

## Step 10 — Discussion loop

You are alternating with the other agents per the round-robin formula.

Repeat until terminal:

1. **Re-read any plans listed in `## Plans touched`** before composing
   your reply.

2. **Handle extension request**, if any. Active cap starts at `5×n`. Accept
   by setting `message_cap: <10×n>` and `extension_accepted: true`. After
   acceptance, every subsequent message must include `message_cap: <10×n>`.

3. **Handle handover proposal**, if any.

4. **Compose your reply.** Status: `continue` / `consensus` / `needs-user`.
   At cap: must use `needs-user` (per spec §5.3).

5. **Edit shared plans this turn (if appropriate).** Plan files at
   `<leaf>/plans/<name>_r<NNN>.md`. Never overwrite. Use `Write-PlanRevision`.

### Protocol self-improvement

- Use `## Protocol limitation observed` in a `status: continue` message for non-blocking protocol friction.
- Use `## Protocol amendment proposal` in a `status: needs-user` message when a protocol limitation blocks progress, risks invalid consensus, or needs user approval.
- Blocking amendments use normal immutable plan revisions under `plans/`; do not create new frontmatter fields or a separate amendment directory.

6. **Compute outgoing write target.** `j_out = i_in + 1`. Verify
   `participants[(j_out-1) mod n] == 'claude'`. Recipient is
   `participants[j_out mod n]`. Filename:
   `arc<activeArc:D2>_<j_out:D3>_claude_to_<recipient>.md`. Atomic-write
   via `Write-MessageAtomic`.

7. **Writer-detects-match.** After writing, re-read last `n` messages.
   If unanimous terminal, write `outcome.md` race-safely (Step 11) and
   exit. Do NOT loop.

8. **Wait for next incoming**. New `i_in` = `j_out + (n-1)` if the next
   round-robin lands on you again right away (false in 3-party);
   otherwise the next claude index. Use the polling helper.

9. Loop.

### Message file format

```markdown
---
protocol: interagent-discussion/v1
arc: <N>
message_index: <M>
from: claude
to: <P[M mod n]>
status: continue
reply_to: <M-1>
created_at_utc: <ISO 8601 UTC>
---

# Claude → <recipient>, message arc<NN>-<MMM>

[reply / counterpoint / agreement]

## Plans touched

(Only if you created a new plan revision file this turn.)
```

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
    throw "Plan revision '$finalName' already exists. Bump to revision $($Revision + 1)."
  }
  $tmp = Join-Path $plansDir ('.tmp_' + [guid]::NewGuid().ToString('N') + '.md')
  Set-Content -LiteralPath $tmp -Value $Content -Encoding utf8
  Move-Item -LiteralPath $tmp -Destination $finalPath
}
```

## Step 11 — Write outcome.md (exactly once, race-safe)

Before writing:

1. Re-read the last `n` messages to confirm termination still holds.
2. Re-check `outcome.md` does not exist.
3. Atomic-write via temp+rename.
4. If the rename target already exists, read it and stop. Do not retry.

```markdown
---
protocol: interagent-discussion/v1
ended_at_message: <int>
ended_at_arc: <N>
ended_by: claude
status: consensus               # consensus | needs-user
user_facing_agent: <claude|codex|opencode>   # default = original arc-1 starter
implementation_owner: <claude|codex|opencode|multiple>   # default = original starter
implementation_owners: [<agent>, <agent>]   # required iff owner == multiple
continuation_starter: <agent>                # optional; default = original starter
---

## Summary

[2–4 paragraphs.]

## Handover (only if applicable)
## Implementation responsibility (only if non-default)
```

## Step 12 — Report to the user (only if you are the user-facing agent)

Default: `user_facing_agent` = original arc-1 starter (whoever wrote
`arc01_001_*.md`). If that's not Claude, deliver a one-line acknowledgement
(discussion closed, leaf path) and stop — the starter delivers the substantive
summary.

If a handover to Claude was accepted, deliver the full report (folder,
message count, terminal status, summary, file listing).

## Notes & gotchas

- **Latest-state discovery, not pair-specific.** The v2.3 heuristic of
  "Codex started, no Claude reply" is gone. Any leaf where the latest
  message is `to: claude` is a candidate.
- **Polymorphic across topology.** Same skill handles 2-party and 3-party,
  and works regardless of which agent opened the discussion.
- **Frontmatter on line 1.**
- **Heartbeat files** are best-effort liveness hints.
- **Temp files** matching `.tmp_*` are ignored by readers.
- **Plans never overwrite.** Each edit is a new revision file.
- **Use `-LiteralPath`** for safety with special characters.
- **Don't paraphrase** verbatim user-supplied context.
- **Fence-collision rule:** longer fence if content contains `~~~`.
- **Default user-facing agent is the original arc-1 starter.**
- **Cross-host invocation wording.** "Invoke the Codex-side
  `codex-discuss-start` skill" or "Invoke the OpenCode-side
  `ocode-discuss-start` skill" rather than slash-prefixed examples.
- **`argument-hint` asymmetry.** Claude/OpenCode skills expose argument
  surface via `argument-hint`; Codex documents in body and `agents/openai.yaml`.
- **v2.3 readback.** When `participants` is missing from `arc01_001`,
  derive it from `[arc01_001.from, arc01_001.to]`. Legacy
  `implementation_owner: both` accepted for v2.3 outcome readback only.

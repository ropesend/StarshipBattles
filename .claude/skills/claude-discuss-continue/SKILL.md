---
name: claude-discuss-continue
description: Continue a previously concluded inter-agent discussion with new user-supplied focus context. No-args by default — resolves to the most-recent v2.3 discussion leaf under the default parent. Role-aware self-dispatch: if Claude was the original starter, archives the latest outcome and opens arc N+1; if Claude was the original responder, waits for the new arc's first message from Codex and replies. Use after a discussion has reached a terminal `outcome.md`. Per-arc cap is 10 messages (extendable once to 20).
argument-hint: [--folder <path>] [context...]
---

# Inter-Agent Discussion — Claude Continues (v2.3)

You are re-opening a previously concluded discussion with new user input.
The skill is **no-args by default**: it resolves to the most-recent
v2.3 discussion leaf under
`c:\Dev\StarshipBattles\AgentCoordination\Scratchpad\Discussion\`. The
optional `--folder <path>` flag overrides the target (path may be a parent
or an exact leaf).

The skill is **role-aware** and self-dispatches based on which agent
originally started the discussion:

- **Original starter was Claude** → start arc N+1 (archive outcome, write
  `arc(N+1)_001_claude_to_codex.md`, enter discussion loop).
- **Original starter was Codex** → wait for `arc(N+1)_001_codex_to_claude.md`
  from the Codex-side `codex-discuss-continue`, then enter respond loop.

The user's mental model: invoke `claude-discuss-continue` on the Claude
side and the Codex equivalent on the Codex side, both with the same new
context; the right thing happens.

## Protocol — interagent-discussion/v1 (v2.3 spec)

| Field | Value |
|-------|-------|
| Argument surface | `[--folder <path>] [context...]` |
| Default parent | `c:\Dev\StarshipBattles\AgentCoordination\Scratchpad\Discussion\` |
| Filename pattern | `arc<NN>_<MMM>_<from>_to_<to>.md` (sole pattern; no legacy fallback) |
| Per-arc cap | 10 messages (one in-band extension to 20 allowed per arc) |
| Outcome archiving | move latest `outcome.md` → `outcome_arc<NN>.md` before writing new arc |

## Step 1 — Parse arguments

```powershell
$DefaultParent = 'c:\Dev\StarshipBattles\AgentCoordination\Scratchpad\Discussion'

# Optional --folder <path> flag, must come before context
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

## Step 2 — Resolve the discussion leaf

If `--folder <path>` was given: the path may be a parent or an exact leaf.
If no `--folder`: scan the default parent for the most-recent leaf.

### Helper: `Test-IsLeaf`

```powershell
function Test-IsLeaf {
  param([string]$P)
  $files = Get-ChildItem -LiteralPath $P -File -ErrorAction SilentlyContinue
  return [bool]($files | Where-Object {
    $_.Name -match '^arc\d{2}_\d{3}_(claude|codex)_to_(claude|codex)\.md$' -or
    $_.Name -eq 'outcome.md' -or
    $_.Name -match '^outcome_arc\d{2}\.md$'
  })
}
```

### Helper: `Find-MostRecentLeaf`

Among immediate children of the parent: keep candidates that are leaves;
score each by the newest `LastWriteTime` of its **protocol files only**
(messages, `outcome.md`, `outcome_arc<NN>.md`); rank by score descending,
tiebreak by child name descending.

```powershell
function Find-MostRecentLeaf {
  param([string]$Parent)
  $candidates = Get-ChildItem -LiteralPath $Parent -Directory -ErrorAction SilentlyContinue |
    Where-Object { Test-IsLeaf -P $_.FullName }
  if (-not $candidates) { return $null }
  $scored = foreach ($c in $candidates) {
    $protocolFiles = Get-ChildItem -LiteralPath $c.FullName -File -ErrorAction SilentlyContinue |
      Where-Object {
        $_.Name -match '^arc\d{2}_\d{3}_(claude|codex)_to_(claude|codex)\.md$' -or
        $_.Name -eq 'outcome.md' -or
        $_.Name -match '^outcome_arc\d{2}\.md$'
      }
    $latest = ($protocolFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime
    [PSCustomObject]@{ Path = $c.FullName; Name = $c.Name; LatestProtocolMtime = $latest }
  }
  $best = $scored | Sort-Object @{Expression='LatestProtocolMtime';Descending=$true}, @{Expression='Name';Descending=$true} | Select-Object -First 1
  return $best.Path
}
```

### Resolution logic

```powershell
if ($FolderArg) {
  if (-not [System.IO.Path]::IsPathRooted($FolderArg)) {
    $FolderArg = Join-Path 'c:\Dev\StarshipBattles' $FolderArg
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
      Write-Output "ABORT: no v2.3 discussion leaf found in $FolderArg"
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
    Write-Output "ABORT: no prior v2.3 discussion found in $DefaultParent. Use claude-discuss-start to open a new one, or pass --folder to target a specific path."
    exit 1
  }
  Write-Output "Resolved most-recent discussion leaf: $Folder"
}
```

## Step 3 — Read original starter from arc 1

```powershell
$arc1Files = Get-ChildItem -LiteralPath $Folder -File -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -match '^arc01_001_(claude|codex)_to_(claude|codex)\.md$' }
if (-not $arc1Files) {
  Write-Output "ABORT: leaf has no arc01_001_*_to_*.md file. Not a v2.3 discussion."
  exit 1
}

$starterFile = $arc1Files | Select-Object -First 1
if ($starterFile.Name -match '^arc01_001_claude_to_codex\.md$') {
  $originalStarter = 'claude'
} elseif ($starterFile.Name -match '^arc01_001_codex_to_claude\.md$') {
  $originalStarter = 'codex'
}
$invokingAgent = 'claude'
$claudeRole = if ($originalStarter -eq 'claude') { 'starter' } else { 'responder' }
Write-Output "Original starter: $originalStarter; this skill's role: $claudeRole"
```

## Step 4 — Determine the next arc number

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
```

## Step 5 — Apply the edge-case table and dispatch

| Caller role | `outcome.md` exists? | Next-arc starter message exists? | Action |
|---|---|---|---|
| starter | yes | n/a | **Mode A:** archive outcome, write `arc<newArc>_001`, enter loop |
| starter | no | n/a | ABORT: latest arc still live; use respond or finish current arc |
| responder | yes | no | **Mode B-wait:** wait for starter to archive + write; then validate, enter respond loop |
| responder | yes | yes | (race) **Mode B-join:** validate `arc<newArc>_001`, enter respond loop |
| responder | no | yes | **Mode B-join:** validate `arc<newArc>_001`, enter respond loop |
| responder | no | no | ABORT: live/inconsistent state |

```powershell
$nextArcStarterPattern = "arc{0:D2}_001_{1}_to_{2}.md" -f $newArc, $originalStarter, ($invokingAgent)
$nextArcStarterPath = Join-Path $Folder $nextArcStarterPattern
$outcomeExists = Test-Path -LiteralPath $outcomePath
$nextStarterExists = Test-Path -LiteralPath $nextArcStarterPath

if ($claudeRole -eq 'starter') {
  if (-not $outcomeExists) {
    Write-Output "ABORT: latest arc still live (no outcome.md at $Folder). Use claude-discuss-respond, or finish the current arc first."
    exit 1
  }
  $mode = 'A'
} else {
  # responder
  if ($outcomeExists -and -not $nextStarterExists) {
    $mode = 'B-wait'
  } elseif ($nextStarterExists) {
    $mode = 'B-join'
  } else {
    Write-Output "ABORT: live/inconsistent state — no outcome.md and no next-arc starter message at $Folder."
    exit 1
  }
}
Write-Output "Continue mode: $mode"
```

## Step 6 — Mode A: original starter (Claude continues a Claude-started discussion)

### A.1 — Compose new arc message in memory

Per v2.2/v2.3 ordering: compose first, archive second, write third. If
composition fails for any reason, the previous outcome stays in place.

Body must include:

1. **`## User-supplied context`** — verbatim fenced block of `$InlineContext`
   (longer fence if content has `~~~`). Do not paraphrase.
2. **Prior arc summary** — read `outcome.md` (about to be archived) and
   summarize the prior consensus. Reference relevant prior plan revisions
   by versioned filename (`plans/<name>_r<NNN>.md`).
3. **What's new in this arc** — the user's new direction, what they want
   refined, any constraints they're adding or removing.

### A.2 — Archive previous outcome.md

```powershell
$archiveName = "outcome_arc{0:D2}.md" -f $priorArc
$archivePath = Join-Path $Folder $archiveName
if (Test-Path -LiteralPath $archivePath) {
  Write-Output "ABORT: archive target $archiveName already exists. State inconsistent."
  exit 1
}
Move-Item -LiteralPath $outcomePath -Destination $archivePath
Write-Output "Archived previous outcome → $archiveName"
```

### A.3 — Atomic-write the new arc's message 001

```powershell
$newName = "arc{0:D2}_001_claude_to_codex.md" -f $newArc
Write-MessageAtomic -Folder $Folder -FinalName $newName -Content $messageBody
Write-Output "Wrote $newName (arc $newArc message 001)"
```

### A.4 — Enter the standard discussion loop

Identical to `claude-discuss-start`'s discussion loop (Step 7), with
`$activeArc = $newArc`. Wait for `arc<newArc>_002_codex_to_claude.md`,
alternate odd messages, apply termination rules (writer-detects-match,
two-confirmation, cap reached). Use the polling helper, atomic write
helpers, and plan revision helper from this skill (defined below).

At terminal: write fresh `outcome.md` (the latest is always at
`outcome.md`; archives are the historical ones).

## Step 7 — Mode B: original responder (Claude responds to a Codex-started continuation)

In Mode B, Claude is NOT the original starter. The user invoked
`claude-discuss-continue` to indicate they want to participate in arc
N+1, but the actual new-arc starter message must come from Codex.

### B.0 — Locally-typed context: warn-and-ignore

```powershell
if ($InlineContext) {
  $excerpt = if ($InlineContext.Length -gt 80) { $InlineContext.Substring(0, 80) + '...' } else { $InlineContext }
  Write-Warning "The starter's forwarded context is canonical; your locally-typed context will not be propagated: '$excerpt'"
}
```

The starter (Codex) forwards the user's verbatim block in
`arc<newArc>_001_codex_to_claude.md`. Don't cross-validate.

### B.1 — Wait for the next-arc starter message

If `mode == 'B-wait'`: poll for `arc<newArc>_001_codex_to_claude.md`. The
starter must archive the previous `outcome.md` before writing the new
message; both events together transition us into a live arc.

```powershell
$target = Join-Path $Folder ("arc{0:D2}_001_codex_to_claude.md" -f $newArc)
$start = Get-Date
$deadline = $start.AddMinutes(5)
while (-not (Test-Path -LiteralPath $target) -and (Get-Date) -lt $deadline) {
  $elapsed = [int]((Get-Date) - $start).TotalSeconds
  Write-Output "waiting for Codex to write arc $newArc message 001... ${elapsed}s elapsed"
  Set-Content -LiteralPath (Join-Path $Folder 'heartbeat_claude.txt') -Value (Get-Date -Format o) -Encoding utf8
  Start-Sleep -Seconds 30
}
if (-not (Test-Path -LiteralPath $target)) { Write-Output 'TIMEOUT' } else { Write-Output 'READY' }
```

Run with `timeout: 320000`. Retry once on TIMEOUT.

If `mode == 'B-join'`: the file is already present. Skip waiting.

### B.2 — Read and validate

```powershell
# Read $target's frontmatter
# Validate: protocol == interagent-discussion/v1, arc == $newArc, message_index == 1,
# from == codex, to == claude
```

If validation fails, surface to user.

### B.3 — Enter the respond loop on arc N+1

Identical to `claude-discuss-respond`'s discussion loop (Step 8), with
`$activeArc = $newArc`. You write even per-arc indexes
(`arc<newArc>_002_claude_to_codex.md`, etc.); Codex writes odd. Apply
termination rules; at terminal, write fresh `outcome.md`.

## Step 8 — Atomic write helpers

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

## Step 9 — Polling helper

Same shape as in start/respond: 30s sleep, 5-min wait, watches both target
and `outcome.md` (during the loop; the initial wait in Mode B-wait can
skip the outcome watch since outcome was just archived). Retry once on
TIMEOUT, no `outcome.md` on timeout.

## Step 10 — Write outcome.md at end of arc

When the arc terminates, write fresh `outcome.md`. The latest outcome is
always at `outcome.md`; archives are at `outcome_arc<NN>.md`.

```markdown
---
protocol: interagent-discussion/v1
ended_at_message: <int>
ended_at_arc: <newArc>
ended_by: claude               # or codex if Codex wrote outcome
status: consensus              # consensus | needs-user
user_facing_agent: <claude|codex>   # default = original starter
implementation_owner: <claude|codex|both>   # default = original starter
---

## Summary

[2–4 paragraphs covering this arc's discussion. May reference prior arc(s)
by `outcome_arc<NN>.md`.]

## Handover (only if applicable)

[1-line rationale.]

## Implementation responsibility (only if non-default)

[1-line rationale.]
```

`user_facing_agent` defaults to the **original starter** — continuation
does not change the original-starter identity. Same for
`implementation_owner`.

## Step 11 — Report to the user

You only deliver the substantive user-facing report if you are the
user-facing agent (default = original starter):

- **Mode A (Claude was original starter):** Claude IS the user-facing
  agent (unless handover was accepted). Deliver the full report: leaf
  path, new arc number, message count, terminal status,
  `user_facing_agent`, `implementation_owner`, brief outcome summary,
  references to earlier-arc outcomes if useful.
- **Mode B (Codex was original starter):** Codex is the user-facing
  agent by default. Minimal acknowledgement (one line: discussion closed,
  leaf path) unless handover to Claude was accepted, in which case
  deliver the full report.

## Notes & gotchas

- **Compose before archive before write.** Don't archive the previous
  outcome until the new message body is fully composed.
- **Self-dispatch is mandatory.** Don't run Mode A logic if Claude wasn't
  the original starter — the original-starter identity is set at arc 1
  and persists across continuations.
- **Per-arc reset.** `message_index` resets to 1 each arc. The cap
  (10, +1 extension to 20) is per-arc.
- **Latest outcome is always `outcome.md`.** Historical outcomes are
  `outcome_arc<NN>.md`. Don't write `outcome_arc<newArc>.md` — that
  filename is reserved for archive of THIS arc's outcome when a future
  continuation runs.
- **Plan revisions persist across arcs.** Revisions accumulate in
  `plans/`. References use `<name>_r<NNN>.md`.
- **`implementation_owner` defaults to original starter.** Even after
  continuation. Change only via accepted proposal during this arc.
- **Frontmatter on line 1.** Same as start/respond.
- **Use `-LiteralPath`** for safety with special characters.
- **Cross-host invocation wording.** Refer to "the Codex-side
  `codex-discuss-continue` skill" rather than slash-prefixed examples.
- **`argument-hint` asymmetry.** Claude exposes argument surface via
  `argument-hint`; Codex documents in body and `agents/openai.yaml`.
- **No legacy compatibility.** v2.3 active skills require arc-prefixed
  filenames everywhere. Pre-v2.3 unprefixed transcripts are historical
  artifacts and not continuation targets — `Find-MostRecentLeaf` ignores
  folders without arc-prefixed message files.
- **Both-agents-typing-continue race.** Claude's archive-then-write
  ordering (in Mode A) ensures the responder side never sees a
  half-state where outcome.md is gone but `arc(newArc)_001` is not yet
  present (modulo a brief filesystem race tolerated by polling).

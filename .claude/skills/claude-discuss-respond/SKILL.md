---
name: claude-discuss-respond
description: Join an inter-agent discussion that Codex opened. The argument may be either the exact discussion leaf or a parent folder containing one or more leaves; if a parent is given, this skill scans for exactly one pending discussion matching Claude's responder role. Claude waits for Codex's first message of the current arc, then alternates writing even-indexed replies up to 10 messages per arc (extendable once to 20). Use after the user has invoked the Codex-side `codex-discuss-start` skill.
argument-hint: <folder-or-parent>
---

# Inter-Agent Discussion — Claude Responds (v2.3)

You are joining a multi-turn discussion that Codex opened. The user may pass
the exact discussion leaf OR a parent folder containing one or more
discussion leaves; this skill resolves the leaf via parent-folder discovery.
Codex's opening message for the current arc lives at
`<leaf>/arc<NN>_001_codex_to_claude.md`.

This is a peer-to-peer dialogue, not a delegation. Codex is your equal here.
Push back, propose alternatives, agree where you actually agree.

## Protocol — interagent-discussion/v1 (v2.3 spec)

| Field | Value |
|-------|-------|
| Argument | `$args[0]` — leaf or parent; resolution algorithm below |
| Filename pattern | `arc<NN>_<MMM>_<from>_to_<to>.md` (sole pattern; no legacy fallback) |
| Default per-arc cap | 10 messages (one in-band extension to 20 allowed per arc) |
| Message format | YAML frontmatter (line 1 = `---`) + markdown body |
| Termination | Two consecutive matching terminal statuses, OR cap reached, OR pre-existing `outcome.md` |
| Atomicity | `.tmp_<guid>.md` then `Move-Item` to final name |
| Shared plans | `<leaf>/plans/<name>_r<NNN>.md` — versioned siblings, never overwrite |

Responder does not take inline context — context arrives forwarded in
Codex's first message of the arc.

## Step 1 — Resolve the folder

```powershell
$Path = $args[0]
if (-not [System.IO.Path]::IsPathRooted($Path)) {
  $Path = Join-Path 'c:\Dev\StarshipBattles' $Path
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

## Step 3 — Parent-folder discovery (find the discussion leaf)

The argument may be the leaf or a parent.

**Resolution algorithm:**

1. **Try as leaf.** If `$Path` directly contains v2.3 protocol files
   matching `^arc\d{2}_\d{3}_(claude|codex)_to_(claude|codex)\.md$`,
   `^outcome\.md$`, or `^outcome_arc\d{2}\.md$`, treat it as a leaf and
   skip to Step 4.

2. **Otherwise scan children.** Look at immediate sub-folders of `$Path`.
   For each, check whether it is a **pending live discussion matching
   responder role:**
   - Has an arc-prefixed starter message from Codex
     (`^arc\d{2}_001_codex_to_claude\.md$`).
   - Does NOT have `outcome.md` (the latest arc is live).

3. Apply the count rule:
   - **Zero candidates** → "no pending discussion found in `<parent>`. Make
     sure the Codex-side `codex-discuss-start` skill has been invoked."
   - **Exactly one candidate** → use it; log the resolved leaf for the user.
   - **Multiple candidates** → abort with an ambiguity message listing
     candidate child folder names. User must re-invoke with an explicit leaf.

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

function Test-IsPendingForClaudeResponder {
  param([string]$P)
  if (-not (Test-IsLeaf -P $P)) { return $false }
  if (Test-Path -LiteralPath (Join-Path $P 'outcome.md')) { return $false }
  $hasIncomingStarter = Get-ChildItem -LiteralPath $P -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match '^arc\d{2}_001_codex_to_claude\.md$' }
  return [bool]$hasIncomingStarter
}

if (Test-IsLeaf -P $Path) {
  $Folder = $Path
} else {
  $candidates = Get-ChildItem -LiteralPath $Path -Directory -ErrorAction SilentlyContinue |
    Where-Object { Test-IsPendingForClaudeResponder -P $_.FullName }
  if (-not $candidates) {
    Write-Output "ABORT: no pending discussion found in $Path."
    exit 1
  } elseif ($candidates.Count -gt 1) {
    Write-Output "ABORT: multiple candidate discussions in $Path. Re-invoke with the explicit leaf."
    $candidates | ForEach-Object { Write-Output "  - $($_.Name)" }
    exit 1
  } else {
    $Folder = $candidates[0].FullName
    Write-Output "Resolved discussion leaf: $Folder"
  }
}
```

## Step 4 — Pre-flight non-mutation

The responder never creates `<leaf>/plans/`. Plan writers create it
immediately before their first plan write (handled by `Write-PlanRevision`).

If `outcome.md` exists at the leaf, the latest arc is concluded — `respond`
is the wrong skill. Surface and exit:

```powershell
$outcomePath = Join-Path $Folder 'outcome.md'
if (Test-Path -LiteralPath $outcomePath) {
  Write-Output "EXISTING_OUTCOME — latest arc is concluded."
  Get-Content -LiteralPath $outcomePath
  Write-Output ""
  Write-Output "If you want to continue this discussion with new context, use claude-discuss-continue (if Claude was the original starter) or the Codex-side codex-discuss-continue (if Codex was)."
  exit 0
}
```

Wrong-parity check:

```powershell
$hasClaudeStarted = Get-ChildItem -LiteralPath $Folder -File -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -match '^arc\d{2}_001_claude_to_codex\.md$' }
$hasCodexStarted = Get-ChildItem -LiteralPath $Folder -File -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -match '^arc\d{2}_001_codex_to_claude\.md$' }
if ($hasClaudeStarted -and -not $hasCodexStarted) {
  Write-Output "ABORT: leaf has claude_to_codex starter but no codex_to_claude. claude-discuss-respond is for joining a Codex-started discussion. Use claude-discuss-start instead."
  exit 1
}
```

## Step 5 — Determine the active arc

The active arc is the highest arc-prefix found in the leaf's filenames.

```powershell
$activeArc = (Get-ChildItem -LiteralPath $Folder -File -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -match '^arc(\d{2})_' } |
  ForEach-Object { if ($_.Name -match '^arc(\d{2})_') { [int]$matches[1] } else { 0 } } |
  Measure-Object -Maximum).Maximum
if (-not $activeArc) {
  Write-Output "ABORT: leaf has no arc-prefixed protocol files. Not a v2.3 discussion."
  exit 1
}
```

## Step 6 — Wait for Codex's first message of the active arc

```powershell
$expectedFromCodex = Join-Path $Folder ("arc{0:D2}_001_codex_to_claude.md" -f $activeArc)
$start = Get-Date
$deadline = $start.AddMinutes(5)
while (-not (Test-Path -LiteralPath $expectedFromCodex) -and -not (Test-Path -LiteralPath $outcomePath) -and (Get-Date) -lt $deadline) {
  $elapsed = [int]((Get-Date) - $start).TotalSeconds
  Write-Output "waiting... ${elapsed}s elapsed"
  Set-Content -LiteralPath (Join-Path $Folder 'heartbeat_claude.txt') -Value (Get-Date -Format o) -Encoding utf8
  Start-Sleep -Seconds 30
}
if (Test-Path -LiteralPath $outcomePath) { Write-Output 'OUTCOME' }
elseif (Test-Path -LiteralPath $expectedFromCodex) { Write-Output 'READY' }
else { Write-Output 'TIMEOUT' }
```

Run with `timeout: 320000`. Retry once on TIMEOUT (~10 min total).

## Step 7 — Read message 001 of the arc and validate

Required frontmatter fields:

- `protocol: interagent-discussion/v1`
- `arc: <activeArc>`
- `message_index: 1`
- `from: codex`, `to: claude`

If frontmatter is wrong, surface to the user.

Codex's message will include a `## User-supplied context` section if the
user provided inline context or `topic.md` to Codex. **Treat the verbatim
fenced blocks as authoritative user intent.** Do not paraphrase.

## Step 8 — Discussion loop

You are alternating with Codex. **Claude writes even per-arc indexes**
(`002`, `004`, ..., `010`; post-extension `012`, ..., `020`). Codex writes
odd indexes.

Per-arc cap starts at 10; if extension is accepted, becomes 20.

Repeat until terminal:

1. **Apply termination rules** against the just-read incoming message:
   - `outcome.md` already exists → done; read, summarize, exit.
   - Incoming `status: consensus` AND your previous outgoing was
     `consensus` → write `outcome.md`, summarize, exit.
   - Same for `needs-user`.
   - Incoming `message_index == active_cap` → cap reached. Write
     `outcome.md`, summarize, exit.

2. **Re-read any plans listed in `## Plans touched`** before composing
   your reply. References point to specific revision files like
   `plans/<name>_r<NNN>.md`.

3. **Handle extension request, if any.**
   - **Accept**: set `message_cap: 20` and `extension_accepted: true`,
     plus one-line body ack. Every subsequent message in this arc must
     include `message_cap: 20`.
   - **Decline**: omit fields, explain in body.
   - At most one extension per arc.

4. **Handle handover proposal, if any.** Body markdown only. If accepted,
   `outcome.md.user_facing_agent` = `claude`.

5. **Compose your reply.** Status: `continue` / `consensus` / `needs-user`.
   At cap: must use `consensus` or `needs-user`.

6. **Edit shared plans this turn (if appropriate).** Plan files at
   `<leaf>/plans/<name>_r<NNN>.md`. **Never overwrite an existing
   revision.** Each edit is a new file with bumped revision number. Plan
   frontmatter:
   ```yaml
   ---
   protocol: interagent-discussion/v1
   last_edited_by: claude
   last_edited_at_utc: <UTC ISO 8601>
   revision: <int matching filename suffix>
   ---
   ```
   If you edit, include `## Plans touched` listing each new revision file.
   Use `Write-PlanRevision`.

7. **Atomic-write the message** via `Write-MessageAtomic` to
   `arc<NN>_<MMM>_claude_to_codex.md` (even per-arc index).

8. **Writer-detects-match termination rule.** After writing, check if your
   outgoing status matches incoming AND is terminal. If yes → write
   `outcome.md` race-safely and exit. Do NOT loop back.

9. **Wait for Codex's next message** at
   `arc<NN>_<MMM+1>_codex_to_claude.md` using the polling helper.
   Validate. Loop.

### Message file format

Frontmatter is the **first thing in the file**. Use longer fences for
verbatim content containing `~~~`.

```markdown
---
protocol: interagent-discussion/v1
arc: <N>
message_index: <M>
from: claude
to: codex
status: continue
reply_to: <previous incoming message_index>
created_at_utc: <ISO 8601 UTC>
---

# Claude → Codex, message arc<NN>-<MMM>

[reply / counterpoint / agreement]

## Plans touched

(Only if you created a new plan revision file this turn.)
```

### Frontmatter schema

**Required:** `protocol`, `arc`, `message_index`, `from`, `to`, `status`, `reply_to`, `created_at_utc`.

**Optional:**
- `agent_turn: <int>` — informational only.
- `message_cap: <int>` — omit unless extension accepted (then `20`).
- `extension_requested_cap: 20` — set to propose an extension.
- `extension_accepted: true` — set when accepting a proposed extension.

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

### Polling helper

Same shape as in `claude-discuss-start`: 30s sleep, 5-min wait, watches
both target and `outcome.md`, retry once on TIMEOUT, no `outcome.md` on
timeout.

## Step 9 — Write outcome.md (exactly once, race-safe)

`outcome.md` requires all seven fields below.

```markdown
---
protocol: interagent-discussion/v1
ended_at_message: <int>
ended_at_arc: <N>
ended_by: claude
status: consensus               # consensus | needs-user
user_facing_agent: codex        # default = starter (codex when Claude is responding)
implementation_owner: codex     # default = starter; can be claude or both via discussion
---

## Summary

[2–4 paragraphs.]

## Handover (only if applicable)

[1-line rationale for `user_facing_agent` if handover was proposed and accepted.]

## Implementation responsibility (only if non-default)

[1-line rationale if `implementation_owner` is not the starter.]
```

`user_facing_agent` defaults to **the starter** (so `codex` when Claude is
responding). `implementation_owner` defaults to the starter likewise. Both
change only via accepted proposal during the discussion.

## Step 10 — Report to the user (only if you are the user-facing agent)

Per default: **the starter is the user-facing agent** unless a handover
was accepted. As `claude-discuss-respond`, the starter is Codex. **You
are NOT the default user-facing agent.**

- If `outcome.md.user_facing_agent == codex`: minimal acknowledgement to
  the user (one line: discussion closed, leaf path) and stop. Codex
  delivers the substantive summary.
- If a handover to `claude` was accepted: deliver the full report (folder,
  message count, terminal status, summary, file listing).

## Notes & gotchas

- **Filename parity (responder, per arc).** Codex writes odd; Claude
  writes even. Resets each arc.
- **Frontmatter on line 1.** No prefix above `---`.
- **Heartbeat files** are best-effort liveness hints.
- **Temp files** matching `.tmp_*` are ignored by readers.
- **Parent-folder discovery.** Try-as-leaf-first; otherwise scan children
  for one pending discussion matching role. Zero/multiple → surface
  cleanly.
- **Pre-flight non-mutation.** Responder never creates `plans/`.
- **Plans never overwrite.** Each edit is a new revision file
  (`<name>_r<NNN>.md`).
- **Use `-LiteralPath`** for safety with special characters.
- **Don't paraphrase** verbatim user-supplied context.
- **Fence-collision rule:** longer fence if content contains `~~~`.
- **Default user-facing agent is the starter** (Codex when responding).
- **Cross-host invocation wording.** "Invoke the Codex-side
  `codex-discuss-start` skill" rather than slash-prefixed examples.
- **`argument-hint` asymmetry.** Claude exposes argument surface via
  `argument-hint`; Codex documents in body and `agents/openai.yaml` only.
- **No legacy compatibility.** v2.3 active skills require arc-prefixed
  filenames everywhere. Pre-v2.3 unprefixed transcripts are historical
  artifacts and not continuation/respond targets.

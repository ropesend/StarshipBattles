---
name: claude-discuss-start
description: Open a v2.4 inter-agent discussion with Codex and/or OpenCode. The user supplies a parent folder; this skill creates a timestamped child sub-folder for the discussion, writes message arc01_001 with optional inline focus context, declares the participant set + canonical-ring turn order, and alternates per the round-robin formula until consensus, needs-user, the per-arc cap, or a pre-existing outcome.md. Defaults to a 2-party Claude+Codex discussion; pass `--with codex,opencode` for 3-party or `--with opencode` for Claude+OpenCode.
argument-hint: <parent-folder> [--slug <slug>] [--with <agents>] [context...]
---

# Inter-Agent Discussion — Claude Starts (v2.4)

You are opening a multi-turn discussion with one or two other agents.
Participants are drawn from `{claude, codex, opencode}` per the canonical
ring. The user supplies a **parent** folder; you create a timestamped child
sub-folder. The user invokes the matching `*-discuss-respond` skill on each
other participant; those skills find the leaf via parent scan.

This is a peer-to-peer dialogue, not a delegation. Other agents are your
equals. Push back, propose alternatives, agree where you actually agree.

## Protocol — interagent-discussion/v1 (v2.4 spec)

| Field | Value |
|-------|-------|
| Parent | `$args[0]`; absolute or repo-relative; quote if it contains spaces |
| Discussion leaf | child of parent: `YYYYMMDDTHHMMSSZ[_<slug>]/` |
| Slug flag | optional `--slug <kebab-case>` (separate flag arg) |
| Participants flag | optional `--with <comma-separated agents>`; default `codex` |
| Inline context | tokens after the optional flags, joined and forwarded verbatim |
| `topic.md` | optional `<leaf>/topic.md`, read at start, forwarded verbatim |
| Filename pattern | `arc<NN>_<MMM>_<from>_to_<to>.md`, where from/to ∈ `{claude,codex,opencode}` |
| Turn formula | `from = P[(i-1) mod n]`, `to = P[i mod n]` where `P = participants`, `n = len(P)`, `i = message_index` |
| Default per-arc cap | `5 × n` messages (one in-band extension to `10 × n` per arc) |
| Termination | Last `n` messages all uniform terminal status, OR cap reached, OR pre-existing `outcome.md` |
| Atomicity | `.tmp_<guid>.md` then `Move-Item` to final name |
| Shared plans | `<leaf>/plans/<name>_r<NNN>.md` — versioned siblings, never overwrite |

## Step 1 — Parse arguments

```powershell
$Parent = $args[0]
if (-not [System.IO.Path]::IsPathRooted($Parent)) {
  $Parent = Join-Path 'c:\Dev\Starship Battles' $Parent
}

# Optional flags after parent: --slug <slug> and/or --with <agents>
$Slug = ''
$WithList = 'codex'  # default: 2-party Claude+Codex
$Idx = 1
while ($Idx -lt $args.Length) {
  if ($args[$Idx] -eq '--slug' -and $Idx + 1 -lt $args.Length) {
    $Slug = $args[$Idx + 1]
    if ($Slug -match '\s' -or $Slug -notmatch '^[a-z0-9][a-z0-9-]*$') {
      Write-Output "ABORT: --slug must be lowercase kebab-case (a-z, 0-9, '-'), got '$Slug'"
      exit 1
    }
    $Idx += 2
  } elseif ($args[$Idx] -eq '--with' -and $Idx + 1 -lt $args.Length) {
    $WithList = $args[$Idx + 1]
    $Idx += 2
  } else {
    break
  }
}
$InlineContext = if ($args.Length -gt $Idx) {
  ($args[$Idx..($args.Length - 1)] -join ' ')
} else { '' }

# Build participants per spec §1.1: canonical ring [claude, codex, opencode]
# rotated so starter (claude) is at index 0, filtered to participants present.
$With = @($WithList -split ',' | ForEach-Object { $_.Trim().ToLower() } | Where-Object { $_ })
foreach ($a in $With) {
  if ($a -notin @('codex','opencode')) {
    Write-Output "ABORT: --with values must be one or more of: codex, opencode (claude is implicit). Got '$a'."
    exit 1
  }
}
$Participants = @('claude') + @('codex','opencode' | Where-Object { $_ -in $With })
$N = $Participants.Count
if ($N -lt 2 -or $N -gt 3) { Write-Output "ABORT: must have 2 or 3 participants, got $N"; exit 1 }
Write-Output ("Participants: " + ($Participants -join ', ') + " (n=$N)")
```

**Slug parsing is flag-based**. Inline context never gets confused with a flag.

## Step 2 — Whitespace warning on the parent leaf

```powershell
$parentLeaf = Split-Path -Path $Parent -Leaf
if ($parentLeaf -match '\s') {
  $suggestion = ($parentLeaf -replace '\s+', '-')
  Write-Warning "Parent folder leaf '$parentLeaf' contains whitespace. Recommended: rename to '$suggestion'. The generated child folder will use no spaces regardless."
}
```

## Step 3 — Pre-flight: refuse to clobber a leaf-shaped path

```powershell
if (Test-Path -LiteralPath $Parent) {
  $leafFiles = Get-ChildItem -LiteralPath $Parent -File -ErrorAction SilentlyContinue |
    Where-Object {
      $_.Name -match '^arc\d{2}_\d{3}_(claude|codex|opencode)_to_(claude|codex|opencode)\.md$' -or
      $_.Name -eq 'outcome.md' -or
      $_.Name -match '^outcome_arc\d{2}\.md$'
    }
  if ($leafFiles) {
    Write-Output "ABORT: '$Parent' looks like an existing discussion leaf, not a parent."
    $leafFiles | Select-Object -First 5 | ForEach-Object { Write-Output "  - $($_.Name)" }
    exit 1
  }
}
```

**Pre-flight before any mutation.**

## Step 4 — Generate child leaf and folder structure

```powershell
$timestamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
$ChildLeaf = if ($Slug) { "${timestamp}_${Slug}" } else { $timestamp }
$Folder = Join-Path $Parent $ChildLeaf
New-Item -ItemType Directory -Force -Path $Parent | Out-Null
New-Item -ItemType Directory -Force -Path $Folder | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $Folder 'plans') | Out-Null
Write-Output "Discussion leaf: $Folder"
```

Recommended (not enforced) parent location:
`AgentCoordination/Scratchpad/Discussion/` per CLAUDE.md scratchpad rule.

## Step 5 — Read optional `<leaf>/topic.md`

```powershell
$TopicMd = ''
$topicPath = Join-Path $Folder 'topic.md'
if (Test-Path -LiteralPath $topicPath) { $TopicMd = Get-Content -LiteralPath $topicPath -Raw }
```

## Step 6 — Compose and write `arc01_001_claude_to_<P[1]>.md`

The recipient of message 1 is `participants[1 mod n]` = `participants[1]`.

Body must include, in order:

1. **`## User-supplied context`** — only if inline context or `topic.md` is
   non-empty. Each in a separate fenced block, **verbatim**. Do NOT
   summarize, paraphrase, or modify these blocks. Synthesis below them is OK.
   **Fence-collision rule:** if verbatim content contains `~~~`, use a longer
   fence (`~~~~` etc.).

2. **`## Turn topology`** — required for every arc-starter message
   (`message_index: 1`). One-line arrow chain, e.g.:
   ```markdown
   ## Turn topology

   Turn order: claude -> codex -> opencode -> claude
   ```

3. **Cold-start context** — other agents have no shared memory with you. Convey:
   - The user's underlying request or problem.
   - The current state (what's been proposed, tried, decided).
   - Relevant files/constraints/conventions other agents need to know.
   - What you want from each other agent.

### Message file format (v2.4 — adds `participants` and `turn_order` to arc-starter frontmatter)

Frontmatter is the **first thing in the file** (line 1 = `---`). Heading goes
inside the body. Use the actual current UTC time.

```markdown
---
protocol: interagent-discussion/v1
arc: 1
message_index: 1
from: claude
to: <next agent in ring>
status: continue
reply_to: null
created_at_utc: <ISO 8601 UTC>
participants: [claude, <p1>, <p2>]   # length 2 or 3, claude at index 0
turn_order: round-robin
---

# Claude → <recipient>, message arc01-001

## User-supplied context

Inline context (verbatim):
~~~
<exact inline context>
~~~

topic.md (verbatim):
~~~
<exact topic.md content>
~~~

[optional synthesis]

## Turn topology

Turn order: claude -> <p1> -> ... -> claude

## [your cold-start brief]

...
```

### Frontmatter schema

**Required, every message:** `protocol`, `arc`, `message_index`, `from`, `to`,
`status`, `reply_to`, `created_at_utc`.

**Required, arc-starter messages only:** `participants`, `turn_order`.
(Legal but not required on later messages; if present must match arc 1.)

**Optional:**
- `agent_turn: <int>` — informational only.
- `message_cap: <int>` — required iff extension accepted (then `10×n`).
- `extension_requested_cap: <int>` — set to propose extension.
- `extension_accepted: true` — set when accepting extension.

### Status values

- `continue` — keep discussing.
- `consensus` — agents have converged. **Does not end alone**; the last `n`
  messages must all be `consensus` for unanimous-terminal termination.
- `needs-user` — only the user can answer. Same unanimous rule.

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

Final filename for arc 1 message 1: `arc01_001_claude_to_<P[1]>.md`.

## Step 7 — Discussion loop

The active per-arc cap starts at `5 × n` (n=2 → 10 matching v2.3; n=3 → 15).
Extension takes it to `10 × n`.

1. **Wait for the next message addressed to you.** Compute `i_in` = smallest
   unused message index where `participants[i_in mod n] == 'claude'`. Glob:
   ```
   arc<NN>_<i_in:03d>_*_to_claude.md
   ```
   Use the polling helper. The glob MUST resolve to **exactly one** file.
   Zero → keep waiting. >1 → see Step 7.6 (fork handling).

2. **Branch on what appeared:**
   - `outcome.md` appeared → done; read, summarize, exit.
   - Target message appeared → read and validate per validation rules
     below. Surface mismatch as `needs-user`.

3. **Apply termination rules** (re-read last `n` messages):
   - **Unanimous terminal**: last `n` messages all carry the same terminal
     status (uniform `consensus` xor `needs-user`) → write `outcome.md`,
     summarize, exit. (For `n=2` this is identical to v2.3's
     "two consecutive matching" rule.)
   - **Cap reached**: incoming `message_index == active_cap` → cap reached.
     Write `outcome.md`, summarize, exit.

4. **Re-read any plans listed in `## Plans touched`** before composing your
   reply. References point to specific revision files.

5. **Handle extension request, if any.** If incoming has
   `extension_requested_cap` and this arc has not yet been extended:
   - **Accept** by setting `message_cap: <10×n>` and `extension_accepted: true`,
     plus a one-line body acknowledgement. After acceptance, every subsequent
     message in this arc must include `message_cap: <10×n>`.
   - **Decline** by omitting both fields and explaining in body.
   - At most one extension per arc.

6. **Handle handover proposal, if any.** If incoming body has
   `## Handover proposal`, accept or decline in your reply's body. If
   accepted, `outcome.md.user_facing_agent` records the new agent.

7. **Compose your reply.** Status:
   - `continue` — more to discuss.
   - `consensus` — you actually agree.
   - `needs-user` — only the user can answer.
   - **At the active cap**: the cap message MUST use `status: needs-user`
     (a cap is forced stop, not proof of agreement). If the agents had
     actually converged, the unanimous rule would have terminated earlier.

8. **Edit shared plans this turn (if appropriate).** Plan files at
   `<leaf>/plans/<name>_r<NNN>.md`. **Never overwrite.** Plan frontmatter:
   ```yaml
   ---
   protocol: interagent-discussion/v1
   last_edited_by: claude
   last_edited_at_utc: <UTC ISO 8601>
   revision: <int matching filename suffix>
   ---
   ```
   If you edit, include `## Plans touched` listing each new revision file.

9. **Compute outgoing write target**: `j_out = i_in + 1`. Verify
   `participants[(j_out-1) mod n] == 'claude'`. Recipient is
   `participants[j_out mod n]`. Filename:
   `arc<NN>_<j_out:03d>_claude_to_<recipient>.md`. Atomic-write via
   `Write-MessageAtomic`.

10. **Writer-detects-match termination rule.** After atomic-writing, re-read
    the latest `n` messages and check unanimous terminal. If satisfied,
    write `outcome.md` race-safely (Step 8) and exit. Do NOT loop back.

11. Loop back to step 1.

### Validation rules (apply to every message read or written)

1. **Schema**: required fields present; types correct; `from != to`;
   `from`/`to` ∈ `{claude, codex, opencode}`.
2. **Turn alignment**: `from == participants[(message_index-1) mod n]` AND
   `to == participants[message_index mod n]`.
3. **Index continuity**: per-arc indexes form `1, 2, 3, ...` with no gaps.
   `reply_to == message_index - 1` for `message_index > 1`, `null` for `1`.
4. **Uniqueness**: at most one non-`.tmp_*` file per `(arc, message_index)`.
5. **Stable arc 1 fields**: `participants`/`turn_order` from arc 1 match
   any later occurrences.

A validation failure is **NOT** auto-repaired. Write your next scheduled
message with `status: needs-user` and a `## Validation failure` body. If
no safe write target exists, abort and surface to the user.

### Fork handling (Step 7.6)

If the incoming-glob in Step 7.1 returns >1 file at the same index:

- If a safe outgoing write target exists at `j_out`, write it with
  `status: needs-user` and a `## Validation failure` body listing the
  forked filenames.
- Otherwise abort with a diagnostic. Do not pick.

### Polling helper (30s sleep, 5-min wait, retry once on TIMEOUT)

```powershell
$arc = 1
$expectedIndex = <i_in computed above>
$pattern = "arc{0:D2}_{1:D3}_*_to_claude.md" -f $arc, $expectedIndex
$outcomePath = Join-Path $Folder 'outcome.md'
$start = Get-Date
$deadline = $start.AddMinutes(5)
while ((@(Get-ChildItem -LiteralPath $Folder -File -Filter $pattern -ErrorAction SilentlyContinue)).Count -eq 0 -and -not (Test-Path -LiteralPath $outcomePath) -and (Get-Date) -lt $deadline) {
  $elapsed = [int]((Get-Date) - $start).TotalSeconds
  Write-Output "waiting... ${elapsed}s elapsed"
  Set-Content -LiteralPath (Join-Path $Folder 'heartbeat_claude.txt') -Value (Get-Date -Format o) -Encoding utf8
  Start-Sleep -Seconds 30
}
$matches = @(Get-ChildItem -LiteralPath $Folder -File -Filter $pattern -ErrorAction SilentlyContinue)
if (Test-Path -LiteralPath $outcomePath) { Write-Output 'OUTCOME' }
elseif ($matches.Count -eq 1) { Write-Output 'READY'; Write-Output $matches[0].Name }
elseif ($matches.Count -gt 1) { Write-Output 'FORK'; $matches | ForEach-Object { Write-Output $_.Name } }
else { Write-Output 'TIMEOUT' }
```

Run via PowerShell tool with `timeout: 320000`. On TIMEOUT, retry once
(~10 min total). If still no file, surface to user:

> Other agents haven't responded after ~10 minutes. Invoke the matching
> `*-discuss-respond` skill on each remaining participant, or tell me to
> keep waiting.

**Do not write `outcome.md` on timeout.**

## Step 8 — Write outcome.md (exactly once, race-safe)

Before writing:

1. Re-read the last `n` messages to confirm termination still holds.
2. Re-check `outcome.md` does not exist.
3. Atomic-write via temp+rename.
4. If the rename target already exists, read it and stop. Do not retry.

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
user_facing_agent: claude       # claude | codex | opencode
implementation_owner: claude    # claude | codex | opencode | multiple
implementation_owners: [<agent>, <agent>]   # required iff owner == multiple, ≥2 entries, ⊆ participants
continuation_starter: claude    # optional; default = original starter
---

## Summary

[2–4 paragraphs.]

## Handover (only if applicable)

[1-line rationale for `user_facing_agent` if a handover was proposed and accepted.]

## Implementation responsibility (only if non-default)

[1-line rationale if `implementation_owner` is not the starter, or `multiple`.]
```

`implementation_owners` MUST be present iff `implementation_owner == multiple`,
and absent otherwise. `continuation_starter` defaults to original starter
(claude); set explicitly only to authorize a different agent to open arc N+1.

## Step 9 — Report to the user

You (`claude-discuss-start`) are the starter, so by default you are the
user-facing agent. Tell the user:

- Generated leaf path (under the parent they supplied).
- Number of messages exchanged (and whether an extension was used).
- Terminal status, `user_facing_agent`, `implementation_owner`.
- 1–2 sentence summary.
- If `needs-user`: what the user must decide.
- File listing.

## Notes & gotchas

- **Default `--with codex`**: when not specified, this is a 2-party
  Claude+Codex discussion (matches v2.3 default behavior).
- **Canonical ring**: `[claude, codex, opencode]`, rotated so claude is at
  index 0 (always, since claude is the starter here), filtered to participants
  present. So 3-party = `[claude, codex, opencode]`; Claude+OpenCode 2-party =
  `[claude, opencode]`.
- **Frontmatter on line 1.** No prefix above `---`.
- **Heartbeat files** are best-effort liveness hints, not load-bearing.
- **Temp files** matching `.tmp_*` are ignored by readers.
- **Plans never overwrite.** Each edit is a new revision file.
- **Use `-LiteralPath`** on path cmdlets for safety with special characters.
- **Cross-host invocation wording.** "Invoke the Codex-side
  `codex-discuss-respond` skill" / "Invoke the OpenCode-side
  `ocode-discuss-respond` skill" rather than slash-prefixed examples.
- **`argument-hint` asymmetry.** Claude and OpenCode skills expose the
  argument surface through `argument-hint`. Codex skills cannot use that
  frontmatter key (validator constraint) and document arguments in body
  + `agents/openai.yaml`.
- **v2.3 readback** (for old Claude+Codex transcripts without `participants`):
  derive `participants = [arc01_001.from, arc01_001.to]`,
  `turn_order = round-robin`. Legacy `implementation_owner: both` accepted
  for v2.3 outcome readback only; v2.4 writers never emit it.
- **No legacy compatibility for new discussions.** v2.4 writers always emit
  `participants` and `turn_order` on arc starters.

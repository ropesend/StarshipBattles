---
name: codex-discuss-continue
description: Continue an inter-agent discussion with Claude Code after it has ended, using the same original starter, a role-aware new arc in the same discussion leaf, optional forwarded starter context, archived outcomes, immutable plan revisions, and per-arc consensus or needs-user termination.
---

# Codex Discuss Continue

Continue an ended v2.3 discussion by selecting a prior discussion leaf, dispatching based on the original starter, and entering the normal `interagent-discussion/v1` loop for the next arc.

Reference: `AgentCoordination/Scratchpad/Discussion/20260503T162834Z/plans/v2.3_spec_r001.md`.

## Inputs

Argument surface: `[--folder <path>] [context...]`. Do not add `argument-hint` frontmatter to Codex skills; document argument surfaces in this body and in `agents/openai.yaml`.

- No positional folder.
- `--folder <path>` is an optional flag-style override pointing to either a parent folder or an exact discussion leaf.
- Without `--folder`, use the hardcoded default parent `c:\Dev\StarshipBattles\AgentCoordination\Scratchpad\Discussion\`.
- All remaining tokens after `--folder <path>`, or all tokens if no `--folder` is present, become inline user context.
- If the resolved path's final segment contains whitespace, warn but do not reject.
- Pre-flight checks must not mutate existing folders until the target is validated.
- Read `<leaf>/topic.md` if it exists. Forward it as additional user context only when Codex is the original starter.

## Leaf Resolution

If `--folder <path>` points to an exact leaf containing files matching the v2.3 message regex, `outcome.md`, or `outcome_arc<NN>.md`, use that leaf. Otherwise resolve a parent folder and find its most-recent leaf.

Most-recent leaf scan:

1. Inspect immediate children only.
2. Candidate filter: a child folder must contain at least one protocol-matching file: a message matching `^arc\d{2}_\d{3}_(claude|codex)_to_(claude|codex)\.md$`, `outcome.md`, or `outcome_arc<NN>.md`.
3. Score candidates by newest `LastWriteTime` among protocol-matching files only; heartbeat files, temp files, and plans do not contribute.
4. Break ties by child folder name descending.

If the parent has zero candidate leaves, abort and suggest `codex-discuss-start`.

## Role Detection

Read `arc01_001_*_to_*.md`. The `from:` field identifies the original starter.

- If Codex is the original starter, run the start-of-new-arc flow.
- If Claude is the original starter, wait for the Claude-side continue skill to start the next arc, then respond as Codex.

## Start-Of-New-Arc Flow

Use this flow only when Codex is the original starter.

1. Verify `outcome.md` exists. If it is missing, abort: the latest arc is still live or inconsistent.
2. Verify the outcome frontmatter contains `ended_at_arc`; abort if the locked v2.3 outcome fields are missing.
3. Determine the just-ended arc from `ended_at_arc`.
4. Compose the next message in memory with `## User-supplied context` from inline context and `topic.md`.
5. Atomically move the current `outcome.md` to `outcome_arc<NN>.md`, where `NN` is the just-ended arc number.
6. Atomic-write the next arc starter message, for example `arc02_001_codex_to_claude.md`.
7. Enter the standard discussion loop for the new arc.

During the live continuation arc, no `outcome.md` exists. At the end, write a fresh latest `outcome.md`.

## Respond-On-New-Arc Flow

Use this flow when Claude is the original starter.

- If local context was supplied, warn-and-ignore it: "The starter's forwarded context is canonical; your locally-typed context (`<short excerpt>`) will not be propagated."
- If `outcome.md` exists and the next-arc starter message is absent, wait for Claude to archive `outcome.md` and write the next arc starter message, for example `arc02_001_claude_to_codex.md`.
- If `outcome.md` exists and the next-arc starter message is already present, validate and enter the respond loop.
- If `outcome.md` is missing and the next-arc starter message exists, join that live arc.
- If `outcome.md` is missing and no next-arc starter message exists, abort: live or inconsistent state.

The starter's forwarded context is canonical. Do not cross-validate it against locally typed context.

## Filenames

v2.3 requires arc-prefixed filenames everywhere. Sole message regex: `^arc\d{2}_\d{3}_(claude|codex)_to_(claude|codex)\.md$`.

For a Codex-started arc:

```text
arc01_001_codex_to_claude.md
arc01_002_claude_to_codex.md
arc01_003_codex_to_claude.md
arc01_004_claude_to_codex.md
arc01_005_codex_to_claude.md
arc01_006_claude_to_codex.md
arc01_007_codex_to_claude.md
arc01_008_claude_to_codex.md
arc01_009_codex_to_claude.md
arc01_010_claude_to_codex.md
```

If Claude started the discussion, the order begins with `arc01_001_claude_to_codex.md`. Continuation arcs use the same ordering, such as `arc02_001_codex_to_claude.md` or `arc02_001_claude_to_codex.md`. Do not add fallback handling for old unprefixed transcripts.

## Message Format

Every message starts with frontmatter on line 1.

Required fields: `protocol`, `arc`, `message_index`, `from`, `to`, `status`, `reply_to`, `created_at_utc`. The arc field is written as `arc: <int>`.

Optional fields: `agent_turn`, `message_cap`, `extension_requested_cap`, `extension_accepted`.

```markdown
---
protocol: interagent-discussion/v1
arc: <int>
message_index: 1
from: codex
to: claude
status: continue
reply_to: null
created_at_utc: YYYY-MM-DDTHH:MM:SSZ
---

# Codex continuation message 001
```

Use `continue | consensus | needs-user` for `status`.

## User-Supplied Context

When Codex is the original starter and inline context or `topic.md` exists, include `## User-supplied context` in the next arc starter message. Forward text verbatim in separate labeled fenced blocks. Do not summarize, paraphrase, or modify those blocks.

## Shared Plans

- Plan files live under `plans/`.
- Plan revisions are immutable siblings: `plans/<name>_r001.md`, `plans/<name>_r002.md`, ...
- Latest = highest revision number. Never overwrite an existing revision file.
- Frontmatter includes `revision: <int>`, matching the `_rNNN` suffix.
- `## Plans touched` references the specific new revision file.

## Loop And Extension

The continuation arc uses the normal per-arc loop. Default cap is 10 messages; one extension to 20 is allowed with `extension_requested_cap: 20`, `extension_accepted: true`, and `message_cap: 20`.

After atomic-writing a reply, if outgoing and incoming statuses are the same terminal status (`consensus` or `needs-user`), this is the second matching terminal confirmation: write `outcome.md` immediately and stop. At the active cap, do not write `continue`.

## Waiting

Poll every 30 seconds for up to 5 minutes, watching both the target message and `outcome.md`; then retry once before surfacing timeout. Never write `outcome.md` on timeout.

```powershell
$target = Join-Path $folder "arc02_002_claude_to_codex.md"
$outcome = Join-Path $folder "outcome.md"
$heartbeat = Join-Path $folder "heartbeat_codex.txt"
$deadline = (Get-Date).AddMinutes(5)
while (
    -not (Test-Path -LiteralPath $target) -and
    -not (Test-Path -LiteralPath $outcome) -and
    (Get-Date) -lt $deadline
) {
    Set-Content -LiteralPath $heartbeat -Value (Get-Date -Format o) -Encoding utf8
    Start-Sleep -Seconds 30
}
```

Treat `heartbeat_claude.txt` as an optional liveness hint only.

## Atomic Writes

Use `.tmp_<guid>.md` temporary file names for messages, outcomes, and plans; readers ignore `.tmp_*`.

```powershell
$tmp = Join-Path $folder ('.tmp_' + [guid]::NewGuid().ToString('N') + '.md')
$final = Join-Path $folder "arc02_001_codex_to_claude.md"
Set-Content -LiteralPath $tmp -Value $content -Encoding utf8
Move-Item -LiteralPath $tmp -Destination $final
```

## Outcome

Archive prior outcomes to `outcome_arc<NN>.md`. The latest arc writes a fresh `outcome.md` with all locked fields.

```markdown
---
protocol: interagent-discussion/v1
ended_at_message: 6
ended_at_arc: 2
ended_by: codex
status: consensus
user_facing_agent: codex
implementation_owner: codex
---
```

All seven outcome fields are required. The original starter remains default user-facing agent and implementation owner unless `## Handover proposal` or `## Implementation responsibility` explicitly changes it in the discussion. Use `both` for coordinated self-owned work.

## Implementation Notes

- Default parent folder is `c:\Dev\StarshipBattles\AgentCoordination\Scratchpad\Discussion\`.
- Continue may use an exact leaf or parent folder only through `--folder <path>`.
- Scan immediate children only when resolving a parent folder.
- pre-flight checks must not mutate existing folders before validation.
- Use host-neutral wording for the peer side.
- Use `v2.3_spec_r001.md` as the current implementation reference.
- The second matching terminal writer writes `outcome.md` immediately.

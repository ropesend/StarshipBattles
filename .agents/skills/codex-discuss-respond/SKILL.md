---
name: codex-discuss-respond
description: Respond in an inter-agent discussion with Claude Code through an exact discussion leaf or discoverable parent folder, including forwarded focus context, shared immutable plan revisions, in-band extension, continuation arcs, and explicit user-facing and implementation ownership.
---

# Codex Discuss Respond

Join a v2.3 discussion that Claude Code started, then alternate using the `interagent-discussion/v1` protocol until `consensus`, `needs-user`, timeout, or the active per-arc message cap.

Reference: `AgentCoordination/Scratchpad/Discussion/20260503T162834Z/plans/v2.3_spec_r001.md`.

## Inputs

Argument surface: `<folder>`. Do not add `argument-hint` frontmatter to Codex skills; Codex documents argument surfaces in this body and in `agents/openai.yaml`.

- Resolve `<folder>` against the repository root or current working directory.
- Respond may accept either the exact discussion leaf or a parent folder containing one or more discussion leaves.
- If the resolved path's final segment contains whitespace, warn but do not reject.
- Pre-flight checks must not mutate existing folders. Do not create `plans/` during respond pre-flight.
- If the resolved leaf has `outcome.md`, read and summarize it instead of writing another message.

## Parent Discovery

If the given path itself contains files matching the v2.3 message regex, `outcome.md`, or `outcome_arc<NN>.md`, treat it as a leaf. Otherwise, scan immediate children for pending live discussions matching Codex's responder role:

- A current/latest-arc starter message from Claude exists, such as `arc01_001_claude_to_codex.md` or `arc02_001_claude_to_codex.md`.
- No Codex response exists yet for that arc, such as `arc01_002_codex_to_claude.md` or `arc02_002_codex_to_claude.md`.
- `outcome.md` is not blocking respond.

Zero candidates: poll the parent before surfacing "no pending discussion found." Claude may still be creating the discussion leaf; this gives time for folder creation and first message atomic write. Re-run the immediate-child scan every 30 seconds for up to 5 minutes, then retry once. This zero-candidate polling is read-only: do not create child folders, `plans/`, or heartbeat files while no leaf is selected.

Exactly one candidate: use it and report the resolved leaf path. Multiple candidates: abort and list candidate child folder names.

## Filenames

v2.3 requires arc-prefixed filenames everywhere. Sole message regex: `^arc\d{2}_\d{3}_(claude|codex)_to_(claude|codex)\.md$`.

For a Claude-started arc:

```text
arc01_001_claude_to_codex.md
arc01_002_codex_to_claude.md
arc01_003_claude_to_codex.md
arc01_004_codex_to_claude.md
arc01_005_claude_to_codex.md
arc01_006_codex_to_claude.md
arc01_007_claude_to_codex.md
arc01_008_codex_to_claude.md
arc01_009_claude_to_codex.md
arc01_010_codex_to_claude.md
```

If Codex starts a different discussion, the order reverses, beginning with `arc01_001_codex_to_claude.md`. Continuation arcs use the same pattern, such as `arc02_001_claude_to_codex.md`. Do not add fallback handling for old unprefixed transcripts.

## Message Format

Every message starts with frontmatter on line 1.

Required fields: `protocol`, `arc`, `message_index`, `from`, `to`, `status`, `reply_to`, `created_at_utc`. The arc field is written as `arc: <int>`.

Optional fields: `agent_turn`, `message_cap`, `extension_requested_cap`, `extension_accepted`.

```markdown
---
protocol: interagent-discussion/v1
arc: 1
message_index: 2
from: codex
to: claude
status: continue
reply_to: 1
created_at_utc: YYYY-MM-DDTHH:MM:SSZ
---

# Codex message 002
```

Use `continue | consensus | needs-user` for `status`.

## First Response

Read Claude's message 001 fully before composing message 002. Preserve any `## User-supplied context` section, including inline context and `topic.md` content. Treat fenced blocks as verbatim user intent.

Address the actual claims, add missing repo constraints, risks, tests, or implementation details, and prefer concrete next steps over general agreement.

## Shared Plans

- Plan files live under `plans/`.
- Plan revisions are immutable siblings: `plans/<name>_r001.md`, `plans/<name>_r002.md`, ...
- Latest = highest revision number. Never overwrite an existing revision file.
- Frontmatter includes `revision: <int>`, matching the `_rNNN` suffix.
- `## Plans touched` references the specific new revision file.

## Loop

1. Wait for the next expected Claude file.
2. Read the full latest Claude message.
3. If `outcome.md` exists, stop and summarize it.
4. Re-read files listed in `## Plans touched`.
5. If the latest message is terminal, reply only if needed to create two consecutive terminal messages within the active per-arc cap.
6. Write `continue`, `consensus`, or `needs-user`.
7. After atomic-writing, if outgoing and incoming statuses are the same terminal status, this is the second matching terminal confirmation: write `outcome.md` immediately and stop.

At the active cap, do not write `continue`; use `consensus` if settled, otherwise `needs-user`.

## Extension

Default per-arc cap is 10. A single 10-to-20 extension is allowed per arc.

- Request with `extension_requested_cap: 20` and `## Extension request`.
- Accept with `message_cap: 20` and `extension_accepted: true`.
- After acceptance, every later message in the arc includes `message_cap: 20`.

## Waiting

Poll every 30 seconds for up to 5 minutes, watching both the target message and `outcome.md`; then retry once before surfacing timeout. Never write `outcome.md` on timeout.

```powershell
$target = Join-Path $folder "arc01_001_claude_to_codex.md"
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

Use `.tmp_<guid>.md` temporary file names for messages and plans; readers ignore `.tmp_*`.

```powershell
$tmp = Join-Path $folder ('.tmp_' + [guid]::NewGuid().ToString('N') + '.md')
$final = Join-Path $folder "arc01_002_codex_to_claude.md"
Set-Content -LiteralPath $tmp -Value $content -Encoding utf8
Move-Item -LiteralPath $tmp -Destination $final
```

## Outcome

Write `outcome.md` once when complete. Include all locked fields.

```markdown
---
protocol: interagent-discussion/v1
ended_at_message: 6
ended_at_arc: 1
ended_by: codex
status: consensus
user_facing_agent: claude
implementation_owner: claude
---
```

All seven outcome fields are required. The starter is default user-facing agent and implementation owner unless `## Handover proposal` or `## Implementation responsibility` records another accepted choice. Use `both` for coordinated self-owned work.

## Continuation

Continuation of a Claude-started discussion is started by the Claude-side continue skill. A continued arc uses filenames such as `arc02_001_claude_to_codex.md` and `arc02_002_codex_to_claude.md`; Codex then responds as usual. Prior latest outcomes are archived as `outcome_arc<NN>.md`.

## Implementation Notes

- Respond may accept either the exact discussion leaf or a parent folder.
- Scan immediate children only when resolving a parent.
- Multiple candidates are ambiguous and require the explicit leaf path.
- pre-flight checks must not mutate existing folders before validation.
- Use host-neutral wording for the peer side.
- Use `v2.3_spec_r001.md` as the current implementation reference.
- The second matching terminal writer writes `outcome.md` immediately.

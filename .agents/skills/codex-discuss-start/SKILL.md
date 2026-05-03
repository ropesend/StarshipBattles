---
name: codex-discuss-start
description: Start an inter-agent discussion with Claude Code through a generated child folder, with optional user focus context, shared immutable plan revisions, in-band extension, continuation arcs, and explicit user-facing and implementation ownership. Use when the user asks Codex to initiate a direct Codex/Claude planning, code, architecture, review, or approach discussion.
---

# Codex Discuss Start

Start a v2.3 shared-folder discussion by creating a child discussion leaf under a parent folder, writing Codex message 001, then alternating with Claude Code until `consensus`, `needs-user`, timeout, or the active per-arc message cap.

Reference: `AgentCoordination/Scratchpad/Discussion/20260503T162834Z/plans/v2.3_spec_r001.md`.

## Inputs

Argument surface: `<parent> [--slug <slug>] [context...]`. Do not add `argument-hint` frontmatter to Codex skills; Codex documents argument surfaces in this body and in `agents/openai.yaml`.

- Resolve `<parent>` against the repository root or current working directory.
- Treat the user-supplied path as a parent folder, not the discussion leaf.
- If the resolved parent folder's final segment contains whitespace, warn but do not reject. Suggest a no-space alternative and remind the user to quote paths with spaces.
- Create a child leaf named `YYYYMMDDTHHMMSSZ` by default.
- If `--slug <kebab-case-slug>` is present, create `YYYYMMDDTHHMMSSZ_<slug>`. Validate the slug as lowercase kebab-case. Do not infer a slug from positional context tokens.
- All tokens after the optional slug become inline user context.
- Read `<leaf>/topic.md` if it exists and forward it as additional user context.
- Pre-flight checks must not mutate an existing discussion folder before deciding it is valid to use. Create `<leaf>/plans/` only after the leaf is accepted for a live discussion, or immediately before an actual plan write.
- Abort before writing if the generated leaf already contains protocol files or `outcome.md`.
- Report the full generated leaf path to the user and tell them to invoke the Claude-side discussion skill on that leaf or the parent folder.

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

If Claude starts a different discussion, the order reverses, beginning with `arc01_001_claude_to_codex.md`. Continuation arcs use the same pattern, such as `arc02_001_codex_to_claude.md`. Do not add fallback handling for old unprefixed transcripts.

## Message Format

Every message starts with frontmatter on line 1. Put headings in the body.

Required fields: `protocol`, `arc`, `message_index`, `from`, `to`, `status`, `reply_to`, `created_at_utc`. The arc field is written as `arc: <int>`.

Optional fields: `agent_turn` (informational only), `message_cap`, `extension_requested_cap`, `extension_accepted`.

```markdown
---
protocol: interagent-discussion/v1
arc: 1
message_index: 1
from: codex
to: claude
status: continue
reply_to: null
created_at_utc: YYYY-MM-DDTHH:MM:SSZ
---

# Codex message 001
```

Use `continue | consensus | needs-user` for `status`.

## User-Supplied Context

If inline context or `topic.md` exists, message 001 must include `## User-supplied context`. Forward text verbatim in separate labeled fenced blocks. Do not summarize, paraphrase, or modify those blocks. If the content contains the default fence marker, use a longer fence.

## Shared Plans

- Plan files live under `plans/`.
- Plan revisions are immutable siblings: `plans/<name>_r001.md`, `plans/<name>_r002.md`, ...
- Latest = highest revision number. There is no mutable latest alias.
- Never overwrite an existing revision file. Each edit creates exactly one new revision file.
- Plan frontmatter includes `protocol: interagent-discussion/v1`, `last_edited_by`, `last_edited_at_utc`, and `revision: <int>`. The `revision:` value must match the `_rNNN` suffix.
- `## Plans touched` names the specific new revision file.

## Loop

1. Atomic-write `arc01_001_codex_to_claude.md` with `status: continue`.
2. Wait for the next expected Claude file.
3. Read the full latest Claude message.
4. If `outcome.md` exists, stop and summarize it.
5. Re-read any files listed in `## Plans touched`.
6. If the latest message is terminal, reply only if needed to create two consecutive terminal messages within the active per-arc cap.
7. If continuing, write `continue`; if converged, write `consensus`; if blocked on user input, write `needs-user`.
8. After atomic-writing a reply, if the outgoing status and just-read incoming status are the same terminal status, this is the second matching terminal confirmation: write `outcome.md` immediately, race-safely, and stop.

At the active cap, do not write `continue`; use `consensus` if settled, otherwise `needs-user`, then write `outcome.md`.

## Extension

Default per-arc cap is 10. A single in-band extension to 20 is allowed per arc.

- Request with `extension_requested_cap: 20` and `## Extension request`.
- Accept with `message_cap: 20` and `extension_accepted: true`.
- After acceptance, every later message in the arc includes `message_cap: 20`.
- Do not request a second extension in the same arc.

## Waiting

Poll every 30 seconds for up to 5 minutes, watching both the target message and `outcome.md`; then retry once before surfacing timeout. Never write `outcome.md` on timeout.

```powershell
$target = Join-Path $folder "arc01_002_claude_to_codex.md"
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
$final = Join-Path $folder "arc01_001_codex_to_claude.md"
Set-Content -LiteralPath $tmp -Value $content -Encoding utf8
Move-Item -LiteralPath $tmp -Destination $final
```

## Outcome

Write `outcome.md` once when complete. If it already exists, read it and skip overwriting.

```markdown
---
protocol: interagent-discussion/v1
ended_at_message: 6
ended_at_arc: 1
ended_by: codex
status: consensus
user_facing_agent: codex
implementation_owner: codex
---
```

All seven outcome fields are required. `user_facing_agent` defaults to the starter unless handover is proposed and accepted through a `## Handover proposal` body section. `implementation_owner` defaults to the starter unless the discussion explicitly records another accepted owner; use `both` for coordinated self-owned work.

## Continuation

Continuation arcs are started by `codex-discuss-continue`. For a continued Codex-started discussion, the next arc begins with `arc02_001_codex_to_claude.md`. Prior latest outcomes are archived as `outcome_arc<NN>.md`.

## Implementation Notes

- Use host-neutral wording when referring to the peer side, such as "invoke the Claude-side discussion skill".
- Warn when the final segment contains whitespace, but do not reject.
- pre-flight checks must not mutate existing folders before validation.
- Use `v2.3_spec_r001.md` as the current implementation reference.
- The second matching terminal writer writes `outcome.md` immediately.

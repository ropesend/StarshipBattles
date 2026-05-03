---
name: codex-discuss-respond
description: Respond in an inter-agent discussion with Claude Code through a shared folder, including forwarded focus context, shared plan files, in-band extension, and starter-default user-facing ownership. Use when Codex should wait for Claude's message 001, answer with the shared Codex/Claude protocol, and alternate until consensus, needs-user, timeout, or the active message cap.
---

# Codex Discuss Respond

Join a shared-folder discussion that Claude Code started by waiting for Claude message 001, then alternate using the `interagent-discussion/v1` protocol.

## Inputs

- Require a folder path from the user.
- Resolve relative paths against the repository root or current working directory.
- The folder must exist, or Codex should surface that to the user instead of creating a new discussion.
- If the folder path contains spaces, require the user to wrap it in double quotes. Prefer discussion folder names without spaces.
- Wait for `001_claude_to_codex.md`.
- If `outcome.md` already exists, read it and summarize it to the user instead of writing another message.
- Claude is the default user-facing agent for discussions it starts unless both agents explicitly agree to hand over.

## Protocol

Use these globally ordered message filenames when Claude starts:

```text
001_claude_to_codex.md
002_codex_to_claude.md
003_claude_to_codex.md
004_codex_to_claude.md
005_claude_to_codex.md
006_codex_to_claude.md
007_claude_to_codex.md
008_codex_to_claude.md
009_claude_to_codex.md
010_codex_to_claude.md
```

If Codex starts in a different discussion, the first file is `001_codex_to_claude.md` and the order reverses.

Every message file must start with frontmatter on line 1. Put human-readable headings in the body after the closing frontmatter delimiter.

Required frontmatter fields:

- `protocol`
- `message_index`
- `from`
- `to`
- `status`
- `reply_to`
- `created_at_utc`

Optional frontmatter fields:

- `agent_turn` - informational only; do not validate it for routing.
- `message_cap` - omit while the cap is the default 10; include after extension acceptance.
- `extension_requested_cap`
- `extension_accepted`

Codex response example:

```markdown
---
protocol: interagent-discussion/v1
message_index: 2
from: codex
to: claude
status: continue
reply_to: 1
created_at_utc: YYYY-MM-DDTHH:MM:SSZ
---

# Codex message 002

Message body.
```

Use `continue | consensus | needs-user` for `status`.

## First Response

Read Claude's message 001 fully before composing message 002. In the response:

- Address the actual claims and proposal in Claude's message.
- Read and preserve the meaning of any `## User-supplied context` section, including inline context and forwarded `topic.md` content.
- Add missing repo constraints, risks, tests, or implementation details.
- Prefer concrete decisions and next steps over general agreement.
- Use `continue` unless the discussion is already ready for `consensus` or `needs-user`.

When Claude includes `## User-supplied context`, treat fenced blocks as verbatim user input forwarded by the starter. The blocks may represent inline context, `<folder>/topic.md`, or both. Do not reinterpret missing details as Claude's own preference unless Claude says so.

## Shared Plans

Agents may create and edit shared working plans separately from discussion messages.

- Store plan files under `<folder>/plans/<name>.md`.
- Only the agent currently composing a reply may edit plans. The waiting agent treats `plans/` as read-only.
- Plan writes use temporary files in `<folder>/plans/` whose names begin `.tmp_*`, then atomic rename to the final plan filename. Readers ignore `.tmp_*`.
- Plan frontmatter starts on line 1 and includes `protocol: interagent-discussion/v1`, `last_edited_by`, `last_edited_at_utc`, and `revision: <int>`.
- Increment `revision:` on every edit because Scratchpad discussions are not a git audit trail.
- Optionally include a `## Revision log` body section.
- If Codex creates or edits plans, its next message must include `## Plans touched` listing each path and a one-line reason.
- When Claude lists touched plans, re-read those plan files before composing the next Codex reply.
- Treat plans as working artifacts; `outcome.md` remains authoritative.

## Extension

Default message cap is 10. A discussion may extend once from 10 to 20 messages.

- To request extension, set `extension_requested_cap: 20` and include `## Extension request` with the human-readable reason.
- To accept extension, set `message_cap: 20` and `extension_accepted: true`, and acknowledge in the body.
- To decline extension, omit acceptance fields and explain in the body.
- Acceptance may happen at message 10; if accepted at message 10, that message may use `status: continue` because the cap is now 20.
- After acceptance, every subsequent message must include `message_cap: 20`.
- Do not request or accept any second extension.
- Do not use a separate `*-discuss-extend` skill for v2.

## User-Facing Agent

The starter is the default user-facing agent. For this skill, default `user_facing_agent` is `claude`.

- Either agent may include `## Handover proposal` in a normal message body, explaining why the other agent should summarize or continue with the user.
- The receiving agent accepts or declines in body markdown.
- Never perform a silent handover.
- Record the final choice in `outcome.md` as `user_facing_agent: claude|codex` plus a one-line rationale in the summary.

## Atomic Writes

Write each message to a temporary file in the same folder, then rename it to the final filename. Readers must ignore temporary files.

PowerShell pattern:

```powershell
$tmp = Join-Path $folder "002_codex_to_claude.md.tmp"
$final = Join-Path $folder "002_codex_to_claude.md"
Set-Content -LiteralPath $tmp -Value $content -Encoding utf8
Move-Item -LiteralPath $tmp -Destination $final
```

## Loop

After writing message 002:

1. Wait for the next expected Claude file.
2. Read the full latest Claude message.
3. If `outcome.md` exists, stop and summarize it to the user.
4. Re-read any files listed in `## Plans touched`.
5. If the latest message status is terminal, reply only if needed to create two consecutive terminal messages from different agents and there is room under the active message cap.
6. If discussion should continue, write the next Codex file with `status: continue`.
7. If Codex believes the agents have converged, write `status: consensus`.
8. If user input is required, write `status: needs-user`.

Completion conditions:

- Two consecutive messages from different agents have the same terminal status: `consensus` or `needs-user`.
- The active message cap is reached.
- `outcome.md` already exists.

At the active message cap, do not write `continue`; use `consensus` if settled, otherwise `needs-user`.

## Waiting

Polling mechanics are implementation-specific. A simple loop can wait up to about 5 minutes, write `heartbeat_codex.txt` as a best-effort liveness hint, and then surface a timeout to the user. Do not write `outcome.md` on timeout.

PowerShell wait pattern:

```powershell
$target = Join-Path $folder "001_claude_to_codex.md"
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
if (Test-Path -LiteralPath $outcome) { "OUTCOME" }
elseif (Test-Path -LiteralPath $target) { "READY" }
else { "TIMEOUT" }
```

Treat `heartbeat_claude.txt` as an optional liveness hint only. The protocol must not depend on heartbeat files.

## Outcome

Write `outcome.md` once when the discussion is complete. If it already exists, read and summarize it instead of overwriting it.

```markdown
---
protocol: interagent-discussion/v1
ended_at_message: 6
ended_by: codex
status: consensus
user_facing_agent: claude
---

## Summary

What was discussed, what was agreed, unresolved questions, the handover rationale if any, and the recommended next action.
```

Use a temporary file then rename for `outcome.md` when practical.

## Status Judgment

Use `consensus` when both agents have converged on a concrete plan or answer with no meaningful disagreement.

Use `needs-user` when:

- A factual or preference question only the user can answer blocks progress.
- The remaining trade-off needs user authority over scope, priorities, or risk.
- The agents are repeating disagreement without producing new evidence.
- The active message cap is reached and the issue is not settled.

When reporting back to the user, include the outcome status, the last message read or written, the `user_facing_agent`, and the discussion folder.

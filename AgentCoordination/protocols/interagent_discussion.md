---
protocol: interagent-discussion/v1
protocol_version: 2.5
last_updated_at_utc: 2026-05-04T14:17:28Z
---

# Inter-Agent Discussion Protocol

Durable shared specification for Claude Code, Codex, and OpenCode discussion
skills. Host-specific skills may keep local operational detail, but this file
is the canonical protocol reference.

## Purpose

The discussion system lets multiple agents independently examine an issue,
verify or refute claims, draft plans, and converge on an outcome. It is not a
delegation channel where one agent tells another what to do.

## Protocol Agents

Protocol identities are:

- `claude`
- `codex`
- `opencode`

OpenCode skill names use the `ocode-*` prefix, but filenames and frontmatter
always use `opencode`.

## Shared Folder

Default parent folder:

```text
<repo-root>/AgentCoordination/Scratchpad/Discussion
```

Resolve `<repo-root>` at runtime from the current checkout. Do not hardcode a
machine-specific checkout path.

Discussion leaves are timestamped children of the parent:

```text
YYYYMMDDTHHMMSSZ[_<slug>]/
```

Each leaf may contain message files, `plans/`, heartbeat files, outcome files,
and temporary `.tmp_*` files.

## Argument Surface

Start skills:

```text
[--folder <parent>] [--slug <slug>] [--with <agents>] [context...]
```

Respond skills:

```text
[--folder <folder-or-parent>]
```

Continue skills:

```text
[--folder <folder-or-parent>] [context...]
```

Rules:

- `--folder` is the only folder override.
- If `--folder` is absent, use the default parent.
- Start skills treat positional tokens as user context, not implicit folders.
- Respond and continue skills accept either an exact discussion leaf or a
  parent containing discussion leaves.
- `--with <agents>` selects peer participants for start skills. The invoking
  agent is implicit.
- Pre-flight checks must not mutate folders before validation.
- If the resolved path's final segment contains whitespace, warn but do not
  reject.

## Turn Order

The canonical ring is:

```text
claude -> codex -> opencode -> claude
```

A starter rotates the ring so the starter is at index 0, then filters it to the
selected participant set. For `participants = P` and `n = len(P)`:

- Message author at index `i` is `P[(i - 1) mod n]`.
- Message recipient is `P[i mod n]`.
- The default per-arc cap is `5 * n`.
- One extension may raise the cap to `10 * n`.

The only legal `turn_order` value is `round-robin`.

## Filenames

Message files match:

```text
^arc\d{2}_\d{3}_(claude|codex|opencode)_to_(claude|codex|opencode)\.md$
```

Temporary files match `.tmp_*` and are ignored by readers.

## Message Frontmatter

Every message starts with frontmatter on line 1.

Required fields on every message:

- `protocol`
- `arc`
- `message_index`
- `from`
- `to`
- `status`
- `reply_to`
- `created_at_utc`

Arc starters also require:

- `participants`
- `turn_order`

Optional fields:

- `agent_turn`
- `message_cap`
- `extension_requested_cap`
- `extension_accepted`

Status values:

- `continue`
- `consensus`
- `needs-user`

## Peer Research

This is a peer-to-peer dialogue, not a delegation. Other agents are equals.
Agents must push back, propose alternatives, and agree only where they have
independently verified or clearly marked uncertainty.

Material claims about the codebase, protocol, file contents, prior transcript,
or another agent's behavior must cite evidence such as `file:line`, a specific
transcript message, or an explicit command/result summary. Claims not yet
checked must be labeled `[unverified]`. Consensus is blocked while an
unverified claim is load-bearing for the proposed conclusion, plan, or
implementation assignment. Incidental unverified remarks do not block
consensus unless another participant identifies them as load-bearing.

Starters may suggest research questions, but responders must independently
verify or refute claims rather than simply execute a task list.

## Shared Plans

Plan files live under `plans/` in the discussion leaf.

Rules:

- Plan revisions are immutable siblings:
  `plans/<name>_r001.md`, `plans/<name>_r002.md`, and so on.
- Latest is the highest revision number.
- Never overwrite an existing revision file.
- Plan frontmatter includes `protocol: interagent-discussion/v1`,
  `last_edited_by`, `last_edited_at_utc`, and `revision: <int>`.
- Message bodies reference specific plan revisions under `## Plans touched`.

## Self-Improvement

Protocol self-improvement is in-band.

Use these recognized body sections:

- `## Protocol limitation observed` in a `status: continue` message for
  non-blocking friction or improvement opportunities.
- `## Protocol amendment proposal` in a `status: needs-user` message when the
  limitation blocks progress, risks invalid consensus, or needs user approval.

Blocking amendment proposals create or revise a normal immutable plan under
`<leaf>/plans/` and list the exact revision under `## Plans touched`. The plan
must include observed limitation, evidence, proposed rule change, files to edit,
validation checks, and implementation owner(s).

These headers are documented search conventions and shared-spec requirements.
They are not new frontmatter fields and do not require parser changes.

## Validation

Validate consumed and produced messages:

- Required fields exist and have valid values.
- `from` and `to` are in `{claude, codex, opencode}` and differ.
- `from == participants[(message_index - 1) mod n]`.
- `to == participants[message_index mod n]`.
- Indexes are contiguous and unique within the arc.
- `reply_to` equals the previous `message_index`, or `null` for arc starters.
- Later `participants` and `turn_order` occurrences match the arc starter for
  the active arc.

Do not auto-repair protocol failures. If a safe outgoing target exists, write
`status: needs-user` with `## Validation failure`. If no safe target exists,
abort and surface the diagnostic.

## Waiting

Poll every 30 seconds for up to 5 minutes, watching both the expected incoming
glob and `outcome.md`. Retry once before surfacing timeout. Do not write
`outcome.md` on timeout.

Heartbeat files are liveness hints only.

## Outcome

Write `outcome.md` once when the latest `n` messages all carry the same
terminal status (`consensus` or `needs-user`) or when the active cap forces a
stop.

Outcome frontmatter includes:

```markdown
---
protocol: interagent-discussion/v1
ended_at_message: <int>
ended_at_arc: <int>
ended_by: <claude|codex|opencode>
status: consensus | needs-user
user_facing_agent: <claude|codex|opencode>
implementation_owner: <claude|codex|opencode|multiple>
implementation_owners: [<agent>, <agent>]
continuation_starter: <claude|codex|opencode>
---
```

`implementation_owners` is required iff `implementation_owner: multiple`.
`continuation_starter` is optional and defaults to the original arc-1 starter.

## Continuation

Continuation skills handle ended leaves. They archive the current `outcome.md`
to `outcome_arc<NN>.md` immediately before writing the next arc starter.

Continuation arcs rotate the participant order so `continuation_starter` is at
index 0 for the new arc. The participant set is preserved.

## Out Of Scope

- Auto-routing daemons.
- `cc:` fields.
- Non-`round-robin` turn modes.
- New amendment directories.
- Compatibility shims for old positional-folder invocation.

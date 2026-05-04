---
name: codex-discuss-respond
description: Respond as Codex in a v2.6 inter-agent discussion with Claude Code and/or OpenCode through an exact discussion leaf or discoverable parent folder, using polymorphic round-robin turn detection and mandatory ack sidecars.
---

# Codex Discuss Respond

Join a live v2.6 `interagent-discussion/v1` discussion when the latest turn is
addressed to Codex or when Codex owes a mandatory observer ack. This skill
handles Codex as the second, third, or later participant by reading
`participants` and `message_index`; it is not tied to a specific peer.

Reference: `AgentCoordination/protocols/interagent_discussion.md`.

This is a peer-to-peer dialogue, not a delegation. Other agents are equals.
Push back, propose alternatives, agree only where you have independently
verified or have clearly marked uncertainty.

Evidence rule: Material claims about the codebase, protocol, file contents,
prior transcript, or another agent's behavior must cite `file:line`, a specific
transcript message, or a command/result summary. Label unchecked claims
`[unverified]`. Consensus is blocked while an unverified claim is load-bearing
for the conclusion, plan, or implementation assignment.

## v2.6 Reliability Rules

Canonical shared spec: `AgentCoordination/protocols/interagent_discussion.md`.
Canonical spec frontmatter includes `protocol_version: 2.6`.

- Publish final protocol artifacts through same-directory `.tmp_*` files and a final rename/move. This applies to message files, plan revisions, outcome files, and ack sidecar files. Direct writes to final protocol filenames are invalid; single-writer safety does not imply reader safety.
- Include `complete: true` in newly written message, plan, outcome, and ack files. If a consumed final file is otherwise valid but lacks `complete: true`, warn and proceed; record it under `## Protocol limitation observed` instead of halting.
- Ack sidecars use `ack_arc<NN>_<MMM>_<from>_to_<to>_<acker>.md`. They are excluded from `message_index`, `reply_to`, cap, consensus, and outcome termination.
- Mandatory observer acks: every participant other than the message author must ack each message before the recipient writes the next substantive reply. The recipient writes its own ack before drafting. If this agent is an observer for the latest message and its ack is missing, write only the observer ack sidecar and stop without writing a protocol message.
- If this agent is the recipient and mandatory observer ack files are missing for the incoming message, write this agent's recipient ack, report the missing observer ack(s), and wait instead of drafting the substantive reply.
- During polling, keep heartbeats as liveness hints with `state: polling | reading | drafting | idle`, `waiting_for`, `last_seen_message`, and `updated_at_utc` when practical.

## Inputs

Argument surface: `[--folder <folder-or-parent>]`. Do not add `argument-hint` frontmatter to Codex
skills.

- No positional folder.
- `--folder <folder-or-parent>` is an optional flag-style override. Without it, use `<repo-root>/AgentCoordination/Scratchpad/Discussion`, resolving `<repo-root>` at runtime from the current checkout.
- Accept either an exact discussion leaf or a parent folder containing one or more discussion leaves.
- If the resolved path's final segment contains whitespace, warn but do not reject.
- Pre-flight checks must not mutate existing folders. Do not create `plans/` during respond pre-flight.
- If the resolved leaf has `outcome.md` and no live next arc, read and summarize it instead of writing another message.

## Parent-Folder Discovery

If the given path itself contains protocol messages, `outcome.md`, or
`outcome_arc<NN>.md`, treat it as a leaf. Otherwise, scan immediate child
folders only.

For each child leaf:

1. Skip it if `outcome.md` exists; ended leaves are handled by `codex-discuss-continue`.
2. Find the highest-numbered arc with at least one non-temp message.
3. Find the latest non-temp message in that arc.
4. Parse frontmatter.
5. The leaf is a candidate iff the latest message has `to: codex`, or iff
   Codex is a participant-observer for the latest message and Codex's
   mandatory observer ack sidecar is missing.

Zero candidates: poll the parent before surfacing "no pending discussion
found." Re-run the immediate-child scan every 30 seconds for up to 5 minutes,
then retry once. This polling is read-only.

Exactly one candidate: use it and report the resolved leaf path. Multiple
candidates: abort and list candidate child folder names.

## Protocol Identity

Protocol agents are `claude`, `codex`, and `opencode`. OpenCode skill names use
the `ocode-*` prefix, but filenames and frontmatter use `opencode`.

Message files match:

```text
^arc\d{2}_\d{3}_(claude|codex|opencode)_to_(claude|codex|opencode)\.md$
```

No pair-specific response skills exist. This `respond` skill is polymorphic.

## Participants And Turn Computation

For v2.6, read `participants` and `turn_order` from the arc starter. The only
legal `turn_order` value is `round-robin`.

For v2.3 readback, if `arc01_001_*` lacks `participants`, derive
`participants = [from, to]` from the arc-1 starter and set
`turn_order = round-robin`. This preserves both Claude-started and
Codex-started v2.3 transcripts.

For `participants = P` and `n = len(P)`:

- Message author at index `i` is `P[(i - 1) mod n]`.
- Message recipient is `P[i mod n]`.
- Incoming wait target for Codex is the smallest missing `i_in` where `P[i_in mod n] == codex`.
- Outgoing target after reading `i_in` is `j_out = i_in + 1`; require `P[(j_out - 1) mod n] == codex`.
- `default_cap = 5 * n`; `extended_cap = 10 * n`.

## Message Format

Every message starts with frontmatter on line 1.

Required fields: `protocol`, `arc`, `message_index`, `from`, `to`, `status`,
`reply_to`, `created_at_utc`.

Arc starters additionally require `participants` and `turn_order`, and must
include a body section:

```markdown
## Turn topology

Turn order: claude -> codex -> opencode -> claude
```

Optional fields: `agent_turn`, `message_cap`, `extension_requested_cap`,
`extension_accepted`.

Use `continue | consensus | needs-user` for `status`. Examples include
`status: continue`.

## Validation

Validate before replying:

- Required fields exist and have valid values.
- `from` and `to` are in `{claude, codex, opencode}` and differ.
- `from == participants[(message_index - 1) mod n]`.
- `to == participants[message_index mod n]`.
- Indexes are contiguous and unique within the arc.
- `reply_to` equals the previous `message_index`, or `null` for arc starters.
- Later `participants` and `turn_order` occurrences match arc 1.

Do not auto-repair. If a safe outgoing target exists, write a
`status: needs-user` reply with `## Validation failure`. If no safe target
exists, abort and surface the diagnostic.

## Reply Flow

1. If the latest message in the leaf is neither authored by Codex nor addressed to Codex, and Codex's ack sidecar for that message is missing, write the mandatory observer ack sidecar and stop without writing a protocol message.
2. If waiting on an exact leaf for a substantive turn, compute `i_in` where `P[i_in mod n] == codex` and glob `arc<NN>_<i_in:03d>_*_to_codex.md`.
3. The incoming glob must resolve to exactly one file. Zero means keep waiting; more than one is a fork.
4. Read the full incoming message.
5. If `outcome.md` exists, stop and summarize it.
6. Atomic-write Codex's recipient ack sidecar for the incoming message if it does not already exist.
7. If any mandatory observer ack sidecars for the incoming message are missing, report the missing acker(s) and wait instead of drafting the substantive reply.
8. Re-read files listed in `## Plans touched`.
9. If the incoming message is terminal, reply only if Codex agrees and the reply is needed to complete the latest `n` matching terminal statuses.
10. If continuing, write `continue`; if converged, write `consensus`; if blocked or validation failed, write `needs-user`.
11. Construct the outgoing filename as `arc<NN>_<j_out:03d>_codex_to_<P[j_out mod n]>.md`.
12. Atomic-write the reply.
13. Re-read the latest `n` messages. If all `n` have the same terminal status, write `outcome.md` race-safely and stop.
14. If the reply status is `continue` and the user asked Codex to poll, or the
    task is an active discussion handoff where Codex is expected to keep the
    conversation moving, continue into the waiting loop for the next incoming
    Codex-addressed message instead of ending the turn immediately. Provide only
    brief progress updates while waiting.

At `message_index == active_cap`, write `status: needs-user`, not
`consensus`, then write `outcome.md`. A cap is a forced stop.

## Fork Handling

If a glob for an incoming file addressed to Codex returns more than one match:

- If Codex has a safe outgoing target after the forked index, write
  `status: needs-user` and list the forked filenames in `## Validation failure`.
- If the duplicate is at the index Codex was about to write, abort and surface a
  diagnostic without writing.

## Extension

One extension per arc is allowed:

- Default cap: `5 * n`.
- Extended cap: `10 * n`.
- Request with `extension_requested_cap: <extended_cap>`.
- Accept with `message_cap: <extended_cap>` and `extension_accepted: true`.
- After acceptance, every later message in the arc includes `message_cap: <extended_cap>`.
- Extension state does not carry into continuation arcs.

## Shared Plans

- Plan files live under `plans/`.
- Plan revisions are immutable siblings: `plans/<name>_r001.md`, `plans/<name>_r002.md`, ...
- Latest is the highest revision number. Never overwrite an existing revision file.
- Plan frontmatter includes `protocol: interagent-discussion/v1`,
  `last_edited_by`, `last_edited_at_utc`, and `revision: <int>`.
- `## Plans touched` references the specific new revision file.

## Protocol Self-Improvement

- Use `## Protocol limitation observed` in a `status: continue` message for non-blocking protocol friction.
- Use `## Protocol amendment proposal` in a `status: needs-user` message when a protocol limitation blocks progress, risks invalid consensus, or needs user approval.
- Blocking amendments use normal immutable plan revisions under `plans/`; do not create new frontmatter fields or a separate amendment directory.

## Waiting

Poll every 30 seconds for up to 5 minutes, watching the incoming glob,
mandatory observer-ack duty for Codex, and `outcome.md`; retry once before
surfacing timeout. Never write `outcome.md` on timeout. Heartbeat files such
as `heartbeat_codex.txt` are liveness hints only; include `state`,
`waiting_for`, `last_seen_message`, and `updated_at_utc` when practical.

When polling after Codex has just written a `continue` reply, compute the next
incoming target from the message just written and keep watching the same leaf.
If the next response arrives, read it and repeat the reply flow in the same user
turn when feasible. Stop only on terminal outcome, validation failure, timeout,
or an explicit user request to pause.

## Atomic Writes

Use same-directory `.tmp_<guid>.md` temporary file names for messages,
outcomes, plans, and ack sidecars; readers ignore `.tmp_*`.

```powershell
$tmp = Join-Path $folder ('.tmp_' + [guid]::NewGuid().ToString('N') + '.md')
$final = Join-Path $folder "arc01_003_codex_to_opencode.md"
Set-Content -LiteralPath $tmp -Value $content -Encoding utf8
Move-Item -LiteralPath $tmp -Destination $final
```

## Outcome

Outcome frontmatter includes:

```markdown
---
protocol: interagent-discussion/v1
ended_at_message: <int>
ended_at_arc: <int>
ended_by: codex
status: consensus | needs-user
user_facing_agent: <claude|codex|opencode>
implementation_owner: <claude|codex|opencode|multiple>
implementation_owners: [<agent>, <agent>]
continuation_starter: <claude|codex|opencode>
---
```

`implementation_owners` is required iff `implementation_owner: multiple`.
`continuation_starter` is optional and defaults to the arc-1 starter.

For v2.3 outcome readback only, accept `implementation_owner: both` as
equivalent to `implementation_owner: multiple` with
`implementation_owners == participants`. v2.6 writers must never emit `both`.

## Continuation Boundary

Respond never starts a new arc. If `outcome.md` exists and no live next arc is
present, summarize the outcome and stop. Use `codex-discuss-continue` for
arc-N to arc-(N+1) transitions authorized by `continuation_starter`.

## Implementation Notes

- Manual routing is expected in v2.6; auto-routing daemons are deferred.
- Use host-neutral wording for peer-side invocations.
- Pre-flight checks must not mutate folders before validation.
- Do not create fallback handling for old unprefixed transcripts.

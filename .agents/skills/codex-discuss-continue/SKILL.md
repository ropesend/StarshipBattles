---
name: codex-discuss-continue
description: Continue an ended v2.4 inter-agent discussion when Codex is the authorized continuation starter, archiving the prior outcome and opening the next round-robin arc.
---

# Codex Discuss Continue

Continue an ended `interagent-discussion/v1` discussion by selecting a prior
discussion leaf, verifying Codex is authorized to open the next arc, archiving
the previous `outcome.md`, writing `arc<N+1>_001_codex_to_<next>.md`, and then
entering the normal v2.4 loop.

Reference: `AgentCoordination/Scratchpad/Discussion/20260504T031013Z/plans/v2.4_three_party_spec_r002.md`.

## Inputs

Argument surface: `[--folder <path>] [context...]`. Do not add `argument-hint`
frontmatter to Codex skills.

- No positional folder.
- `--folder <path>` is an optional flag-style override pointing to either a parent folder or an exact discussion leaf.
- Without `--folder`, use the default parent `C:\Dev\Starship Battles\AgentCoordination\Scratchpad\Discussion`.
- All remaining tokens after `--folder <path>`, or all tokens if no `--folder` is present, become inline user context.
- If the resolved path's final segment contains whitespace, warn but do not reject.
- Pre-flight checks must not mutate existing folders until the target is validated.
- Read `<leaf>/topic.md` if it exists. Forward it as additional user context only when Codex writes the continuation arc starter.

## Leaf Resolution

If `--folder <path>` points to an exact leaf containing protocol messages,
`outcome.md`, or `outcome_arc<NN>.md`, validate that leaf. Otherwise resolve a
parent folder and scan immediate children.

For each candidate leaf with `outcome.md`:

- Treat it as continuable by Codex iff `continuation_starter == codex`, or
  `continuation_starter` is absent and Codex is the original arc-1 starter.
- The original starter is read from `arc01_001_*` frontmatter `from`.
- If no leaf qualifies, abort and tell the user which continuation starter is authorized when that can be determined.
- If exactly one leaf qualifies, use it.
- If multiple leaves qualify, abort and list candidate leaf names.

If the selected leaf has no `outcome.md`, it is live or inconsistent. Use
`codex-discuss-respond` for live arcs addressed to Codex.

## Protocol Identity

Protocol agents are `claude`, `codex`, and `opencode`. OpenCode skill names use
the `ocode-*` prefix, but filenames and frontmatter use `opencode`.

Message files match:

```text
^arc\d{2}_\d{3}_(claude|codex|opencode)_to_(claude|codex|opencode)\.md$
```

## Participants And Turn Computation

Read `participants` and `turn_order` from arc 1. Continuation arcs inherit both
unchanged. The only legal `turn_order` value in v2.4 is `round-robin`.

For v2.3 readback, if `arc01_001_*` lacks `participants`, derive
`participants = [from, to]` from the arc-1 starter and set
`turn_order = round-robin`.

For `participants = P` and `n = len(P)`:

- Message author at index `i` is `P[(i - 1) mod n]`.
- Message recipient is `P[i mod n]`.
- A continuation arc starter written by Codex is allowed only if `P[0] == codex` or the current discussion's inherited `participants` already puts Codex at the proper starter position for the next arc.
- The continuation starter message uses `message_index: 1`, `from: codex`, and `to: P[1]`.
- `default_cap = 5 * n`; `extended_cap = 10 * n`.

Do not reorder `participants` during continuation. If Codex is authorized by
`continuation_starter` but the inherited participant order would not make Codex
the author of `message_index: 1`, abort and surface the inconsistency; do not
invent a new order.

## Start-Of-New-Arc Flow

Use this flow only when Codex is the authorized continuation starter.

1. Verify `outcome.md` exists.
2. Verify outcome frontmatter contains `ended_at_arc`, `ended_at_message`, `status`, `user_facing_agent`, and `implementation_owner`.
3. Verify `implementation_owners` is present iff `implementation_owner: multiple`.
4. Accept legacy v2.3 `implementation_owner: both` only for v2.3 readback; treat it as `implementation_owner: multiple` with `implementation_owners == participants`.
5. Determine the just-ended arc from `ended_at_arc`.
6. Determine the next arc number as just-ended arc + 1.
7. Compose the next arc starter with inherited `participants`, `turn_order`, `## Turn topology`, and any user-supplied context.
8. Atomically move current `outcome.md` to `outcome_arc<NN>.md`, where `NN` is the just-ended arc number.
9. Atomic-write `arc<N+1>_001_codex_to_<P[1]>.md`.
10. Enter the normal response loop.

During the live continuation arc, no latest `outcome.md` exists. At completion,
write a fresh `outcome.md`.

This is the arc-N to arc-(N+1) transition point. Responding within an already
live arc remains the job of `codex-discuss-respond`.

## Arc Starter Message

Every continuation starter includes `participants`, `turn_order`, and a body
`## Turn topology` section.

```markdown
---
protocol: interagent-discussion/v1
arc: 2
message_index: 1
from: codex
to: opencode
status: continue
reply_to: null
created_at_utc: YYYY-MM-DDTHH:MM:SSZ
participants: [codex, opencode, claude]
turn_order: round-robin
---

# Codex continuation message 001

## Turn topology

Turn order: codex -> opencode -> claude -> codex
```

## User-Supplied Context

When Codex writes the next arc starter and inline context or `topic.md` exists,
include `## User-supplied context`. Forward text verbatim in separate labeled
fenced blocks. Do not summarize, paraphrase, or modify those blocks.

## Validation

Validate all consumed and produced protocol files:

- Required fields exist and have valid values.
- `from` and `to` are in `{claude, codex, opencode}` and differ.
- `from == participants[(message_index - 1) mod n]`.
- `to == participants[message_index mod n]`.
- Indexes are contiguous and unique within each arc.
- `reply_to` equals the previous `message_index`, or `null` for arc starters.
- Arc 1 `participants` and `turn_order` remain stable.

Do not auto-repair protocol failures. If no safe write target exists, abort and
surface the diagnostic.

## Loop And Extension

After writing the new arc starter, use the normal v2.4 loop:

- Incoming wait target for Codex: smallest missing `i_in` where `P[i_in mod n] == codex`; glob `arc<NN>_<i_in:03d>_*_to_codex.md`.
- Outgoing target after reading `i_in`: `j_out = i_in + 1`; require `P[(j_out - 1) mod n] == codex`; write `arc<NN>_<j_out:03d>_codex_to_<P[j_out mod n]>.md`.
- The incoming glob must resolve to exactly one file. Zero means wait; more than one is a fork.
- Re-read plans named in `## Plans touched`.
- After writing, re-read the latest `n` messages. If all have the same terminal status, write `outcome.md`.

One extension per arc is allowed:

- Default cap: `5 * n`.
- Extended cap: `10 * n`.
- Request with `extension_requested_cap: <extended_cap>`.
- Accept with `message_cap: <extended_cap>` and `extension_accepted: true`.
- Extension state does not carry from one arc to the next.

At `message_index == active_cap`, write `status: needs-user`, not `consensus`,
then write `outcome.md`.

## Waiting

Poll every 30 seconds for up to 5 minutes, watching both the incoming glob and
`outcome.md`; retry once before surfacing timeout. Never write `outcome.md` on
timeout. Heartbeat files are liveness hints only.

## Atomic Writes

Use `.tmp_<guid>.md` temporary file names for messages, outcomes, and plans;
readers ignore `.tmp_*`.

```powershell
$tmp = Join-Path $folder ('.tmp_' + [guid]::NewGuid().ToString('N') + '.md')
$final = Join-Path $folder "arc02_001_codex_to_opencode.md"
Set-Content -LiteralPath $tmp -Value $content -Encoding utf8
Move-Item -LiteralPath $tmp -Destination $final
```

For the outcome archive, move `outcome.md` to `outcome_arc<NN>.md` only after
all validation passes and immediately before writing the next arc starter.

## Outcome

The latest arc writes a fresh `outcome.md` with:

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
`continuation_starter` is optional and defaults to the original arc-1 starter.
If present, it must be in `participants`.

## Implementation Notes

- Continue handles only authorized arc archival and next-arc startup.
- Respond handles live in-arc replies.
- Manual routing is expected in v2.4; auto-routing daemons are deferred.
- Do not create fallback handling for old unprefixed transcripts.

---
name: codex-discuss-start
description: Start an inter-agent discussion with Claude Code and/or OpenCode through a generated discussion leaf, using the v2.4 round-robin shared-folder protocol with immutable plans, continuation arcs, and explicit ownership.
---

# Codex Discuss Start

Start a v2.4 `interagent-discussion/v1` shared-folder discussion by creating a
child discussion leaf, writing Codex message 001, and then following the
round-robin loop until `consensus`, `needs-user`, timeout, or the per-arc cap.

Reference: `AgentCoordination/Scratchpad/Discussion/20260504T031013Z/plans/v2.4_three_party_spec_r002.md`.

## Inputs

Argument surface: `<parent> [--participants <agents>] [--slug <slug>] [context...]`. Do not add `argument-hint` frontmatter to Codex skills.

- Resolve `<parent>` against the repository root or current working directory.
- Treat the user-supplied path as a parent folder, not the discussion leaf.
- If the resolved parent folder's final segment contains whitespace, warn but do not reject. Remind the user to quote paths with spaces.
- Create a child leaf named `YYYYMMDDTHHMMSSZ` by default.
- If `--slug <kebab-case-slug>` is present, create `YYYYMMDDTHHMMSSZ_<slug>`. Validate the slug as lowercase kebab-case. Do not infer a slug from positional context tokens.
- `--participants <agents>` chooses the participant set. Accepted values are `claude`, `opencode`, `claude,opencode`, `codex,claude`, `codex,opencode`, `codex,claude,opencode`, and `all`.
- If `--participants` is absent, default to the current two-party behavior: `[codex, claude]`.
- Codex is always the starter and must be in the participant set. Abort if fewer than two or more than three protocol agents would participate.
- All remaining tokens after flags become inline user context.
- Read `<leaf>/topic.md` if it exists and forward it as additional user context.
- Pre-flight checks must not mutate an existing discussion folder before deciding it is valid to use. Create `<leaf>/plans/` only after the leaf is accepted for a live discussion, or immediately before an actual plan write.
- Abort before writing if the generated leaf already contains protocol files or `outcome.md`.
- Report the full generated leaf path and the next participant in the turn order.

## Participant Order

Protocol agents are `claude`, `codex`, and `opencode`. OpenCode skill names use
the `ocode-*` prefix, but the protocol identity is `opencode`.

The fixed canonical ring is `[claude, codex, opencode]`. For a Codex-started
discussion, rotate the ring to `[codex, opencode, claude]`, then filter it to the
chosen participant set:

- Codex + Claude: `[codex, claude]`
- Codex + OpenCode: `[codex, opencode]`
- Three-party: `[codex, opencode, claude]`

The user may override the order only through explicit context. If they do,
validate that the order contains Codex at index 0 and only known participant
names.

For `participants = P` and `n = len(P)`:

- Message author at index `i` is `P[(i - 1) mod n]`.
- Message recipient is `P[i mod n]`.
- `default_cap = 5 * n`; `extended_cap = 10 * n`.

## Filenames

v2.4 requires arc-prefixed filenames everywhere. Message files match:

```text
^arc\d{2}_\d{3}_(claude|codex|opencode)_to_(claude|codex|opencode)\.md$
```

For a Codex-started three-party arc:

```text
arc01_001_codex_to_opencode.md
arc01_002_opencode_to_claude.md
arc01_003_claude_to_codex.md
arc01_004_codex_to_opencode.md
```

For a Codex + Claude arc:

```text
arc01_001_codex_to_claude.md
arc01_002_claude_to_codex.md
```

Never add pair-specific skill variants. The same Codex skills handle Claude and
OpenCode by reading `participants`.

## Arc Starter Message

Every message starts with frontmatter on line 1. The first message of every arc
must include `participants` and `turn_order`.

```markdown
---
protocol: interagent-discussion/v1
arc: 1
message_index: 1
from: codex
to: <P[1]>
status: continue
reply_to: null
created_at_utc: YYYY-MM-DDTHH:MM:SSZ
participants: [codex, opencode, claude]
turn_order: round-robin
---

# Codex message 001

## Turn topology

Turn order: codex -> opencode -> claude -> codex
```

Use `continue | consensus | needs-user` for `status`. Later messages may repeat
`participants` and `turn_order`, but must not change them.

Optional fields on any message: `agent_turn`, `message_cap`,
`extension_requested_cap`, and `extension_accepted`.

## User-Supplied Context

If inline context or `topic.md` exists, message 001 must include
`## User-supplied context`. Forward text verbatim in separate labeled fenced
blocks. Do not summarize, paraphrase, or modify those blocks. If the content
contains the default fence marker, use a longer fence.

## Shared Plans

- Plan files live under `plans/`.
- Plan revisions are immutable siblings: `plans/<name>_r001.md`, `plans/<name>_r002.md`, ...
- Latest is the highest revision number. There is no mutable latest alias.
- Never overwrite an existing revision file. Each edit creates exactly one new revision file.
- Plan frontmatter includes `protocol: interagent-discussion/v1`, `last_edited_by`, `last_edited_at_utc`, and `revision: <int>`.
- `## Plans touched` names the specific new revision file.

## Validation

Validate every message consumed or produced:

- Required fields exist and `from != to`.
- `from` and `to` are in `{claude, codex, opencode}`.
- `from == participants[(message_index - 1) mod n]`.
- `to == participants[message_index mod n]`.
- Indexes are contiguous, unique, and `reply_to` points to the prior message.
- Arc 1 `participants` and `turn_order` remain stable across continuation arcs.

Do not auto-repair protocol failures. If a safe outgoing target exists, write
`status: needs-user` with `## Validation failure`. If no safe write target
exists, abort and surface the diagnostic.

## Loop

1. Atomic-write `arc01_001_codex_to_<P[1]>.md` with `status: continue`.
2. Manual routing is expected in v2.4. Tell the user which peer-side skill should be invoked next.
3. If remaining in the loop, wait for the incoming message addressed to Codex.
4. Incoming wait target: smallest missing `i_in` where `P[i_in mod n] == codex`; glob `arc<NN>_<i_in:03d>_*_to_codex.md`.
5. The incoming glob must resolve to exactly one file. Zero means keep waiting; more than one is a fork.
6. Read the full latest incoming message. If `outcome.md` exists, stop and summarize it.
7. Re-read any files listed in `## Plans touched`.
8. Compose the outgoing message with `j_out = i_in + 1`; require `P[(j_out - 1) mod n] == codex`; write `arc<NN>_<j_out:03d>_codex_to_<P[j_out mod n]>.md`.
9. After writing, re-read the latest `n` messages. If all `n` carry the same terminal status, write `outcome.md` race-safely and stop.

At `message_index == active_cap`, write the cap message with
`status: needs-user` and then write `outcome.md`. A cap is not proof of
agreement. Extension state is per arc and does not carry into continuation
arcs.

## Extension

One extension per arc is allowed:

- Default cap: `5 * n`.
- Extended cap: `10 * n`.
- Request with `extension_requested_cap: <extended_cap>`.
- Accept with `message_cap: <extended_cap>` and `extension_accepted: true`.
- After acceptance, every later message in the arc includes `message_cap: <extended_cap>`.

## Waiting

Poll every 30 seconds for up to 5 minutes, watching both the incoming glob and
`outcome.md`; retry once before surfacing timeout. Never write `outcome.md` on
timeout. Heartbeat files such as `heartbeat_codex.txt` are liveness hints only.

## Atomic Writes

Use `.tmp_<guid>.md` temporary file names for messages, outcomes, and plans;
readers ignore `.tmp_*`.

```powershell
$tmp = Join-Path $folder ('.tmp_' + [guid]::NewGuid().ToString('N') + '.md')
$final = Join-Path $folder "arc01_001_codex_to_opencode.md"
Set-Content -LiteralPath $tmp -Value $content -Encoding utf8
Move-Item -LiteralPath $tmp -Destination $final
```

## Outcome

Write `outcome.md` once when complete. If it already exists, read it and skip
overwriting.

```markdown
---
protocol: interagent-discussion/v1
ended_at_message: <int>
ended_at_arc: <int>
ended_by: codex
status: consensus
user_facing_agent: codex
implementation_owner: multiple
implementation_owners: [codex, opencode]
continuation_starter: codex
---
```

`implementation_owner` is one of `claude | codex | opencode | multiple`.
`implementation_owners` is required iff `implementation_owner: multiple`;
otherwise it must be absent. `continuation_starter` is optional and defaults to
the arc-1 starter.

For v2.3 outcome readback only, accept `implementation_owner: both` as
equivalent to `implementation_owner: multiple` with
`implementation_owners == participants`. v2.4 writers must never emit `both`.

## Continuation

Continuation arcs are started by `codex-discuss-continue` only when Codex is the
authorized continuation starter. Prior latest outcomes are archived as
`outcome_arc<NN>.md`.

## Implementation Notes

- Use host-neutral wording such as "invoke the OpenCode-side discussion skill" or "invoke the Claude-side discussion skill".
- Pre-flight checks must not mutate existing folders before validation.
- Read v2.3 transcripts by deriving `participants = [from, to]` from `arc01_001_*`; do not rewrite them.
- Auto-routing daemons, `cc:`, and non-`round-robin` turn modes are out of scope for v2.4.

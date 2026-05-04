---
name: ocode-discuss-start
description: Open a v2.5 inter-agent discussion with Claude and/or Codex. Defaults to the shared discussion parent unless `--folder` is supplied; creates a timestamped child leaf, writes message arc01_001 with optional inline focus context, declares the participant set + canonical-ring turn order, and alternates per the round-robin formula until consensus, needs-user, the per-arc cap, or a pre-existing outcome.md. Defaults to a 2-party OpenCode+Claude discussion; pass `--with claude,codex` for 3-party or `--with codex` for OpenCode+Codex.
argument-hint: [--folder <parent>] [--slug <slug>] [--with <agents>] [context...]
---

# Inter-Agent Discussion — OpenCode Starts (v2.5)

You are opening a multi-turn discussion with one or two other agents.
Participants are drawn from `{claude, codex, opencode}` per the canonical
ring. The parent folder defaults to
`<repo_root>/AgentCoordination/Scratchpad/Discussion`; `--folder` overrides it.
You create a timestamped child sub-folder. The user invokes the matching
`*-discuss-respond` skill on each other participant; those skills find the leaf
via parent scan.

Reference: `AgentCoordination/protocols/interagent_discussion.md`.

This is a peer-to-peer dialogue, not a delegation. Other agents are your
equals. Push back, propose alternatives, agree only where you have independently
verified or have clearly marked uncertainty.

Evidence rule: Material claims about the codebase, protocol, file contents,
prior transcript, or another agent's behavior must cite `file:line`, a specific
transcript message, or a command/result summary. Label unchecked claims
`[unverified]`. Consensus is blocked while an unverified claim is load-bearing
for the conclusion, plan, or implementation assignment.

## Protocol — interagent-discussion/v1 (v2.5 spec)

| Field | Value |
|-------|-------|
| Parent | optional `--folder <parent>`; default `<repo_root>/AgentCoordination/Scratchpad/Discussion` |
| Discussion leaf | child of parent: `YYYYMMDDTHHMMSSZ[_<slug>]/` |
| Slug flag | optional `--slug <kebab-case>` |
| Participants flag | optional `--with <comma-separated agents>`; default `claude` |
| Inline context | tokens after the optional flags, joined and forwarded verbatim |
| `topic.md` | optional `<leaf>/topic.md`, read at start, forwarded verbatim |
| Filename pattern | `arc<NN>_<MMM>_<from>_to_<to>.md`, where from/to ∈ `{claude,codex,opencode}` |
| Turn formula | `from = P[(i-1) mod n]`, `to = P[i mod n]` where `P = participants`, `n = len(P)`, `i = message_index` |
| Default per-arc cap | `5 × n` messages (one in-band extension to `10 × n` per arc) |
| Termination | Last `n` messages all uniform terminal status, OR cap reached, OR pre-existing `outcome.md` |
| Atomicity | write to `.tmp_<random>.md` then `mv` to final name |
| Shared plans | `<leaf>/plans/<name>_r<NNN>.md` — versioned siblings, never overwrite |

## Step 1 — Parse arguments

Use `<repo_root>/AgentCoordination/Scratchpad/Discussion` as the parent unless
`--folder <parent>` is supplied. Resolve relative folder overrides against the
repository root (discovered at runtime; do not hardcode a checkout path). Accept
any combination of `--folder <parent>`, `--slug <kebab-case>`, and
`--with <comma-list>` flags before the inline context.

- `--slug` value: lowercase kebab-case (`a-z`, `0-9`, `-`). Reject otherwise.
- `--with` value: comma-separated agents from `{claude, codex}` (opencode
  is implicit). Default if absent: `claude` (2-party OpenCode+Claude).
- Everything after the last recognized flag is **inline context**. Positional
  tokens are never treated as folder paths.

Build participants per spec §1.1: canonical ring `[claude, codex, opencode]`
rotated so the starter (`opencode`) is at index 0, then filtered to
participants present. Examples:

| `--with` | Participants                 |
|----------|------------------------------|
| (none)   | `[opencode, claude]`         |
| `codex`  | `[opencode, codex]`          |
| `claude,codex` or `codex,claude` | `[opencode, claude, codex]` |

(For 3-party the canonical filter from `[claude, codex, opencode]` rotated
to opencode-at-0 is `[opencode, claude, codex]`.)

Bash skeleton:

```bash
PARENT="<repo_root>/AgentCoordination/Scratchpad/Discussion"
SLUG=""
WITH_LIST="claude"
while [ $# -gt 0 ]; do
  case "$1" in
    --folder) PARENT="$2"; shift 2 ;;
    --slug) SLUG="$2"; shift 2 ;;
    --with) WITH_LIST="$2"; shift 2 ;;
    *) break ;;
  esac
done
case "$PARENT" in
  /*|[a-zA-Z]:[/\\]*) ;;  # absolute
  *) PARENT="<repo_root>/$PARENT" ;;
esac
INLINE_CONTEXT="$*"
```

## Step 2 — Whitespace warning on the parent leaf

If the parent folder's leaf name contains whitespace, emit a warning (do
not abort). The generated child folder uses a timestamp and never has
spaces.

## Step 3 — Pre-flight: refuse to clobber a leaf-shaped path

If the parent folder already contains files matching the v2.5 message
regex `^arc[0-9]{2}_[0-9]{3}_(claude|codex|opencode)_to_(claude|codex|opencode)\.md$`,
or `outcome.md`, or `outcome_arc[0-9]{2}\.md`, abort: it's a leaf, not a parent.

**Pre-flight before any mutation.**

## Step 4 — Generate child leaf and folder structure

Compute `TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)`. The child leaf is
`$TIMESTAMP` (no slug) or `${TIMESTAMP}_${SLUG}` (with slug). Create:

- the parent folder if missing
- the child leaf folder
- `<leaf>/plans/`

Default parent: `<repo_root>/AgentCoordination/Scratchpad/Discussion/`
per AGENTS.md scratchpad rule.

## Step 5 — Read optional `<leaf>/topic.md`

If the user pre-seeded `<leaf>/topic.md`, read it verbatim for inclusion
in message 1 below. (Unusual for a generated child leaf; preserved for
explicit-leaf invocations.)

## Step 6 — Compose and write `arc01_001_opencode_to_<P[1]>.md`

The recipient of message 1 is `participants[1 mod n]` = `participants[1]`.

Body must include, in order:

1. **`## User-supplied context`** — only if inline context or `topic.md` is
   non-empty. Each in a separate fenced block, **verbatim**. Do NOT
   summarize, paraphrase, or modify these blocks. Synthesis below them is OK.
   **Fence-collision rule:** if verbatim content contains `~~~`, use a longer
   fence (`~~~~` etc.).

2. **`## Turn topology`** — required for every arc-starter message
   (`message_index: 1`). One-line arrow chain:
   ```markdown
   ## Turn topology

   Turn order: opencode -> claude -> codex -> opencode
   ```

3. **Cold-start context** — other agents have no shared memory with you. Convey:
   - The user's underlying request or problem.
   - The current state (what's been proposed, tried, decided).
   - Relevant files/constraints/conventions other agents need to know.
   - What you want from each other agent.

### Message file format (v2.5)

Frontmatter is the **first thing in the file** (line 1 = `---`). Use the
actual current UTC time.

```markdown
---
protocol: interagent-discussion/v1
arc: 1
message_index: 1
from: opencode
to: <next agent in ring>
status: continue
reply_to: null
created_at_utc: <ISO 8601 UTC, e.g. 2026-05-04T03:10:13Z>
participants: [opencode, <p1>, <p2>]   # length 2 or 3, opencode at index 0
turn_order: round-robin
---

# OpenCode → <recipient>, message arc01-001

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

Turn order: opencode -> <p1> -> ... -> opencode

## [your cold-start brief]

...
```

### Frontmatter schema

**Required, every message:** `protocol`, `arc`, `message_index`, `from`, `to`,
`status`, `reply_to`, `created_at_utc`.

**Required, arc-starter messages only:** `participants`, `turn_order`.

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

### Atomic write helper (bash)

```bash
write_message_atomic() {
  # write_message_atomic <folder> <final_name> <<<"$content"
  local folder="$1" final="$2"
  local tmp="${folder}/.tmp_$(od -An -N16 -tx1 /dev/urandom | tr -d ' \n').md"
  cat > "$tmp"
  mv "$tmp" "${folder}/${final}"
}

write_plan_revision() {
  # write_plan_revision <folder> <plan_basename> <revision_int> <<<"$content"
  local folder="$1" base="$2" rev="$3"
  local plansdir="${folder}/plans"
  mkdir -p "$plansdir"
  printf -v final "%s_r%03d.md" "$base" "$rev"
  if [ -e "${plansdir}/${final}" ]; then
    echo "ABORT: plan revision '${final}' already exists. Bump to revision $((rev+1))." >&2
    return 1
  fi
  local tmp="${plansdir}/.tmp_$(od -An -N16 -tx1 /dev/urandom | tr -d ' \n').md"
  cat > "$tmp"
  mv "$tmp" "${plansdir}/${final}"
}
```

Use the OpenCode `write` tool when convenient — it writes the file in one
shot, which is also atomic enough for this protocol's contention level
(single-writer-per-index). The `.tmp_` + `mv` pattern is required only when
multiple writers may race; for in-skill writing the `write` tool is fine.

Final filename for arc 1 message 1: `arc01_001_opencode_to_<P[1]>.md`.

## Step 7 — Discussion loop

The active per-arc cap starts at `5 × n` (n=2 → 10; n=3 → 15). Extension
takes it to `10 × n`.

1. **Wait for the next message addressed to you.** Compute `i_in` = smallest
   unused message index where `participants[i_in mod n] == 'opencode'`.
   Glob: `arc<NN>_<i_in:03d>_*_to_opencode.md`. Use the polling helper.
   The glob MUST resolve to **exactly one** file. Zero → keep waiting.
   >1 → fork handling.

2. **Branch on what appeared:**
   - `outcome.md` appeared → done; read, summarize, exit.
   - Target message appeared → read and validate per validation rules
     below. Surface mismatch as `needs-user`.

3. **Apply termination rules** (re-read last `n` messages):
   - **Unanimous terminal**: last `n` messages all carry the same terminal
     status (uniform `consensus` xor `needs-user`) → write `outcome.md`,
     summarize, exit.
   - **Cap reached**: incoming `message_index == active_cap` → cap reached.
     Write `outcome.md`, summarize, exit.

4. **Re-read any plans listed in `## Plans touched`** before composing your
   reply.

5. **Handle extension request**, if any. Active cap starts at `5×n`. Accept
   by setting `message_cap: <10×n>` and `extension_accepted: true`. After
   acceptance, every subsequent message must include `message_cap: <10×n>`.

6. **Handle handover proposal**, if any.

7. **Compose your reply.** Status: `continue` / `consensus` / `needs-user`.
   At cap: must use `needs-user` (per spec §5.3 — a cap is forced stop,
   not proof of agreement).

8. **Edit shared plans this turn (if appropriate).** Plan files at
   `<leaf>/plans/<name>_r<NNN>.md`. Never overwrite. Plan frontmatter:
   ```yaml
   ---
   protocol: interagent-discussion/v1
   last_edited_by: opencode
   last_edited_at_utc: <UTC ISO 8601>
   revision: <int matching filename suffix>
   ---
   ```
   If you edit, include `## Plans touched` listing each new revision file.

### Protocol self-improvement

- Use `## Protocol limitation observed` in a `status: continue` message for non-blocking protocol friction.
- Use `## Protocol amendment proposal` in a `status: needs-user` message when a protocol limitation blocks progress, risks invalid consensus, or needs user approval.
- Blocking amendments use normal immutable plan revisions under `plans/`; do not create new frontmatter fields or a separate amendment directory.

9. **Compute outgoing write target**: `j_out = i_in + 1`. Verify
   `participants[(j_out-1) mod n] == 'opencode'`. Recipient is
   `participants[j_out mod n]`. Filename:
   `arc<NN>_<j_out:03d>_opencode_to_<recipient>.md`. Atomic-write.

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

### Fork handling

If the incoming-glob in Step 7.1 returns >1 file at the same index:

- If a safe outgoing write target exists at `j_out`, write it with
  `status: needs-user` and a `## Validation failure` body listing the
  forked filenames.
- Otherwise abort with a diagnostic. Do not pick.

### Polling helper (bash, 30s sleep, 5-min wait)

```bash
poll_for_message() {
  local folder="$1" arc="$2" idx="$3"
  printf -v pattern "arc%02d_%03d_*_to_opencode.md" "$arc" "$idx"
  local outcome="${folder}/outcome.md"
  local start_s=$(date +%s) elapsed
  while :; do
    matches=("${folder}/"$pattern)
    real_matches=()
    for m in "${matches[@]}"; do [ -e "$m" ] && real_matches+=("$m"); done
    if [ -e "$outcome" ]; then echo "OUTCOME"; return 0; fi
    if [ "${#real_matches[@]}" -eq 1 ]; then
      echo "READY"; basename "${real_matches[0]}"; return 0
    elif [ "${#real_matches[@]}" -gt 1 ]; then
      echo "FORK"; for m in "${real_matches[@]}"; do basename "$m"; done; return 0
    fi
    elapsed=$(( $(date +%s) - start_s ))
    [ "$elapsed" -ge 300 ] && { echo "TIMEOUT"; return 0; }
    echo "waiting... ${elapsed}s elapsed"
    date -u +"%Y-%m-%dT%H:%M:%SZ" > "${folder}/heartbeat_opencode.txt"
    sleep 30
  done
}
```

On TIMEOUT, retry once (~10 min total). If still no file, surface to user:

> Other agents haven't responded after ~10 minutes. Invoke the matching
> `*-discuss-respond` skill on each remaining participant, or tell me to
> keep waiting.

**Do not write `outcome.md` on timeout.**

## Step 8 — Write outcome.md (exactly once, race-safe)

Before writing:

1. Re-read the last `n` messages to confirm termination still holds.
2. Re-check `outcome.md` does not exist.
3. Atomic-write via temp+rename (or use the `write` tool — single writer).
4. If the rename target already exists, read it and stop. Do not retry.

Format:

```markdown
---
protocol: interagent-discussion/v1
ended_at_message: <int>
ended_at_arc: 1
ended_by: opencode
status: consensus               # consensus | needs-user
user_facing_agent: opencode     # claude | codex | opencode
implementation_owner: opencode  # claude | codex | opencode | multiple
implementation_owners: [<agent>, <agent>]   # required iff owner == multiple, ≥2 entries, ⊆ participants
continuation_starter: opencode  # optional; default = original starter
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
(opencode); set explicitly only to authorize a different agent to open arc N+1.

## Step 9 — Report to the user

You (`ocode-discuss-start`) are the starter, so by default you are the
user-facing agent. Tell the user:

- Generated leaf path (under the parent they supplied).
- Number of messages exchanged (and whether an extension was used).
- Terminal status, `user_facing_agent`, `implementation_owner`.
- 1–2 sentence summary.
- If `needs-user`: what the user must decide.
- File listing.

## Notes & gotchas

- **Default `--with claude`**: 2-party OpenCode+Claude.
- **Canonical ring rotation**: `[claude, codex, opencode]` rotated so opencode
  is at index 0 (always, since opencode is the starter here): for 3-party →
  `[opencode, claude, codex]`; for OpenCode+Codex 2-party → `[opencode, codex]`.
- **Frontmatter on line 1.** No prefix above `---`.
- **Heartbeat files** are best-effort liveness hints, not load-bearing.
- **Temp files** matching `.tmp_*` are ignored by readers.
- **Plans never overwrite.** Each edit is a new revision file.
- **Cross-host invocation wording.** "Invoke the Claude-side
  `claude-discuss-respond` skill" / "Invoke the Codex-side
  `codex-discuss-respond` skill" rather than slash-prefixed examples.
- **`opencode.json` `permission.skill`** already allows `ocode-*`. No
  permission change needed for this skill family.
- **v2.3 readback** (for old Claude+Codex transcripts without `participants`):
  derive `participants = [arc01_001.from, arc01_001.to]`,
  `turn_order = round-robin`. Legacy `implementation_owner: both` accepted
  for v2.3 outcome readback only; v2.5 writers never emit it.

## Step — Log Skill Usage

```bash
python Tools/agent_coordination/log_skill_usage.py --agent ocode --skill ocode-discuss-start
```

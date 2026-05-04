---
name: ocode-discuss-respond
description: Join a v2.4 inter-agent discussion that Claude or Codex opened. The argument may be either the exact discussion leaf or a parent folder containing one or more leaves; if a parent is given, this skill scans for exactly one pending discussion where the latest message is addressed to OpenCode. The skill is polymorphic across 2-party and 3-party discussions and does not care which agent opened the discussion — it just takes the next turn whenever it is OpenCode's turn. Use after the user has invoked the matching `*-discuss-start` skill on the originating agent.
argument-hint: <folder-or-parent>
---

# Inter-Agent Discussion — OpenCode Responds (v2.4)

You are joining a multi-turn discussion. The user may pass the exact
discussion leaf OR a parent folder containing one or more discussion leaves;
this skill resolves the leaf via parent-folder discovery (latest-state
based, NOT pair-specific).

This is a peer-to-peer dialogue, not a delegation. Other agents are your
equals. Push back, propose alternatives, agree where you actually agree.

## Protocol — interagent-discussion/v1 (v2.4 spec)

| Field | Value |
|-------|-------|
| Argument | first positional arg — leaf or parent; resolution algorithm below |
| Filename pattern | `arc<NN>_<MMM>_<from>_to_<to>.md`, where from/to ∈ `{claude,codex,opencode}` |
| Turn formula | `from = P[(i-1) mod n]`, `to = P[i mod n]` where `P = participants`, `n = len(P)` |
| Default per-arc cap | `5 × n` messages (one in-band extension to `10 × n` per arc) |
| Termination | Last `n` messages all uniform terminal status, OR cap reached, OR pre-existing `outcome.md` |
| Atomicity | `.tmp_<random>.md` then `mv` to final name |
| Shared plans | `<leaf>/plans/<name>_r<NNN>.md` — versioned siblings, never overwrite |

Responder does not take inline context — context arrives forwarded in the
arc-starter message.

## Step 1 — Resolve the folder

Take the first positional argument. Resolve relative to the repo root
(`c:\Dev\Starship Battles`) if not absolute. Abort if the path does not
exist.

## Step 2 — Whitespace warning (informational)

If the resolved path's leaf contains whitespace, emit a warning. Do not
abort.

## Step 3 — Latest-state parent-folder discovery

The argument may be the leaf or a parent.

**Resolution algorithm:**

1. **Try as leaf.** If the path directly contains v2.4 protocol files
   matching `^arc[0-9]{2}_[0-9]{3}_(claude|codex|opencode)_to_(claude|codex|opencode)\.md$`,
   `^outcome\.md$`, or `^outcome_arc[0-9]{2}\.md$`, treat it as a leaf and
   skip to Step 4.

2. **Otherwise scan children.** For each immediate sub-folder of the path
   that is a leaf, skip those with `outcome.md` present (they are
   handled by `ocode-discuss-continue`, not `respond`). For each
   remaining leaf:
   1. Find the highest-numbered arc with at least one message file.
   2. Find the highest-indexed message in that arc (excluding `.tmp_*`).
   3. Parse its frontmatter.
   4. The leaf is a candidate iff `to == opencode`.

3. Apply the count rule:
   - **Zero candidates** → keep polling for ~5 minutes (the starter may
     still be writing message 1). After timeout, retry once. If still
     nothing: "no pending discussion found in `<parent>`. Make sure the
     starter's `*-discuss-start` skill has been invoked."
   - **Exactly one candidate** → use it; log the resolved leaf for the user.
   - **Multiple candidates** → abort with an ambiguity message listing
     candidate child folder names. User must re-invoke with an explicit leaf.

Implementation hint: use `glob` to enumerate child folders, `read` to parse
the latest message's frontmatter (the YAML block between the first two
`---` lines). Don't run heavy regex in `bash` if the OpenCode tool surface
makes structured reading easier.

## Step 4 — Pre-flight non-mutation

The responder never creates `<leaf>/plans/`. Plan writers create it
immediately before their first plan write.

If `outcome.md` exists at the leaf, the latest arc is concluded — `respond`
is the wrong skill. Read the outcome, surface to the user, and exit:

> EXISTING_OUTCOME — latest arc is concluded.
> If you want to continue this discussion with new context, use
> `ocode-discuss-continue` (when authorized by `continuation_starter` or
> as the original arc-1 starter).

## Step 5 — Determine active arc and parse `participants`

The active arc is the highest arc-prefix found in the leaf's filenames.
The `participants` and `turn_order` come from the arc-1 starter message.

1. Find `arc01_001_*.md`. Read its frontmatter.
2. If `participants:` is present, parse the YAML list (e.g. `[opencode, claude, codex]`).
3. **v2.3 readback**: if `participants:` is missing, derive
   `participants = [arc01_001.from, arc01_001.to]` (from the filename
   regex `^arc01_001_(\w+)_to_(\w+)\.md$`). Treat `turn_order` as
   `round-robin`.
4. Verify `opencode` is in `participants`. If not, abort.

## Step 6 — Compute incoming wait target

`i_in` = smallest unused index in the active arc where
`participants[i_in mod n] == 'opencode'`.

```bash
# Example bash:
# Given arr "${PARTICIPANTS[@]}", N="${#PARTICIPANTS[@]}", existing indexes EXISTING_IDX
i=1
while :; do
  if [[ ! " ${EXISTING_IDX[*]} " == *" $i "* ]]; then
    if [ "${PARTICIPANTS[$((i % N))]}" = "opencode" ]; then I_IN=$i; break; fi
  fi
  i=$((i+1))
  [ "$i" -gt 100 ] && { echo "ABORT: could not find next opencode turn"; exit 1; }
done
```

## Step 7 — Wait for the incoming message (poll)

Glob: `arc<activeArc:02d>_<I_IN:03d>_*_to_opencode.md`. Use the polling
helper. The glob MUST resolve to **exactly one** file.

Behavior:
- 1 match → READY, proceed.
- 0 matches at deadline → TIMEOUT, retry once.
- >1 matches → FORK; write your scheduled message at `j_out = i_in + 1`
  with `status: needs-user` and a `## Validation failure` body listing
  the forked filenames. If no safe write target exists, abort.

```bash
poll_for_message() {
  local folder="$1" arc="$2" idx="$3"
  printf -v pattern "arc%02d_%03d_*_to_opencode.md" "$arc" "$idx"
  local outcome="${folder}/outcome.md"
  local start_s=$(date +%s) elapsed
  while :; do
    matches=("${folder}/"$pattern)
    real=()
    for m in "${matches[@]}"; do [ -e "$m" ] && real+=("$m"); done
    [ -e "$outcome" ] && { echo "OUTCOME"; return 0; }
    [ "${#real[@]}" -eq 1 ] && { echo "READY"; basename "${real[0]}"; return 0; }
    [ "${#real[@]}" -gt 1 ] && { echo "FORK"; for m in "${real[@]}"; do basename "$m"; done; return 0; }
    elapsed=$(( $(date +%s) - start_s ))
    [ "$elapsed" -ge 300 ] && { echo "TIMEOUT"; return 0; }
    echo "waiting... ${elapsed}s elapsed"
    date -u +"%Y-%m-%dT%H:%M:%SZ" > "${folder}/heartbeat_opencode.txt"
    sleep 30
  done
}
```

## Step 8 — Read incoming and validate

Required validation per v2.4:

1. **Schema**: required fields present; `from != to`; `from`/`to` ∈
   `{claude,codex,opencode}`.
2. **Turn alignment**: `from == participants[(message_index-1) mod n]` AND
   `to == participants[message_index mod n]` AND `to == opencode`.
3. **Index continuity**: `reply_to == message_index - 1` for `i > 1`.

If validation fails, write your scheduled message with `status: needs-user`
and a `## Validation failure` body.

If the incoming message has `## User-supplied context`, the verbatim fenced
blocks are authoritative user intent. Do not paraphrase.

## Step 9 — Apply termination rules (re-read last `n` messages)

- **Unanimous terminal**: last `n` messages all carry the same terminal
  status (uniform `consensus` xor `needs-user`) → write `outcome.md`,
  summarize, exit.
- **Cap reached**: if the just-read message has `message_index == active_cap`,
  it should be the cap message (`status: needs-user`). Write `outcome.md`,
  summarize, exit.

If neither terminates, proceed to Step 10.

## Step 10 — Discussion loop

Repeat until terminal:

1. **Re-read any plans listed in `## Plans touched`** before composing
   your reply.

2. **Handle extension request**, if any. Active cap starts at `5×n`. Accept
   by setting `message_cap: <10×n>` and `extension_accepted: true`. After
   acceptance, every subsequent message must include `message_cap: <10×n>`.

3. **Handle handover proposal**, if any.

4. **Compose your reply.** Status: `continue` / `consensus` / `needs-user`.
   At cap: must use `needs-user` (per spec §5.3).

5. **Edit shared plans this turn (if appropriate).** Plan files at
   `<leaf>/plans/<name>_r<NNN>.md`. Never overwrite.

6. **Compute outgoing write target.** `j_out = i_in + 1`. Verify
   `participants[(j_out-1) mod n] == 'opencode'`. Recipient is
   `participants[j_out mod n]`. Filename:
   `arc<activeArc:02d>_<j_out:03d>_opencode_to_<recipient>.md`. Atomic-write.

7. **Writer-detects-match.** After writing, re-read last `n` messages.
   If unanimous terminal, write `outcome.md` race-safely (Step 11) and
   exit. Do NOT loop.

8. **Wait for next incoming**. New `i_in` = next unused index where
   `participants[i_in mod n] == 'opencode'`. Use the polling helper.

9. Loop.

### Message file format

```markdown
---
protocol: interagent-discussion/v1
arc: <N>
message_index: <M>
from: opencode
to: <P[M mod n]>
status: continue
reply_to: <M-1>
created_at_utc: <ISO 8601 UTC>
---

# OpenCode → <recipient>, message arc<NN>-<MMM>

[reply / counterpoint / agreement]

## Plans touched

(Only if you created a new plan revision file this turn.)
```

### Atomic write helpers

```bash
write_message_atomic() {
  local folder="$1" final="$2"
  local tmp="${folder}/.tmp_$(od -An -N16 -tx1 /dev/urandom | tr -d ' \n').md"
  cat > "$tmp"
  mv "$tmp" "${folder}/${final}"
}
```

Or use the OpenCode `write` tool directly — it writes atomically enough
for single-writer-per-index contention.

## Step 11 — Write outcome.md (exactly once, race-safe)

Before writing:

1. Re-read the last `n` messages to confirm termination still holds.
2. Re-check `outcome.md` does not exist.
3. Atomic-write via temp+rename (or `write` tool).
4. If the rename target already exists, read it and stop. Do not retry.

```markdown
---
protocol: interagent-discussion/v1
ended_at_message: <int>
ended_at_arc: <N>
ended_by: opencode
status: consensus               # consensus | needs-user
user_facing_agent: <agent>      # default = original arc-1 starter
implementation_owner: <agent>   # default = original starter
implementation_owners: [<a>, <a>]   # required iff owner == multiple
continuation_starter: <agent>       # optional; default = original starter
---

## Summary
## Handover (only if applicable)
## Implementation responsibility (only if non-default)
```

## Step 12 — Report to the user (only if you are the user-facing agent)

Default: `user_facing_agent` = original arc-1 starter (whoever wrote
`arc01_001_*.md`). If that's not OpenCode, deliver a one-line acknowledgement
(discussion closed, leaf path) and stop — the starter delivers the substantive
summary.

If a handover to OpenCode was accepted, deliver the full report (folder,
message count, terminal status, summary, file listing).

## Notes & gotchas

- **Latest-state discovery, not pair-specific.** Any leaf where the latest
  message is `to: opencode` is a candidate.
- **Polymorphic across topology.** Same skill handles 2-party and 3-party,
  and works regardless of which agent opened the discussion.
- **Frontmatter on line 1.**
- **Heartbeat files** are best-effort liveness hints.
- **Temp files** matching `.tmp_*` are ignored by readers.
- **Plans never overwrite.** Each edit is a new revision file.
- **Don't paraphrase** verbatim user-supplied context.
- **Fence-collision rule:** longer fence if content contains `~~~`.
- **Default user-facing agent is the original arc-1 starter.**
- **`opencode.json` `permission.skill`** already allows `ocode-*`. No
  permission change needed.
- **v2.3 readback.** When `participants` is missing from `arc01_001`,
  derive it from `[arc01_001.from, arc01_001.to]`. Legacy
  `implementation_owner: both` accepted for v2.3 outcome readback only.

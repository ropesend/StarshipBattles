---
name: ocode-discuss-respond
description: Join a v2.6 inter-agent discussion that Claude or Codex opened. Defaults to the shared discussion parent unless `--folder` is supplied; if a parent is given, this skill scans for exactly one pending discussion where the latest message is addressed to OpenCode or awaits OpenCode's mandatory observer ack. The skill is polymorphic across 2-party and 3-party discussions and does not care which agent opened the discussion.
argument-hint: [--folder <folder-or-parent>]
---

# Inter-Agent Discussion â€” OpenCode Responds (v2.6)

You are joining a multi-turn discussion. The folder defaults to
`<repo_root>/AgentCoordination/Scratchpad/Discussion`; `--folder` may point to
the exact discussion leaf OR a parent folder containing one or more discussion
leaves. This skill resolves the leaf via parent-folder discovery (latest-state
based, NOT pair-specific).

Reference: `AgentCoordination/protocols/interagent_discussion.md`.

This is a peer-to-peer dialogue, not a delegation. Other agents are your
equals. Push back, propose alternatives, agree only where you have independently
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

## Protocol â€” interagent-discussion/v1 (v2.6 spec)

| Field | Value |
|-------|-------|
| Argument | optional `--folder <folder-or-parent>`; defaults to `<repo_root>/AgentCoordination/Scratchpad/Discussion` |
| Filename pattern | `arc<NN>_<MMM>_<from>_to_<to>.md`, where from/to âˆˆ `{claude,codex,opencode}` |
| Turn formula | `from = P[(i-1) mod n]`, `to = P[i mod n]` where `P = participants`, `n = len(P)` |
| Default per-arc cap | `5 Ã— n` messages (one in-band extension to `10 Ã— n` per arc) |
| Termination | Last `n` messages all uniform terminal status, OR cap reached, OR pre-existing `outcome.md` |
| Atomicity | `.tmp_<random>.md` then `mv` to final name |
| Shared plans | `<leaf>/plans/<name>_r<NNN>.md` â€” versioned siblings, never overwrite |

Responder does not take inline context â€” context arrives forwarded in the
arc-starter message.

## Step 1 â€” Resolve the folder

Use `<repo_root>/AgentCoordination/Scratchpad/Discussion` unless
`--folder <folder-or-parent>` is supplied. Resolve relative overrides against
the repository root (discovered at runtime; do not hardcode a checkout path).
Abort if the path does not exist. Positional folders are not part of v2.6.

## Step 2 â€” Whitespace warning (informational)

If the resolved path's leaf contains whitespace, emit a warning. Do not
abort.

## Step 3 â€” Latest-state parent-folder discovery

The argument may be the leaf or a parent.

**Resolution algorithm:**

1. **Try as leaf.** If the path directly contains v2.6 protocol files
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
   4. The leaf is a candidate iff `to == opencode`, or iff OpenCode is a participant-observer for the latest message and OpenCode's mandatory observer ack sidecar is missing.

3. Apply the count rule:
   - **Zero candidates** â†’ keep polling for ~5 minutes (the starter may
     still be writing message 1). After timeout, retry once. If still
     nothing: "no pending discussion found in `<parent>`. Make sure the
     starter's `*-discuss-start` skill has been invoked."
   - **Exactly one candidate** â†’ use it; log the resolved leaf for the user.
   - **Multiple candidates** â†’ abort with an ambiguity message listing
     candidate child folder names. User must re-invoke with an explicit leaf.

Implementation hint: use `glob` to enumerate child folders, `read` to parse
the latest message's frontmatter (the YAML block between the first two
`---` lines). Don't run heavy regex in `bash` if the OpenCode tool surface
makes structured reading easier.

## Step 4 â€” Pre-flight non-mutation

The responder never creates `<leaf>/plans/`. Plan writers create it
immediately before their first plan write.

If `outcome.md` exists at the leaf, the latest arc is concluded â€” `respond`
is the wrong skill. Read the outcome, surface to the user, and exit:

> EXISTING_OUTCOME â€” latest arc is concluded.
> If you want to continue this discussion with new context, use
> `ocode-discuss-continue` (when authorized by `continuation_starter` or
> as the original arc-1 starter).

## Step 5 â€” Determine active arc and parse `participants`

The active arc is the highest arc-prefix found in the leaf's filenames.
The `participants` and `turn_order` come from the arc-1 starter message.

1. Find `arc01_001_*.md`. Read its frontmatter.
2. If `participants:` is present, parse the YAML list (e.g. `[opencode, claude, codex]`).
3. **v2.3 readback**: if `participants:` is missing, derive
   `participants = [arc01_001.from, arc01_001.to]` (from the filename
   regex `^arc01_001_(\w+)_to_(\w+)\.md$`). Treat `turn_order` as
   `round-robin`.
4. Verify `opencode` is in `participants`. If not, abort.

## Step 6 â€” Compute incoming wait target

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

## Step 7 â€” Wait for the incoming message (poll)

Glob: `arc<activeArc:02d>_<I_IN:03d>_*_to_opencode.md`. Use the polling
helper. The glob MUST resolve to **exactly one** file.

Behavior:
- 1 match â†’ READY, proceed.
- 0 matches at deadline â†’ TIMEOUT, retry once.
- >1 matches â†’ FORK; write your scheduled message at `j_out = i_in + 1`
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

## Step 8 â€” Read incoming and validate

If the latest message in the leaf is neither authored by OpenCode nor
addressed to OpenCode, and OpenCode's ack sidecar is missing, write the
mandatory observer ack sidecar and stop without writing a protocol message.

Required validation per v2.6:

1. **Schema**: required fields present; `from != to`; `from`/`to` âˆˆ
   `{claude,codex,opencode}`.
2. **Turn alignment**: `from == participants[(message_index-1) mod n]` AND
   `to == participants[message_index mod n]` AND `to == opencode`.
3. **Index continuity**: `reply_to == message_index - 1` for `i > 1`.

If validation fails, write your scheduled message with `status: needs-user`
and a `## Validation failure` body.

After reading an OpenCode-addressed incoming message, atomic-write OpenCode's
recipient ack sidecar if it does not already exist. If any mandatory observer
ack sidecars for that incoming message are missing, report the missing
acker(s) and wait instead of drafting the substantive reply.

If the incoming message has `## User-supplied context`, the verbatim fenced
blocks are authoritative user intent. Do not paraphrase.

## Step 9 â€” Apply termination rules (re-read last `n` messages)

- **Unanimous terminal**: last `n` messages all carry the same terminal
  status (uniform `consensus` xor `needs-user`) â†’ write `outcome.md`,
  summarize, exit.
- **Cap reached**: if the just-read message has `message_index == active_cap`,
  it should be the cap message (`status: needs-user`). Write `outcome.md`,
  summarize, exit.

If neither terminates, proceed to Step 10.

## Step 10 â€” Discussion loop

Repeat until terminal:

1. **Re-read any plans listed in `## Plans touched`** before composing
   your reply.

2. **Handle extension request**, if any. Active cap starts at `5Ã—n`. Accept
   by setting `message_cap: <10Ã—n>` and `extension_accepted: true`. After
   acceptance, every subsequent message must include `message_cap: <10Ã—n>`.

3. **Handle handover proposal**, if any.

4. **Compose your reply only after all mandatory ack sidecars exist for the incoming message.** Status: `continue` / `consensus` / `needs-user`.
   At cap: must use `needs-user` (per spec Â§5.3).

5. **Edit shared plans this turn (if appropriate).** Plan files at
   `<leaf>/plans/<name>_r<NNN>.md`. Never overwrite.

### Protocol self-improvement

- Use `## Protocol limitation observed` in a `status: continue` message for non-blocking protocol friction.
- Use `## Protocol amendment proposal` in a `status: needs-user` message when a protocol limitation blocks progress, risks invalid consensus, or needs user approval.
- Blocking amendments use normal immutable plan revisions under `plans/`; do not create new frontmatter fields or a separate amendment directory.

6. **Compute outgoing write target.** `j_out = i_in + 1`. Verify
   `participants[(j_out-1) mod n] == 'opencode'`. Recipient is
   `participants[j_out mod n]`. Filename:
   `arc<activeArc:02d>_<j_out:03d>_opencode_to_<recipient>.md`. Atomic-write.

7. **Writer-detects-match.** After writing, re-read last `n` messages.
   If unanimous terminal, write `outcome.md` race-safely (Step 11) and
   exit. Do NOT loop.

   **HARD GATE â€” DO NOT SKIP:** If the last message's status is `continue`
   (not `consensus`, not `needs-user`), you MUST proceed to Step 8. Do NOT
   report to the user. Do NOT exit the skill. You are mid-conversation.
   The only path past this gate is polling for the next incoming message.

8. **Wait for next incoming**. New `i_in` = next unused index where
   `participants[i_in mod n] == 'opencode'`. Use the polling helper.

   **Polling rule:** Use `glob` to check for the expected incoming file
   (e.g. `arc01_005_*_to_opencode.md`). If it exists, proceed to Step 8
   (read and validate). If it does not exist, write a heartbeat and
   **retry the glob every 15-30 seconds** until the file appears or a
   5-minute timeout elapses. On timeout, retry once. On second timeout,
   surface "no response from {sender} within polling window" to the user.
   Do not write `outcome.md` on timeout.

9. Read the incoming message, validate per Step 8, then **loop back to
   Step 10.1** (re-read plans, compose reply). Do NOT skip to Step 12.

10. **This loop (Steps 10.1â€“10.9) runs until terminal.** You are a
    participant in an ongoing conversation. Every non-terminal message you
    write must be followed by polling for the next incoming. Only when the
    loop terminates (unanimous terminal + outcome.md written) should you
    proceed to Step 12.

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

# OpenCode â†’ <recipient>, message arc<NN>-<MMM>

[reply / counterpoint / agreement]

## Plans touched

(Only if you created a new plan revision file this turn.)
```

### Atomic write helpers

```bash
write_message_atomic() {
  local folder="$1" final="$2"
  local tmp
  tmp=$(mktemp "${folder}/.tmp_XXXXXX.md")
  cat > "$tmp"
  mv "$tmp" "${folder}/${final}"
}
```

On PowerShell-only hosts, use a GUID temp name with `Set-Content`, then
`Move-Item` to the final filename. Always write the temp file first and rename
it into place; do not write directly to the final protocol filename.

## Step 11 â€” Write outcome.md (exactly once, race-safe)

Before writing:

1. Re-read the last `n` messages to confirm termination still holds.
2. Re-check `outcome.md` does not exist.
3. Atomic-write via same-directory temp+rename.
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

## Step 12 â€” Report to the user (ONLY after termination or when user-facing agent)

**PRE-GATE:** This step runs ONLY if:
- An `outcome.md` was just written (Step 11), OR
- The polling loop (Step 10) timed out and you are surfacing that timeout, OR
- You are the original arc-1 starter AND a terminal condition exists.

If none of these conditions are met, DO NOT proceed to this step. You are
still mid-conversation â€” go back to polling (Step 10.8).

Default: `user_facing_agent` = original arc-1 starter (whoever wrote
`arc01_001_*.md`). If that's not OpenCode, deliver a one-line acknowledgement
(discussion closed, leaf path) and stop â€” the starter delivers the substantive
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

## Step â€” Log Skill Usage

```bash
python Tools/agent_coordination/log_skill_usage.py --agent ocode --skill ocode-discuss-respond
```

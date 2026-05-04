---
name: ocode-discuss-continue
description: Continue a previously concluded v2.4 inter-agent discussion with new user-supplied focus context. No-args by default — resolves to the most-recent v2.4 discussion leaf under the default parent. Role-aware self-dispatch: if OpenCode is the authorized continuation starter (per `outcome.md.continuation_starter`, defaulting to the original arc-1 starter), archives the latest outcome and opens arc N+1; otherwise waits for the authorized agent to write the new arc's first message and joins the respond loop. Use after a discussion has reached a terminal `outcome.md`. Per-arc cap is `5 × len(participants)` messages (extendable once to `10 × n`).
argument-hint: "[--folder <path>] [context...]"
---

# Inter-Agent Discussion — OpenCode Continues (v2.4)

You are re-opening a previously concluded discussion with new user input.
The skill is **no-args by default**: it resolves to the most-recent
v2.4 discussion leaf under
`c:\Dev\Starship Battles\AgentCoordination\Scratchpad\Discussion\`. The
optional `--folder <path>` flag overrides the target (path may be a parent
or an exact leaf).

The skill is **role-aware** and self-dispatches based on
`outcome.md.continuation_starter` (defaulting to the original arc-1 starter):

- **OpenCode is the continuation starter** → start arc N+1 (archive outcome,
  write `arc(N+1)_001_opencode_to_<P[1]>.md`, enter discussion loop).
- **Another agent is the continuation starter** → wait for the authorized
  agent to write `arc(N+1)_001_*_to_*.md`, then enter the respond loop.

The user's mental model: invoke `ocode-discuss-continue` on the OpenCode
side and the matching skill on the other agent(s) with the same new
context; the right thing happens regardless of who started.

## Protocol — interagent-discussion/v1 (v2.4 spec)

| Field | Value |
|-------|-------|
| Argument surface | `[--folder <path>] [context...]` |
| Default parent | `c:\Dev\Starship Battles\AgentCoordination\Scratchpad\Discussion\` |
| Filename pattern | `arc<NN>_<MMM>_<from>_to_<to>.md` |
| Per-arc cap | `5 × n` messages (one in-band extension to `10 × n` per arc) |
| Outcome archiving | move latest `outcome.md` → `outcome_arc<NN>.md` before writing new arc |

## Step 1 — Parse arguments

```bash
DEFAULT_PARENT="c:/Dev/Starship Battles/AgentCoordination/Scratchpad/Discussion"
FOLDER_ARG=""
if [ "$1" = "--folder" ]; then
  FOLDER_ARG="$2"
  shift 2
fi
INLINE_CONTEXT="$*"
```

## Step 2 — Resolve the discussion leaf

If `--folder <path>` was given: the path may be a parent or an exact leaf.
If no `--folder`: scan the default parent for the most-recent leaf.

**Leaf detection:** a folder is a leaf if it directly contains files
matching `^arc[0-9]{2}_[0-9]{3}_(claude|codex|opencode)_to_(claude|codex|opencode)\.md$`,
`^outcome\.md$`, or `^outcome_arc[0-9]{2}\.md$`.

**Most-recent leaf scoring:** among immediate children that are leaves,
score each by the most recent modification time of its **protocol files
only** (messages, `outcome.md`, `outcome_arc<NN>.md`). Tiebreak by child
folder name descending.

Folders without any arc-prefixed message file are **not** leaves
(pre-v2.3 transcripts are not continuation targets).

## Step 3 — Read original starter and `participants` from arc 1

Find `arc01_001_*.md`. Parse:

- `originalStarter` from filename: `arc01_001_(\w+)_to_\w+.md`.
- `participants` from frontmatter (if present); fallback v2.3 readback:
  `[arc01_001.from, arc01_001.to]`.
- `n = len(participants)`.

## Step 4 — Determine next arc number and read continuation_starter

Compute `maxArc` = highest arc-prefix in any message filename. Set
`newArc = maxArc + 1`, `priorArc = maxArc`.

Read `continuation_starter` from `outcome.md` frontmatter. If the field
is absent, default to `originalStarter`.

## Step 5 — Apply the dispatch table

| Caller role | `outcome.md` exists? | Next-arc starter file exists? | Action |
|---|---|---|---|
| starter (opencode is continuation_starter) | yes | n/a | **Mode A**: archive outcome, write `arc<newArc>_001`, enter loop |
| starter | no | n/a | ABORT: latest arc still live |
| responder (someone else is continuation_starter) | yes | no | **Mode B-wait**: wait for starter to archive + write; validate; enter respond loop |
| responder | yes | yes | **Mode B-join**: validate `arc<newArc>_001`, enter respond loop |
| responder | no | yes | **Mode B-join**: validate `arc<newArc>_001`, enter respond loop |
| responder | no | no | ABORT: live/inconsistent state |

## Step 6 — Mode A: opencode is the continuation starter

### A.1 — Compose new arc message in memory

Per the compose-before-archive ordering: compose first, archive second,
write third. If composition fails, the previous outcome stays in place.

Body must include:

1. **`## User-supplied context`** — verbatim fenced block of the inline
   context (longer fence if content has `~~~`). Do not paraphrase.
2. **`## Turn topology`** — required for arc starters.
3. **Prior arc summary** — read `outcome.md` (about to be archived) and
   summarize. Reference relevant prior plan revisions by versioned filename.
4. **What's new in this arc** — the user's new direction.

### A.2 — Compute rotated participants

Continuation arc rotates `participants` so that `continuation_starter`
(opencode) is at index 0 for that arc. The set is preserved; the order
rotates. Recipient of message 1 is the new `participants[1]`.

```bash
# rotate so opencode is at index 0
oc_idx=-1
for i in "${!PARTICIPANTS[@]}"; do
  [ "${PARTICIPANTS[$i]}" = "opencode" ] && oc_idx=$i
done
ROTATED=()
for ((j=0; j<N; j++)); do
  ROTATED+=("${PARTICIPANTS[$(( (oc_idx + j) % N ))]}")
done
RECIPIENT="${ROTATED[1]}"
```

### A.3 — Archive previous outcome.md

```bash
ARCHIVE=$(printf "outcome_arc%02d.md" "$priorArc")
if [ -e "${FOLDER}/${ARCHIVE}" ]; then
  echo "ABORT: archive target ${ARCHIVE} already exists. State inconsistent." >&2
  exit 1
fi
mv "${FOLDER}/outcome.md" "${FOLDER}/${ARCHIVE}"
```

### A.4 — Atomic-write the new arc's message 001

```bash
NEW_NAME=$(printf "arc%02d_001_opencode_to_%s.md" "$newArc" "$RECIPIENT")
# write_message_atomic "$FOLDER" "$NEW_NAME" <<<"$messageBody"
```

The frontmatter MUST include `participants: [<rotated>]` and
`turn_order: round-robin`.

### A.5 — Enter the standard discussion loop

Identical to `ocode-discuss-respond`'s loop (Step 10), with `activeArc =
newArc` and the rotated `PARTICIPANTS`.

At terminal: write fresh `outcome.md` (latest is always at `outcome.md`;
archives are historical).

## Step 7 — Mode B: opencode is responder for this continuation

### B.0 — Locally-typed context: warn-and-ignore

If the user provided inline context but opencode is NOT the continuation
starter, warn that the starter's forwarded context is canonical and the
locally-typed context will not be propagated.

### B.1 — Wait for next-arc starter message (if Mode B-wait)

If `mode == B-wait`: poll for
`arc<newArc:02d>_001_<continuationStarter>_to_*.md`. Use the polling helper
(30s sleep, 5-min wait, retry once).

### B.2 — Read and validate the new arc's message 001

Required: `protocol == interagent-discussion/v1`, `arc == newArc`,
`message_index == 1`, `from == continuationStarter`,
`participants` and `turn_order` present (rotated ring with
`continuationStarter` at index 0).

If validation fails, write your scheduled message with `status: needs-user`
and a `## Validation failure` body. If no safe write target exists, abort.

### B.3 — Compute opencode's incoming wait target on the new arc

Use the rotated `participants` from arc N+1's frontmatter. Apply Step 6
of `ocode-discuss-respond`'s logic to compute `i_in` and enter the
respond loop.

## Step 8 — Atomic write helpers

```bash
write_message_atomic() {
  local folder="$1" final="$2"
  local tmp="${folder}/.tmp_$(od -An -N16 -tx1 /dev/urandom | tr -d ' \n').md"
  cat > "$tmp"
  mv "$tmp" "${folder}/${final}"
}

write_plan_revision() {
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

Or use the OpenCode `write` tool directly.

## Step 9 — Polling helper

Same shape as start/respond: 30s sleep, 5-min wait, watches both target
glob and `outcome.md` (during the loop). Retry once on TIMEOUT, no
`outcome.md` on timeout.

## Step 10 — Write outcome.md at end of arc

When the arc terminates, write fresh `outcome.md` per the spec §7 schema.

```markdown
---
protocol: interagent-discussion/v1
ended_at_message: <int>
ended_at_arc: <newArc>
ended_by: <claude|codex|opencode>
status: consensus              # consensus | needs-user
user_facing_agent: <agent>     # default = original arc-1 starter
implementation_owner: <agent>  # default = original starter
implementation_owners: [<a>, <a>]   # required iff owner == multiple
continuation_starter: <agent>       # optional; default = original starter
---

## Summary
## Handover (only if applicable)
## Implementation responsibility (only if non-default)
```

`user_facing_agent` defaults to the **original arc-1 starter** —
continuation does not change that identity unless a handover is accepted.
Same for `implementation_owner`.

## Step 11 — Report to the user

You only deliver the substantive user-facing report if you are the
user-facing agent (default = original arc-1 starter):

- **If OpenCode is the original arc-1 starter**: deliver the full report.
- **Otherwise**: minimal acknowledgement (one line: discussion closed,
  leaf path) unless a handover to OpenCode was accepted.

## Notes & gotchas

- **Compose before archive before write.** Don't archive the previous
  outcome until the new message body is fully composed.
- **Self-dispatch via `continuation_starter`.** Don't run Mode A logic if
  `continuation_starter` (or default = original starter) is not OpenCode.
- **Continuation arc rotates participants.** The set is preserved, but
  the order rotates so `continuation_starter` is at index 0 for the new
  arc. The new arc's `arc<NN>_001` frontmatter records the rotated
  `participants` explicitly.
- **Per-arc reset.** `message_index` resets to 1 each arc. Cap state
  does NOT carry from arc N to arc N+1.
- **Latest outcome is always `outcome.md`.** Historical outcomes are
  `outcome_arc<NN>.md`. Don't write `outcome_arc<newArc>.md` yourself —
  reserved for archive of THIS arc's outcome by a future continuation.
- **Plan revisions persist across arcs.** Revisions accumulate in
  `plans/`. References use `<name>_r<NNN>.md`.
- **`implementation_owner` defaults to original arc-1 starter.**
- **Frontmatter on line 1.**
- **Cross-host invocation wording.** Refer to "the Claude-side
  `claude-discuss-continue` skill" or "the Codex-side
  `codex-discuss-continue` skill" rather than slash-prefixed examples.
- **`opencode.json` `permission.skill`** already allows `ocode-*`. No
  permission change needed.
- **v2.3 readback.** When `participants` is missing from `arc01_001`,
  derive `[arc01_001.from, arc01_001.to]`. `turn_order = round-robin`.
  Legacy `implementation_owner: both` accepted only for v2.3 outcome
  readback.
- **Most-recent leaf scan ignores folders without arc-prefixed files.**
  Pre-v2.3 unprefixed transcripts are not continuation targets.

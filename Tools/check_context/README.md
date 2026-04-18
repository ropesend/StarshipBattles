# check_context

Check current Claude Code session context usage.

Reads the most recently modified session JSONL transcript under
`~/.claude/projects/<cwd-slug>/`, finds the last `assistant` record, and
reports Anthropic's `usage` object as ground truth — the exact input
token count for the most recent turn (i.e., the live context window
occupancy).

No estimation. `usage = input_tokens + cache_read_input_tokens + cache_creation_input_tokens`
is what the Anthropic API billed for the input and includes everything
in Claude's context window: system prompt, tool schemas (loaded +
deferred), memory files, skills, and all message history.

## Usage

```bash
python Tools/check_context/check_context.py
```

Output:
```
Session: da41ee62-...
Tokens used: 525,552 / 1,000,000 (52.6%)
  cache_read:       522,554
  cache_created:      2,997
  fresh_input:            1
Threshold: 80.0%
Verdict: CONTINUE
```

## Exit codes

- `0` — CONTINUE (below threshold)
- `1` — STOP (at or above threshold, default 80%)
- `2` — UNKNOWN (transcript not found, or no assistant turns yet)

## Configuration

Threshold + window size come from `Projects/protocols/context_config.md`:
- `CONTEXT_WINDOW_TOKENS` (default 1,000,000)
- `STOP_THRESHOLD_PERCENT` (default 80)

## Integration

Wired as a `Stop` hook in `.claude/settings.json` — the harness runs
this automatically when the assistant finishes a response, so the
current context usage appears before the next user prompt. No manual
invocation needed during a session.

Also invoked by the autonomous work loop protocols:
- `Projects/protocols/03a_continue_working.md` (`/proj-continue` workflow)
- `Projects/protocols/08_automated_loop_protocol.md`
- `Projects/protocols/03b_parallel_projects.md`

## History

- Originally at `Projects/scripts/check_context.py` with a char-count heuristic that estimated ~2× low. Rewrote 2026-04-18 to use Anthropic's `usage` data directly.
- Moved to `Tools/check_context/` 2026-04-18 to align with the per-tool subfolder convention.

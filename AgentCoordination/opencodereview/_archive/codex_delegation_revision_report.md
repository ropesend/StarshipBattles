# Codex Delegation Revision Report

**Date:** 2026-05-02  
**Scope:** Claude Code to OpenCode delegated review system under `AgentCoordination/`, `Tools/agent_coordination/`, `.claude/skills/claude-delegate-review/`, and `.opencode/skills/ocode-review-request/`.

## Executive Summary

The current system should stay with a single review daemon and multiple worker subprocesses. Multiple Claude agents can submit requests concurrently into one queue, and the daemon can launch one independent `opencode run` process per request. Each subprocess has its own OpenCode context window, so separate Claude requests do not share reviewer context.

The next revision should focus on three contract fixes:

1. Make request creation robust for multiline scope, instructions, context, and expected-deliverable text.
2. Standardize completed request files on Option B: original request body, pickup metadata, and one authoritative `## Results` section.
3. Strengthen tests so they prove real follow-up parsing, controlled daemon shutdown, and independent worker execution without relying on real OpenCode in unit tests.

Old completed requests do not need compatibility guarantees. The Claude agent that requests a review may move, archive, or delete older request files before depending on parent/follow-up behavior.

## Architecture Decision

Use one daemon per checkout.

Recommended model:

- Many Claude agents write request files through `create_review_request.py`.
- One daemon watches `AgentCoordination/pending_review_requests/`.
- The daemon has `--max-workers N`.
- Each worker starts a distinct `opencode run --dangerously-skip-permissions ...` subprocess.
- Each OpenCode subprocess receives a distinct request path, review directory, and `result.json` sidecar path.

This meets the independence requirement because context isolation is provided by the separate OpenCode subprocesses, not by separate daemons.

Multiple daemons are not recommended unless there is a future requirement for separate machines, separate queues, or separate resource policies. With the current PID-keyed lock design, multiple daemons against the same queue are intentionally outside the safe operating model.

## Multiline Request Creation

The helper should support a structured payload file as the canonical path for Claude-generated requests.

Recommended interface:

```bash
python Tools/agent_coordination/create_review_request.py --payload-file path/to/request.json
```

Optional secondary interface:

```bash
python Tools/agent_coordination/create_review_request.py --payload-stdin
```

Payload schema:

```json
{
  "type": "code",
  "title": "Follow-up review",
  "scope": "multi\nline\nscope",
  "instructions": "multi\nline\ninstructions",
  "context": "optional multiline context",
  "expected_deliverable": "Report + result.json sidecar.",
  "parent": "req_20260502_010000_abcdef",
  "requester": "claude-code"
}
```

Keep the existing CLI flags for short manual requests, but update `claude-delegate-review/SKILL.md` to prefer `--payload-file`. This avoids shell quoting problems with quotes, backticks, Markdown lists, Windows paths, and long multiline instructions.

The current `--scope-stdin` and `--instructions-stdin` combination is unreliable because the first `stdin.read()` consumes the whole stream. Either reject both flags used together with a clear error or deprecate them in favor of payload JSON.

## Completed File Contract

Adopt Option B.

A completed request file should contain:

- The original request fields and body.
- `**PickedUp:** <timestamp>` as lifecycle metadata outside `## Results`.
- A single authoritative `## Results` section at the end.

It should not contain a stale top-level `**Status:** in-progress` once completed.

Successful result:

```markdown
# Review Request: Example
**Request ID:** req_20260502_120000_abcdef
**Review Type:** code
**Created:** 2026-05-02T12:00:00Z
**Requester:** claude-code
**PickedUp:** 2026-05-02T12:00:03Z

## Scope

...

## Instructions

...

## Results

**Status:** completed
**Completed:** 2026-05-02T12:04:30Z
**Report:** Reviews/results/.../report.md
**Findings:** 7 total (critical: 0, major: 2, minor: 3, info: 2)
```

Failed result:

```markdown
## Results

**Status:** failed
**Completed:** 2026-05-02T12:01:10Z
**FailureReason:** Scope paths do not exist.
```

### Pros

- Keeps the request intent and review output together in one durable receipt.
- Preserves useful pickup timing for debugging queue latency and daemon behavior.
- Gives parsers one canonical place for final status and report metadata.
- Avoids stale or contradictory status fields outside the final result section.

### Cons

- Requires small cleanup logic when moving from `in_progress/` to `completed/`.
- Parsers must treat `## Results` as authoritative instead of scanning every field in the whole file.
- Existing flat-field completed files will not parse unless migrated or explicitly ignored.

## Required Implementation Changes

1. `Tools/agent_coordination/create_review_request.py`
   - Add `--payload-file`.
   - Add optional `--payload-stdin`.
   - Validate required fields from JSON: `type`, `title`, `scope`, `instructions`.
   - Keep `context`, `expected_deliverable`, `parent`, and `requester` optional.
   - Reject malformed JSON and unknown request types with non-zero exits.
   - Reject simultaneous `--scope-stdin` and `--instructions-stdin`, or document them as deprecated.

2. `.claude/skills/claude-delegate-review/SKILL.md`
   - Route normal request creation through a temporary JSON payload file and `--payload-file`.
   - Tell Claude to report the actual request ID printed by the helper.
   - Remove stale `req_{TIMESTAMP}` wording.
   - Fix the malformed request-template code fence around `## Scope`, `## Instructions`, `## Context`, and `## Expected Deliverable`.

3. `Tools/agent_coordination/review_daemon.py`
   - Keep one daemon plus worker pool.
   - Keep PID guard for single-daemon enforcement.
   - On pickup, add or update `PickedUp`.
   - On completion, remove any top-level transient `Status` field before writing `## Results`.
   - Treat `## Results` as the only final status location.
   - Use the same process-tree kill helper for timeout handling that shutdown uses on Windows.

4. `Tools/agent_coordination/parse_results.py`
   - Parse only the `## Results` section.
   - Return normalized JSON keys useful to OpenCode, including `Report`, `Findings`, and optionally `review_dir`.
   - Strip surrounding Markdown backticks if the report path is formatted with them, or stop adding backticks in daemon output.

5. `.opencode/skills/ocode-review-request/SKILL.md`
   - State explicitly that follow-up parent context is loaded through `parse_results.py`.
   - Derive the parent `result.json` path from the normalized parent report path or returned `review_dir`.
   - If the parent is missing or has no parseable `## Results`, write the daemon-provided `result.json` error sidecar and exit.

6. `AgentCoordination/DELEGATION.md`
   - Document one daemon, many independent OpenCode subprocesses.
   - Remove stale priority inheritance language.
   - Fix the direct command example so `--timeout` and `--orphan-age` match their defaults.
   - Clarify that PID-keyed lock files are safe under the single-daemon contract, not a multi-daemon safety mechanism.
   - Document Option B as the completed-file contract.

7. `Tools/agent_coordination/test_daemon_lifecycle.py`
   - Delete the old fake shutdown test containing `or True`.
   - Ensure the real shutdown test injects a mock OpenCode command instead of resolving real `opencode` from PATH.
   - In the follow-up test, assert the follow-up `result.json` contains `parent_report_seen: true` and the parent report path.

8. `tests/unit/tools/test_claude_skill_usage_hook.py`
   - Replace the stale non-Claude no-op expectation with a positive test proving built-in skill names pass through.
   - Patch `_resolve_repo_root` and `subprocess.run` in hook tests so tests never mutate real skill-usage counters.

## Test Plan

Follow strict TDD. Add or revise failing tests before implementation.

Recommended tests:

1. `test_payload_file_preserves_multiline_fields`
   - Create a JSON payload with multiline scope, instructions, context, quotes, backticks, and Windows paths.
   - Run `create_review_request.py --payload-file`.
   - Assert the generated request file preserves exact content.

2. `test_payload_stdin_preserves_multiline_fields`
   - Same as above, but through `--payload-stdin` if that interface is implemented.

3. `test_rejects_dual_plain_stdin_fields`
   - Run with both `--scope-stdin` and `--instructions-stdin`.
   - Assert non-zero exit and clear error, unless the flags are removed.

4. `test_completed_file_option_b_contract`
   - Process a request with a mock sidecar.
   - Assert `PickedUp` remains outside `## Results`.
   - Assert no top-level `Status: in-progress` remains.
   - Assert `Status`, `Completed`, `Report`, and `Findings` are inside `## Results`.

5. `test_failed_file_option_b_contract`
   - Mock an error sidecar.
   - Assert final `FailureReason` is inside `## Results`.
   - Assert no `report.md` assumption is made.

6. `test_follow_up_parser_round_trip_reads_parent_sidecar`
   - Complete a parent request.
   - Run a follow-up mock that calls `parse_results.py` on the parent.
   - Assert the follow-up `result.json` records `parent_report_seen: true`.
   - Assert the parent `result.json` was found from the parsed parent report path or review directory.

7. `test_run_daemon_shutdown_uses_mock_opencode`
   - Start `run_daemon(install_signal_handlers=False)` with an injected mock command.
   - Confirm the mock subprocess is active.
   - Trigger shutdown.
   - Assert daemon exits, PID is removed, and active subprocesses are killed.

8. `test_timeout_kills_process_tree_on_windows`
   - If practical, use a mock process that spawns a child and sleeps.
   - Force a short timeout.
   - Assert the child is not left alive.
   - If Windows child-process assertions are too brittle, isolate process-tree kill into a helper and unit-test helper invocation.

## Open Questions

1. Should `parse_results.py` support legacy flat-field completed files for convenience, or should old requests be treated as disposable and managed by the calling Claude agent?
2. Should request payload JSON files be written to a temp directory and deleted after helper success, or retained in `AgentCoordination/local/` for debugging failed request creation?
3. Should `Report` in `## Results` be raw path text instead of Markdown-backticked text to simplify machine parsing?

## Recommended Next Step

Create a v2.4 implementation spec from this report. Keep the implementation narrow: payload-file request creation, Option B completed files, real follow-up proof, and corrected tests/docs. Avoid redesigning the daemon or lock model until there is evidence that one daemon plus worker pool is insufficient.

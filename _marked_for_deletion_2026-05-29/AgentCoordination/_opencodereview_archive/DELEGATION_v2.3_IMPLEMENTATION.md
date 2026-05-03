# Delegation System v2.3 — Implementation Spec for OpenCode

**Status:** End-to-end trial passed 2026-05-02 (`c:/tmp/delegation_trial_report.md`). One real bug found that breaks follow-ups; rest of this spec is hardening + cleanup. All fixes go in one commit, TDD per item.

**Versions:** v2 implemented. v2.1 lost (overwritten before commit). v2.2 implemented. v2.3 is the post-trial hardening pass and supersedes the prior drafts.

**Files in scope:**
- `Tools/agent_coordination/review_daemon.py`
- `Tools/agent_coordination/test_daemon_lifecycle.py`
- `Tools/agent_coordination/Start-ReviewDaemon.ps1`
- `Tools/agent_coordination/create_review_request.py` (new)
- `Tools/agent_coordination/test_create_review_request.py` (new)
- `Tools/agent_coordination/parse_results.py` (new — small utility)
- `Tools/agent_coordination/README.md`
- `tests/unit/tools/test_claude_skill_usage_hook.py`
- `.claude/skills/claude-delegate-review/SKILL.md`
- `.opencode/skills/ocode-review-request/SKILL.md`
- `AgentCoordination/DELEGATION.md`

---

## Bugs

**B1 — Daemon must refuse to start if another daemon is already running.** [review_daemon.py: `write_pid()`](../Tools/agent_coordination/review_daemon.py). Currently overwrites an existing PID file unconditionally. Two daemons against the same queue would not be safe given the current per-PID lock design.

```python
def _check_no_other_daemon(force: bool = False) -> None:
    if PID_FILE.exists():
        try:
            existing_pid = int(PID_FILE.read_text().strip())
        except (OSError, ValueError):
            existing_pid = None
        if existing_pid and _pid_alive(existing_pid) and existing_pid != os.getpid():
            if not force:
                raise SystemExit(
                    f"Another daemon appears to be running (PID={existing_pid}). "
                    f"Use --force to override (only if you've verified the other process is dead)."
                )
            log(f"--force specified; overriding existing PID file (was PID={existing_pid})")
        # Stale PID file: safe to overwrite
```

Call from `run_daemon()` before `write_pid()`. Add `--force` arg.

**B2 — `Popen` startup failure causes `UnboundLocalError`.** [review_daemon.py: `process_request`](../Tools/agent_coordination/review_daemon.py). The `_active_procs` discard pattern in `finally` references `proc` which may be unbound if `Popen` raised.

```python
proc: subprocess.Popen | None = None
try:
    proc = subprocess.Popen(cmd, ...)
    with _procs_lock:
        _active_procs.add(proc)
    # ... existing communicate/timeout logic
finally:
    if proc is not None:
        with _procs_lock:
            _active_procs.discard(proc)
```

**B3 — Daemon must emit a real `## Results` section, not flat fields.** [review_daemon.py: `move_to_completed`](../Tools/agent_coordination/review_daemon.py). **This is the bug that silently breaks follow-up reviews.** Skill `ocode-review-request` Step 1.5 parses the parent's `## Results` section; daemon today appends `**Field:** value` lines at EOF.

Replace `move_to_completed`'s field appending with section writing:

```python
def _write_results_section(request_path: Path, fields: dict[str, str]) -> None:
    """Write or replace the ## Results section in a request file."""
    content = request_path.read_text(encoding="utf-8")
    # Strip any pre-existing Results section (from EOF)
    content = re.sub(r"\n+## Results\b.*\Z", "", content, flags=re.DOTALL).rstrip()
    lines = ["", "## Results", ""]
    for key, value in fields.items():
        lines.append(f"**{key}:** {value}")
    request_path.write_text(content + "\n".join(lines) + "\n", encoding="utf-8")
```

`move_to_completed` builds the fields dict and calls `_write_results_section` once. Drop the loop of separate `update_request_status` calls for the success path.

`update_request_status` itself stays — it's still used for `Status: in-progress` and `PickedUp:` during pickup, which are top-of-file frontmatter, not Results.

**B4 — Request ID collisions across parallel Claude agents.** Add a helper script and route the skill through it.

New file `Tools/agent_coordination/create_review_request.py`:

```python
"""Create a review request file with a collision-resistant ID and atomic write.

Called by the claude-delegate-review skill. Prints the request ID to stdout
on success; exits non-zero with an error message on failure.
"""
# CLI args:
#   --type {code|plan|architecture|tests|security|performance|consistency|general|custom}
#   --title TEXT
#   --scope TEXT (multi-line; read from stdin if --scope-stdin)
#   --instructions TEXT (multi-line; read from stdin if --instructions-stdin)
#   --context TEXT (optional)
#   --expected-deliverable TEXT (optional)
#   --parent req_<id> (optional, for follow-ups)
#   --requester {claude-code|codex|...} (default: claude-code)
#
# Behavior:
# 1. Generate ID: req_<YYYYMMDD>_<HHMMSS>_<6_hex>
#    Use secrets.token_hex(3) for the suffix; retry up to 5 times if file exists.
# 2. Validate --type against allowed set; reject otherwise.
# 3. Render request body using a Jinja-style fill (no Jinja dep — f-strings).
# 4. Write to AgentCoordination/pending_review_requests/.tmp_<id>.md
# 5. os.replace() to AgentCoordination/pending_review_requests/req_<id>.md (atomic on POSIX and Windows for same-volume).
# 6. Print the request_id to stdout. Exit 0.
```

Also update [claude-delegate-review/SKILL.md](../.claude/skills/claude-delegate-review/SKILL.md) Step 2: replace the inline file-writing instructions with an instruction to call the helper script via Bash and read the request_id from stdout. Keep the request-file template in the skill as documentation of what the helper produces.

---

## Correctness

**C1 — Drop `Priority:` field entirely.** No product semantics defined. Remove from:
- `review_daemon.py` (`_parse_request_priority` and any references)
- `claude-delegate-review/SKILL.md` template
- `create_review_request.py` (don't accept `--priority`)
- `DELEGATION.md` request-format docs
- `test_daemon_lifecycle.py` `test_parse_request_priority` (delete; remove `priority=` arg from `write_request` helper)

**C2 — Document trust boundary in DELEGATION.md.** Add a paragraph near the top:

> **Trust boundary.** `pending_review_requests/` is a trusted-local automation queue. The daemon invokes OpenCode with `--dangerously-skip-permissions`, so request content is effectively a privileged prompt. Only trusted local agents (`claude-code`, `codex`) and the project owner should write to this directory. Do not expose it to untrusted users or remote sources.

No allowlist enforcement — doc-only.

**C3 — Launcher script fixes.** [Start-ReviewDaemon.ps1](../Tools/agent_coordination/Start-ReviewDaemon.ps1):

1. Drop the hard `.venv/` requirement. Replace with: if `.venv\Scripts\Activate.ps1` exists, activate it; otherwise log a note that the script will run against system Python.
2. Replace `python -c "import opencode"` with `Get-Command opencode -ErrorAction SilentlyContinue`. Warn if not found, but proceed (daemon will fail loudly on first request if opencode is genuinely missing).

**C4 — Replace fake `or True` shutdown assertion.** Per Codex MAJ-002, the existing shutdown test contains `assert proc.poll() is not None or True` which can never fail. Delete the entire weak test and replace with the real `run_daemon()`-in-thread test specified in T6.

---

## Tests

Add to existing test files. Run after each: `pytest Tools/agent_coordination/ -x`.

**T1 — PID guard refuses second daemon.** Write a fake PID file with the current process's PID (alive) into `LOCAL_DIR / "review_daemon.pid"`. Call `_check_no_other_daemon()`. Assert it raises `SystemExit`. Then call with `force=True`; assert no exception. Then write a stale PID (e.g. 999999) and assert no exception (stale PID is safe to overwrite).

**T2 — Popen failure produces clean Status: failed.** Pass `opencode_cmd=["nonexistent_executable_xyz_12345"]` to `process_request`. Assert no `UnboundLocalError`, request ends in `completed/` with `Status: failed`, `FailureReason` populated. (`Popen` raises `FileNotFoundError` immediately on invalid executable.)

**T3 — Completed file has real `## Results` section.** Run happy-path mock; assert completed file contains:
- A literal `## Results` heading.
- `**Status:**`, `**Completed:**`, `**Report:**`, `**Findings:**` *under* that heading (regex with `re.DOTALL` matching `## Results.*?\*\*Findings:\*\*`).
- No flat-field results outside the section (i.e., no `**Report:**` line at EOF that isn't under `## Results`).

Update the existing happy-path test (`test_happy_path`) to use the same assertion pattern. The old `_read_status_fields` helper still works for top-of-file fields like `Status: in-progress` during pickup; use a new `_read_results_section` helper for completed files.

**T4 — Helper script tests.** New file `test_create_review_request.py`:
- Generates IDs that match `req_\d{8}_\d{6}_[0-9a-f]{6}`.
- Two calls in rapid succession produce different IDs (collision-resistant).
- Request file appears in `pending/` after a successful run; no leftover `.tmp_*` files.
- Invalid `--type` fails with exit code != 0 and no file created.
- `--parent` adds a `**Parent:** req_<id>` field; absent flag means no Parent line.
- Atomic write: kill the process mid-write (use `os.kill` after `subprocess.Popen`) and assert the destination doesn't exist (only `.tmp_*` should, which can be cleaned up). *Skip on Windows if signal semantics are awkward; mark `xfail` on win32.*

**T5 — Follow-up integration test (parser round-trip).** This is the end-to-end test we missed.
- Mock-OpenCode-1 runs against a parent request, writes `report.md` and `result.json`.
- Daemon completes the parent (writes new-format `## Results` section per B3).
- A follow-up request file is created with `**Parent:** req_<parent_id>`.
- Mock-OpenCode-2 is invoked. Inside the mock, parse the parent's `## Results` section using a small Python snippet (the same pattern the real `ocode-review-request` skill should use; can shell out to `parse_results.py`). Assert the parser successfully extracts `Report:` and `Findings:` from the parent file.
- Mock-2 writes its own `result.json` containing `parent_report_seen: true` and the parent's report path.
- Daemon completes the follow-up. Assert the follow-up's `result.json` confirms the parent context loaded.

**Why a parser utility:** the test needs *something* runnable to assert the skill's prose ("read the parent's `## Results` section") would actually work. Add a small `Tools/agent_coordination/parse_results.py` that reads a request file and prints/returns the Results-section fields as JSON. Use it in T5 and reference it from the OpenCode skill's Step 1.5 ("call `parse_results.py <parent_path>` to load parent context"). Daemon doesn't need it; only the OpenCode-side skill does.

**T6 — Real shutdown test.** Replace the `or True` placeholder.
- Refactor: `run_daemon(install_signal_handlers: bool = True)`. Default behavior unchanged.
- Test: drop two requests, mock opencode sleeps 10s, start `run_daemon(install_signal_handlers=False)` in a thread, wait until both are picked up (poll `_active_workers`), set `daemon._shutdown_requested = True`.
- Assert: thread exits within `SHUTDOWN_TIMEOUT + 5s`; mock subprocesses dead (`proc.poll() is not None` for each tracked proc); `PID_FILE` removed; `_active_procs` empty.

---

## Cosmetic / Docs

**Cs1 — Skill-logging README and hook test.** [Tools/agent_coordination/README.md](../Tools/agent_coordination/README.md) still says the hook filters to `claude-*`; CLAUDE.md and AGENTS.md now say "all skills." Fix README. Replace `test_main_no_op_for_non_claude_prefix` in `tests/unit/tools/test_claude_skill_usage_hook.py` with a positive test that built-in skills (e.g., `loop`, `simplify`) are passed through to `log_skill_usage.py`. Add one negative test for invalid skill-name syntax.

**Cs2 — DELEGATION.md updates** (in addition to C2):
- Drop `Priority:` from the request-format section.
- Document that completed files contain a `## Results` section (matches new B3 reality).
- Document the new helper script as the canonical way to create requests.
- Add a "Failure path" note: failed reviews have an `error` key in `result.json` and may not produce a `report.md`; consumers traversing `Reviews/results/` must not assume `report.md` exists.

**Cs3 — Skill files updated:**
- `claude-delegate-review/SKILL.md`: Step 2 routes through `create_review_request.py`. Drop the inline timestamp instructions. Drop the Priority field from the template. Update the follow-up template the same way.
- `ocode-review-request/SKILL.md`: Step 1.5 references `parse_results.py` for parent context loading. Drop Priority from the parsed-fields list.

**Cs4 — Collapse versioned drafts (do last).** After all tests green and docs updated:
- `AgentCoordination/DELEGATION.md` is the canonical operating doc.
- Move `DELEGATION_v2_IMPLEMENTATION.md`, `DELEGATION_v2.2_IMPLEMENTATION.md`, and `DELEGATION_v2.3_IMPLEMENTATION.md` into `AgentCoordination/_archive/delegation_drafts/`. Don't delete; the trail is useful.
- Move `codex_DELEGATION_REVIEW_REPORT.md` to the same archive directory.

---

## Out of scope (push-back from prior reviews)

- **Codex MAJ-005 (subagent_type terminology).** Trial proved no problem — OpenCode loaded the skill cleanly with `subagent_type: general`. Don't change without evidence.
- **Codex MED-004 (split `review_daemon.py` into 4 files).** Defer; not a blocker. Single file works. Re-evaluate after v2.3 lands and the file actually becomes painful to navigate.
- **Cross-process safe lock naming.** Single-daemon design with PID guard (B1) is sufficient. Don't redesign locks.

---

## Order

(One commit. TDD per item.)
1. T1 + B1 — PID guard
2. T2 + B2 — Popen UnboundLocalError
3. T3 + B3 — `## Results` section + `_write_results_section`
4. T4 + B4 — helper script `create_review_request.py`
5. T6 + C4 — real shutdown test (`install_signal_handlers` refactor)
6. C1 — drop Priority everywhere
7. C3 — launcher fixes
8. Add `parse_results.py` utility
9. T5 — follow-up integration test (depends on B3 + parse_results)
10. C2 — trust boundary doc paragraph
11. Cs1, Cs2, Cs3 — README, DELEGATION.md, skills
12. Cs4 — archive draft specs (very last)

---

## When done

Reply with:
1. Diff summary (files + LOC).
2. Full pytest output: `pytest Tools/agent_coordination/ tests/unit/tools/ -v`.
3. Confirmation that the system was re-tested end-to-end against real OpenCode for at least the follow-up flow (Test 5 above is the unit-level proxy, but a real end-to-end follow-up review is the better signal). Cite the request IDs and review directories.
4. Any deviations from this spec, with rationale.

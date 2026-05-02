# Delegation System v2.4 — Implementation Spec for OpenCode

**Status:** Final hardening pass before the system is locked. v2.3 was implemented in the worktree but never used as the operating contract; v2.4 supersedes it based on Codex's revision report and confirmed user decisions. All fixes go in one commit, TDD per item.

**Versions:** v2 implemented. v2.1 lost. v2.2 implemented. **v2.3 was implemented but never operationalized**; v2.4 includes deletions of v2.3 surface (per-field flags, stdin variants, current `test_create_review_request.py` body, related skill prose) plus the new contract. v2.4 is authoritative.

**Files in scope (✱ already exists from v2.3 — edit/replace; ⚙ exists pre-v2.3):**
- ⚙ `Tools/agent_coordination/review_daemon.py`
- ⚙ `Tools/agent_coordination/test_daemon_lifecycle.py`
- ⚙ `Tools/agent_coordination/Start-ReviewDaemon.ps1`
- ✱ `Tools/agent_coordination/create_review_request.py` — strip per-field/stdin flags, rewrite around `--payload-file`
- ✱ `Tools/agent_coordination/test_create_review_request.py` — replace test body to match the new contract
- ✱ `Tools/agent_coordination/parse_results.py` — verify it parses only `## Results` and rejects flat-field files
- `Tools/agent_coordination/test_parse_results.py` (new)
- ⚙ `Tools/agent_coordination/README.md`
- ⚙ `tests/unit/tools/test_claude_skill_usage_hook.py`
- ✱ `.claude/skills/claude-delegate-review/SKILL.md` — rewrite request-creation section, **fix the malformed code fence at lines 118-142** (verified malformed: fence closes at L125 but template content continues through L141, then a dangling fence at L142)
- ⚙ `.opencode/skills/ocode-review-request/SKILL.md`
- ⚙ `AgentCoordination/DELEGATION.md`

---

## Bugs

**B1 — Daemon must refuse to start if another daemon is already running.** [review_daemon.py: `write_pid()`](../Tools/agent_coordination/review_daemon.py). PID guard at startup; `--force` to override.

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
```

Call from `run_daemon()` before `write_pid()`. Add `--force` CLI arg.

**B2 — `Popen` startup failure causes `UnboundLocalError`.** [review_daemon.py: `process_request`](../Tools/agent_coordination/review_daemon.py). `proc` may be unbound in `finally` if `Popen` raised.

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

**B3 — Completed-file contract: Option B with full lifecycle hygiene.** This is the bug that silently broke follow-ups in the trial.

Required behavior in `move_to_completed`:

1. **Read the in_progress file.** It contains the original request body plus a top-level `**Status:** in-progress` line and `**PickedUp:** <ts>` line written at pickup time.
2. **Strip the top-level `**Status:**` line.** It's stale once we're completing. Use a single-line regex deletion (`re.sub(r"^\*\*Status:\*\*.*\n", "", content, flags=re.MULTILINE, count=1)`).
3. **Keep the `**PickedUp:**` line in place.** It's lifecycle metadata, useful for queue-latency debugging.
4. **Strip any pre-existing `## Results` section** (defensive against retried writes).
5. **Append a single authoritative `## Results` section** at EOF with these fields, in order: `Status`, `Completed`, `Report`, `Findings`, `FailureReason` (the last only if failure).
6. **Do NOT wrap the report path in backticks.** Raw path. Editors still make it clickable; machine parsing doesn't have to strip them.

```python
def _write_results_section(request_path: Path, fields: dict[str, str]) -> None:
    content = request_path.read_text(encoding="utf-8")
    # Strip stale top-level Status (set during pickup, no longer current)
    content = re.sub(r"^\*\*Status:\*\*.*\n", "", content, flags=re.MULTILINE, count=1)
    # Strip any pre-existing Results section
    content = re.sub(r"\n+## Results\b.*\Z", "", content, flags=re.DOTALL).rstrip()
    lines = ["", "", "## Results", ""]
    for key, value in fields.items():
        lines.append(f"**{key}:** {value}")
    request_path.write_text(content + "\n".join(lines) + "\n", encoding="utf-8")
```

Daemon's `move_to_completed` builds the fields dict (no backticks on Report) and calls this helper once. Drop the loop of separate `update_request_status` calls for completion. `update_request_status` itself stays — used at pickup for `Status: in-progress` and `PickedUp:` (top-of-file frontmatter, not Results).

**B4 — Request creation via JSON payload file.** Strip the existing per-field and stdin flags from `create_review_request.py` (v2.3 surface) and rewrite around `--payload-file`. Multiline scope/instructions/context with quotes, backticks, Markdown, and Windows paths cannot be reliably shell-quoted from Bash; JSON payload file is the only sane path.

**Existing flags to remove from `create_review_request.py`:**
- `--scope` (positional value flag)
- `--scope-stdin` (read scope from stdin)
- `--instructions` (positional value flag)
- `--instructions-stdin` (read instructions from stdin)
- Any `--context` / `--expected-deliverable` / `--parent` / `--requester` / `--type` / `--title` flags that bypass the payload (they're now JSON keys)

**New shape of `Tools/agent_coordination/create_review_request.py`:**

```
CLI:
  --payload-file <path>   (required; only interface)

Payload schema (JSON):
  {
    "type": "code|plan|architecture|tests|security|performance|consistency|general|custom",   # required
    "title": "string",                                                                          # required
    "scope": "string (multiline OK)",                                                           # required
    "instructions": "string (multiline OK)",                                                    # required
    "context": "string (multiline OK)",                                                         # optional
    "expected_deliverable": "string",                                                           # optional
    "parent": "req_<id>",                                                                       # optional (follow-ups)
    "requester": "claude-code|codex|..."                                                        # optional, default: claude-code
  }

Behavior:
  1. Validate JSON parses; reject malformed with non-zero exit.
  2. Validate required fields present and `type` is in the allowed set.
  3. Generate request_id: req_<YYYYMMDD>_<HHMMSS>_<secrets.token_hex(3)>.
     Retry up to 5 times if the destination file exists (unique-suffix collision).
  4. Render the request body using the template (see Cs2 for the canonical template).
  5. Write to AgentCoordination/pending_review_requests/.tmp_<request_id>.md.
  6. os.replace() to AgentCoordination/pending_review_requests/req_<request_id>.md
     (atomic on POSIX and same-volume Windows).
  7. Print request_id to stdout, exit 0.

On failure:
  - Validation errors: stderr message, exit non-zero, NO file created.
  - I/O errors mid-write: ensure no partial file left in the destination
    (.tmp_*.md may remain; best-effort cleanup in finally block).
  - Move the offending payload JSON to AgentCoordination/local/failed_payloads/<request_id_attempt>_<reason>.json
    for debugging (create dir if absent).
  - On success: caller's responsibility to delete the temp payload JSON.
    Helper does not retain successful payloads.
```

No `--scope`, `--instructions`, `--scope-stdin`, `--instructions-stdin`, `--payload-stdin`. Payload-file is the only interface.

---

## Correctness

**C1 — Drop `Priority:` everywhere.** No product semantics. Remove from:
- `review_daemon.py`: `_parse_request_priority` and any references.
- Helper script payload schema: no `priority` key.
- `claude-delegate-review/SKILL.md` template and prose.
- `DELEGATION.md` request-format docs.
- `test_daemon_lifecycle.py`: delete `test_parse_request_priority`; remove `priority=` arg from `write_request` helper.

**C2 — Trust boundary doc paragraph in DELEGATION.md.** Add near the top:

> **Trust boundary.** `pending_review_requests/` is a trusted-local automation queue. The daemon invokes OpenCode with `--dangerously-skip-permissions`, so request content is effectively a privileged prompt. Only trusted local agents (`claude-code`, `codex`) and the project owner should write to this directory. Do not expose it to untrusted users or remote sources.

No allowlist enforcement — doc-only.

**C3 — Launcher script fixes.** [Start-ReviewDaemon.ps1](../Tools/agent_coordination/Start-ReviewDaemon.ps1):

1. Drop the hard `.venv/` requirement. If `.venv\Scripts\Activate.ps1` exists, activate it; otherwise log a one-line note and proceed against system Python.
2. Replace `python -c "import opencode"` with `Get-Command opencode -ErrorAction SilentlyContinue`. Warn if not found, but proceed (daemon will fail loudly on first request if opencode is genuinely missing).

**C4 — Replace fake `or True` shutdown assertion.** Per Codex MAJ-002, the existing shutdown test contains `assert proc.poll() is not None or True` which is a tautology. Delete the entire weak test; replace with the real test specified in T6.

**C5 — Process-tree kill helper.** Extract a single helper used by both timeout and shutdown paths:

```python
def _kill_process_tree(proc: subprocess.Popen) -> None:
    """Kill a subprocess and its descendants (Windows-aware)."""
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                           capture_output=True, timeout=10)
        else:
            proc.kill()
    except Exception:
        pass
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass
```

Replace the inline kill+wait in the timeout branch and the shutdown loop with calls to this helper.

**C6 — Delete trial-era flat-field completed files.** As part of v2.4 cleanup, remove the four pre-existing flat-field files in `AgentCoordination/completed_review_requests/` (the 2026-05-02 trial output). They will not parse with the new `parse_results.py` and are disposable. Document this in the commit message; don't try to migrate them.

---

## Tests

Run after each: `pytest Tools/agent_coordination/ tests/unit/tools/ -x`.

**T1 — PID guard.** Write a fake PID file pointing at the current process (alive). Call `_check_no_other_daemon()`. Assert it raises `SystemExit`. Then with `force=True`, no exception. Then write a stale PID (e.g., 999999) and assert no exception (stale is safe to overwrite).

**T2 — Popen failure.** Pass `opencode_cmd=["nonexistent_executable_xyz_12345"]` to `process_request`. Assert: no `UnboundLocalError`, request ends in `completed/` with `Status: failed` and `FailureReason` populated.

**T3 — Option B completed-file contract (success path).** Run happy-path mock; assert completed file:
- Contains a literal `## Results` heading.
- `**Status:**`, `**Completed:**`, `**Report:**`, `**Findings:**` *under* the heading (regex with `re.DOTALL`).
- **No top-level `**Status:** in-progress`** anywhere outside the section.
- `**PickedUp:**` line still present at top-level (not under Results).
- `**Report:**` value is a raw path (no backticks).
- Original request body (Scope, Instructions, etc.) intact.

**T4 — Option B completed-file contract (failure path).** Mock writes error sidecar; assert completed file contains `**Status:** failed` and `**FailureReason:**` inside `## Results`, no top-level Status, no `Report:` line.

**T5 — Helper script tests** (`test_create_review_request.py` — **replace the existing file body wholesale**; v2.3's tests cover the old per-field interface and become obsolete):
- **`test_payload_file_preserves_multiline_fields`**: payload with multiline scope, instructions, context containing quotes, backticks, Markdown lists, and Windows paths. Run helper. Assert generated request file preserves exact content byte-for-byte (modulo template wrapping).
- **`test_id_format_and_uniqueness`**: 10 sequential calls produce 10 different IDs all matching `req_\d{8}_\d{6}_[0-9a-f]{6}`.
- **`test_no_leftover_temp_files_on_success`**: after a successful run, no `.tmp_*` files remain in `pending/`.
- **`test_invalid_type_rejected`**: payload with `type: "bogus"` exits non-zero, no request file created, payload moved to `local/failed_payloads/`.
- **`test_malformed_json_rejected`**: payload file with `{not json}` exits non-zero, no request file created.
- **`test_parent_field_emitted_when_present`**: payload with `parent: "req_abc_123"` produces a request file containing `**Parent:** req_abc_123`. Without the field, no Parent line appears.
- **`test_no_per_field_flags`** (regression guard against v2.3 flags being re-added): invoking with `--scope`, `--scope-stdin`, `--instructions`, `--instructions-stdin`, `--payload-stdin` exits non-zero (these flags must not exist in argparse after v2.4 rewrite).

**T6 — Real shutdown test.** Replace the deleted `or True` test.
- Refactor: `run_daemon(install_signal_handlers: bool = True)`. Default unchanged.
- Test: drop two requests with mock opencode that sleeps 10s, start `run_daemon(install_signal_handlers=False)` in a thread, wait until both are picked up (poll `_active_workers`), set `daemon._shutdown_requested = True`.
- Assert: thread exits within `SHUTDOWN_TIMEOUT + 5s`; mock subprocesses dead (`proc.poll() is not None` for each tracked proc); `PID_FILE` removed; `_active_procs` empty.
- The test must use an injected mock command, not resolve real `opencode` from PATH.

**T7 — Parser round-trip + follow-up integration (mocked).**
- New utility `parse_results.py`: reads a request file, parses **only** the `## Results` section, returns JSON to stdout: `{"Status", "Completed", "Report", "Findings", "FailureReason"?}` plus optional `review_dir` derived from the report path's parent directory. Does NOT support legacy flat-field files; if no `## Results` section is found, exit non-zero with a clear message.
- `test_parse_results.py`: round-trip test — daemon writes a completed file via `_write_results_section`, parser reads it back, assert all fields recovered exactly.
- Follow-up integration test in `test_daemon_lifecycle.py`:
  1. Run mock-OpenCode-1 against a parent request; daemon writes parent's `## Results` section per B3.
  2. Create a follow-up request with `parent: req_<parent_id>`.
  3. Mock-OpenCode-2 shells out to `parse_results.py <parent_request_path>`, reads JSON, derives parent's `result.json` path from the parsed `Report` value's parent directory, reads parent `result.json`, writes its own `result.json` containing `parent_report_seen: true` and the parent's report path.
  4. Daemon completes the follow-up.
  5. Assert: follow-up's `result.json` contains `parent_report_seen: true` and a non-empty parent report path.

**T8 — Skill-usage hook tests (cleanup).** [tests/unit/tools/test_claude_skill_usage_hook.py](../tests/unit/tools/test_claude_skill_usage_hook.py):
- Delete `test_main_no_op_for_non_claude_prefix` (wrong post-"all skills" change).
- Add positive tests: `loop`, `simplify`, `review`, `security-review` are passed through to `log_skill_usage.py`.
- Add one negative test: invalid skill-name syntax (e.g., `BadName`, `with spaces`) is rejected by the regex.
- Patch `_resolve_repo_root` and `subprocess.run` so tests do not mutate real skill-usage counters.

---

## Cosmetic / Docs

**Cs1 — Skill-logging README.** [Tools/agent_coordination/README.md](../Tools/agent_coordination/README.md) still says hook filters to `claude-*`. Update to "all valid skill names per `SKILL_NAME_RE`."

**Cs2 — DELEGATION.md updates** (in addition to C2 trust boundary):
- Drop `Priority:` from request-format section.
- Document `## Results` as the canonical completion contract per Option B; state explicitly that `Status: in-progress` is removed at completion and `PickedUp` stays outside `## Results`.
- Document that `Report:` paths are raw (no backticks).
- Document the helper script as the canonical request-creation interface; show a payload-file example.
- Add a "Failure path" note: failed reviews have an `error` key in `result.json` and may not produce a `report.md`. Consumers traversing `Reviews/results/` must not assume `report.md` exists.
- Fix the example command line to use defaults that match the code (`--timeout 1800 --orphan-age 3600`).
- Clarify that PID-keyed lock files are safe under the single-daemon contract, not a multi-daemon mechanism.

**Cs3 — Skill files updated:**
- `claude-delegate-review/SKILL.md`:
  - Rewrite Step 2 around `--payload-file`. Show a JSON payload example. Drop `Priority:` from prose and template. Drop the inline timestamp instructions. Update follow-up template the same way.
  - **Fix the malformed code fence at lines 118-142.** The opening fence at L118 is closed at L125, leaving the template's `## Scope`/`## Instructions`/`## Context`/`## Expected Deliverable` sections (L127-L141) outside the fence and rendering as real document headings, plus a dangling fence at L142. The rewrite should produce one well-formed example block (or replace the example entirely with a JSON-payload example, which is preferred — the markdown template doesn't need to be shown if the helper script handles it).
- `ocode-review-request/SKILL.md`: Step 1.5 explicitly calls `parse_results.py <parent_path>` to load parent context. Derive parent `result.json` from the parsed `Report` path's parent directory. If the parent has no parseable `## Results`, write an error sidecar and exit. Drop `Priority:` from parsed-fields list.

**Cs4 — Collapse versioned drafts (do last).** After all tests green and docs updated:
- `AgentCoordination/DELEGATION.md` is the canonical operating doc.
- Move `DELEGATION_v2_IMPLEMENTATION.md`, `DELEGATION_v2.2_IMPLEMENTATION.md`, `DELEGATION_v2.3_IMPLEMENTATION.md`, `DELEGATION_v2.4_IMPLEMENTATION.md`, `codex_DELEGATION_REVIEW_REPORT.md`, and `codex_delegation_revision_report.md` into `AgentCoordination/_archive/delegation_drafts/`.
- Don't delete; trail is useful.

---

## Out of scope

- **Codex MAJ-005 (subagent_type terminology).** Trial proved no problem. Not changing without evidence.
- **Codex MED-004 (split `review_daemon.py`).** Defer; single file works.
- **Cross-process safe lock naming.** Single-daemon design with PID guard is sufficient.
- **Legacy flat-field parser support.** New format only; old files are disposable (C6).
- **`--payload-stdin`, `--scope-stdin`, `--instructions-stdin`, per-field `--scope`/`--instructions` flags.** Payload-file is the only request-creation interface.
- **Real `opencode run` invocation in unit tests.** Mocks only. The live end-to-end follow-up sign-off run (below) is the real-OpenCode signal.

---

## Order

(One commit. TDD per item.)
1. T1 + B1 — PID guard
2. T2 + B2 — Popen UnboundLocalError
3. T3 + T4 + B3 + C5 — Option B completion + process-tree kill helper
4. T5 + B4 — payload-file helper script
5. T6 + C4 — real shutdown test (`install_signal_handlers` refactor)
6. T7 — parse_results utility + follow-up integration test
7. C1 — drop Priority everywhere
8. C3 — launcher fixes
9. C2 — trust boundary doc
10. C6 — delete trial-era flat-field files
11. T8 + Cs1 — skill-usage hook tests + README
12. Cs2 — DELEGATION.md
13. Cs3 — skill rewrites
14. Cs4 — archive versioned drafts (very last)

---

## Sign-off requirements

When done, reply with:

1. **Diff summary** — files touched, LOC delta.
2. **Full pytest output** — `pytest Tools/agent_coordination/ tests/unit/tools/ -v`.
3. **Live end-to-end follow-up review.** Run a real parent review against live OpenCode (small target — one Python file is fine), confirm it completes with a proper `## Results` section. Then submit a follow-up via `--payload-file` with `parent: <parent_id>`. Confirm OpenCode reads parent context via `parse_results.py` and the follow-up's `result.json` contains a verification matrix or equivalent evidence that parent findings were considered. Cite both request IDs and review directories in the report.
4. **Any deviations from this spec, with rationale.**

The unit-level T7 proves the parser works. The live follow-up run is the only signal that the *skill* actually invokes the parser. Both are required for sign-off.

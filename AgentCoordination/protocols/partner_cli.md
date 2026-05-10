---
protocol_version: 1.0
last_verified_utc: 2026-05-09T17:00:00Z
status: help-documented; live cross-agent invocation unproven
---

# Partner CLI Recipe Registry

Canonical invocation patterns for cross-agent CLI calls used by consult and
discuss-automation skills. The harmonized contract this registry implements
lives at `AgentCoordination/Scratchpad/Discussion/20260509T170814Z_consult-discuss-harmonize/plans/consult_harmonization_r002.md`.

## Status of evidence

These recipes are **help-documented and command-verified present** on the
agent host that authored this file. Live cross-agent model invocation in
this repo (e.g. `claude` shelling out to `codex exec` and getting a real
response) has NOT been proven. Expect the first user-driven smoke test to
surface flag-name or sandbox-policy adjustments. Update the
`last_verified_utc` field above when the smoke passes.

## Per-agent recipes

The trailing positional argument is always the prompt string. The Python
helper `Tools/agent_coordination/partner_invoke.py` constructs these
commands programmatically; this document is the human-readable reference.

### opencode

```
opencode run --dir <repo-root> --format json --dangerously-skip-permissions <prompt>
```

| Flag | Purpose |
|------|---------|
| `--dir <repo-root>` | Sets the working directory the OpenCode worker runs in. |
| `--format json` | Structured output for parsing. |
| `--dangerously-skip-permissions` | Bypass interactive approval. Required for non-interactive use. |

Binary discovery: `shutil.which("opencode" / "opencode.exe" / "opencode.cmd" / "opencode.ps1")`.

Reference call site: `Tools/agent_coordination/review_daemon.py:471` (uses `--dangerously-skip-permissions` non-interactively, proven in production).

### codex

```
codex exec -C <repo-root> --sandbox <read-only|workspace-write> --skip-git-repo-check [-o <response-file>] <prompt>
```

| Flag | Purpose |
|------|---------|
| `-C <repo-root>` | Equivalent of cwd: the directory Codex resolves paths from. |
| `--sandbox <mode>` | `read-only` for advisory consults; `workspace-write` only when `allow_tests: true`. Treat as policy, not enforcement, until probed. |
| `--skip-git-repo-check` | Allow running outside a strict Git workspace; needed when the consult leaf or invoking shell is not at a clean repo root. |
| `--output-last-message <file>` | Capture Codex's final assistant message to a file. **Callers MUST validate the captured text against the `consult/v1` schema before treating it as a response artifact** (see `partner_invoke.validate_response_file`); the wrapper does NOT distinguish between a deliberately-written artifact and Codex's chat output. `partner_invoke.invoke_sync` performs this validation automatically and moves invalid captures to `<response>.invalid-output-<timestamp>.txt` while downgrading the result to `error_kind="missing-response"`. |

`codex exec` is non-interactive by default (no `--ask-for-approval` flag exists in 0.130.x). Verified against `codex exec --help` 2026-05-09.

Binary discovery: `shutil.which("codex" / "codex.exe" / "codex.cmd")`. **Live finding 2026-05-09:** the codex installer (`%LOCALAPPDATA%\OpenAI\Codex\bin\codex.exe`) is NOT auto-added to PATH on Windows; the consult skill must either prepend the install dir to `$env:PATH` or surface a clear "codex not on PATH" error pointing at the standard install location.

### gemini

```
gemini -p <prompt> -m <model> --approval-mode plan --skip-trust --output-format json --session-id <fresh-uuid>
```

| Flag | Purpose |
|------|---------|
| `-p, --prompt <string>` | Non-interactive headless mode. Required. **String-valued: the prompt must be the next arg, not at end of argv** (live smoke 2026-05-10 surfaced "Not enough arguments following: p" when prompt was at the end). |
| `-m, --model <id>` | Model id. Default: `gemini-3.1-pro-preview`. The CLI accepts any string; the API enforces. Per-invocation override via `--model` on `claude-consult`. |
| `--approval-mode plan` | Read-only mode at the CLI level: blocks all write/edit/run tools. Pattern A enforces gemini cannot mutate the workspace. |
| `--skip-trust` | Trust the workspace for this invocation. Required to make `--approval-mode plan` take effect (otherwise it gets overridden to `default`). |
| `--output-format json` | Structured stdout the wrapper parses to extract the assistant text. NOT reliably honored when tool errors cascade — see "Materialization fallback" below. |
| `--session-id <uuid>` | **Mandatory per r003 Change D.** Fresh `uuid.uuid4()` per invocation. Without this, gemini `-p` mode persists session/tool state across separate invocations and can leak prior-leaf reads into the current run (codex live smoke 2026-05-10). |

Pattern A (read-only + wrapper-writes): gemini has no `--output-last-message` flag. The wrapper extracts the final assistant text from stdout JSON via `partner_invoke._materialize_gemini_response` and writes `response.md` itself, then runs `validate_response_file`. Gemini does not directly publish files.

Pattern B (auto_edit + `--include-directories <leaf>`) is documented as fallback if Pattern A's prompt fails to suppress preamble/postamble around the artifact. Not the default.

#### Materialization fallback

`_materialize_gemini_response` has TWO paths:

1. **JSON path:** `--output-format json` produces `{"session_id": ..., "response": "<assistant text>", "stats": ...}`. Helper extracts the `response` field.
2. **Text fallback:** When tool errors cascade (gitignored read failures, blocked tools), gemini's stdout becomes raw markdown prose with no JSON wrapping. Helper falls back to a regex-locate of `^---\nprotocol: consult/v1` in the raw text and extracts from there. The regex is intentionally strict — fenced JSON or arbitrary prose won't match.

Either path → the materialized file gets validated against the `consult/v1` schema by `validate_response_file`; invalid captures move to a `*.invalid-output-<timestamp>.txt` sidecar.

#### Direction validation (r003 Change E)

`validate_response_file(path, expected_from=..., expected_to=...)` REJECTS schema-shaped artifacts that have reversed direction fields. Codex live smoke 2026-05-10 produced an artifact with `from: codex, to: gemini` (totally wrong but schema-valid) that passed pre-r003 validation. The consult skill MUST pass `expected_from=<partner>, expected_to=<initiator>` when calling `invoke_sync`.

#### Expected stderr noise (r003 Change F)

The following stderr lines are EXPECTED during normal gemini invocations and do NOT indicate failure. Smoke pass conditions evaluate exit code, response artifact validity, direction fields, and absence of `*.invalid-output-*.txt` sidecar — NOT stderr cleanliness:

- `Attempt N failed: You have exhausted your capacity on this model.. Retrying after Nms...` — gemini-cli's automatic quota retry (Google AI Ultra subscription has rate-limit-style backoff). Transparent and benign.
- `[LocalAgentExecutor] Blocked call: Unauthorized tool call: 'X' is not available to this agent.` — Pattern A doing its job; gemini reaches for a write/network tool, plan mode blocks it. Expected.
- `Error executing tool read_file: File path '...' is ignored by configured ignore patterns.` — gemini's gitignore-aware tool layer; expected when gemini reaches into Scratchpad/ or other gitignored locations. The wrapper embeds the request body inline so gemini doesn't need these reads to succeed.
- `Ripgrep is not available. Falling back to GrepTool.` — minor; gemini falls back automatically.
- `Warning: 256-color support not detected.` — terminal warning; harmless.

Auth precondition: gemini-cli requires one of `GEMINI_API_KEY`, `GOOGLE_GENAI_USE_VERTEXAI`, `GOOGLE_GENAI_USE_GCA` env vars (or `~/.gemini/settings.json` carrying an auth method). The consult skill checks this before invocation and surfaces an actionable error pointing the user at the right path for their account.

Binary discovery: `shutil.which("gemini" / "gemini.exe" / "gemini.cmd" / "gemini.ps1")`.

### claude

```
claude -p --no-session-persistence --output-format json --permission-mode dontAsk [--allowedTools <set>] [--disallowedTools <set>] <prompt>
```

| Flag | Purpose |
|------|---------|
| `-p` (`--print`) | Non-interactive: produce response and exit. |
| `--no-session-persistence` | Don't carry session state across invocations. |
| `--output-format json` | Structured output for parsing. |
| `--permission-mode dontAsk` | Apply allowlist without prompting. |
| `--allowedTools <set>` | Restrict tool surface. Prefer read/search tools for advisory consults. |
| `--disallowedTools <set>` | Block edit/write tools when calling Claude as a consult responder. |

Binary discovery: `shutil.which("claude" / "claude.exe" / "claude.cmd" / "claude.ps1")`.

Tool allowlist: the exact safe Starship allowlist for the responder side
needs a live probe before reliance. Until then, the responder skill
relies on its own SKILL.md instructions to enforce read-only behavior, not
on `--allowedTools`/`--disallowedTools`.

## Sandbox defaults by consult mode

| Mode | codex sandbox | claude permission surface | Tests allowed |
|------|---------------|---------------------------|---------------|
| `planning` | `read-only` | restricted (read/search only) | no |
| `mid-project-review` | `read-only` | restricted | no |
| `pre-final-check` | `workspace-write` | broader (test runners) | yes (opt-in via `--allow-tests`) |
| `deep-dive` | `workspace-write` | broader | yes (opt-in) |

`workspace-write` granting "consult-leaf-only" writes is an aspiration. Treat
it as a prompt/tool-restriction policy until the first live probe confirms
the sandbox flag actually bounds writes that way.

## Usage

The Python helper `Tools/agent_coordination/partner_invoke.py` exports:

- `resolve_binary(name)` — returns binary path or `None`.
- `build_command(partner, binary, prompt, *, repo_root, response_file=None, sandbox="read-only")` — returns the argv list per recipes above.
- `invoke_sync(partner, prompt, *, log_path, repo_root=None, response_file=None, sandbox="read-only", timeout_sec=600)` — runs the partner, returns `InvokeResult` with `exit_status`, `error_kind`, `partner_completed`, captured stdout/stderr, and a log path.
- `validate_response_file(path)` — validates `consult/v1` response frontmatter and completion semantics.
- `write_error_response(path, *, from_agent, to_agent, mode, error_kind, detail="")` — publishes a complete `exit_status: error` artifact when the wrapper, not the partner, completes failure handling.

Skills should not construct argv themselves; route everything through
`partner_invoke.build_command` to keep the recipe registry single-source.

## Update procedure

When a partner CLI changes flag names or default behavior:

1. Update the relevant section above.
2. Update `Tools/agent_coordination/partner_invoke.py::build_command`.
3. Update the unit tests in `tests/unit/agent_coordination/test_partner_invoke.py`.
4. Bump `last_verified_utc` when a live smoke passes.

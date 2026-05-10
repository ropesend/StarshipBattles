# LLM Context Security Report
## Summary
- Sites Audited: 17
- Total Findings: 3
- Critical: 0 | Major: 1 | Minor: 2

## Findings

### 1. MAJOR — ImageBackgroundCall lacks non-ImageException safety net (no `ImageUnexpectedError` wrapper)

**File:** `game/ui/services/image/background.py:166-194`

`LLMBackgroundCall._run()` (at `background.py:285`) wraps unexpected non-LLM provider exceptions in `LLMUnexpectedError`, preserving `__cause__` and storing `original_exception_type` in context. This ensures the `_error` property stays typed as `LLMException`, `_status` transitions to ERROR, and the worker thread doesn't crash silently.

`ImageBackgroundCall._run()` only catches `ImageCancelled` and `ImageException`. If a concrete image provider raises a non-`ImageException` (e.g., `RuntimeError`, `KeyError` during response parsing, or a third-party HTTP-library exception), it:

- Escapes the inner try/except block
- Reaches the outer `finally` (which correctly releases the in-flight slot)
- Propagates as an unhandled exception on the worker thread
- Leaves `_status` as `RUNNING` (a non-terminal state)
- Stores no `_error` for callers to inspect

Additionally, `ImageBackgroundCall` has no `_done_event` / `wait()` mechanism (present in the LLM counterpart), making it impossible to deterministically block on completion from test threads.

**Remediation:** Add a broad-catch wrapper analogous to `LLMUnexpectedError`, or ensure every image provider maps all third-party failures to `ImageException` subclasses before crossing the provider boundary (as docs/05_ERROR_HANDLING.md §"New image provider" already requires). Since providers are pluggable, the safety net in the background helper is the stronger guarantee.

---

### 2. MINOR — RaceDescriptionLLMController logs `call.error` str() directly

**File:** `game/strategy/services/race_description_llm_controller.py:294-299`

```python
logger.error(
    "Race description %s ERROR: %s: %s",
    state.log_label,
    type(call.error).__name__ if call.error else "Unknown",
    call.error,
)
```

The `%s` format for `call.error` invokes `str(LLMException)`, which includes the exception's message. All LLM exceptions in this codebase carry safe messages (no API keys, no request bodies, no response bodies) — no actual leak exists. However, logging the full exception string is more verbose than necessary when `type(call.error).__name__` already identifies the category. Trimming this to only log the error type name would reduce log noise and eliminate any future risk if provider error messages change.

**Remediation:** Remove `call.error` from the log line; `type(call.error).__name__` is sufficient for this diagnostic log.

---

### 3. MINOR — ImageBackgroundCall missing `_done_event` / `wait()` (feature parity gap with LLM counterpart)

**File:** `game/ui/services/image/background.py`

`LLMBackgroundCall` supports `wait(timeout=None)` via `_done_event` (PROJ-324 Phase 2), which allows deterministic blocking on terminal state — critical for tests that need to assert on results without polling `status` with `time.sleep`. `ImageBackgroundCall` lacks this mechanism entirely. Callers (including tests) can only poll `status` in a loop, which is slower and less reliable.

**Remediation:** Add `_done_event` and `wait()` to `ImageBackgroundCall`, mirroring the LLM implementation. The event should be set in all terminal branches (`CANCELLED`, `ERROR`, `DONE`, and `cancel()`) outside the state lock.

---

## Contract Compliance Summary

| Contract | File | Status |
|---|---|---|
| `__repr__` redacts API key | `deepseek.py:76-77` | PASS |
| `__repr__` redacts API key | `openai_provider.py:78-79` | PASS |
| API key per-request, never cached | `deepseek.py:68-72,241-253` | PASS |
| API key per-request, never cached | `openai_provider.py:70-74,234-243` | PASS |
| No secrets in exception context (LLM) | `deepseek.py:110-236` | PASS |
| No secrets in exception context (Image) | `openai_provider.py:114-230,331-381` | PASS |
| No secrets in logs (LLM) | `deepseek.py:125-136,334-337` | PASS |
| No secrets in logs (Image) | `openai_provider.py:134-159,385-388` | PASS |
| SSL verification ON | `deepseek.py:118-123` (default) | PASS |
| SSL verification ON | `openai_provider.py` (default) | PASS |
| Timeouts always set | `deepseek.py:99-103` | PASS |
| Timeouts always set | `openai_provider.py:100-104` | PASS |
| Retry 5xx only, never 429 | `deepseek.py:106-237` | PASS |
| Retry 5xx only, never 429 | `openai_provider.py:110-230` | PASS |
| Provider errors → domain exceptions | `deepseek.py:124-237` | PASS |
| Provider errors → domain exceptions | `openai_provider.py:133-230` | PASS |
| `LLMBackgroundCall.start()` enforces MAX_CONCURRENT | `background.py:151-161` | PASS |
| `LLMBackgroundCall.wait()` only observes terminal states | `background.py:222-235` | PASS |
| `LLMProviderFactory.create()` routes unknown providers | `factory.py:71-81` | PASS |
| `ImageProviderFactory.create()` routes unknown providers | `image/factory.py:63-73` | PASS |
| `LLMUnexpectedError` wraps non-LLM escapes | `background.py:285-307` | PASS |
| Equivalent image unexpected wrapper | `image/background.py:166-194` | **FAIL** (no wrapper) |
| Deferred validation: constructor `LLMConfigError` → `None` | `factory.py:85-87` | PASS |
| Deferred validation: constructor `ImageConfigError` → `None` | `image/factory.py:77-79` | PASS |
| Broad-catch justification comments present | `background.py:285`, `race_description_llm_controller.py:308`, `openai_provider.py:413` | PASS |
| No prompt/response body in logs or context | All sites | PASS |
| No API key, Authorization header in logs or context | All sites | PASS |
| No `except:` (bare except) | All sites | PASS |
| No generic `raise Exception` | All sites | PASS |

## Recommendations

1. **Add `ImageUnexpectedError` and broad-catch in `ImageBackgroundCall._run()`** — Mirror the `LLMUnexpectedError` pattern to prevent silent worker-thread crashes from non-`ImageException` provider escapes. This is the single highest-priority fix.

2. **Add `_done_event` / `wait()` to `ImageBackgroundCall`** — Parity with `LLMBackgroundCall` for deterministic test blocking. Lower priority than #1 but important for test reliability.

3. **Trim `call.error` from `RaceDescriptionLLMController` error log** — Remove the verbatim exception string (line 298); `type(call.error).__name__` is sufficient for the diagnostic. Cosmetic / defense-in-depth.

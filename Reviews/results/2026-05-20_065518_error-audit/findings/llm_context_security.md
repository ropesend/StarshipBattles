# LLM Context Security Report

## Summary
- **Sites Audited**: 21 files
- **Total Findings**: 5
- **Critical**: 0 | **Major**: 0 | **Minor**: 5

---

## LLM Service Security Review

### `game/services/llm/deepseek.py` (354 lines)

**API Key Handling**: Pass
- `_read_api_key()` (line 241): reads `DEEPSEEK_API_KEY` from `os.environ` per-request, never cached on instance.
- `__repr__` (line 77): `"DeepSeekProvider(api_key=<REDACTED>)"` — key completely redacted.
- `__str__` (line 79): delegates to `__repr__`.
- `_build_headers()` (line 280): builds `Authorization: Bearer <key>` header — never logged, never included in exception context.
- `LLMConfigError` for missing key (line 248): context contains only `{"provider": "deepseek"}` — safe.

**Exception Context Safety**: Pass
Every exception site verified. All context dicts contain ONLY safe fields:
| Exception Type | Context Fields | Safe? |
|---|---|---|
| `LLMTimeoutError` (line 128) | `attempt`, `model` | ✓ |
| `LLMNetworkError` (line 138) | `attempt`, `model`, `error_type` | ✓ |
| `LLMNetworkError` SSL (line 149) | `attempt`, `model` | ✓ |
| `LLMRateLimited` (line 165) | `status_code`, `model`, `request_duration_ms` | ✓ |
| `LLMConfigError` auth (line 178) | `status_code`, `model` | ✓ |
| `LLMResponseError` 4xx (line 190) | `status_code`, `model` | ✓ |
| `LLMResponseError` unexpected (line 222) | `status_code`, `model` | ✓ |
| `LLMNetworkError` 5xx exhausted (line 229) | `status_code`, `attempts`, `model` | ✓ |
| `LLMResponseError` non-JSON (line 297) | `status_code`, `model` | ✓ |
| `LLMResponseError` missing fields (line 315) | `status_code`, `model`, `missing_field` | ✓ |
| `LLMCancelled` (line 110) | `attempt` | ✓ |

No `body`, `prompt`, `messages`, `response`, `api_key`, or `headers` in any context dict or log statement.

**Logging Safety**: Pass
- Line 125: `logger.error("DeepSeek request timed out: attempt=%d", attempt)` — safe.
- Line 134: `logger.error("DeepSeek connection error: attempt=%d type=%s", ...)` — safe.
- Line 148: `logger.error("DeepSeek SSL error: attempt=%d", attempt)` — safe.
- Line 207: `logger.warning("DeepSeek 5xx, retrying: status=%d attempt=%d backoff=%.2fs", ...)` — safe.
- Line 334: `logger.info("DeepSeek call ok: model=%s tokens=%d latency_ms=%d", ...)` — safe (metadata only).
- Line 313: `request_id` extracted from response and stored in `CompletionResult`. Provider-issued trace IDs are standard practice for support diagnostics; verified not a credential.

**Retry Policy**: Pass — 5xx only with exponential backoff, never retry 429. Cancel token checked between retries.

---

### `game/services/llm/background.py` (375 lines)

**API Key / Secret Leakage**: Pass — no API keys or credentials referenced in this module.

**Exception Context Safety**: Pass
- `LLMConfigError` at max concurrent calls (line 153): context `{"in_flight": ..., "max": ...}` — safe.
- `LLMUnexpectedError` wrapping (line 296): context `{"original_exception_type": type(e).__name__}` — safe, original exception on `__cause__`.

**Logging Safety**: **MINOR finding** (see "Logging `%r` on unexpected worker exceptions").

- Line 292-295: `logger.exception("LLMBackgroundCall worker raised non-LLM exception: %r", e)` — uses `%r` on a raw `Exception` instance, invoking `repr(e)`. While standard exception `repr()` typically returns `TypeName('message')`, a third-party exception could include sensitive data in its repr (e.g., request metadata). This catch is only reached for true provider escapes (non-`LLMException` types), so blast radius is small, but `%s` is safer and sufficient for diagnostic purposes.

**Provider Exception Conversion**: Pass
- `LLMCancelled` → stays `CANCELLED` (line 270-275).
- `LLMException` → `ERROR` with error stored (line 277-284).
- Non-`LLMException` → wrapped as `LLMUnexpectedError` (line 285-299), preserving the original on `__cause__` and the type name in safe context. Without this, `_status` would stay `RUNNING` forever.

**Instance State**: Pass — `self._messages` (prompt content) is stored on the instance but never exposed through public API. It is passed to `provider.complete()` internally only.

---

### `game/services/llm/provider.py` (76 lines)

Protocol definition only — no concrete code, no logging, no exception handling. Pass.

---

### `game/services/llm/factory.py` (79 lines)

Delegates to shared `resolve_provider()` in `game/services/provider_factory.py`. No logging, no credential handling. Pass.

---

### `game/services/llm/types.py` (95 lines)

DTO definitions only. **MINOR finding**: No `__repr__` override.

- `CompletionResult` (line 63): frozen dataclass with fields `text`, `usage`, `model`, `finish_reason`, `latency_seconds`, `provider`, `request_id`. Default `__repr__` would include the full `text` (LLM response) and full `usage` object. If this object is ever logged via `%r` / `repr()` / f-string `{result!r}`, the LLM's complete response text appears in logs.
- `Message` (line 41): frozen dataclass with fields `role`, `content`. Default `__repr__` would include the full `content` (prompt text). If message list is ever logged via `repr()`, all prompt text leaks.
- Current production code does not log these objects via repr; the finding is a defensive hardening recommendation.

---

### `game/services/llm/defaults.py` (42 lines)

Simple getter/setter — no logging, no exception handling. Pass.

---

### `game/services/llm/__init__.py` (51 lines)

Re-export only + registration import. Pass.

---

### `game/services/provider_factory.py` (87 lines)

Shared factory machinery. No logging. Deferred validation catch (line 82-83) drops the exception without logging — safe (the caller is expected to handle None). Pass.

---

## Image Service Security Review

### `game/ui/services/image/openai_provider.py` (426 lines)

**API Key Handling**: Pass
- `_read_api_key()` (line 234): reads `OPENAI_API_KEY` from `os.environ` per-request.
- `__repr__` (line 79): `"OpenAIImageProvider(api_key=<REDACTED>)"` — key completely redacted.
- `__str__` (line 81): delegates to `__repr__`.
- `_build_headers()` (line 245): builds `Authorization: Bearer <key>` — never logged, never in exception context.

**Exception Context Safety**: Pass
All context dicts verified — only safe fields:
| Exception Type | Context Fields |
|---|---|
| `ImageTimeoutError` (line 135) | `attempt`, `model`, `endpoint` |
| `ImageNetworkError` SSL (line 142) | `attempt`, `model`, `endpoint` |
| `ImageNetworkError` connection (line 152) | `attempt`, `model`, `endpoint`, `error_type` |
| `ImageRateLimited` (line 171) | `status_code`, `model`, `request_duration_ms` |
| `ImageConfigError` auth (line 182) | `status_code`, `model` |
| `ImageResponseError` 4xx (line 190) | `status_code`, `model` |
| `ImageResponseError` unexpected (line 216) | `status_code`, `model` |
| `ImageNetworkError` 5xx exhausted (line 222) | `status_code`, `attempts`, `model` |
| `ImageResponseError` non-JSON (line 352) | `status_code`, `model` |
| `ImageResponseError` missing fields (line 364) | `status_code`, `model`, `missing_field` |
| `ImageResponseError` bad base64 (line 377) | `status_code`, `model` |
| `ImageConfigError` file read failed (line 331) | `endpoint`, `field`, `path`, `error_type` |
| `ImageCancelled` (line 114) | `attempt` |
| `ImageConfigError` no key (line 238) | `{"provider": "openai"}` |

No `prompt`, `body`, `response`, `image_bytes`, or `api_key` in any context dict or log statement.

**Prompt Security**: Pass
- `prompt` parameter is received and passed to `_post_generation()`/`_post_edit()` as JSON body — never logged.
- `revised_prompt` from OpenAI response is stored on `ImageResult` but never logged in this module.

**Logging Safety**: Pass
- Line 385: `logger.info("OpenAI image ok: model=%s size=%dx%d latency_ms=%d", ...)` — metadata only.
- Line 325: `logger.error("OpenAI image edit file read failed: field=%s path=%s error_type=%s", ...)` — file path is logged (this is a local filesystem path to an edit source image; not sensitive).

---

### `game/ui/services/image/background.py` (288 lines)

**Logging Safety**: **MINOR finding** (same pattern as LLM background)

- Line 225-228: `logger.exception("ImageBackgroundCall worker raised non-Image exception: %r", e)` — uses `%r`. Same analysis as the LLM equivalent: prefer `%s` for defensive safety.

**Exception Conversion**: Pass
- `ImageCancelled` → `CANCELLED` (line 203-209).
- `ImageException` → `ERROR` (line 210-216).
- Non-`ImageException` → wrapped as `ImageUnexpectedError` (line 217-239), preserving original on `__cause__` and type name in safe context.

**Instance State**: Pass — `self._prompt` is stored on the instance and passed to `provider.generate_image()`, never exposed through public API or logged.

---

### `game/ui/services/image/provider.py` (82 lines)

Protocol definition only — no concrete code. Pass.

---

### `game/ui/services/image/factory.py` (71 lines)

Delegates to shared `resolve_provider()`. Pass.

---

### `game/ui/services/image/types.py` (43 lines)

**MINOR finding**: No `__repr__` override.

- `ImageResult` (line 14): frozen dataclass with fields `image_bytes`, `size`, `model`, `latency_ms`, `provider`, `request_id`, `revised_prompt`. Default `__repr__` would dump the full binary `image_bytes` (potentially huge) and the full `revised_prompt` (provider-rewritten prompt text). If this object is ever logged via `repr()`, binary garbage + prompt text leaks.

---

### `game/ui/services/image/null_provider.py` (62 lines)

Always raises `ImageConfigError` with safe context: `{"provider": "null", "model": ..., "size": ...}`. Pass.

---

### `game/ui/services/image/defaults.py` (45 lines)

Simple getter/setter. Pass.

---

## Caller Security Review

### `game/strategy/services/race_description_llm_controller.py` (312 lines)

This is the primary LLM consumer. Verified all log sites:

- Line 231: `logger.info("Race description %s START: captions=%s", state.log_label, cap_summary)` — `cap_summary` is `{"flag": "present"/"missing", ...}` booleans. Safe.
- Line 241: `logger.error("Race description %s start failed: %s", state.log_label, e)` — `e` is an `LLMConfigError` with safe context. `str(e)` returns the message only (no context dict). Safe.
- Line 287-291: `logger.info("Race description %s DONE: text_len=%d latency=%.2fs tokens=%d", ...)` — metadata only (length, latency, token count). Response text not logged. Safe.
- Line 294-299: `logger.error("Race description %s ERROR: %s: %s", type(call.error).__name__, call.error)` — `call.error` is `LLMException`. `str(call.error)` returns the message string (human-readable error) — the `context` dict is **not** included in `str()`. Safe.
- Line 309: `logger.error("on_change callback raised: %s: %s", type(e).__name__, e)` — safe.

**Instance State**: `self._messages` (from prompt builder) passed directly to `LLMBackgroundCall`. Never logged. Safe.

**Exception Propagation**: `LLMConfigError` at `call.start()` time is caught, logged at error level as `str(e)`, and stored as `state.error` (line 242-243). No sensitive context in `str(e)`. Safe.

---

### `game/strategy/services/race_description_prompt_builder.py` (258 lines)

Pure prompt assembly from game data (RaceConfig + visual captions). No logging, no exception handling. Prompt content contains game-identity fields (race name, government type, aptitudes) — not PII. Environment preferences are numeric game values. Visual captions are parsed sidecar metadata. Safe.

---

### `game/ui/screens/race_setup/llm_dialog_service.py` (154 lines)

Error-to-user-message mapping. `error_message()` (line 136) maps exception types to hardcoded user-facing strings. No exception context or sensitive fields are interpolated. Safe.

---

### `game/ui/screens/race_setup/panel_factory.py` (177 lines)

Wires `get_default_llm_provider()` → `RaceDescriptionLLMController`. No logging, no exception handling. Safe.

---

### `game/ui/panels/race_description_panel.py` (418 lines)

Polls controller status per frame. Logs nothing sensitive. `_tick_field_label()` (line 343) shows elapsed seconds in UI — purely numeric. Safe.

---

### `game/run_loop.py` (223 lines)

Calls `shutdown_all_calls()` at pygame teardown. No sensitive data. Safe.

---

### `game/context.py` (224 lines)

Calls `LLMProviderFactory.create()` / `ImageProviderFactory.create()` at startup. Returns `None` on config error (deferred validation). No logging of credentials. Safe.

---

### `game/core/exceptions.py` (544 lines)

Verified the full `GameException` → `LLMException` → `ImageException` hierarchy:
- `GameException.__init__` (line 101): stores `message`, `code`, `context`. No `__repr__` or `__str__` override — default `str()` returns just the message. The `context` dict is not exposed through stringification. Safe.
- `LLMUnexpectedError` (line 386): `context["original_exception_type"]` contains only a type name string. Safe.
- `ImageUnexpectedError` (line 473): same pattern. Safe.
- No subclass includes any `__repr__` override. Pass.

---

## Findings Summary

### MINOR-1: `%r` in worker-thread unexpected-exception logging
**Files**: `game/services/llm/background.py:293`, `game/ui/services/image/background.py:226`

Both `LLMBackgroundCall._run()` and `ImageBackgroundCall._run()` use `logger.exception("...: %r", e)` when catching unexpected non-domain exceptions. `%r` invokes `repr(e)`, which for third-party exceptions could include sensitive request metadata. The log level is `exception()` (ERROR + traceback), and the traceback alone provides sufficient diagnostic context.

**Recommendation**: Change `%r` to `%s` to only format `str(e)`:
```python
logger.exception(
    "LLMBackgroundCall worker raised non-LLM exception: %s", e,
)
```

### MINOR-2: `CompletionResult` lacks `__repr__` override
**File**: `game/services/llm/types.py:63`

The `text` field (full LLM response) is exposed through the default dataclass `__repr__`. If a `CompletionResult` is ever formatted with `%r` or `repr()`, the entire response body enters log output.

**Recommendation**: Override `__repr__`:
```python
def __repr__(self) -> str:
    return (
        f"CompletionResult(model={self.model!r}, "
        f"text_len={len(self.text)}, finish={self.finish_reason.value!r}, "
        f"latency={self.latency_seconds:.2f}s, tokens={self.usage.total_tokens})"
    )
```

### MINOR-3: `ImageResult` lacks `__repr__` override
**File**: `game/ui/services/image/types.py:14`

The `image_bytes` field (raw PNG binary) and `revised_prompt` (provider-rewritten prompt text) are exposed through default dataclass `__repr__`.

**Recommendation**: Override `__repr__`:
```python
def __repr__(self) -> str:
    return (
        f"ImageResult(model={self.model!r}, size={self.size}, "
        f"latency={self.latency_ms:.0f}ms, provider={self.provider!r}, "
        f"bytes_len={len(self.image_bytes)})"
    )
```

### MINOR-4: `Message` lacks `__repr__` override
**File**: `game/services/llm/types.py:41`

The `content` field (prompt text) is exposed through default dataclass `__repr__`.

**Recommendation**: Override `__repr__`:
```python
def __repr__(self) -> str:
    return f"Message(role={self.role.value!r}, content_len={len(self.content)})"
```

### MINOR-5: `request_id` propagation to result DTOs
**Files**: `game/services/llm/types.py:86`, `game/ui/services/image/types.py:39`

Provider-issued request IDs are stored on `CompletionResult.request_id` and `ImageResult.request_id`. These are not logged directly in production code but could be exposed through the default dataclass repr. Provider request IDs are typically opaque trace identifiers (UUIDs or similar), not credentials — this is standard industry practice for API observability. No action needed unless a specific provider documents their request ID format as containing sensitive information.

**Recommendation**: Document in `docs/05_ERROR_HANDLING.md` that provider-issued `request_id` values are considered safe for logging (non-credential trace identifiers). Add a sentence to the "Service Error Hygiene" safe-fields list.

---

## Recommendations (Prioritized)

| Priority | Finding | Effort | Impact |
|---|---|---|---|
| 1 | MINOR-1: Replace `%r` with `%s` in worker exception logs (2 sites) | 5 min | Defensive hardening against unexpected third-party repr leakage |
| 2 | MINOR-2: Add `__repr__` to `CompletionResult` | 5 min | Prevents accidental LLM response text in logs |
| 3 | MINOR-3: Add `__repr__` to `ImageResult` | 5 min | Prevents binary dump + prompt in logs |
| 4 | MINOR-4: Add `__repr__` to `Message` | 5 min | Prevents accidental prompt content in logs |
| 5 | MINOR-5: Document `request_id` as safe for logging | 2 min | Clarity |

All five findings are MINOR severity — **no instance of API key, token, full request body, or full response body was found in any log statement, exception context dict, or persisted state across all 21 audited sites.** The codebase's "Service Error Hygiene" contract from `docs/05_ERROR_HANDLING.md` line 112-113 is faithfully implemented throughout.

---

## Verification Commands

```bash
# Run LLM service tests to validate no regressions
pytest tests/unit/services/llm/

# Run image service tests
pytest tests/unit/ui/services/image/

# Full audit (if error_audit tool exists)
python Tools/error_audit/error_audit.py
```

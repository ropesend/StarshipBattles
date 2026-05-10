# Phase 4: DeepSeek Implementation [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-296 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** First concrete provider. Hardened HTTP client (SSL on, timeouts, custom UA). Retry on 5xx only (not 429). Adds `requests>=2.31.0` to `requirements.txt`. Adds session-scoped autouse fixture preventing real HTTP calls in tests.

---

## Tasks

### Task 4.1: Add session-scoped `_block_real_http` fixture [Simple]
**File:** `tests/conftest.py`
**Tests:** Run any one test that imports requests.

- [x] Write a test that calls `requests.post('http://example.com')` directly. Confirm without the fixture it would attempt a real call.
- [x] Add to `tests/conftest.py`:
  ```python
  @pytest.fixture(autouse=True, scope='session')
  def _block_real_http():
      """Forbid real HTTP calls in tests. Tests that need to mock HTTP must
      explicitly override requests.post via unittest.mock.patch."""
      import requests
      original_post = requests.post
      original_get = requests.get
      def _raise(*a, **k):
          raise RuntimeError(
              "real HTTP forbidden in tests; use unittest.mock.patch on "
              "requests.post/get with a mock_llm_response fixture"
          )
      requests.post = _raise
      requests.get = _raise
      yield
      requests.post = original_post
      requests.get = original_get
  ```
- [x] Add a test: `def test_real_http_is_blocked():` confirming `requests.post(...)` raises `RuntimeError`
- [x] Verify **no existing test breaks**. If any does (someone was making a real HTTP call), STOP and investigate.

**Notes:**

### Task 4.2: Pin `requests` in `requirements.txt` [Simple]
**File:** `requirements.txt`
**Tests:** `pip install -r requirements.txt` succeeds

- [x] Add line: `requests>=2.31.0`
- [x] Run `pip install -r requirements.txt` to confirm clean install
- [x] Verify `import requests; requests.__version__` reports >= 2.31.0

**Notes:**

### Task 4.3: Implement `DeepSeekProvider` [Complex]
**File:** `game/services/llm/deepseek.py` (NEW)
**Tests:** `pytest tests/unit/services/llm/test_deepseek.py`

- [x] Write failing tests (TDD — define the behavior first):
  - **Construction:**
    - `DeepSeekProvider()` constructs OK regardless of env (key is read per-call, not at init)
    - `repr(DeepSeekProvider())` does NOT include the API key (use `monkeypatch.setenv` to set a fake key, assert it's not in repr)
  - **`complete()` happy path:**
    - With `requests.post` patched to return a valid DeepSeek response, `complete([Message(role=Role.USER, content='hi')])` returns a `CompletionResult` with all fields populated correctly
    - Assert the request body shape: `{model: 'deepseek-chat', messages: [{role, content}], temperature, max_tokens}`
    - Assert headers: `Authorization: Bearer <key>`, `Content-Type: application/json`, `User-Agent: starship-battles-llm/1.0`
    - Assert `timeout=(5, 30)` was passed
    - Assert `verify` is NOT explicitly set (defaults to True)
  - **`complete()` no key:**
    - With env var unset, raises `LLMConfigError` with code L001
  - **`complete()` 5xx retry:**
    - Mock returns 503 twice then 200; provider succeeds with 2 retries
    - Mock returns 503 three times; provider raises `LLMNetworkError` with code L002
    - Backoff timing follows `LLMConfig.RETRY_BACKOFF_BASE_SECONDS * 2 ** attempt` (use a mock clock)
  - **`complete()` 429 NOT retried:**
    - Mock returns 429 once; provider raises `LLMRateLimited` with code L004 immediately (no retry)
  - **`complete()` 4xx (other):**
    - Mock returns 401; provider raises `LLMConfigError` with code L001 (auth)
    - Mock returns 400; provider raises `LLMResponseError` with code L003
  - **`complete()` timeout:**
    - Mock raises `requests.Timeout`; provider raises `LLMTimeoutError` with code L005
  - **`complete()` connection error:**
    - Mock raises `requests.ConnectionError`; provider raises `LLMNetworkError` with code L002
  - **`complete()` malformed response:**
    - Mock returns 200 with non-JSON body; provider raises `LLMResponseError`
    - Mock returns 200 with JSON missing `choices` key; provider raises `LLMResponseError`
  - **Logging hygiene:**
    - On error, captured log records do NOT contain the API key (use `caplog`)
- [x] Implement `DeepSeekProvider`:
  - Endpoint: `https://api.deepseek.com/v1/chat/completions`
  - Read `os.environ.get("DEEPSEEK_API_KEY")` inside `complete()`, raise `LLMConfigError` if missing/empty
  - Build request body from `messages`, falling back to `LLMConfig` defaults for unset kwargs
  - `requests.post(endpoint, json=body, headers=headers, timeout=(LLMConfig.CONNECT_TIMEOUT_SECONDS, timeout_seconds or LLMConfig.DEFAULT_TIMEOUT_SECONDS))`
  - Retry loop: catch `requests.Timeout` → raise `LLMTimeoutError`; catch `requests.ConnectionError`/`requests.SSLError` → raise `LLMNetworkError`; check `cancel_token` between retries
  - Status handling: 200 → parse; 429 → `LLMRateLimited`; 401/403 → `LLMConfigError`; other 4xx → `LLMResponseError`; 5xx → retry up to `LLMConfig.MAX_RETRIES_5XX`, then `LLMNetworkError`
  - Parse: extract `text` from `choices[0].message.content`, `finish_reason` from `choices[0].finish_reason` (map to enum), `usage.prompt_tokens/completion_tokens/total_tokens`, `model` from response, `request_id` from `id` field if present
  - Compute `latency_seconds` via `time.monotonic()` around the request
  - Override `__repr__` to return `"DeepSeekProvider(key=<REDACTED>)"`
- [x] Run tests, confirm all pass

**Notes:**

### Task 4.4: Auto-register DeepSeek in factory [Simple]
**File:** `game/services/llm/__init__.py`, `game/services/llm/deepseek.py`
**Tests:** `pytest tests/unit/services/llm/test_factory.py`

- [x] At the bottom of `deepseek.py`, register: `register_provider('deepseek', DeepSeekProvider)`
- [x] Update `__init__.py` to import deepseek module (so the registration runs): `from game.services.llm import deepseek  # noqa: F401`
- [x] Add a factory test: `LLMProviderFactory.create('deepseek')` returns a `DeepSeekProvider` instance (with mock env var set)
- [x] Add a factory test: with env var unset, `create('deepseek')` returns `None`

**Notes:**

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] ~12 new tests in `test_deepseek.py` + the `_block_real_http` test
- [x] `pytest tests/unit/services/llm/` — all green
- [x] No real HTTP calls escape any test (verified by `_block_real_http`)
- [x] No baseline regression
- [x] Update status at top of this file to `Complete`
- [x] Update `plan.md` phase table row to `Complete`
- [x] Update `plan.md` Current State to point to Phase 5

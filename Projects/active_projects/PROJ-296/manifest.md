# PROJ-296 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/core/exceptions.py` | Production | 1 | Add `LLMException` branch + 6 sub-classes |
| `game/core/error_codes.py` | Production | 1 | Add `L001`-`L006` codes to `ErrorCode` enum |
| `game/core/__init__.py` | Production | 1 | Export new exception classes |
| `game/core/config.py` | Production | 2 | Add `LLMConfig` class |
| `game/services/__init__.py` | Production | 2 | NEW package marker (one-line docstring) |
| `game/services/llm/__init__.py` | Production | 2, 3, 5, 6 | NEW; populated incrementally across phases |
| `game/services/llm/types.py` | Production | 2 | NEW — `Role`, `FinishReason`, `Message`, `TokenUsage`, `CompletionResult` |
| `game/services/llm/provider.py` | Production | 2 | NEW — `LLMProvider` Protocol |
| `game/services/llm/factory.py` | Production | 3 | NEW — `LLMProviderFactory`, `register_provider`, `_PROVIDERS` registry |
| `game/services/llm/deepseek.py` | Production | 4 | NEW — `DeepSeekProvider` concrete implementation |
| `game/services/llm/background.py` | Production | 5 | NEW — `LLMBackgroundCall`, `CallStatus`, `shutdown_all_calls` |
| `game/app.py` | Production | 5 | Add `shutdown_all_calls()` call before `pygame.quit()` |
| `game/context.py` | Production | 6 | 5 specific edits to `__init__`, `create_production`, `create_test` |
| `requirements.txt` | Build | 4 | Add `requests>=2.31.0` |
| `tests/conftest.py` | Test | 4 | Add session-scoped autouse `_block_real_http` fixture |
| `tests/unit/services/__init__.py` | Test | 2 | NEW package marker |
| `tests/unit/services/llm/__init__.py` | Test | 2 | NEW package marker |
| `tests/unit/services/llm/conftest.py` | Test | 3 | NEW — `_StubProvider`, `stub_llm_provider`, `mock_llm_provider`, `reset_llm_default_provider` fixtures |
| `tests/unit/services/llm/test_package_imports.py` | Test | 2 | NEW — smoke import test |
| `tests/unit/services/llm/test_types.py` | Test | 2 | NEW — DTO tests (~10 tests) |
| `tests/unit/services/llm/test_provider_protocol.py` | Test | 2 | NEW — Protocol tests (~3 tests) |
| `tests/unit/services/llm/test_factory.py` | Test | 3, 4 | NEW — Factory dispatch tests (~6 tests + DeepSeek registration) |
| `tests/unit/services/llm/test_deepseek.py` | Test | 4 | NEW — DeepSeek provider tests (~12 tests, all HTTP-mocked) |
| `tests/unit/services/llm/test_background.py` | Test | 5 | NEW — Threading helper tests (~13 tests) |
| `tests/unit/services/llm/test_defaults.py` | Test | 6 | NEW — Module-level accessor tests (~3 tests) |
| `tests/unit/core/test_exceptions.py` | Test | 1 | Extend with LLM branch tests (~7 tests) |
| `tests/unit/core/test_error_codes.py` | Test | 1 | Extend with `L*` code tests (~3 tests) |
| `tests/unit/core/test_config.py` | Test | 2 | Extend with `LLMConfig` tests (~2 tests) |
| `tests/unit/core/test_application_context.py` | Test | 6 | Extend with LLM provider field tests (~3 tests) |
| `tests/regression/test_services_layer_rule.py` | Test | 7 | NEW — enforce `services/` layer dep rule |
| `docs/01_ARCHITECTURE.md` | Docs | 7 | Add `services/` layer to diagram, dep rules, package map |
| `docs/02_PATTERNS.md` | Docs | 7 | Add Pattern #28 "Background Service Call" |
| `docs/04_SERVICES.md` | Docs | 7 | Add LLM Service section |
| `docs/05_ERROR_HANDLING.md` | Docs | 7 | Add `LLMException` branch + `L*` codes |

## Summary

- **Production new:** 8 files (1 package marker + 5 LLM modules + `services/__init__.py` + `app.py` edit)
- **Production modified:** 5 files (`exceptions`, `error_codes`, `core/__init__`, `config`, `context`)
- **Tests new:** 11 files
- **Tests modified:** 5 files (`conftest`, `test_exceptions`, `test_error_codes`, `test_config`, `test_application_context`)
- **Docs modified:** 4 files
- **Build:** 1 file (`requirements.txt`)

**Total: ~34 files touched.**

# ProviderFactory Consolidation (DUP-X-02) + Phase 2 Superseded Marker Verification

**Review:** agent_provider_factory_phase2
**Date:** 2026-05-09
**Scope:** PROJ-380 audit-shrink cleanup — Phase 2 verification of DUP-X-02 consolidation and PROJ-384 `_static` marker.

---

## Item A: DUP-X-02 ProviderFactory Consolidation

### Reviewed Files

| File | Lines | Role |
|------|-------|------|
| `game/services/provider_factory.py` | 87 | Shared `resolve_provider` base (new, PROJ-380) |
| `game/services/llm/factory.py` | 79 | LLM provider factory consumer |
| `game/ui/services/image/factory.py` | 71 | Image provider factory consumer |

---

## Findings

### FND-001 — Genuine delegation confirmed (INFO, Item A Q1)

Both consumers genuinely delegate to the shared `resolve_provider` function; neither is a renamed internal class.

- **`game/services/llm/factory.py:68`**: `LLMProviderFactory.create()` calls `resolve_provider(name, providers=_PROVIDERS, env_var="LLM_PROVIDER", default="deepseek", config_error_cls=LLMConfigError, ...)` — a direct delegation with 7 keyword arguments.
- **`game/ui/services/image/factory.py:60`**: `ImageProviderFactory.create()` calls `resolve_provider(name, providers=_PROVIDERS, env_var="IMAGE_PROVIDER", default="openai", config_error_cls=ImageConfigError, ...)` — identical delegation shape.

The pre-duplication logic (env-var read, dict lookup, `config_error_cls` raise, deferred-validation `try/except`, `None` return) existed in both factories and has been fully extracted. No residual copy of that logic remains in either consumer. The `PROVIDERS` dict and `register_*` function stay per-factory — these are domain-specific registries, not duplicated behavior.

**Verdict:** PASS — delegation is genuine.

---

### FND-002 — Shared base captures actual behavior, not just type hints (INFO, Item A Q2)

The shared `resolve_provider` function at `game/services/provider_factory.py:30-84` contains concrete behavioral logic:

| Line(s) | Behavior |
|---------|----------|
| 65-66 | `os.environ.get(env_var, default)` — env-var resolution with default fallback |
| 68-69 | `providers.get(name)` — dict-based provider lookup |
| 70-78 | `raise config_error_cls(...)` — config error with `code=` and `context=` dict |
| 80-84 | `try: return provider_cls() / except config_error_cls: return None` — deferred-validation pattern |

The function's signature is parameterized over 7 inputs (`name`, `providers`, `env_var`, `default`, `config_error_cls`, `error_code`, `label`), making it generic across provider domains without coupling to `LLMProvider`, `ImageProvider`, or any concrete type beyond `T = TypeVar("T")`.

The `T = TypeVar("T")` is used for return-type inference only; no `T` constraints or protocols tie it to a specific layer.

**Verdict:** PASS — shared base contains real behavior.

---

### FND-003 — Zero layer violations (INFO, Item A Q3)

`game/services/provider_factory.py` imports checked against the architecture layers (Core → Services → UI):

| Import | Layer | Direction |
|--------|-------|-----------|
| `from __future__ import annotations` | stdlib | n/a |
| `import os` | stdlib | n/a |
| `from typing import Optional, TypeVar` | stdlib | n/a |
| `from game.core.exceptions import GameException` | Core | Core ← Services — **allowed** |

No import from `game/ui/`, `game/engine/`, `game/simulation/`, `game/research/`, `game/strategy/`, or `game/ai/`. The module sits in the Services layer and only references the Core layer (permitted by the architecture: _Services depends on Core only_).

The reverse dependency (`game/ui/services/image/factory.py` importing `game.services.provider_factory`) is also clean: UI depends on Services (permitted).

**Verdict:** PASS — no layer violations.

---

### FND-004 — No shim introduced (INFO, Item A Q4)

Per `docs/03_CONVENTIONS.md` and AGENTS.md Rule 3:

> "No compatibility shims, fallback systems, monkey patches, or duplicate logic."

`game/services/provider_factory.py` is a **new shared utility module**, not a shim. It does not:

- Re-export symbols under old names or provide aliases
- Wrap legacy implementations behind a compatibility layer
- Contain `deprecated` markers or migration-guard code
- Duplicate the old factory bodies (the old bodies were deleted in favor of delegation)

Both `LLMProviderFactory.create()` and `ImageProviderFactory.create()` are thin **delegating facades** — they retain their public API surface (`create(name: str | None) -> LLMProvider | None` and `create(name: str | None) -> ImageProvider | None`) but the implementation is a single call to `resolve_provider`. This is consistent with the existing Facade/Delegate pattern documented in `docs/02_PATTERNS.md`.

**Verdict:** PASS — no shim.

---

## Item B: Phase 2 Superseded Marker (PROJ-384 `_static`)

### Verification

```bash
grep -n "_static" game/simulation/components/modifier_manager.py
# (no output — 0 hits)
```

A broader grep for `PROJ-384` across `game/simulation/components/` also returned 0 hits, confirming no dangling PROJ-384 references.

### FND-005 — PROJ-384 `_static` marker verified (INFO, Item B)

The grep for `_static` in `game/simulation/components/modifier_manager.py` returned **0 hits**. All `_static` references targeted by PROJ-384 have been fully removed. The superseded marker is correct.

**Verdict:** PASS — deletion is complete.

---

## Summary

| ID | Severity | Category | Status |
|----|----------|----------|--------|
| FND-001 | INFO | DUP-X-02 delegation | PASS |
| FND-002 | INFO | Shared behavior depth | PASS |
| FND-003 | INFO | Layer isolation | PASS |
| FND-004 | INFO | Shim detection | PASS |
| FND-005 | INFO | PROJ-384 `_static` marker | PASS |

**Zero CRITICAL, MAJOR, or MINOR findings.** Both the DUP-X-02 consolidation and the PROJ-384 superseded marker are clean and conform to all applicable conventions.

### Follow-up (non-blocking)

- The `LLMProviderFactory` and `ImageProviderFactory` classes have been reduced to thin static-method wrappers around `resolve_provider`. If these classes accumulate no further responsibilities, they could be considered for future removal in favor of direct `resolve_provider` calls with the appropriate domain constants (PROJ-380 follow-up). This is deferred by the current consolidation scope.

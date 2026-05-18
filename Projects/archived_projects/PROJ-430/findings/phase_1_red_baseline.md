# Phase 1 — Red Baseline (PROJ-430 / TD-08)

Generated 2026-05-17 against `proj/PROJ-430/main` at Phase 1 commit boundary.

## Test files authored

1. `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py` — rewritten in place. Old `PUBLIC_METHODS`/`PROTECTED_ATTRS` constants replaced with `PUBLIC_TOP_LEVEL`, `PUBLIC_GROUP_ACCESSORS`, `GROUP_CONTRACT`, `LEGACY_FLAT_METHODS`, `LEGACY_CACHE_ATTRS`.
2. `tests/unit/strategy/facade/test_facade_grouped_namespaces.py` — new file. Behavior-parity per namespace.

## Red summary

```
pytest tests/unit/strategy/facade/test_strategy_session_facade_public_api.py \
       tests/unit/strategy/facade/test_facade_grouped_namespaces.py -q
```

43 failures, 0 passed. Failure categories:

- `TestTopLevelSurface::test_only_target_top_level_callables_exist` — top-level surface still has 68 callables.
- `TestTopLevelSurface::test_only_target_top_level_attrs_exist` — only `facade_state` is currently a top-level non-callable attribute; the 9 grouped accessors do not exist.
- `TestTopLevelSurface::test_no_legacy_flat_methods` — all 36 dispatch helpers + 32 flat read methods still exist as top-level facade methods.
- `TestGroupedNamespaces::test_grouped_namespaces_expose_expected_methods[*]` — 8 parametrized failures: groups don't exist.
- `TestGroupedNamespaces::test_commands_namespace_strips_dispatch_prefix` — `commands` accessor missing.
- `TestLegacyCacheAttrsRemoved::test_legacy_cache_attr_not_settable[*]` — 6 parametrized failures: each of the 6 cache fields round-trips through the legacy `@property` forwarder.
- `test_facade_grouped_namespaces.py` (29 tests) — all red because the namespaces do not exist yet.

## Target green transitions

| Test | Goes green in |
|---|---|
| `test_only_target_top_level_callables_exist` | Phase 5 (deletion of legacy flat methods) |
| `test_only_target_top_level_attrs_exist` | Phase 2 (grouped accessors added; the *exactness* of the set goes green only after Phase 5 deletes the cache forwarders' property descriptors) |
| `test_no_legacy_flat_methods` | Phase 5 |
| `test_grouped_namespaces_expose_expected_methods` | Phase 2 |
| `test_commands_namespace_strips_dispatch_prefix` | Phase 2 |
| `test_legacy_cache_attr_not_settable` | Phase 5 |
| `test_facade_grouped_namespaces.py` (whole file) | Phase 2 (modulo Phase 4 cache attribute migration which doesn't affect this file) |

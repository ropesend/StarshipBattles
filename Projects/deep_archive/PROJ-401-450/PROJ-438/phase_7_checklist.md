# Phase 7: Order persistence + metadata-driven serialization convergence

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-438 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** Phase 6 (issuer-aware execution contract landed)
**Objective:** Make order persistence derive more directly from live executable metadata. Revisit `CommandSpec.serializer_codec`, `Order.to_dict()`, `OrderSerializer`, and the post-load rebinding. Default stance from D3 LOCKED: treat `IMPLICIT_ACTION_ORDER_TYPES`, mission decomposition, and the `JOIN_FLEET` instant path as acceptable specialized behavior unless the implementation audit proves blocking leakage.

**Resolution (2026-05-18):** Phase 7 is a **tight metadata-surfacing pass**, not a wholesale serializer rewrite. The audit found: (a) every `CommandSpec.serializer_codec` value (`'hex_coord'`, `'fleet_ref'`, `'planet_ref'`, `'transfer'`, `'warp_params'`, `'ship_id_list'`, `'dict'`) already matches the discriminator vocabulary `OrderSerializer._deserialize_target` understands; (b) the field was previously documentation-only — no lookup method existed; (c) `Order.to_dict()`'s inline `isinstance`/`OrderType` branching works correctly and does not *block* anything per D3. The Phase 7 work product surfaces the existing codec metadata through the live `OrderMetadataView` lookup pattern and pins the vocabulary consistency so a future project can flip `Order.to_dict()` to dispatch via the codec lookup with confidence.

---

## Tasks

### Task 7.1: Failing TDD test for metadata-driven codec lookup
**Files:** `tests/unit/strategy/engine/test_order_persistence_from_metadata.py` (new)

- [x] Pin `CommandRegistry.serializer_codec_for(order_type)` API existence + correctness on three representative OrderTypes (MOVE → `'hex_coord'`, TRANSFER → `'transfer'`, IMPLODE_PLANET → `'planet_ref'`).
- [x] Pin `OrderMetadataView.serializer_codec_for(order_type)` API existence and that it returns the same value as the underlying registry.
- [x] Add a **vocabulary-consistency** ratchet: every distinct `CommandSpec.serializer_codec` value in the seeded registry must be in `KNOWN_DESERIALIZABLE_CODECS` (the set that `OrderSerializer._deserialize_target` already understands, plus the special-case `'colonize_params'` and `'raw'`). A new codec added without matching deserializer plumbing breaks this test.
- [x] Confirm 6 tests fail before any production change.

### Task 7.2: Add the metadata lookup
**Files:** `game/strategy/engine/commands/registry.py`, `game/strategy/engine/commands/order_metadata_view.py`

- [x] Add `CommandRegistry.serializer_codec_for(order_type)` — scans `_specs.values()` for a matching `spec.order_type == order_type` with a non-None `serializer_codec`; returns the first such codec or None.
- [x] Add `OrderMetadataView.serializer_codec_for(order_type)` — delegates to the lazy registry.
- [x] Confirm Task 7.1 tests: 7/7 green.

### Task 7.3: Document the future-direction migration target on `Order.to_dict()`
**Files:** `game/strategy/data/order_types.py`

- [x] Add a comment in `Order.to_dict()` explaining: the inline `isinstance`/`OrderType` branching is the current path; `order_metadata.serializer_codec_for(...)` already exposes the matching codec names; a future project may flip this method to dispatch via the codec lookup. The vocabulary-consistency test in `test_order_persistence_from_metadata.py` pins the safety net for that flip.

### Task 7.4 (intentionally skipped — D3 LOCKED)
- [x] `JOIN_FLEET`, mission decomposition, `IMPLICIT_ACTION_ORDER_TYPES`: per D3 LOCKED default, these are acceptable specialized behavior. Audit confirms no blocking leakage. No work product.

### Task 7.5: Sweep + sharded suite
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Run the canonical sharded suite green.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `python Tools/test_sharded/test_sharded.py` green (no NEW failures vs. Phase 0 baseline)
- [x] Game still runnable / savable / loadable (no behavior change — the new lookup is additive; `Order.to_dict()` is untouched)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 8 (HARD STOP — surface before starting)
- [x] `python Projects/scripts/validate_phase.py PROJ-438 7` passes

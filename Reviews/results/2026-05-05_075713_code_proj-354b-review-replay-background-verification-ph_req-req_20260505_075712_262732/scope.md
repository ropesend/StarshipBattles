# Review Scope: PROJ-354B Review: Replay Background Verification (Phases 1-4)
**Type:** code (delegated by Claude Code)
**Request ID:** req_20260505_075712_262732
**Scope:** 
- `game/simulation/replay/replay_verifier.py`
- `game/strategy/services/replay_verification_sidecar.py`
- `game/strategy/services/replay_verification_coordinator.py`
- `game/strategy/services/replay_store.py` (listener API + sidecar lifecycle)
- `game/strategy/services/replay_resolver.py` (verification_status field)
- Tests under `tests/unit/simulation/replay/` and `tests/unit/strategy/services/`

**Instructions:**
- Verify the pure verifier is layer-clean (only stdlib + simulation/replay DTOs)
- Audit `compute_outcome_diff` correctness
- Confirm cap-25 truncation logic is correct and `total_diff_count` is accurate
- Verify sidecar atomic write/read and lifecycle cleanup
- Examine listener wiring on ReplayStore (per-listener try/except isolation, fire timing)
- Audit the coordinator: single FIFO worker, condition-variable queue, `shutdown_all_coordinators`
- Race condition R6 (sidecar/replay race) — assess residual risk

**Context:** PROJ-354B Phases 1-4. Phases 5-6 deferred.

**Note:** `game/simulation/replay/replay_settings.py` listed in scope does not exist; `ReplaySettings` is defined in `game/strategy/services/replay_store.py`.

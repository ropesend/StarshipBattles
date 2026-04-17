# Clean-Sheet Migration — Skeptical Audit (CLAUDE.md Rule 3)

## Verdict
**Material violations requiring rework.** The project shipped the 5 stated acceptance criteria and 28 regression guards, but it did so by preserving several compat shims that CLAUDE.md Rule 3 + the System Migration Policy explicitly forbid. Multiple decisions are self-flagged in the checklists as "scope trim" or "legacy retained" with no follow-up ticket, meaning they will rot into permanent fixtures. The worst offender is a duplicated engine-plumbing block copy-pasted into three production call sites because the controller path was never routed through `start_engine_from_spec`.

## Findings

### Finding: `engine.boundary`/`engine.modifier_stack` plumbing duplicated across three production call sites
**Severity:** Critical
**Rule violated:** Rule 3 (Clean-Sheet) + Long-Term Quality ("Delegate to existing logic over reimplementing it")
**Location:** `game/app.py:572-574`, `game/ui/screens/test_lab/screen.py:437-439`, `combat_lab/services/test_execution_service.py:80-82` — identical to `game/simulation/battle_runner.py:150-152`
**What's wrong:** `start_engine_from_spec` already contains the `if spec.boundary is not None: engine.boundary = ...; engine.modifier_stack = spec.modifier_stack` block. The visual-mode path uses `BattleService.create_battle` to construct the engine and then every caller reimplements the spec→engine plumbing by hand. If a future field (e.g., per-team AI policy, new arena-level effect) is added to BattleSpec, `run_battle` gets it for free but all three visual paths will silently drop it.
**Evidence:** `phase_4_checklist.md:43` explicitly admits "did NOT route through `start_engine_from_spec` from within `configure()` as originally scoped. That would be a much deeper refactor." That is the definition of a scope-trim fig leaf — it's the design delta that made the closure "quick."
**Recommended fix:** Either (a) have `BattleController.configure(config, spec)` call `start_engine_from_spec` internally (replacing the `BattleService.create_battle` + manual engine.boundary step) and then take over with `add_ships` / `start()` + per-frame update, or (b) introduce a single `start_engine_from_spec_for_controller(spec, service)` helper so all three call sites reduce to one line. Option (a) is the true clean-sheet solution.

### Finding: `BattleController.set_spec` is a public method that exists only because `configure(spec=...)` was not tightened
**Severity:** High
**Rule violated:** Rule 3 (Clean-Sheet) — "Optional parameters that should be required"
**Location:** `game/simulation/battle_controller.py:273-280`, called from `configure` at line 138
**What's wrong:** `configure(config, spec=None)` is declared optional. When the caller passes a spec, `configure` internally calls `self.set_spec(spec)`. `set_spec` exists as a standalone public method solely so tests and the `BattleScreen.start` bypass can continue to work. The regression guard at `tests/unit/simulation/test_unified_entry_guard.py:248` actively protects `set_spec`'s existence as an "internal API" — but it's `public`, callable from anywhere, and duplicates the effect of the configure kwarg.
**Evidence:** `phase_4_checklist.md:55` says "spec remains optional on configure() — required in spirit (all production paths pass it) but kept optional in signature to preserve the legacy test-convenience BattleScreen.start bypass without breaking ~60 unit tests." This admits the signature is a workaround for test legacy, not a design choice.
**Recommended fix:** Make `spec` required on `configure`. Migrate the ~60 pre-spec unit tests to construct a minimal `BattleSpec` via a test fixture (which already exists in `tests/fixtures/battle.py`). Delete `set_spec` and the guard that protects it.

### Finding: `BattleScreen.start(team0, team1)` + `_build_fallback_outcome` are a classic "retained for tests" compat shim
**Severity:** High
**Rule violated:** Rule 3 + System Migration Policy ("ERADICATE the old system completely")
**Location:** `game/ui/screens/battle_screen.py:227` (`start`), lines 474-486 (`_get_or_build_outcome`), lines 488+ (`_build_fallback_outcome`)
**What's wrong:** The "test-convenience" `start(team0, team1)` method still exists in production code. Its existence then forces a second compat shim (`_build_fallback_outcome`) whose only purpose is to synthesize a `BattleOutcome` for callers who didn't build a spec. Two layers of shims to preserve one legacy entry point.
**Evidence:** Code comment at `battle_screen.py:478` explicitly calls this out: "fallback: if the controller was configured without a spec (legacy `BattleScreen.start(team0, team1)` path), there's no outcome to pull. Build a minimal `BattleOutcome` from the live engine." `NEXT_AGENT_PROMPT.md:212` calls this "intentional legacy support for existing tests." The acceptance audit literally says "Fallback path emits a synthesized outcome → criterion met" — it is papering over a bypass by observing that the bypass still produces a DTO.
**Recommended fix:** Delete `BattleScreen.start`. Migrate its callers (tests — per grep, only `tests/unit/combat/test_battle_setup_logic.py` and a few others) to compile a `BattleSpec` via `build_test_battle_spec` helper. Delete `_build_fallback_outcome` and `_get_or_build_outcome`. One code path, one way to enter a battle.

### Finding: `battle_config.py` re-exports `ReturnDestination` for backwards compat — textbook System Migration Policy violation
**Severity:** High
**Rule violated:** System Migration Policy ("NEVER keep backward compatibility layers 'just in case'")
**Location:** `game/simulation/battle_config.py:11-14` (docstring), line 25 (import), propagated to 5 production importers
**What's wrong:** The module's own docstring admits this is a compat shim: "This module re-exports it only for backwards compatibility during the transition — new callers should import from `game.core.return_destination` directly." Five production files still import from the old location (`battle_screen.py:242`, `test_lab/screen.py:415`, `test_execution_service.py:61`, `app.py` indirectly, `test_scene_protocol.py:89`). The "transition" never happened — the grep sweep was scheduled in the same project but the re-export was not removed.
**Evidence:** `phase_5_checklist.md:38` closes Task 5.2 with "Future migration sweep could update all importers to use `game.core.return_destination` directly and remove the re-export." That's a TODO-as-decision — no ticket filed, no follow-up scheduled.
**Recommended fix:** sed-replace the 5 importers to `from game.core.return_destination import ReturnDestination` in one commit and delete the re-export from `battle_config.py`. This is a 10-minute task that the project left hanging.

### Finding: `ComponentStateSpec.is_active` is half-wired — read path exists, write path does not
**Severity:** Medium
**Rule violated:** Rule 3 ("designing for hypothetical future requirements" anti-pattern)
**Location:** `game/simulation/battle_spec.py:114`, consumers at `battle_runner.py:498` (read), `strategy/combat/spec_compiler.py:282` (attempted write)
**What's wrong:** Phase 5.5's audit admits: "Strategy's `_spec_components_from_instance` in `game/strategy/combat/spec_compiler.py` is the author; if it doesn't populate `is_active` today, that's a minor compiler omission." Since the read side unconditionally emits `is_active`, the outcome always carries the value (typically `True` by default) but the data is not truly driven through the round-trip — it's the field's *default*, not the ship's actual state, that ends up in the outcome for non-strategy battles.
**Evidence:** `phase_5_checklist.md:93` says "flag for later compiler audit" with no ticket filed.
**Recommended fix:** Either finish the round-trip (populate from live `comp.is_active` in every compiler and thread it through the engine's disable/enable calls), or delete the field and have the engine compute it from damage state. A field that only round-trips a default value is not carrying information — it's a fossil.

### Finding: `AIPolicy` is a zero-field dataclass — textbook "scaffolding for future work" anti-pattern
**Severity:** Medium
**Rule violated:** Rule 3 ("Unused architectural scaffolding")
**Location:** `game/simulation/battle_spec.py:67-79`
**What's wrong:** The class has one statement — `pass`. The docstring says "Reserved for future fields (aggression bias, reserve-commit threshold, flagship-preservation priority, etc.). Kept empty in Phase 1 so specs can be constructed without guessing defaults." This is designing-for-hypothetical-requirements, forbidden by Rule 3. It ripples into `TeamSpec.ai_policy`, which every compiler must set to `AIPolicy()` for no effect. Grep for `ai_policy.` returns **zero attribute access sites** across the codebase — no one reads any field from it because it has no fields.
**Evidence:** `phase_5_checklist.md:91` "Keep" with no consumer and no ticket to add one.
**Recommended fix:** Delete `AIPolicy` and the `ai_policy` field on `TeamSpec`. Add it back when a concrete consumer exists. Follow YAGNI.

### Finding: `TaskForceOutcome` carries only `task_force_id` — placeholder DTO kept "in case"
**Severity:** Low (but should be treated as paired with AIPolicy)
**Rule violated:** Rule 3
**Location:** `game/simulation/battle_outcome.py:155-160`
**What's wrong:** Identical pattern to `AIPolicy`. The docstring promises "richer fields (survivors, casualties, resolved formations) land in later phases." There is no later-phase ticket. The tuple lives on `TeamOutcome.fleet_hierarchy` purely to satisfy a shape contract no one reads. Grep for `fleet_hierarchy` in production (not tests) returns only the construction sites in compilers and `battle_runner.py`. No consumer reads it back.
**Recommended fix:** Delete `TaskForceOutcome` and `TeamOutcome.fleet_hierarchy`. Reintroduce when a consumer needs it.

### Finding: `UnboundedRegion.closest_edge_point` raises NotImplementedError — API design leaks into runtime
**Severity:** Medium
**Rule violated:** Rule 3 ("Propose a larger refactor if the right fix requires it")
**Location:** `game/simulation/combat/boundary.py:188-193`
**What's wrong:** The `BoundaryRegion` protocol promises `closest_edge_point(pos) -> Vector2`. `UnboundedRegion` throws at runtime. Every caller must either (a) isinstance-check first (which `RetreatManager.request_retreat` does at line 105, a per-call type-dispatch that Rule 3 forbids) or (b) use `distance_to_edge == math.inf` as a sentinel. This is a bandaid around a type-model flaw — the protocol should be `BoundedRegion` (has edges) and `Region` (parent, might be unbounded), with `closest_edge_point` declared only on the bounded subtype.
**Evidence:** Protocol docstring admits this: "Unbounded regions have no edge — `UnboundedRegion.closest_edge_point` raises `NotImplementedError`."
**Recommended fix:** Split the protocol into `Region` (contains + closest_inside_point) and `BoundedRegion(Region)` (adds closest_edge_point + distance_to_edge). `RetreatManager` takes `Optional[BoundedRegion]` for edge retreat; the `isinstance(..., UnboundedRegion)` branch disappears.

### Finding: `RetreatManager` in `load_state` defaults to `UnboundedRegion` forever — silent loss of retreat behavior
**Severity:** Medium
**Rule violated:** Rule 3 (workaround pretending to be design)
**Location:** `game/simulation/battle_controller.py:478-483`
**What's wrong:** When loading a saved battle, the controller has no spec, so it defaults boundary to `UnboundedRegion`. Edge retreat is silently disabled on every restored battle. The comment justifies this with "saves are disposable (CLAUDE.md)" — but that argument only covers not writing a migration shim; it doesn't justify silently degrading behavior when a save IS loaded. CLAUDE.md says old saves get discarded, not that live loads should lose behavior.
**Evidence:** Code comment at lines 479-481.
**Recommended fix:** Either persist the boundary inside `BattleState` (the clean-sheet choice — battle state genuinely needs it) or remove `load_state` entirely if saves truly are disposable (then the feature shouldn't exist at all). Picking neither and silently losing behavior is the worst of both worlds.

### Finding: `FORBIDDEN_FIELDS` regression guard proliferation
**Severity:** Low
**Rule violated:** Long-Term Quality (smells of unboundedly-growing guards)
**Location:** `tests/unit/simulation/test_battle_config.py:70-79`; also forbidden-legacy-comments / no-setup-in-templates / no-engine-ref-closure guards in `test_unified_entry_guard.py`
**What's wrong:** The FORBIDDEN_FIELDS set starts at 8 entries after two projects. Each field deletion adds one more. This is useful for a brief transition but will grow unboundedly across future projects and becomes a ledger of past sins instead of a specification of current design. Once the code is clean for 6 months, these are dead weight — they guard against a regression no one is actively attempting.
**Recommended fix:** Tag each FORBIDDEN_FIELDS entry with a removal date (e.g., "remove after 2026-10-01") so they get pruned. Same policy for the guard-test classes in `test_unified_entry_guard.py`.

### Finding: Task 6.5 (end-to-end storm/modifier test) deferred to PROJ-271 Phase 4 — fig leaf
**Severity:** Medium
**Rule violated:** Rule 1 (TDD) + Rule 3 (don't leave it half-done)
**Location:** `plan.md:21-23` + `phase_6_checklist.md`
**What's wrong:** Phase 6 Track A claims to restore the strategic-modifier battle math regression from PROJ-269. Every sub-task has unit coverage, but the end-to-end test that actually proves the restored math affects a full simulated battle is deferred to the NEXT project. Without that test, the claim "storm shield interference applies correctly again" rests on implementation inspection, not observed behavior.
**Evidence:** `plan.md:21` "Complete (Track A; 6.5 end-to-end test deferred to PROJ-271 Phase 4)".
**Recommended fix:** Write the end-to-end test now (compile a spec with a storm, run `run_battle`, measure shield damage with vs without). Estimated 1-2 hours. Deferring a 1-2 hour test to a future project is exactly the "later never comes" pattern Rule 2 warns about.

### Finding: Task 7.3 "intentionally deferred — low ROI" without a filed follow-up
**Severity:** Low
**Rule violated:** Rule 3 (shrug as design justification)
**Location:** `phase_7_checklist.md:42-51`
**What's wrong:** The checklist self-flags the task and closes it. The stated reason ("no current test requires the real-spec fixture") is circular — no test requires it because the fixture doesn't exist. The shim fixture's `teams=()` short-circuit is then justified with "not a bug — intentional shortcut." That is the voice of a workaround explaining itself.
**Recommended fix:** Either delete the shim fixture entirely (force its users to use the real one), or write the real-spec fixture and migrate the callers. Leaving the shim is cheap; leaving a "deferred" checkbox is free and accumulates debt.

---

## Summary of required rework

1. Collapse the three-site duplicated engine-plumbing block by routing `BattleController.configure` through `start_engine_from_spec` (Critical).
2. Make `spec` required on `configure`, migrate the ~60 legacy tests, delete `set_spec` (High).
3. Delete `BattleScreen.start(team0, team1)` + `_build_fallback_outcome` + `_get_or_build_outcome` after migrating the handful of tests that still use it (High).
4. Update the 5 `ReturnDestination` importers and delete the re-export (High — 10-minute task).
5. Complete the `ComponentStateSpec.is_active` write path or delete the field (Medium).
6. Delete `AIPolicy` and `TaskForceOutcome` until a consumer exists (Medium).
7. Split `BoundaryRegion` into `Region` / `BoundedRegion` to eliminate the `NotImplementedError` (Medium).
8. Decide whether `load_state` persists boundary or is deleted — don't silently degrade (Medium).
9. Land the deferred Task 6.5 end-to-end storm test before archiving (Medium).
10. Add sunset dates to `FORBIDDEN_FIELDS` and grep-based guard classes (Low).

The project's "complete" status should be challenged until at least items 1–4 are addressed. The remaining items can fairly be scoped as PROJ-271 or follow-ups, but they must have filed tickets with owners, not closed checkboxes.

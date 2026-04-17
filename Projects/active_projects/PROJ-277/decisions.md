# PROJ-277: Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-16 | Project initialized | User confirmed A/B should be a first-class runner, not an embedded scenario method. |
| 2026-04-16 | A/B runner is a separate service class (ABBattleRunner), not a method on scenarios | Scenarios should be INPUT to the runner, not orchestrators. Matches PROJ-269 architecture: `run_battle` is the single entry; scenarios are compiled to BattleSpec inputs. |
| 2026-04-16 | `validate()` runs in ALL modes including visual-baseline | No silent contract bypass. Visual-baseline is a rendering choice, not a validation gate. The old `_run_validation()` override was a silent violation. |
| 2026-04-16 | `ABBattleOutcome` is a frozen dataclass carrying both (outcome, telemetry) pairs | Eliminates `_baseline_*` attribute stashing and telemetry role-remapping. |
| 2026-04-16 | Baseline and variant produced by separate builder methods (`build_baseline_spec`, `build_variant_spec`) | Explicit per-spec transformation; callers can see what's being compared. Replaces the single `before_run_battle` that had to do both implicitly. |
| 2026-04-16 | Visual-baseline mode still runs BOTH battles but renders only baseline | Preserves the "see the baseline" feature without skipping validation. Rendering is orthogonal to correctness. |
| 2026-04-16 | Independent of PROJ-273/274/275 | No shared production files. Can run in parallel. |
| 2026-04-16 | ComparisonScenario's ship_builder override preserved | Its role-tracking is orthogonal to the A/B refactor. If PROJ-274 lands first, role-tracking can move to the materializer layer — but not a requirement. |

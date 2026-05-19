# Known Issues - Compact Agent Reference

> **Last verified:** 2026-05-19 - SettingsWindow added to the two-stage retrofit list and the stale `tests/fixtures/README.md` warning paragraph removed (PROJ-458 Phase 1 / F-C-016 closure).
> Basis: `docs/known-issues.md`, `AgentCoordination/Scratchpad/reports/known-issues_ALT_compact.md`, and spot-checks of current source paths referenced below. Historical project paths under `Projects/active_projects/PROJ-327` and `Projects/active_projects/PROJ-329A` have moved to archives; treat archived project files as provenance, not current work queues.

This file keeps only current cautions, live contracts, useful workarounds, and stale-reference corrections. It intentionally omits release-note archaeology from PROJ-321..329.

## UI Widget Testability

`tests/fixtures/ui_widget_factory.py` is the canonical widget helper. Use `make_ui_widget(Cls, **kwargs)` for ordinary pygame_gui widgets.

For `pygame_gui.elements.UIWindow` and `StrategyModalWindow` subclasses, follow `docs/02_PATTERNS.md` section 33. New UI classes should prefer Compositional Construction from section 32 instead of adding retrofit seams later.

Two-stage UIWindow construction contract:

- Stage 1 runs before the bypass guard and must stay cheap and pure Python: store state, wire `Default{Foo}DelegateFactory`, install `{Foo}Delegates`, and accept/inject a UI-builder seam.
- Do not construct pygame_gui elements, call `self.get_container()`, or perform asset I/O before the bypass guard.
- The bypass guard belongs after Stage 1 and before the UIWindow shell: `if getattr(type(self), "bypass_init", False): return`.
- Stage 2 calls `super().__init__(...)` and builds the heavyweight widget tree through the production UI builder.
- Tests scope the bypass with `with bypass_init(Cls):`, never with bare `Cls.bypass_init = True`.
- The guard must check `type(self)`, not the class that defines `__init__`, so inherited `StrategyModalWindow.__init__` honors flags set on concrete subclasses.
- Audit subclasses that explicitly call `pygame_gui.elements.UIWindow.__init__(self, ...)`; the normal guard only protects the path that checks it before the parent init.
- Legacy `__new__` bypass helpers can be removed once the target class has the two-stage shape and tests use the factory/context-manager path.

Fixture naming convention:

- Production default: `Default{Foo}DelegateFactory` plus `{Foo}Delegates`.
- Test UI builders: `Null{Foo}UiBuilder` for silent no-op construction and `Mock{Foo}UiBuilder` when tests assert builder calls.
- Existing examples live under `tests/fixtures/*_ui_builder.py`.

Production classes already on the two-stage recipe (do not re-retrofit):

- `StrategyModalWindow` (base)
- `RaceSetupScreen`, `NewGameSetupScreen`
- `BuildQueueListWindow`, `OrdersWindow`, `FleetReportWindow`, `TransferDialog`
- `SettingsWindow` (PROJ-458 Phase 1)

## LLM Background Calls

`game/services/llm/background.py::LLMBackgroundCall.wait(timeout: float | None = None) -> bool` is the deterministic test hook. Use it instead of polling `status` with `time.sleep()`.

Current contract:

- `wait()` returns `True` only after a terminal state: `DONE`, `ERROR`, or `CANCELLED`.
- `wait()` returns `False` on timeout and returns immediately if the call is already terminal.
- `cancel()` sets the done event for cancel-before-start; `_run()` sets it for worker terminal paths.
- Current code releases the in-flight slot and removes the worker from `_active_workers` before signalling completion, so a `wait()` observer can start another call without racing the concurrent-call cap.
- Tests in `tests/unit/services/llm/test_background.py` should use `assert call.wait(timeout=2.0)` for worker completion.

Residual warning: timing assertions around `elapsed_seconds` can still depend on platform timer resolution. That is separate from the old polling-loop blocker.

## Shared-Test-Helper Non-Issues

Some repeated helpers are intentionally file-local because the setup shapes differ enough that a shared factory would become a switch-heavy builder.

- Superweapon handler tests split execution-path setup from dependency-injection validation setup; five handlers times two contracts does not collapse cleanly.
- `make_mock_ship` variants differ by file: cargo capacity, fuel, display names, facade shape, and other local concerns.
- Do not reconsolidate these without new evidence that the call shapes have converged.

Narrow shared factories remain valid where shapes align:

- `tests/fixtures/cargo_mock_ship.py`
- `tests/fixtures/yard_facility.py`
- `tests/fixtures/mock_planet.py`

Historical evidence moved from `Projects/active_projects/PROJ-327/findings/*` to `Projects/deep_archive/PROJ-301-350/PROJ-327/findings/*`. Do not cite those archived paths as active references.

## Tool Bugs And Workarounds

### Sharded Test Runner Path Escaping - Fixed

File: `Tools/test_sharded/test_sharded.py`

The old known issue said worktree paths like `.claude/worktrees/agent-...` could make the inline shard runner parse `\a` as a bell escape in `--junitxml=...`. Current code now builds:

```python
xml_arg = json.dumps(f"--junitxml={xml_path.as_posix()}")
```

That fixes the stale workaround. The canonical full-suite command remains:

```bash
python Tools/test_sharded/test_sharded.py
```

If this regresses, the fallback from affected worktrees is still:

```bash
python -m pytest tests/
```

### Project Markdown Parser Encoding Crash

File: `Projects/scripts/utils/markdown_parser.py`

Current code still reads markdown with strict UTF-8 (`read_text(encoding='utf-8')`). `python Projects/scripts/project_status.py PROJ-XXX` can therefore crash if a checklist contains a raw Windows cp1252 em dash byte (`0x97`) instead of UTF-8.

One-off repair for an affected file:

```bash
python -c "fp = '<path-to-file>'; raw = open(fp, 'rb').read(); open(fp, 'wb').write(raw.replace(b'\x97', b'\xe2\x80\x94'))"
```

Expected durable fix: read markdown with `encoding='utf-8', errors='replace'`, or add an encoding normalizer before project-status parsing.

## Test Runtime Notes

Do not cite the old suite-level runtime reclaim. The observed sharded-suite delta was inside run-to-run noise.

Verified file-level facts only:

- About 30 ms in `test_virtual_table.py`.
- About 330 ms across `test_ship_io.py` and `test_empire_treasury_panel.py`.
- Remaining runtime pressure is mostly integration tests, the `test_component_definitions.py` validation cluster, and `test_main_integration::test_game_instantiation`.

Useful maintainability patterns from that work:

- Collapse many universal `@patch` decorators into an autouse fixture only when the patch really applies to every test in the scope.
- Rescope mutable mock fixtures only after auditing that no test mutates shared state or call records.
- Use Compositional Construction to replace brittle `__init__` monkey-patching.

## UIWindow Retrofit Boundaries

These are boundaries for future UI testability work, not active tickets.

### `DesignWorkshopScreen`

File: `game/ui/screens/workshop_screen.py`

- `DesignWorkshopScreen` is a bare app-managed screen, not a `UIWindow` or `StrategyModalWindow` subclass.
- It is constructed through the workshop screen factory path.
- The two-stage UIWindow retrofit recipe does not apply; any testability project here needs a separate factory/composition design.

### Planet Target Editors

Files:

- `game/ui/screens/atmosphere_target_editor.py`
- `game/ui/screens/gravity_target_editor.py`
- `game/ui/screens/water_target_editor.py`
- `game/ui/screens/radiation_shield_editor.py`
- Base: `game/ui/screens/planet_target_editor_base.py`

Stale correction: the old source said these had no UI/widget tests. Current tests do cover modal registration, click blocking, and explicit `window_manager` requirements in `tests/integration/ui/test_editor_click_blocking.py` and `tests/unit/ui/screens/test_strategy_modal_window.py`.

Current caution:

- The concrete editors still build widgets directly after `super().__init__(...)` and call `self.get_container()`.
- Do not perform a cleanup-only two-stage retrofit unless it is paired with characterization tests for each editor's slider/buttons/apply/cancel behavior or a scoped planet-target editor batch.
- `PlanetTargetEditor` base has no `__init__`; the shell concern is in concrete subclasses.

### `MoveChoiceWindow`

File: `game/ui/screens/strategy_windows/move_choice_dialog.py`

- `MoveChoiceWindow` has no `__init__` of its own.
- Widget construction happens through `MoveChoiceDialog.show()` after the window class exists.
- The inherited `StrategyModalWindow` bypass shell is sufficient unless future code adds constructor work.

### `SettingsWindow`

File: `game/ui/screens/settings_window.py`

- Raw `pygame_gui.elements.UIWindow` subclass.
- It has registrar/slot tests through `tests/unit/ui/screens/strategy_windows/test_empire_panel_ctrl.py`, but no direct widget characterization tests for its slider/buttons.
- Pair any two-stage retrofit with characterization tests or a confirmed production failure mode.

## Useful References

- `docs/02_PATTERNS.md` section 32: Compositional Construction.
- `docs/02_PATTERNS.md` section 33: UI Widget Test Factory and two-stage UIWindow construction.
- `tests/fixtures/ui_widget_factory.py`: `make_ui_widget` and `bypass_init`.
- `tests/fixtures/cargo_mock_ship.py`, `tests/fixtures/yard_facility.py`, `tests/fixtures/mock_planet.py`: shared factories that remain valid.
- Historical only: `Projects/deep_archive/PROJ-301-350/PROJ-327/findings/` and `Projects/archived_projects/PROJ-329A/findings/uiwindow_inventory.md`.

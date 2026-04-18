# PROJ-274 File Manifest

## Files

| File | Type | Notes |
|------|------|-------|
| `game/simulation/services/ship_materializer.py` | Production | NEW — interface + 2 implementations |
| `game/context.py` | Production | Add `get_default_ship_materializer()` / `set_default_ship_materializer()` |
| `game/simulation/battle_spec.py` | Production | Add `instance_ref: Optional[Any] = None` to `ShipSpec` |
| `game/simulation/battle_runner.py` | Production | `ship_builder` optional; default from context; update `materialize_spec_ships` |
| `game/simulation/battle_controller.py` | Production | Same override story for `start_from_spec` |
| `game/app.py` | Production | Delete `_ship_builder` closure in `start_battle` |
| `game/ui/screens/test_lab/screen.py` | Production | Delete ship_builder closure in `_switch_to_battle` |
| `combat_lab/services/test_execution_service.py` | Production | Delete ship_builder closures at L83, L95; swap to context materializer |
| `combat_lab/services/scenario_run_helper.py` | Production | Use context materializer (was `scenario._load_ship`) |
| `combat_lab/spec_compiler.py` | Production | Docstring at L12 updated |
| `tests/unit/simulation/services/test_ship_materializer.py` | Test | NEW — unit tests for both implementations |
| `tests/integration/test_app_integration.py` | Test | Update test at L160-190 to verify materializer path |
| `tests/integration/simulation/test_three_team_battle.py` | Test | Keep ship_builder override — VERIFY still works |
| `tests/integration/simulation/test_boundary_retreat.py` | Test | Keep ship_builder override — VERIFY still works |
| `tests/performance/test_telemetry_overhead.py` | Test | Keep ship_builder override — VERIFY still works |
| `docs/04_SERVICES.md` | Doc | Add ShipMaterializer to services table |
| `docs/01_ARCHITECTURE.md` | Doc | Update service list |
| `docs/systems/combat_simulation.md` | Doc | Remove `ship_builder=...` from canonical `run_battle` invocation example |

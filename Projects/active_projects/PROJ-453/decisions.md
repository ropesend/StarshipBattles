# PROJ-453: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-18 | Project initialized | Starting point for Engine + services surface polish (annotations + dead skips + stale docstrings) |
| 2026-05-17 | Phase 1 executed by Group B run-agent | All 10 mechanical polish items closed: F-B-006/F-B-007/F-B-008 (annotations + `# type: ignore` drop on `superweapon_order_processor`), F-B-009 (`resolve_requested` PEP-604 return), F-B-010 (`planet_modifier_effect_engine` property), F-B-011 (6 `_get_*_mutator` accessors annotated as `-> Any`; 3 of 5 files needed `Any` added to typing imports), F-B-012 (deleted two dead `try/except ImportError → pytest.skip` guards in `test_superweapon_registry_contract.py`), F-B-015 (docstring `_cargo_contents → ShipCargoManager`), F-B-016 (dropped "Phase 7 deletes the legacy path" stale promise in `conflict_modifier_collection.py` + parallel reference in `fleet_speed_calculator.py:175`), F-B-021 (annotated `_iter_replay_files -> Iterator[Path]`; added `from collections.abc import Iterator`). Sharded 23368/23368 green. |

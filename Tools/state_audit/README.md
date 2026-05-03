# state_audit

State management & mutability audit. Scans every .py file under `game/` for module-level mutable state, singleton patterns, global keyword usage, and DI context adoption.

## Usage

```powershell
python Tools/state_audit/state_audit.py
```

Outputs to `Reviews/results/YYYY-MM-DD_HHMMSS_state-audit/raw/`:
- `singleton_sites.json` — `_default_*`, `_instance`, `_singleton` definitions
- `module_mutables.json` — module-level dict/list/set assignments
- `global_usages.json` — every `global` keyword with function context
- `class_mutable_defaults.json` — class-level mutable parameter defaults
- `random_seed_sites.json` — `random.seed()` outside per-battle RNG pattern
- `ctx_usage_ratio.json` — `get_default_xxx()` vs `ctx.xxx` call ratio
- `manifest.json` — 4-shard file assignments

## Why a subdirectory

`Tools/README.md` requires every tool to have its own subdirectory and README.

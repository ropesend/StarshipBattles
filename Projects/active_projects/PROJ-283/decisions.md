# PROJ-283: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-18 | Project initialized | Starting point for Race Setup & Habitability Foundation. |
| 2026-04-18 | Unify all 4 preference axes (atmosphere + temp + gravity + water) under one `(setpoint, tolerance)` model | User-confirmed (Q2): consistency across the race-setup UX. One formula, one cost curve. Setpoint free, tolerance costs exponentially in width. |
| 2026-04-18 | Use all 10 gases matching `AtmosphereEngine` (O2, N2, CO2, H2O, CH4, H2, He, Ar, NH3, SO2) | User-confirmed (Q3): parity with the planet atmosphere engine so every gas the game models is addressable by races. |
| 2026-04-18 | Add total surface pressure, tectonic activity, magnetic field as first-class habitability factors; split magnetic field out of the radiation formula | User-confirmed (Q1): pressure + tectonic are real physical factors and magnetic deserves its own weight instead of being rolled into radiation. |
| 2026-04-18 | Delete `aptitude_happiness` — happiness is fully derived downstream (PROJ-284) | Plan agent recommendation accepted: paying points for happiness on top of habitability was double-dipping. Happiness becomes a seeded cache written by the new HappinessEngine. `base_happiness: float = 0.5` replaces the aptitude. |
| 2026-04-18 | Delete `aptitude_population_growth`; replace with `base_reproduction_rate: float = 0.03` | User-confirmed: default 3%, exponential cost to raise. See PROJ-283/Phase 3 for cost curve. |
| 2026-04-18 | Below 3% reproduction rate refunds points linearly to a 0.5% floor | User-confirmed (Q5-round-2): symmetric, lets slow-breeding specialized races exist. Linear (not exponential) refund keeps the trade simple. |
| 2026-04-18 | Store atmosphere pressures in Pa (matching `planet.atmosphere` dict), display kPa in UI | User-confirmed (Q8-round-2): zero conversions in habitability formulas; UI labels convert for readability. |
| 2026-04-18 | Delete existing user race JSON files (disposable) | User stated races "can be deleted"; keeps migration footprint zero. |
| 2026-04-18 | Registry-driven habitability: `FACTOR_REGISTRY: Dict[str, HabitabilityFactor]` is the single source of truth | Plan agent recommendation: adding a new factor becomes a single data-edit instead of touching formula + UI + budget + validators. Maximum extensibility per user request. |
| 2026-04-18 | Factor weights (v1): gravity=1.0, temperature=1.0, pressure=0.9, water=0.8, radiation=0.6, magnetic=0.6, tectonic=0.4, atmosphere per gas normalized so gas bucket sums to 1.5 | Plan agent recommendation. Tunable; parity tests in Phase 2 may force a retune. |
| 2026-04-18 | Project split from master plan at `C:\Users\rossr\.claude\plans\i-want-to-effervescent-hennessy.md` | User requested the big plan be broken into smaller projects. PROJ-283 owns the foundation (data model, formula, budget, race UI). |

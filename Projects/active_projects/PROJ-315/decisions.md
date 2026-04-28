# PROJ-315: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-28 | Project initialized | Starting point for Fleet Report Component Damage Panel |
| 2026-04-28 | Project title: "Fleet Report Component Damage Panel" | User-selected from three proposed titles during triage-to-proj. |
| 2026-04-28 | Average damage % (not worst) on collapsed group rows | User-explicit during initial triage: 4 engines at 75/75/25/25 → 50%. Average is more intuitive for at-a-glance damage assessment. |
| 2026-04-28 | `<functional> / <total>` fraction on group rows uses `is_active` directly | User-explicit during initial triage: simpler than computing per-instance threshold arithmetic in UI; `is_active` already encodes the threshold decision. |
| 2026-04-28 | Layer order: `[CORE, INNER, OUTER, ARMOR]`; HULL excluded | User-explicit during planning Q1: match Workshop's `layer_panel.py:128` order; HULL was Workshop-only and not relevant to the Fleet Report's per-component view. |
| 2026-04-28 | Default expand state: all collapsed; auto-expand layers with destroyed instances | User-explicit during planning Q2. Reduces wall-of-text on capital ships with 30+ components; surfaces critical info without interaction. |
| 2026-04-28 | Section title: "COMPONENT STATUS" (was "COMPONENT DAMAGE") | User-explicit during planning Q3. Old title implied damage-only content; new section always renders. |
| 2026-04-28 | Phase structure: 3 phases (data helper → widget rewrite → docs) | User-explicit during planning Q4. The grouping helper colocates as a module-level function rather than a separate module — matches `planet_report_panel.py` precedent. |
| 2026-04-28 | No facade DTO + slice query | Plan-time decision. Panel already direct-reads `ShipInstance` via TYPE_CHECKING; file docstring documents this as accepted "Cross-layer imports (acceptable for UI display)". Adding facade indirection here is unrelated churn. |
| 2026-04-28 | `ComponentInstanceView` lives in `game/core/component_state.py` | Architecture Analyst recommendation. Sibling of `ComponentState`; Core layer keeps view + state types colocated and avoids forcing simulation/strategy callers to import from each other for read-only views. |
| 2026-04-28 | `iter_all_components_by_layer()` lives on `ShipInstance` | Architecture Analyst recommendation. Joins `design_data['layers']` (string keys, e.g. "CORE") with `self.components` state — both are Strategy-layer concerns. |
| 2026-04-28 | Iterate layers by string list `['CORE', 'INNER', 'OUTER', 'ARMOR']` | `LayerType` enum is sim-layer-only; `design_data['layers']` keys are strings. No need to import `LayerType` in the iterator. |
| 2026-04-28 | Visual distinction between damage-induced inactive and manually-disabled components | User-explicit Phase C Q1: damage-inactive renders in red + strikethrough; manual-disable renders in muted grey, no strike. Requires comparing HP vs `damage_threshold` to detect "damage-induced inactive". |
| 2026-04-28 | Auto-expand re-fires on every ship selection | User-explicit Phase C Q2: deterministic; user always sees critical info. No per-(ship, layer) state required. |
| 2026-04-28 | Strikethrough rendered via manual `pygame.draw.line()` overlay | pygame_gui `<s>` rich-text not supported in this version. Manual overlay matches the precedent in `game/ui/screens/test_lab/dialogs.py`. Encapsulated as `_apply_strikethrough(label)` helper. |
| 2026-04-28 | New `MUTED_GREY` colour constant in `game/ui/colors.py` for manual-disable | Distinct from `HP_DESTROYED` grey to communicate "off but not broken". Suggested value `(130, 130, 150)` — finalise during implementation if a sibling tone exists. |
| 2026-04-28 | Damage-threshold lookup is dependency-injected into `group_components_by_id` | Pure-function testability. Production passes `get_default_registry_provider().get_component_registry().get_component(id).damage_threshold`; tests stub a `dict.get(id, default)` lookup. Falls back to `CombatConstants.DEFAULT_DAMAGE_THRESHOLD` (0.5) on miss. |
| 2026-04-28 | Existing `_`-vs-`#` parsing bug at `ship_detail_panel.py:367-375` is fixed implicitly by the rewrite | The new view uses `ComponentInstanceView.component_id` directly, never re-parses a key. Regression test `test_component_state_key_with_underscores_in_id` pins the fix. |
| 2026-04-28 | Chevron characters: keep existing `▼` (expanded) / `▶` (collapsed) | Pattern Scout flagged a codebase inconsistency between Workshop's `▲`/`▼` and the existing panel's `▼`/`▶`. Within-this-panel continuity wins; chevron unification is out of scope. |
| 2026-04-28 | Per-tick rebuild on every toggle is acceptable | Risk Assessor flagged it as Low (user-action-paced). ~30 components × ~5 layers rebuild fits comfortably within pygame_gui's per-frame budget. Document with a comment; do not optimise prematurely. |
| 2026-04-28 | Legacy save with renamed `component_id` falls back to default view | Per CLAUDE.md "Saves are disposable" policy. Iterator returns a default `ComponentInstanceView(current_hp=max_hp, is_active=True)` on missing ComponentState; never crashes. Documented in iterator docstring. |

"""Effect ability display helpers — grouping, naming, formatting, and status.

Extracted from `system_effects_collector.py` (PROJ-362 audit remediation,
MAJ-001 — 500 LOC ceiling). These functions operate on raw ability dicts
and `ComponentActivationState` values; they are read-only display helpers
with no aggregation responsibility.

Public surface:
- `make_group_key(ability_name, ability_data) -> str`
- `make_display_name(ability_name, ability_data) -> str`
- `format_intrinsic_ability_magnitude(ability_name, ability_data) -> str`

Internal helpers (re-exported by `system_effects_collector` for back-compat):
- `_ability_kind`, `_format_status`, `_is_activatable`
"""
from game.strategy.data.component_activation_state import (
    ActivationPhase,
    ComponentActivationState,
)
from game.strategy.services.effect_ability_metadata import find_metadata


def _ability_kind(ability_name: str) -> str:
    """Return 'rate' or 'multiplier' based on the metadata registry.

    Falls back to 'multiplier' for unknown ability names (matches the
    legacy `_RATE_ABILITIES` membership-check behavior).
    """
    m = find_metadata(ability_name)
    return m.kind if m is not None else 'multiplier'


# ---------------------------------------------------------------------------
# Status helpers (unchanged from the pre-PROJ-300 collector). These work on
# any object exposing `get_activation_state(comp_key) -> ComponentActivationState`.
# ---------------------------------------------------------------------------


def _format_status(state: ComponentActivationState | None) -> str:
    """Render an activation state as a human-readable status string."""
    if state is None:
        return "Active"  # Sources without activation tracking are always-on.
    if state.phase == ActivationPhase.ACTIVE:
        return "Active"
    if state.phase == ActivationPhase.ACTIVATING:
        remaining = state.required_ticks - state.progress_ticks
        return f"Activating ({remaining})"
    if state.phase == ActivationPhase.DEACTIVATING:
        remaining = state.required_ticks - state.progress_ticks
        return f"Deactivating ({remaining})"
    return "Inactive"


def _is_activatable(ability_data: dict) -> bool:
    """Activatable abilities have an `activation_time` field."""
    return isinstance(ability_data, dict) and 'activation_time' in ability_data


# ---------------------------------------------------------------------------
# Grouping + display name (unchanged).
# ---------------------------------------------------------------------------


def make_group_key(ability_name: str, ability_data) -> str:
    """Group key for an ability instance.

    Driven by `EffectAbilityMetadata.grouping_key_field` from the registry.
    When set (e.g. 'resource_type' for ResourceHarvestBooster, 'damage_type'
    for EnvironmentalDamage), the key is `f"{ability_name}:{value}"`. When
    absent (or the ability is unknown), the key is the ability_name alone.

    Public since FEAT-16 — also consumed by the Planet List effects filter
    and per-effect column generators.
    """
    metadata = find_metadata(ability_name)
    if metadata is None or metadata.grouping_key_field is None:
        return ability_name
    if not isinstance(ability_data, dict):
        return ability_name
    field_value = ability_data.get(metadata.grouping_key_field)
    # Per-resource grouping for QualityImprovement preserves the legacy
    # behavior of falling back to the bare ability_name when the field is
    # missing/empty (e.g. tests with sparse fixtures).
    if not field_value:
        # EnvironmentalDamage's legacy fallback was the literal string
        # 'environmental' when damage_type was missing — keep that exact
        # behavior so callers see the same group keys.
        if ability_name == 'EnvironmentalDamage':
            return f"{ability_name}:environmental"
        return ability_name
    return f"{ability_name}:{field_value}"


def make_display_name(ability_name: str, ability_data) -> str:
    """Human-readable label for an ability instance.

    Driven by `EffectAbilityMetadata.display_name`. When the registry entry
    has an explicit display_name, it is returned verbatim. When display_name
    is None, the label is derived from the `grouping_key_field` value in
    `ability_data` ("Metals Harvest Boost", "Plasma Damage").

    Public since FEAT-16 — used as Planet List per-effect column titles and
    Effects filter chip labels.
    """
    metadata = find_metadata(ability_name)
    if metadata is None:
        return ability_name
    if metadata.display_name is not None:
        return metadata.display_name
    # Derived display name from the data field. Pick the right suffix
    # per grouping family — resource boosters get "Harvest Boost",
    # environmental damage gets "Damage".
    if isinstance(ability_data, dict) and metadata.grouping_key_field:
        value = ability_data.get(metadata.grouping_key_field)
        if metadata.grouping_key_field == 'resource_type':
            label_value = value if value else 'unknown'
            return f"{label_value.capitalize()} Harvest Boost"
        if metadata.grouping_key_field == 'damage_type':
            label_value = value if value else 'environmental'
            return f"{label_value.capitalize()} Damage"
    return ability_name


def format_intrinsic_ability_magnitude(ability_name: str, ability_data) -> str:
    """Render the magnitude of a single ability instance for UI display.

    Used by the Planet List per-effect columns (FEAT-16) and by the System
    Tree panel's per-effect rendering. The aggregate-effect formatter in
    `system_tree_panel._format_effect_value` delegates to this for the
    shared multiplier/rate paths.

    Returns "" when the value is the additive/multiplicative identity (so
    cells stay blank rather than rendering noise like "x1.00").
    """
    if not isinstance(ability_data, dict):
        return ""

    metadata = find_metadata(ability_name)
    if metadata is None:
        # Unknown ability — render nothing rather than fabricating "x..."
        # for arbitrary input.
        return ""

    if metadata.kind == 'rate':
        rate = ability_data.get('rate')
        if not rate:
            return ""
        try:
            r = float(rate)
        except (TypeError, ValueError):
            return ""
        if ability_name == 'EnvironmentalDamage':
            return f"-{r:.2f} hull/turn"
        if ability_name == 'FuelDrain':
            return f"-{r:.2f} fuel/turn"
        return f"{r:+.2f}/turn"

    # Multiplier-style.
    mult = ability_data.get('multiplier')
    if mult is None:
        return ""
    try:
        m = float(mult)
    except (TypeError, ValueError):
        return ""
    if m == 1.0:
        return ""
    return f"x{m:.2f}"

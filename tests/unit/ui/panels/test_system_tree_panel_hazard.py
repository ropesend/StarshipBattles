"""PROJ-302 D8: hostile-system hazard hint formatter tests."""
from game.ui.panels.system_tree_panel import _format_star_hazard_hints


def _star_provider(label, ability_data):
    return {
        'source_kind': 'star',
        'source_label': label,
        'source_id': f'star:{label}',
        'is_active': True,
        'ability_data': ability_data,
    }


def _effect(ability_name, providers):
    return {'ability_name': ability_name, 'providers': providers}


def test_no_effects_yields_empty_hints():
    assert _format_star_hazard_hints([]) == []


def test_benign_main_sequence_star_yields_no_hint():
    """A main-sequence star that DOES project an ability but whose
    multiplier is benign (>= 1.0) yields no hazard hint.

    PROJ-346 strengthening: previously had a body identical to
    ``test_no_effects_yields_empty_hints`` — both passed an empty list.
    Rewrite to a distinct variant: a star provider that survives
    both the source_kind=='star' filter AND the scope=='system' filter
    but is ruled out by the hostility-threshold check (multiplier == 1.0
    is the boundary, see test_thrust_modifier_at_one_no_hint for the
    matching ThrustModifier case). This pins the formatter's combined
    hostility-test rather than just its empty-list short-circuit.
    """
    effects = [_effect('ShieldModifier', [
        _star_provider('Sol (G2V Main Sequence)',
                       {'multiplier': 1.0, 'scope': 'system'}),
    ])]
    assert _format_star_hazard_hints(effects) == []


def test_pulsar_shield_modifier_renders_hazard():
    """PROJ-302 D7: a pulsar with ShieldModifier 0.7 system-scope is HOSTILE."""
    effects = [_effect('ShieldModifier', [
        _star_provider('Pulsar X-1 (Pulsar)', {'multiplier': 0.7, 'scope': 'system'}),
    ])]
    hints = _format_star_hazard_hints(effects)
    assert len(hints) == 1
    assert 'Pulsar X-1' in hints[0]
    assert '-30%' in hints[0]
    assert 'shields' in hints[0].lower()


def test_neutron_star_environmental_damage_renders_hazard():
    effects = [_effect('EnvironmentalDamage', [
        _star_provider('Cyg X-3 (Neutron Star)', {
            'rate': 0.3, 'damage_type': 'radiation', 'scope': 'system',
        }),
    ])]
    hints = _format_star_hazard_hints(effects)
    assert len(hints) == 1
    assert 'radiation' in hints[0]
    assert '0.30' in hints[0]


def test_black_hole_thrust_modifier_renders_hazard():
    effects = [_effect('ThrustModifier', [
        _star_provider('Sgr A* (Black Hole)', {'multiplier': 0.5, 'scope': 'system'}),
    ])]
    hints = _format_star_hazard_hints(effects)
    assert len(hints) == 1
    assert 'thrust' in hints[0].lower()
    assert '-50%' in hints[0]


def test_facility_provider_does_not_render_hazard_hint():
    """Hazard hints are STAR-specific (D8 — only system-scope hostile stars)."""
    facility_provider = {
        'source_kind': 'facility',
        'source_label': 'Shield Generator',
        'is_active': True,
        'ability_data': {'multiplier': 0.5, 'scope': 'system'},
    }
    effects = [_effect('ShieldModifier', [facility_provider])]
    assert _format_star_hazard_hints(effects) == []


def test_storm_provider_does_not_render_hazard_hint():
    """Storms are sector-scope, not system-scope hostile stars."""
    storm_provider = {
        'source_kind': 'storm',
        'source_label': 'Ion Storm Alpha',
        'is_active': True,
        'ability_data': {'multiplier': 0.5, 'scope': 'sector'},
    }
    effects = [_effect('ShieldModifier', [storm_provider])]
    assert _format_star_hazard_hints(effects) == []


def test_buff_shield_modifier_does_not_render_hazard():
    """A friendly system-wide shield buff (>= 1.0) is not a hazard."""
    effects = [_effect('ShieldModifier', [
        _star_provider('Friendly Aura Star', {'multiplier': 1.25, 'scope': 'system'}),
    ])]
    assert _format_star_hazard_hints(effects) == []


def test_multiple_hazards_all_rendered():
    """Pulsar + neutron-star binary in same system: both hazards visible."""
    effects = [
        _effect('ShieldModifier', [
            _star_provider('Star A (Pulsar)', {'multiplier': 0.7, 'scope': 'system'}),
        ]),
        _effect('EnvironmentalDamage', [
            _star_provider('Star B (Neutron Star)', {
                'rate': 0.4, 'damage_type': 'radiation', 'scope': 'system',
            }),
        ]),
    ]
    hints = _format_star_hazard_hints(effects)
    assert len(hints) == 2
    assert any('Pulsar' in h for h in hints)
    assert any('Neutron' in h for h in hints)


# ---------------------------------------------------------------------------
# PROJ-338 — Characterization corner cases for the hazard formatter
# ---------------------------------------------------------------------------


def test_thrust_modifier_at_one_no_hint():
    """Thrust modifier exactly == 1.0 is benign (no hazard)."""
    effects = [_effect('ThrustModifier', [
        _star_provider('Neutral Star', {'multiplier': 1.0, 'scope': 'system'}),
    ])]
    assert _format_star_hazard_hints(effects) == []


def test_multiple_star_providers_each_yield_a_hint():
    """Two stars both projecting ShieldModifier each get their own hint."""
    effects = [_effect('ShieldModifier', [
        _star_provider('Star A', {'multiplier': 0.5, 'scope': 'system'}),
        _star_provider('Star B', {'multiplier': 0.8, 'scope': 'system'}),
    ])]
    hints = _format_star_hazard_hints(effects)
    assert len(hints) == 2
    assert any('Star A' in h and '-50%' in h for h in hints)
    assert any('Star B' in h and '-20%' in h for h in hints)


def test_non_star_provider_ignored_even_if_shield_modifier_low():
    """Source-kind != star → never a hazard, even with very low multiplier."""
    facility_provider = {
        'source_kind': 'facility',
        'source_label': 'Old Generator',
        'is_active': True,
        'ability_data': {'multiplier': 0.1, 'scope': 'system'},
    }
    effects = [_effect('ShieldModifier', [facility_provider])]
    assert _format_star_hazard_hints(effects) == []


def test_missing_ability_data_dict_treated_as_empty_no_hint():
    """ability_data=None falls through to {} → multiplier defaults to 1.0 → no hint."""
    provider = {
        'source_kind': 'star',
        'source_label': 'Mystery Star',
        'is_active': True,
        'ability_data': None,
    }
    effects = [_effect('ShieldModifier', [provider])]
    assert _format_star_hazard_hints(effects) == []


def test_environmental_damage_zero_rate_no_hint():
    """rate <= 0 produces no hint (the > 0 gate)."""
    effects = [_effect('EnvironmentalDamage', [
        _star_provider('Calm Star', {'rate': 0.0, 'damage_type': 'radiation', 'scope': 'system'}),
    ])]
    assert _format_star_hazard_hints(effects) == []

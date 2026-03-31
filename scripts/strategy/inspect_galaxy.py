#!/usr/bin/env python3
"""
Galaxy generation inspector for balancing feedback loops.

Generates galaxies using the real game code and outputs comprehensive stats
as structured JSON (optimized for AI-agent parsing) plus human-readable
console summaries.

Supports single-galaxy inspection, batch comparison across multiple runs,
and optional visual chart generation.

Usage:
    python scripts/strategy/inspect_galaxy.py --seed 42
    python scripts/strategy/inspect_galaxy.py --seed 42 --systems 100 --type spiral
    python scripts/strategy/inspect_galaxy.py --batch 10 --seed 1000 --type cluster
    python scripts/strategy/inspect_galaxy.py --seed 42 --charts
    python scripts/strategy/inspect_galaxy.py --seed 42 -v 0   # JSON only
"""
import sys
import os
import json
import random
import math
import time
import argparse
import statistics
from pathlib import Path
from datetime import datetime, timezone

# Add project root to path (scripts/strategy/ -> scripts/ -> project root)
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Must chdir to project root so Galaxy can find data files
os.chdir(project_root)

from game.strategy.data.galaxy import Galaxy
from game.strategy.data.planet import PlanetType
from game.strategy.data.stars import StarType
from game.core.hex_math import hex_distance, hex_to_pixel
from game.core.resources import ResourceCatalog

PLANET_RESOURCES = [d.id for d in ResourceCatalog.from_json().by_display_group("planetary")]
from game.strategy.generation.placement_strategies import (
    RandomPlacementStrategy,
    DensityBasedPlacementStrategy
)
from game.strategy.generation.loaders.galaxy_layouts_loader import GalaxyLayoutsLoader
from game.strategy.generation.density.density_map import DensityMap
from game.strategy.generation.region_classifier import RegionClassifier
from game.strategy.formulas.habitability import calculate_habitability

# Valid galaxy types from galaxy_layouts.json
VALID_GALAXY_TYPES = [
    'random', 'cluster', 'spiral', 'spiral_no_core',
    'barred_spiral', 'ring', 'irregular', 'diamond', 'uniform'
]

# Reference species for habitability scoring (Earth-like baseline)
REF_GRAVITY_IDEAL = 1.0       # g
REF_GRAVITY_TOLERANCE = 0.3   # g
REF_TEMP_IDEAL = 288.0        # K (~15°C)
REF_TEMP_TOLERANCE = 30.0     # K
REF_WATER_IDEAL = 0.7
REF_WATER_TOLERANCE = 0.3
REF_ATMOSPHERE_PREFS = {
    'Oxygen': 80.0,
    'Nitrogen': 60.0,
    'CO2': -20.0,
    'Methane': -40.0,
    'Hydrogen': -60.0,
    'Helium': -10.0,
}
REF_RADIATION_TOLERANCE = 0.0  # neutral

MIN_DIST = 400  # Minimum distance between systems (matches GameSession)


def calculate_radius(count: int, min_dist: int = MIN_DIST) -> int:
    """Calculate appropriate galaxy radius for system count."""
    area_needed = count * min_dist * min_dist
    base_radius = int(math.sqrt(area_needed / math.pi))
    return max(3000, int(base_radius * 2.5))


def generate_galaxy(seed, system_count, galaxy_type, radius, region_mode='normal'):
    """Generate a galaxy using the real game generation pipeline.

    Returns:
        Galaxy object with systems, stars, planets, storms, and warp points.
    """
    random.seed(seed)
    rng = random.Random(seed)

    galaxy = Galaxy(radius=radius)
    region_classifier = None

    if galaxy_type == 'random':
        strategy = RandomPlacementStrategy()
    else:
        scaled_config = GalaxyLayoutsLoader.load_and_scale(galaxy_type, radius)
        density_map = DensityMap.from_config(scaled_config, radius)
        strategy = DensityBasedPlacementStrategy(density_map)
        region_classifier = RegionClassifier(scaled_config, radius)

    galaxy.generate_systems(
        count=system_count,
        min_dist=MIN_DIST,
        placement_strategy=strategy,
        rng=rng
    )

    if region_classifier:
        for sys in galaxy.systems.values():
            sys.region_id = region_classifier.classify(sys.global_location)

    galaxy.generate_warp_lanes(
        region_classifier=region_classifier,
        inter_region_mode=region_mode
    )

    return galaxy


# ---------------------------------------------------------------------------
# Data extraction
# ---------------------------------------------------------------------------

def _ref_habitability(planet):
    """Compute reference habitability score for a planet."""
    return calculate_habitability(
        gravity_ms2=planet.surface_gravity,
        temperature_k=planet.surface_temperature,
        water_coverage=planet.surface_water,
        atmosphere=planet.atmosphere,
        magnetic_field=planet.magnetic_field,
        gravity_ideal=REF_GRAVITY_IDEAL,
        gravity_tolerance=REF_GRAVITY_TOLERANCE,
        temp_ideal=REF_TEMP_IDEAL,
        temp_tolerance=REF_TEMP_TOLERANCE,
        water_ideal=REF_WATER_IDEAL,
        water_tolerance=REF_WATER_TOLERANCE,
        atmosphere_preferences=REF_ATMOSPHERE_PREFS,
        radiation_tolerance=REF_RADIATION_TOLERANCE,
    )


def _hex_dict(h):
    return {'q': h.q, 'r': h.r}


def extract_star_data(star):
    return {
        'name': star.name,
        'star_type': star.star_type.name,
        'mass_solar': star.mass,
        'temperature_k': star.temperature,
        'luminosity_solar': star.luminosity,
        'radius_hexes': star.radius_hexes,
        'age_years': star.age,
        'color': list(star.color) if star.color else [255, 255, 255],
        'location': _hex_dict(star.location),
        'spectrum': star.spectrum.to_dict(),
    }


def extract_planet_data(planet):
    return {
        'id': planet.id,
        'name': planet.name,
        'planet_type': planet.planet_type.name,
        'location': _hex_dict(planet.location),
        'orbit_distance': planet.orbit_distance,
        'orbit_parent_name': planet.orbit_parent_name,
        'mass_kg': planet.mass,
        'radius_m': planet.radius,
        'surface_area_m2': planet.surface_area,
        'density_kg_m3': planet.density,
        'surface_gravity_ms2': planet.surface_gravity,
        'surface_pressure_pa': planet.surface_pressure,
        'surface_temperature_k': planet.surface_temperature,
        'surface_water': planet.surface_water,
        'tectonic_activity': planet.tectonic_activity,
        'magnetic_field': planet.magnetic_field,
        'atmosphere': dict(planet.atmosphere),
        'resources': {
            name: {'quantity': r.get('quantity', 0), 'quality': r.get('quality', 0)}
            for name, r in planet.deposits.items()
        },
        'habitability_reference': round(_ref_habitability(planet), 4),
    }


def extract_storm_data(storm):
    return {
        'name': storm.name,
        'storm_type': storm.storm_type,
        'location': _hex_dict(storm.location),
        'hex_count': len(storm.hex_offsets),
        'intensity': storm.intensity,
        'effects': storm.effects.to_dict(),
    }


def extract_system_data(system):
    stars = [extract_star_data(s) for s in system.stars]
    planets = [extract_planet_data(p) for p in system.planets]
    storms = [extract_storm_data(s) for s in system.storms]
    warp_points = [
        {'destination': wp.destination_id, 'location': _hex_dict(wp.location)}
        for wp in system.warp_points
    ]

    # System-level resource totals
    total_resources = {}
    for p in system.planets:
        for res_name in PLANET_RESOURCES:
            r = p.resources.get(res_name, {})
            total_resources[res_name] = total_resources.get(res_name, 0) + r.get('quantity', 0)

    return {
        'name': system.name,
        'global_location': _hex_dict(system.global_location),
        'region_id': system.region_id,
        'stars': stars,
        'planets': planets,
        'storms': storms,
        'warp_points': warp_points,
        'system_summary': {
            'star_count': len(stars),
            'planet_count': len(planets),
            'storm_count': len(storms),
            'warp_point_count': len(warp_points),
            'total_resources': total_resources,
        },
    }


def extract_galaxy_json(galaxy, seed, system_count, galaxy_type, radius, region_mode, gen_time):
    """Build the full JSON-serializable dict for a galaxy."""
    systems = [extract_system_data(s) for s in galaxy.systems.values()]

    return {
        'metadata': {
            'version': '1.0',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'seed': seed,
            'system_count_requested': system_count,
            'system_count_actual': len(galaxy.systems),
            'galaxy_type': galaxy_type,
            'galaxy_radius': galaxy.radius,
            'region_mode': region_mode,
            'generation_time_seconds': round(gen_time, 3),
        },
        'galaxy': {
            'systems': systems,
        },
        'balance_metrics': compute_balance_metrics(galaxy),
    }


# ---------------------------------------------------------------------------
# Balance metrics
# ---------------------------------------------------------------------------

def _safe_stats(values):
    """Compute min/max/avg/stddev for a list of numbers."""
    if not values:
        return {'count': 0, 'avg': 0, 'stddev': 0, 'min': 0, 'max': 0, 'total': 0}
    avg = statistics.mean(values)
    stddev = statistics.stdev(values) if len(values) > 1 else 0
    return {
        'count': len(values),
        'total': sum(values),
        'avg': round(avg, 2),
        'stddev': round(stddev, 2),
        'min': round(min(values), 2),
        'max': round(max(values), 2),
    }


def compute_balance_metrics(galaxy):
    """Compute aggregate balance metrics across the entire galaxy."""
    all_planets = []
    all_stars = []
    all_storms = []

    for system in galaxy.systems.values():
        all_planets.extend(system.planets)
        all_stars.extend(system.stars)
        all_storms.extend(system.storms)

    total_planets = len(all_planets)
    total_stars = len(all_stars)

    # Planet type distribution
    planet_type_dist = {}
    for pt in PlanetType:
        count = sum(1 for p in all_planets if p.planet_type == pt)
        if count > 0 or pt != PlanetType.DYSON_SPHERE:
            planet_type_dist[pt.name] = {
                'count': count,
                'pct': round(100 * count / total_planets, 1) if total_planets else 0,
            }

    # Star type distribution
    star_type_dist = {}
    for st in StarType:
        count = sum(1 for s in all_stars if s.star_type == st)
        if count > 0:
            star_type_dist[st.name] = {
                'count': count,
                'pct': round(100 * count / total_stars, 1) if total_stars else 0,
            }

    # Resource distribution
    resource_dist = {}
    for res_name in PLANET_RESOURCES:
        quantities = [
            p.resources.get(res_name, {}).get('quantity', 0)
            for p in all_planets
        ]
        qualities = [
            p.resources.get(res_name, {}).get('quality', 0)
            for p in all_planets
        ]
        resource_dist[res_name] = {
            'quantity': _safe_stats(quantities),
            'quality': _safe_stats(qualities),
        }

    # Habitability distribution
    hab_scores = [_ref_habitability(p) for p in all_planets]
    hab_stats = _safe_stats(hab_scores)

    # Habitability histogram (10 buckets)
    hab_histogram = []
    for i in range(10):
        lo = i * 0.1
        hi = (i + 1) * 0.1
        count = sum(1 for h in hab_scores if lo <= h < hi) if i < 9 else sum(1 for h in hab_scores if lo <= h <= hi)
        hab_histogram.append({
            'range': f'{lo:.1f}-{hi:.1f}',
            'count': count,
        })

    hab_stats['histogram'] = hab_histogram

    # System richness
    planets_per_sys = [len(s.planets) for s in galaxy.systems.values()]
    storms_per_sys = [len(s.storms) for s in galaxy.systems.values()]
    resources_per_sys = []
    for system in galaxy.systems.values():
        total = 0
        for p in system.planets:
            for res_name in PLANET_RESOURCES:
                total += p.resources.get(res_name, {}).get('quantity', 0)
        resources_per_sys.append(total)

    system_richness = {
        'planets_per_system': _safe_stats(planets_per_sys),
        'resources_per_system': _safe_stats(resources_per_sys),
        'storms_per_system': _safe_stats(storms_per_sys),
    }

    # Storm coverage
    systems_with_storms = sum(1 for s in galaxy.systems.values() if s.storms)
    storm_type_counts = {}
    total_storm_hexes = 0
    for storm in all_storms:
        storm_type_counts[storm.storm_type] = storm_type_counts.get(storm.storm_type, 0) + 1
        total_storm_hexes += len(storm.hex_offsets)

    storm_coverage = {
        'systems_with_storms': systems_with_storms,
        'systems_without_storms': len(galaxy.systems) - systems_with_storms,
        'total_storms': len(all_storms),
        'storm_type_distribution': storm_type_counts,
        'total_storm_hexes': total_storm_hexes,
        'avg_storm_hex_count': round(total_storm_hexes / len(all_storms), 1) if all_storms else 0,
    }

    # Connectivity
    connections_per_sys = [len(s.warp_points) for s in galaxy.systems.values()]
    total_warp_lanes = sum(connections_per_sys) // 2
    isolated = sum(1 for c in connections_per_sys if c == 0)

    # Inter vs intra region lanes
    inter_region = 0
    intra_region = 0
    counted_pairs = set()
    for system in galaxy.systems.values():
        for wp in system.warp_points:
            pair_key = tuple(sorted([system.name, wp.destination_id]))
            if pair_key in counted_pairs:
                continue
            counted_pairs.add(pair_key)
            target = galaxy.get_system_by_name(wp.destination_id)
            if target and system.region_id is not None and target.region_id is not None:
                if system.region_id == target.region_id:
                    intra_region += 1
                else:
                    inter_region += 1

    connectivity = {
        'total_warp_lanes': total_warp_lanes,
        'avg_connections_per_system': round(statistics.mean(connections_per_sys), 1) if connections_per_sys else 0,
        'min_connections': min(connections_per_sys) if connections_per_sys else 0,
        'max_connections': max(connections_per_sys) if connections_per_sys else 0,
        'isolated_systems': isolated,
        'inter_region_lanes': inter_region,
        'intra_region_lanes': intra_region,
    }

    # Spatial distribution
    system_locs = list(galaxy.systems.keys())
    distances = []
    for i in range(len(system_locs)):
        for j in range(i + 1, len(system_locs)):
            d = hex_distance(system_locs[i], system_locs[j])
            distances.append(d)

    # Systems per region
    region_counts = {}
    for system in galaxy.systems.values():
        rid = system.region_id if system.region_id is not None else -1
        region_counts[str(rid)] = region_counts.get(str(rid), 0) + 1

    spatial = {
        'system_distances': _safe_stats(distances),
        'systems_per_region': region_counts,
    }

    # Moon/co-orbital analysis: group planets by hex location within each system
    from collections import Counter
    hex_group_sizes = []  # how many bodies share each occupied hex
    for system in galaxy.systems.values():
        loc_counts = Counter()
        for p in system.planets:
            loc_counts[p.location] += 1
        hex_group_sizes.extend(loc_counts.values())

    # Count how many hexes have N bodies (1=solo, 2=primary+1moon, etc.)
    group_size_dist = Counter(hex_group_sizes)
    total_hexes = len(hex_group_sizes)
    moon_hexes = sum(1 for s in hex_group_sizes if s > 1)
    total_moons = sum(s - 1 for s in hex_group_sizes)  # extra bodies beyond the primary

    # Histogram: how many hexes have 1, 2, 3, ... bodies
    max_group = max(hex_group_sizes) if hex_group_sizes else 0
    moon_histogram = {}
    for size in range(1, max_group + 1):
        count = group_size_dist.get(size, 0)
        if count > 0 or size <= 5:
            moon_histogram[str(size)] = count

    moons = {
        'total_occupied_hexes': total_hexes,
        'hexes_with_moons': moon_hexes,
        'hexes_without_moons': total_hexes - moon_hexes,
        'total_moons': total_moons,
        'pct_hexes_with_moons': round(100 * moon_hexes / total_hexes, 1) if total_hexes else 0,
        'avg_moons_per_hex': round(total_moons / total_hexes, 2) if total_hexes else 0,
        'bodies_per_hex_histogram': moon_histogram,
    }

    return {
        'total_systems': len(galaxy.systems),
        'total_planets': total_planets,
        'total_stars': total_stars,
        'total_storms': len(all_storms),
        'planet_type_distribution': planet_type_dist,
        'star_type_distribution': star_type_dist,
        'resource_distribution': resource_dist,
        'habitability_distribution': hab_stats,
        'system_richness': system_richness,
        'storm_coverage': storm_coverage,
        'connectivity': connectivity,
        'spatial': spatial,
        'moons': moons,
    }


# ---------------------------------------------------------------------------
# Console summary
# ---------------------------------------------------------------------------

def print_summary(data, verbosity):
    """Print human-readable summary to console."""
    if verbosity <= 0:
        return

    meta = data['metadata']
    metrics = data['balance_metrics']

    print('=' * 70)
    print(f"GALAXY INSPECTION  seed={meta['seed']}  type={meta['galaxy_type']}")
    print(f"  Systems: {metrics['total_systems']}  Planets: {metrics['total_planets']}  "
          f"Stars: {metrics['total_stars']}  Storms: {metrics['total_storms']}")
    print(f"  Radius: {meta['galaxy_radius']}  Generated in {meta['generation_time_seconds']}s")
    print('=' * 70)

    # Planet type distribution
    print('\nPlanet Type Distribution:')
    for pt_name, info in sorted(metrics['planet_type_distribution'].items(), key=lambda x: -x[1]['count']):
        bar = '#' * max(1, info['count'])
        print(f"  {pt_name:<14} {info['count']:>4}  ({info['pct']:>5.1f}%)  {bar}")

    # Star type distribution
    print('\nStar Type Distribution:')
    for st_name, info in sorted(metrics['star_type_distribution'].items(), key=lambda x: -x[1]['count']):
        print(f"  {st_name:<16} {info['count']:>4}  ({info['pct']:>5.1f}%)")

    # Resource distribution
    print('\nResource Distribution (quantity per planet):')
    print(f"  {'Resource':<14} {'Total':>12} {'Avg':>10} {'StdDev':>10} {'Min':>10} {'Max':>10}")
    for res_name in PLANET_RESOURCES:
        q = metrics['resource_distribution'][res_name]['quantity']
        print(f"  {res_name:<14} {q['total']:>12,.0f} {q['avg']:>10,.0f} {q['stddev']:>10,.0f} "
              f"{q['min']:>10,.0f} {q['max']:>10,.0f}")

    # Habitability
    hab = metrics['habitability_distribution']
    print(f"\nHabitability (Earth-like reference):  "
          f"avg={hab['avg']:.3f}  stddev={hab['stddev']:.3f}  "
          f"min={hab['min']:.3f}  max={hab['max']:.3f}")
    print('  Histogram: ', end='')
    for bucket in hab['histogram']:
        print(f"[{bucket['range']}]={bucket['count']} ", end='')
    print()

    # System richness
    sr = metrics['system_richness']
    print(f"\nSystem Richness:")
    print(f"  Planets/system:   avg={sr['planets_per_system']['avg']:.1f}  "
          f"stddev={sr['planets_per_system']['stddev']:.1f}  "
          f"range=[{sr['planets_per_system']['min']:.0f}, {sr['planets_per_system']['max']:.0f}]")
    print(f"  Resources/system: avg={sr['resources_per_system']['avg']:,.0f}  "
          f"stddev={sr['resources_per_system']['stddev']:,.0f}")

    # Connectivity
    conn = metrics['connectivity']
    print(f"\nConnectivity:")
    print(f"  Warp lanes: {conn['total_warp_lanes']}  "
          f"avg={conn['avg_connections_per_system']:.1f}/system  "
          f"range=[{conn['min_connections']}, {conn['max_connections']}]  "
          f"isolated={conn['isolated_systems']}")
    print(f"  Inter-region: {conn['inter_region_lanes']}  Intra-region: {conn['intra_region_lanes']}")

    # Storm coverage
    sc = metrics['storm_coverage']
    print(f"\nStorm Coverage:")
    print(f"  {sc['systems_with_storms']}/{sc['systems_with_storms'] + sc['systems_without_storms']} "
          f"systems have storms  ({sc['total_storms']} storms, {sc['total_storm_hexes']} hexes)")
    if sc['storm_type_distribution']:
        parts = [f"{k}={v}" for k, v in sc['storm_type_distribution'].items()]
        print(f"  Types: {', '.join(parts)}")

    # Moons
    mn = metrics['moons']
    print(f"\nMoons/Co-orbitals:")
    print(f"  {mn['total_occupied_hexes']} orbital hexes, {mn['hexes_with_moons']} have moons "
          f"({mn['pct_hexes_with_moons']:.1f}%), {mn['total_moons']} total moons")
    print(f"  Bodies per hex: ", end='')
    for size, count in sorted(mn['bodies_per_hex_histogram'].items(), key=lambda x: int(x[0])):
        label = 'solo' if size == '1' else f'{int(size)-1} moon{"s" if int(size) > 2 else ""}'
        print(f"[{label}]={count} ", end='')
    print()

    # Verbose: per-system breakdown
    if verbosity >= 2:
        print('\n' + '=' * 70)
        print('PER-SYSTEM BREAKDOWN')
        print('=' * 70)
        for sys_data in data['galaxy']['systems']:
            ss = sys_data['system_summary']
            loc = sys_data['global_location']
            print(f"\n  {sys_data['name']} @ ({loc['q']},{loc['r']})  "
                  f"region={sys_data['region_id']}  "
                  f"stars={ss['star_count']} planets={ss['planet_count']} "
                  f"storms={ss['storm_count']} warps={ss['warp_point_count']}")

            for star in sys_data['stars']:
                print(f"    Star: {star['name']}  type={star['star_type']}  "
                      f"mass={star['mass_solar']:.2f}Msol  "
                      f"temp={star['temperature_k']:.0f}K  "
                      f"lum={star['luminosity_solar']:.3f}Lsol  "
                      f"hex_r={star['radius_hexes']}")

            for p in sys_data['planets']:
                res_str = '  '.join(
                    f"{k}={v['quantity']:,.0f}" for k, v in p['resources'].items()
                )
                print(f"    Planet: {p['name']}  type={p['planet_type']}  "
                      f"orbit={p['orbit_distance']}  "
                      f"mass={p['mass_kg']:.2e}kg  "
                      f"grav={p['surface_gravity_ms2']:.2f}m/s²  "
                      f"temp={p['surface_temperature_k']:.0f}K  "
                      f"water={p['surface_water']:.2f}  "
                      f"hab={p['habitability_reference']:.3f}")
                print(f"             {res_str}")

            for storm in sys_data['storms']:
                print(f"    Storm: {storm['name']}  type={storm['storm_type']}  "
                      f"hexes={storm['hex_count']}  intensity={storm['intensity']:.2f}")

    print()


# ---------------------------------------------------------------------------
# Batch mode
# ---------------------------------------------------------------------------

def run_batch(args):
    """Generate multiple galaxies and compute aggregate statistics."""
    n = args.batch
    base_seed = args.seed if args.seed is not None else random.randint(0, 999999)
    radius = args.radius if args.radius else calculate_radius(args.systems)

    print(f"Batch mode: generating {n} galaxies (seeds {base_seed}-{base_seed + n - 1})")
    print(f"  type={args.type}  systems={args.systems}  radius={radius}")

    all_metrics = []
    seeds_used = []
    total_time = 0

    for i in range(n):
        seed = base_seed + i
        seeds_used.append(seed)

        t0 = time.time()
        galaxy = generate_galaxy(seed, args.systems, args.type, radius, args.region_mode)
        gen_time = time.time() - t0
        total_time += gen_time

        metrics = compute_balance_metrics(galaxy)
        all_metrics.append(metrics)

        if args.verbosity >= 1:
            print(f"  [{i+1}/{n}] seed={seed}  systems={metrics['total_systems']}  "
                  f"planets={metrics['total_planets']}  time={gen_time:.2f}s")

    # Compute aggregates
    aggregate = _compute_batch_aggregates(all_metrics)

    batch_result = {
        'batch_metadata': {
            'batch_size': n,
            'base_seed': base_seed,
            'seeds_used': seeds_used,
            'system_count': args.systems,
            'galaxy_type': args.type,
            'galaxy_radius': radius,
            'region_mode': args.region_mode,
            'total_generation_time_seconds': round(total_time, 3),
            'timestamp': datetime.now(timezone.utc).isoformat(),
        },
        'aggregate_metrics': aggregate,
        'individual_runs': [
            {'seed': seeds_used[i], 'balance_metrics': all_metrics[i]}
            for i in range(n)
        ],
    }

    # Save
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f'batch_{base_seed}_{n}runs.json'
    with open(out_path, 'w') as f:
        json.dump(batch_result, f, indent=2, default=str)
    print(f"\nBatch results saved to: {out_path}")

    # Print batch summary
    if args.verbosity >= 1:
        _print_batch_summary(aggregate, n)

    # Charts
    if args.charts:
        _generate_batch_charts(all_metrics, seeds_used, output_dir)

    return batch_result


def _compute_batch_aggregates(all_metrics):
    """Compute cross-run aggregate statistics."""
    n = len(all_metrics)

    def _agg(values):
        if not values:
            return {'avg': 0, 'stddev': 0, 'min': 0, 'max': 0}
        return {
            'avg': round(statistics.mean(values), 2),
            'stddev': round(statistics.stdev(values), 2) if len(values) > 1 else 0,
            'min': round(min(values), 2),
            'max': round(max(values), 2),
        }

    # Planet type counts across runs
    planet_type_agg = {}
    all_pt_names = set()
    for m in all_metrics:
        all_pt_names.update(m['planet_type_distribution'].keys())
    for pt_name in sorted(all_pt_names):
        counts = [m['planet_type_distribution'].get(pt_name, {}).get('count', 0) for m in all_metrics]
        planet_type_agg[pt_name] = _agg(counts)

    # Star type counts across runs
    star_type_agg = {}
    all_st_names = set()
    for m in all_metrics:
        all_st_names.update(m['star_type_distribution'].keys())
    for st_name in sorted(all_st_names):
        counts = [m['star_type_distribution'].get(st_name, {}).get('count', 0) for m in all_metrics]
        star_type_agg[st_name] = _agg(counts)

    # Resource distribution
    resource_agg = {}
    for res_name in PLANET_RESOURCES:
        totals = [m['resource_distribution'][res_name]['quantity']['total'] for m in all_metrics]
        avgs = [m['resource_distribution'][res_name]['quantity']['avg'] for m in all_metrics]
        resource_agg[res_name] = {
            'total': _agg(totals),
            'per_planet_avg': _agg(avgs),
        }

    # Habitability
    hab_avgs = [m['habitability_distribution']['avg'] for m in all_metrics]
    hab_maxes = [m['habitability_distribution']['max'] for m in all_metrics]

    # Connectivity
    warp_lanes = [m['connectivity']['total_warp_lanes'] for m in all_metrics]
    isolated = [m['connectivity']['isolated_systems'] for m in all_metrics]

    # Totals
    total_planets = [m['total_planets'] for m in all_metrics]
    total_systems = [m['total_systems'] for m in all_metrics]

    return {
        'totals': {
            'systems': _agg(total_systems),
            'planets': _agg(total_planets),
        },
        'planet_type_distribution': planet_type_agg,
        'star_type_distribution': star_type_agg,
        'resource_distribution': resource_agg,
        'habitability': {
            'mean_across_runs': _agg(hab_avgs),
            'max_across_runs': _agg(hab_maxes),
        },
        'connectivity': {
            'warp_lanes': _agg(warp_lanes),
            'isolated_systems': _agg(isolated),
        },
    }


def _print_batch_summary(aggregate, n):
    """Print aggregate batch statistics."""
    print('\n' + '=' * 70)
    print(f'BATCH AGGREGATE ({n} runs)')
    print('=' * 70)

    t = aggregate['totals']
    print(f"  Systems: avg={t['systems']['avg']:.0f}  Planets: avg={t['planets']['avg']:.0f}")

    print('\nPlanet Types (avg count per galaxy):')
    for pt_name, stats in sorted(aggregate['planet_type_distribution'].items(), key=lambda x: -x[1]['avg']):
        print(f"  {pt_name:<14} avg={stats['avg']:>5.1f}  stddev={stats['stddev']:>5.1f}  "
              f"range=[{stats['min']:.0f}, {stats['max']:.0f}]")

    print('\nResources (total per galaxy):')
    for res_name in PLANET_RESOURCES:
        s = aggregate['resource_distribution'][res_name]['total']
        print(f"  {res_name:<14} avg={s['avg']:>12,.0f}  stddev={s['stddev']:>10,.0f}  "
              f"range=[{s['min']:,.0f}, {s['max']:,.0f}]")

    hab = aggregate['habitability']
    print(f"\nHabitability: mean={hab['mean_across_runs']['avg']:.3f}±{hab['mean_across_runs']['stddev']:.3f}  "
          f"best_planet={hab['max_across_runs']['avg']:.3f}±{hab['max_across_runs']['stddev']:.3f}")

    conn = aggregate['connectivity']
    print(f"Connectivity: warp_lanes={conn['warp_lanes']['avg']:.0f}±{conn['warp_lanes']['stddev']:.0f}  "
          f"isolated={conn['isolated_systems']['avg']:.1f}")
    print()


# ---------------------------------------------------------------------------
# Chart generation
# ---------------------------------------------------------------------------

def _generate_charts(data, output_dir):
    """Generate visual charts for a single galaxy run."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print("WARNING: matplotlib not installed, skipping charts. Install with: pip install matplotlib")
        return

    charts_dir = Path(output_dir) / 'charts'
    charts_dir.mkdir(parents=True, exist_ok=True)

    metrics = data['balance_metrics']

    # 1. Planet type histogram
    fig, ax = plt.subplots(figsize=(12, 6))
    pt_data = metrics['planet_type_distribution']
    names = sorted(pt_data.keys(), key=lambda x: -pt_data[x]['count'])
    counts = [pt_data[n]['count'] for n in names]
    ax.bar(names, counts, color='steelblue')
    ax.set_title('Planet Type Distribution')
    ax.set_ylabel('Count')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    fig.savefig(charts_dir / 'planet_types.png', dpi=150)
    plt.close(fig)

    # 2. Star type distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    st_data = metrics['star_type_distribution']
    names = sorted(st_data.keys(), key=lambda x: -st_data[x]['count'])
    counts = [st_data[n]['count'] for n in names]
    ax.bar(names, counts, color='goldenrod')
    ax.set_title('Star Type Distribution')
    ax.set_ylabel('Count')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    fig.savefig(charts_dir / 'star_types.png', dpi=150)
    plt.close(fig)

    # 3. Resource distribution box plots
    fig, ax = plt.subplots(figsize=(12, 6))
    res_data = []
    res_labels = []
    for sys_data in data['galaxy']['systems']:
        for p in sys_data['planets']:
            for res_name in PLANET_RESOURCES:
                r = p['resources'].get(res_name, {})
                res_data.append(r.get('quantity', 0))
                res_labels.append(res_name)

    # Group by resource
    grouped = {r: [] for r in PLANET_RESOURCES}
    for val, label in zip(res_data, res_labels):
        grouped[label].append(val)

    box_data = [grouped[r] for r in PLANET_RESOURCES if grouped[r]]
    box_labels = [r for r in PLANET_RESOURCES if grouped[r]]
    if box_data:
        ax.boxplot(box_data, labels=box_labels)
        ax.set_title('Resource Quantity Distribution per Planet')
        ax.set_ylabel('Quantity')
        plt.tight_layout()
        fig.savefig(charts_dir / 'resource_distribution.png', dpi=150)
    plt.close(fig)

    # 4. Habitability histogram
    fig, ax = plt.subplots(figsize=(10, 6))
    hab = metrics['habitability_distribution']
    bucket_labels = [b['range'] for b in hab['histogram']]
    bucket_counts = [b['count'] for b in hab['histogram']]
    ax.bar(bucket_labels, bucket_counts, color='forestgreen')
    ax.set_title(f"Habitability Distribution (avg={hab['avg']:.3f})")
    ax.set_xlabel('Habitability Score')
    ax.set_ylabel('Planet Count')
    plt.tight_layout()
    fig.savefig(charts_dir / 'habitability.png', dpi=150)
    plt.close(fig)

    print(f"  Charts saved to: {charts_dir}")


def _generate_galaxy_map(galaxy, output_dir):
    """Generate galaxy map PNG using PIL (adapted from galaxy_screenshot.py)."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("WARNING: Pillow not installed, skipping galaxy map. Install with: pip install Pillow")
        return

    WIDTH, HEIGHT = 1920, 1080
    img = Image.new('RGB', (WIDTH, HEIGHT), (15, 20, 30))
    draw = ImageDraw.Draw(img)

    REGION_COLORS = [
        (255, 100, 100), (100, 255, 100), (100, 150, 255),
        (255, 200, 50), (200, 100, 255), (100, 255, 255),
        (255, 150, 100), (200, 200, 200),
    ]

    if not galaxy.systems:
        return

    hex_size = 10.0
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')

    for sys in galaxy.systems.values():
        px, py = hex_to_pixel(sys.global_location, hex_size)
        min_x = min(min_x, px)
        max_x = max(max_x, px)
        min_y = min(min_y, py)
        max_y = max(max_y, py)

    margin = 100
    world_w = max_x - min_x + margin * 2
    world_h = max_y - min_y + margin * 2
    zoom = min(WIDTH / world_w if world_w > 0 else 1, HEIGHT / world_h if world_h > 0 else 1)
    cx = (min_x + max_x) / 2
    cy = (min_y + max_y) / 2

    def w2s(wx, wy):
        return int((wx - cx) * zoom + WIDTH / 2), int((wy - cy) * zoom + HEIGHT / 2)

    # Warp lanes
    drawn = set()
    for sys in galaxy.systems.values():
        sx, sy = hex_to_pixel(sys.global_location, hex_size)
        for wp in sys.warp_points:
            pair = tuple(sorted([sys.name, wp.destination_id]))
            if pair in drawn:
                continue
            drawn.add(pair)
            target = galaxy.get_system_by_name(wp.destination_id)
            if not target:
                continue
            tx, ty = hex_to_pixel(target.global_location, hex_size)
            if sys.region_id is not None and target.region_id is not None and sys.region_id != target.region_id:
                color = (255, 80, 80)
            else:
                color = (40, 60, 80)
            draw.line([w2s(sx, sy), w2s(tx, ty)], fill=color, width=1)

    # Systems
    for sys in galaxy.systems.values():
        px, py = hex_to_pixel(sys.global_location, hex_size)
        x, y = w2s(px, py)
        r = max(2, int(4 * zoom))
        if sys.region_id is not None:
            color = REGION_COLORS[sys.region_id % len(REGION_COLORS)]
        else:
            color = (200, 200, 100)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color)

    charts_dir = Path(output_dir) / 'charts'
    charts_dir.mkdir(parents=True, exist_ok=True)
    img.save(charts_dir / 'galaxy_map.png')
    print(f"  Galaxy map saved to: {charts_dir / 'galaxy_map.png'}")


def _generate_batch_charts(all_metrics, seeds, output_dir):
    """Generate comparison charts across batch runs."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print("WARNING: matplotlib not installed, skipping batch charts.")
        return

    charts_dir = Path(output_dir) / 'charts'
    charts_dir.mkdir(parents=True, exist_ok=True)

    # Resource totals across runs
    fig, ax = plt.subplots(figsize=(12, 6))
    for res_name in PLANET_RESOURCES:
        totals = [m['resource_distribution'][res_name]['quantity']['total'] for m in all_metrics]
        ax.plot(range(len(totals)), totals, marker='o', label=res_name, markersize=4)
    ax.set_title('Resource Totals Across Runs')
    ax.set_xlabel('Run #')
    ax.set_ylabel('Total Quantity')
    ax.legend()
    plt.tight_layout()
    fig.savefig(charts_dir / 'batch_resources.png', dpi=150)
    plt.close(fig)

    # Planet count variation
    fig, ax = plt.subplots(figsize=(10, 6))
    planet_counts = [m['total_planets'] for m in all_metrics]
    ax.bar(range(len(planet_counts)), planet_counts, color='steelblue')
    ax.set_title('Total Planets per Run')
    ax.set_xlabel('Run #')
    ax.set_ylabel('Planet Count')
    ax.axhline(y=statistics.mean(planet_counts), color='red', linestyle='--', label=f'Mean={statistics.mean(planet_counts):.0f}')
    ax.legend()
    plt.tight_layout()
    fig.savefig(charts_dir / 'batch_planet_counts.png', dpi=150)
    plt.close(fig)

    # Habitability means across runs
    fig, ax = plt.subplots(figsize=(10, 6))
    hab_means = [m['habitability_distribution']['avg'] for m in all_metrics]
    hab_maxes = [m['habitability_distribution']['max'] for m in all_metrics]
    x = range(len(hab_means))
    ax.plot(x, hab_means, marker='o', label='Mean Habitability', markersize=4)
    ax.plot(x, hab_maxes, marker='s', label='Max Habitability', markersize=4)
    ax.set_title('Habitability Across Runs')
    ax.set_xlabel('Run #')
    ax.set_ylabel('Score')
    ax.legend()
    plt.tight_layout()
    fig.savefig(charts_dir / 'batch_habitability.png', dpi=150)
    plt.close(fig)

    print(f"  Batch charts saved to: {charts_dir}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_single(args):
    """Generate and inspect a single galaxy."""
    seed = args.seed if args.seed is not None else random.randint(0, 999999)
    radius = args.radius if args.radius else calculate_radius(args.systems)

    if args.verbosity >= 1:
        print(f"Generating galaxy: seed={seed}  type={args.type}  "
              f"systems={args.systems}  radius={radius}")

    t0 = time.time()
    galaxy = generate_galaxy(seed, args.systems, args.type, radius, args.region_mode)
    gen_time = time.time() - t0

    data = extract_galaxy_json(galaxy, seed, args.systems, args.type, radius, args.region_mode, gen_time)

    # Save JSON
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f'galaxy_{seed}.json'
    with open(out_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)

    if args.verbosity >= 1:
        print(f"JSON saved to: {out_path}")

    # Console summary
    print_summary(data, args.verbosity)

    # Charts
    if args.charts:
        _generate_galaxy_map(galaxy, output_dir)
        _generate_charts(data, output_dir)

    return data


def main():
    parser = argparse.ArgumentParser(
        description='Galaxy generation inspector for balancing feedback loops.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  %(prog)s --seed 42
  %(prog)s --seed 42 --systems 100 --type spiral
  %(prog)s --batch 10 --seed 1000 --type cluster
  %(prog)s --seed 42 --charts --output ./output/review
  %(prog)s --seed 42 -v 0
""")
    parser.add_argument('--seed', type=int, default=None,
                        help='RNG seed for reproducibility (default: random)')
    parser.add_argument('--systems', type=int, default=25,
                        help='Number of star systems (default: 25)')
    parser.add_argument('--type', choices=VALID_GALAXY_TYPES, default='random',
                        help='Galaxy layout type (default: random)')
    parser.add_argument('--radius', type=int, default=None,
                        help='Galaxy radius in hex units (default: auto-calculated)')
    parser.add_argument('--output', '-o', default='./output/galaxy_inspect',
                        help='Output directory (default: ./output/galaxy_inspect)')
    parser.add_argument('--batch', type=int, default=None, metavar='N',
                        help='Batch mode: generate N galaxies and show aggregate stats')
    parser.add_argument('--charts', action='store_true',
                        help='Generate PNG charts (requires matplotlib and Pillow)')
    parser.add_argument('-v', '--verbosity', type=int, default=1, choices=[0, 1, 2],
                        help='Verbosity: 0=JSON only, 1=summary (default), 2=detailed')
    parser.add_argument('--region-mode', dest='region_mode', default='normal',
                        choices=['normal', 'limited', 'minimal'],
                        help='Inter-region warp mode (default: normal)')

    args = parser.parse_args()

    if args.batch:
        run_batch(args)
    else:
        run_single(args)


if __name__ == '__main__':
    main()

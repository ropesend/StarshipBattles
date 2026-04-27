"""Galaxy warp lane generation module.

Extracted from Galaxy as part of PROJ-173 Phase 2 (internal delegation pattern).
This module handles all warp lane generation logic including MST connectivity
and density edge creation.
"""
import math
import random
from typing import List, Optional, TYPE_CHECKING

from game.core.hex_math import hex_distance, hex_to_pixel, pixel_to_hex

if TYPE_CHECKING:
    from game.strategy.data.galaxy import Galaxy, StarSystem
    from game.strategy.generation.region_classifier import RegionClassifier


class GalaxyWarpGenerator:
    """Stateless warp lane generator for Galaxy.

    Handles all warp lane generation logic:
    - MST (minimum spanning tree) for guaranteed connectivity
    - Density edges for additional connections
    - Angle validation to avoid overlapping warp points
    - Region-aware generation with inter-region link limits
    """

    def _calculate_warp_distance(self, system: 'StarSystem') -> float:
        """Calculate the distance for a warp point based on the primary star's size.

        Formula: Base (15) + (Star Radius * 3.0) + Random(-2 to 5)
        Min Distance: 10

        Args:
            system: StarSystem to calculate warp distance for.

        Returns:
            Distance in hex units for warp point placement.
        """
        star_radius = 1
        if system.primary_star:
            star_radius = system.primary_star.radius_hexes

        base_dist = 15.0
        scaled_dist = base_dist + (star_radius * 3.0)  # radius * 3.0 preserves proportional relationship
        jitter = random.uniform(-2.0, 5.0)

        total_dist = scaled_dist + jitter
        return max(10.0, total_dist)

    def _is_angle_clear(self, system: 'StarSystem', target_angle_rad: float, threshold_deg: float = 30) -> bool:
        """Check if a target angle is clear of existing warp lines.

        Args:
            system: StarSystem to check angles for.
            target_angle_rad: Target angle in radians.
            threshold_deg: Minimum angle difference required (default 30 degrees).

        Returns:
            True if the angle difference to all existing lines is >= threshold.
        """
        if not system.warp_points:
            return True

        threshold_rad = math.radians(threshold_deg)

        for wp in system.warp_points:
            # Calculate angle of existing WP
            # We need to convert hex location to angle relative to system center (0,0)
            # Local hex coords are relative to system center.
            wx, wy = hex_to_pixel(wp.location, 1.0)
            existing_angle = math.atan2(wy, wx)

            diff = abs(target_angle_rad - existing_angle)
            # Normalize to 0-PI
            while diff > math.pi:
                diff -= 2 * math.pi
            diff = abs(diff)

            if diff < threshold_rad:
                return False

        return True

    def create_warp_link(self, sys_a: 'StarSystem', sys_b: 'StarSystem') -> None:
        """Create a warp link between two systems.

        Args:
            sys_a: First system.
            sys_b: Second system.
        """
        for wp in sys_a.warp_points:
            if wp.destination_id == sys_b.name:
                return

        # 1. Determine direction in Global Map
        ax, ay = hex_to_pixel(sys_a.global_location, 1.0)
        bx, by = hex_to_pixel(sys_b.global_location, 1.0)

        angle_a_to_b = math.atan2(by - ay, bx - ax)
        angle_b_to_a = math.atan2(ay - by, ax - bx)

        # 2. Place Warp Point at System Edge (Local Map)

        dist_a = self._calculate_warp_distance(sys_a)
        dist_b = self._calculate_warp_distance(sys_b)

        # hex_to_pixel(size=1) scales x by 1.5.

        # For A -> B
        projection_dist_a = dist_a * 1.5
        local_ax = math.cos(angle_a_to_b) * projection_dist_a
        local_ay = math.sin(angle_a_to_b) * projection_dist_a
        loc_a = pixel_to_hex(local_ax, local_ay, 1.0)

        # For B -> A
        projection_dist_b = dist_b * 1.5
        local_bx = math.cos(angle_b_to_a) * projection_dist_b
        local_by = math.sin(angle_b_to_a) * projection_dist_b
        loc_b = pixel_to_hex(local_bx, local_by, 1.0)

        sys_a.add_warp_point(sys_b.name, loc_a)
        sys_b.add_warp_point(sys_a.name, loc_b)

    def _build_edge_candidates(
        self,
        systems: List['StarSystem'],
        spatial_index,
        k_neighbors: int
    ) -> List[tuple]:
        """Build sorted (dist, i, j) edge list using k-nearest neighbors.

        Computes edges via k-nearest neighbor queries on the spatial index,
        deduplicates, calculates distances, and returns sorted by distance.

        Args:
            systems: Ordered list of star systems (index = system ID).
            spatial_index: SpatialIndex populated with system coordinates.
            k_neighbors: Number of nearest neighbors to consider per system.

        Returns:
            List of (distance, i, j) tuples sorted by distance ascending.
        """
        edge_set = set()  # Avoid duplicates
        for i, sys in enumerate(systems):
            neighbors = spatial_index.get_k_nearest(
                sys.global_location,
                k=k_neighbors,
                exclude_coord=sys.global_location
            )
            for neighbor_coord, j in neighbors:
                if i < j:
                    edge_set.add((i, j))
                else:
                    edge_set.add((j, i))

        # Convert to edge list with distances
        edges = []
        for i, j in edge_set:
            dist = hex_distance(systems[i].global_location, systems[j].global_location)
            edges.append((dist, i, j))

        # Sort by distance (asc)
        edges.sort(key=lambda x: x[0])
        return edges

    def _apply_mst_edges(
        self,
        systems: List['StarSystem'],
        edges: List[tuple]
    ) -> None:
        """Apply Kruskal's MST algorithm to ensure full connectivity.

        Uses union-find with path compression to build a minimum spanning
        tree over the edge candidates. Creates warp links for all MST edges.

        Args:
            systems: Ordered list of star systems (index = system ID).
            edges: Sorted list of (distance, i, j) edge tuples.
        """
        parent = list(range(len(systems)))

        def find(i) -> int:
            if parent[i] == i:
                return i
            parent[i] = find(parent[i])
            return parent[i]

        def union(i, j) -> bool:
            root_i = find(i)
            root_j = find(j)
            if root_i != root_j:
                parent[root_i] = root_j
                return True
            return False

        for dist, i, j in edges:
            if union(i, j):
                self.create_warp_link(systems[i], systems[j])

    def _should_add_density_edge(
        self,
        s_i: 'StarSystem',
        s_j: 'StarSystem',
        dist: float,
        region_classifier: 'Optional[RegionClassifier]',
        inter_region_mode: str,
        inter_region_links: dict
    ) -> bool:
        """Evaluate whether a single density edge candidate should be added.

        Checks degree caps, existing links, region constraints, angle
        validation, and probability calculation. Consumes one random.random()
        call for candidates that pass all pre-checks.

        Args:
            s_i: Source system.
            s_j: Destination system.
            dist: Distance between the two systems.
            region_classifier: Optional RegionClassifier for region filtering.
            inter_region_mode: Region connection mode ('normal', 'limited', 'minimal').
            inter_region_links: Mutable dict tracking inter-region link counts.

        Returns:
            True if the edge should be created, False otherwise.
        """
        # Skip if already linked (MST covered it)
        already_linked = any(wp.destination_id == s_j.name for wp in s_i.warp_points)
        if already_linked:
            return False

        # Cap degree logic: "3 to 10 warp points"
        deg_i = len(s_i.warp_points)
        deg_j = len(s_j.warp_points)

        if deg_i >= 10 or deg_j >= 10:
            return False

        # Check region constraints
        if region_classifier and inter_region_mode != 'normal':
            region_i = s_i.region_id
            region_j = s_j.region_id

            if region_i is not None and region_j is not None and region_i != region_j:
                # This is an inter-region edge
                if inter_region_mode == 'minimal':
                    # Only MST edges allowed between regions
                    return False
                elif inter_region_mode == 'limited':
                    # Allow limited inter-region links
                    region_pair = (min(region_i, region_j), max(region_i, region_j))
                    current_count = inter_region_links.get(region_pair, 0)
                    if current_count >= 2:
                        return False

        # Check Angle Preference
        # Calculate intended angle for both
        ax, ay = hex_to_pixel(s_i.global_location, 1.0)
        bx, by = hex_to_pixel(s_j.global_location, 1.0)
        angle_i_to_j = math.atan2(by - ay, bx - ax)
        angle_j_to_i = math.atan2(ay - by, ax - bx)

        # If angles are bad, reduce chance drastically or skip
        # Preference: "prefer to have at least 30 degrees... if necessary... ok"
        valid_angles = True
        if not self._is_angle_clear(s_i, angle_i_to_j, threshold_deg=30):
            valid_angles = False
        if not self._is_angle_clear(s_j, angle_j_to_i, threshold_deg=30):
            valid_angles = False

        # If degree is low, boost chance
        base_chance = 40.0 / (dist + 1)  # Arbitrary tuning

        if deg_i < 3 or deg_j < 3:
            base_chance *= 3.0  # Boost to help them get up to min

        # Penalize bad angles
        if not valid_angles:
            # If degrees are decent (>3), strictly reject (or very low chance)
            # If degrees are low (<3), allow with penalty because "if it is necessary... that is ok"
            if deg_i > 3 and deg_j > 3:
                return False
            else:
                base_chance *= 0.1  # Severe penalty

        return random.random() < base_chance

    def _add_density_edges(
        self,
        systems: List['StarSystem'],
        edges: List[tuple],
        region_classifier: 'Optional[RegionClassifier]',
        inter_region_mode: str
    ) -> None:
        """Add additional random edges beyond the MST to meet density targets.

        Iterates all edge candidates, evaluates each with
        _should_add_density_edge, creates warp links for accepted edges,
        and tracks inter-region link counts.

        Args:
            systems: Ordered list of star systems (index = system ID).
            edges: Sorted list of (distance, i, j) edge tuples.
            region_classifier: Optional RegionClassifier for region filtering.
            inter_region_mode: Region connection mode ('normal', 'limited', 'minimal').
        """
        # Track inter-region links for 'limited' mode
        inter_region_links = {}  # (min_region, max_region) -> count

        for dist, i, j in edges:
            s_i, s_j = systems[i], systems[j]

            if self._should_add_density_edge(
                s_i, s_j, dist,
                region_classifier, inter_region_mode, inter_region_links
            ):
                self.create_warp_link(s_i, s_j)

                # Track inter-region link
                if region_classifier and inter_region_mode == 'limited':
                    region_i = s_i.region_id
                    region_j = s_j.region_id
                    if region_i is not None and region_j is not None and region_i != region_j:
                        region_pair = (min(region_i, region_j), max(region_i, region_j))
                        inter_region_links[region_pair] = inter_region_links.get(region_pair, 0) + 1

    def generate_warp_lanes(
        self,
        galaxy: 'Galaxy',
        k_neighbors: int = 20,
        region_classifier: 'Optional[RegionClassifier]' = None,
        inter_region_mode: str = 'normal'
    ) -> None:
        """Generate warp lanes ensuring connectivity (MST) and adding density.

        Uses spatial indexing with k-nearest neighbors for O(n*k) performance
        instead of O(n²) all-pairs computation.

        Args:
            galaxy: Galaxy instance to generate warp lanes for.
            k_neighbors: Number of nearest neighbors to consider per system.
                         Higher values = more edges to consider, slower but
                         potentially better connectivity. Default 20.
            region_classifier: Optional RegionClassifier for region-aware
                         warp lane generation. If provided, inter-region
                         connections are penalized based on inter_region_mode.
            inter_region_mode: How to handle inter-region connections:
                         - 'normal': No region restrictions (default)
                         - 'limited': Allow 1-2 inter-region links per region pair
                         - 'minimal': Only allow MST-required inter-region links
        """
        from game.strategy.data.spatial_index import SpatialIndex

        systems = list(galaxy.systems.values())
        if len(systems) < 2:
            return

        # Build spatial index for efficient neighbor lookup
        spatial_index = SpatialIndex(cell_size=500)
        for i, sys in enumerate(systems):
            spatial_index.add(sys.global_location, i)

        # 1. Build sorted edge candidates via k-nearest neighbors
        edges = self._build_edge_candidates(systems, spatial_index, k_neighbors)

        # 2. Apply MST for guaranteed connectivity
        self._apply_mst_edges(systems, edges)

        # 3. Add density edges beyond MST
        self._add_density_edges(systems, edges, region_classifier, inter_region_mode)

        # 4. PROJ-303: roll warp_type + intrinsic abilities for each generated point.
        _apply_warp_point_intrinsic_abilities(systems)


# PROJ-303 — module-level warp point intrinsics helper.
_WARP_POINT_TYPES_CACHE = None


def _load_warp_point_types() -> dict:
    global _WARP_POINT_TYPES_CACHE
    if _WARP_POINT_TYPES_CACHE is None:
        from pathlib import Path
        import json
        from game.core.paths import Paths

        path = Path(Paths.WARP_POINT_TYPES_FILE)
        if path.exists():
            with path.open('r', encoding='utf-8') as f:
                data = json.load(f)
            _WARP_POINT_TYPES_CACHE = data.get('warp_point_types', {})
        else:
            _WARP_POINT_TYPES_CACHE = {}
    return _WARP_POINT_TYPES_CACHE


# Default weighted distribution for warp_type rolls. Most warp points are stable.
_DEFAULT_WARP_TYPE_WEIGHTS = [
    ('stable', 80),
    ('unstable', 10),
    ('dimensional_rift', 7),
    ('precursor_gateway', 3),
]


def _roll_warp_type(rng) -> str:
    total = sum(w for _, w in _DEFAULT_WARP_TYPE_WEIGHTS)
    pick = rng.randint(1, total)
    cumulative = 0
    for type_name, weight in _DEFAULT_WARP_TYPE_WEIGHTS:
        cumulative += weight
        if pick <= cumulative:
            return type_name
    return 'stable'


def _apply_warp_point_intrinsic_abilities(systems) -> None:
    """PROJ-303: roll warp_type + intrinsic abilities for each warp point."""
    import random as _random
    from game.strategy.services.ability_sources import roll_intrinsic_abilities

    types_data = _load_warp_point_types()
    if not types_data:
        return

    rng = _random.Random()
    for system in systems:
        for wp in getattr(system, 'warp_points', []) or []:
            # Idempotent: respect pre-set warp_type from scenarios.
            if wp.warp_type and wp.warp_type != 'stable':
                continue
            if wp.intrinsic_abilities:
                continue
            wp.warp_type = _roll_warp_type(rng)
            template = types_data.get(wp.warp_type, {}).get('abilities', {})
            if template:
                wp.intrinsic_abilities = roll_intrinsic_abilities(template, rng)

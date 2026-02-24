"""
Region classifier for galaxy layouts.

Determines which region (arm/cluster) a star system belongs to based
on the galaxy layout configuration.
"""

import math
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple

from game.core.hex_math import HexCoord, hex_axial_to_cartesian


@dataclass
class RegionInfo:
    """Information about a region in the galaxy.

    Attributes:
        region_id: Unique identifier for this region (0-indexed)
        region_type: Type of region ('arm', 'cluster', 'core', 'bar', 'ring')
        name: Human-readable name (e.g., 'Arm 0', 'Cluster 3')
    """
    region_id: int
    region_type: str
    name: str


class RegionClassifier:
    """Classifies star systems into regions based on layout.

    Supports spiral arms, clusters, and other layout types.
    All configuration is parsed once at initialization for fast classification.
    """

    def __init__(self, layout_config: Dict[str, Any], galaxy_radius: int):
        """Initialize the classifier with a layout configuration.

        Args:
            layout_config: Scaled layout configuration from GalaxyLayoutsLoader
            galaxy_radius: Galaxy radius in hex units
        """
        self._config = layout_config
        self._radius = galaxy_radius

        # Parse primitives once
        primitives = self._config.get('primitives', [])

        # Detect layout type once
        self._has_spiral = any(p.get('type') == 'spiral_arm' for p in primitives)
        self._has_clusters = sum(1 for p in primitives if p.get('type') == 'radial' and p.get('weight', 0) > 0.1) > 1
        self._has_bar = any(p.get('type') == 'linear' for p in primitives)
        self._has_ring = any(p.get('type') == 'ring' for p in primitives)

        # Cache spiral parameters
        self._spiral_params = None
        self._core_params = None
        if self._has_spiral:
            for prim in primitives:
                if prim.get('type') == 'spiral_arm':
                    self._spiral_params = {
                        'center_q': prim.get('center_q', 0),
                        'center_r': prim.get('center_r', 0),
                        'arm_count': prim.get('arm_count', 2),
                        'pitch_angle': prim.get('pitch_angle', 20.0),
                        'rotation': prim.get('rotation', 0),
                    }
                    # Pre-compute pitch values
                    pitch_rad = math.radians(self._spiral_params['pitch_angle'])
                    if abs(pitch_rad) >= 0.001:
                        self._spiral_params['b'] = 1.0 / math.tan(pitch_rad)
                    else:
                        self._spiral_params['b'] = 0
                    self._spiral_params['arm_spacing'] = 2.0 * math.pi / max(1, self._spiral_params['arm_count'])
                elif prim.get('type') == 'radial' and prim.get('weight', 0) >= 0.1:
                    self._core_params = {
                        'center_q': prim.get('center_q', 0),
                        'center_r': prim.get('center_r', 0),
                        'sigma': prim.get('sigma', 100),
                    }
                    # Pre-compute threshold
                    self._core_params['threshold_sq'] = (self._core_params['sigma'] * 1.5) ** 2

        # Cache cluster centers
        self._cluster_centers: List[Tuple[float, float, float]] = []
        if self._has_clusters:
            for prim in primitives:
                if prim.get('type') == 'radial' and prim.get('weight', 0) > 0.1:
                    self._cluster_centers.append((
                        prim.get('center_q', 0),
                        prim.get('center_r', 0),
                        prim.get('sigma', 100)
                    ))

        # Build regions list
        self._regions = self._build_regions()

    def _build_regions(self) -> List[RegionInfo]:
        """Build list of regions from cached configuration."""
        regions = []

        if self._has_spiral and self._spiral_params:
            arm_count = self._spiral_params['arm_count']
            for i in range(arm_count):
                regions.append(RegionInfo(i, 'arm', f'Arm {i}'))
            # Core is a separate region if present
            if self._core_params:
                regions.append(RegionInfo(arm_count, 'core', 'Core'))
        elif self._has_clusters:
            for i in range(len(self._cluster_centers)):
                regions.append(RegionInfo(i, 'cluster', f'Cluster {i}'))
        elif self._has_ring:
            regions.append(RegionInfo(0, 'ring', 'Ring'))
            regions.append(RegionInfo(1, 'core', 'Core'))
        elif self._has_bar:
            regions.append(RegionInfo(0, 'bar', 'Central Bar'))

        return regions

    @property
    def regions(self) -> List[RegionInfo]:
        """Get list of all regions."""
        return self._regions

    @property
    def region_count(self) -> int:
        """Get number of regions."""
        return len(self._regions)

    def classify(self, coord: HexCoord) -> int:
        """Classify a coordinate into a region.

        Args:
            coord: Hex coordinate to classify

        Returns:
            Region ID (0-indexed). Returns 0 if no regions defined.
        """
        if not self._regions:
            return 0

        if self._has_spiral:
            return self._classify_spiral(coord)
        elif self._has_clusters:
            return self._classify_cluster(coord)
        else:
            return 0

    def _classify_spiral(self, coord: HexCoord) -> int:
        """Classify a point in a spiral galaxy.

        Returns the arm index (0 to arm_count-1) for the nearest arm,
        or the core region ID if within the core.
        """
        if not self._spiral_params:
            return 0

        q, r = coord.q, coord.r
        sp = self._spiral_params
        arm_count = sp['arm_count']

        # Check if in core first
        if self._core_params:
            cp = self._core_params
            dq = q - cp['center_q']
            dr = r - cp['center_r']
            dist_sq = dq * dq + dr * dr + dq * dr

            if dist_sq < cp['threshold_sq']:
                return arm_count  # Core is the last region

        # Convert hex axial to Cartesian for spiral math
        x, y = hex_axial_to_cartesian(q, r, sp['center_q'], sp['center_r'])

        distance = math.sqrt(x * x + y * y)
        if distance < 1.0:
            return arm_count if self._core_params else 0

        if sp['b'] == 0:
            return 0

        angle = math.atan2(y, x)
        expected_angle = math.log(max(1.0, distance)) * sp['b'] + sp['rotation']

        # Find which arm is closest
        best_arm = 0
        min_distance = float('inf')

        for arm in range(arm_count):
            arm_angle = expected_angle + arm * sp['arm_spacing']
            diff = angle - arm_angle
            # Normalize to [-pi, pi] using modulo (faster than while loop)
            diff = (diff + math.pi) % (2.0 * math.pi) - math.pi

            linear_distance = abs(diff) * distance
            if linear_distance < min_distance:
                min_distance = linear_distance
                best_arm = arm

        return best_arm

    def _classify_cluster(self, coord: HexCoord) -> int:
        """Classify a point in a cluster galaxy.

        Returns the cluster index (0 to n-1) for the nearest cluster center.
        """
        if not self._cluster_centers:
            return 0

        q, r = coord.q, coord.r
        best_cluster = 0
        min_weighted_dist = float('inf')

        for i, (cq, cr, sigma) in enumerate(self._cluster_centers):
            dq = q - cq
            dr = r - cr
            dist_sq = dq * dq + dr * dr + dq * dr
            # Weight by sigma (smaller clusters have smaller reach)
            weighted_dist = math.sqrt(dist_sq) / max(1.0, sigma)

            if weighted_dist < min_weighted_dist:
                min_weighted_dist = weighted_dist
                best_cluster = i

        return best_cluster

    def get_region_neighbors(self) -> Dict[int, List[int]]:
        """Get neighboring regions for connectivity purposes.

        For spirals: adjacent arms are neighbors (wrapping around)
        For clusters: proximity-based neighbors

        Returns:
            Dict mapping region_id to list of neighbor region_ids
        """
        neighbors = {r.region_id: [] for r in self._regions}

        if not self._regions:
            return neighbors

        if self._has_spiral:
            arm_regions = [r for r in self._regions if r.region_type == 'arm']
            core_regions = [r for r in self._regions if r.region_type == 'core']

            for i, arm in enumerate(arm_regions):
                next_arm = arm_regions[(i + 1) % len(arm_regions)]
                neighbors[arm.region_id].append(next_arm.region_id)
                neighbors[next_arm.region_id].append(arm.region_id)

                for core in core_regions:
                    if core.region_id not in neighbors[arm.region_id]:
                        neighbors[arm.region_id].append(core.region_id)
                    if arm.region_id not in neighbors[core.region_id]:
                        neighbors[core.region_id].append(arm.region_id)

        elif self._has_clusters:
            cluster_regions = [r for r in self._regions if r.region_type == 'cluster']

            for i, (cq1, cr1, _) in enumerate(self._cluster_centers):
                distances = []
                for j, (cq2, cr2, _) in enumerate(self._cluster_centers):
                    if i != j:
                        dq = cq1 - cq2
                        dr = cr1 - cr2
                        dist = math.sqrt(dq*dq + dr*dr + dq*dr)
                        distances.append((dist, j))

                distances.sort()
                for _, j in distances[:3]:
                    if j not in neighbors[i]:
                        neighbors[i].append(j)
                    if i not in neighbors[j]:
                        neighbors[j].append(i)

        return neighbors

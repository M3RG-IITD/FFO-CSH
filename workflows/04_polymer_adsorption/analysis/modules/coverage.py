"""
Module 2: Surface Coverage

Computes the fraction of the CSH surface covered by the adsorbed polymer.
Two methods:
  1. Convex hull of projected polymer xy coordinates
  2. Grid-based: count bins with polymer atoms within cutoff of surface
"""
import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull


def compute_coverage_convex_hull(positions_xy, box_xy):
    """
    Compute surface coverage from convex hull of xy-projected polymer positions.
    
    Returns coverage fraction and hull area.
    """
    Lx, Ly = box_xy
    surface_area = Lx * Ly
    
    if len(positions_xy) < 3:
        return 0.0, 0.0
    
    try:
        hull = ConvexHull(positions_xy)
        coverage = hull.volume / surface_area  # In 2D, "volume" = area
        return coverage, hull.volume
    except Exception:
        return 0.0, 0.0


def compute_coverage_grid(positions_xy, box_xy, grid_spacing=2.0):
    """
    Grid-based surface coverage: divide surface into bins,
    count fraction with at least one polymer atom.
    """
    Lx, Ly = box_xy
    nx = int(Lx / grid_spacing)
    ny = int(Ly / grid_spacing)
    
    grid = np.zeros((nx, ny), dtype=bool)
    
    for x, y in positions_xy:
        ix = int(((x + Lx/2) % Lx) / grid_spacing)
        iy = int(((y + Ly/2) % Ly) / grid_spacing)
        ix = min(ix, nx - 1)
        iy = min(iy, ny - 1)
        grid[ix, iy] = True
    
    coverage = grid.sum() / grid.size
    return coverage


def analyze_coverage(universe, polymer_types, csh_types, equil_frames=700,
                     surface_cutoff=10.0, grid_spacing=2.0, label="system"):
    """
    Compute surface coverage for each production frame.
    
    Only counts polymer atoms within surface_cutoff of the CSH top surface.
    """
    from .utils import select_by_types, get_surface_z
    
    polymer = select_by_types(universe, polymer_types)
    
    results = {
        'frame': [], 'time_ns': [],
        'coverage_hull': [], 'hull_area': [],
        'coverage_grid': [],
    }
    
    for ts in universe.trajectory[equil_frames:]:
        box = universe.dimensions[:3]
        Lx, Ly = box[0], box[1]
        
        # Get surface z
        surface_z = get_surface_z(universe, csh_types)
        
        # Get polymer atoms near surface
        pos = polymer.positions
        near_surface = pos[:, 2] < (surface_z + surface_cutoff)
        pos_near = pos[near_surface]
        
        if len(pos_near) < 3:
            results['frame'].append(ts.frame)
            results['time_ns'].append(ts.time / 1000.0)
            results['coverage_hull'].append(0.0)
            results['hull_area'].append(0.0)
            results['coverage_grid'].append(0.0)
            continue
        
        # Convex hull method
        coverage_hull, hull_area = compute_coverage_convex_hull(
            pos_near[:, :2], (Lx, Ly))
        
        # Grid method
        coverage_grid = compute_coverage_grid(
            pos_near[:, :2], (Lx, Ly), grid_spacing)
        
        results['frame'].append(ts.frame)
        results['time_ns'].append(ts.time / 1000.0)
        results['coverage_hull'].append(coverage_hull)
        results['hull_area'].append(hull_area)
        results['coverage_grid'].append(coverage_grid)
    
    df = pd.DataFrame(results)
    
    summary = {
        'label': label,
        'coverage_hull_mean': df['coverage_hull'].mean() * 100,
        'coverage_hull_std': df['coverage_hull'].std() * 100,
        'coverage_grid_mean': df['coverage_grid'].mean() * 100,
        'coverage_grid_std': df['coverage_grid'].std() * 100,
        'hull_area_mean': df['hull_area'].mean(),
    }
    
    print(f"  [{label}] Coverage (hull): {summary['coverage_hull_mean']:.1f} ± "
          f"{summary['coverage_hull_std']:.1f} %")
    print(f"  [{label}] Coverage (grid): {summary['coverage_grid_mean']:.1f} ± "
          f"{summary['coverage_grid_std']:.1f} %")
    
    return df, summary

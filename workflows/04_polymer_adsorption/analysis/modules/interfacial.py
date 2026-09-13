"""
Module 3: Interfacial Structure Analysis

Computes:
  - Ca-COO contact number and statistics
  - Number density profiles ρ(z)
  - Radial distribution functions g(r)
  - Polymer COM height above surface
  - Backbone orientation angle relative to surface
"""
import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist


# ============================================================
#  CONTACT ANALYSIS
# ============================================================

def compute_contacts(pos_a, pos_b, cutoff, box=None):
    """
    Count contacts between two sets of positions within cutoff.
    Uses minimum image convention if box is provided.
    Returns number of contacts and list of distances.
    """
    if box is not None:
        # Minimum image distances
        delta = pos_a[:, np.newaxis, :] - pos_b[np.newaxis, :, :]
        delta -= box * np.round(delta / box)
        dists = np.sqrt((delta**2).sum(axis=2))
    else:
        dists = cdist(pos_a, pos_b)
    
    contacts = (dists < cutoff).sum()
    contact_dists = dists[dists < cutoff]
    return contacts, contact_dists


def analyze_contacts(universe, coo_types, ca_type, equil_frames=700,
                     cutoff=3.5, label="system"):
    """Compute Ca-COO contacts over production trajectory."""
    from .utils import select_by_types
    
    coo_atoms = select_by_types(universe, coo_types)
    ca_atoms = universe.select_atoms(f"type {ca_type}")
    
    results = {'frame': [], 'time_ns': [], 'n_contacts': [], 'mean_dist': []}
    
    for ts in universe.trajectory[equil_frames:]:
        box = universe.dimensions[:3]
        n_contacts, contact_dists = compute_contacts(
            coo_atoms.positions, ca_atoms.positions, cutoff, box)
        
        results['frame'].append(ts.frame)
        results['time_ns'].append(ts.time / 1000.0)
        results['n_contacts'].append(n_contacts)
        results['mean_dist'].append(np.mean(contact_dists) if len(contact_dists) > 0 else np.nan)
    
    df = pd.DataFrame(results)
    
    summary = {
        'label': label,
        'contacts_mean': df['n_contacts'].mean(),
        'contacts_std': df['n_contacts'].std(),
        'mean_dist': df['mean_dist'].mean(),
    }
    
    print(f"  [{label}] Ca-COO contacts: {summary['contacts_mean']:.1f} ± "
          f"{summary['contacts_std']:.1f}")
    
    return df, summary


# ============================================================
#  DENSITY PROFILES
# ============================================================

def compute_density_profile(universe, type_list, equil_frames=700,
                            nbins=200, label="atoms"):
    """
    Compute number density profile ρ(z) for atoms of given types,
    averaged over production frames.
    """
    from .utils import select_by_types
    
    atoms = select_by_types(universe, type_list)
    
    # Get box bounds from first production frame
    universe.trajectory[equil_frames]
    box = universe.dimensions
    zlo = -box[2] / 2  # centered box assumption
    zhi = box[2] / 2
    
    # Actually get bounds from atom positions
    all_z = []
    n_frames = 0
    hist_sum = None
    
    for ts in universe.trajectory[equil_frames:]:
        z = atoms.positions[:, 2]
        
        if hist_sum is None:
            zmin = universe.dimensions[2] * -0.5 if hasattr(universe, 'dimensions') else z.min() - 5
            zmax = universe.dimensions[2] * 0.5 if hasattr(universe, 'dimensions') else z.max() + 5
            # Use actual coordinate range
            zmin, zmax = z.min() - 2, z.max() + 2
            bins = np.linspace(zmin, zmax, nbins + 1)
            hist_sum = np.zeros(nbins)
        
        hist, _ = np.histogram(z, bins=bins)
        
        # Convert to number density (atoms/Å³)
        dz = bins[1] - bins[0]
        Lx, Ly = universe.dimensions[0], universe.dimensions[1]
        volume_per_bin = Lx * Ly * dz
        hist_sum += hist / volume_per_bin
        n_frames += 1
    
    density = hist_sum / n_frames
    z_centers = 0.5 * (bins[:-1] + bins[1:])
    
    return z_centers, density


def analyze_density_profiles(universe, polymer_types, water_ow_type,
                             ca_type, coo_types, csh_types,
                             equil_frames=700, nbins=200, label="system"):
    """Compute density profiles for polymer, water, Ca, and COO.
    
    Returns z_centers referenced to the CSH surface (distance from surface).
    """
    from .utils import get_surface_z
    
    profiles = {}
    
    print(f"  [{label}] Computing density profiles...")
    
    # Get surface z once from first production frame
    universe.trajectory[equil_frames]
    surface_z = get_surface_z(universe, csh_types, ca_type)
    print(f"  [{label}] Surface z = {surface_z:.1f} Å")
    
    # Polymer
    z, rho = compute_density_profile(universe, polymer_types, equil_frames, nbins, "polymer")
    profiles['polymer'] = (z - surface_z, rho)
    
    # Water oxygen
    z, rho = compute_density_profile(universe, [water_ow_type], equil_frames, nbins, "water_O")
    profiles['water_O'] = (z - surface_z, rho)
    
    # Surface Ca
    z, rho = compute_density_profile(universe, [ca_type], equil_frames, nbins, "Ca")
    profiles['Ca'] = (z - surface_z, rho)
    
    # COO oxygen
    z, rho = compute_density_profile(universe, coo_types, equil_frames, nbins, "COO")
    profiles['COO'] = (z - surface_z, rho)
    
    print(f"  [{label}] Done.")
    
    return profiles


# ============================================================
#  RADIAL DISTRIBUTION FUNCTION
# ============================================================

def compute_rdf_manual(universe, types_a, types_b, equil_frames=700,
                       rmax=10.0, nbins=200, label="g(r)"):
    """
    Compute RDF g(r) between atoms of types_a and types_b.
    Averaged over production frames.
    """
    from .utils import select_by_types
    
    group_a = select_by_types(universe, types_a)
    group_b = select_by_types(universe, types_b)
    
    dr = rmax / nbins
    bins = np.linspace(0, rmax, nbins + 1)
    r_centers = 0.5 * (bins[:-1] + bins[1:])
    hist_sum = np.zeros(nbins)
    n_frames = 0
    
    for ts in universe.trajectory[equil_frames:]:
        box = universe.dimensions[:3]
        pos_a = group_a.positions
        pos_b = group_b.positions
        
        # Compute pairwise distances with PBC
        for i in range(len(pos_a)):
            delta = pos_b - pos_a[i]
            delta -= box * np.round(delta / box)
            dists = np.sqrt((delta**2).sum(axis=1))
            hist, _ = np.histogram(dists, bins=bins)
            hist_sum += hist
        
        n_frames += 1
    
    # Normalize: g(r) = hist / (N_a * N_b/V * 4πr²dr * n_frames)
    na = len(group_a)
    nb = len(group_b)
    box = universe.dimensions[:3]
    V = box[0] * box[1] * box[2]
    rho_b = nb / V
    
    for i in range(nbins):
        r = r_centers[i]
        shell_vol = 4.0 * np.pi * r**2 * dr
        if shell_vol > 0 and n_frames > 0:
            hist_sum[i] /= (na * rho_b * shell_vol * n_frames)
    
    print(f"  [{label}] RDF computed over {n_frames} frames")
    
    return r_centers, hist_sum


# ============================================================
#  POLYMER HEIGHT
# ============================================================
# universe=u_s1
# polymer_types=POLYMER_TYPES
# csh_types=CSH_TYPES
# ca_type=16
# equil_frames=EQUIL_FRAMES
# label=ce_name
def analyze_height(universe, polymer_types, csh_types, ca_type=16,
                   equil_frames=700, label="system"):
    """Compute polymer COM height above CSH surface over time."""
    from .utils import select_by_types, get_surface_z
    
    polymer = select_by_types(universe, polymer_types)
    
    results = {'frame': [], 'time_ns': [], 'height': [], 'com_z': [], 'surface_z': []}
    
    for ts in universe.trajectory[equil_frames:]:
        # Use center_of_geometry if masses are zero
        if polymer.masses.sum() > 0:
            com = polymer.center_of_mass()
        else:
            com = polymer.center_of_geometry()
        surface_z = get_surface_z(universe, csh_types, ca_type)
        height = com[2] - surface_z
        
        results['frame'].append(ts.frame)
        results['time_ns'].append(ts.time / 1000.0)
        results['height'].append(height)
        results['com_z'].append(com[2])
        results['surface_z'].append(surface_z)
    
    df = pd.DataFrame(results)
    
    summary = {
        'label': label,
        'height_mean': df['height'].mean(),
        'height_std': df['height'].std(),
    }
    
    print(f"  [{label}] Polymer height above surface: {summary['height_mean']:.1f} ± "
          f"{summary['height_std']:.1f} Å")
    
    return df, summary


# ============================================================
#  BACKBONE ORIENTATION
# ============================================================

def analyze_orientation(universe, backbone_types, equil_frames=700,
                        label="system"):
    """
    Compute angle between polymer backbone end-to-end vector and the surface (xy) plane.
    0° = parallel to surface, 90° = perpendicular.
    """
    from .utils import select_by_types
    
    backbone = select_by_types(universe, backbone_types)
    
    results = {'frame': [], 'time_ns': [], 'angle_deg': []}
    
    for ts in universe.trajectory[equil_frames:]:
        pos = backbone.positions
        
        if len(pos) < 2:
            continue
        
        # End-to-end vector
        e2e = pos[-1] - pos[0]
        
        # Angle with xy plane: arcsin(|z| / |r|)
        r = np.linalg.norm(e2e)
        if r > 0.01:
            angle = np.degrees(np.arcsin(abs(e2e[2]) / r))
        else:
            angle = 0.0
        
        results['frame'].append(ts.frame)
        results['time_ns'].append(ts.time / 1000.0)
        results['angle_deg'].append(angle)
    
    df = pd.DataFrame(results)
    
    summary = {
        'label': label,
        'angle_mean': df['angle_deg'].mean(),
        'angle_std': df['angle_deg'].std(),
    }
    
    print(f"  [{label}] Backbone angle from surface: {summary['angle_mean']:.1f} ± "
          f"{summary['angle_std']:.1f}°")
    
    return df, summary


# ============================================================
#  STERIC LAYER THICKNESS
# ============================================================

def compute_steric_layer_thickness(z_centers, density, threshold_fraction=0.01):
    """
    Estimate steric layer thickness from polymer density profile.
    Defined as the distance from the surface where polymer density
    drops below threshold_fraction of the peak density.
    """
    peak = density.max()
    if peak <= 0:
        return 0.0
    
    threshold = peak * threshold_fraction
    
    # Find the outermost z where density exceeds threshold
    above = z_centers[density > threshold]
    if len(above) == 0:
        return 0.0
    
    return above.max() - above.min()

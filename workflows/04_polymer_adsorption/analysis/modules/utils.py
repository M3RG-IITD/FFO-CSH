"""
Utility functions: trajectory loading, surface detection, log parsing.
"""
import numpy as np
import re
from pathlib import Path


def load_universe(data_file, traj_file):
    """Load MDAnalysis Universe from LAMMPS data + dump files."""
    import MDAnalysis as mda
    u = mda.Universe(str(data_file), str(traj_file),
                     topology_format='DATA',
                     format='LAMMPSDUMP',
                     atom_style='id resid type charge x y z',
                     dt=0.001)  # dt in ps (1 fs = 0.001 ps)
    return u


def select_by_types(u, type_list):
    """Select atoms by LAMMPS type IDs."""
    type_str = " ".join(str(t) for t in type_list)
    return u.select_atoms(f"type {type_str}")


def get_surface_z(u, csh_types, ca_type=16, surface_layer_depth=3.0):
    """
    Find the z-coordinate of the CSH top surface.
    
    Strategy: in a slab geometry with boundary p p p, the CSH slab
    wraps through PBC in z. Ca atoms from the BOTTOM of the slab 
    appear at high z (near zhi), while the actual top surface Ca 
    atoms sit at moderate z below the vacuum/water gap.
    
    Algorithm:
      1. Sort all Ca z-coordinates.
      2. Find the LARGEST gap in z — this is the vacuum/water region
         above the slab where the polymer sits.
      3. The top surface = Ca atoms just BELOW that gap.
      4. Return mean z of Ca within `surface_layer_depth` Å of the
         gap boundary.
    
    Parameters
    ----------
    u : MDAnalysis.Universe
    csh_types : list
        All CSH atom type IDs (not used directly, kept for API compat).
    ca_type : int
        LAMMPS type ID for surface Ca (default 16 = casl).
    surface_layer_depth : float
        How deep below the gap boundary to include Ca atoms (Å).
    
    Returns
    -------
    float : z-coordinate of the CSH top surface
    """
    ca = u.select_atoms(f"type {ca_type}")
    z_ca = np.sort(ca.positions[:, 2])
    
    if len(z_ca) == 0:
        raise ValueError("No Ca atoms found — check ca_type")
    
    # Find the largest gap in sorted z (= vacuum above slab)
    dz = np.diff(z_ca)
    largest_gap_idx = np.argmax(dz)
    gap_size = dz[largest_gap_idx]
    
    # The Ca atom just below the vacuum gap is the top of the slab
    slab_top_z = z_ca[largest_gap_idx]
    
    # Collect the surface layer: Ca atoms within a few Å below slab_top_z
    surface_mask = (z_ca >= slab_top_z - surface_layer_depth) & (z_ca <= slab_top_z)
    
    if surface_mask.sum() == 0:
        # Shouldn't happen, but fallback to the single atom at the gap edge
        return slab_top_z
    
    surface_z = np.mean(z_ca[surface_mask])
    
    return surface_z


def production_frames(u, equil_frames=700):
    """Iterator over production frames (skip equilibration)."""
    for ts in u.trajectory[equil_frames:]:
        yield ts


def get_equil_frames(u, equil_ns=7.0, min_production_frames=50):
    """
    Compute the number of equilibration frames to skip, ensuring
    at least `min_production_frames` remain for analysis.
    
    Parameters
    ----------
    u : MDAnalysis.Universe
    equil_ns : float
        Equilibration time in nanoseconds (default 7 ns).
    min_production_frames : int
        Minimum frames that must remain for production analysis.
    
    Returns
    -------
    int : number of frames to skip
    """
    n_total = len(u.trajectory)
    
    # Estimate equil frames from timestep info
    if n_total >= 2:
        dt_ps = u.trajectory[1].time - u.trajectory[0].time
        if dt_ps > 0:
            equil_ps = equil_ns * 1000.0
            equil_frames = int(equil_ps / dt_ps)
        else:
            equil_frames = 0
    else:
        equil_frames = 0
    
    # Safety: ensure enough production frames remain
    max_equil = n_total - min_production_frames
    if equil_frames > max_equil:
        equil_frames = max(0, max_equil)
        print(f"  [WARNING] Reduced equil_frames to {equil_frames} "
              f"(trajectory has {n_total} frames, need ≥{min_production_frames} "
              f"for production)")
    
    return equil_frames


def extract_thermo_data(log_path, cutoff_step=None, last_ns=None, timestep_fs=1.0):
    """Extract thermo quantities from a LAMMPS log file."""
    with open(log_path, "r") as f:
        lines = f.readlines()

    # Find ALL thermo headers and collect data from each block
    all_data = {}
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("Step") and ("PotEng" in line or "pe" in line or "TotEng" in line):
            header = line.split()
            if not all_data:
                all_data = {key: [] for key in header}
            
            i += 1
            while i < len(lines):
                parts = lines[i].split()
                if len(parts) != len(header):
                    break
                try:
                    int(parts[0])  # check it's a data line
                    for key, value in zip(header, parts):
                        try:
                            all_data[key].append(float(value))
                        except ValueError:
                            pass
                except (ValueError, IndexError):
                    break
                i += 1
        else:
            i += 1

    # Convert to numpy
    for key in all_data:
        all_data[key] = np.array(all_data[key])

    # Apply filtering
    if all_data and "Step" in all_data:
        steps = all_data["Step"]
        if cutoff_step is not None:
            mask = steps >= cutoff_step
            # mask = (steps >= cutoff_step) & (steps <= cutoff_step + 2_000_000)
        elif last_ns is not None:
            max_step = steps.max()
            steps_target = int((last_ns * 1e6) / timestep_fs)
            cutoff = max_step - steps_target
            mask = steps >= cutoff
        else:
            mask = np.ones_like(steps, dtype=bool)
        
        for key in all_data:
            all_data[key] = all_data[key][mask]

    return all_data


def compute_eads_timeseries(log_s1, log_s2, log_s3,
                            equil_steps=7_000_000, timestep_fs=1.0,
                            energy_key="PotEng"):
    """
    Compute adsorption energy time series: E_ads(t) = E_S1(t) - E_S2(t) - E_S3(t)
    
    Aligns the three log files by step number (inner join) so only
    steps present in all three contribute. This is what was missing —
    calling extract_thermo_data with last_ns or cutoff_step separately
    and then trying to subtract arrays of different lengths produces
    either nothing or garbage.
    
    Parameters
    ----------
    log_s1, log_s2, log_s3 : path-like
        Paths to LAMMPS log files for S1, S2, S3.
    equil_steps : int
        Steps to skip as equilibration.
    timestep_fs : float
        MD timestep in femtoseconds.
    energy_key : str
        Column name in thermo output ('PotEng' or 'TotEng').
    
    Returns
    -------
    dict with keys: 'step', 'time_ns', 'E_S1', 'E_S2', 'E_S3', 'E_ads'
    Empty dict if alignment fails.
    """
    data_s1 = extract_thermo_data(log_s1, cutoff_step=equil_steps)
    data_s2 = extract_thermo_data(log_s2, cutoff_step=equil_steps)
    data_s3 = extract_thermo_data(log_s3, cutoff_step=equil_steps)
    
    # Check all three have the required columns
    for label, d in [("S1", data_s1), ("S2", data_s2), ("S3", data_s3)]:
        if "Step" not in d or energy_key not in d:
            print(f"  [WARNING] {label} log missing 'Step' or '{energy_key}'. "
                  f"Available keys: {list(d.keys())}")
            return {}
        if len(d["Step"]) == 0:
            print(f"  [WARNING] {label} log has no data after equil cutoff "
                  f"({equil_steps} steps)")
            return {}
    
    # Align by step using inner join
    steps_s1 = set(data_s1["Step"].astype(int))
    steps_s2 = set(data_s2["Step"].astype(int))
    steps_s3 = set(data_s3["Step"].astype(int))
    common_steps = sorted(steps_s1 & steps_s2 & steps_s3)
    
    if len(common_steps) == 0:
        print(f"  [WARNING] No common steps across S1/S2/S3 logs. "
              f"S1: {len(steps_s1)} steps, S2: {len(steps_s2)}, S3: {len(steps_s3)}")
        print(f"  S1 range: {min(steps_s1)}-{max(steps_s1)}")
        print(f"  S2 range: {min(steps_s2)}-{max(steps_s2)}")
        print(f"  S3 range: {min(steps_s3)}-{max(steps_s3)}")
        return {}
    
    # Build lookup: step → energy
    def make_lookup(data):
        return dict(zip(data["Step"].astype(int), data[energy_key]))
    
    lut_s1 = make_lookup(data_s1)
    lut_s2 = make_lookup(data_s2)
    lut_s3 = make_lookup(data_s3)
    
    steps = np.array(common_steps)
    e_s1 = np.array([lut_s1[s] for s in common_steps])
    e_s2 = np.array([lut_s2[s] for s in common_steps])
    e_s3 = np.array([lut_s3[s] for s in common_steps])
    e_ads = e_s1 - e_s2 - e_s3
    
    time_ns = steps * timestep_fs / 1e6  # fs → ns
    
    print(f"  Eads time series: {len(common_steps)} points, "
          f"mean = {np.mean(e_ads):.1f} ± {np.std(e_ads):.1f} kcal/mol")
    
    return {
        'step': steps,
        'time_ns': time_ns,
        'E_S1': e_s1,
        'E_S2': e_s2,
        'E_S3': e_s3,
        'E_ads': e_ads,
    }

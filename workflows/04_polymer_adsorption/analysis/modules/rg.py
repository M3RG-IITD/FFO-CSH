"""
Module 1: Radius of Gyration and Flattening Index

Computes:
  - Rg(t) total
  - Rg_parallel (in-plane, xy)
  - Rg_perpendicular (out-of-plane, z)
  - Flattening index F = Rg_parallel / Rg_perpendicular
  
For both S1 (adsorbed) and S2 (bulk solution).
"""
import numpy as np
import pandas as pd


def compute_gyration_tensor(positions, masses=None):
    """
    Compute the gyration tensor for a set of positions.
    Returns eigenvalues (sorted ascending) and the full tensor.
    """
    if masses is None:
        masses = np.ones(len(positions))
    
    total_mass = masses.sum()
    com = np.average(positions, weights=masses, axis=0)
    dr = positions - com
    
    # Gyration tensor: S_ij = (1/M) * sum(m_k * dr_i * dr_j)
    S = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            S[i, j] = np.sum(masses * dr[:, i] * dr[:, j]) / total_mass
    
    eigenvalues = np.sort(np.linalg.eigvalsh(S))
    return eigenvalues, S


def analyze_rg(universe, polymer_types, equil_frames=700, label="system"):
    """
    Compute Rg, Rg_parallel, Rg_perpendicular, and flattening index
    for every production frame.
    """
    from .utils import select_by_types
    
    polymer = select_by_types(universe, polymer_types)
    
    results = {
        'frame': [], 'time_ns': [],
        'Rg': [], 'Rg_parallel': [], 'Rg_perp': [], 'F_index': [],
        'Rg_x': [], 'Rg_y': [], 'Rg_z': [],
    }
    
    for ts in universe.trajectory[equil_frames:]:
        pos = polymer.positions
        # MDAnalysis may not parse masses from LAMMPS data correctly;
        # use uniform masses (geometric Rg) as fallback
        masses = polymer.masses
        if masses.sum() == 0:
            masses = np.ones(len(pos))
        
        eigenvalues, S = compute_gyration_tensor(pos, masses)
        
        Rg = np.sqrt(np.sum(eigenvalues))
        Rg_x = np.sqrt(S[0, 0])
        Rg_y = np.sqrt(S[1, 1])
        Rg_z = np.sqrt(S[2, 2])
        
        # Parallel = in-plane (xy), Perpendicular = out-of-plane (z)
        Rg_parallel = np.sqrt(S[0, 0] + S[1, 1])
        Rg_perp = Rg_z
        
        F_index = Rg_parallel / Rg_perp if Rg_perp > 0.01 else np.nan
        
        results['frame'].append(ts.frame)
        results['time_ns'].append(ts.time / 1000.0)  # ps to ns
        results['Rg'].append(Rg)
        results['Rg_parallel'].append(Rg_parallel)
        results['Rg_perp'].append(Rg_perp)
        results['F_index'].append(F_index)
        results['Rg_x'].append(Rg_x)
        results['Rg_y'].append(Rg_y)
        results['Rg_z'].append(Rg_z)
    
    df = pd.DataFrame(results)
    
    # Summary statistics
    summary = {
        'label': label,
        'Rg_mean': df['Rg'].mean(),
        'Rg_std': df['Rg'].std(),
        'Rg_parallel_mean': df['Rg_parallel'].mean(),
        'Rg_perp_mean': df['Rg_perp'].mean(),
        'F_index_mean': df['F_index'].mean(),
        'F_index_std': df['F_index'].std(),
    }
    
    print(f"  [{label}] Rg = {summary['Rg_mean']:.2f} ± {summary['Rg_std']:.2f} Å")
    print(f"  [{label}] Rg_parallel = {summary['Rg_parallel_mean']:.2f} Å, "
          f"Rg_perp = {summary['Rg_perp_mean']:.2f} Å")
    print(f"  [{label}] Flattening F = {summary['F_index_mean']:.2f} ± {summary['F_index_std']:.2f}")
    
    return df, summary

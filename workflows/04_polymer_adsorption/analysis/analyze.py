#!/usr/bin/env python3
"""
CSH-PCE Adsorption Analysis Pipeline
=====================================

Analyzes PCE polymer adsorption on C-S-H surfaces from LAMMPS trajectories.
Produces publication-quality Figure 5 with multiple descriptors.

Usage:
    python analyze.py                    # Run all analyses
    python analyze.py --skip-traj        # Skip trajectory analysis, only thermo
    python analyze.py --ce 1:1           # Analyze only one C:E ratio
    python analyze.py --modules rg,contacts  # Run specific modules only

Requirements:
    pip install MDAnalysis numpy scipy pandas matplotlib
"""

import argparse
import sys
import os
import json
import numpy as np
import pandas as pd
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))
from config import *

def run_thermo_analysis():
    """Run thermodynamic analysis (adsorption energy) from log files."""
    from modules.thermo import compute_adsorption_energy
    
    print("\n" + "="*60)
    print("  THERMODYNAMIC ANALYSIS")
    print("="*60)
    
    energy_results = {}
    
    for ce_name, sys_config in SYSTEMS.items():
        print(f"\n--- {ce_name} ---")
        result = compute_adsorption_energy(
            s1_log=str(sys_config['S1_log']),
            s2_log=str(sys_config['S2_log']),
            s3_log=str(S3_CONFIG['log']),
            cutoff_step=EQUIL_STEPS,
            # average_last_n=1000,
            label=ce_name,
        )
        energy_results[ce_name] = result
    
    return energy_results


def run_trajectory_analysis(ce_filter=None, modules=None):
    """Run trajectory-based analyses (Rg, coverage, contacts, etc.)."""
    from modules.utils import load_universe
    from modules.rg import analyze_rg
    from modules.coverage import analyze_coverage
    from modules.interfacial import (
        analyze_contacts, analyze_density_profiles,
        compute_rdf_manual, analyze_height, analyze_orientation,
        compute_steric_layer_thickness,
    )
    
    all_results = {
        'rg_s1': {}, 'rg_s2': {},
        'coverage': {}, 'contacts': {},
        'density': {}, 'rdf': {},
        'height': {}, 'orientation': {},
    }
    
    run_modules = set(modules.split(',')) if modules else {
        'rg', 'coverage', 'contacts', 'density', 'rdf', 'height', 'orientation'
    }
    
    systems_to_run = {k: v for k, v in SYSTEMS.items()
                      if ce_filter is None or k == ce_filter}
    
    for ce_name, sys_config in systems_to_run.items():
        print(f"\n{'='*60}")
        print(f"  TRAJECTORY ANALYSIS: C:E = {ce_name}")
        print(f"{'='*60}")
        
        # ---- Load S1 (adsorbed) ----
        print(f"\n  Loading S1 (adsorbed)...")
        try:
            u_s1 = load_universe(sys_config['S1_data'], sys_config['S1_traj'])
            print(f"  S1: {u_s1.atoms.n_atoms} atoms, {u_s1.trajectory.n_frames} frames")
        except Exception as e:
            print(f"  ERROR loading S1: {e}")
            continue
        
        # ---- Load S2 (bulk solution) ----
        print(f"\n  Loading S2 (bulk)...")
        try:
            u_s2 = load_universe(sys_config['S2_data'], sys_config['S2_traj'])
            print(f"  S2: {u_s2.atoms.n_atoms} atoms, {u_s2.trajectory.n_frames} frames")
        except Exception as e:
            print(f"  WARNING: Could not load S2: {e}")
            u_s2 = None
        
        # ---- Module: Radius of Gyration ----
        if 'rg' in run_modules:
            print(f"\n  --- Rg Analysis ---")
            rg_df_s1, rg_sum_s1 = analyze_rg(
                u_s1, POLYMER_TYPES, EQUIL_FRAMES, label=f"{ce_name} adsorbed")
            all_results['rg_s1'][ce_name] = rg_sum_s1
            rg_df_s1.to_csv(OUTPUT_DIR / f"rg_s1_{ce_name.replace(':','')}.csv", index=False)
            
            if u_s2 is not None:
                rg_df_s2, rg_sum_s2 = analyze_rg(
                    u_s2, POLYMER_TYPES, EQUIL_FRAMES_BULK, label=f"{ce_name} bulk")
                all_results['rg_s2'][ce_name] = rg_sum_s2
                rg_df_s2.to_csv(OUTPUT_DIR / f"rg_s2_{ce_name.replace(':','')}.csv", index=False)
        
        # ---- Module: Surface Coverage ----
        if 'coverage' in run_modules:
            print(f"\n  --- Surface Coverage ---")
            cov_df, cov_sum = analyze_coverage(
                u_s1, POLYMER_TYPES, CSH_TYPES, EQUIL_FRAMES,
                surface_cutoff=15.0, label=ce_name)
            all_results['coverage'][ce_name] = cov_sum
            cov_df.to_csv(OUTPUT_DIR / f"coverage_{ce_name.replace(':','')}.csv", index=False)
        
        # ---- Module: Ca-COO Contacts ----
        if 'contacts' in run_modules:
            print(f"\n  --- Contact Analysis ---")
            con_df, con_sum = analyze_contacts(
                u_s1, COO_OXYGEN_TYPES, CA_SURFACE_TYPE,
                EQUIL_FRAMES, cutoff=CONTACT_CUTOFF, label=ce_name)
            all_results['contacts'][ce_name] = con_sum
            con_df.to_csv(OUTPUT_DIR / f"contacts_{ce_name.replace(':','')}.csv", index=False)
        
        # ---- Module: Density Profiles ----
        if 'density' in run_modules:
            print(f"\n  --- Density Profiles ---")
            profiles = analyze_density_profiles(
                u_s1, POLYMER_TYPES, OW_TYPE, CA_SURFACE_TYPE,
                COO_OXYGEN_TYPES, EQUIL_FRAMES, DENSITY_NBINS, label=ce_name)
            all_results['density'][ce_name] = profiles
            
            # Compute steric layer thickness
            z_poly, rho_poly = profiles['polymer']
            delta = compute_steric_layer_thickness(z_poly, rho_poly)
            print(f"  [{ce_name}] Steric layer thickness δ ≈ {delta:.1f} Å")
            
            # Save profiles
            for comp, (z, rho) in profiles.items():
                pd.DataFrame({'z': z, 'density': rho}).to_csv(
                    OUTPUT_DIR / f"density_{comp}_{ce_name.replace(':','')}.csv", index=False)
        
        # ---- Module: RDF ----
        if 'rdf' in run_modules:
            print(f"\n  --- Ca-COO RDF ---")
            r, gr = compute_rdf_manual(
                u_s1, [CA_SURFACE_TYPE], COO_OXYGEN_TYPES,
                EQUIL_FRAMES, rmax=RDF_CUTOFF, nbins=RDF_NBINS,
                label=f"Ca-COO {ce_name}")
            all_results['rdf'][ce_name] = (r, gr)
            pd.DataFrame({'r': r, 'g_r': gr}).to_csv(
                OUTPUT_DIR / f"rdf_ca_coo_{ce_name.replace(':','')}.csv", index=False)
        
        # ---- Module: Polymer Height ----
        if 'height' in run_modules:
            print(f"\n  --- Polymer Height ---")
            h_df, h_sum = analyze_height(
                u_s1, POLYMER_TYPES, CSH_TYPES, equil_frames=EQUIL_FRAMES, label=ce_name)
            all_results['height'][ce_name] = h_sum
            h_df.to_csv(OUTPUT_DIR / f"height_{ce_name.replace(':','')}.csv", index=False)
        
        # ---- Module: Orientation ----
        if 'orientation' in run_modules:
            print(f"\n  --- Backbone Orientation ---")
            ori_df, ori_sum = analyze_orientation(
                u_s1, BACKBONE_TYPES, EQUIL_FRAMES, label=ce_name)
            all_results['orientation'][ce_name] = ori_sum
            ori_df.to_csv(OUTPUT_DIR / f"orientation_{ce_name.replace(':','')}.csv", index=False)
    
    return all_results


def main():
    parser = argparse.ArgumentParser(description='CSH-PCE Analysis Pipeline')
    parser.add_argument('--skip-traj', action='store_true',
                        help='Skip trajectory analysis, only run thermo')
    parser.add_argument('--skip-thermo', action='store_true',
                        help='Skip thermo analysis')
    parser.add_argument('--ce', type=str, default=None,
                        help='Analyze only this C:E ratio (e.g., "1:1")')
    parser.add_argument('--modules', type=str, default=None,
                        help='Comma-separated list of modules to run')
    parser.add_argument('--no-plot', action='store_true',
                        help='Skip figure generation')
    args = parser.parse_args()
    
    # Create output directories
    OUTPUT_DIR.mkdir(exist_ok=True)
    FIGURE_DIR.mkdir(exist_ok=True)
    
    all_results = {}
    
    # ---- Thermodynamic Analysis ----
    if not args.skip_thermo:
        energy_results = run_thermo_analysis()
        all_results['energy'] = energy_results
    
    # ---- Trajectory Analysis ----
    if not args.skip_traj:
        traj_results = run_trajectory_analysis(
            ce_filter=args.ce, modules=args.modules)
        all_results.update(traj_results)
    
    # ---- Generate Figure 5 ----
    if not args.no_plot and all_results:
        from modules.plotting import assemble_figure5
        print("\n" + "="*60)
        print("  GENERATING FIGURE 5")
        print("="*60)
        assemble_figure5(all_results, output_path=str(FIGURE_DIR / "figure5.pdf"))
        assemble_figure5(all_results, output_path=str(FIGURE_DIR / "figure5.png"))
    
    # ---- Summary Table ----
    print("\n" + "="*60)
    print("  SUMMARY TABLE")
    print("="*60)
    print(f"\n{'C:E':>6} | {'E_ads':>12} | {'Rg_ads':>8} | {'Rg_bulk':>8} | "
          f"{'F_ads':>6} | {'Coverage':>10} | {'Contacts':>10} | {'Height':>8}")
    print("-" * 90)
    
    for ce in CE_ORDER:
        row = f"{ce:>6}"
        
        if 'energy' in all_results and ce in all_results['energy']:
            e = all_results['energy'][ce]
            row += f" | {e['E_ads']:>8.1f}±{e['E_ads_err']:.0f}"
        else:
            row += f" | {'--':>12}"
        
        if 'rg_s1' in all_results and ce in all_results['rg_s1']:
            row += f" | {all_results['rg_s1'][ce]['Rg_mean']:>8.2f}"
        else:
            row += f" | {'--':>8}"
        
        if 'rg_s2' in all_results and ce in all_results['rg_s2']:
            row += f" | {all_results['rg_s2'][ce]['Rg_mean']:>8.2f}"
        else:
            row += f" | {'--':>8}"
        
        if 'rg_s1' in all_results and ce in all_results['rg_s1']:
            row += f" | {all_results['rg_s1'][ce]['F_index_mean']:>6.2f}"
        else:
            row += f" | {'--':>6}"
        
        if 'coverage' in all_results and ce in all_results['coverage']:
            c = all_results['coverage'][ce]
            row += f" | {c['coverage_grid_mean']:>6.1f}±{c['coverage_grid_std']:.1f}%"
        else:
            row += f" | {'--':>10}"
        
        if 'contacts' in all_results and ce in all_results['contacts']:
            row += f" | {all_results['contacts'][ce]['contacts_mean']:>6.1f}±{all_results['contacts'][ce]['contacts_std']:.0f}"
        else:
            row += f" | {'--':>10}"
        
        if 'height' in all_results and ce in all_results['height']:
            row += f" | {all_results['height'][ce]['height_mean']:>6.1f}Å"
        else:
            row += f" | {'--':>8}"
        
        print(row)
    
    print("\n  All results saved to:", OUTPUT_DIR)
    print("  Figures saved to:", FIGURE_DIR)
    print("\n  Done!")


if __name__ == "__main__":
    main()

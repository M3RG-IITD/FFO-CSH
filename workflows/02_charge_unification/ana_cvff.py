import time
import numpy as np
import pandas as pd
import pickle

import os
from mdsetup import MDSetup


# 2. Simulation with MDSetup

# === Change to working dir and initialize MDSetup ===
os.chdir('')
lammps_setup = MDSetup(
    system_setup="config/setup_mechanical_charge_cvff.yaml",
    simulation_default="config/defaults.yaml",
    simulation_ensemble="config/ensemble.yaml",
    simulation_sampling="config/sampling_mechanical.yaml",
    submission_command="qsub",
)

TOB_STRUCTURES = ["Tob11", "Tob11H", "Tob14"]


start_index=6
end_index=13
optimizer='cvff'
CHARGE_SETS = [f"Charge_set_{i}_{optimizer}" for i in range(start_index, end_index)]

# === 1. Density Analysis ===
den_results = {tob: [] for tob in TOB_STRUCTURES}

for charge_set in CHARGE_SETS:
    for tob in TOB_STRUCTURES:
        try:
            analysis_folder = f"{tob}/{charge_set}/equilibration"
            extracted = lammps_setup.analysis_extract_properties(
                analysis_folder=analysis_folder,
                ensemble='01_npt',
                extracted_properties=['density'],
                output_suffix='density',
                time_fraction=0.2,
            )
            avg = extracted.get('01_npt', {}).get("data", {}).get("average", {})
            mean, std = avg.get('density', {}).get("mean"), avg.get('density', {}).get("std")
            den_results[tob].append((mean, std))
        except Exception as e:
            print(f"❌ Density analysis failed for {tob} | {charge_set}: {e}")
            den_results[tob].append((None, None))

# === 2. Surface Energy Analysis ===
NA = 6.022e23
CONVERSION = 4184  # kcal/mol to J/mol

box_coords = {
    "Tob11":    [0.527972175, 23.057572175, -0.431033519, 21.723966481], # CF = 0.6959
    "Tob11H":   [0.065633394, 22.383633394, -0.317852898, 29.242147102], # CF = 0.5265
    "Tob14":    [-0.658063909, 21.871536091, -0.289451837, 21.985548163], # CF = 0.6922
}

se_results = {tob: [] for tob in TOB_STRUCTURES}

for charge_set in CHARGE_SETS:
    for tob in TOB_STRUCTURES:
        try:
            # Bulk
            folder = f"{tob}/{charge_set}/SE/bulk"
            bulk = lammps_setup.analysis_extract_properties(
                analysis_folder=folder,
                ensemble="00_nvt",
                extracted_properties=["potential energy"],
                output_suffix="energy",
                time_fraction=0.4,
            )["00_nvt"]["data"]["average"]["potential energy"]

            # Vacuum
            folder = f"{tob}/{charge_set}/SE/vacuum"
            vac = lammps_setup.analysis_extract_properties(
                analysis_folder=folder,
                ensemble="00_nvt",
                extracted_properties=["potential energy"],
                output_suffix="energy",
                time_fraction=0.4,
            )["00_nvt"]["data"]["average"]["potential energy"]

            # Surface Energy
            xlo, xhi, ylo, yhi = box_coords[tob]
            A = abs(xhi - xlo) * abs(yhi - ylo) * 1e-20
            deltaE = 1000 * (vac["mean"] - bulk["mean"]) * CONVERSION / (2 * A * NA)
            s_dev = 1000 * (vac["std"] + bulk["std"]) * CONVERSION / (2 * A * NA)
            se_results[tob].append((deltaE, s_dev))
        except Exception as e:
            print(f"❌ SE analysis failed for {tob} | {charge_set}: {e}")
            se_results[tob].append((None, None))

# === 3. Mechanical Properties Analysis ===
bm_results = {tob: [] for tob in TOB_STRUCTURES}

for charge_set in CHARGE_SETS:
    for tob in TOB_STRUCTURES:
        try:
            folder = f"{tob}/{charge_set}/deformation"
            BM, BM_std, _, _ = lammps_setup.analysis_mechanical_proerties(
                analysis_folder=folder,
                ensemble="00_nvt",
                deformation_rates=[-0.02, -0.01, 0.00, 0.01, 0.02],
                method="VRH",
                time_fraction=0.4,
                visualize_stress_strain=False,
            )
            bm_results[tob].append((BM, BM_std))
        except Exception as e:
            print(f"❌ BM analysis failed for {tob} | {charge_set}: {e}")
            bm_results[tob].append((None, None))


# === Save Results ===
timestamp = time.strftime("%Y%m%d_%H%M%S")
OUTPUT_DIR = 'runs/charge_optimization/cvff'
pickle_path = f"{OUTPUT_DIR}/results_charge_{timestamp}.pkl"
csv_path = f"{OUTPUT_DIR}/results_charge_{timestamp}.csv"

with open(pickle_path, 'wb') as f:
    pickle.dump({
        'optimizer': optimizer,
        'den_results': den_results,
        'se_results': se_results,
        'bm_results': bm_results,
    }, f)

# Create and save DataFrame
df = pd.DataFrame({
    'D_11': np.array(den_results['Tob11'])[:, 0],
    'D_11H': np.array(den_results['Tob11H'])[:, 0],
    'D_14': np.array(den_results['Tob14'])[:, 0],

    'SE_T11': np.array(se_results['Tob11'])[:, 0],
    'SE_T11H': np.array(se_results['Tob11H'])[:, 0],
    'SE_T14': np.array(se_results['Tob14'])[:, 0],

    'BM_T11': np.array(bm_results['Tob11'])[:, 0],
    'BM_T11H': np.array(bm_results['Tob11H'])[:, 0],
    'BM_T14': np.array(bm_results['Tob14'])[:, 0],

    'D_11_std': np.array(den_results['Tob11'])[:, 1],
    'D_11H_std': np.array(den_results['Tob11H'])[:, 1],
    'D_14_std': np.array(den_results['Tob14'])[:, 1],

    'SE_T11_std': np.array(se_results['Tob11'])[:, 1],
    'SE_T11H_std': np.array(se_results['Tob11H'])[:, 1],
    'SE_T14_std': np.array(se_results['Tob14'])[:, 1],

    'BM_T11_std': np.array(bm_results['Tob11'])[:, 1],
    'BM_T11H_std': np.array(bm_results['Tob11H'])[:, 1],
    'BM_T14_std': np.array(bm_results['Tob14'])[:, 1],
})


mean_cols = ['D_11', 'D_11H', 'D_14', 'SE_T11', 'SE_T11H', 'SE_T14', 'BM_T11', 'BM_T11H', 'BM_T14']
mask = df[mean_cols].dropna().index
df_full_masked = df.loc[mask]

target_y = np.array([2.46, 2.39, 2.23, 680, 325, 635, 71, 55.35, 47])

std_cols = [col + '_std' for col in mean_cols]

# Compute percentage errors (mean and std)
error_mean = 100 * np.abs(df_full_masked[mean_cols].values - target_y[None, :]) / target_y[None, :]
error_std = 100 * df_full_masked[std_cols].values / target_y[None, :]

# Add errors to new DataFrame
df_full_new = df_full_masked.copy()
for i, col in enumerate(mean_cols):
    df_full_new[f'error_{col}'] = error_mean[:, i]
    df_full_new[f'error_{col}_std'] = error_std[:, i]


df_full_new.to_csv(csv_path, index=False)
print(f"✅ Analysis completed and saved to:\n📁 {csv_path}\n📦 {pickle_path}")


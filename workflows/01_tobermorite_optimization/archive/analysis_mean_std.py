from mdsetup import MDSetup
import os
import time
import pandas as pd
import numpy as np
import datetime
import pickle

current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

os.chdir('')

BASE_DIR = "input_tob_all"
# if dirs starts with "LJ_set_" keep it, otherwise remove it

lj_dirs = [d for d in os.listdir(BASE_DIR) if d.startswith("LJ_set")]
lj_dirs.sort(key=lambda x: int(x.split('_')[2]) if len(x.split('_')) > 2 and x.split('_')[2].isdigit() else float('inf'))
# lj_dirs = lj_dirs[-42:-32] # 18, 14, 10, 32
# get the last part of the lj_dirs and if it is a number, then append None otherwise append the last part
optimizers = [None if d.split('_')[-1].isdigit() else d.split('_')[-1] for d in lj_dirs]

# === load all set of parameters ===

BASE_DIR = "input_tob_all"

sc_r_values_n = []
sc_eps_values_n = []
oc_r_values_n = []
oc_eps_values_n = []
ocx_r_values_n = []
ocx_eps_values_n = []
sos_ktheta_values_n = []
oso_ktheta_values_n = []
so_kr_values_n = []

# dir = 'LJ_set_582_ocxktheta'
for dir in lj_dirs:    
    param_dir = os.path.join(BASE_DIR, dir)
    num = [i for i in dir.split('_') if i.isdigit() and len(i) > 0][0]
    frc_path = os.path.join(param_dir, f"modified_LJ_{num}.frc")
    
    with open(frc_path, "r") as file:
        lines = file.readlines()

    sc_r, sc_eps = [float(i) for i in lines[3953].strip().split()[-2:]]
    oc_r, oc_eps = [float(i) for i in lines[3957].strip().split()[-2:]]
    ocx_r, ocx_eps = [float(i) for i in lines[3961].strip().split()[-2:]]
    
    sos_ktheta = float(lines[2950].strip().split()[-3])
    oso_ktheta = float(lines[2953].strip().split()[-3])
    so_kr = float(lines[2091].strip().split()[-3])

    sc_r_values_n.append(sc_r)
    sc_eps_values_n.append(sc_eps)
    oc_r_values_n.append(oc_r)
    oc_eps_values_n.append(oc_eps)
    ocx_r_values_n.append(ocx_r)
    ocx_eps_values_n.append(ocx_eps)
    sos_ktheta_values_n.append(sos_ktheta)
    oso_ktheta_values_n.append(oso_ktheta)
    so_kr_values_n.append(so_kr)


# 2. MDSetup

lammps_setup = MDSetup(
    system_setup="input_tob_all/setup_mechanical_pcff.yaml",
    simulation_default="input_tob_all/defaults.yaml",
    simulation_ensemble="input_tob_all/ensemble.yaml",
    simulation_sampling="input_tob_all/sampling_mechanical.yaml",
    submission_command="qsub",
)

TOB_STRUCTURES = ["Tob11", "Tob11H", "Tob14"]
# 1. Density Analysis
den_results = {tob: [] for tob in TOB_STRUCTURES}
for lj_set in lj_dirs:
    for tob_structure in TOB_STRUCTURES:
        try:
            analysis_folder = f"{tob_structure}/{lj_set}/equilibration"
            extracted_values = lammps_setup.analysis_extract_properties(
                analysis_folder=analysis_folder,
                ensemble='01_npt',
                extracted_properties=['density'],
                output_suffix='density',
                time_fraction=0.2, # Percentage to discard from beginning of the simulation
            )
            average_values = extracted_values.get('01_npt', {}).get("data", {}).get("average", {})
            mean_value = average_values.get('density', {}).get("mean", None)
            std_value = average_values.get('density', {}).get("std", None)
            den_results[tob_structure].append((mean_value, std_value))
        
        except Exception as e:
            print(f"❌ Failed to analyze density for {tob_structure} with {lj_set}: {e}")
            den_results[tob_structure].append((None, None))
            continue

# 2. Surface Energy Analysis
NA = 6.022e23
CONVERSION = 4184  # kcal/mol to J/mol

# Box dimensions (structure-dependent)
box_coords = {
    "Tob11":    [0.527972175, 23.057572175, -0.431033519, 21.723966481],
    "Tob11H":   [0.065633394, 22.383633394, -0.317852898, 29.242147102],
    "Tob14":    [-0.658063909, 21.871536091, -0.289451837, 21.985548163],
}

se_results = {struct: [] for struct in TOB_STRUCTURES}
for struct in TOB_STRUCTURES:
    for lj in lj_dirs:
        try:
            base = f"{struct}/{lj}/SE"
            
            state = 'bulk'
            folder = f"{base}/{state}"
            extracted_values = lammps_setup.analysis_extract_properties(
                analysis_folder=folder,
                ensemble="00_nvt",
                extracted_properties=["potential energy"],
                output_suffix="energy",
                time_fraction=0.4,
            )
            
            bulk_energy = extracted_values.get("00_nvt", {}).get("data", {}).get("average", {}).get("potential energy", {})
            

            state = 'vacuum'
            folder = f"{base}/{state}"
            extracted_values = lammps_setup.analysis_extract_properties(
                analysis_folder=folder,
                ensemble="00_nvt",
                extracted_properties=["potential energy"],
                output_suffix="energy",
                time_fraction=0.4,
            )
            vac_energy = extracted_values.get("00_nvt", {}).get("data", {}).get("average", {}).get("potential energy", {})
            
            E_bulk, SD_bulk = bulk_energy["mean"], bulk_energy["std"]
            E_vac, SD_vac = vac_energy["mean"], vac_energy["std"]

            # Compute surface area
            xlo, xhi, ylo, yhi = box_coords[struct]
            A = abs(xhi - xlo) * abs(yhi - ylo) * 1e-20  # m²

            # Compute SE and std dev
            deltaE = 1000 * (E_vac - E_bulk) * CONVERSION / (2 * A * NA)  # mJ/m²
            s_dev = 1000 * (SD_bulk + SD_vac) * CONVERSION / (2 * A * NA)

            se_results[struct].append((deltaE, s_dev))
            print(f"✅ Analyzed {struct} with {lj}: SE = {deltaE:.2f} ± {s_dev:.2f} mJ/m²")
        
        except Exception as e:
            print(f"❌ Failed to analyze SE for {struct} with {lj}: {e}")
            se_results[struct].append((None, None))
            continue

# 3. Mechanical Properties Analysis            

bm_results = {tob: [] for tob in TOB_STRUCTURES}
for lj_set in lj_dirs:
    for tob_structure in TOB_STRUCTURES:
        try:
            # Define the deformation analysis folder
            analysis_folder = f"{tob_structure}/{lj_set}/deformation"
            # Run analysis
            BM, BM_std, Cij, Cij_std = lammps_setup.analysis_mechanical_proerties(
                analysis_folder=analysis_folder,
                ensemble="00_nvt",
                deformation_rates=[-0.02, -0.01, 0.00, 0.01, 0.02],
                method="VRH",
                time_fraction=0.4,
                visualize_stress_strain=False,
            )

            print(f"✅ Analyzed {tob_structure} with {lj_set}: BM = {BM:.2f} GPa")
            bm_results[tob_structure].append((BM, BM_std))

        except Exception as e:
            print(f"❌ Failed to analyze BM for {tob_structure} with {lj_set}: {e}")
            bm_results[tob_structure].append((None, None))
            continue


# save all results as pkl file
with open(f'ML_Pipeline/data/data_len_{len(lj_dirs)}_mean_std_{current_time}.pkl', 'wb') as f:
    results = {
        'optimizers': optimizers,
        'sc_r_values_n': sc_r_values_n,
        'sc_eps_values_n': sc_eps_values_n,
        'oc_r_values_n': oc_r_values_n,
        'oc_eps_values_n': oc_eps_values_n,
        'ocx_r_values_n': ocx_r_values_n,
        'ocx_eps_values_n': ocx_eps_values_n,
        'sos_ktheta_values_n': sos_ktheta_values_n,
        'oso_ktheta_values_n': oso_ktheta_values_n,
        'so_kr_values_n': so_kr_values_n,
        'den_results': den_results,
        'se_results': se_results,
        'bm_results': bm_results
    }
    pickle.dump(results, f)

df_full = pd.DataFrame({
    'optimizers': optimizers,
    'sc_r': sc_r_values_n,
    'sc_eps': sc_eps_values_n,
    'oc_r': oc_r_values_n,
    'oc_eps': oc_eps_values_n,
    'ocx_r': ocx_r_values_n,
    'ocx_eps': ocx_eps_values_n,
    'sos_ktheta': sos_ktheta_values_n,
    'oso_ktheta': oso_ktheta_values_n,
    'so_kr': so_kr_values_n,
    
    'D_11': np.array(den_results['Tob11'])[:,0],
    'D_11H': np.array(den_results['Tob11H'])[:,0],
    'D_14': np.array(den_results['Tob14'])[:,0],
    
    'SE_T11': np.array(se_results['Tob11'])[:,0],
    'SE_T11H': np.array(se_results['Tob11H'])[:,0],
    'SE_T14': np.array(se_results['Tob14'])[:,0],
    
    'BM_T11': np.array(bm_results['Tob11'])[:,0],
    'BM_T11H': np.array(bm_results['Tob11H'])[:,0],
    'BM_T14': np.array(bm_results['Tob14'])[:,0],
    
    'D_11_std': np.array(den_results['Tob11'])[:,1],
    'D_11H_std': np.array(den_results['Tob11H'])[:,1],
    'D_14_std': np.array(den_results['Tob14'])[:,1],
    
    'SE_T11_std': np.array(se_results['Tob11'])[:,1],
    'SE_T11H_std': np.array(se_results['Tob11H'])[:,1],
    'SE_T14_std': np.array(se_results['Tob14'])[:,1],
    
    'BM_T11_std': np.array(bm_results['Tob11'])[:,1],
    'BM_T11H_std': np.array(bm_results['Tob11H'])[:,1],
    'BM_T14_std': np.array(bm_results['Tob14'])[:,1]
    
})

mean_cols = ['D_11', 'D_11H', 'D_14', 'SE_T11', 'SE_T11H', 'SE_T14', 'BM_T11', 'BM_T11H', 'BM_T14']
mask = df_full[mean_cols].dropna().index
df_full_masked = df_full.loc[mask]

# Define target property values and tolerable errors
target_y = np.array([2.46, 2.39, 2.23, 680, 325, 635, 71, 55.35, 47])

# Define columns for means and stds
mean_cols = ['D_11', 'D_11H', 'D_14', 'SE_T11', 'SE_T11H', 'SE_T14', 'BM_T11', 'BM_T11H', 'BM_T14']
std_cols = [col + '_std' for col in mean_cols]  # Exclude BM stds for now

# Compute percentage errors (mean and std)
error_mean = 100 * np.abs(df_full_masked[mean_cols].values - target_y[None, :]) / target_y[None, :]
error_std = 100 * df_full_masked[std_cols].values / target_y[None, :]

# Add errors to new DataFrame
df_full_new = df_full_masked.copy()
for i, col in enumerate(mean_cols):
    df_full_new[f'error_{col}'] = error_mean[:, i]
    df_full_new[f'error_{col}_std'] = error_std[:, i]

df_full_new.to_csv(f"ML_Pipeline/data/data_len_{len(lj_dirs)}_mean_std_{current_time}.csv", index=False)

import os
import time
from mdsetup import MDSetup
import pandas as pd
import numpy as np
os.chdir('')

count1 = 526
count2 = 549
optimizer = 'ocxktheta'

# === 1. Load Data ===
df_full = pd.read_csv('ML_Pipeline/data/AL_data.csv')
df_full = df_full.dropna()

# Define target property values and tolerable errors
target_y = np.array([2.46, 2.39, 2.23, 680, 325, 635, 71, 55.35, 47])

# Calculate percentage error
y_error_fulll = (100 * (np.abs(df_full.values[:, 4:] - target_y) / target_y))

for i, prop in enumerate(['error_D_11', 'error_D_11H', 'error_D_14', 'error_SE_T11', 'error_SE_T11H', 'error_SE_T14', 'error_BM_T11', 'error_BM_T11H', 'error_BM_T14']):
    df_full[prop] = y_error_fulll[:, i]

df_clean  = df_full.iloc[(y_error_fulll < np.array([100, 1, 1, 100, 100, 100, 10, 10, 100])).sum(axis=1) == 9]

# === load all set of parameters ===

# === create new set of parameters ===
ocx_r = 3.70
ocx_eps = 0.12
ktheta_sets = [170, 150, 100, 80]

suggested_params = np.array([
    [
        float(df_clean['sc_r'].values[i]),
        float(df_clean['sc_eps'].values[i]),
        float(df_clean['oc_r'].values[i]),
        float(df_clean['oc_eps'].values[i]),
        ocx_r,
        ocx_eps,
        k,
        k
    ]
    for i in range(len(df_clean))
    for k in ktheta_sets
])
print(suggested_params.shape)

# 2. MDSetup
lammps_setup = MDSetup(
    system_setup="input_tob_all/setup_mechanical_pcff.yaml",
    simulation_default="input_tob_all/defaults.yaml",
    simulation_ensemble="input_tob_all/ensemble.yaml",
    simulation_sampling="input_tob_all/sampling_mechanical.yaml",
    submission_command="qsub",
)

LJ_SETS = [f"LJ_set_{i+1}_{optimizer}" for i in range(count1, count2)]


try:
    TOB_STRUCTURES = ["Tob11", "Tob11H", "Tob14"]
    # 1. Density Analysis
    den_results = {tob: [] for tob in TOB_STRUCTURES}

    for lj_set in LJ_SETS:
        for tob_structure in TOB_STRUCTURES:
            try:
                analysis_folder = f"{tob_structure}/{lj_set}/equilibration"    
                extracted_values = lammps_setup.analysis_extract_properties(
                    analysis_folder=analysis_folder,
                    ensemble='01_npt',
                    extracted_properties=['density'],
                    output_suffix='density',
                    time_fraction=0.2,
                )
                average_values = extracted_values.get('01_npt', {}).get("data", {}).get("average", {})
                mean_value = average_values.get('density', {}).get("mean", None)
                den_results[tob_structure].append(mean_value)
            
            except Exception as e:
                print(f"❌ Failed to analyze density for {tob_structure} with {lj_set}: {e}")
                den_results[tob_structure].append(None)
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
        for lj in LJ_SETS:
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
    for lj_set in LJ_SETS:
        for tob_structure in TOB_STRUCTURES:
            try:
                # Define the deformation analysis folder
                analysis_folder = f"{tob_structure}/{lj_set}/deformation"
                # Run analysis
                BM, Cij = lammps_setup.analysis_mechanical_proerties(
                    analysis_folder=analysis_folder,
                    ensemble="00_nvt",
                    deformation_rates=[-0.02, -0.01, 0.00, 0.01, 0.02],
                    method="VRH",
                    time_fraction=0.4,
                    visualize_stress_strain=False,
                )

                print(f"✅ Analyzed {tob_structure} with {lj_set}: BM = {BM:.2f} GPa")
                bm_results[tob_structure].append(BM)

            except Exception as e:
                print(f"❌ Failed to analyze BM for {tob_structure} with {lj_set}: {e}")
                bm_results[tob_structure].append(None)
                continue

    sc_r, sc_eps, oc_r, oc_eps, ocx_r, ocx_eps, sos_ktheta, oso_ktheta =  suggested_params[:, 0], suggested_params[:, 1], suggested_params[:, 2], suggested_params[:, 3], suggested_params[:, 4], suggested_params[:, 5], suggested_params[:, 6], suggested_params[:, 7]


    df = pd.DataFrame({
        'sc_r': sc_r,
        'sc_eps': sc_eps,
        'oc_r': oc_r,
        'oc_eps': oc_eps,
        'ocx_r': ocx_r,
        'ocx_eps': ocx_eps,
        'sos_ktheta': sos_ktheta,
        'oso_ktheta': oso_ktheta,
        
        'D_11': np.array(den_results['Tob11']),
        'D_11H': np.array(den_results['Tob11H']),
        'D_14': np.array(den_results['Tob14']),
        
        'SE_T11': np.array(se_results['Tob11'])[:,0],
        'SE_T11H': np.array(se_results['Tob11H'])[:,0],
        'SE_T14': np.array(se_results['Tob14'])[:,0],
        
        'BM_T11': np.array(bm_results['Tob11']),
        'BM_T11H': np.array(bm_results['Tob11H']),
        'BM_T14': np.array(bm_results['Tob14'])
        
    })
    # save the df as a csv file with the name "data_time.csv"
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    df.to_csv(f"ML_Pipeline/data/data_LJ_{count1}_{count2}_{timestamp}.csv", index=False)
    print(f"✅ All jobs completed and data saved as data_LJ_{count1}_{count2}_{timestamp}.csv")
except:
    print(lj_set)
    
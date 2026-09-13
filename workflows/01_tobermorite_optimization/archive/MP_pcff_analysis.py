import os
import numpy as np
import matplotlib.pyplot as plt
from mdsetup import MDSetup
import pickle

# Change to the correct directory
os.chdir('')

# Initialize MDSetup
lammps_setup = MDSetup(
    system_setup="input_tob_all/setup_mechanical_pcff.yaml",
    simulation_default="input_tob_all/defaults.yaml",
    simulation_ensemble="input_tob_all/ensemble.yaml",
    simulation_sampling="input_tob_all/sampling_mechanical.yaml",
    submission_command="qsub",
)

# Define paths
# LJ_SETS = [f"LJ_set_{i+1}" for i in range(50,68)]
# TOB_STRUCTURES = ["Tob9", "Tob11", "Tob11H", "Tob14"]

LJ_SETS = [f"LJ_set_{i+1}" for i in range(68,123)]
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
            print(f"✅ Analyzed {tob_structure} with {lj_set}: Density = {mean_value:.2f} g/cm³")
        except Exception as e:
            print(f"❌ Failed to analyze {tob_structure} with {lj_set}: {e}")
            den_results[tob_structure].append(None)
            continue
            
# save den_results
with open("results_den123.pkl", "wb") as f:
    pickle.dump(den_results, f)
    
# 2. Surface Energy Analysis

NA = 6.022e23
CONVERSION = 4184  # kcal/mol to J/mol

# Box dimensions (structure-dependent)
box_coords = {
    "Tob9":     [-0.378508016, 21.933491984, -0.012474231, 21.896525769],
    "Tob11":    [0.527972175, 23.057572175, -0.431033519, 21.723966481],
    "Tob11H":   [0.065633394, 22.383633394, -0.317852898, 29.242147102],
    "Tob14":    [-0.658063909, 21.871536091, -0.289451837, 21.985548163],
}

# SE results
se_results = {struct: [] for struct in TOB_STRUCTURES}

# Loop over all structures and LJ param sets
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
            print(f"❌ Failed to analyze {struct} with {lj}: {e}")
            se_results[struct].append((None, None))
            continue
        


# save se_results
with open("results_se123.pkl", "wb") as f:
    pickle.dump(se_results, f)
    

# 3. Mechanical Properties Analysis
# Define parameters for deformation analysis
ENSEMBLE = "00_nvt"
DEFORMATION_RATES = [-0.02, -0.01, 0.00, 0.01, 0.02]
TIME_FRACTION = 0.4
METHOD = "VRH"
VISUALIZE_STRESS_STRAIN = False  # Change to True if you want plots per simulation

# Dictionary to hold Bulk Modulus values
bm_results = {tob: [] for tob in TOB_STRUCTURES}
cij_results = {tob: [] for tob in TOB_STRUCTURES}
# Loop through each LJ set and Tob structure
for lj_set in LJ_SETS:
    for tob_structure in TOB_STRUCTURES:
        try:
            # Define the deformation analysis folder
            analysis_folder = f"{tob_structure}/{lj_set}/deformation"

            # Run analysis
            BM, Cij = lammps_setup.analysis_mechanical_proerties(
                analysis_folder=analysis_folder,
                ensemble=ENSEMBLE,
                deformation_rates=DEFORMATION_RATES,
                method=METHOD,
                time_fraction=TIME_FRACTION,
                visualize_stress_strain=VISUALIZE_STRESS_STRAIN,
            )

            print(f"✅ Analyzed {tob_structure} with {lj_set}: BM = {BM:.2f} GPa")
            bm_results[tob_structure].append(BM)
            cij_results[tob_structure].append(Cij)

        except Exception as e:
            print(f"❌ Failed to analyze {tob_structure} with {lj_set}: {e}")
            bm_results[tob_structure].append(None)
            cij_results[tob_structure].append(None)
            continue

# save bm_results and cij_results
with open('results_bm123.pkl', 'wb') as f:
    pickle.dump(bm_results, f)

with open('results_cij123.pkl', 'wb') as f:
    pickle.dump(cij_results, f)






# #load den_results 50
# with open("results_den50.pkl", "rb") as f:
#     den_results_50 = pickle.load(f)


# #load den_results last 18
# with open("results_den68.pkl", "rb") as f:
#     den_results_18 = pickle.load(f)



# # Start with a copy to avoid modifying the original
# den_results = {'density': den_results_50['density'].copy()}

# # Now update/append from den_results_18
# for key, value in den_results_18['density'].items():
#     if key in den_results['density']:
#         den_results['density'][key].extend(value)
#     else:
#         den_results['density'][key] = value



# #load se_results 50
# with open("results_se50.pkl", "rb") as f:
#     se_results_50 = pickle.load(f)


# #load se_results last 18
# with open("results_se68.pkl", "rb") as f:
#     se_results_18 = pickle.load(f)


# # Start with a copy to avoid modifying the original
# se_results = se_results_50.copy()

# # Now update/append from se_results_18
# for key, value in se_results_18.items():
#     if key in se_results:
#         se_results[key].extend(value)
#     else:
#         se_results[key] = value


# #load bm_results 50
# with open("results_bm50.pkl", "rb") as f:
#     bm_results_50 = pickle.load(f)


# #load bm_results last 18
# with open("results_bm68.pkl", "rb") as f:
#     bm_results_18 = pickle.load(f)


# # Start with a copy to avoid modifying the original
# bm_results = bm_results_50.copy()

# # Now update/append from bm_results_18
# for key, value in bm_results_18.items():
#     if key in bm_results:
#         bm_results[key].extend(value)
#     else:
#         bm_results[key] = value




# # create a dataframe with sc_r, oc_r, sc_eps, oc_eps, density, surface energy, bulk modulus
# import pandas as pd
# df = pd.DataFrame({
#     'sc_r': sc_r_values_n,
#     'sc_eps': sc_eps_values_n,
#     'oc_r': oc_r_values_n,
#     'oc_eps': oc_eps_values_n,
    
#     'D_9': np.array(den_results['density']['Tob9']).reshape(-1),
#     'D_11': np.array(den_results['density']['Tob11']).reshape(-1),
#     'D_11H': np.array(den_results['density']['Tob11H']).reshape(-1),
#     'D_14': np.array(den_results['density']['Tob14']).reshape(-1),
    
#     'SE_T9': np.array(se_results['Tob9'])[:,0],
#     'SE_T11': np.array(se_results['Tob11'])[:,0],
#     'SE_T11H': np.array(se_results['Tob11H'])[:,0],
#     'SE_T14': np.array(se_results['Tob14'])[:,0],
    
#     'BM_T9': np.array(bm_results['Tob9']),
#     'BM_T11': np.array(bm_results['Tob11']),
#     'BM_T11H': np.array(bm_results['Tob11H']),
#     'BM_T14': np.array(bm_results['Tob14'])
    
# })

# # save the df
# df.to_csv('training_data_68.csv', index=False)

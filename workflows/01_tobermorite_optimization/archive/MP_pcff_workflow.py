from mdsetup import MDSetup
import os

# os.chdir('')

# Initialize MDSetup
lammps_setup = MDSetup(
    system_setup="input_tob_all/setup_mechanical_pcff.yaml",
    simulation_default="input_tob_all/defaults.yaml",
    simulation_ensemble="input_tob_all/ensemble.yaml",
    simulation_sampling="input_tob_all/sampling_mechanical.yaml",
    submission_command="qsub",
)

# Define paths
LJ_SETS = [f"LJ_set_{i+1}" for i in range(68, 118)]

# ## 1. Setting up equilibration
# TOB_STRUCTURES = {
#     "Tob9": "tob9_122.data",
#     "Tob11": "tob11_221.data",
#     "Tob11H": "tob11H_221.data",
#     "Tob14": "tob14_221.data",
# }

# # Loop over LJ parameter sets and Tob structures
# for lj_set in LJ_SETS:
#     for tob_structure, data_file in TOB_STRUCTURES.items():
#         # Define simulation folder
#         simulation_folder = f"{tob_structure}/{lj_set}/equilibration"
        
#         # Define initial data file path
#         initial_systems = [f"input_tob_all/{lj_set}/{tob_structure}/{data_file}"]

#         # Prepare simulation
#         lammps_setup.prepare_simulation(
#             folder_name=simulation_folder,
#             ensembles=["em", "npt"],
#             simulation_times=[0.1, 1.0],
#             initial_systems=initial_systems,
#             input_kwargs={},
#             copies=0,
#             off_set=0,
#         )

#         # Submit the simulation job
#         lammps_setup.submit_simulation()
#         print(f"✅ Submitted job for {tob_structure} with {lj_set}")

# ## 2 (i). Setting up surface energy calculations sys1 - bulk:
# TOB_STRUCTURES = {
#     "Tob9": "Tob9_001_004_bulk.data",
#     "Tob11": "Tob11_004_Bulk_cV05_r00.data",
#     "Tob11H": "Tob11_Hamid_004_002_Bulk_cV02_r00.data",
#     "Tob14": "Tob14_001_004_Bulk_cV07_r01.data",
# }

# # Loop over LJ parameter sets and Tob structures
# for lj_set in LJ_SETS:
#     for tob_structure, data_file in TOB_STRUCTURES.items():
#         # Define simulation folder
#         simulation_folder = f"{tob_structure}/{lj_set}/SE/bulk"
#         # Define initial data file path
#         initial_systems = [f"input_tob_all/{lj_set}/{tob_structure}/{data_file}"]

#         # Prepare simulation
#         lammps_setup.prepare_simulation(
#             folder_name=simulation_folder,
#             ensembles=["nvt"],
#             simulation_times=[1.0],
#             initial_systems=initial_systems,
#             input_kwargs={},
#             copies=0,
#             off_set=0,
#         )

#         # Submit the simulation job
#         lammps_setup.submit_simulation()
#         print(f"✅ Submitted job for {tob_structure} with {lj_set}")

# ## 2 (ii). Setting up surface energy calculations sys2 - cleaved:
# TOB_STRUCTURES = {
#     "Tob9": "Tob9_004_vacuum.data",
#     "Tob11": "Tob11_004_vacuum_cV05_r01.data",
#     "Tob11H": "Tob11_Hamid_004_Cleaved_cV02_r00.data",
#     "Tob14": "Tob14_004_vacuum_cV07_r01.data",
# }

# # Loop over LJ parameter sets and Tob structures
# for lj_set in LJ_SETS:
#     for tob_structure, data_file in TOB_STRUCTURES.items():
#         # Define simulation folder
#         simulation_folder = f"{tob_structure}/{lj_set}/SE/vacuum"
#         # Define initial data file path
#         initial_systems = [f"input_tob_all/{lj_set}/{tob_structure}/{data_file}"]

#         # Prepare simulation
#         lammps_setup.prepare_simulation(
#             folder_name=simulation_folder,
#             ensembles=["nvt"],
#             simulation_times=[1.0],
#             initial_systems=initial_systems,
#             input_kwargs={},
#             copies=0,
#             off_set=0,
#         )

#         # Submit the simulation job
#         lammps_setup.submit_simulation()
#         print(f"✅ Submitted job for {tob_structure} with {lj_set}")



## 3. Setting up deformation
TOB_STRUCTURES = {
    "Tob9": "tob9_122.data",
    "Tob11": "tob11_221.data",
    "Tob11H": "tob11H_221.data",
    "Tob14": "tob14_221.data",
}

# Deformation directions and rates
deformation_directions = ["xx", "yy", "zz", "xy", "xz", "yz", "undeformed"]
deformation_rates = [-0.02, -0.01, 0.00, 0.01, 0.02]
ensembles = ["nvt"]
simulation_times = [1.0]
copies = 0
off_set = 0

# Loop over each LJ set and Tob structure
for lj_set in LJ_SETS:
    for tob_structure, data_file in TOB_STRUCTURES.items():
        # Path to equilibrated system
        initial_systems = [
            f"output_tob_all/pcff_lj_params/{tob_structure}/{lj_set}/equilibration/temp_298.1_pres_1.0/copy_0/01_npt/npt.data"
        ]

        # Setup job_files array per temperature state
        job_files = [[] for _ in lammps_setup.system_setup["temperature"]]

        for deformation_direction in deformation_directions:
            for deformation_rate in deformation_rates:
                # Skip redundant combinations
                if (deformation_rate == 0.0 and deformation_direction != "undeformed") or (
                    deformation_rate != 0.0 and deformation_direction == "undeformed"
                ):
                    continue

                # Define folder path
                simulation_folder = (
                    f"{tob_structure}/{lj_set}/deformation/{deformation_direction}/{deformation_rate}"
                )

                # Input arguments to control deformation
                input_kwargs = {
                    "deformation": {
                        "direction": deformation_direction,
                        "rate": deformation_rate,
                    }
                }

                # Prepare simulation
                lammps_setup.prepare_simulation(
                    folder_name=simulation_folder,
                    ensembles=ensembles,
                    simulation_times=simulation_times,
                    initial_systems=initial_systems,
                    input_kwargs=input_kwargs,
                    copies=copies,
                    off_set=off_set,
                )

                for j, files in enumerate(lammps_setup.job_files):
                    job_files[j].extend(files)

        # Update job_files and submit
        lammps_setup.job_files = job_files
        lammps_setup.submit_simulation(individual_sub=False)
        print(f"✅ Submitted deformation jobs for {tob_structure} with {lj_set}")

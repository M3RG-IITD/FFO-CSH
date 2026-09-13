
import os
import shutil
import subprocess

import time
import numpy as np
import pandas as pd
import pickle
from mdsetup import MDSetup


def MD_sim_csh(optimizer='None'):
    def deform_job_count():
        result = subprocess.run(
            f"qstat -awTu $USER | grep {optimizer}_def* | wc -l",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        return int(result.stdout.strip())

    def equil_job_count():
        result = subprocess.run(
            f"qstat -awTu $USER | grep {optimizer}_eq* | wc -l",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        return int(result.stdout.strip())

    # 2. Simulation with MDSetup

    # === Change to working dir and initialize MDSetup ===
    # TODO: Update working directory for your local setup

    lammps_setup = MDSetup(
        system_setup="config/cvff/setup_mechanical_charge_cvff.yaml",
        simulation_default="config/cvff/defaults.yaml",
        simulation_ensemble="config/cvff/ensemble.yaml",
        simulation_sampling="config/cvff/sampling_mechanical.yaml",
        submission_command="qsub",
    )
    
    CSH_DATASETS = [f for f in os.listdir('../../data/structures/csh') if f.endswith('.data')]
    # CSH_DATASETS = ['CaSi-1.2_WSi-1.2_1_IFF.data']
    
    # === 1. Equilibration ===
    for idx, data_file in enumerate(CSH_DATASETS):
        lammps_setup.prepare_simulation(
            folder_name=f"equilibration/{idx}",
            ensembles=["em", "npt"],
            simulation_times=[0.1, 1.0],
            initial_systems=[f"../../data/structures/csh/{data_file}"],
            input_kwargs={},
            copies=0,
            off_set=0,
        )
        lammps_setup.submit_simulation()
        print(f"✅ Submitted equilibration for {data_file}")

    # === 3. Deformation (after equil is done) ===
    while True:
        if equil_job_count() <= 0:
            print("✨ Submitting deformation jobs...")

            deformation_directions = ["xx", "yy", "zz", "xy", "xz", "yz", "undeformed"]
            deformation_rates = [-0.02, -0.01, 0.00, 0.01, 0.02]

            for idx, data_file in enumerate(CSH_DATASETS):
                try:
                    initial_systems = [f"equilibration/{idx}/temp_298.1_pres_1.0/copy_0/01_npt/npt.data"]
                    job_files = [[] for _ in lammps_setup.system_setup["temperature"]]

                    for direction in deformation_directions:
                        for rate in deformation_rates:
                            if (rate == 0.0 and direction != "undeformed") or (rate != 0.0 and direction == "undeformed"):
                                continue
                            folder = f"deformation/{idx}/{direction}/{rate}"
                            input_kwargs = {"deformation": {"direction": direction, "rate": rate}}

                            lammps_setup.prepare_simulation(
                                folder_name=folder,
                                ensembles=["nvt"],
                                simulation_times=[1.0],
                                initial_systems=initial_systems,
                                input_kwargs=input_kwargs,
                                copies=0,
                                off_set=0,
                            )
                            for j, files in enumerate(lammps_setup.job_files):
                                job_files[j].extend(files)

                    lammps_setup.job_files = job_files
                    lammps_setup.submit_simulation(individual_sub=False)
                    print(f"✅ Deformation jobs for {data_file}")
                except Exception as e:
                    print(f"❌ Deformation error for {data_file}: {e}")
                    continue
            break
        else:
            print(f"⏳ Waiting: {equil_job_count()} equil jobs still running...")
            time.sleep(30)

    print("🎉 All charge optimization jobs submitted.")


    # 3. Analysis
    while True:
        if (equil_job_count() + deform_job_count()) <= 0:
            import re as _re

            def parse_casi_ratio(filename):
                """Extract Ca/Si ratio from filename like CaSi-1.2_WSi-1.6_3_IFF.data."""
                m = _re.match(r'CaSi-([\d.]+)', filename)
                return float(m.group(1)) if m else None

            results = []

            for idx, data_file in enumerate(CSH_DATASETS):
                casi_ratio = parse_casi_ratio(data_file)

                # --- Density ---
                den_mean, den_std = None, None
                try:
                    extracted = lammps_setup.analysis_extract_properties(
                        analysis_folder=f"equilibration/{idx}",
                        ensemble='01_npt',
                        extracted_properties=['density'],
                        output_suffix='density',
                        time_fraction=0.2,
                    )
                    avg = extracted.get('01_npt', {}).get("data", {}).get("average", {})
                    den_mean = avg.get('density', {}).get("mean")
                    den_std = avg.get('density', {}).get("std")
                except Exception as e:
                    print(f"❌ Density analysis failed for {data_file}: {e}")

                # --- Bulk modulus ---
                bm_mean, bm_std = None, None
                try:
                    BM, BM_std_val, _, _ = lammps_setup.analysis_mechanical_proerties(
                        analysis_folder=f"deformation/{idx}",
                        ensemble="00_nvt",
                        deformation_rates=[-0.02, -0.01, 0.00, 0.01, 0.02],
                        method="VRH",
                        time_fraction=0.4,
                        visualize_stress_strain=False,
                    )
                    bm_mean, bm_std = BM, BM_std_val
                except Exception as e:
                    print(f"❌ BM analysis failed for {data_file}: {e}")

                results.append({
                    'data_file': data_file,
                    'CaSi_ratio': casi_ratio,
                    'density_mean': den_mean,
                    'density_std': den_std,
                    'bulk_modulus_mean': bm_mean,
                    'bulk_modulus_std': bm_std,
                })

            # === Save Results ===
            OUTPUT_DIR = f'runs/csh_transfer/{optimizer}'
            os.makedirs(OUTPUT_DIR, exist_ok=True)

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            pickle_path = os.path.join(OUTPUT_DIR, f"results_{timestamp}.pkl")
            csv_path = os.path.join(OUTPUT_DIR, f"results_{timestamp}.csv")

            with open(pickle_path, 'wb') as f:
                pickle.dump({'optimizer': optimizer, 'results': results}, f)

            df = pd.DataFrame(results)
            df.sort_values('CaSi_ratio', inplace=True)
            df.to_csv(csv_path, index=False)

            print(f"✅ Analysis completed and saved to:\n📁 {csv_path}\n📦 {pickle_path}")
            return df

        else:
            print(f"{deform_job_count()} deformation jobs still running. Waiting (for Analysis)...")
            time.sleep(30)











# import subprocess

# def job_count():
#     result = subprocess.run(
#         f"qstat -awTu $USER | grep ^[0-9] | grep R | wc -l",
#         shell=True,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         universal_newlines=True
#     )
#     return int(result.stdout.strip())


# # === Change to working dir and initialize MDSetup ===
# # TODO: Update working directory for your local setup

# lammps_setup = MDSetup(
#     system_setup="config/setup_mechanical_charge_cvff_deform.yaml",
#     simulation_default="config/cvff/defaults.yaml",
#     simulation_ensemble="config/cvff/ensemble.yaml",
#     simulation_sampling="config/cvff/sampling_mechanical.yaml",
#     submission_command="qsub",
# )


# import time
# while True:
#     if (job_count()==1):
#         print("All jobs are done, proceeding to deformation simulations.")
        
#         CSH_DATASETS = [f for f in os.listdir('../../data/structures/csh') if f.endswith('.data')]

#         deformation_directions = ["xx", "yy", "zz", "xy", "xz", "yz", "undeformed"]
#         deformation_rates = [-0.02, -0.01, 0.00, 0.01, 0.02]
#         num_run = len(os.listdir('cvff'))
#         for data_file in CSH_DATASETS:
#             # if 'CaSi-2.1' in data_file:
#             #     print('skipping')
#             # else:
#             initial_systems = [f"cvff/run{num_run}/{data_file.split('_')[0]}/equilibration/temp_298.1_pres_1.0/copy_0/01_npt/npt.data"]
#             job_files = [[] for _ in lammps_setup.system_setup["temperature"]]

#             for direction in deformation_directions:
#                 for rate in deformation_rates:
#                     if (rate == 0.0 and direction != "undeformed") or (rate != 0.0 and direction == "undeformed"):
#                         continue
#                     else:
#                         folder = (f"run{num_run}/{data_file.split('_')[0]}/deformation/{direction}/{rate}")
#                         input_kwargs = {"deformation": {"direction": direction, "rate": rate}}

#                         lammps_setup.prepare_simulation(
#                             folder_name=folder,
#                             ensembles=["nvt"],
#                             simulation_times=[1.0],
#                             initial_systems=initial_systems,
#                             input_kwargs=input_kwargs,
#                             copies=0,
#                             off_set=0,
#                         )
#                         for j, files in enumerate(lammps_setup.job_files):
#                             print(j)
#                             job_files[j].extend(files)

#             lammps_setup.job_files = job_files
#             lammps_setup.submit_simulation(individual_sub=False)
#             print(f"✅ Deformation jobs for {data_file}")
#         break
        
#     else:
#         print(f"⏳ Waiting: equil jobs still running...")
#         time.sleep(60)
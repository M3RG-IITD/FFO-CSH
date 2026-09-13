import os
import time
import shutil
import subprocess
from mdsetup import MDSetup
import pandas as pd
import numpy as np
import pickle


def MD_sim(suggested_params, optimizer='None'):
    
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


    # 1. Data generation
    BASE_DIR = "../../data/structures/templates"
    TEMPLATE_FRC = os.path.join(BASE_DIR, "pcff_template.frc")
    TOB_DIRS = ["Tob11_car_mdf", "Tob11H_car_mdf", "Tob14_car_mdf"]

    lj_dir = [d for d in os.listdir("../../data/structures/lj_sets") if os.path.isdir(os.path.join("../../data/structures/lj_sets", d)) and d.startswith("LJ_set_")]
    if lj_dir:
        lj_dir.sort(key=lambda x: int(x.split("_")[2]) if len(x.split("_")) > 2 and x.split("_")[2].isdigit() else float("inf"))
        num = [i for i in lj_dir[-1].split("_") if i.isdigit() and len(i) > 0][0]
        count1 = int(num)
    else:
        count1 = 0

    for i, (sc_r, sc_eps, oc_r, oc_eps, ocx_r, ocx_eps, sos_ktheta, oso_ktheta, so_kr) in enumerate(zip(*suggested_params.T)):
        i += count1
        param_dir = os.path.join("../../data/structures/lj_sets", f"LJ_set_{i+1}_{optimizer}")
        os.makedirs(param_dir, exist_ok=True)

        # Modify FRC file
        with open(TEMPLATE_FRC, "r") as f:
            frc_content = f.read()
        
        # Replace placeholders
        frc_content = frc_content.replace("{sc_r}", str(sc_r))
        frc_content = frc_content.replace("{sc_eps}", str(sc_eps))
        frc_content = frc_content.replace("{oc_r}", str(oc_r))
        frc_content = frc_content.replace("{oc_eps}", str(oc_eps))
        frc_content = frc_content.replace("{ocx_r}", str(ocx_r))
        frc_content = frc_content.replace("{ocx_eps}", str(ocx_eps))
        
        frc_content = frc_content.replace("{sos_ktheta}", str(sos_ktheta))
        frc_content = frc_content.replace("{oso_ktheta}", str(oso_ktheta))
        
        frc_content = frc_content.replace("{so_kr}", str(so_kr))
        
        frc_path = os.path.join(param_dir, f"modified_LJ_{i+1}.frc")
        otp_path = os.path.join(param_dir, f"optimizer{i+1}.txt")
        with open(frc_path, "w") as f:
            f.write(frc_content)
        
        with open(otp_path, "w") as f:
            f.write(optimizer + "\n")
        
        print(f"🔧 MD simulation for LJ_set_{i+1}_{optimizer} using optimizer: {optimizer}")
    
        # Run msi2lmp
        for tob_dir in TOB_DIRS:
            dir_path = os.path.join(BASE_DIR, tob_dir)
            output_folder = os.path.join(param_dir, tob_dir.split("_")[0])
            os.makedirs(output_folder, exist_ok=True)

            prefixes = sorted(set("_".join(f.split(".")[:-1]) for f in os.listdir(dir_path) if f.endswith((".car", ".mdf"))))
            for prefix in prefixes:
                output_prefix = os.path.join(dir_path, prefix)
                cmd = ["msi2lmp", output_prefix, "-class", "2", "-frc", os.path.join(param_dir, f"modified_LJ_{i+1}.frc"), "-ignore"]
                print(f"Running: {' '.join(cmd)} with LJ_set_{i+1}_{optimizer}")
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

                if result.returncode == 0:
                    print(f"✅ Successfully generated {prefix}.data for LJ_set_{i+1}_{optimizer}")
                    try:
                        shutil.move(f"{output_prefix}.data", output_folder)
                    except Exception as e:
                        print(f"⚠️ Unexpected error: {e}")
                else:
                    print(f"❌ Error in {prefix}: {result.stderr}")

    count2 = count1 + len(suggested_params)

    # 2. MDSetup
    # Working directory: run from workflows/01_tobermorite_optimization/
    lammps_setup = MDSetup(
        system_setup="config/setup_mechanical_pcff.yaml",
        simulation_default="config/defaults.yaml",
        simulation_ensemble="config/ensemble.yaml",
        simulation_sampling="config/sampling_mechanical.yaml",
        submission_command="qsub",
    )

    LJ_SETS = [f"LJ_set_{i+1}_{optimizer}" for i in range(count1, count2)]

    # 2.1. Equilibration Setup
    TOB_STRUCTURES = {
        "Tob11": "tob11_221.data",
        "Tob11H": "tob11H_221.data",
        "Tob14": "tob14_221.data",
    }

    for lj_set in LJ_SETS:
        for tob_structure, data_file in TOB_STRUCTURES.items():

            lammps_setup.prepare_simulation(
                folder_name=f"{tob_structure}/{lj_set}/equilibration",
                ensembles=["em", "npt"],
                simulation_times=[0.1, 1.0],
                initial_systems=[f"../../data/structures/lj_sets/{lj_set}/{tob_structure}/{data_file}"],
                input_kwargs={},
                copies=0,
                off_set=0,
            )
            lammps_setup.submit_simulation()
            print(f"✅ Submitted job for {tob_structure} with {lj_set}")

    # 2.2.(i). Surface Energy - Bulk
    SE_STRUCTURES_BULK = {
        "Tob11": "Tob11_004_Bulk_cV05_r00.data",
        "Tob11H": "Tob11_Hamid_004_002_Bulk_cV02_r00.data",
        "Tob14": "Tob14_001_004_Bulk_cV07_r01.data",
    }

    for lj_set in LJ_SETS:
        for tob_structure, data_file in SE_STRUCTURES_BULK.items():
            lammps_setup.prepare_simulation(
                folder_name=f"{tob_structure}/{lj_set}/SE/bulk",
                ensembles=["nvt"],
                simulation_times=[1.0],
                initial_systems=[f"../../data/structures/lj_sets/{lj_set}/{tob_structure}/{data_file}"],
                input_kwargs={},
                copies=0,
                off_set=0,
            )
            lammps_setup.submit_simulation()
            print(f"✅ Submitted job for {tob_structure} with {lj_set}")

    # 2.2.(ii). Surface Energy - Cleaved
    SE_STRUCTURES_VACUUM = {
        "Tob11": "Tob11_004_vacuum_cV05_r01.data",
        "Tob11H": "Tob11_Hamid_004_Cleaved_cV02_r00.data",
        "Tob14": "Tob14_004_vacuum_cV07_r01.data",
    }

    for lj_set in LJ_SETS:
        for tob_structure, data_file in SE_STRUCTURES_VACUUM.items():
            lammps_setup.prepare_simulation(
                folder_name=f"{tob_structure}/{lj_set}/SE/vacuum",
                ensembles=["nvt"],
                simulation_times=[1.0],
                initial_systems=[f"../../data/structures/lj_sets/{lj_set}/{tob_structure}/{data_file}"],
                input_kwargs={},
                copies=0,
                off_set=0,
            )
            lammps_setup.submit_simulation()
            print(f"✅ Submitted job for {tob_structure} with {lj_set}")

    # 2.3. Deformation Jobs
    while True:
        if equil_job_count() <= 0:
            print("Submitting deformation jobs...")
            deformation_directions = ["xx", "yy", "zz", "xy", "xz", "yz", "undeformed"]
            deformation_rates = [-0.02, -0.01, 0.00, 0.01, 0.02]

            for lj_set in LJ_SETS:
                try:
                    for tob_structure, data_file in TOB_STRUCTURES.items():
                        initial_systems = [f"runs/pcff_lj_params/{tob_structure}/{lj_set}/equilibration/temp_298.1_pres_1.0/copy_0/01_npt/npt.data"]
                        job_files = [[] for _ in lammps_setup.system_setup["temperature"]]

                        for direction in deformation_directions:
                            for rate in deformation_rates:
                                if (rate == 0.0 and direction != "undeformed") or (rate != 0.0 and direction == "undeformed"):
                                    continue
                                folder = f"{tob_structure}/{lj_set}/deformation/{direction}/{rate}"
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
                        print(f"✅ Submitted deformation jobs for {tob_structure} with {lj_set}")
                except Exception as e:
                    print(f"❌ Error submitting deformation jobs for {tob_structure} with {lj_set}: {e}")
                    continue
            break
        else:
            print(f"{equil_job_count()} equilibrium jobs still running. Waiting (for deformation)...")
            time.sleep(30)
    
    print("All jobs submitted successfully.")
    

    #3. Analysis
    while True:
        if (equil_job_count()+deform_job_count()) <= 0:
            
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

            sc_r, sc_eps, oc_r, oc_eps, ocx_r, ocx_eps, sos_ktheta, oso_ktheta, so_kr =  suggested_params[:, 0], suggested_params[:, 1], suggested_params[:, 2], suggested_params[:, 3], suggested_params[:, 4], suggested_params[:, 5], suggested_params[:, 6], suggested_params[:, 7], suggested_params[:, 8]
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            # Save results to a pickle file
            with open(f"runs/pcff_lj_params/data_LJ_{count1}_{count2}_{timestamp}.pkl", 'wb') as f:
                results = {
                    'optimizers': [optimizer] * len(suggested_params),
                    'sc_r_values_n': sc_r,
                    'sc_eps_values_n': sc_eps,
                    'oc_r_values_n': oc_r,
                    'oc_eps_values_n': oc_eps,
                    'ocx_r_values_n': ocx_r,
                    'ocx_eps_values_n': ocx_eps,
                    'sos_ktheta_values_n': sos_ktheta,
                    'oso_ktheta_values_n': oso_ktheta,
                    'so_kr_values_n': so_kr,
                    'den_results': den_results,
                    'se_results': se_results,
                    'bm_results': bm_results
                }
                pickle.dump(results, f)
            
            df = pd.DataFrame({
                'optimizers': [optimizer] * len(suggested_params),
                'sc_r': sc_r,
                'sc_eps': sc_eps,
                'oc_r': oc_r,
                'oc_eps': oc_eps,
                'ocx_r': ocx_r,
                'ocx_eps': ocx_eps,
                'sos_ktheta': sos_ktheta,
                'oso_ktheta': oso_ktheta,
                'so_kr': so_kr,
                
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

            df_full_new.to_csv(f"runs/pcff_lj_params/data_LJ_{count1}_{count2}_{timestamp}.csv", index=False)
            print(f"✅ All jobs completed and data saved as runs/pcff_lj_params/data_LJ_{count1}_{count2}_{timestamp}.csv")
            return df_full_new
        
        else:
            print(f"{deform_job_count()} deformation jobs still running. Waiting (for Analysis)...")
            time.sleep(30)

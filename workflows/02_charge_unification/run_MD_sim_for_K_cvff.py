import os
import shutil
import subprocess

import time
import numpy as np
import pandas as pd
import pickle
from mdsetup import MDSetup


def MD_sim_charge(Q_VALS_DEN, Q_VALS_SE, Q_VALS_SE14, optimizer='None'):
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
    TEMPLATE_CAR_MDF_DIR = os.path.join(BASE_DIR, "template_car_mdf/replaced")
    # TEMPLATE_CAR_MDF_DIR = os.path.join(BASE_DIR, "template_car_mdf")
    TOB_DIRS = ["Tob11_car_mdf", "Tob11H_car_mdf", "Tob14_car_mdf"]
    CHARGE_DIR = os.path.join(BASE_DIR, "../Charge_Opt/CVFF")

    TEMPLATE_LJ_FRC_PATH = os.path.join(BASE_DIR, "cvff_template.frc")
    BEST_LJ_FRC_PATH = os.path.join(BASE_DIR, "CVFF_best_LJ.frc")


    sc_r, sc_eps, oc_r, oc_eps, ocx_r, ocx_eps, sos_ktheta, oso_ktheta, so_kr = [4.316, 0.440, 3.715, 0.045, 3.715, 0.045, 100, 100, 350]
    # sc_r, sc_eps, oc_r, oc_eps, ocx_r, ocx_eps, sos_ktheta, oso_ktheta, so_kr = [4.361, 0.440, 3.715, 0.045, 3.715, 0.045, 100, 100, 350]
    ca_r, ca_eps, cat_r, cat_eps = [3.350, 0.290, 3.350, 0.290]
    # CHARMM -> CVFF
    ca_a = ca_eps * ca_r**12
    ca_b = 2 * ca_eps * ca_r**6
    cat_a = cat_eps * cat_r**12
    cat_b = 2 * cat_eps * cat_r**6

    sc_a = sc_eps * sc_r**12
    sc_b = 2 * sc_eps * sc_r**6
    oc_a = oc_eps * oc_r**12
    oc_b = 2 * oc_eps * oc_r**6
    ocx_a = ocx_eps * ocx_r**12
    ocx_b = 2 * ocx_eps * ocx_r**6
    sos_ktheta = sos_ktheta
    oso_ktheta = oso_ktheta
    so_kr = so_kr
    
    
    sc2_oc12 = 1.658 #iff_value = 1.70
    sc3_oc12 = 1.658 #iff_value = 1.70
    sc3_ocx  = 1.658 #iff_value = 1.62
    sc2_oc13 = 1.658 #iff_value = 1.62
    sc3_oc14 = 1.658 #iff_value = 1.68
    sc3_oc22 = 1.658 #iff_value = 1.59
    
    sc2_oc12_sc3  = 141.5 #iff_value = 139.0
    sc2_oc12_sc2  = 141.5 #iff_value = 144.0
    sc3_ocx_sc3  =  174.5 #iff_value = 174.5
    oc12_sc2_oc12 = 109.47 #iff_value = 100.2
    oc12_sc3_oc12 = 109.47 #iff_value = 107.0
    oc14_sc3_oc14 = 109.47 #iff_value = 113.0
    oc12_sc2_oc13 = 109.47 #iff_value = 111.5
    oc13_sc2_oc13 = 109.47 #iff_value = 112.5
    oc12_sc3_oc14 = 109.47 #iff_value = 111.0

    
    with open(TEMPLATE_LJ_FRC_PATH, "r") as f:
        frc_content = f.read()

    # Replace placeholders
    frc_content = frc_content.replace("{ca_a}", str(ca_a))
    frc_content = frc_content.replace("{ca_b}", str(ca_b))
    frc_content = frc_content.replace("{cat_a}", str(cat_a))
    frc_content = frc_content.replace("{cat_b}", str(cat_b))

    frc_content = frc_content.replace("{sc_a}", str(sc_a))
    frc_content = frc_content.replace("{sc_b}", str(sc_b))
    frc_content = frc_content.replace("{oc_a}", str(oc_a))
    frc_content = frc_content.replace("{oc_b}", str(oc_b))
    frc_content = frc_content.replace("{ocx_a}", str(ocx_a))
    frc_content = frc_content.replace("{ocx_b}", str(ocx_b))

    frc_content = frc_content.replace("{sos_ktheta}", str(sos_ktheta))
    frc_content = frc_content.replace("{oso_ktheta}", str(oso_ktheta))

    frc_content = frc_content.replace("{so_kr}", str(so_kr))
    
    frc_content = frc_content.replace("{sc2_oc12}", str(sc2_oc12))
    frc_content = frc_content.replace("{sc3_oc12}", str(sc3_oc12))
    frc_content = frc_content.replace("{sc3_ocx}", str(sc3_ocx))
    frc_content = frc_content.replace("{sc2_oc13}", str(sc2_oc13))
    frc_content = frc_content.replace("{sc3_oc14}", str(sc3_oc14))
    frc_content = frc_content.replace("{sc3_oc22}", str(sc3_oc22))
    
    frc_content = frc_content.replace("{sc2_oc12_sc3}", str(sc2_oc12_sc3))
    frc_content = frc_content.replace("{sc2_oc12_sc2}", str(sc2_oc12_sc2))
    frc_content = frc_content.replace("{sc3_ocx_sc3}", str(sc3_ocx_sc3))
    frc_content = frc_content.replace("{oc12_sc2_oc12}", str(oc12_sc2_oc12))
    frc_content = frc_content.replace("{oc12_sc3_oc12}", str(oc12_sc3_oc12))
    frc_content = frc_content.replace("{oc14_sc3_oc14}", str(oc14_sc3_oc14))
    frc_content = frc_content.replace("{oc12_sc2_oc13}", str(oc12_sc2_oc13))
    frc_content = frc_content.replace("{oc13_sc2_oc13}", str(oc13_sc2_oc13))
    frc_content = frc_content.replace("{oc12_sc3_oc14}", str(oc12_sc3_oc14))
    

    with open(BEST_LJ_FRC_PATH, "w") as f:
        f.write(frc_content)

    # === Find latest Charge_set index ===
    existing_dirs = [d for d in os.listdir(CHARGE_DIR) if d.startswith("Charge_set_")]
    existing_dirs.sort(key=lambda x: int(x.split('_')[2]) if len(x.split('_')) > 2 and x.split('_')[2].isdigit() else float('inf'))
    start_index = int(existing_dirs[-1].split('_')[-2]) + 1 if existing_dirs else 1
    end_index = start_index
    
    # for idx, q_vals in enumerate(Q_VALS, start=start_index):
    q_vals_den, q_vals_se, q_vals_se14, idx = Q_VALS_DEN, Q_VALS_SE, Q_VALS_SE14, start_index
    
    def select_charge_scheme(folder_name, file_name):
        if "Tob14" in folder_name:
            return q_vals_se14 if any(tag in file_name for tag in ['Bulk', 'vacuum', 'Cleaved']) else q_vals_den
        else:
            return q_vals_se if any(tag in file_name for tag in ['Bulk', 'vacuum', 'Cleaved']) else q_vals_den

    def replace_charges(file_path, q_vals):
        with open(file_path, "r") as f:
            content = f.read()
        for placeholder, val in q_vals.items():
            content = content.replace(placeholder, f"{val:.5f}")
        return content

        
    end_index+= 1
    # === Main Data Generation ===
    charge_dir = os.path.join(CHARGE_DIR, f"Charge_set_{idx}_{optimizer}")
    os.makedirs(charge_dir, exist_ok=True)

    print(f"\n🔧 Generating .data files (Charge_set_{idx}_{optimizer})")

    for tob_dir in TOB_DIRS:
        template_path = os.path.join(TEMPLATE_CAR_MDF_DIR, tob_dir)
        output_subdir = os.path.join(charge_dir, tob_dir.split("_")[0])
        os.makedirs(output_subdir, exist_ok=True)

        # Find all prefix names, Skip 'temp' files when building prefix list
        prefixes = sorted(set("_".join(f.split(".")[:-1]) for f in os.listdir(template_path) if f.endswith((".car", ".mdf")) and not f.startswith("temp_cvff")))

        for prefix in prefixes:

            car_path = os.path.join(template_path, prefix + ".car")
            mdf_path = os.path.join(template_path, prefix + ".mdf")

            # Select proper charge scheme based on polymorph and cleavage type
            q_vals = select_charge_scheme(tob_dir, prefix)

            # Replace charges in .car and .mdf
            car_content = replace_charges(car_path, q_vals)
            mdf_content = replace_charges(mdf_path, q_vals)

            temp_prefix = os.path.join(template_path, "temp_cvff")
            temp_car_path = temp_prefix + ".car"
            temp_mdf_path = temp_prefix + ".mdf"

            with open(temp_car_path, "w") as f:
                f.write(car_content)
            with open(temp_mdf_path, "w") as f:
                f.write(mdf_content)

            # Run msi2lmp
            cmd = ["msi2lmp", temp_prefix, "-class", "1", "-frc", BEST_LJ_FRC_PATH, "-ignore"]
            print(f"⚙️  Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

            if result.returncode == 0:
                print(f"✅ Created {prefix}.data")
                try:
                    shutil.move(temp_prefix + ".data", os.path.join(output_subdir, f"{prefix}.data"))
                except Exception as e:
                    print(f"⚠️ Move error: {e}")
            else:
                print(f"❌ msi2lmp failed for {prefix}:\n{result.stderr}")

            # Clean up temp files
            for ext in [".car", ".mdf"]:
                try:
                    os.remove(temp_prefix + ext)
                except FileNotFoundError:
                    pass

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

    # CHARGE_SETS from start_index to end_index
    CHARGE_SETS = [f"Charge_set_{i}_{optimizer}" for i in range(start_index, end_index)]

    TOB_STRUCTURES = {
        "Tob11": "tob11_221.data",
        "Tob11H": "tob11H_221.data",
        "Tob14": "tob14_221.data",
    }
    SE_STRUCTURES_BULK = {
        "Tob11": "Tob11_004_Bulk_cV05_r00.data",
        "Tob11H": "Tob11_Hamid_004_002_Bulk_cV02_r00.data",
        "Tob14": "Tob14_001_004_Bulk_cV07_r01.data",
    }
    SE_STRUCTURES_VACUUM = {
        "Tob11": "Tob11_004_vacuum_cV05_r01.data",
        "Tob11H": "Tob11_Hamid_004_Cleaved_cV02_r00.data",
        "Tob14": "Tob14_004_vacuum_cV07_r01.data",
    }



    # === 1. Equilibration ===
    for charge_set in CHARGE_SETS:
        for tob, data_file in TOB_STRUCTURES.items():
            lammps_setup.prepare_simulation(
                folder_name=f"{tob}/{charge_set}/equilibration",
                ensembles=["em", "npt"],
                simulation_times=[0.1, 1.0],
                initial_systems=[f"{CHARGE_DIR}/{charge_set}/{tob}/{data_file}"],
                input_kwargs={},
                copies=0,
                off_set=0,
            )
            lammps_setup.submit_simulation()
            print(f"✅ Submitted equilibration for {tob} | {charge_set}")

    # === 2. Surface Energy (Bulk & Vacuum) ===
    for charge_set in CHARGE_SETS:
        for tob, data_file in SE_STRUCTURES_BULK.items():
            lammps_setup.prepare_simulation(
                folder_name=f"{tob}/{charge_set}/SE/bulk",
                ensembles=["nvt"],
                simulation_times=[1.0],
                initial_systems=[f"{CHARGE_DIR}/{charge_set}/{tob}/{data_file}"],
                input_kwargs={},
                copies=0,
                off_set=0,
            )
            lammps_setup.submit_simulation()
            print(f"✅ Submitted bulk SE for {tob} | {charge_set}")

        for tob, data_file in SE_STRUCTURES_VACUUM.items():
            lammps_setup.prepare_simulation(
                folder_name=f"{tob}/{charge_set}/SE/vacuum",
                ensembles=["nvt"],
                simulation_times=[1.0],
                initial_systems=[f"{CHARGE_DIR}/{charge_set}/{tob}/{data_file}"],
                input_kwargs={},
                copies=0,
                off_set=0,
            )
            lammps_setup.submit_simulation()
            print(f"✅ Submitted vacuum SE for {tob} | {charge_set}")

    # === 3. Deformation (after equil is done) ===
    while True:
        if equil_job_count() <= 0:
            print("✨ Submitting deformation jobs...")

            deformation_directions = ["xx", "yy", "zz", "xy", "xz", "yz", "undeformed"]
            deformation_rates = [-0.02, -0.01, 0.00, 0.01, 0.02]

            for charge_set in CHARGE_SETS:
                for tob in TOB_STRUCTURES:
                    try:
                        initial_systems = [
                            f"runs/charge_optimization/cvff/{tob}/{charge_set}/equilibration/temp_298.1_pres_1.0/copy_0/01_npt/npt.data"
                        ]
                        job_files = [[] for _ in lammps_setup.system_setup["temperature"]]

                        for direction in deformation_directions:
                            for rate in deformation_rates:
                                if (rate == 0.0 and direction != "undeformed") or (rate != 0.0 and direction == "undeformed"):
                                    continue
                                folder = f"{tob}/{charge_set}/deformation/{direction}/{rate}"
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
                        print(f"✅ Deformation jobs for {tob} | {charge_set}")
                    except Exception as e:
                        print(f"❌ Deformation error for {tob} | {charge_set}: {e}")
                        continue
            break
        else:
            print(f"⏳ Waiting: {equil_job_count()} equil jobs still running...")
            time.sleep(30)

    print("🎉 All charge optimization jobs submitted.")


    #3. Analysi
    while True:
        if (equil_job_count()+deform_job_count()) <= 0:

            TOB_STRUCTURES = ["Tob11", "Tob11H", "Tob14"]

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
            return df_full_new
        
        else:
            print(f"{deform_job_count()} deformation jobs still running. Waiting (for Analysis)...")
            time.sleep(30)

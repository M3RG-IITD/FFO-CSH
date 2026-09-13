import os
import shutil
import subprocess

# import time
# import numpy as np
# import pandas as pd
# import pickle
from mdsetup import MDSetup

def MD_sim_charge(Q_VALS, R_eps_theta_k, optimizer='None'):
    # 1. Data generation
    BASE_DIR = "../../data/structures/templates"
    TEMPLATE_CAR_MDF_DIR = os.path.join(BASE_DIR, "template_car_mdf/replaced")
    TOB_DIRS = ["Tob11_car_mdf", "Tob11H_car_mdf", "Tob14_car_mdf"]
    CHARGE_DIR = os.path.join(BASE_DIR, "../Charge_Opt/PCFF")

    TEMPLATE_LJ_FRC_PATH = os.path.join(BASE_DIR, "pcff_template.frc")
    BEST_LJ_FRC_PATH = os.path.join(BASE_DIR, "PCFF_best_LJ.frc")
    
    # sc_r, sc_eps, oc_r, oc_eps, ocx_r, ocx_eps, sos_ktheta, oso_ktheta, so_kr = [4.783, 0.260, 3.616, 0.039, 3.616, 0.039, 90, 90, 350]
    # === Find latest Charge_set index ===
    existing_dirs = [d for d in os.listdir(CHARGE_DIR) if d.startswith("Charge_set_")]
    existing_dirs.sort(key=lambda x: int(x.split('_')[2]) if len(x.split('_')) > 2 and x.split('_')[2].isdigit() else float('inf'))
    start_index = int(existing_dirs[-1].split('_')[-2]) + 1 if existing_dirs else 1
    end_index = start_index
    for idx, r_eps_theta_k in enumerate(R_eps_theta_k, start=start_index):
        sc_r, sc_eps, oc_r, oc_eps, ocx_r, ocx_eps, sos_ktheta, oso_ktheta, so_kr = r_eps_theta_k
        ca_r, ca_eps, cat_r, cat_eps = [3.550, 0.240, 3.550, 0.240]
        
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
        frc_content = frc_content.replace("{ca_r}", str(ca_r))
        frc_content = frc_content.replace("{ca_eps}", str(ca_eps))
        frc_content = frc_content.replace("{cat_r}", str(cat_r))
        frc_content = frc_content.replace("{cat_eps}", str(cat_eps))

        frc_content = frc_content.replace("{sc_r}", str(sc_r))
        frc_content = frc_content.replace("{sc_eps}", str(sc_eps))
        frc_content = frc_content.replace("{oc_r}", str(oc_r))
        frc_content = frc_content.replace("{oc_eps}", str(oc_eps))
        frc_content = frc_content.replace("{ocx_r}", str(ocx_r))
        frc_content = frc_content.replace("{ocx_eps}", str(ocx_eps))

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
        # existing_dirs = [d for d in os.listdir(CHARGE_DIR) if d.startswith("Charge_set_")]
        # existing_dirs.sort(key=lambda x: int(x.split('_')[2]) if len(x.split('_')) > 2 and x.split('_')[2].isdigit() else float('inf'))
        # start_index = int(existing_dirs[-1].split('_')[-2]) + 1 if existing_dirs else 1
        # end_index = start_index
        # for idx, X in enumerate(Q_VALS, start=start_index):
        # q_vals, idx  =  Q_VALS, start_index
        q_vals = Q_VALS
        # Replace charges in car/mdf
        def replace_charges(file_path,q_vals):
            with open(file_path, "r") as f:
                content = f.read()
            for k, v in q_vals.items():
                content = content.replace(k, f"{v:.5f}")
            return content

        end_index+= 1
        charge_dir = os.path.join(CHARGE_DIR, f"Charge_set_{idx}_{optimizer}")
        os.makedirs(charge_dir, exist_ok=True)

        print(f"\n🔧 Generating .data files (Charge_set_{idx}_{optimizer})")

        for tob_dir in TOB_DIRS:
            template_path = os.path.join(TEMPLATE_CAR_MDF_DIR, tob_dir)
            output_subdir = os.path.join(charge_dir, tob_dir.split("_")[0])
            os.makedirs(output_subdir, exist_ok=True)

            # Find all prefix names, Skip 'temp' files when building prefix list
            prefixes = sorted(set("_".join(f.split(".")[:-1]) for f in os.listdir(template_path) if f.endswith((".car", ".mdf")) and not f.startswith("temp_pcff")))

            for prefix in prefixes:

                car_path = os.path.join(template_path, prefix + ".car")
                mdf_path = os.path.join(template_path, prefix + ".mdf")

                car_content = replace_charges(car_path, q_vals)
                mdf_content = replace_charges(mdf_path, q_vals)

                temp_prefix = os.path.join(template_path, "temp_pcff")
                temp_car_path = temp_prefix + ".car"
                temp_mdf_path = temp_prefix + ".mdf"

                with open(temp_car_path, "w") as f:
                    f.write(car_content)
                with open(temp_mdf_path, "w") as f:
                    f.write(mdf_content)

                # Run msi2lmp
                cmd = ["msi2lmp", temp_prefix, "-class", "2", "-frc", BEST_LJ_FRC_PATH, "-ignore"]
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
        system_setup="config/setup_mechanical_charge_pcff2.yaml",
        simulation_default="config/defaults.yaml",
        simulation_ensemble="config/ensemble.yaml",
        simulation_sampling="config/sampling_mechanical.yaml",
        submission_command="qsub",
    )

    # CHARGE_SETS from start_index to end_index
    CHARGE_SETS = [f"Charge_set_{i}_{optimizer}" for i in range(start_index, end_index)]

    SE_STRUCTURES_BULK = {
        "Tob11_004": "Tob11_004_Bulk_cV05_r00.data",
        "Tob11H_004": "Tob11_Hamid_004_002_Bulk_cV02_r00.data",
        "Tob14_004": "Tob14_001_004_Bulk_cV07_r01.data",
        
        "Tob11_100": "Tob11_100_Bulk_cV05_r00.data",
        "Tob11H_100": "Tob11_Hamid_100_Bulk_cV02_r00.data",
        "Tob14_100": "Tob14_100_Bulk_cV07_r01.data",
                
        "Tob11H_001": "Tob11_Hamid_004_002_Bulk_cV02_r00.data",
        "Tob14_001": "Tob14_001_004_Bulk_cV07_r01.data",
    }

    SE_STRUCTURES_VACUUM = {
        "Tob11_004": "Tob11_004_vacuum_cV05_r01.data",
        "Tob11H_004": "Tob11_Hamid_004_Cleaved_cV02_r00.data",
        "Tob14_004": "Tob14_004_vacuum_cV07_r01.data",
        
        "Tob11_100": "Tob11_100_vacuum_cV05_r00.data",
        "Tob11H_100": "Tob11_Hamid_100_Cleaved_cV02_r00.data",
        "Tob14_100": "Tob14_100_vacuum_cV07_r01.data",
        
        "Tob11H_001": "Tob11_Hamid_002_Cleaved_cV02_r00.data",
        "Tob14_001": "Tob14_001_vacuum_cV07_r01.data",
    }

    # === 2. Surface Energy (Bulk & Vacuum) ===
    for charge_set in CHARGE_SETS:
        for tob, data_file in SE_STRUCTURES_BULK.items():
            tob, fol = tob.split('_')
            lammps_setup.prepare_simulation(
                folder_name=f"{tob}/{charge_set}/SE/{fol}/bulk",
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
            tob, fol = tob.split('_')
            lammps_setup.prepare_simulation(
                folder_name=f"{tob}/{charge_set}/SE/{fol}/vacuum",
                ensembles=["nvt"],
                simulation_times=[1.0],
                initial_systems=[f"{CHARGE_DIR}/{charge_set}/{tob}/{data_file}"],
                input_kwargs={},
                copies=0,
                off_set=0,
            )
            lammps_setup.submit_simulation()
            print(f"✅ Submitted vacuum SE for {tob} | {charge_set}")
    print("🎉 All charge optimization jobs submitted.")

_q_vals = {
    '{q_cat}': 1.7, # Ca(dry)
    '{q_casl}': 1.7, # Ca(wet)
    '{q_sc2_3}': 1.0, # Si(dry / wet sides)
    '{q_oc12}': -0.5, # Obridge
    '{q_oc13}': -1.1, # Osiloxide (dry)
    '{q_oc22}': -1.1, # Osiloxide (wet)
    '{q_ocx}': -0.5, # Ointerlayer bridge
    '{q_oc14}': -0.67, # Osilanol
    '{q_hoy}': 0.42 # Hsilanol
}

_r_eps_theta_k = [[4.77259229, 0.294096718, 3.569694063, 0.112071613, 3.569694063, 0.112071613, 100.0, 100.0, 350.0]]
MD_sim_charge(_q_vals, _r_eps_theta_k, optimizer='pcff2')
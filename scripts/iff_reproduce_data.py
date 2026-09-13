import numpy as np

import os
import subprocess
import shutil

# Define constants
BASE_DIR = "../../data/structures/templates"
TOB_DIRS = ["Tob9_car_mdf", "Tob11_car_mdf", "Tob11H_car_mdf", "Tob14_car_mdf"]

# ff_name = 'PCFF'
# ff_path = "../../data/structures/templates/pcff_interface_v1_5_TobermoriteV14.frc"

ff_name = 'CVFF'
ff_path = "../../data/structures/templates/cvff_interface_v1_5_Tobermorite_v08.frc"

param_dir = os.path.join(BASE_DIR, f"IFF_reproduce/{ff_name}")
os.makedirs(param_dir, exist_ok=True)


for tob_dir in TOB_DIRS:
    class_type = "2" if ff_name == "PCFF" else "1"

    dir_path = os.path.join(BASE_DIR, tob_dir)
    output_folder = os.path.join(param_dir, tob_dir.split("_")[0])
    os.makedirs(output_folder, exist_ok=True)

    prefixes = sorted(set("_".join(f.split(".")[:-1]) for f in os.listdir(dir_path) if f.endswith((".car", ".mdf"))))

    for prefix in prefixes:
        output_prefix = os.path.join(dir_path, prefix)
        cmd = ["msi2lmp", output_prefix, "-class", class_type, "-frc", ff_path, "-ignore"]

        print(f"Running: {' '.join(cmd)} with {ff_name}")
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            print(f"✅ Successfully generated {prefix}.data for IFF_reproduce_{ff_name}")
            try:
                shutil.move(f"{output_prefix}.data", output_folder)
            except Exception as e:
                print(f"⚠️ Unexpected error: {e}")
        else:
            print(f"❌ Error in {prefix}: {result.stderr}")
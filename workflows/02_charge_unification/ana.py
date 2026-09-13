import os
from mdsetup import MDSetup

os.chdir('')
lammps_setup = MDSetup(
    system_setup="config/setup_mechanical_charge_pcff.yaml",
    simulation_default="config/defaults.yaml",
    simulation_ensemble="config/ensemble.yaml",
    simulation_sampling="config/sampling_mechanical.yaml",
    submission_command="qsub",
)



# CHARGE_SETS from start_index to end_index
CHARGE_SETS = [f"Charge_set_{i}_pcff" for i in range(20, 27)]

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


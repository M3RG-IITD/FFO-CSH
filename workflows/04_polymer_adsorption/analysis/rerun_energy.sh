#!/bin/bash
# ============================================================
#  LAMMPS RERUN: Interaction Energy Decomposition
#  
#  This reprocesses existing trajectories to compute
#  polymer-CSH electrostatic and vdW interaction energies.
#  
#  Takes MINUTES, not hours — no new MD needed.
#
#  Usage: 
#    cd S1_directory
#    bash ../../rerun_energy.sh
# ============================================================

cat > rerun_energy.in << 'LAMMPS_EOF'
# Rerun trajectory for interaction energy decomposition

units           real
dimension       3
boundary        p p p
atom_style      full
atom_modify     map array sort 1000 0.0

# Read the post-equilibration structure
read_data       S1_1_1_15_post_nvt.data

# Include force field parameters
include         ../../S1_1_1_15.params

# Define groups
group           csh type 16 17 18 19 20 21 22 23 24 25
group           polymer type 1 2 3 4 5 6 7 8 9 10 11 12 13
group           water type 14 15

# Compute pairwise interaction energies
compute         pe_poly_csh polymer group/group csh
compute         pe_poly_water polymer group/group water
compute         pe_csh_water csh group/group water

neighbor        2.0 bin
neigh_modify    every 1 delay 0 check yes

thermo          1
thermo_style    custom step c_pe_poly_csh c_pe_poly_water c_pe_csh_water

# Write to file for easy parsing
fix             print_energy all print 1 &
    "$(step) $(c_pe_poly_csh) $(c_pe_poly_water) $(c_pe_csh_water)" &
    file interaction_energies.dat screen no title &
    "# Step  E_poly_csh  E_poly_water  E_csh_water"

# Rerun the trajectory
rerun S1_1_1_15_dump.lammpstrj dump x y z
LAMMPS_EOF

echo "Running LAMMPS rerun for interaction energy decomposition..."
echo "This should take only a few minutes."

# Adjust the LAMMPS command to match your setup
mpirun -np 4 lmp -in rerun_energy.in > rerun_energy.log 2>&1

echo "Done! Results in interaction_energies.dat"
echo ""
echo "Parse with:"
echo "  import numpy as np"
echo "  data = np.loadtxt('interaction_energies.dat', skiprows=1)"
echo "  E_poly_csh = data[:, 1]    # polymer-CSH interaction"
echo "  E_poly_water = data[:, 2]  # polymer-water interaction"
echo "  E_csh_water = data[:, 3]   # CSH-water interaction"

#!/bin/bash
#PBS -P m3rg.spons
#PBS -l select=1:ncpus=1:mpiprocs=1:centos=haswell:mem=3000mb
#PBS -l walltime=01:00:00
#PBS -N build_system
#PBS -o {{folder}}/build_log.o 
#PBS -e {{folder}}/build_log.e 


module purge
module load apps/lammps/intel/5Jun19 #module load mpi/openmpi/3.1-gnu-9.2

# Define the main working path 
WORKING_PATH={{folder}}
cd $WORKING_PATH

echo "This is the working path: $WORKING_PATH"

mpirun --bind-to core --map-by core -report-bindings lmp_mpi_cpu -i {{build_input_file}}

# End
echo "Ending. Job completed."

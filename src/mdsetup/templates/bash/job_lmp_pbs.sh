#!/bin/bash
#PBS -P m3rg.spons
#PBS -l select=1:ncpus=28:mpiprocs=28:centos=haswell:mem=3000mb=1
#PBS -l walltime=20:00:00
#PBS -N {{job_name}}
#PBS -o {{log_path}}.o 
#PBS -e {{log_path}}.e 


module purge
module load apps/lammps/intel/5Jun19 #module load mpi/openmpi/3.1-gnu-9.2

# Define the main working path 
WORKING_PATH={{working_path}}
cd $WORKING_PATH

echo "This is the working path: $WORKING_PATH"

# Define the names of each simulation step taken. The folder as well as the output files will be named like this
{% for ensemble_name, ensemble in ensembles.items() %}

################################# 
#       {{ensemble_name}}       #
#################################
echo ""
echo "Starting ensemble: {{ensemble_name}}"
echo ""

mkdir -p {{ensemble_name}}
cd {{ensemble_name}}

mpirun --bind-to core --map-by core -report-bindings lmp_mpi_cpu -i {{ensemble.mdrun}}

echo "Completed ensemble: {{ensemble_name}}"

cd ../
sleep 10

{% endfor %}


# End
echo "Ending. Job completed."

# HPC Setup Guide

The full optimization pipeline (Workflows 1-3) requires a compute cluster with
LAMMPS and a PBS or SLURM scheduler. This guide provides generic templates that
can be adapted to any cluster.

## Prerequisites

- LAMMPS built with the `CLASS2` and `KSPACE` packages (required for PCFF/CVFF)
- Python >= 3.9 with the packages listed in `environment.yml`
- PBS Pro or SLURM scheduler

## Environment Setup

```bash
# Create the conda environment
conda env create -f environment.yml
conda activate csh-iff

# Install the local MDSetup package
pip install -e src/mdsetup/

# Verify LAMMPS is available
which lmp  # or lmp_mpi, lmp_serial - depends on your cluster module system
```

On clusters with module systems, you may need to load LAMMPS separately:

```bash
module load lammps  # exact name varies by cluster
```

## PBS Template

```bash
#!/bin/bash
#PBS -N csh_md
#PBS -l select=1:ncpus=16:mpiprocs=16
#PBS -l walltime=04:00:00
#PBS -q standard
#PBS -j oe

cd $PBS_O_WORKDIR

# Activate environment
source activate csh-iff

# Run LAMMPS
mpirun -np 16 lmp -in input.lammps
```

## SLURM Template

```bash
#!/bin/bash
#SBATCH --job-name=csh_md
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --time=04:00:00
#SBATCH --partition=standard

cd $SLURM_SUBMIT_DIR

# Activate environment
source activate csh-iff

# Run LAMMPS
srun lmp -in input.lammps
```

## Job Submission in the Workflows

The `run_MD_sim*.py` scripts in Workflows 1-3 use PBS `qsub` by default and
monitor job completion via `qstat -u $USER`. To adapt for SLURM:

1. Modify the submission command from `qsub` to `sbatch`
2. Replace `qstat -u $USER` polling with `squeue -u $USER`
3. Update job script headers from `#PBS` to `#SBATCH` directives

The MDSetup library (`src/mdsetup/`) handles job template rendering via Jinja2.
LAMMPS input templates are in `src/mdsetup/templates/`.

## Typical Resource Requirements

| Workflow | Jobs per iteration | Time per job | Total wall time |
|----------|-------------------|--------------|-----------------|
| 01: Tobermorite optimization | ~50-100 (per AL round x 10-15 rounds) | 1-4 hours | ~2 weeks |
| 02: Charge unification | ~20-50 per charge set | 1-4 hours | ~1 week |
| 03: C-S-H transfer | ~50-100 per Ca/Si ratio | 2-6 hours | ~1 week |
| 04: Polymer adsorption | 3 x 3 replicas | 12-24 hours | ~3 days |

These are rough estimates; actual times depend on system size and cluster throughput.

## Troubleshooting

**LAMMPS "Unknown pair_style" error**: Ensure LAMMPS was built with the `CLASS2`
package. Rebuild with `make yes-CLASS2` if needed.

**Job hangs at qstat polling**: The `run_MD_sim*.py` scripts poll `qstat` in a
loop. If your cluster qstat output format differs, you may need to adjust the
grep patterns in the polling loop.

**Force field not found**: Verify that the `.frc` file paths in the YAML configs
point to the correct location under `forcefields/`. Paths should be relative to
the repository root.

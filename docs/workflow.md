# Workflow Guide

This document maps the four computational workflows to the manuscript sections
and explains how to configure and run each stage.

## Overview

```
Workflow 1                    Workflow 2              Workflow 3           Workflow 4
Tobermorite Optimization  ->  Charge Unification  ->  C-S-H Transfer  ->  Polymer Adsorption
(LJ parameters)              (partial charges)       (validation)        (application)
```

Each workflow directory is self-contained: it has its own entry-point scripts,
configuration files, and (where applicable) Jupyter notebooks for analysis.

---

## Workflow 1: Tobermorite Optimization

**Directory**: `workflows/01_tobermorite_optimization/`

**Purpose**: Optimize Lennard-Jones epsilon and sigma parameters for Ca-O(water) and
Si-O(water) interactions across four tobermorite polymorphs (Tob11,
Tob11H, Tob14) using an active-learning loop.

### Entry Points

| Script | Optimizer | Description |
|--------|-----------|-------------|
| `main.py` | NSGA-II | Original AL loop (archived — see `archive/`) |
| `main_nsga2.py` | NSGA-II | Standalone NSGA-II optimization |
| `main_nsga3a.py` | NSGA-III (variant a) | Alternative reference-point optimizer |
| `main_nsga3b.py` | NSGA-III (variant b) | Alternative with different reference points |
| `main_all_9_opt.py` | NSGA-II | All-9-property variant |
| `archive/main_bo.py` | Bayesian Optimization | Exploratory - not used in final results |
| `archive/main_cma.py` | CMA-ES | Exploratory - not used in final results |

### Active-Learning Cycle

1. **Sample** LJ parameter sets (Grid/LHS or NN-guided)
2. **Run MD** via `run_MD_sim_for_K.py` / `run_md_sim.py` - submits LAMMPS jobs
   to the PBS scheduler for each parameter set x polymorph x property
3. **Extract** density, bulk modulus, and surface energy from LAMMPS output
   (`ana_pcff_all.py`, `ana_pcff_den.py`)
4. **Train** neural-network surrogate models (`ML_train.py`)
5. **Optimize** on the surrogate using NSGA-II/III (`MP_ML_active_learning.py`)
6. **Select** next batch of LJ parameter sets from the Pareto front
7. Repeat from step 2

### Configuration

YAML configuration files in `config/` control polymorph selection, LJ parameter
bounds, number of active-learning iterations, and MD simulation settings. Key
parameters:

- `n_iterations`: Number of active-learning rounds
- `batch_size`: LJ parameter sets per round
- `objectives`: Properties to optimize (density, bulk_modulus, surface_energy)
- `polymorph`: Tobermorite variant (Tob11, Tob11H, Tob14)

### Outputs

- `data/training/models/NSGA2/` - Saved NN model weights per iteration
- `data/training/*.csv` - Training data accumulated across AL rounds
- `data/training/optimal_parameter_sets_7.csv` - Final Pareto-optimal LJ sets

### Analysis Notebooks

Located in `notebooks/`:
- `main.ipynb` - Full pipeline walkthrough
- `main_all_9_opt.ipynb` - All-9-property analysis
- `MP_ML_training_new.ipynb` - Model training diagnostics
- `AL_analysis_17June.ipynb` - Active-learning convergence analysis
- `ana.ipynb`, `ana_cvff1.ipynb` - Paper figure generation

---

## Workflow 2: Charge Unification

**Directory**: `workflows/02_charge_unification/`

**Purpose**: Optimize partial charges so a single charge set works across all
tobermorite polymorphs for both CVFF and PCFF force fields.

### Scripts

| Script | Force Field | Description |
|--------|-------------|-------------|
| `run_MD_sim_for_K_cvff.py` | CVFF | MD runner for CVFF charge optimization |
| `run_MD_sim_for_K_cvff_SE.py` | CVFF | Surface energy variant |
| `run_MD_sim_for_K_pcff.py` | PCFF (original) | MD runner for PCFF |
| `run_MD_sim_for_K_pcff1.py` | PCFF (variant 1) | Alternative PCFF parameterization |
| `run_MD_sim_for_K_pcff2.py` | PCFF (variant 2) | Alternative PCFF parameterization |
| `pinn/` | Both | PINN-based charge optimization |

### Outputs

Optimized charge values feed into Workflows 3 and 4. The charge parameters
(`q_vals_den`, `q_vals_se`, `q_vals_se14`) must be transferred manually to
`workflows/03_csh_transfer/main_csh.py`.

---

## Workflow 3: C-S-H Transfer Validation

**Directory**: `workflows/03_csh_transfer/`

**Purpose**: Validate the optimized IFF on disordered C-S-H structures at
varying Ca/Si ratios, without any re-fitting.

### Entry Points

- `main_csh.py` - Main driver (requires charge parameters from Workflow 2)
- `run_MD_sim_csh.py` - MD simulation submission for C-S-H structures

### Configuration

- `config/cvff/` - CVFF-specific templates and settings
- `config/pcff/` - PCFF-specific templates and settings
- `structures/` - Pre-generated C-S-H structures from pyCSH

### Pre-Computed Results

Three summary CSVs extracted from the full simulation outputs:

| File | Rows | Contents |
|------|------|----------|
| `summary_density.csv` | 9 | Density by Ca/Si ratio |
| `summary_bulk_modulus.csv` | 29 | Bulk modulus by Ca/Si and pressure |
| `summary_deformation.csv` | 725 | Full elastic tensor components |

### Notebooks

- `run_MD.ipynb` - Interactive walkthrough of the CVFF C-S-H validation
- `run_MD_pcff.ipynb` - Same for PCFF

---

## Workflow 4: Polymer Adsorption

**Directory**: `workflows/04_polymer_adsorption/`

**Purpose**: Simulate PCE superplasticizer adsorption on C-S-H surfaces and
compute adsorption energies.

### Structure

- `setup/` - LAMMPS input generation for polymer-on-surface systems
- `production/` - Representative production run inputs (1 replica per C:E ratio)
- `analysis/` - Post-processing scripts

### PCE Configurations

Three chain-to-ester (C:E) ratios are studied:
- 1:1 (`pce_11/`)
- 2:1 (`pce_21/`)
- 3:1 (`pce_31/`)

### Analysis

`analysis/analyze.py` reads LAMMPS energy outputs and computes per-component
adsorption energies. Pre-computed results are in
`data/reference_results/adsorption_energy_*.csv`.

---

## Manuscript Figure Mapping

| Figure | Data Source | Notebook / Script |
|--------|-----------|-------------------|
| LJ parameter space / Pareto fronts | `data/training/*.csv` | `workflows/01_.../notebooks/main.ipynb` |
| NN surrogate accuracy | `data/training/models/` | `workflows/01_.../notebooks/MP_ML_training_new.ipynb` |
| Property predictions vs experiment | `data/reference_results/*.csv` | `workflows/01_.../notebooks/ana.ipynb` |
| C-S-H density vs Ca/Si | `workflows/03_.../summary_density.csv` | `workflows/03_.../run_MD.ipynb` |
| Elastic properties | `workflows/03_.../summary_deformation.csv` | `workflows/03_.../run_MD.ipynb` |
| Adsorption energies | `data/reference_results/adsorption_energy_*.csv` | `workflows/04_.../analysis/analyze.py` |

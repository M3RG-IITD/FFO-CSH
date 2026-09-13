# Archive — Historical / Exploratory Scripts

These scripts were used during development and exploration but are **not part
of the primary reproducible workflow**. They are preserved for reference.

| Script | Description |
|--------|-------------|
| `main.py` | Original AL loop combining BO + CMA-ES + NSGA-II + NSGA-III |
| `main_bo.py` | Bayesian Optimization entry point (exploratory) |
| `main_cma.py` | CMA-ES entry point (exploratory) |
| `main_all_9_opt.py` | All-9-property optimization variant |
| `MP_ML_active_learning.py` | Earlier active-learning driver |
| `MP_pcff_analysis.py` | PCFF property analysis (standalone) |
| `MP_pcff_workflow.py` | PCFF workflow driver (standalone) |
| `MechanicalProperties_pcff.py` | Mechanical property extraction (standalone) |
| `MechanicalProperties_pcff_iff_reproduce.py` | IFF reproduction analysis |
| `analysis_mean_std.py` | Mean/std aggregation of training data |
| `run_analysis_only.py` | Post-hoc analysis without re-running MD |

**Note**: These scripts reference the original flat directory layout
(`ML_Pipeline/`, `input_tob_all/`, `output_tob_all/`) and will not run
from this restructured repository without modification.

The supported entry points are `main_nsga2.py`, `main_nsga3a.py`, and
`main_nsga3b.py` in the parent directory.

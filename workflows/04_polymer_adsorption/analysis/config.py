"""
Configuration for CSH-PCE adsorption analysis pipeline.

Edit this file to point to your simulation directories.
Everything else is automatic.
"""
from pathlib import Path

# ============================================================
#  SYSTEM DEFINITIONS
# ============================================================
# Each system is defined by its C:E ratio name and file paths.
# The pipeline expects:
#   - S1 (close): PCE + water + CSH
#   - S2 (sol):   PCE + water
#   - S3 (surf):  CSH + water (shared across all C:E ratios)


# BASE path: update to point to your local simulation output directory.
# For reproducing Figure 5 from precomputed CSVs, this path is not needed —
# the analysis/results/ CSVs are sufficient.
# For full reproduction from trajectories, set this to your simulation root.
BASE = Path("../production")


# BASE = Path("/path/to/your/simulations")  # <-- EDIT THIS
RUN = "0_run13_pcff_merged"


# SYSTEMS = {
#     "1:1": {
#         "S1_data": BASE / RUN / "1_1-12E/S1/S1_1_1_15_Relaxed.data",
#         "S1_traj": BASE / RUN / "1_1-12E/S1/S1_1_1_15_dump.lammpstrj",
#         "S1_log":  BASE / RUN / "1_1-12E/S1/log.lammps",
#         "S2_data": BASE / RUN / "1_1-12E/S2/S2_1_1_15_Relaxed.data",
#         "S2_traj": BASE / RUN / "1_1-12E/S2/S2_dump_1_1_12E.lammpstrj",
#         "S2_log":  BASE / RUN / "1_1-12E/S2/log.lammps",
#         "n_side_chains": 12,
#         "CE_ratio": "1:1",
#     },
#     "2:1": {
#         "S1_data": BASE / RUN / "2_1-8E/S1/S1_2_1_15_Relaxed.data",
#         "S1_traj": BASE / RUN / "2_1-8E/S1/S1_2_1_15_dump.lammpstrj",
#         "S1_log":  BASE / RUN / "2_1-8E/S1/log.lammps",
#         "S2_data": BASE / RUN / "2_1-8E/S2/S2_2_1_15_Relaxed.data",
#         "S2_traj": BASE / RUN / "2_1-8E/S2/S2_dump_2_1_8E.lammpstrj",
#         "S2_log":  BASE / RUN / "2_1-8E/S2/log.lammps",
#         "n_side_chains": 8,
#         "CE_ratio": "2:1",
#     },
#     "3:1": {
#         "S1_data": BASE / RUN / "3_1-6E/S1/S1_3_1_15_Relaxed.data",
#         "S1_traj": BASE / RUN / "3_1-6E/S1/S1_3_1_15_dump.lammpstrj",
#         "S1_log":  BASE / RUN / "3_1-6E/S1/log.lammps",
#         "S2_data": BASE / RUN / "3_1-6E/S2/S2_3_1_15_Relaxed.data",
#         "S2_traj": BASE / RUN / "3_1-6E/S2/S2_dump_3_1_6E.lammpstrj",
#         "S2_log":  BASE / RUN / "3_1-6E/S2/log.lammps",
#         "n_side_chains": 6,
#         "CE_ratio": "3:1",
#     },
# }

# # Shared S3 system (CSH + water)
# S3_CONFIG = {
#     "data": BASE / RUN / "S3/S3_csh_water.data",
#     "traj": BASE / RUN / "S3/3_dump_csh_water.lammpstrj",
#     "log":  BASE / RUN / "S3/log.lammps",
# }



SYSTEMS = {
    "1:1": {
        "S1_data": BASE / RUN / "1_1-12E/S1/S1_1_1_15_Relaxed.data",
        "S1_traj": BASE / RUN / "1_1-12E/S1/S1_1_1_15_dump_merged.lammpstrj",
        "S1_log":  BASE / RUN / "1_1-12E/S1/log_merged.lammps",
        "S2_data": BASE / RUN / "1_1-12E/S2/S2_1_1_15_Relaxed.data",
        "S2_traj": BASE / RUN / "1_1-12E/S2/S2_dump_1_1_12E_merged.lammpstrj",
        "S2_log":  BASE / RUN / "1_1-12E/S2/log_merged.lammps",
        "n_side_chains": 12,
        "CE_ratio": "1:1",
    },
    "2:1": {
        "S1_data": BASE / RUN / "2_1-8E/S1/S1_2_1_15_Relaxed.data",
        "S1_traj": BASE / RUN / "2_1-8E/S1/S1_2_1_15_dump_merged.lammpstrj",
        "S1_log":  BASE / RUN / "2_1-8E/S1/log_merged.lammps",
        "S2_data": BASE / RUN / "2_1-8E/S2/S2_2_1_15_Relaxed.data",
        "S2_traj": BASE / RUN / "2_1-8E/S2/S2_dump_2_1_8E_merged.lammpstrj",
        "S2_log":  BASE / RUN / "2_1-8E/S2/log_merged.lammps",
        "n_side_chains": 8,
        "CE_ratio": "2:1",
    },
    "3:1": {
        "S1_data": BASE / RUN / "3_1-6E/S1/S1_3_1_15_Relaxed.data",
        "S1_traj": BASE / RUN / "3_1-6E/S1/S1_3_1_15_dump_merged.lammpstrj",
        "S1_log":  BASE / RUN / "3_1-6E/S1/log_merged.lammps",
        "S2_data": BASE / RUN / "3_1-6E/S2/S2_3_1_15_Relaxed.data",
        "S2_traj": BASE / RUN / "3_1-6E/S2/S2_dump_3_1_6E_merged.lammpstrj",
        "S2_log":  BASE / RUN / "3_1-6E/S2/log_merged.lammps",
        "n_side_chains": 6,
        "CE_ratio": "3:1",
    },
}

# Shared S3 system (CSH + water)
S3_CONFIG = {
    "data": BASE / RUN / "S3/S3_csh_water.data",
    "traj": BASE / RUN / "S3/3_dump_csh_water_merged.lammpstrj",
    "log":  BASE / RUN / "S3/log_merged.lammps",
}


# ============================================================
#  ATOM TYPE DEFINITIONS (PCFF type ordering)
# ============================================================
# Polymer types: 1-13
# Water types: 14-15
# CSH types: 16-25

POLYMER_TYPES = list(range(1, 14))   # c_1, c, c2, hc, c3, c-, o-, o_1, ca++, ce1, he1, o_2, oe1
WATER_TYPES = [14, 15]               # Hw, Ow
CSH_TYPES = list(range(16, 26))      # casl, sc2, oc13, oc12, o*, h*, oc14, hoy, Oh, Ho

# Specific functional group types
COO_OXYGEN_TYPES = [7]               # o- (carboxylate oxygen)
CA_SURFACE_TYPE = 16                 # casl (CSH surface calcium)
OW_TYPE = 15                         # Ow (water oxygen)

# Backbone types (non-H, non-sidechain)
BACKBONE_TYPES = [1, 2, 3, 5, 6]     # c_1, c, c2, c3, c-

# ============================================================
#  ANALYSIS PARAMETERS
# ============================================================
TIMESTEP_FS = 1.0                    # MD timestep in fs
DUMP_EVERY = 10000                   # frames saved every N steps
THERMO_EVERY = 1000                  # thermo output every N steps

# Production window: skip equilibration (anneal + cool + equil)
# Total equil = 2ns anneal + 1ns cool + 4ns equil = 7ns = 7,000,000 steps
EQUIL_STEPS = 9_000_000
# EQUIL_NS = 7.0                       # used by get_equil_frames()

# EQUIL_FRAMES is a FALLBACK only. Prefer utils.get_equil_frames(universe)
# which auto-detects from the trajectory timestep and ensures enough
# production frames remain. The old hardcoded 700 assumed DUMP_EVERY=10000,
# but if the trajectory has fewer total frames, this leaves ≤2 for analysis.
EQUIL_FRAMES = EQUIL_STEPS // DUMP_EVERY  # 700 — only used if auto-detect fails

EQUIL_FRAMES_BULK = 400
# For analysis, use last N ns of production
# PRODUCTION_LAST_NS = 2              # analyze last 20 ns of production

# Contact analysis
CONTACT_CUTOFF = 3.5                 # Å, for Ca-COO contacts
RDF_CUTOFF = 10.0                    # Å, max distance for RDF
RDF_NBINS = 200                      # number of bins for RDF

# Density profile
DENSITY_NBINS = 200                  # bins along z for density profile

# Surface reference
SURFACE_Z_BUFFER = 5.0               # Å above CSH top for surface definition

# ============================================================
#  OUTPUT
# ============================================================
OUTPUT_DIR = Path("results")
FIGURE_DIR = Path("figures")
CE_ORDER = ['1:1', '2:1', '3:1']
# Upstream Dependencies

This repository includes modified forks of two open-source packages. Both are
bundled under `src/` to ensure reproducibility with the exact versions used in
the manuscript.

## MDSetup (`src/mdsetup/`)

- **Upstream**: [github.com/samirdarouich/MDSetup](https://github.com/samirdarouich/MDSetup)
- **Author**: Samir Darouich
- **License**: See `src/mdsetup/LICENSE`

**Modifications for this project**:

1. Added LAMMPS template files for tobermorite bulk, surface energy, and
   deformation simulations (`src/mdsetup/templates/`)
2. Extended `submission.py` to support PBS job arrays and wait-for-completion
   polling via `qstat`
3. Added `stiffness.py` and `voigt_reuss_hill.py` for elastic tensor
   extraction and Voigt-Reuss-Hill averaging
4. Modified force field reader to handle CVFF/PCFF interface force field
   parameter mixing
5. Added analysis utilities for extracting density, bulk modulus, and surface
   energy from LAMMPS thermo output

## pyCSH (`src/pycsh/`)

- **Upstream**: [github.com/jlopez141/pyCSH](https://github.com/jlopez141/pyCSH)
- **Author**: Jorge Lopez
- **License**: See `src/pycsh/LICENSE`

**Modifications for this project**:

1. Renamed building blocks directory from `Blocks/` to `blocks/` (case
   normalization for cross-platform compatibility)
2. Used the renamed block set from `Blocks_Renamed/` for consistent naming
3. No changes to core generation logic (`main_brick.py`, `mod_construct_*.py`)

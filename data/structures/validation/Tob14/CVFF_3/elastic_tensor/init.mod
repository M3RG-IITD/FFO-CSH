# NOTE: This script can be modified for different atomic structures, 
# units, etc. See in.elastic for more info.
#

# Define the finite deformation size. Try several values of this
# variable to verify that results do not depend on it.
variable up equal 2e-2
 
# metal units, elastic constants in GPa
units		real
# variable cfac equal 1.0e-4
variable cfac equal 1.01325e-4
variable cunits string GPa

# Define MD parameters
variable nevery equal 100                  # sampling interval
variable nrepeat equal 100                 # number of samples
variable nfreq equal ${nevery}*${nrepeat} # length of one average
variable nthermo equal ${nfreq}           # interval for thermo output
variable nequil equal 100*${nthermo}       # length of equilibration run
variable nrun equal 40*${nthermo}          # length of equilibrated run

variable temp equal 298.15                   # temperature of initial sample
variable timestep equal 0.5            # timestep
variable mass1 equal 28.06                # mass
variable adiabatic equal 0                # adiabatic (1) or isothermal (2)
variable tdamp equal 50                 # time constant for thermostat
variable seed equal 666                # seed for thermostat

# generate the box and atom positions using a diamond lattice
#variable a equal 5.431

boundary	p p p
dimension 3
atom_style full
newton  on

kspace_style ewald 1e-6
pair_style		lj/cut/coul/long 12.0

bond_style		harmonic
angle_style		harmonic
dihedral_style	harmonic
improper_style	cvff
box tilt large

read_data after_sim.data
# read_data T14_CVFF.data
# read_data sys.restart

# velocity	all create ${temp} 4928459 rot yes dist gaussian



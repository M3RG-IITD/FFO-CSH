from mdsetup import MDSetup

import os
os.chdir('')

# ## Mechanical properties
# 
# This notebook uses MDSetup to setup simulations to compute mechanical properties using finite differences

lammps_setup = MDSetup(
    system_setup="input_tob_all/setup_mechanical_pcff.yaml",
    simulation_default="input_tob_all/defaults.yaml",
    simulation_ensemble="input_tob_all/ensemble.yaml",
    simulation_sampling="input_tob_all/sampling_mechanical.yaml",
    submission_command="qsub",
)

# ## Setting up equilibration
# 
# In this section the inital system is equilibrated at desired temperature and pressure.
# 
# 1) Setup simulation

# Define the simulation folder
simulation_folder = "Tob14/equilibration"

# Define the ensembles that should be simulated (definition what each ensemble means is provided in yaml file)
ensembles = ["em", "npt"]

# Define the simulation time per ensemble in nano seconds (for em the number of iterations is provided in the ensemble yaml)
simulation_times = [0.1, 1.0]

# Define initial data file (for each pressure & temperature state one)
initial_systems = ['input_tob_all/LJ_set_1/Tob14/tob14_221.data']

# Provide kwargs that should be passed into the input template directly
input_kwargs = {}

# Define number of copies
copies = 0

# Define the starting number for the first ensemble ( 0{off_set}_ensemble )
off_set = 0

lammps_setup.prepare_simulation(
    folder_name=simulation_folder,
    ensembles=ensembles,
    simulation_times=simulation_times,
    initial_systems=initial_systems,
    input_kwargs=input_kwargs,
    copies=copies,
    off_set=off_set,
)


# 2) Submit jobs to cluster


# Submit the simulations
lammps_setup.submit_simulation()


# ## Tob 11 Hamid (Mechanical properties)


# ### Setting up equilibration
# 
# In this section the inital system is equilibrated at desired temperature and pressure.
# 
# 1) Setup simulation
# 


# Define the simulation folder
simulation_folder = "Tob11H/equilibration"

# Define the ensembles that should be simulated (definition what each ensemble means is provided in yaml file)
ensembles = ["em", "npt"]

# Define the simulation time per ensemble in nano seconds (for em the number of iterations is provided in the ensemble yaml)
# simulation_times = [0.1, 1.0]
simulation_times = [0.01, 0.1]

# Define initial data file (for each pressure & temperature state one)
initial_systems = ['input_tob_all/LJ_set_1/Tob11H/tob11H_221.data']

# Provide kwargs that should be passed into the input template directly
input_kwargs = {}

# Define number of copies
copies = 0

# Define the starting number for the first ensemble ( 0{off_set}_ensemble )
off_set = 0

lammps_setup.prepare_simulation(
    folder_name=simulation_folder,
    ensembles=ensembles,
    simulation_times=simulation_times,
    initial_systems=initial_systems,
    input_kwargs=input_kwargs,
    copies=copies,
    off_set=off_set,
)


# 2) Submit jobs to cluster


# Submit the simulations
lammps_setup.submit_simulation()




# Define the analysis folder
analysis_folder = "Tob14/equilibration"

# Define analysis ensemble
ensemble = "01_npt"

# Properties to extract
properties = ["a", "b", "c", "alpha", "beta", "gamma"]

# Suffix of output file
output_suffix = "lattice"

# Percentage to discard from beginning of the simulation
time_fraction = 0.4

# Extract properties from LAMMPS and analyse them
lammps_setup.analysis_extract_properties(
    analysis_folder=analysis_folder,
    ensemble=ensemble,
    extracted_properties=properties,
    output_suffix=output_suffix,
    time_fraction=time_fraction,
)

# Properties to extract
properties = ["density", "volume"]

# Suffix of output file
output_suffix = "density"

# Extract properties from LAMMPS and analyse them
lammps_setup.analysis_extract_properties(
    analysis_folder=analysis_folder,
    ensemble=ensemble,
    extracted_properties=properties,
    output_suffix=output_suffix,
    time_fraction=time_fraction,
)


# Properties to extract
properties = ["potential energy"]

# Suffix of output file
output_suffix = "energy"

# Extract properties from LAMMPS and analyse them
lammps_setup.analysis_extract_properties(
    analysis_folder=analysis_folder,
    ensemble=ensemble,
    extracted_properties=properties,
    output_suffix=output_suffix,
    time_fraction=time_fraction,
)
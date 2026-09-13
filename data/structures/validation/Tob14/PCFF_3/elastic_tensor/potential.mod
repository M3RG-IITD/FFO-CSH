# NOTE: This script can be modified for different pair styles 
# See in.elastic for more info.

#reset_timestep 0

# Setup neighbor style
# neighbor 1.0 nsq
neighbor		2.0 bin
# neigh_modify   delay 10 every 10 check yes
neigh_modify once no every 1 delay 0 check yes
special_bonds	lj/coul 0.0 0.0 1.0
kspace_style ewald 1e-6
change_box      all triclinic 
# Setup output

fix avp all ave/time  ${nevery} ${nrepeat} ${nfreq} c_thermo_press mode vector
thermo		${nthermo}
thermo_style custom step temp pe press f_avp[1] f_avp[2] f_avp[3] f_avp[4] f_avp[5] f_avp[6]
thermo_modify norm no

# Setup MD
timestep ${timestep}
fix 4 all nvt temp ${temp} ${temp} ${tdamp}
if "${thermostat} == 1" then &
   "fix 5 all langevin ${temp} ${temp} ${tdamp} ${seed}"

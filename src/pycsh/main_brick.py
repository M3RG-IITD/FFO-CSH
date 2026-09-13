# Params defination
seed = 23137
shape = (4,4,2)   # Minimum (1,1,1)

# Ca_Si_ratio = 1.2
# W_Si_ratio  = 1.6
# prefix = f"CaSi-{Ca_Si_ratio}_WSi-{W_Si_ratio}"

make_independent = True

offset_gaussian = False
width_Ca_Si = 0.1
width_SiOH = 0.1
width_CaOH = 0.1

create =True
check = False

write_lammps = False
write_lammps_erica = True
write_vasp = False
write_siesta = False

read_structure = False
surface_from_bulk = False
surface_separation = False

shape_read = (3,3,2)
brick_code = { 
(  0,   0,   0)  :   ['<Lo', 'CU', '<R', '>L', 'CD', 'oMDR', '>R'], 
(  0,   0,   1)  :   ['<L', '<R', 'XD', 'CIU', 'oDL', '>Lo', '>R'], 
(  0,   1,   0)  :   ['<L', 'CU', '<R', 'XU', 'oUL', '>L', '>Ro'], 
(  0,   1,   1)  :   ['<L', '<R', 'XU', 'XD', 'oUL', 'oXU', '>Lo', '>R'], 
(  0,   2,   0)  :   ['<L', 'CU', '<R', 'CII', 'oDR', '>Lo', '>R'], 
(  0,   2,   1)  :   ['<Lo', 'CU', 'oMUL', '<R', 'XD', '>L', '>R'], 
(  1,   0,   0)  :   ['<L', 'SU', 'oMUL', '<R', 'CII', 'XU', 'XD', 'CID', 'CIU', 'oDL', 'oUR', 'oXU', '>L', 'SDo', 'oMDL', '>R'], 
(  1,   0,   1)  :   ['<L', '<R', 'XU', 'oDL', '>Lo', 'CD', '>R'], 
(  1,   1,   0)  :   ['<L', 'CU', '<R', '>L', 'CD', 'oMDR', '>R'], 
(  1,   1,   1)  :   ['<L', 'SUo', 'oMUL', '<R', 'CII', 'XU', 'XD', 'CID', 'CIU', 'oDL', 'oUR', 'oXU', '>L', 'SD', 'oMDL', '>R'], 
(  1,   2,   0)  :   ['<L', 'CU', '<R', 'CII', 'oDR', '>Lo', '>R'], 
(  1,   2,   1)  :   ['<Lo', 'CU', 'oMUL', '<R', 'XU', '>L', '>R'], 
(  2,   0,   0)  :   ['<Lo', '<R', 'XD', 'oUL', 'oXD', '>L', 'CD', '>R'], 
(  2,   0,   1)  :   ['<L', 'SU', 'oMUL', '<R', 'CII', 'XU', 'XD', 'CID', 'CIU', 'oDL', 'oUR', 'oXU', '>L', 'SD', 'oMDL', '>R'], 
(  2,   1,   0)  :   ['<Lo', '<R', 'XD', 'CIU', 'oDL', 'oUR', '>L', '>R'], 
(  2,   1,   1)  :   ['<Lo', '<R', 'XD', '>L', 'CD', 'oMDR', '>R'], 
(  2,   2,   0)  :   ['<L', 'CU', 'oMUL', 'oMUR', '<Ro', 'CID', '>L', '>R'], 
(  2,   2,   1)  :   ['<L', 'CU', '<R', 'CII', 'oDL', '>L', '>Ro'], 
}

water_code = { 
(  0,   0,  0)  :   ['wMDL', 'wXD', 'wUL', 'wIR2', 'wIR'], 
(  0,   0,  1)  :   ['wDR', 'wXD', 'wMDR', 'wMUR', 'w15'], 
(  0,   1,  0)  :   ['wMUR', 'wDR', 'wMUL', 'w15', 'wMDR'], 
(  0,   1,  1)  :   ['w16', 'wIR', 'w15', 'wIR2', 'wIL'], 
(  0,   2,  0)  :   ['wXD', 'wIR', 'w16', 'wMUL', 'wIR2'], 
(  0,   2,  1)  :   ['w14', 'wDR', 'wIL', 'wXD', 'wIR'], 
(  1,   0,  0)  :   ['wXD', 'w16', 'w15', 'wIL'], 
(  1,   0,  1)  :   ['wMDR', 'wIL', 'wIR2', 'wIR'], 
(  1,   1,  0)  :   ['wMUR', 'w15', 'wDR', 'w16'], 
(  1,   1,  1)  :   ['wIR2', 'w14', 'w15', 'wXD'], 
(  1,   2,  0)  :   ['wMDL', 'w16', 'wUL', 'wIR2'], 
(  1,   2,  1)  :   ['wIL', 'wXD', 'wIR', 'wMUR'], 
(  2,   0,  0)  :   ['wMDL', 'w14', 'wMUR', 'w15'], 
(  2,   0,  1)  :   ['w16', 'wIR2', 'w14', 'wIL'], 
(  2,   1,  0)  :   ['wXU', 'wMUL', 'wUL', 'w14'], 
(  2,   1,  1)  :   ['wIL', 'wMDL', 'w16', 'wXD'], 
(  2,   2,  0)  :   ['w16', 'w15', 'wXD', 'wIL'], 
(  2,   2,  1)  :   ['wMUR', 'wIR', 'wIL', 'wXD'], 
}



from mod_construct_brick import *
from mod_sample import *
from mod_construct_supercell import *
from mod_write import *
from mod_check import *
from mod_make_graphs import *
import time


widths = [width_Ca_Si, width_SiOH, width_CaOH]

np.random.seed(seed)
random.seed(seed+10)

if create or check:
	# Get all possible bricks
	bricks, sorted_bricks = get_all_bricks(pieces)

	# for CaSi in sorted_bricks:
	# 	if 0 in sorted_bricks[CaSi]:
	# 		for Si in sorted_bricks[CaSi][0]:
	# 			for Ca in sorted_bricks[CaSi][0][Si]:
	# 				print(CaSi, Si, Ca, len(sorted_bricks[CaSi][0][Si][Ca]))
	# 	print()


#combs = [ b.comb for b in bricks ]

#s = set(tuple(i) for i in combs)


if create or read_structure:
	if not os.path.isdir("./output"):
		os.makedirs('./output')


list_properties = []

if create:
    import numpy as np

    # Lattice
    unitcell = np.array([
        [6.7352,    0.0 ,      0.0],
        [-4.071295, 6.209521,  0.0],
        [0.7037701,-6.2095578,13.9936836]
    ])
    supercell = np.zeros((3,3))
    for i in range(3):
        supercell[i,:] = unitcell[i,:]*shape[i]

    N_brick = shape[0]*shape[1]*shape[2]

    # ratios = np.linspace(1.2, 2.1, 10)  # 30 uniform Ca/Si values
    # Ca_Si_ratios = [1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1]
    Ca_Si_ratios = [1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 2.1]
    W_Si_ratio = 1.6  # fixed water/Si ratio
    list_properties = []
    list_crystals = []

    t_all = time.time()

    for r_idx, Ca_Si_ratio in enumerate(Ca_Si_ratios, start=1):
        # unique prefix per ratio
        prefix = f"CaSi-{Ca_Si_ratio}_WSi-{W_Si_ratio}"

        # (optional) subfolder per ratio — uncomment if you prefer folders
        # outdir = os.path.join("output", f"CaSi_{Ca_Si_ratio}")
        # os.makedirs(outdir, exist_ok=True)

        offset = [0.0, 0.0]
        if offset_gaussian:
            off_Si, off_Ca = get_offset(500, sorted_bricks, Ca_Si_ratio, W_Si_ratio, N_brick, widths)
            offset = [off_Si, off_Ca]

        jsample = 0
        t = time.time()
        if Ca_Si_ratio in [1.6, 1.7, 1.8, 2.1]:
            N_samples = 15
        else:
            N_samples = 10

        for isample in range(N_samples):
            crystal, N_Ca, N_Si, r_SiOH, r_CaOH, MCL, N_water, r_2H_Si = sample_Ca_Si_ratio(
                sorted_bricks, Ca_Si_ratio, W_Si_ratio, N_brick, widths, offset=offset
            )

            crystal_index = [brick.ind for brick in crystal]
            new = False
            if make_independent and set(crystal_index) not in list_crystals:
                new = True
                list_crystals.append(set(crystal_index))
            elif not make_independent and crystal_index not in list_crystals:
                new = True
                list_crystals.append(crystal_index)

            if not new:
                continue

            list_properties.append([N_Ca/N_Si, r_SiOH, r_CaOH, MCL, jsample+1, r_2H_Si])

            water_in_crystal = fill_water(crystal, N_water=N_water)
            crystal_rs, water_in_crystal_rs = reshape_crystal(crystal, water_in_crystal, shape)
            entries_crystal, entries_bonds, crystal_dict, water_dict = get_full_coordinates(
                crystal_rs, water_in_crystal_rs, shape, pieces
            )
            entries_angle = get_angles(crystal_dict, water_dict, shape)

            # fix overlapping water H
            entries_crystal, N_not_ok, itry = check_move_water_hydrogens(entries_crystal)
            if N_not_ok != 0:
                print(f"[Ca/Si={Ca_Si_ratio}] Warning: structure {jsample:5d} contains {N_not_ok:5d} wrong water molecules")
            else:
                print(f"[Ca/Si={Ca_Si_ratio}] Structure {jsample:5d} converged after {itry:5d} iterations")

            # Write files (prefix carries the ratio)
            write_output(
                jsample, entries_crystal, entries_bonds, entries_angle, shape, crystal_rs, water_in_crystal_rs,
                supercell, N_Ca, N_Si, r_SiOH, r_CaOH, MCL,
                write_lammps, write_lammps_erica, write_vasp, write_siesta, prefix
            )
            jsample += 1
    
        print(f"[Ca/Si={Ca_Si_ratio}] Generation completed in {time.time()-t:12.6f} s")

    # One set of summary plots/logs for all runs
    list_properties = np.array(list_properties)
    plot_XOH_X(list_properties)
    plot_MCL(list_properties)
    plot_distributions(list_properties)
    plot_water(list_properties)
    get_sorted_log(list_properties)

    print(f"All ratios completed in {time.time()-t_all:12.6f} s")


if check:
	check_SiOH_CaOH_MCL(sorted_bricks, widths, shape)
	plot_experimental()





if read_structure:

	shape, crystal_rs, water_in_crystal_rs, N_Si, N_Ca, r_SiOH, r_CaOH, MCL = read_brick(shape_read, brick_code, water_code, pieces, surface_from_bulk)
	
	entries_crystal, entries_bonds, crystal_dict, water_dict = get_full_coordinates( crystal_rs, water_in_crystal_rs, shape, pieces )

	entries_angle = get_angles(crystal_dict, water_dict, shape)

	entries_crystal, N_not_ok, itry = check_move_water_hydrogens(entries_crystal)



	unitcell = np.array([ [6.7352,    0.0 ,      0.0],
				 		   [-4.071295, 6.209521,  0.0],
						   [0.7037701, -6.2095578, 13.9936836] ])

	supercell = np.zeros((3,3))
	for i in range(3):
		supercell[i,:] = unitcell[i,:]*shape[i]


	if surface_separation:
		entries_crystal, supercell = transform_surface_separation(entries_crystal, supercell, unitcell, surface_separation)		

	mypath = os.path.abspath(".")
	path = os.path.join(mypath, "output/")

	name = prefix+"_fromManualCode.data"
	name = os.path.join(path, name)
	get_lammps_input(name, entries_crystal, entries_bonds, entries_angle, supercell, write_lammps_erica) 
	name = prefix+"_fromManualCode.log"
	name = os.path.join(path, name)
	get_log(name, shape, crystal_rs, water_in_crystal_rs, N_Ca, N_Si, r_SiOH, r_CaOH, MCL )

	name = prefix+"_fromManualCode.vasp"
	name = os.path.join(path, name)
	get_vasp_input(name, entries_crystal, supercell)

	name = prefix+"_fromManualCode.xyz"
	name = os.path.join(path, name)
	get_xyz_input(name, entries_crystal, supercell)

	name = prefix+"_fromManualCode.fdf"
	name = os.path.join(path, name)
	get_siesta_input(name, entries_crystal, supercell)
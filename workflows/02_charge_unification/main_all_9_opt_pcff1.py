import numpy as np
import pandas as pd
from run_MD_sim_for_K_pcff1 import MD_sim_charge


# === Run MD simulation ===
# Charge definitions
q_vals = {
    '{q_cat}': 1.7, # Ca(dry)
    '{q_casl}': 1.7, # Ca(wet)
    '{q_sc2_3}': 1.0, # Si(dry / wet sides)
    '{q_oc12}': -0.5, # Obridge
    '{q_oc13}': -1.1, # Osiloxide (dry)
    '{q_oc22}': -1.1, # Osiloxide (wet)
    '{q_ocx}': -0.5, # Ointerlayer bridge
    '{q_oc14}': -0.67, # Osilanol
    '{q_hoy}': 0.42 # Hsilanol
}

# sc_r, sc_eps, oc_r, oc_eps, ocx_r, ocx_eps, sos_ktheta, oso_ktheta, so_kr
# r_eps_theta_k = [[4.783425252, 0.26020483, 3.615604502, 0.038971308, 3.615604502, 0.038971308, 100, 100, 350],
# [4.5145568, 0.334787397, 3.705772483, 0.080167756, 3.705772483, 0.080167756, 100, 100, 350]]

# r_eps_theta_k = [[4.54246617, 0.353988826, 3.585991144, 0.131453089, 3.585991144, 0.131453089, 100, 100, 350],
# [4.575, 0.265, 3.65, 0.11, 3.7, 0.12, 100, 100, 350],
# [4.695828644, 0.350136893, 3.488717377, 0.13020344, 3.488717377, 0.13020344, 100, 100, 350],
# [4.54250886, 0.357622178, 3.679453595, 0.091791874, 3.679453595, 0.091791874, 100, 100, 350],
# [4.66272, 0.19291879, 3.537951, 0.12879516, 3.537951, 0.12879516, 100, 100, 350]]



MD_sim_charge(q_vals, r_eps_theta_k, optimizer='pcff1')

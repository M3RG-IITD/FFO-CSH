import numpy as np
import pandas as pd
from run_MD_sim_for_K_pcff import MD_sim_charge


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
r_eps_theta_k = [[4.695828644, 0.350136893, 3.488717377, 0.13020344, 3.488717377, 0.13020344, 100, 100, 350],
[4.539837965, 0.35012039, 3.540883449, 0.129731503, 3.540883449, 0.129731503, 100, 100, 350],
[4.783425252, 0.26020483, 3.615604502, 0.038971308, 3.615604502, 0.038971308, 95, 95, 490]]


MD_sim_charge(q_vals, r_eps_theta_k, optimizer='pcff')

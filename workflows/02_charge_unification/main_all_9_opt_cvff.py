import numpy as np
import pandas as pd
from run_MD_sim_for_K_cvff_SE import MD_sim_charge


# === Run MD simulation ===
# X_list = [0.9, 1.0, 1.1]
# X_list = [0.5, 0.6, 0.7, 0.8, 1.2, 1.3, 1.4, 1.5]
# X_list = [1.2]


# Charge definitions
# Define charges
q_vals_den = {
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

q_vals_se = {
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
q_vals_se14 = {
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


# q_vals_se = {
#     '{q_cat}': 1.7,
#     '{q_casl}': 1.7,
#     '{q_sc2_3}': 1.0,
#     '{q_oc12}': -0.48,          ----
#     '{q_oc13}': -1.11,          ----
#     '{q_oc22}': -1.14,          ----
#     '{q_ocx}': -0.54,           ----
#     '{q_oc14}': -0.65,          ----
#     '{q_hoy}': 0.40             ----
# }

# q_vals_se14 = {
#     '{q_cat}': 1.7,
#     '{q_casl}': 1.7,
#     '{q_sc2_3}': 1.0,
#     '{q_oc12}': -0.47,
#     '{q_oc13}': -1.11,
#     '{q_oc22}': -1.15,
#     '{q_ocx}': -0.54,
#     '{q_oc14}': -0.65,
#     '{q_hoy}': 0.40
# }



# q_vals_se = {
#     '{q_cat}': 1.7,
#     '{q_casl}': 1.7,
#     '{q_sc2_3}': 1.0,
#     '{q_oc12}': -0.46,
#     '{q_oc13}': -1.12,
#     '{q_oc22}': -1.18,
#     '{q_ocx}': -0.58,
#     '{q_oc14}': -0.63,
#     '{q_hoy}': 0.38
# }

# q_vals_se14 = {
#     '{q_cat}': 1.7,
#     '{q_casl}': 1.7,
#     '{q_sc2_3}': 1.0,
#     '{q_oc12}': -0.45,
#     '{q_oc13}': -1.12,
#     '{q_oc22}': -1.17,
#     '{q_ocx}': -0.58,
#     '{q_oc14}': -0.63,
#     '{q_hoy}': 0.38
# }



MD_sim_charge(q_vals_den, q_vals_se, q_vals_se14, optimizer='cvff')


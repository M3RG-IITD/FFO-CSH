import numpy as np
import pandas as pd
from run_MD_sim_for_K import MD_sim_CVFF

import numpy as np
from scipy.stats import qmc

############################# Grid and LHS sampling #############################
# # Grid
# sc_r_values_n = []
# sc_eps_values_n = []
# oc_r_values_n = []
# oc_eps_values_n = []

# sc_r_values = np.linspace(4.30, 4.55, 5)
# sc_eps_values = np.linspace(0.30, 0.51, 5)

# oc_r_values = np.linspace(3.30, 3.80, 5)
# oc_eps_values = np.linspace(0.08, 0.19, 5)


# for i, (s_r,s_eps) in enumerate(zip(sc_r_values, sc_eps_values)):
#     for  j, (o_r,o_eps) in enumerate(zip(oc_r_values, oc_eps_values)):
#         # print(f"sc_r: {s_r}, sc_eps: {s_eps}, oc_r: {o_r}, oc_eps: {o_eps}")
#         sc_r_values_n.append(s_r)
#         sc_eps_values_n.append(s_eps)
#         oc_r_values_n.append(o_r)
#         oc_eps_values_n.append(o_eps)

# all_params_grid = np.array([sc_r_values_n, sc_eps_values_n, oc_r_values_n, oc_eps_values_n]).T

# # LHS
# param_bounds = {
#     "sc_r": (4.30, 4.55),
#     "sc_eps": (0.30, 0.51),
#     "oc_r": (3.30, 3.80),
#     "oc_eps": (0.03, 0.19),
# }

# n_samples = 50
# # Create LHS sampler
# sampler = qmc.LatinHypercube(d=len(param_bounds))
# lhs_unit = sampler.random(n=n_samples)
# # Scale to actual bounds
# lower_bounds = [v[0] for v in param_bounds.values()]
# upper_bounds = [v[1] for v in param_bounds.values()]
# lhs_scaled = qmc.scale(lhs_unit, lower_bounds, upper_bounds)

# all_params_lhs = lhs_scaled

# all_params = np.vstack((all_params_grid, all_params_lhs))



################################### ocx optimization ###################################


# === 1. Load Data ===
df_full = pd.read_csv('runs/cvff_lj_params/data_LJ_0_75_20250627_083515.csv')

mean_cols = ['D_11', 'D_11H', 'D_14', 'SE_T11', 'SE_T11H', 'SE_T14', 'BM_T11', 'BM_T11H', 'BM_T14']
error_cols = [f'error_{i}' for i in mean_cols]
y_error_fulll = df_full[error_cols].values # y_error_all = np.abs(100 * (y - target_y) / target_y)

targeted_error = np.array([1, 1, 1, 5, 5, 5, 10, 10, 10])  # in %


df_clean1  = df_full.iloc[(y_error_fulll < np.array([100, 2, 2, 100, 100, 100, 10, 10, 100])).sum(axis=1) == 9].sort_values(by='error_D_14', ascending=True)
df_clean2  = df_full.iloc[(y_error_fulll < np.array([100, 2, 2, 100, 100, 100, 10, 10, 100])).sum(axis=1) == 9].sort_values(by='error_D_11H', ascending=True)
df_clean3  = df_full.iloc[(y_error_fulll < np.array([100, 2, 2, 100, 100, 100, 10, 10, 100])).sum(axis=1) == 9].sort_values(by='error_D_11', ascending=True)
df_clean4  = df_full.iloc[(y_error_fulll < np.array([100, 2, 2, 100, 100, 100, 10, 10, 100])).sum(axis=1) == 9].sort_values(by='error_BM_T14', ascending=True)
df_clean5  = df_full.iloc[(y_error_fulll < np.array([2, 2, 2, 100, 100, 100, 100, 100, 100])).sum(axis=1) == 9].sort_values(by='error_BM_T14', ascending=True)

# df_clean1[error_cols]
# df_clean2[error_cols]
# df_clean3[error_cols]
# df_clean4[error_cols]
# df_clean5[error_cols]

df1 = df_clean1[['optimizers', 'sc_r', 'sc_eps', 'oc_r', 'oc_eps', 'ocx_r', 'ocx_eps', 'sos_ktheta', 'oso_ktheta', 'so_kr']].iloc[:3]
df2 = df_clean2[['optimizers', 'sc_r', 'sc_eps', 'oc_r', 'oc_eps', 'ocx_r', 'ocx_eps', 'sos_ktheta', 'oso_ktheta', 'so_kr']].iloc[:3]
df3 = df_clean3[['optimizers', 'sc_r', 'sc_eps', 'oc_r', 'oc_eps', 'ocx_r', 'ocx_eps', 'sos_ktheta', 'oso_ktheta', 'so_kr']].iloc[:3]
df4 = df_clean4[['optimizers', 'sc_r', 'sc_eps', 'oc_r', 'oc_eps', 'ocx_r', 'ocx_eps', 'sos_ktheta', 'oso_ktheta', 'so_kr']].iloc[:3]
df5 = df_clean5[['optimizers', 'sc_r', 'sc_eps', 'oc_r', 'oc_eps', 'ocx_r', 'ocx_eps', 'sos_ktheta', 'oso_ktheta', 'so_kr']].iloc[:3]


df_clean = pd.concat([df1, df2, df3, df4, df5])
# df_clean.drop_duplicates(subset=['sc_r', 'sc_eps', 'oc_r', 'oc_eps', 'ocx_r', 'ocx_eps'])
df_clean = df_clean[['sc_r', 'sc_eps', 'oc_r', 'oc_eps']].drop_duplicates()

# === create new set of parameters ===
so_kr = [350.0]
ktheta_sets = [100.0]
# ocx: 3.329406565	0.059328007
all_params = np.array([
    [
        float(df_clean['sc_r'].values[i]),
        float(df_clean['sc_eps'].values[i]),
        float(df_clean['oc_r'].values[i]),
        float(df_clean['oc_eps'].values[i]),
        3.329406565,
        0.059328007,
        k,
        k,
        kr
    ]
    for i in range(len(df_clean))
    for k in ktheta_sets
    for kr in so_kr
])

print(f'shape_of_params: {all_params.shape}')

# === Run MD simulation ===
df_new_ocx_ktheta = MD_sim_CVFF(all_params, optimizer='None')

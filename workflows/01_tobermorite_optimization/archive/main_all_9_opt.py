import numpy as np
import pandas as pd
import os 
os.chdir('ML_Pipeline')
from run_MD_sim_for_K import MD_sim

# === 1. Load Data ===
df_full = pd.read_csv('ML_Pipeline/data/data_len_663_mean_std_20250618_051644.csv')

mean_cols = ['D_11', 'D_11H', 'D_14', 'SE_T11', 'SE_T11H', 'SE_T14', 'BM_T11', 'BM_T11H', 'BM_T14']
error_cols = [f'error_{i}' for i in mean_cols]
y_error_fulll = df_full[error_cols].values # y_error_all = np.abs(100 * (y - target_y) / target_y)

targeted_error = np.array([1, 1, 1, 5, 5, 5, 10, 10, 10])  # in %


df_clean1  = df_full.iloc[(y_error_fulll < np.array([100, 1, 1, 100, 100, 100, 10, 10, 100])).sum(axis=1) == 9].sort_values(by='error_D_14', ascending=True)
df_clean2  = df_full.iloc[(y_error_fulll < np.array([100, 1, 1, 100, 100, 100, 10, 10, 100])).sum(axis=1) == 9].sort_values(by='error_D_11H', ascending=True)
df_clean3  = df_full.iloc[(y_error_fulll < np.array([100, 1, 1, 100, 100, 100, 10, 10, 100])).sum(axis=1) == 9].sort_values(by='error_D_11', ascending=True)
df_clean4  = df_full.iloc[(y_error_fulll < np.array([100, 1, 1, 100, 100, 100, 10, 10, 100])).sum(axis=1) == 9].sort_values(by='error_BM_T14', ascending=True)
df_clean5  = df_full.iloc[(y_error_fulll < np.array([1.5, 1.5, 1.5, 100, 100, 100, 100, 100, 100])).sum(axis=1) == 9].sort_values(by='error_BM_T14', ascending=True)

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
# ocx_r = 3.70
# ocx_eps = 0.12
# ktheta_sets = [170, 150, 100, 80]

# 4.783425252	0.26020483	3.615604502	0.038971308	3.615604502	0.038971308	90	90

# ktheta_sets = [90, 95]
# # so_kr = [330, 340, 350, 360, 370]

# so_kr = [300, 310, 320, 380, 390, 400, 410, 420, 430, 440, 450, 460, 470, 480, 490, 500]

# all_params = np.array([
#     [
#         4.783425252, #float(df_clean['sc_r'].values[i]),
#         0.26020483, #float(df_clean['sc_eps'].values[i]),
#         3.615604502, #float(df_clean['oc_r'].values[i]),
#         0.038971308, #float(df_clean['oc_eps'].values[i]),
#         3.615604502,
#         0.038971308,
#         k,
#         k,
#         kr
#     ]
#     # for i in range(len(df_clean))
#     for k in ktheta_sets
#     for kr in so_kr
# ])


# 4.54250886	0.357622178	3.679453595	0.091791874	3.679453595	0.091791874	100	100	350

so_kr = [340, 350, 360, 420, 430, 440]
ktheta_sets = [90, 100, 110, 160, 170, 180]

all_params = np.array([
    [
        float(df_clean['sc_r'].values[i]),
        float(df_clean['sc_eps'].values[i]),
        float(df_clean['oc_r'].values[i]),
        float(df_clean['oc_eps'].values[i]),
        float(df_clean['oc_r'].values[i]),
        float(df_clean['oc_eps'].values[i]),        
        k,
        k,
        kr
    ]
    for i in range(len(df_clean))
    for k in ktheta_sets
    for kr in so_kr
])
print(f'shape_of_params: {all_params.shape}')


# ocx_rs = [3.4, 3.45, 3.457076515] #[3.35, 3.4, 3.45]
# ocx_epss = 	[0.085, 0.098264456, 0.13] # [0.04, 0.05, 0.06, 0.085, 0.13]
# ktheta_sets = [170, 160]

# i = 1 # 4.575	0.265	3.65	0.11

# all_params = np.array([
#     [
#         float(df_clean['sc_r'].values[i]),
#         float(df_clean['sc_eps'].values[i]),
#         float(df_clean['oc_r'].values[i]),
#         float(df_clean['oc_eps'].values[i]),
#         ocx_r,
#         ocx_eps,
#         k,
#         k
#     ]
#     # for i in range(len(df_clean))
#     for k in ktheta_sets
#     for ocx_r in ocx_rs
#     for ocx_eps in ocx_epss
# ])
# print(f'shape_of_params: {all_params.shape}')

# === Run MD simulation ===

df_new_ocx_ktheta = MD_sim(all_params, optimizer= 'new11H14')

# df_new_ocx_ktheta = df_new_ocx_ktheta.dropna()

# # === Evaluate match ===
# md_prop_pred = df_new_ocx_ktheta.values[:,4:]
# y_error = np.abs(100*(md_prop_pred - np.array(target_y))/np.array(target_y))

# for i in range(len(y_error)):
#     targeted_error = np.array([1, 1, 1, 5, 5, 5, 10, 10, 10])
#     if (y_error[i] <= targeted_error).sum() == 9:
#         print("All properties are within error limits")
#         print(df_new_ocx_ktheta.iloc[i])
#         break # break Active learning loop.

#     else:
#         total_false = (~(y_error[i] <= targeted_error)).sum()
#         print("❌ Failure! Outside acceptable error range.")
#         print(f"Failed for {total_false} properties")
#         print("Error percentage:", y_error[i].round(2))




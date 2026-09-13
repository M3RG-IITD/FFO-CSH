import numpy as np

def compute_elastic_properties(C):
    """
    Computes bulk modulus (K), Young's moduli (E), Poisson's ratios (nu), and shear moduli (G)
    from a given 6x6 elastic stiffness tensor C.
    """
    # Compute Bulk modulus (K)
    K = (1/9) * (C[0,0] + C[1,1] + C[2,2] + 2*(C[0,1] + C[0,2] + C[1,2]))

    # Compute compliance matrix S = C^-1
    S = np.linalg.inv(C)

    # Compute Young’s moduli (E_x, E_y, E_z)
    E_x = 1 / S[0,0]
    E_y = 1 / S[1,1]
    E_z = 1 / S[2,2]

    # Compute Poisson's ratios
    nu_xy = -S[0,1] / S[0,0]
    nu_yx = -S[1,0] / S[1,1]
    nu_yz = -S[1,2] / S[1,1]
    nu_zy = -S[2,1] / S[2,2]
    nu_zx = -S[2,0] / S[2,2]
    nu_xz = -S[0,2] / S[0,0]

    # Compute shear moduli (G_xy, G_yz, G_zx)
    G_xy = 1 / S[3,3]
    G_yz = 1 / S[4,4]
    G_zx = 1 / S[5,5]

    # Compute Voigt and Reuss shear moduli
    G_V = (1/15) * (C[0,0] + C[1,1] + C[2,2] - C[0,1] - C[1,2] - C[0,2] + 3*(C[3,3] + C[4,4] + C[5,5]))
    G_R = 15 / (4*(S[0,0] + S[1,1] + S[2,2] - S[0,1] - S[1,2] - S[0,2]) + 3*(S[3,3] + S[4,4] + S[5,5]))
    G_H = (G_V + G_R) / 2  # Hill Shear Modulus

    return {
        "Bulk Modulus (K)": K,
        "Young's Moduli (E_x, E_y, E_z)": (E_x, E_y, E_z),
        "Poisson Ratios (ν_xy, ν_yx, ν_yz, ν_zy, ν_zx, ν_xz)": (nu_xy, nu_yx, nu_yz, nu_zy, nu_zx, nu_xz),
        "Shear Moduli (G_xy, G_yz, G_zx)": (G_xy, G_yz, G_zx),
        "Hill Shear Modulus (G_H)": G_H
    }

# Given elastic stiffness tensor (Cij matrix)
# this is 0.1ns
# C = np.array([
#     [107.37,  48.69,  13.94, -0.09, -0.26, -11.50],
#     [48.69,  139.44,  23.80,  0.04,  0.19,  -6.42],
#     [13.94,  23.80,  51.70, -0.33,  0.47,  -0.75],
#     [-0.09,   0.04,  -0.33, 29.69, -8.17,  -0.18],
#     [-0.26,   0.19,   0.47, -8.17, 15.05,   0.11],
#     [-11.50, -6.42,  -0.75, -0.18,  0.11,  35.29]
# ])

# this is 1ns
C = np.array([
    [101.64, 50.70, 10.26, -0.28, -0.06, -10.99],
    [50.70, 133.38, 21.84, 1.44, 1.05, -6.62],
    [10.26, 21.84, 45.21, -0.83, -0.22, -0.10],
    [-0.28, 1.44, -0.83, 28.43, -7.25, 0.58],
    [-0.06, 1.05, -0.22, -7.25, 12.73, 0.23],
    [-10.99, -6.62, -0.10, 0.58, 0.23, 33.88]
])

# Compute properties
properties = compute_elastic_properties(C)

# Print results
for key, value in properties.items():
    print(f"{key}: {value}")

# Bulk Modulus (K): 49.536666666666655
# Young's Moduli (E_x, E_y, E_z): (np.float64(80.07293670706855), np.float64(101.3073379488806), np.float64(41.463791675527546))
# Poisson Ratios (ν_xy, ν_yx, ν_yz, ν_zy, ν_zx, ν_xz): (np.float64(0.3598359300018358), np.float64(0.4552601873490134), np.float64(0.3823453456163301), np.float64(0.15648903702062247), np.float64(0.026771509289095545), np.float64(0.0516998875943048))
# Shear Moduli (G_xy, G_yz, G_zx): (np.float64(24.200356356111477), np.float64(10.845640201325756), np.float64(32.61875122208858))
# Hill Shear Modulus (G_H): 24.587611876701093


# Bulk_Modulus = 49.54
# Young_Modulus = 80.07, 101.31, 41.46
# Poisson_Ratio = 0.36, 0.46, 0.38, 0.16, 0.03, 0.05
# Shear_Modulus = 24.20, 10.85, 32.62
# Hill_Shear_Modulus = 24.59

# Given bulk modulus (from other method)
Bulk_Modulus = 49.54  # GPa

E_x, E_y, E_z = 80.07, 101.31, 41.46 # directional Young's moduli (in GPa)
E_bulk = 3 / ((1/E_x) + (1/E_y) + (1/E_z)) # Compute the bulk Young's modulus using the harmonic mean formula

G_x, G_y, G_z = 24.20, 10.85, 32.62 # directional shear moduli (in GPa)
G_bulk = 3 / ((1/G_x) + (1/G_y) + (1/G_z))

# Compute the bulk Poisson's ratio using the formula
nu_bulk = (3 * Bulk_Modulus - 2 * G_bulk) / (6 * Bulk_Modulus + 2 * G_bulk)

E_bulk, G_bulk, nu_bulk
# (64.54, 18.28, 0.34)

# import seaborn as sns
# import matplotlib.pyplot as plt

# # Given Cij matrix
# Cij = C.round(2)

# # Create a mask to highlight diagonal
# mask = np.zeros_like(Cij, dtype=bool)
# np.fill_diagonal(mask, False)

# # Set a color palette for symmetric values
# ax = sns.heatmap(Cij, annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5, center=0, 
#                  mask=mask, cbar=True, square=True)

# # Overlay the diagonal in a different color
# for i in range(len(Cij)):
#     ax.add_patch(plt.Rectangle((i, i), 1, 1, fill=False, edgecolor='black', lw=2))

# plt.title("Bulk_Modulus = 52.37 \n Young_Modulus = 87.22, 111.17, 47.25 \n Poisson_Ratio = 0.32, 0.40, 0.35, 0.15, 0.07, 0.12 \n \n Elastic Stiffness Tensor (Cij)")
# plt.tight_layout()
# plt.savefig('elastic_stiffness_tensor1.png')

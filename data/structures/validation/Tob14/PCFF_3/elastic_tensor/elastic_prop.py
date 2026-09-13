import numpy as np

def compute_elastic_properties(C):
    """
    Computes bulk modulus (K), Young's moduli (E), Poisson's ratios (nu), and shear moduli (G)
    from a given 6x6 elastic stiffness tensor C.
    """
    # Compute Bulk modulus (K)
    K = (1/9) * (C[0,0] + C[1,1] + C[2,2] + C[0,1] + C[1,0] + C[0,2]+ C[2,0] + C[1,2]+ C[2,1])

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

    # # Compute Voigt and Reuss shear moduli
    # G_V = (1/15) * (C[0,0] + C[1,1] + C[2,2] - C[0,1] - C[1,2] - C[0,2] + 3*(C[3,3] + C[4,4] + C[5,5]))
    # G_R = 15 / (4*(S[0,0] + S[1,1] + S[2,2] - S[0,1] - S[1,2] - S[0,2]) + 3*(S[3,3] + S[4,4] + S[5,5]))
    # G_H = (G_V + G_R) / 2  # Hill Shear Modulus

    return {
        "Bulk Modulus (K)": K,
        "Young's Moduli (E_x, E_y, E_z)": (E_x, E_y, E_z),
        "Poisson Ratios (ν_xy, ν_yx, ν_yz, ν_zy, ν_zx, ν_xz)": (nu_xy, nu_yx, nu_yz, nu_zy, nu_zx, nu_xz),
        "Shear Moduli (G_xy, G_yz, G_zx)": (G_xy, G_yz, G_zx)
        # "Hill Shear Modulus (G_H)": G_H
    }


C11 = 72.8021272172299
C22 = 109.767782101361
C33 = 28.3814433862682

C12 = 43.9216582385571
C21 = 54.7829166962297
C13 = 14.024840753745
C31 = 9.8395399778616
C23 = 11.0500530780131
C32 = 13.1706709511904

C44 = 14.8786865292459
C55 = 7.20342379318252
C66 = 25.5371258593643

C14 = -7.94042402214222
C41 = -9.9874341692635
C15 = -4.1425200433814
C51 = 1.09578010314381
C16 = -10.8146884857891
C61 = -7.26818521562555

C24 = -5.03092035731317
C42 = 1.24994480474986
C25 = 0.59661120206778
C52 = 5.06756323135614
C26 = -8.19994175086324
C62 = -11.0885597952398

C34 = 7.31974885446499
C43 = -1.22408008821416
C35 = -8.57971826591629
C53 = 5.30038413627046
C36 = 2.28749227437612
C63 = -3.19744615950936

C45 = -13.1101418700982
C54 = -7.70785448711642
C46 = 18.6728467225517
C64 = -3.09278847223717
C56 = 9.88813733953534
C65 = -7.55002947408949


# Make Elastic tensor 6*6
C = np.array([[C11, C12, C13, C14, C15, C16],
              [C21, C22, C23, C24, C25, C26],
              [C31, C32, C33, C34, C35, C36],
              [C41, C42, C43, C44, C45, C46],
              [C51, C52, C53, C54, C55, C56],
              [C61, C62, C63, C64, C65, C66]])
             
# Compute properties
properties = compute_elastic_properties(C)

# Print results
for key, value in properties.items():
    print(f"{key}: {value}")


# Bulk Modulus (K): 39.749003600050656
# Young's Moduli (E_x, E_y, E_z): (np.float64(38.75481799292407), np.float64(70.35998939107489), np.float64(28.003826419922458))
# Poisson Ratios (ν_xy, ν_yx, ν_yz, ν_zy, ν_zx, ν_xz): (np.float64(0.4680379370095317), np.float64(0.7613078954991741), np.float64(-0.11482331828555449), np.float64(0.07705306636497913), np.float64(0.14003702976978996), np.float64(0.5337132638769304))
# Shear Moduli (G_xy, G_yz, G_zx): (np.float64(10.196019311206259), np.float64(7.609293845939113), np.float64(-273.24954504588976))


# Bulk_Modulus = 39.74
# Young_Modulus = 38.75, 70.36, 28.00
# Poisson_Ratio = 0.47, 0.76, -0.11, 0.08, 0.14, 0.53
# Shear_Modulus = 10.20, 7.61, -273.25


import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Given Cij matrix
Cij = C.round(2)

# Create a mask to highlight diagonal
mask = np.zeros_like(Cij, dtype=bool)
np.fill_diagonal(mask, False)

# Set a color palette for symmetric values
ax = sns.heatmap(Cij, annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5, center=0, 
                 mask=mask, cbar=True, square=True)

# Overlay the diagonal in a different color
for i in range(len(Cij)):
    ax.add_patch(plt.Rectangle((i, i), 1, 1, fill=False, edgecolor='black', lw=2))

plt.title("Bulk_Modulus = 39.74 \n Young_Modulus = 38.75, 70.36, 28.00 \n Poisson_Ratio = 0.47, 0.76, -0.11, 0.08, 0.14, 0.53 \n \n Elastic Stiffness Tensor (Cij)")
plt.tight_layout()
plt.savefig('elastic_stiffness_tensor.png')

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


C11all = 97.3312817903903
C22all = 136.371508691372
C33all = 50.3864889524067
C12all = 45.2324024278611
C13all = -4.70195778525355
C23all = 31.0033883443403
C44all = 31.4489152728278
C55all = 3.99951231172156
C66all = 38.0574719361989
C14all = -2.06032151366278
C15all = -3.98019801139293
C16all = -16.098960823115
C24all = -5.09159631702513
C25all = -1.34099245046109
C26all = -6.21969748387594
C34all = 3.34076408800338
C35all = 3.8865247803263
C36all = -2.67802150285058
C45all = 2.96897931182991
C46all = 4.61703131359614
C56all = 1.56952434524794

# Elastic tensor 6*6
C = np.array([[C11all, C12all, C13all, C14all, C15all, C16all],
              [C12all, C22all, C23all, C24all, C25all, C26all],
              [C13all, C23all, C33all, C34all, C35all, C36all],
              [C14all, C24all, C34all, C44all, C45all, C46all],
              [C15all, C25all, C35all, C45all, C55all, C56all],
              [C16all, C26all, C36all, C46all, C56all, C66all]])

# Compute properties
properties = compute_elastic_properties(C)

# Print results
for key, value in properties.items():
    print(f"{key}: {value}")


# Bulk Modulus (K): 47.461882823118295
# Young's Moduli (E_x, E_y, E_z): (np.float64(70.46788645473082), np.float64(90.87156840251434), np.float64(36.53831293779082))
# Poisson Ratios (ν_xy, ν_yx, ν_yz, ν_zy, ν_zx, ν_xz): (np.float64(0.3877327668504834), np.float64(0.4999991686622303), np.float64(0.71643225588218), np.float64(0.28806838513228755), np.float64(-0.16697832657982817), np.float64(-0.32203483991890436))
# Shear Moduli (G_xy, G_yz, G_zx): (np.float64(28.548515625206804), np.float64(3.2977034970846657), np.float64(34.073562425637014))
# Hill Shear Modulus (G_H): 19.99802612288901


# Bulk_Modulus = 47.46
# Young_Modulus = 70.47, 90.87, 36.54
# Poisson_Ratio = 0.39, 0.50, 0.72, 0.29, -0.17, -0.32
# Shear_Modulus = 28.55, 3.30, 34.07
# Hill_Shear_Modulus = 19.99

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

plt.title("Bulk_Modulus = 47.46 \n Young_Modulus = 70.47, 90.87, 36.54 \n Poisson_Ratio = 0.39, 0.50, 0.72, 0.29, -0.17, -0.32 \n \n Elastic Stiffness Tensor (Cij)")
plt.tight_layout()
plt.savefig('elastic_stiffness_tensor1.png')

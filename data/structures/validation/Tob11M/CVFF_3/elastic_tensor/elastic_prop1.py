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

C11all = 137.621604070639
C22all = 171.032759310708
C33all = 171.527586386742
C12all = 45.8307274965819
C13all = 25.5917114316958
C23all = 45.6712258546928
C44all = 35.3269945024507
C55all = 32.5144983053344
C66all = 36.8227044605933
C14all = -5.86534993215453
C15all = -3.15326159703651
C16all = -7.88912794617918
C24all = -0.653015685320731
C25all = 2.731080539686
C26all = -6.88906634966902
C34all = -5.61924062584808
C35all = 1.09121458306662
C36all = -12.4438869789092
C45all = 1.51016553970411
C46all = -1.0357126648174
C56all = -1.56250230352905

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


# Bulk Modulus (K): 79.37436437044778
# Young's Moduli (E_x, E_y, E_z): (np.float64(122.16871763965123), np.float64(146.93602268353152), np.float64(154.3905204154442))
# Poisson Ratios (ν_xy, ν_yx, ν_yz, ν_zy, ν_zx, ν_xz): (np.float64(0.24474997525530864), np.float64(0.2943682197105729), np.float64(0.2205064057207017), np.float64(0.23169334593656352), np.float64(0.08678111233593394), np.float64(0.06866961249236789))
# Shear Moduli (G_xy, G_yz, G_zx): (np.float64(34.79032342827934), np.float64(32.227503395090814), np.float64(35.476243047602914))
# Hill Shear Modulus (G_H): 43.0600455465341

# Bulk_Modulus = 79.37
# Young_Modulus = 112.17, 146.93, 154.39
# Poisson_Ratio = 0.24, 0.29, 0.22, 0.23, 0.08, 0.06
# Shear_Modulus = 34.79, 32.23, 35.47
# Hill_Shear_Modulus = 43.06

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



plt.title("Bulk_Modulus = 79.37 \n Young_Modulus = 112.17, 146.93, 154.39 \n Poisson_Ratio = 0.24, 0.29, 0.22, 0.23, 0.08, 0.06 \n \n Elastic Stiffness Tensor (Cij)")
plt.tight_layout()
plt.savefig('elastic_stiffness_tensor1.png')

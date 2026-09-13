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

C11 = 97.3312817903903
C21 = 44.61187801799015
C31 = -2.473160761912
C41 = -1.1406126834707775
C51 = -2.565587267186814
C61 = -9.510137969999745
C12 = 45.852926837732
C22 = 136.3715086913715
C32 = 33.7273362168851
C42 = -7.7538685291711555
C52 = 3.153856007792985
C62 = -14.110294936897525
C13 = -6.9307548085951005
C23 = 28.27944047179535
C33 = 50.38648895240665
C43 = 11.532651403273618
C53 = -6.21200645312011
C63 = -4.546797013130195
C14 = -2.9800303438547795
C24 = -2.4293241048790897
C34 = -4.85112322726684
C44 = 31.44891527282775
C54 = -2.734710008637435
C64 = 13.207311437603556
C15 = -5.394808755599046
C25 = -5.835840908715175
C35 = 13.985056013772684
C45 = 8.672668632297254
C55 = 3.99951231172156
C65 = 1.2802854273014002
C16 = -22.6877836762303
C26 = 1.6708999691456201
C36 = -0.809245992570962
C46 = -3.973248810411316
C56 = 1.858763263194465
C66 = 38.05747193619885


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

# Bulk Modulus (K): 47.46188282311821
# Young's Moduli (E_x, E_y, E_z): (np.float64(75.1734925877573), np.float64(108.95878368824053), np.float64(62.1823839281266))
# Poisson Ratios (ν_xy, ν_yx, ν_yz, ν_zy, ν_zx, ν_xz): (np.float64(0.3691725944993365), np.float64(0.45236384452892103), np.float64(0.47993659570291), np.float64(0.17628756845283108), np.float64(-0.03528889609512742), np.float64(-0.3912708219886205))
# Shear Moduli (G_xy, G_yz, G_zx): (np.float64(35.38398907643933), np.float64(7.142086213664709), np.float64(37.22616102401582))

# Bulk_Modulus = 47.46
# Young_Modulus = 75.17, 108.96, 62.18
# Poisson_Ratio = 0.37, 0.45, 0.48, 0.18, -0.04, -0.39
# Shear_Modulus = 35.38, 7.14, 37.23


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

plt.title("Bulk_Modulus = 47.46 \n Young_Modulus = 75.17, 108.96, 62.18 \n Poisson_Ratio = 0.37, 0.45, 0.48, 0.18, -0.04, -0.39 \n \n Elastic Stiffness Tensor (Cij)")
plt.tight_layout()
plt.savefig('elastic_stiffness_tensor2.png')

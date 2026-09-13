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


C11 = 137.621604070639
C22 = 171.032759310708
C33 = 171.527586386742

C12 = 36.65224446983155
C21 = 55.0092105233321
C13 = 21.3963351664464
C31 = 29.78708769694535
C23 = 37.02688559493255
C32 = 54.31556611445295

C44 = 35.3269945024507
C55 = 32.5144983053344
C66 = 36.8227044605933

C14 = -20.76628972993287
C41 = 9.035589865623837
C15 = 4.46140849553978
C51 = -10.767931689612801
C16 = 0.11612496956495022
C61 = -15.894380861923299

C24 = 8.320132666670851
C42 = -9.62616403731231
C25 = 2.8333636213260824
C52 = 2.628797458045918
C26 = -1.9225796996833449
C62 = -11.855552999654725

C34 = -15.031463635057811
C43 = 3.7929823833616547
C35 = 2.00107067308625
C53 = 0.18135849304698887
C36 = -11.867272264723825
C63 = -13.02050169309454

C45 = -3.20287758963957
C54 = 6.2232086690477875
C46 = -2.8981791449926324
C64 = 0.8267538153578354
C56 = 3.516337174709779
C65 = -6.641341781767875

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

# Bulk Modulus (K): 79.37436437044776
# Young's Moduli (E_x, E_y, E_z): (np.float64(132.25712616106566), np.float64(154.42273435846562), np.float64(157.32176704427363))
# Poisson Ratios (ν_xy, ν_yx, ν_yz, ν_zy, ν_zx, ν_xz): (np.float64(0.1463216077232148), np.float64(0.34198456991469767), np.float64(0.16456082227781135), np.float64(0.25202545315664704), np.float64(0.09739644684674889), np.float64(0.10555056739238086))
# Shear Moduli (G_xy, G_yz, G_zx): (np.float64(38.78752634542417), np.float64(33.86750759448066), np.float64(36.703679976105605))

# Bulk_Modulus = 79.37
# Young_Modulus = 132.26, 154.42, 157.32
# Poisson_Ratio = 0.15, 0.34, 0.16, 0.25, 0.10, 0.11
# Shear_Modulus = 38.79, 33.87, 36.70


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

plt.title("Bulk_Modulus = 79.37 \n Young_Modulus = 132.26, 154.42, 157.32 \n Poisson_Ratio = 0.15, 0.34, 0.16, 0.25, 0.10, 0.11 \n \n Elastic Stiffness Tensor (Cij)")
plt.tight_layout()
plt.savefig('elastic_stiffness_tensor2.png')

# plt.clf()
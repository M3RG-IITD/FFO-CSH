# same for both non cleaved (NC) and cleaved system
ca+t =  1.500
casl =  1.700
sc2  =  1.000
sc3  =  1.000
o*   = -0.820
h*   =  0.410

# 11M Bulk
NC_oc12 = -0.580
NC_oc13 = -0.930
NC_ocx  = -0.500
NC_oc14 = -0.710
NC_hoy  =  0.420

# 11H Bulk
NC_oc12 = -0.600
NC_oc13 = -0.930
NC_oc22 = -1.000
NC_oc14 = -0.690
NC_hoy  =  0.420

# 14M Bulk
NC_oc12 = -0.620
NC_oc13 = -0.930
NC_oc22 = -1.000
NC_oc14 = -0.690
NC_hoy  =  0.420


# 11M cleaved
oc12 = -0.560 # NC_oc12+0.02
oc13 = -0.940 # NC_oc13-0.01
ocx  = -0.580 # NC_ocx-0.08
oc14 = -0.670 # NC_oc14+0.04
hoy  =  0.400 # NC_hoy-0.02

# 11H cleaved
oc12 = -0.580 # NC_oc12+0.02
oc13 = -0.940 # NC_oc13-0.01
oc22 = -1.040 # NC_oc22-0.04
oc14 = -0.670 # NC_oc14+0.02
hoy  =  0.400 # NC_hoy-0.02

# 14M cleaved
oc12 = -0.580 # NC_oc12+0.04
oc13 = -0.940 # NC_oc13-0.01
oc22 = -1.080 # NC_oc22-0.08
oc14 = -0.670 # NC_oc14+0.02
hoy  =  0.400 # NC_hoy-0.02


######################################################################################################

# same for both non cleaved (NC) and cleaved system
ca+t    Ca  1.500
casl    Ca  1.700
sc2     Si  1.000
sc3     Si  1.000
o*      O  -0.820
h*      H   0.410

# 11M Bulk [cat-32, sc2-32, sc3-16, oc12-48, oc13-64, ocx-8, oc14-16, hoy-16]
oc12    O  -0.580
oc13    O  -0.930
ocx     O  -0.500
oc14    O  -0.710
hoy     H   0.420

# 11H Bulk [cat-32, casl-4, sc2-32, sc3-16, oc12-48, oc13-64, oc22-8, oc14-24, hoy-24]
oc12    O  -0.600
oc13    O  -0.930
oc22    O  -1.000
oc14    O  -0.690
hoy     H   0.420

# 14M Bulk [cat-32, casl-8, sc2-32, sc3-16, oc12-48, oc13-64, oc22-16, oc14-16, hoy-16]
oc12    O  -0.620
oc13    O  -0.930
oc22    O  -1.000
oc14    O  -0.690
hoy     H   0.420


# 11M cleaved
oc12    O  -0.560 # NC_oc12+0.02
oc13    O  -0.940 # NC_oc13-0.01
ocx     O  -0.580 # NC_ocx-0.08
oc14    O  -0.670 # NC_oc14+0.04
hoy     H   0.400 # NC_hoy-0.02

# 11H cleaved
oc12    O  -0.580 # NC_oc12+0.02
oc13    O  -0.940 # NC_oc13-0.01
oc22    O  -1.040 # NC_oc22-0.04
oc14    O  -0.670 # NC_oc14+0.02
hoy     H   0.400 # NC_hoy-0.02

# 14M cleaved
oc12    O  -0.580 # NC_oc12+0.04
oc13    O  -0.940 # NC_oc13-0.01
oc22    O  -1.080 # NC_oc22-0.08
oc14    O  -0.670 # NC_oc14+0.02
hoy     H   0.400 # NC_hoy-0.02





# charge constraint
cat = 1.500
casl = 1.700
sc2  = 1.000
sc3  = 1.000

oc12 = -0.580
oc13 = -0.930
ocx  = -0.500
oc14 = -0.710
hoy  =  0.420
cat*32 + sc2*32 + sc3*16 + oc12*48 + oc13*64 + ocx*8 + oc14*16 + hoy*16

oc12 = -0.600
oc13 = -0.930
oc22 = -1.000
oc14 = -0.690
hoy  =  0.420
cat*32 + casl*4 + sc2*32 + sc3*16 + oc12*48 + oc13*64 + oc22*8 + oc14*24 + hoy*24

oc12 = -0.620
oc13 = -0.930
oc22 = -1.000
oc14 = -0.690
hoy  =  0.420
cat*32 + casl*8 + sc2*32 + sc3*16 + oc12*48 + oc13*64 + oc22*16 + oc14*16 + hoy*16



# charge neutrality constraint
cat = 1.700
casl = 1.700
sc2  = 1.000
sc3  = 1.000
oc12 = -0.5
oc13 = -1.1
ocx  = -0.5
oc14 = -0.67
hoy  =  0.42
oc22 = -1.1
# 11M
(cat*32 + sc2*32 + sc3*16 + oc12*48 + oc13*64 + ocx*8 + oc14*16 + hoy*16) == 0.0
# 11H
(cat*32 + casl*4 + sc2*32 + sc3*16 + oc12*48 + oc13*64 + oc22*8 + oc14*24 + hoy*24) == 0.0
# 14M
(cat*32 + casl*8 + sc2*32 + sc3*16 + oc12*48 + oc13*64 + oc22*16 + oc14*16 + hoy*16) == 0.0



# Old charges correction
# 11M
oc12 = +0.02
oc13 = -0.01
ocx  = -0.08
oc14 = +0.04
hoy  = -0.02
oc12*48 + oc13*64 + ocx*8 + oc14*16 + hoy*16


# 11H
oc12 = +0.02
oc13 = -0.01
oc22  = -0.04
oc14 = +0.02
hoy  = -0.02
oc12*48 + oc13*64 + oc22*8 + oc14*24 + hoy*24

# 14M
oc12 = +0.04
oc13 = -0.01
oc22  = -0.08
oc14 = +0.02
hoy  = -0.02
oc12*48 + oc13*64 + oc22*16 + oc14*16 + hoy*16



# New charges correction 1
# 11M
oc12 = +0.02
oc13 = -0.01
ocx  = -0.04
oc14 = +0.02
hoy  = -0.02
oc12*48 + oc13*64 + ocx*8 + oc14*16 + hoy*16

# 11H
oc22  = -0.04
oc12*48 + oc13*64 + oc22*8 + oc14*24 + hoy*24

# 14M
oc12 = +0.03
oc22  = -0.05
oc12*48 + oc13*64 + oc22*16 + oc14*16 + hoy*16



# New charges correction 2
# 11M
oc12 = +0.04
oc13 = -0.02
ocx  = -0.08
oc14 = +0.04
hoy  = -0.04
oc12*48 + oc13*64 + ocx*8 + oc14*16 + hoy*16

# 11H
oc22  = -0.08
oc12*48 + oc13*64 + oc22*8 + oc14*24 + hoy*24

# 14M
oc12 = +0.05
oc22  = -0.07
oc12*48 + oc13*64 + oc22*16 + oc14*16 + hoy*16




# New charges correction 3
# 11M
oc12 = -0.05
ocx  = -0.05 #+0.12*8

oc13 = +0.04 #-0.03*64
oc22  = +0.04

oc14 = +0.04
hoy  = -0.04

oc12*48 + oc13*64 + ocx*8 + oc14*16 + hoy*16

# 11H
oc22  = +0.04
oc12*48 + oc13*64 + oc22*8 + oc14*24 + hoy*24

# 14M
oc12 = +0.05
oc22  = -0.07
oc12*48 + oc13*64 + oc22*16 + oc14*16 + hoy*16



# check
cat = 1.700
casl = 1.700
sc2  = 1.000
sc3  = 1.000
oc12 = -0.5
oc13 = -1.1
ocx  = -0.5
oc14 = -0.67
hoy  =  0.42
oc22 = -1.1


# increase/decrease charges
oc13 += -0.02
ocx  += -0.08
oc14 += +0.04
hoy  += -0.04
oc12 += +0.04
oc22  += -0.08

print(oc12, oc13, ocx , oc14, hoy , oc22)
# 14M
oc12 += +0.05
oc22  += -0.07
print(oc12, oc13, ocx , oc14, hoy , oc22)
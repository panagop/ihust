# OpenseespyGravity Salar

import openseespy.opensees as ops 
import numpy as np
import math
import opsvis as opsv
import matplotlib.pyplot as plt


# Δεδομένα      
# Μονάδες: N, mm, C
# --------------------------------

# Σκυρόδεμα 
# Πυρήνας Σκυροδέματος
fcC = -27.6     # [N/mm²] Θλιπτική αντοχή
ec0C = -0.0045  # [mm/mm] Παραμόρφωση 
fcUC = -21      # [N/mm²] Θλιπτική αντοχή σε θλίψη
ecuC = -0.015   # [mm/mm] Παραμόρφωση σε θλίψη
Ec = 2.5e4      # [N/mm²] Μέτρο Ελαστικότητας Σκυροδέματος                 # >>>


# Επικάλυψη Σκυροδέματος
fcU = -18           # [N/mm²] Θλιπτική αντοχή
ec0U = -0.0025      # [mm/mm] Παραμόρφωση
fcUU = -2           # [N/mm²] Θλιπτική αντοχή σε θλίψη
ecuU = -0.008       # [mm/mm] Παραμόρφωση σε θλίψη

# Χαλυβάς   
fy = 400                # [N/mm²] οριο διαρροής
Es = 2e5                 # [N/mm²] Μέτρο Ελαστικότητας
ey = fy/Es               # [mm/mm] Παραμόρφωση 
fu = 1.1818*fy           # [N/mm²] Θλιπτική Αντοχή
esu = ey*75.2            # [mm/mm] Παραμόρφωση σε Θλίψη
Esh = (fu - fy)/(esu - ey)
Bs = Esh / Es

# Διατομές 
# Υποστυλώματα
Bc = 500                 # [mm] Βάθος Διατομής
Hc = 500                 # [mm] Ύψος Διατομής
coverC = 50              # [mm] Επικάλυψη Σκυροδέματος
DIAc = 25                # [mm] Διάμετρος Ράβδου
AsC = np.pi*(DIAc**2)/4  # [mm²] Εμβαδόν Ράβδου

# Δοκός
Bb = 500                 # [mm] Βάθος Διατομής
Hb = 300                 # [mm] Ύψος Διατομής
coverB = 50              # [mm] Επικάλυψη Σκυροδέματος
DIAb = 18                # [mm] Διάμετρος Ράβδου
AsB = np.pi*(DIAb**2)/4  # [mm²] Εμβαδόν Ράβδου

# Διαστάσεις
LENGTH_COL = 3000        # [mm] Μήκος Υποστυλώματος
LENGTH_BM = 7000         # [mm] Μήκος Δοκού

# Model

ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3)

# Nodes
ops.node(1, 0.0, 0.0)
ops.node(2, LENGTH_BM, 0.0)
ops.node(3, 0.0, LENGTH_COL)
ops.node(4, LENGTH_BM, LENGTH_COL)

# Στηρίξεις
ops.fix(1, 1, 1, 1) 
ops.fix(2, 1, 1, 1)         

# Ορισμός Υλικών
# Σκυρόδεμα Πυρήνας
ops.uniaxialMaterial('Concrete01', 1, fcC, ec0C, fcUC, ecuC)

# Σκυρόδεμα Επικάλυψη
ops.uniaxialMaterial('Concrete01', 2, fcU, ec0U, fcUU, ecuU)

# Χαλυβάς
ops.uniaxialMaterial('Steel01', 3, fy, Es, Bs) 

# Διατομές

# Some variables derived from the parameters
y1 = Hc / 2.0
z1 = Bc / 2.0

ops.section('Fiber', 1)

# Concrete Core Fibers
ops.patch('rect', 1, 20, 5, coverC - y1, coverC - z1, y1 - coverC, z1 - coverC)

#  Οπλισμοί fibers (top, bottom, left, right)
ops.patch('rect', 2, 20, 5, -y1, z1 - coverC, y1, z1)
ops.patch('rect', 2, 20, 5, -y1, -z1, y1, coverC - z1)
ops.patch('rect', 2, 20, 5, -y1, coverC - z1, coverC - y1, z1 - coverC)
ops.patch('rect', 2, 20, 5, y1 - coverC, coverC - z1, y1, z1 - coverC)

# Οπλισμοί (left, middle, right)
ops.layer('straight', 3, 3, AsC, y1 - coverC, z1 - coverC, y1 - coverC, coverC - z1)
ops.layer('straight', 3, 2, AsC, 0.0, z1 - coverC, 0.0, coverC - z1)
ops.layer('straight', 3, 3, AsC, coverC - y1, z1 - coverC, coverC - y1, coverC - z1)

# Ορισμός στοιχείων Υποστυλωμάτων

# Γεωμετρία

ops.geomTransf('PDelta', 1) 

# Αριθμός ολοκλήρωσης κατά μήκος του στοιχείου
np = 5 

# Ολοκλήρωση Lobatto
ops.beamIntegration('Lobatto', 1, 1, np)

# Δημιουργία Στοιχείων Στύλων (Beam-Column Elements)
ops.eleType = 'forceBeamColumn'
ops.element(ops.eleType, 1, 1, 3, 1, 1)
ops.element(ops.eleType, 2, 2, 4, 1, 1)    

# Ορισμός Διατομής Δοκού
ops.geomTransf('Linear', 2)

ops.element('elasticBeamColumn', 3, 3, 4, Bb*Hb, Ec, (Bb*Hb**3)/12, 2)

# Φορτία

#  a parameter for the axial load

#  a parameter for the axial load (με βάση τον Ευροκώδικα 2)            # >>>
Ag = Bc * Hc                                                            # >>>      
nBars = 8  # 3+2+3                                                      # >>>                                                
As_tot = nBars * AsC                                                    # >>>
fpc = abs(fcC)                                                          # >>> 
P0_col = 0.85 * fpc * (Ag - As_tot) + fy * As_tot                       # >>>
P = 0.10 * P0_col                                                       # >>>
print("Αξονικό φορτίο:", P, "N")                                        # >>>



# Create a Plain load pattern with a Linear TimeSeries
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

# Create nodal loads at nodes 3 & 4
#    nd  FX,  FY, MZ
ops.load(3, 0.0, -P, 0.0)
ops.load(4, 0.0, -P, 0.0)

# Τελος δημιουργίας μοντέλου


# Οπτικοποίηση μοντέλου
opsv.plot_model(node_labels=1, element_labels=1, fig_wi_he=(20, 15))   # >>>
plt.title('Μοντέλο Πλαισίου')                                          # >>>
plt.grid(False)                                                        # >>>
plt.show()                                                             # >>>


# ------------------------------
# Start of analysis generation
# ------------------------------

# Create the system of equation, a sparse solver with partial pivoting
ops.system('BandGeneral')

# Create the constraint handler, the transformation method
ops.constraints('Transformation')

# Create the DOF numberer, the reverse Cuthill-McKee algorithm
ops.numberer('RCM')

# Create the convergence test, the norm of the residual with a tolerance of
# 1e-12 and a max number of iterations of 10
ops.test('NormDispIncr', 1.0e-12, 10, 3)

# Create the solution algorithm, a Newton-Raphson algorithm
ops.algorithm('Newton')

# Create the integration scheme, the LoadControl scheme using steps of 0.1
ops.integrator('LoadControl', 0.1)

# Create the analysis object
ops.analysis('Static')

# ------------------------------
# End of analysis generation
# ------------------------------


# ------------------------------
# Finally perform the analysis
# ------------------------------

# perform the gravity load analysis, requires 10 steps to reach the load level
ops.analyze(10)

# Print out the state of nodes 3 and 4
# print node 3 4

# Print out the state of element 1
# print ele 1

u3 = ops.nodeDisp(3, 2)
u4 = ops.nodeDisp(4, 2)

print("==========================")
print("Node 3 displacement in Y direction:", u3,'mm')
print("Node 4 displacement in Y direction:", u4,'mm')

print("==========================")


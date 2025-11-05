# OpenseespyPushover Analysis

import openseespy.opensees as ops  
import OpenseespyGravity
import numpy as np
import matplotlib.pyplot as plt



print("Gravity Analysis Completed")


# Set the gravity loads to be constant & reset the time in the domain
ops.loadConst('-time', 0.0)

# ----------------------------------------------------
# End of Model Generation & Initial Gravity Analysis
# ----------------------------------------------------


# ----------------------------------------------------
# Start of additional modelling for lateral loads
# ----------------------------------------------------

# Define lateral loads
# --------------------

# Set some parameters
F = 10  # Reference lateral load

# Set lateral load pattern with a Linear TimeSeries
ops.pattern('Plain', 2, 1)

# Create nodal loads at nodes 3 & 4
#    nd    FX  FY  MZ
ops.load(3, F, -F, 0.0)
ops.load(4, F, -F, 0.0)

# ----------------------------------------------------
# End of additional modelling for lateral loads
# ----------------------------------------------------


# ----------------------------------------------------
# Start of modifications to analysis for push over
# ----------------------------------------------------

# Set some parameters
dU = 1  # Displacement increment

# Change the integration scheme to be displacement control
#                             node dof init Jd min max
ops.integrator('DisplacementControl', 3, 1, dU, 1, dU, dU)

# ----------------------------------------------------
# End of modifications to analysis for push over
# ----------------------------------------------------


# ------------------------------
# Start of recorder generation
# ------------------------------

# Stop the old recorders by destroying them
# remove recorders

# Create a recorder to monitor nodal displacements
# recorder Node -file node32.out -time -node 3 4 -dof 1 2 3 disp

# Create a recorder to monitor element forces in columns
# recorder EnvelopeElement -file ele32.out -time -ele 1 2 forces

# --------------------------------
# End of recorder generation
# ---------------------------------


# ------------------------------
# Finally perform the analysis
# ------------------------------

# Set some parameters
maxU = 600  # Max displacement
currentDisp = 0.0
ok = 0

# Step-by-step logging (terminal + CSV)                                 # >>>
step = 0                                                                # >>>
print_every = 10  # βάλε 1 για κάθε βήμα                                # >>>
log = open('pushover_steps.csv', 'w', encoding='utf-8')                 # >>>
log.write('step,disp_mm,base_shear_N,percent\n')                        # >>>
print(f"{'Step':>6} {'Disp[mm]':>12} {'BaseShear[N]':>16} {'%':>6}")    # >>>


# Λίστες για αποθήκευση δεδομένων                                       # >>>
disp_hist = []                                                          # >>>
shear_hist = []                                                         # >>>        

ops.test('NormDispIncr', 1.0e-12, 1000)
ops.algorithm('ModifiedNewton', '-initial')

while ok == 0 and currentDisp < maxU:

    ok = ops.analyze(1)

    # if the analysis fails try initial tangent iteration
    if ok != 0:
        print("modified newton failed")
        break
    # print "regular newton failed .. lets try an initail stiffness for this step"
    # test('NormDispIncr', 1.0e-12,  1000)
    # # algorithm('ModifiedNewton', '-initial')
    # ok = analyze(1)
    # if ok == 0:
    #     print "that worked .. back to regular newton"

    # test('NormDispIncr', 1.0e-12,  10)
    # algorithm('Newton')

    currentDisp = ops.nodeDisp(3, 1)

    # Υπολογισμός Base Shear                                                       # >>>
    ops.reactions()                                                    
    base_shear = -(ops.nodeReaction(1, 1) + ops.nodeReaction(2, 1))                # >>>

    # Αποθήκευση δεδομένων                                             
    disp_hist.append(currentDisp)                                                  # >>>    
    shear_hist.append(base_shear)                                                  # >>>

    # Εκτύπωση και καταγραφή βήματος                                               # >>>
    step += 1                                                                      # >>>
    percent = 100.0 * currentDisp / maxU                                           # >>>
    if step % print_every == 0 or step == 1:                                       # >>>
        print(f"{step:6d} {currentDisp:12.3f} {base_shear:16.2f} {percent:6.1f}")  # >>>
    log.write(f"{step},{currentDisp:.6f},{base_shear:.6f},{percent:.3f}\n")        # >>>

    

results = open('results.out', 'a+')

if ok == 0:
    results.write('PASSED : OpenseespyPushover.py\n')
    print("Passed!")
else:
    results.write('FAILED : OpenseespyPushover.py\n')
    print("Failed!")

results.close()

log.close()  # κλείσιμο του CSV                                                    # >>>

# Print the state at node 3
# print node 3


print("==========================")



# ========== ΔΗΜΙΟΥΡΓΙΑ ΓΡΑΦΗΜΑΤΟΣ PUSHOVER ==========                                       # >>>

# Δημιουργία γραφήματος                                                                      # >>>
plt.figure(figsize=(10, 7))                                                                  # >>>
plt.plot(disp_hist, shear_hist, '-b', linewidth=2, label='Pushover Curve')                   # >>>
plt.xlabel('Displacement in X [mm]', fontsize=12)                                            # >>>
plt.ylabel('Base Shear [N]', fontsize=12)                                                    # >>>
plt.title('Pushover Analysis - Base Shear vs Displacement', fontsize=14, fontweight='bold')  # >>>
plt.grid(True, alpha=0.3)                                                                    # >>>
plt.legend()                                                                                 # >>>
plt.tight_layout()                                                                           # >>>
plt.savefig('pushover_curve.png', dpi=300)                                                   # >>>
plt.show()                                                                                   # >>>

# Αποθήκευση δεδομένων σε αρχείο                                                             # >>>
np.savetxt('pushover_data.txt',                                                              # >>>
    np.column_stack((disp_hist, shear_hist)),                                                # >>>
        header='Displacement[mm] BaseShear[N]',                                              # >>>
        fmt='%.6f')                                                                          # >>>

print(f"Max Displacement: {max(disp_hist):.2f} mm")                                          # >>>
print(f"Max Base Shear: {max(shear_hist):.2f} N")                                            # >>>
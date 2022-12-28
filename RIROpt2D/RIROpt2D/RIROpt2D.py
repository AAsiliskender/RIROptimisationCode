###### -- Global Optimisation Code for Resin Injection Repair Reduced-Order Simulation
###### -- By Ahmed Asiliskender, initial write date 03 Sept 2021 
###### -- The 'Global' refers to this code being overarching rather than seeking the
###### global optimum.

# -- STARCCM_COMMAND is the cmd terminal's string that opens STARCCM (i.e. starccm+ for starccm+.exe.)
# -- STARCCM_DRIVE and directory indicate the location (and drive) of the STAR-CCM+ executable.
# -- STARCCM_DIR is the path of the directory containing the .sim file to be used. Provide the full directory
# -- SIM_FILE_DIR is the directory of the target .sim file.
# -- SIM_FILE_NAME is the name of the .sim file to be used (with the extension).
# -- MACRO_FILE_NAME is the Javascript file that is used by STAR-CCM+ to automate processes (cannot be empty ""
# as optimisation requires cycles of simulation).
# -- MACRO_DIR is the path of directory containing the macro file. If empty, it assumes the same value
# the simdir variable. Provide the full directory, if at all.
# -- MACRO_CHANGEVARS is the name of the variables to be changes in the macro file.
# -- MACRO_LINES is the line number(s) where macro_changevar will be applied.
# -- NUMOFCORES is the CPU/node count setting in STAR-CCM+, (it states 'cores' in the GUI but it appears
# to actually be threads which is generally 2 per CPU core.)
# -- GEOMETRY_DIR is the directory containing the porosity map.
# -- GEOMETRY_FILE is the porosity map file. 
# -- PWONDEMANDKEY is the Power-on-Demand key required to run STAR-CCM+.
# -- PUSHBULLETTOKEN is the token for creating push notifications to indicate completion (may not be used.)

print("~~~~~~~~~~~~~~~~~~~~~~~~~")

version = "1.0.1"

print("Initialising Global Optimisation Code for RIR v. " + version + ".")

import time
import numpy
import os
import scipy
from scipy import optimize
from scipy.optimize import minimize_scalar
from scipy.optimize import minimize

# Tick
starttime=time.time()
# Start time statement
print ("Optimisation Start Time: %s" % time.ctime())

# May be removed if import becomes automatic
print("Importing STARCCM module")
from STAR_CCM import STARCCM

print("Importing PRAXIS module")
from PRAXIS import PRAXIS

# Base Directory (of this file), needed to call submodules easily
base_dir_path = os.path.dirname(os.path.realpath(__file__))

# Change current working directory to where this file is
os.chdir(base_dir_path)
######~~~~~~~~~~~~~~~~~~~~~~~~~~~######
###### Key Parameters (user-set) ######
######~~~~~~~~~~~~~~~~~~~~~~~~~~~######

### STAR-CCM+ Execution Parameters (for running the script)
starccm_command = "starccm+"
starccm_drive = "C:" # Provide the drive X location as "X:"
starccm_dir = "C:\Program Files\Siemens/15.04.008-R8\STAR-CCM+15.04.008-R8\star/bin"
# ^ Provide forwardslash over backslash where possible and include drive location
numofcores = 7
# ^ Can be int., but will be converted to str., is actually the number of processes (threads)
pwondemandkey = "YA5cJ0s8ywF51ihTkOmQTg"

# Sim information
sim_file_dir = "D:\Ahmeds_Files\PhD\Simulations\Validation\QUB-C3"
sim_file_name = "QUB-C3.sim" # Include file ext.

### Macro run and modification parameters
macro_file_name = "automation_macro.java"
macro_dir = "D:/Ahmeds_Files/PhD/Simulations/Optimisation/Codes/OptimisationFiles" #If empty, put [], will assume simfiledir value.
macro_changevars = ["expressionReport_ventx1","expressionReport_venty1","expressionReport_ventx2","expressionReport_venty2","expressionReport_ventx3","expressionReport_venty3"]#,"expressionReport_injectionx1","expressionReport_injectiony1","expressionReport_injectionx2","expressionReport_injectiony2","expressionReport_injectionx3","expressionReport_injectiony3","expressionReport_injectionx4","expressionReport_injectiony4","expressionReport_injectionx5","expressionReport_injectiony5"]#"expressionReport_ventx2","expressionReport_venty2", "expressionReport_injectionx1","expressionReport_injectiony1"]
# ^ Can reduce no. of vars changed by reducing this only, but also remove macro_line args.
# Save File (Simulation, Images, then Datasets)
macro_savedirs = ["D:/Ahmeds_Files/PhD/Simulations/Optimisation/Codes/OptimisationFiles/SaveFiles","D:/Ahmeds_Files/PhD/Simulations/Optimisation/Codes/OptimisationFiles/Images","D:/Ahmeds_Files/PhD/Simulations/Optimisation/Codes/OptimisationFiles/Images2","D:/Ahmeds_Files/PhD/Simulations/Optimisation/Codes/OptimisationFiles/Data"]
# Don't have / at end of directory
macro_savenames = ["1_Validation_Opt_C3_auto","1_Validation_Opt_Flow_C3","1_Validation_Opt_Flow_Closeup_C3","1_Validation_C3_Fill_eff_dataset"]
macro_saveextensions = [".sim",".png",".png",".csv"]
# Only write the variable name (i.e. expressionReport_1) whos values are to be edited.
macro_lines = [40,45,50,55,60,65]#,70,75,80,85,90,95,100,105,110,115] # Count 1st line as line 1, not 0. Use int. not str.
macro_savelines=[470,453,454,466] # Save File, Scene Image (Full), Scene Image (Closeup), CSV

### Feasbility Check Parameters
geometry_dir = "D:\Ahmeds_Files\PhD\Simulations\Optimisation\Codes\OptimisationFiles"
geometry_file = "QUB-C3-Porosity.csv"
porosity_filter = 0.015 # Min. porosity filter applied in STAR-CCM+ #0.01 a1 0.012 b5 0.015 c3
#^ Make sure to change porosity limits at the automation macro script

### Simulation and Optimisation Parameters
# Full optimisation settings
# Leave variable empty (i.e. as []) if not to be used
port_initial = [[]] # Coordinates in STAR-CCM+, in mm [x, y]
vent_initial = [[-6, 11], [5, 17], [16,0]] # [[x1, y1,], [x2, y2], ...]

# Reduced optimisation settings, reduces 2 coord/hole to 1 (along line)
reduced_opt = 0 # 1 - Reduced optimisation on, 0 - Off
red_opt_line_angle = [315,270,225,180,135,90,45,0] 
# ^Reduced optimisation line angle in degrees (against x-axis, anticlockwise) to slide hole location on (ONE FOR EACH HOLE)
red_opt_line_center = [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]] # Vent then Port
# ^(X,Y) coordinates of the centre of the reduced optimisation line in mm -- Can override directly later
simplex_size=[6,1,5]
simplex_override = 1 # 1 - Override (for manual input), 0 - no override

# Distance (mm) away from line center
red_port_initial = [10, 18, 6, 14, 15]#() # (v1, v2, ...), use tuple (or int/float) not list
red_vent_initial = [28, 10, 6] # Use same format for both


# General optimisation settings
step_tol = 1 # Distance tolerance to convergence. 
opt_tolerance = 0.025 # Tolerance to objective function minima for convergence. 

### Below are non-critical parameters (0 verb is no verbosity)
STAR_verb = 1 # Verbosity of STARCCM.py
macro_verb = 0 # Verbosity of MacroEdit.py
feas_verb = 1 # Verbosity of FeasibilityCheck.py, 0 none, 1 low, 2+ high
praxis_verb = 1 # PRAXIS verbosity, 1-4 low to high
red_opt_verb = 0 # Reduced Optimiser verbosity
pushbullettoken = "o.Xm8HY3DXPnal9STDab4cfy0tYnS00Tt2"
defuserpswd = "ChangeToYOURS"

######~~~~~~~~~~~~~~~~~~~~~~~~~~~######
######~~~~~~~~~~~~~~~~~~~~~~~~~~~######
######~~~~~~~~~~~~~~~~~~~~~~~~~~~######

numofcores = str(numofcores)

### Storing Optimisation and Parameter Data
# Optimisation Data
opt_cycle_count = 0
optfile = open("OptimisationData//OptCycleCounter.txt", "w")
optfile.write(str(opt_cycle_count))
optfile.close()

# Parameters for STAR-CCM+
star_param_file = open("OptimisationData//STARCCMParamFile.txt", "w")
star_paramsum = [starccm_command, starccm_drive, starccm_dir, sim_file_dir, sim_file_name, macro_dir, macro_file_name, numofcores, pwondemandkey, pushbullettoken, STAR_verb]
star_param_file.write(str(star_paramsum))
star_param_file.close()

# Parameters for Macro Editing
macro_param_file = open("OptimisationData//MacroEditParamFile.txt", "w")
macro_paramsum = [macro_dir, macro_file_name, macro_lines, macro_changevars, macro_savedirs, macro_savenames, macro_savelines, macro_saveextensions, macro_verb]
macro_param_file.write(str(macro_paramsum))
macro_param_file.close()

# Parameters for the Feasibility checker
feas_param_file = open("OptimisationData//FeasibilityParamFile.txt", "w")
feas_paramsum = [geometry_dir, geometry_file, porosity_filter, feas_verb]
feas_param_file.write(str(feas_paramsum))
feas_param_file.close()

# Parameters for Optimisation
red_opt_param_file = open("OptimisationData//ReducedOptimisationParamFile.txt", "w")
# Here we put full or reduced optimisation parameters
if reduced_opt != 1:
    red_opt_paramsum = [reduced_opt, red_opt_verb]
else:
    red_opt_paramsum = [reduced_opt, red_opt_line_center, red_opt_line_angle, red_opt_verb]
red_opt_param_file.write(str(red_opt_paramsum))
red_opt_param_file.close()

#########

if reduced_opt == 1:
    initial_vals = red_vent_initial + red_port_initial
else:
    if port_initial != [[]]:
        initial_vals = vent_initial + port_initial
    else:
        initial_vals = vent_initial
hole_count = len(initial_vals)
ex_vals=(1,)
print(initial_vals)
#print(len(initial_vals))

#if reduced_opt != 1: # Bad input check (full optimisation)
#    if (hole_count % 2) != 0:
#        badholeinput="The number of initial hole coordinate inputs is odd, should be even (X,Y)!"
#        raise Exception(badholeinput)

# Used to debug/test and do single runs
#STARCCM.STARCCM(initial_vals,hole_count)

# For jac
#fprime=lambda x,*args: optimize.approx_fprime(x, STARCCM.STARCCM, 0.5,hole_count)

# For initial simplex (important for Nelder-Mead, to have a good scale)
if simplex_override == 1: # Simplex override check (simplex needs to be size [N, N+1], i.e N rows x (N+1) cols)

    initial_simplex= [[-6, 11, 5, -17, 16, 0], [-7, -6, 1, 12, 15, -14], [-13, 18, 5, -17, 16, 0], [-7, -6, 1, 12, 21, -23], [-7, -6, 1, 12, 26, -20], [-7, -6, -6, 11, 26, -20], [-7, -6, 16, 0, 21, -23]]

    #[[28, 10, 6, 10, 18, 6, 14, 15], [28, 10, 6, 10, 18, 4.5, 14, 15], [28, 10, 6, 7, 18, 6, 14, 15], [25, 8, 5, 9, 16, 5, 12, 13], [30, 11, 7, 11, 19, 7, 15, 16], [26, 9, 5, 9, 17, 5, 13, 14], [12, 5, 3, 5, 9, 3, 7, 7], [14, 10, 6, 10, 18, 6, 14, 15], [28, 10, 6, 10, 9, 6, 14, 15]]
else:
    initial_simplex=[initial_vals]
    for i in range(0,len(initial_vals)):
        simplex_vals=[]
        for j in range(0,len(simplex_size)):
            simplex_vals.append(initial_vals[i]+simplex_size[j])
        initial_simplex.append(simplex_vals)

    
#print(initial_simplex)

print("Calling Optimiser module...")
#[reslt] = scipy.optimize.brent(STARCCM.STARCCM,args=(hole_count,),brack=(0,1),tol=opt_tolerance,full_output=True,maxiter=30)
#reslt = scipy.optimize.minimize(STARCCM.STARCCM,(numpy.array(initial_vals)),args=(hole_count),method='CG',jac=None,tol=None,options={'eps': 0.5, 'maxiter':30, 'disp': True, 'return_all': True, 'finite_diff_rel_step': None})
#reslt = scipy.optimize.minimize(STARCCM.STARCCM,(numpy.array(initial_vals)),args=(hole_count),method='Newton-CG',jac=fprime,hess=None,hessp=None,tol=None,callback=None,options={'xtol':0.05,'eps': 0.5, 'maxiter':20, 'disp': True, 'return_all': True})
reslt = scipy.optimize.minimize(STARCCM.STARCCM,(numpy.array(initial_vals)),args=(hole_count),method='Nelder-Mead',bounds=None,tol=None,callback=None,options={'maxiter':120,'return_all':True,'initial_simplex':initial_simplex,'xatol':step_tol,'fatol':opt_tolerance,'adaptive':True})
#reslt = scipy.optimize.minimize(STARCCM.STARCCM,(numpy.array(initial_vals)),args=(hole_count),method='Powell',bounds=None,tol=None,callback=None,options={'direc':None, 'maxiter':30,'xatol':0.005,'fatol':0.002, 'return_all': True})
#reslt = scipy.optimize.minimize(STARCCM.STARCCM,(numpy.array(initial_vals)),args=(hole_count),method='BFGS',jac=fprime,tol=None,callback=None,options={'eps':0.5, 'disp':True,'return_all': True,'finite_diff_rel_step': 0.5})
print("Solution (array): %s" % reslt.x)
print("Solution success: %s" % reslt.success)
print("Solution message: %s" % reslt.message)

#(-30,50)
#print("Calling PRAXIS module...") 
#PRAXIS.praxis(opt_tolerance,opt_max_step,hole_count,praxis_verb,numpy.array(initial_vals),STARCCM.STARCCM)


# Tock
endtime=time.time()
print ("Optimisation End Time: %s" % time.ctime())

totaltime=endtime-starttime
print ("Total Time Elapsed: ", ("%.2f" % (totaltime/3600)) + " hours, or ", ("%.2f" % (totaltime/60)) + " minutes, or ", ("%.2f" % totaltime) + " seconds.")
print("~~~~~~~~~~~~~~~~~~~~~~~~~")

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

version = "0.0.1"

print("Initialising Global Optimisation Code for RIR v. " + version + ".")

import time
import numpy
import os

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

######~~~~~~~~~~~~~~~~~~~~~~~~~~~######
###### Key Parameters (user-set) ######
######~~~~~~~~~~~~~~~~~~~~~~~~~~~######

### STAR-CCM+ Execution Parameters (for running the script)
starccm_command = "starccm+"
starccm_drive = "C:" # Provide the drive X location as "X:"
starccm_dir = "C:\Program Files\Siemens/15.04.008-R8\STAR-CCM+15.04.008-R8\star/bin"
# ^ Provide forwardslash over backslash where possible and include drive location
numofcores = 12
# ^ Can be int., but will be converted to str., is actually the number of processes (threads)
pwondemandkey = "EsZx3xudjt4dptN3dl0GJg"

# Sim information
sim_file_dir = "D:/Ahmeds_Files/PhD/Simulations/Optimisation"
sim_file_name = "1-Optimisation.sim" # Include file ext.

### Macro run and modification parameters
macro_file_name = "automation_macro.java"
macro_dir = "D:/Ahmeds_Files/PhD/Simulations/Optimisation/Codes/OptimisationFiles" #If empty, put [], will assume simfiledir value.
macro_changevars = ["expressionReport_ventx1","expressionReport_venty1"]#"expressionReport_ventx2","expressionReport_venty2", "expressionReport_injectionx1","expressionReport_injectiony1"]
# ^ Can reduce no. of vars changed by reducing this only, but also remove macro_line args.
# Save File (Simulation, Images, then Datasets)
macro_savedirs = ["D:/Ahmeds_Files/PhD/Simulations/Optimisation/Codes/OptimisationFiles/SaveFiles","D:/Ahmeds_Files/PhD/Simulations/Optimisation/Codes/OptimisationFiles/Images","D:/Ahmeds_Files/PhD/Simulations/Optimisation/Codes/OptimisationFiles/Data"]
# Don't have / at end of directory
macro_savenames = ["1-Optimisation_auto","Optimisation_Flow","Fill_eff_dataset"]
macro_saveextensions = [".sim",".png",".csv"]
# Only write the variable name (i.e. expressionReport_1) whos values are to be edited.
macro_lines = [40,45]#,50,55] # Count 1st line as line 1, not 0. Use int. not str.
macro_savelines=[383,366,379] # Save File, Scene Image, CSV

### Feasbility Check Parameters
geometry_dir = "D:\Ahmeds_Files\PhD\Simulations\Optimisation\Codes\OptimisationFiles"
geometry_file = "QUB1-CScan-Porosity.csv"
porosity_filter = 0.08 # Min. porosity filter applied in STAR-CCM+

### Simulation and Optimisation Parameters
# Full optimisation settings
# Leave variable empty (i.e. as []) if not to be used
port_initial = [[]] # Coordinates in STAR-CCM+, in mm [x, y]
vent_initial = [[]] # [[x1, y1,], [x2, y2], ...]

# Reduced optimisation settings, reduces 2 coord/hole to 1 (along line)
reduced_opt = 1 # 1 - Reduced optimisation on, 0 - Off
red_opt_line_angle = 135 
# ^Reduced optimisation line angle in degrees (against x-axis, anticlockwise) to slide hole location on
red_opt_line_center = [4,5]
# ^(X,Y) coordinates of the centre of the reduced optimisation line in mm
red_port_initial = [] # Distance (mm) away from line center
red_vent_initial = [49] # [v1, v2, ...], use list not int


# General optimisation settings
opt_max_step = 50 # Have this value just under the max. domain length (in mm). 
opt_tolerance = 0.1 # Tolerance to objective function minima, no need to change. 

### Below are non-critical parameters (0 verb is no verbosity)
STAR_verb = 1 # Verbosity of STARCCM.py
macro_verb = 0 # Verbosity of MacroEdit.py
feas_verb = 3 # Verbosity of FeasibilityCheck.py, 0 none, 1 low, 2+ high
praxis_verb = 1 # PRAXIS verbosity, 1-4 low to high
red_opt_verb = 1 # Reduced Optimiser verbosity
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
    initial_vals = vent_initial + port_initial
hole_count = len(initial_vals)

if reduced_opt != 1: # Bad input check (full optimisation)
    if (hole_count % 2) != 0:
        badholeinput="The number of initial hole coordinate inputs is odd, should be even (X,Y)!"
        raise Exception(badholeinput)

# Used to debug/test and do single runs
STARCCM.STARCCM(initial_vals,hole_count)


print("Calling PRAXIS module...") 
#PRAXIS.praxis(opt_tolerance,opt_max_step,hole_count,praxis_verb,numpy.array(initial_vals),STARCCM.STARCCM)




# Tock
endtime=time.time()
print ("Optimisation End Time: %s" % time.ctime())

totaltime=endtime-starttime
print ("Total Time Elapsed: ", ("%.2f" % (totaltime/3600)) + " hours, or ", ("%.2f" % (totaltime/60)) + " minutes, or ", ("%.2f" % totaltime) + " seconds.")
print("~~~~~~~~~~~~~~~~~~~~~~~~~")

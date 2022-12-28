from asyncore import read
from distutils.log import error
from logging import exception
import sys
import os
import glob
import time
import subprocess
from typing import Tuple

def STARCCM(positions,poscount,Verb=0):
    # -- POSITIONS provides the coordinate(s) of the hole(s).
    # -- POSCOUNT provides the number of coordinates provided by POSITIONS
    # -- VERB is the verbosity, default 0 is low verbosity.

    # -- Make sure to note that the directories should be typed appropriately in order run in shell. Forward
    # slashes may be preferred to avoid misreads.
    # -- Input all arguments in string.
    # -- STARCCM calls FeasibilityChecker followed by MacroEdit and is called by ObjectiveFunction
    
    print("------------------")
    print("Initialising STARCCM Module:")
    print("Inputted position(s): %s" % positions.tolist())
    import sys
    import os
    import glob
    import time
    import subprocess
    import ast
    import numpy
    from STAR_CCM import MacroEdit
    from STAR_CCM import FeasibilityCheck
    from STAR_CCM import ReducedOptChecker
    from STAR_CCM import ObjectiveFunction

    # Tick
    simstarttime=time.time()

    print("Reading External Arguments:")
    # Read parameter file to retrieve necessary parameters
    parameterfile = open("OptimisationData//STARCCMParamFile.txt", "r")
    parameterdata = parameterfile.readlines()
    parameters = ast.literal_eval(parameterdata[0])
    parameterfile.close()


    optcycle=0 #Initialisation
    optread = open("OptimisationData//OptCycleCounter.txt", "r")
    optcycle = int(optread.read()) + 1
    optread.close()
    optwrite = open("OptimisationData//OptCycleCounter.txt", "w")
    optwrite.write(str(optcycle))
    optwrite.close()
    
    # Start time statement
    print ("Batch Simulation, Cycle Number %s" % optcycle + " Start Time: %s" % time.ctime())
    
    
    
    # Taking extra args from parameter file and converting to string 
    executable = "%s" % parameters[0]
    drive = "%s" % parameters[1]
    directory = "%s" % parameters[2]
    simdir = "%s" % parameters[3]
    simname = "%s" % parameters[4]
    macrodir = "%s" % parameters[5]
    macro = "%s" % parameters[6]
    threads = str(parameters[7])
    podkey = "%s" % parameters[8]
    pushtoken = "%s" % parameters[9]
    Verb = parameters[10]

    if pushtoken!=[]:
        pushtoken = "%s" % pushtoken
    else:
        print("Notice: No Push token used.")
    
    if Verb != 0:
        print("--- Parameters read from file:")
        print(parameters)

    ###
    ##### Repeat Sim Check PART 1 - 1st optcycle position check
    ###
    expedite=True
    repeating=False
    if expedite==True:
        if optcycle ==1:
            old_position_history = open("OptimisationData//PositionParamHistory.txt", "r")
            old_pos = ast.literal_eval(old_position_history.readlines()[0])
            if tuple(old_pos[0]) == tuple(positions):
                print('Same first attempt')
                repeating=True
            old_position_history.close()
    ###
    #####
    ###

    # Save positions called just before starting sequence:
    if Verb != 0:
        print("Saving called location parameter(s).")
    if optcycle == 1:
        position_history = open("OptimisationData//PositionParamHistory.txt", "w")
    else:
        position_history = open("OptimisationData//PositionParamHistory.txt", "a")
    position_history.write(str(positions.tolist())+",")
    position_history.close()

    # Call the reduced optimiser
    positions = ReducedOptChecker.ReducedOptChecker(positions) 
    # Reduced opt either returns normal positions, otherwise applies reduced opt.

    # Call the feasibility checker/enforcer here (also converts values from mm to m for STAR-CCM+)
    [feasible_positions,penalty] = FeasibilityCheck.FeasibilityCheck(positions)

    # Penalty Check (if exists, returned value is here)
    if penalty != 0:
        fill_eff_read = open("OptimisationData//FillEffHistory.txt", "r")
        last_valid_feff = ast.literal_eval(fill_eff_read.readlines()[0])
        print("Penalty detected. Penalty Value: %s" % penalty)
        print("Last (Valid) Fill Efficiency: %s" % last_valid_feff[-1])
        #penalised_feff = last_valid_feff[-1]*(1-penalty)
        penalised_feff = round(-penalty,2)
        print("Penalised Filling Efficiency: %s" % penalised_feff)
        
        # Write into history (inc. penalised vals)
        penalty_fill_eff_history = open("OptimisationData//PenalisedFillEffHistory.txt", "a")
        penalty_fill_eff_history.write(str(penalised_feff)+", ")
        penalty_fill_eff_history.close()

        # State Obj Fct and Fill Eff values
        print("Objective Function value: %.5f" % (1-penalised_feff/100) )
        print("Fill Efficiency obtained: %.2f" % (penalised_feff) + "%" )

        # Tock
        simendtime=time.time()
        # End Time Statement
        print ("Simulation Skipped (Penalised). Cycle Number %s" % optcycle + " End Time: %s" % time.ctime())

        simtotaltime=simendtime-simstarttime
        # Total Time Statement
        print ("Total Penalised Simulation Process Time Elapsed (Cycle Number %s" % optcycle + "): ", ("%.2f" % (simtotaltime/3600)) + " hours, or ", ("%.2f" % \
                     (simtotaltime/60)) + " minutes, or ", ("%.2f" % simtotaltime) + " seconds.")
        print("------------------")
        return 1-penalised_feff/100


    # Macro Edit call, returns the filling efficiency .csv file (with directory)
    macrocall_and_filleff_file = MacroEdit.MacroEdit(feasible_positions)
    if Verb > 1:
        print("Fill efficiency file saved at: " + macrocall_and_filleff_file)

    ###
    ##### Repeat Sim Check PART 2 - Use existing sim result
    ###
    if repeating == True:
        old_fill_eff = open("OptimisationData//FillEffHistory.txt", "r")
        old_feff = ast.literal_eval(old_fill_eff.readlines()[0])
        
        if old_feff == float:
            print("Objective Function value: %.5f" % (1-old_feff/100) )
            print("Fill Efficiency obtained: %.2f" % (old_feff) + "%" )
        else:
            print("Objective Function value: %.5f" % (1-old_feff[0]/100) )
            print("Fill Efficiency obtained: %.2f" % (old_feff[0]) + "%" )

        # Tock
        simendtime=time.time()
        # End Time Statement
        print ("Simulation Skipped (Already Done). Cycle Number %s" % optcycle + " End Time: %s" % time.ctime())

        simtotaltime=simendtime-simstarttime
        # Total Time Statement
        print ("Total Skipped Simulation Process Time Elapsed (Cycle Number %s" % optcycle + "): ", ("%.2f" % (simtotaltime/3600)) + " hours, or ", ("%.2f" % \
                     (simtotaltime/60)) + " minutes, or ", ("%.2f" % simtotaltime) + " seconds.")
        print("------------------")

        if optcycle == 1:
            fill_eff_history = open("OptimisationData//FillEffHistory.txt", "w")
            penalty_fill_eff_history = open("OptimisationData//PenalisedFillEffHistory.txt", "w")
        else:
            fill_eff_history = open("OptimisationData//FillEffHistory.txt", "a")
            penalty_fill_eff_history = open("OptimisationData//PenalisedFillEffHistory.txt", "a")

        if old_feff == float:
            fill_eff_history.write(str(old_feff)+", ")
            penalty_fill_eff_history.write(str(old_feff)+", ")
        else:
            fill_eff_history.write(str(old_feff[0])+", ")
            penalty_fill_eff_history.write(str(old_feff[0])+", ")
        fill_eff_history.close()
        penalty_fill_eff_history.close()

        if old_feff == float:
            return (1-old_feff/100)
        else:
            return (1-old_feff[0]/100)
    ###
    #####
    ###

    ### STAR-CCM+ CALL
    #calling= drive + " & cd " + directory + " & " + executable + " -batch " + macrodir + "/" + macro + " -power -np " + threads + \
    #            " " + " -podkey " + podkey + " -licpath 1999@flex.cd-adapco.com " + simdir + "/" + simname + "\n"
    #if Verb != 0:
    #    print("--- Executing STAR-CCM+ Batch Simulation with " + threads + " thread(s).")
    #    print("--- Call command: " + calling)
    #subprocess.call(calling,shell=True)

    # " & " seems to make gui, but how to call with commands with gui too?
    #nonbatchcalling= drive + " & cd " + directory + " & " + executable + " -server -power -np " + threads + \
    #            " -m " + macrodir + "/" + macro + " -podkey " + podkey + " -licpath 1999@flex.cd-adapco.com " + simdir + "/" + simname + "\n"
    nonbatchcalling= drive + " & cd " + directory + " & " + executable + " -power -np " + threads + \
                " -macro " + macrodir + "/" + macro + " -podkey " + podkey + " -licpath 1999@flex.cd-adapco.com " + simdir + "/" + simname + "\n"
    if Verb != 0:
        print("--- Executing STAR-CCM+ Server Simulation with " + threads + " thread(s).")
        print("--- Call command: " + nonbatchcalling)
    subprocess.call(nonbatchcalling,shell=True)

    # Tock
    simendtime=time.time()
    # End Time Statement
    print ("Simulation Complete. Cycle Number %s" % optcycle + " End Time: %s" % time.ctime())

    # Call the objective function script
    [result, filleff] = ObjectiveFunction.ObjectiveFunction(macrocall_and_filleff_file)
    print("Objective Function value: %.5f" % result )
    print("Fill Efficiency obtained: %.2f" % (100*filleff) + "%" )
    # Save fill eff to file
    if optcycle == 1:
        fill_eff_history = open("OptimisationData//FillEffHistory.txt", "w")
        penalty_fill_eff_history = open("OptimisationData//PenalisedFillEffHistory.txt", "w")
    else:
        fill_eff_history = open("OptimisationData//FillEffHistory.txt", "a")
        penalty_fill_eff_history = open("OptimisationData//PenalisedFillEffHistory.txt", "a")
    fill_eff_history.write(str(100*round(filleff,5))+", ")
    penalty_fill_eff_history.write(str(100*round(filleff,5))+", ")
    fill_eff_history.close()
    penalty_fill_eff_history.close()

    simtotaltime=simendtime-simstarttime
    # Total Time Statement
    print ("Total Simulation Process Time Elapsed (Cycle Number %s" % optcycle + "): ", ("%.2f" % (simtotaltime/3600)) + " hours, or ", ("%.2f" % \
                 (simtotaltime/60)) + " minutes, or ", ("%.2f" % simtotaltime) + " seconds.")
    print("------------------")

    # Return the result to optimiser
    return result


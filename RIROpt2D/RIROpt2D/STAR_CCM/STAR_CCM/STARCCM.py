import sys
import os
import glob
import time
import subprocess

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

    import sys
    import os
    import glob
    import time
    import subprocess
    import ast
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

    # Save positions called just before starting sequence:
    if Verb != 0:
        print("Saving called location parameter(s).")
    if optcycle == 1:
        position_history = open("OptimisationData//PositionParamHistory.txt", "w")
    else:
        position_history = open("OptimisationData//PositionParamHistory.txt", "a")
    position_history.write(str(positions))
    position_history.close()

    # Call the reduced optimiser
    positions = ReducedOptChecker.ReducedOptChecker(positions) 
    # Reduced opt either returns normal positions, otherwise applies reduced opt.

    # Upgrade possible: CAN DRAW A RADIUS AROUND THE HOLE TO BE USED BY FEASIBILITY CHECK

    # Call the feasibility checker/enforcer here (also converts values from mm to m for STAR-CCM+)
    feasible_positions = FeasibilityCheck.FeasibilityCheck(positions)

    
    # Macro Edit call, returns the filling efficiency .csv file (with directory)
    macrocall_and_filleff_file = MacroEdit.MacroEdit(feasible_positions)
    if Verb > 1:
        print("Fill efficiency file saved at: " + macrocall_and_filleff_file)

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
    else:
        fill_eff_history = open("OptimisationData//FillEffHistory.txt", "a")
    fill_eff_history.write(str(100*filleff)+", ")
    fill_eff_history.close()


    simtotaltime=simendtime-simstarttime
    # Total Time Statement
    print ("Total Simulation Process Time Elapsed (Cycle Number %s" % optcycle + "): ", ("%.2f" % (simtotaltime/3600)) + " hours, or ", ("%.2f" % \
                 (simtotaltime/60)) + " minutes, or ", ("%.2f" % simtotaltime) + " seconds.")
    print("------------------")

    # Return the result to optimiser
    return result





## Below is commented out script taken from online source 
#with open('batch.sh', 'w') as f:
#    f.write(r'#!/bin/bash' + "\n")
#    for i, sim in enumerate(simfulldir):
#        f.write(starccmcommand + " -batch -power -np " + numofcores +
#                " " + macrodir + sim + " -podkey " + pwondemandkey + "\n")
#        f.write("curl -u " + pushbullettoken +
#                ": https://api.pushbullet.com/v2/pushes -d type=note -d title=\"" + simfiles[i] + " finished\"\n")
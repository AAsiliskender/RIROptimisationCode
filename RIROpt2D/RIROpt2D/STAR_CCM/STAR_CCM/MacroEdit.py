###### -- Macro Editor Code for RIROpt2D.py
###### -- By Ahmed Asiliskender, initial write date 20 Sept 2021 
###### -- Called by STARCCM and works by using selecting specific line 
###### in Macro to modify for changing the port/vent locations. Could 
###### be modified to change other things but, may be unnecessary.

from os import error


def MacroEdit(NewVals, Verb=0):
    
    # -- MacroDir should be in string.
    # -- MacroFile should be in string and contain the file extension.
    # -- Lines indicate the line to be modified.
    # -- Variables indicate the variable to be modified (i.e. expressionReport_1)
    # -- NewVals are the new variables (i.e. new guess)
    # -- Verb is the verbosity, default 0 only states basics, any other states
    # the pre- and post-change lines.
    
    print("++++++++++++++++++")
    print("Initialising Macro Editor Module:")

    import ast
    import time

    optcycle=0
    optread = open("OptimisationData//OptCycleCounter.txt", "r")
    optcycle = int(optread.read())
    optread.close()

    # Tick
    macrostarttime=time.time()
    # Start time statement
    print ("Macro Editor, Cycle Number %s" % optcycle + " Start Time: %s" % time.ctime())


    print("Reading External Arguments:")
    # Read parameter file to retrieve necessary parameters
    parameterfile = open("OptimisationData//MacroEditParamFile.txt", "r")
    parameterdata = parameterfile.readlines()
    parameters = ast.literal_eval(parameterdata[0])
    parameterfile.close()

    # Taking extra args from parameter file (converting some to string) 
    MacroDir = "%s" % parameters[0]
    MacroFile = "%s" % parameters[1]
    Lines = parameters[2]
    Variables = parameters[3]
    SaveDirs = parameters[4]
    SaveNames = parameters[5]
    SaveLines = parameters[6]
    SaveExtensions = parameters[7] 
    Verb = parameters[8]

    # Put all new values in one list to allow easy macro editing
    Change_Vals=[]
    for i in range(0,len(NewVals)):
        Change_Vals = Change_Vals + NewVals[i]


    if len(Variables) != len(Change_Vals):
        varvalcount="Numbers do not match! \n Variable change count: %s" % len(Variables) + "\n Value change count: %s" % len(Change_Vals)
        raise Exception(varvalcount)

    if Verb != 0:
        print("--- Parameters read from file:")
        print(parameters)


    MacroFull = MacroDir + "/" + MacroFile

    with open(MacroFull, 'r') as file:
        # Read a list of lines into data
        data = file.readlines()
        if Verb > 1:
            print("--- Pre-change Macro file:")
            print(data)
        

    ### Create new lines to replace old lines (variables)
    edit=[]
    for i in range(0, len(Variables)):
        edit.append("    "+ Variables[i] + ".setDefinition(\"%s" % Change_Vals[i] + "\");\n")
        # Selectively edit lines
        data[Lines[i]-1]=edit[i]

    ### Create new lines to replace old lines (save files)
    editsave=[]; SaveLoc=[]
    for i in range(0,len(SaveLines)): # Get the full directory of file save locations
        SaveLoc.append(SaveDirs[i] + "/" + SaveNames[i] + "_%s" % optcycle + SaveExtensions[i])

    editsave.append("    simulation_0.saveState(\"%s" % SaveLoc[0] + "\");\n")
    editsave.append("    scene_0.printAndWait(resolvePath(\"%s" % SaveLoc[1] + "\"), 1, 1200, 800, true, true);\n") #Full view
    editsave.append("    scene_0.printAndWait(resolvePath(\"%s" % SaveLoc[2] + "\"), 1, 1200, 800, true, true);\n") #Closeup
    editsave.append("    monitorPlot_0.getDataSetManager().writeCSVDataSet(monitorDataSet_0, resolvePath(\"%s" % SaveLoc[3] + "\"), \",\");\n")

    for i in range(0, len(SaveLines)):
        # Selectively edit lines
        data[SaveLines[i]-1]=editsave[i]


    # Compile all lines into a single string for writing
    outcompile=""
    for i in range(0, len(data)):
        outcompile=outcompile + data[i]
    
    if Verb != 0:
        print("--- Post-change Macro file:")
        print(outcompile)
    
    file.close
    out = open(MacroFull,'w')
    out.writelines(outcompile)
    out.close

    # Tock
    macroendtime=time.time()
    # End Time Statement
    print ("Macro Editor Complete. Cycle Number %s" % optcycle + " End Time: %s" % time.ctime())
    print ("Returning Filling Efficiency file name.")

    macrototaltime=macroendtime-macrostarttime
    # Total Time Statement
    print ("Total Macro Editor Time Elapsed (Cycle Number %s" % optcycle + "): ", ("%.2f" % (macrototaltime/3600)) + " hours, or ", ("%.2f" % \
                 (macrototaltime/60)) + " minutes, or ", ("%.2f" % macrototaltime) + " seconds.")
    print("++++++++++++++++++")
    return str(SaveLoc[3])
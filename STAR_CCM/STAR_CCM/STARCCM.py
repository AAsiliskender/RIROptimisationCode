import sys
import os
import glob
import time
import subprocess

def STARCCM(executable,drive,directory,simdir,simname,macro,macrodir=[],threads=1,podkey=[],optcycle=[],pushtoken=[]):
    # -- EXECUTABLE is the cmd terminal's string that opens STARCCM (i.e. starccm+ for starccm+.exe.)
    # -- DRIVE and directory indicate the location (and drive) of the STAR-CCM+ executable.
    # -- SIMDIR is the path of the directory containing the .sim file to be used.
    # -- SIMNAME is the name of the .sim file to be used (with the extension).
    # -- MACRODIR is the path of directory containing the macro file. If empty, it assumes the same value
    # the simdir variable.
    # -- MACRO is the Javascript file that is used by STAR-CCM+ to automate processes (cannot be empty ""
    # as optimisation requires cycles of simulation).
    # -- THREADS is the CPU/node count setting in STAR-CCM+, (it states 'cores' in the GUI but it appears
    # to actually be threads which is generally 2 per CPU core.)
    # -- PODKEY is the Power-on-Demand key required to run STAR-CCM+.
    # -- OPTCYCLE is an optional input stating the current optimisation cycle.
    # -- PUSHTOKEN is the token for creating push notifications to indicate completion (may not be used.)


    # -- Make sure to note that the directories should be typed appropriately in order run in shell. Forward
    # slashes may be preferred to avoid misreads.
    # -- Input all arguments in string.
    
    print("Initialising STARCCM Module:")

    import sys
    import os
    import glob
    import time
    import subprocess


    simstarttime=time.time()
    if optcycle==[]:
        print ("Batch Simulation Start Time: %s" % time.ctime())
    else:
        print ("Batch Simulation Number %s" % optcycle + " Start Time: %s" % time.ctime())
    
    
    
    # Converting all inputs to string
    executable = "%s" % executable
    #drive = "%s" % drive
    #directory = "%s" % directory
    simdir = "%s" % simdir
    simname = "%s" % simname
    macrodir = "%s" % macrodir
    macro = "%s" % macro
    threads = "%s" % threads
    if podkey!=[]:
        podkey = "%s" % podkey
    else:
        return print(os.error("Critical Error (STARCCM): PoD key not inputted!"))

    if pushtoken!=[]:
        pushtoken = "%s" % pushtoken
    else:
        print("Notice: No Push token used.")
        

    print("Executing STAR-CCM+ Batch Simulation")
    calling="C: & cd C:\Program Files\Siemens/15.04.008-R8\STAR-CCM+15.04.008-R8\star/bin & " \
             + executable + " -batch -power -np " + threads + \
                " " + macrodir + "/" + macro + " " + simdir + "/" + simname + " -podkey " + podkey + "\n"
    #subprocess.call(calling,shell=True)
    print("Call command: " + calling)
    







    simendtime=time.time()
    if optcycle==[]:
        print ("Batch Simulation End Time: %s" % time.ctime())
    else:
        print ("Batch Simulation Number %s" % optcycle + " End Time: %s" % time.ctime())

    simtotaltime=simendtime-simstarttime
    if optcycle==[]:
        print ("Total Batch Simulation Time Elapsed: ", ("%.2f" % (simtotaltime/3600)) + " hours, or ", ("%.2f" % \
                     (simtotaltime/60)) + " minutes, or ", ("%.2f" % simtotaltime) + " seconds.")
    else:
        print ("Total Batch Simulation Time Elapsed (Number %s" % optcycle + "): ", ("%.2f" % (simtotaltime/3600)) + " hours, or ", ("%.2f" % \
                     (simtotaltime/60)) + " minutes, or ", ("%.2f" % simtotaltime) + " seconds.")




## Below is commented out script taken from online source 
#with open('batch.sh', 'w') as f:
#    f.write(r'#!/bin/bash' + "\n")
#    for i, sim in enumerate(simfulldir):
#        f.write(starccmcommand + " -batch -power -np " + numofcores +
#                " " + macrodir + sim + " -podkey " + pwondemandkey + "\n")
#        f.write("curl -u " + pushbullettoken +
#                ": https://api.pushbullet.com/v2/pushes -d type=note -d title=\"" + simfiles[i] + " finished\"\n")
# -- Global Optimisation Code for Resin Injection Repair Reduced-Order Simulation
# -- By Ahmed Asiliskender, initial write date 03 Sept 2021 
# -- The 'Global' refers to this code being overarching rather than seeking the
# global optimum.

version = "0.0.1"

print("Initialising Global Optimisation Code for RIR v. " + version + ".")

import time
import subprocess


starttime=time.time()
print ("Optimisation Start Time: %s" % time.ctime())

print("Importing STARCCM module")
from STAR_CCM import STARCCM

print("Importing PRAXIS module")

# Parameters (user-set)
starccmcommand = "starccm+"
defuserpswd = "ChangeToYOURS"
pushbullettoken = "o.Xm8HY3DXPnal9STDab4cfy0tYnS00Tt2"
numofcores = "12"
pwondemandkey = "EsZx3xudjt4dptN3dl0GJg"
macrofile = "meshandrun.java"




STARCCM.STARCCM("starccm+",2,3,"D:\Ahmeds_Files\PhD\Simulations\Optimisation","1-Optimisation.sim","D:\Ahmeds_Files\PhD\Simulations\Optimisation\Codes\STAR_CCM\STAR_CCM","automation_macro.java","2","BELO",1,[])

endtime=time.time()
print ("Optimisation End Time: %s" % time.ctime())

totaltime=endtime-starttime
print ("Total Time Elapsed: ", ("%.2f" % (totaltime/3600)) + " hours, or ", ("%.2f" % (totaltime/60)) + " minutes, or ", ("%.2f" % totaltime) + " seconds.")


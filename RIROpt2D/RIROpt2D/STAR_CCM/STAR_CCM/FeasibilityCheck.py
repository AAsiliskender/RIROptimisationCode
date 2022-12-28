###### -- Feasibility Check Code for RIROpt2D.py
###### -- By Ahmed Asiliskender, initial write date 20 Sept 2021 
###### -- Called by STARCCM and works by using initial guess or 
###### optimiser guess and determines if next guess is within domain,
###### if initial not in domain, fails, if optimiser guess not in
###### domain, it 'bounces' it back in.

from time import process_time_ns
from typing import final
import numpy

def FeasibilityCheck(holepositions):

    print("==================")
    print("Initialising Feasibility Checker Module:")

    import csv
    import ast
    import time

    print("Initialising Summarised Functions")

    #####################################
    # --- Number Rounder
    # --- Rounds numbers halfway up (e.g. from 0.5 to 1)
    # --- Fortified with an error arg that removes float error possibilities for vals exactly
    # given as halves. This applies so long as the decimals needed is above the error magnitude.
    def round_half_up(n, decimals=0,error=0.00001): 
        import math
        multiplier = 10 ** decimals
        return math.floor(n*multiplier + 0.5+error) / multiplier
    #####################################

    #####################################
    # --- Iterative Binary Search Function
    # --- It returns index of ytarget in given array y_array if present, else returns -1
    def binary_search(y_array, ytarget):
        low = 0
        high = len(y_array) - 1
        mid = 0
 
        while low <= high:
 
            mid = (high + low) // 2
 
            # If x is greater, ignore left half
            if y_array[mid] < ytarget:
                low = mid + 1
 
            # If x is smaller, ignore right half
            elif y_array[mid] > ytarget:
                high = mid - 1
 
            # means x is present at mid
            else:
                return mid
     
        # If we reach here, then the element was not present
        return -1
    #####################################

    optcycle=0
    optread = open("OptimisationData//OptCycleCounter.txt", "r")
    optcycle = int(optread.read())
    optread.close()

    # Tick
    feasstarttime=time.time()
    # Start time statement
    print ("Feasibility Checker, Cycle Number %s" % optcycle + " Start Time: %s" % time.ctime())


    ####################################################
    print("Reading External Arguments:")
    ### Read parameter file to retrieve necessary parameters
    parameterfile = open("OptimisationData//FeasibilityParamFile.txt", "r")
    parameterdata = parameterfile.readlines()
    parameters = ast.literal_eval(parameterdata[0])
    parameterfile.close()

    geo_dir = parameters[0]
    geo_filename = parameters[1]
    por_filter = parameters[2]
    Verb = parameters[3]

    if Verb != 0:
        print("--- Parameters read from file:")
        print(parameters)

    geo_file = open(geo_dir + "/" + geo_filename,'r')

    csvreader=csv.reader(geo_file)
    
    # Read header
    header=next(csvreader)

    if Verb != 0:
        print("--- CSV file header:")
        print(header)
    
    # Obtain datasets
    datarows=[]
    for row in csvreader:
        datarows.append(row)

    # Create separate variables for x, y and porosity
    x=[]; y=[]; por=[]
    for location in datarows: # Must use float() otherwise it reads as str
        x.append(float(location[0]))
        y.append(float(location[1]))
        por.append(float(location[2]))

    if Verb != 0:
        print("--- Data lengths (X,Y,Porosity):")
        print(len(x))
        print(len(y))
        print(len(por))
    ####################################################

    ### Round inputs to align with coord points
    for hole in range(0,len(holepositions)):
        for coord in range(0,len(holepositions[hole])):
            holepositions[hole][coord]=round_half_up(holepositions[hole][coord],1)

    ### Change porosity values into domain value (1 - domain, 0 - not domain)
    filteredpor=por # Cheap preallocation
    for i in range(0,len(por)):
        if por[i]<por_filter:
            filteredpor[i]=0
        if por[i]>=por_filter:
            filteredpor[i]=1

    ### Search for location of new hole coordinates
    # Reorganising field into [ [x1,y1], [x2,y2], ... ] to search positions
    field_positions = []
    for i in range(0,len(x)):
        field_positions.append([x[i],y[i]])
    
    # Error Check (if placement outside entire field)
    xtgt=[]; ytgt=[]
    for num in range(0,len(holepositions)):
        xtgt.append(float(holepositions[num][0]))
        ytgt.append(float(holepositions[num][1]))   
    if max(xtgt) > max(x) or min(xtgt) < min(x) or max(ytgt) > max(y) or min(ytgt) < min(y):
            Outside="##### Hole target(s) outside entire porosity field! [xtgt, ytgt]: %s" % [xtgt, ytgt] 
            raise Exception(Outside)

    # Find index location of all of new holes
    hole_index=[]
    for num in range(0,len(holepositions)):
        hole_index.append(binary_search(field_positions,holepositions[num]))

    # Find coords of all of new holes
    for i in range(0,len(hole_index)):
        if Verb != 0:
            print("--- Hole Number %s" % (i+1) + " Information:")
            print("Looking for hole at coordinates: %s" % holepositions[i])
            print("Looking for hole at global index: %s" % hole_index[i])
            if Verb > 1:
                print("Found hole at x-coordinate: %s" % x[hole_index[i]])
                print("Found hole at y-coordinate: %s" % y[hole_index[i]])

    # Assume feasible (penalty is 0, unless shown otherwise)
    penaltyratio=0

    # Check if hole is outside domain (i.e. bad)
    bad_hole_index=[1] # Start by assuming there is (to do this cycle at least once)
    bad_hole_cycle=0
    bad_hole_event_storage=[] # Stores all holes when bad hole event occurs
    bad_hole_file_storage=[] # Combines all bad hole events within one optcycle for file save
    bad_hole_prev=[] # Stores most recent bad hole group
    bad_hole_current=[] # Stores current bad hole group (in case needed)
    while len(bad_hole_index)>0: # Keep iterating until no more exists. 
        
        bad_hole_index=[]; bad_hole_locindex=[]; bad_hole_loc=[]
        for i in range(0,len(hole_index)): # For all holes this optcycle
            if filteredpor[hole_index[i]]==0: # Bad hole check
                bad_hole_index.append(i)
                bad_hole_locindex.append(hole_index[i])
                bad_hole_loc.append(holepositions[i])

        if bad_hole_cycle==30: # The script has failed if it fails to do it in 30 cycles
            failedfeas = "Feasibility enforcement failed!"
            print(failedfeas)
            penaltyratio=0.01
            return holepositions,penaltyratio
            #raise Exception(failedfeas)

        if bad_hole_index!=[]: # Warns if outside
            bad_hole_cycle=bad_hole_cycle+1
            for i in range(0,len(bad_hole_index)):
                print("~~~ Warning: Bad hole detected!")
                print("Bad hole cycle: %s" % bad_hole_cycle)
                print("Hole number %s" % (bad_hole_index[i]+1) + " is outside the domain")
                print("Bad hole at global index: %s" % bad_hole_locindex[i])
                print("Coordinate of bad hole: %s" % bad_hole_loc[i])

            if optcycle == 1: # End script if first cycle as there is no possibility of reflection
                BadHole="##### Initial hole placement(s) outside the domain!"
                raise Exception(BadHole)

            else: # Here we store hole data as bad hole event occured
                for i in range(0,len(hole_index)): # Store all hole data
                    bad_hole_event_storage=bad_hole_event_storage+[holepositions[i]] + [hole_index[i]] # [[Hole positions], [Hole indices]]
                bad_hole_current=[]
                bad_hole_current=[bad_hole_index]+[bad_hole_loc]+[bad_hole_locindex] # Store only most recent bad holes here
                # ^[[Bad hole index], [Bad hole location([x,y])], [Bad hole location index]]
                # Index is which hole is bad, location is coords, location index is the global index

                ### Read previous hole coordinates or past bad hole data set
                # Previous hole data if 1st bad hole cycle, otherwise prev. bad holes
                if bad_hole_cycle == 1: # Case for using previous iteration hole
                    holesdatareadfile = open("OptimisationData//HolesData.txt", "r")
                    prev_holedata = holesdatareadfile.readline()
                    prev_holes = ast.literal_eval(prev_holedata)
                    holesdatareadfile.close()
                    
                    # To pick out last iteration hole data (only for holes currently bad)
                    prev_holes_loc=[]; prev_holes_locindex=[]
                    prev_holes_index=bad_hole_index # Same as bad_hole_current[0]
                    for bad_hole_num in bad_hole_index:
                        # 2nd to last index is the latest set of hole locations
                        prev_holes_loc.append(prev_holes[len(prev_holes)-2][bad_hole_num])
                        # Last index is the latest set of hole global index data
                        prev_holes_locindex.append(prev_holes[len(prev_holes)-1][bad_hole_num])
                
                else: # If not 1st bad hole cycle use last bad hole set
                    prev_holes_index = bad_hole_prev[0]
                    prev_holes_loc = bad_hole_prev[1]
                    prev_holes_locindex = bad_hole_prev[2]

                bad_hole_prev=bad_hole_current # Set current bad hole as previous in case of next cycle

            # -- Here we just reflect the overshooting hole location back from nearest distance
            # -- I will have a setting to change how much it reflects (factor) but it will be kept at 1
            # -- If somehow it's reflected back outside the domain, we use the bad hole as old hole 
            # (i.e. bad_hole_cycle!=1) and reflect back again until in domain.
            
            ### Correction of bad hole locations
            # --- Here we bisect the bad hole and previous hole midpoints until the rounded
            # value stops changing (we land next/on a boundary). We use it to obtain the
            # reflection distance and thus the coords of the new hole to be tested.

            ####################################################
            #### Boundary Bisection, Hole Reflection Script ####
            ####################################################
            # Conducting process for each hole individually
            vectorset=[] # We only use 2 coordinates
            boundary=[] # These variables are held for all holes
            reflect_vector=[]
            covered_vector=[]
            new_hole_locations=[]
            new_hole_moveset=[]
            new_hole_locindex=[]
            penaltyvalue=[]
            for hole in range(0,len(bad_hole_loc)):# For each bad hole

                print("------")
                print("--- Bad hole Index %s" % (bad_hole_index[hole]+1))
                inside = prev_holes_loc[hole] # Previous used hole (last iter) is inside
                outside = bad_hole_loc[hole] # Bad hole is outside
                midptprevlast=[[]]; midptlast=[]
                loop=0

                while midptlast != midptprevlast:
                    loop = loop+1

                    midpoint=[]
                    for coord in range(0,len(bad_hole_loc[hole])):
                        midpoint.append(round_half_up((inside[coord]+outside[coord])/2,1))
                    midpointindex=binary_search(field_positions, midpoint)

                    if Verb >= 2:
                        print("-~-~-~-~-~-~")
                        print("--- Bisection Loop: %s" % loop)
                        print("    Internal hole @ %s" % inside)
                        print("    External (bad) hole %s" % outside)
                        print("    Midpoint (boundary guess) index: %s" % midpointindex)
                        print("    Midpoint Coordinate %s" % field_positions[midpointindex])
                        print("    Midpoint in domain? %s" % filteredpor[midpointindex])
                        print("    Last midpoint location: %s" % midptlast)
                        print("    2nd last midpoint location: %s" % midptprevlast)
                        print("-~-~-~-~-~-~")

                    if filteredpor[midpointindex] == 1:
                        inside = midpoint # If inside domain, midpoint replaces prev. inside
                    else:
                        outside = midpoint # If outside domain, midpoint replaces prev. outside

                    midptprevlast = midptlast # 2nd most recent midpoint (used for stop check)
                    midptlast=midpoint # Most recent midpoint

                print("--- Boundary location @ %s" % midpoint)
                if Verb >= 3:
                    print("~~~~~~")
                    print("--- Last loop midpoint (boundary guess) @ %s" % midptlast)
                    print("Midpoint 2 loops ago @ %s" % midptprevlast)
                    print("~~~~~~")
                    
                # Recording the boundary pt and the vectors of distance covered and reflect distance
                boundary.append(midpoint)
                covered_dist=[] # These values are held only for each hole processed, stored elsewhere
                reflect_dist=[]
                vector=[]
                new_hole=[]; new_hole_move=[]
                
                for coord in range(0,len(bad_hole_loc[hole])): # For every coordinate
                    # Obtain difference in coordinates to make vectors
                    # We use round_half_up here just to eliminate floating point errors
                    # Shift vector
                    vector.append(round_half_up((bad_hole_loc[hole][coord]-prev_holes_loc[hole][coord]),1))
                    # Distance covered
                    covered_dist.append(round_half_up((midpoint[coord]-prev_holes_loc[hole][coord]),1))
                    # Remaining distance to reflect
                    reflect_dist.append(round_half_up((covered_dist[coord]-vector[coord]),1))
                    # Movement required for new hole
                    new_hole_move.append(round_half_up((covered_dist[coord]+reflect_dist[coord]),1))
                    # Coordinate of new hole
                    new_hole.append(round_half_up((prev_holes_loc[hole][coord]+new_hole_move[coord]),1))
                
                # Penalty value of bad hole
                penaltyvalue.append(abs(numpy.linalg.norm(reflect_dist))**2)
                    
                # Location index of new hole
                new_hole_locindex.append(binary_search(field_positions,new_hole))

                # Combine vectors, locations of all bad holes in the cycle
                vectorset.append(vector) 
                covered_vector.append(covered_dist)
                reflect_vector.append(reflect_dist)
                new_hole_moveset.append(new_hole_move)
                new_hole_locations.append(new_hole)
                

                if Verb >= 2:
                    print("--- Summary:")
                    print("Original shift vector: %s" % vector)
                    print("Vector of distance (to boundary): %s" % covered_dist)
                    print("Vector of reflection: %s" % reflect_dist)
                    print("Vector of hole movement: %s" % new_hole_move)
                print("New hole indexed %s" % (bad_hole_index[hole]+1) + " location from: %s" % prev_holes_loc[hole] + " to %s" % new_hole)
                print("Hole location index: %s" % new_hole_locindex[hole])
            
            if penaltyvalue != []: #Avg of penalty value to get penalty ratio
                penaltyratio=sum(penaltyvalue)/len(hole_index)

            if Verb >= 1:
                print("-~-~-~-~-~-~")
                print("--- Summary of all bad holes:")
                print("    Original shift vectors: %s" % vectorset)
                print("    Vector of boundary distances: %s" % covered_vector)
                print("    Vector of reflections: %s" % reflect_vector)
                print("    Vector of hole movements: %s" % new_hole_moveset)
                print("    Detected boundary coordinates: %s" % boundary)
                print("    All previously used hole locations (now bad): %s" % prev_holes_loc)
                print("    All (bad) old hole locations: %s" % bad_hole_loc)
                print("    All new hole locations: %s" % new_hole_locations)
                print("    All new hole location indicies: %s" % new_hole_locindex)
                print("    Penalty Ratio: %s" % penaltyratio)
                print("-~-~-~-~-~-~")

            # Change hole positions (bad ones) with new provided value
            for hole in range(0,len(bad_hole_index)): # For each hole
                hole_index[bad_hole_index[hole]] = new_hole_locindex[hole]
                # ^Change loc index to match new hole

                holepositions[bad_hole_index[hole]]=new_hole_locations[hole]
                # ^Change locations of only bad holes to new ones

            ####################################################
            ####################################################
            ####################################################

            
            # IMPORTANT: MAY NEED TO APPLY ROUNDING AT START TO MAKE HOLE LOCS STACK IN THIS SCRIPT


        # --- Once we reach here either we have applied correction or none is needed, next loop
        # occurs if we had bad holes just now.


        
    # If we reach here, holes are fine and we stop and save data here, if not, there's an error
    
    if bad_hole_event_storage!=[]: # Prep bad hole data for file (cold) storage
        bad_hole_file_storage=[bad_hole_event_storage]+[optcycle]
        if optcycle == 1: #(Over)write file if 1st cycle
            bad_hole_write = open("OptimisationData//BadHolesData.txt", "w")
            bad_hole_write.write(str(bad_hole_file_storage)+", ")
            bad_hole_write.close()
        else: # Otherwise append
            bad_hole_append=open("OptimisationData//BadHolesData.txt", "a")
            bad_hole_append.write(str(bad_hole_file_storage)+", ")
            bad_hole_append.close()

    ### Write file of working hole data and close (once no more bad holes)
    if optcycle != 1:
        # Append to HolesData.txt file if not 1st cycle
        holesdata_appendfile = open("OptimisationData//HolesData.txt", "a")
        holesdata_appendfile.write(str(holepositions) +", "+str(hole_index) +", ")
        holesdata_appendfile.close()
    else:
        # (Over)write existing HolesData.txt file (if there is one) if 1st cycle
        holesdata_writefile = open("OptimisationData//HolesData.txt", "w")
        holesdata_writefile.write(str(holepositions) +", "+str(hole_index) +", ")
        holesdata_writefile.close()  


    # Should we do a hole radius check? Not for now
    print("Feasibility Check Successful!")

    # Tock
    feasendtime=time.time()
    # End Time Statement
    print("Feasibility Checker Complete. Cycle Number %s" % optcycle + " End Time: %s" % time.ctime())


    feastotaltime=feasendtime-feasstarttime
    # Total Time Statement
    print("Total Feasibility Checker Time Elapsed (Cycle Number %s" % optcycle + "): ", ("%.2f" % (feastotaltime/3600)) + " hours, or ", ("%.2f" % \
                 (feastotaltime/60)) + " minutes, or ", ("%.2f" % feastotaltime) + " seconds.")
    print("==================")

    # We divide by 1000 as this provides the macro with the right units (m, rather than mm)
    for hole in range(0,len(holepositions)):
        for coord in range(0,len(holepositions[hole])):
            holepositions[hole][coord]=holepositions[hole][coord]/1000

    return holepositions,penaltyratio

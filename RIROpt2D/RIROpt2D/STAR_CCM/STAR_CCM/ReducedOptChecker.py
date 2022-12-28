def ReducedOptChecker(positionparameters, Verb=0):

    import time
    import ast
    import math
    import numpy



    print("::::::::::::::")
    print("Checking for Reduced Optimisation:")

    # Read parameter file to retrieve necessary parameters
    parameterfile = open("OptimisationData//ReducedOptimisationParamFile.txt", "r")
    parameterdata = parameterfile.readlines()
    parameters = ast.literal_eval(parameterdata[0])
    parameterfile.close()

    reduced_opt_switch = parameters[0]
    
    if reduced_opt_switch == 0:
        Verb = parameters[1]
        print("Reduced optimisation inactive.")
        if Verb > 0:
            print("Returning with applying full (X,Y) coordinate settings.")
        print("::::::::::::::::::")
        ### Put input into [x,y] setting before sending back
        tempx=[]; tempy=[]
        for val in range(0,len(positionparameters)):
            if val % 2 == 0:
                tempx.append(positionparameters[val])
            else:
                tempy.append(positionparameters[val])
        newposparam =[]
        for num in range(0,len(tempx)):
            newposparam.append([tempx[num], tempy[num]])
        return newposparam # Return the input as no reduced optimisation
    elif reduced_opt_switch == 1:

        print("Reduced optimisation active.")
        print("Initialising Reduced Optimisation Checker Module:")
        
        line_center = parameters[1]
        line_angle = parameters[2]
        Verb = parameters[3]

        if Verb != 0:
            print("--- Parameters read from file:")
            print(parameters)
        
        print("::::::::::::::::::")
        
    else:
        no_red_opt_set = "No setting specifying use (or not) of reduced optimiser!"
        raise Exception (no_red_opt_set)

    # Initialising for multiple inputs
    rad_angle=[]; x_vector=[]; y_vector=[]
    for parameternum in range(0,len(positionparameters)):    
        rad_angle.append(line_angle[parameternum]*math.pi/180)

        x_vector.append(math.cos(rad_angle[parameternum])) # x-value for linevector
        y_vector.append(math.sin(rad_angle[parameternum])) # y-value for linevector

    #Line_vector gives vectors of the lines for all parameters separately

    # [Vent locations, port locations]
    hole_params = positionparameters
    
    # Make hole_loc into list (from tuple or any other form)
    if type(hole_params) == int:
        hole_params=[hole_params]
    elif type(hole_params) == float:
        hole_params=[hole_params]
    elif type(hole_params) == tuple:
        hole_paramstemp=[]
        for i in range(0,len(hole_params)):
            hole_paramstemp=hole_paramstemp+[hole_params[i]]
        
        hole_params = hole_paramstemp
            

    # Make [x,y] coords of all holes and combine: [Vent holes, port holes] order
    locations=[]
    for hole in range(0,len(hole_params)):
        distance=[hole_params[hole]*x_vector[hole], hole_params[hole]*y_vector[hole]] # Dist. vector of current hole
        
        locations.append([line_center[hole][0]+distance[0],line_center[hole][1]+distance[1]]) # Coords of hole
    
    return locations



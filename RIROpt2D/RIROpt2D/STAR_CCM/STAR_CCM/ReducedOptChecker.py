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
        if Verb > 0:
            print("Reduced optimisation inactive.")
            print("Returning with applying full (X,Y) coordinate settings.")
        print("::::::::::::::::::")
        return positionparameters # Return the input as no reduced optimisation
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
    
    rad_angle = line_angle*math.pi/180

    x_vect = math.cos(rad_angle)
    y_vect = math.sin(rad_angle)

    line_vector = [x_vect, y_vect]

    # [Vent locations, port locations]
    hole_params = positionparameters
    
    # Make [x,y] coords of all holes and combine: [Vent holes, port holes] order
    locations=[]
    for hole_loc in hole_params:
        distance=[hole_loc*line_vector[0], hole_loc*line_vector[1]] # Dist. vector of current hole
        locations.append([line_center[0]+distance[0],line_center[1]+distance[1]]) # Coords of hole
    
    return locations



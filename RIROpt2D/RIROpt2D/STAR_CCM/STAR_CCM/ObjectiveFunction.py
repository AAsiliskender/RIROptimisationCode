###### -- Objective Function Code for RIROpt2D.py
###### -- By Ahmed Asiliskender, initial write date 19 Sept 2021 
###### -- Called by STARCCM and works by using STAR-CCM+ data to 
###### try and ascertain the objective function from its result.

def ObjectiveFunction(results_file_path, Verb=0):
    import csv

    # -- Results_file_path provides path of results file containing the filling efficiency.
    # -- Input arg in string.
    # ObjectiveFunction called by STARCCM and reads its output to determine objective
    # function value in order to feed it back into PRAXIS.py

    print("..................")
    print("Initialising Objective Function Module:")

    # Reading STARCCM result file
    print("Reading Fill Efficiency Data File.")
    
    fill_eff_file = open(results_file_path,'r')

    csvreader=csv.reader(fill_eff_file)
    
        # Read header
    header=next(csvreader)

    if Verb != 0:
        print("--- CSV file header:")
        print(header)

    # Obtain datasets
    for row in csvreader:
        pass

    fill_eff = float(row[-1])

    if Verb != 0:
        print("--- Filling Efficiency for this cycle:")
        print(fill_eff)
    
    # Objective Function result from the read file
    Objective=1-fill_eff

    print("Objective Function value obtained.")
    print("..................")

    # Return's Objective Function result to caller
    return Objective, fill_eff










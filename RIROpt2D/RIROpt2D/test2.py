import ast
#####################################
# Iterative Binary Search Function
# It returns index of ytarget in given array y_array if present, else returns -1
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

loc=[[0,0],[0,1],[0,2],[1,0],[1,1],[1,2],[2,0],[2,1],[2,2]]
x=[0,0,0,1,1,1,2,2,2]
y=[0,1,2,0,1,2,0,1,2]




import random
import math

bad_hole_index=[0,1]
bad_hole_loc=[[0.2,0.2],[5,1.2]]
bad_hole_locindex=[19235,50230]

rand1=random.random()
rand2=random.random()
print(rand1)
randq=1
print(round(rand1,3))
print(round(rand1/randq,3)*randq)

#####################################
# --- Number Rounder
# --- Rounds numbers halfway up (e.g. from 0.5 to 1)
# --- Fortified with an error arg that removes float error possibilities for vals exactly
# given as halves. This applies so long as the decimals needed is above the error magnitude.
def round_half_up(n, decimals=0,error=0.000001): 
    import math
    multiplier = 10 ** decimals
    return math.floor(n*multiplier + 0.5+error) / multiplier
#####################################
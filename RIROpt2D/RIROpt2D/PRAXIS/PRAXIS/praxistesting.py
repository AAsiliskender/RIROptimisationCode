def eq1 (x,n):
    z=x[0]**6  # f=(x+4.5)^2+(y-2)^2-34.25 (-10-4.5^2-2^2) - i.e min of -34.25 at x=-4.5 and y=2
    return z

def eq2 (x,n):
    z=x[0]**4+22*x[0]-10  # f=(x+4.5)^2+(y-2)^2-34.25 (-10-4.5^2-2^2) - i.e min of -34.25 at x=-4.5 and y=2
    return z

def eq3 (x,n):
    z=x[0]*x[0]+x[1]*x[1]-4*x[1]+9*x[0]#+x[2]**4-2*x[2]-10 
    return z

def eq4 (x,n):
    z=x[0]*x[0]+x[1]*x[1]-4*x[1]+9*x[0]+x[2]**2+x[3]**2-x[2]+3*x[3]-10  # unknown eq. pt., n=4
    return z

def testeq(x,n):
    z=100-( -5*(x[0]/20)**4 + 13*(x[0]/20)**2 + 1)*10
    return z

def testeq3(x,n):
    z=100-( -5*(x[0]/20)**4 + 13*(x[0]/20)**2 + 1)*5 + (100-( -5*(x[1]/20)**4 + 13*(x[1]/20)**2 + 1)*5)*(abs(x[0]-x[1])/(abs(x[0])+abs(x[1]) ) )
    return z

def testeq2(x,n):
    z=100-( -5*(x/20)**4 + 13*(x/20)**2 + 1)*10
    return z

def compleq3 (x,n):
    z=x[0]*x[0]+6*x[1]*x[1]-4*x[1]+9*x[0]+x[2]**4-2*x[2]+2.5*x[0]**6+5*x[1]**4-x[0]**2-10
    return z

import os

# 100-(-5*(x/20)^4+13*(x/20)^2+1)*10 is the curve similar to expected plot for reduced opt test

dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)
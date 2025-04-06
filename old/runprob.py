'''
Die Run
    ProgramInfo
        Nolan Peet
        CSC 119 - 001
        DieRunApp
        11/27/18
        Description: generates a list of 20 random d6 die rolls and puts repeated outputs in ()
'''
from random import randint
def main_():
                                        #variables
    inRun = False                           #bool for inside "(....)" run of same num
    rolls = [randint(1,6) for i in range(20)]   #creates a list of 20 random rolls

                                                #process
    for i in range(len(rolls)):             #could just say 20
        if inRun:                       #if theres a "(..",
            if rolls[i] != rolls[i-1]:      #is this the same as the last roll?
                print(")", end = "")            # if not print a "..)"
                inRun = False
        if not inRun:                           #does there need to be a "("?
            if i != 19 and rolls[i] == rolls[i+1]:  #is the number the same as next?
                print("(", end = "")                    #then put a "("
                inRun = True                        #now it is in a run

        print(rolls[i], end = "")               #At the end of loop, print the num

    if inRun:                                   #after the last number, make sure
        print(")")                          #not in run, else ")" close 'em out.

main_()                                 #Execute the Function.

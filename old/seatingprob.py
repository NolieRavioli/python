'''
Theater Seating
    ProgramInfo
        Nolan Peet
        CSC 119 - 001
        SeatingProb
        11/27/18
        Description: Outputs total revenue from 5 seats chosen by the user
'''

def main_():
                                                            #variables
    seatList = [['50' for i in range(5)],       #var of nested lists make the seatlist...
                ['40','45','45','45','40'],                 #some rows 
                ['30','35','35','35','30'],         #have unique patterns
                ['20' for i in range(5)],   #<==#but I'm cool so i did this
                ['10' for i in range(5)]]       #on the not unique rows.
    revenue = 0                                 #var that shows the money made
    soldSeats = 0                               #var that counts the loops 

    while soldSeats < 5:
        r = 0           #resetting the variables
        c = 0           #resetting the variables

        #Prints the list
        for i in seatList:
            for j in i:
                print(j, end = " ")
            print('')
            
        while r not in [str(i+1) for i in range(5)] or c not in [str(i+1) for i in range(5)] or seatList[int(r)-1][int(c)-1] == 'SS':
            #valid input loop
            r = input("What row?(1-5) ")
            c = input("What column?(1-5) ")
            if r in [str(i+1) for i in range(5)] and c in [str(i+1) for i in range(5)] and seatList[int(r)-1][int(c)-1] == 'SS':
                #cant but a sold seat
                print("That seat is taken!")
                
                
        running = False                             #stops the run
        revenue += int(seatList[int(r)-1][int(c)-1])    #adds the total
        soldSeats += 1                                      #adds to seats sold
        print("You owe $"+seatList[int(r)-1][int(c)-1]+" dollars.\nYou sit row: "+r+", column: "+c) #tells user where they sit, what they owe
        seatList[int(r)-1][int(c)-1] = 'SS'                     #marks the seat as sold
        input("\nPress enter to continue.")                     #pauses the program so the user can read.


                            #after the 5 seats have been sold,
    for i in seatList:          #print
        for j in i:                 #the
            print(j, end = " ")         #seating chart
        print('')

    print("We sold 5 seats for $"+str(revenue)+" tonight!") #and print the revenue.

main_()                         #Execute the Function.

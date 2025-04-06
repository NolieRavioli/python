'''
Theater Seating
    ProgramInfo
        Nolan Peet
        CSC 119 - 001
        SeatingProb
        11/27/18
        Description: Outputs total revenue from 5 seats chos
'''

def numeralToDec(n): #makes sense
    if n in ["I","i"]:
        return(1)
    if n in ["V","v"]:
        return(5)
    if n in ["X","x"]:
        return(10)
    if n in ["L","l"]:
        return(50)
    if n in ["C","c"]:
        return(100)
    if n in ["D","d"]:
        return(500)
    if n in ["M","m"]:
        return(1000)
    else: #only used if invalid input
        return("error")

def main_():
    goOn = False
    while not goOn:
        goOn = True                             #Will be set to go on unless error is found
        rnList = list(input("roman number: "))  #Creates list from input
        for i in rnList:
            if numeralToDec(i) == "error":
                goOn = False                    #makes sure the input is good, if not asks again
    total = 0
    
    while len(rnList) > 0:
        if (len(rnList) == 1) or (numeralToDec(rnList[0]) >= numeralToDec(rnList[1])):
            #if bigger than second value, just add to total
            total += numeralToDec(rnList[0])
            rnList.pop(0)
        else:
            #if second value bigger, take the difference
            total += numeralToDec(rnList[1])-numeralToDec(rnList[0])
            rnList.pop(0)
            rnList.pop(1)

    print(total)

main_()

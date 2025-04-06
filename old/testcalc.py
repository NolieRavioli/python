from Tkinter import *
import tkMessageBox
import sys
import os
import math
main = Tk()
string = []
x = 'add'
def exit():
        sys.exit()
def addNumberOne():
        string.append(1.0)
        Label(main, text = "1").grid(row = 0, column = 0)
def addNumberTwo():
        string.append(2.0)
        print '2'
        Label(main, text = "2").grid(row = 0, column = 0)
def addNumberThree():
        string.append(3.0)
        print '3'
        Label(main, text = "3").grid(row = 0, column = 0)
def addNumberFour():
        string.append(4.0)
        print '4'
        Label(main, text = "4").grid(row = 0, column = 0)
def addNumberFive():
        string.append(5.0)
        print '5'
        Label(main, text = "5").grid(row = 0, column = 0)
def addNumberSix():
        string.append(6.0)
        Label(main, text = "6").grid(row = 0, column = 0)
def addNumberSeven():
        string.append(7.0)
        print '7'
        Label(main, text = "7").grid(row = 0, column = 0)
def addNumberEight():
        string.append(8.0)
        print '8'
        Label(main, text = "8").grid(row = 0, column = 0)
def addNumberNine():
        string.append(9.0)
        print '9'
        Label(main, text = "9").grid(row = 0, column = 0)
def addNumberZero():
        string.append(0)
        print '0'
        Label(main, text = "0").grid(row = 0, column = 0)
def add():
        global x
        x = 'add'
        Label(main, text = "+").grid(row = 0, column = 1)
        #Label(main, text = "You have selected addition.").pack()
        #tkMessageBox.showinfo( "The Answer Is:", "%d"%(
        Label(main, text = 'Changed operator to "add"').grid(row = 1, column = 4, columnspan = 30)
def sub():
        global x
        x = 'sub'
        Label(main, text = "-").grid(row = 0, column = 1)
        Label(main, text = 'Changed operator to "sub"').grid(row = 1, column = 4)
def mult():
    global x
    x = 'mul'
    Label(main, text = "*").grid(row = 0, column = 1)
    Label(main, text = 'Changed operator to "mul"').grid(row = 1, column = 4)
def div():
    global x
    x = 'div'
    Label(main, text = "/").grid(row = 0, column = 1)
    Label(main, text = 'Changed operator to "div"').grid(row = 1, column = 4)
def square_root():
    Label(main, text = "%f"%(math.sqrt(string[0]))).grid(row = 0, column = 3)
def enter():
        global x
        if x == 'add':
            answer = Entry(main)
            answer.grid(row = 0, column = 3, columnspan = 30)
            answer.insert(0, "%f"%(string[0] + string[1]))
                #Label(main, text = "%f"%(string[0] + string[1])).grid(row = 0, column = 3)
                #tkMessageBox.showinfo( "The Answer Is:", "%d"%(string[0] + string[1]))
        elif x == 'sub':
        #        Label(main, text = "The answer is: %d"%(string[0] - string[1])).pack()
        #        tkMessageBox.showinfo( "The Answer Is:", "%d"%(string[0] - string[1]))
    #   Label(main, text = "%f"%(string[0] - string[1])).grid(row = 0, column = 3)
        answer = Entry(main)
                answer.grid(row = 0, column = 3, columnspan = 30)
                answer.insert(0, "%f"%(string[0] - string[1]))
    elif x == 'mul':
        #Label(main, text = "%f"%(string[0] * string[1])).grid(row = 0, column = 3)
        answer = Entry(main)
                answer.grid(row = 0, column = 3, columnspan = 30)
                answer.insert(0, "%f"%(string[0] * string[1]))
    elif x == 'div':
        #Label(main, text = "%f"%(string[0] / string[1])).grid(row = 0, column = 3)
        answer = Entry(main)
                answer.grid(row = 0, column = 3, columnspan = 30)
                answer.insert(0, "%f"%(string[0] / string[1]))
        string.pop(0)
        string.pop(0)
def viewString():
        tkMessageBox.showinfo('viewString', '%s\n[%f,%f] '%(x, string[0], string[1]))
        print string
        print x
def restartAPI():
        os.system("python calctest2.py")
        sys.exit()
def add_entry1():
    string.append(int(entry1.get()))
def add_entry2():
        string.append(int(entry2.get()))
def clear_entry():
    string.pop(0)
        string.pop(0)
Label(main, text = '?').grid(row = 0, column = 3)
Button(main, text = '1', command = addNumberOne).grid(row = 1, column = 0)
Button(main, text = '2', command = addNumberTwo).grid(row = 1, column = 1)
Button(main, text = '3', command = addNumberThree).grid(row = 1, column = 2)
Button(main, text = '4', command = addNumberFour).grid(row = 2, column = 0)
Button(main, text = '5', command = addNumberFive).grid(row = 2, column = 1)
Button(main, text = '6', command = addNumberSix).grid(row = 2, column = 2)
Button(main, text = '7', command = addNumberSeven).grid(row = 3, column = 0)
Button(main, text = '8', command = addNumberEight).grid(row = 3, column = 1)
Button(main, text = '9', command = addNumberNine).grid(row = 3, column = 2)
Button(main, text = '0', command = addNumberZero).grid(row = 4, column = 1)
Button(main, text = '=', command = enter).grid(row = 4, column = 0)
Button(main, text = 'exit', command = exit).grid(row = 4, column = 3)
Button(main, text = '+', command = add).grid(row = 5, column = 0)
Button(main, text = '-', command = sub).grid(row = 5, column = 1)
Button(main, text = '*', command = mult).grid(row = 5, column = 2)
Button(main, text = '/', command = div).grid(row = 5, column = 3)
Button(main, text = 'V', command = viewString).grid(row = 4, column = 2)
Button(main, text = 'RS', command  = restartAPI).grid(row = 3, column = 3)
Button(main, text = 'sqrt', command = square_root).grid(row = 2, column = 3)
Button(main, text = 'clr', command = clear_entry).grid(row = 1, column = 3)
Label(main, text = 'Num1:').grid(row = 6, column = 1)
Label(main, text = 'Num2:').grid(row = 7, column = 1)
entry1 = Entry(main)
entry1.grid(row = 6, column = 2, columnspan = 30)
entry2 = Entry(main)
entry2.grid(row = 7, column = 2, columnspan = 30)
Button(main, text = '>', command = add_entry1).grid(row = 6, column = 0)
Button(main, text = '>', command = add_entry2).grid(row = 7, column = 0)
main.mainloop()

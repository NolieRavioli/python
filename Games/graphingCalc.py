from tkinter import *
import math


class Calc():
    def __init__(self):
        self.total = 0
        self.current = ""
        self.percent = False
        self.new_num = True
        self.op_pending = False
        self.op = ""
        self.eq = False

    def num_press(self, num):
        self.eq = False
        temp = text_box.get()
        temp2 = str(num)
        if self.new_num:
            self.current = temp2
            self.new_num = False
        else:
            if temp2 == '.':
                if temp2 in temp:
                    return
            self.current = temp + temp2
        self.display(self.current)

    def calc_total(self):
        self.eq = True
        self.current = float(self.current)
        if self.op_pending == True:
            self.do_sum()
        else:
            if not text_box.get() == int(text_box.get()):
                self.total = (int(text_box.get()))
            else:
                self.total = (float(text_box.get()))

    def display(self, value):
        text_box.delete(0, END)
        text_box.insert(0, value)

    def do_sum(self):
        if self.op == "add":
            self.total += self.current
        if self.op == "subtract":
            self.total -= self.current
        if self.op == "multiply":
            self.total *= self.current
        if self.op == "divide":
            self.total /= self.current
        self.new_num = True
        self.op_pending = False
        self.display(self.total)

    def sign_change(self):
        self.eq = False
        if int(text_box.get()) == float(text_box.get()):
            self.current = -(int(text_box.get()))
        else:
            self.current = -(float(text_box.get()))
        self.display(self.current)

    def square_root(self):
        self.eq = False
        if int(math.sqrt(float(self.current))) == float(math.sqrt(float(self.current))):
            self.current = int(math.sqrt(float(self.current)))
        else:
            self.current = math.sqrt(float(self.current))
        self.display(self.current)

    def percent(self):
        if self.percent == False:
            self.eq = False
            if (self.current * float(100)) % 1 == 0:
                self.current *= int(100)
                self.display(self.current)
            else:
                self.current *= float(100)
            self.percent == True
            self.display(self.current)
        else:
            self.eq = False
            if int(self.current) == float(self.current):
                self.current = int(self.current)
            else:
                self.current = float(self.current)
            self.percent = True
            self.display(self.current)

    def invrs(self):
        self.eq = False
        if (1 / float(self.current)) % 1 == 0:
            self.current = int(1 / float(self.current))
        else:
            self.current = float(1 / float(self.current))
        self.display(self.current)

    def operation(self, op):
        self.current = float(self.current)
        if self.op_pending:
            self.do_sum()
        elif not self.eq:
            self.total = self.current
        self.new_num = True
        self.percent = False
        self.op_pending = True
        self.op = op
        self.eq = False

    def cancel(self):
        self.eq = False
        self.current = "0"
        self.display('')
        self.new_num = True
        self.percent = False

    def all_cancel(self):
        self.cancel()
        self.total = 0

    def bkspace(self):
        self.eq = False
        self.current = text_box.get()[:-1]
        self.display(self.current)

    def test(self):
        return


window = Calc()
Calculator = Tk()
calc = Frame(Calculator)
calc.grid()

Calculator.title("Calculator")
text_box = Entry(calc, justify=RIGHT)
text_box.grid(row=0, column=0, columnspan=5, padx=2.5, pady=2.5)
text_box.insert(0, "0")

numbers = "789456123"
i = 0
bttn = []
for j in range(2, 5):
    for k in range(3):
        bttn.append(Button(calc, text="  " + numbers[i] + "  "))
        bttn[i].grid(row=j, column=k, padx=2.5, pady=2.5)
        bttn[i]["command"] = lambda x=numbers[i]: window.num_press(x)
        i += 1

# single backspace
bkspc = Button(calc, text="  ←  ")
bkspc['command'] = window.bkspace
bkspc.grid(row=1, column=0, padx=2.5, pady=2.5)

# clear
clear = Button(calc, text="  C  ")
clear["command"] = window.cancel
clear.grid(row=1, column=1, padx=2.5, pady=2.5)

# clear everything
all_clear = Button(calc, text="C E")
all_clear["command"] = window.all_cancel
all_clear.grid(row=1, column=2, padx=2.5, pady=2.5)

# sign change
neg = Button(calc, text="  ±  ")
neg["command"] = window.sign_change
neg.grid(row=1, column=3, padx=2.5, pady=2.5)

# square root
sqrt = Button(calc, text="  √  ")
sqrt["command"] = window.square_root
sqrt.grid(row=1, column=4, padx=2.5, pady=2.5)

###!!!!!!!!!!!NEED ^2 thing~~~~~~~~###
"""
sq = Button(calc, text = " x²  ")
sq["command"] = lambda: window.instant_sum("square")
sq.grid(row = 1, column = 4, padx = 2.5, pady = 2.5)
"""

# decimal to percent
prcnt = Button(calc, text="  %  ")
prcnt["command"] = window.percent
prcnt.grid(row=2, column=4, padx=2.5, pady=2.5)

# inverse
invrs = Button(calc, text=" x⁻¹ ")
invrs["command"] = window.invrs
invrs.grid(row=3, column=4, padx=2.5, pady=2.5)

# 4 Basic ops
bttn_div = Button(calc, text="  /  ")
bttn_div["command"] = lambda: window.operation("divide")
bttn_div.grid(row=2, column=3, padx=2.5, pady=2.5)

bttn_mult = Button(calc, text="  *  ")
bttn_mult["command"] = lambda: window.operation("multiply")
bttn_mult.grid(row=3, column=3, padx=2.5, pady=2.5)

minus = Button(calc, text="  -  ")
minus["command"] = lambda: window.operation("subtract")
minus.grid(row=4, column=3, padx=2.5, pady=2.5)

add = Button(calc, text="  +  ")
add["command"] = lambda: window.operation("add")
add.grid(row=5, column=3, padx=2.5, pady=2.5)

point = Button(calc, text="  .  ")
point["command"] = lambda: window.num_press(".")
point.grid(row=5, column=2, padx=2.5, pady=2.5)

bttn_0 = Button(calc, text="        0        ")
bttn_0["command"] = lambda: window.num_press(0)
bttn_0.grid(row=5, column=0, columnspan=2, padx=2.5, pady=2.5)

equals = Button(calc, text=str(" \n  =  \n "))
equals["command"] = window.calc_total
equals.grid(row=4, rowspan=2, column=4, padx=2.5, pady=2.5)


Calculator.mainloop()
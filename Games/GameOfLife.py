from tkinter import *
from threading import Thread
import random, time, ast

global Results
global running
global StartL
global TickCounter
global totalButtons

Results = []
running = True


class ChangingButton:
    global totalButtons

    def __init__(self):
        # makes a list of all this classes
        totalButtons.append(self)

    def CreateB(self, x, y):
        # makes button instance
        self.b = Button(gameboard, width=2, command=self.changeColorOnClick, bg='blue')
        self.b.grid(row=y, column=x)

    def changeColorOnClick(self):
        # Inverts the color
        if self.b.config('bg')[-1] == 'blue':
            self.b.config(bg='red')
            StartL[int(self.b.grid_info()['row'])][int(self.b.grid_info()['column'])] = 1
        else:
            self.b.config(bg='blue')
            StartL[int(self.b.grid_info()['row'])][int(self.b.grid_info()['column'])] = 0


def UpdateFromL():
    for self in totalButtons:
        if StartL[int(self.b.grid_info()['row'])][int(self.b.grid_info()['column'])] == 1:
            self.b.config(bg='red')
        else:
            self.b.config(bg='blue')
    gameboard.update()
    time.sleep((speed.get() - 100) / 1000)


###~~~~~Options for before game starts~~~~~###
def GenGameboard():
    global StartL
    global totalButtons
    try:
        for button in gameboard.winfo_children():
            button.destroy()
    except:
        pass
    StartL = [[0 for j in range(width.get())] for i in range(height.get())]
    totalButtons = []
    for i in range(width.get()):
        for j in range(height.get()):
            ChangingButton().CreateB(i, j)
    randomizeGrid.config(state='normal')
    begin.config(state='normal')
    stop.config(state='disabled')


def RandGrid():
    global StartL
    StartL = [[random.randrange(2) for j in range(width.get())] for i in
              range(height.get())]  # Randomizes starting list
    UpdateFromL()


def Paste():
    global StartL
    tmp = ast.literal_eval(root.clipboard_get())
    height.set(len(tmp))
    width.set(len(tmp[0]))
    GenGameboard()
    StartL = tmp[:]
    UpdateFromL()
    time.sleep((speed.get()) / 1000)


def Copy():
    root.clipboard_clear()
    root.clipboard_append(str(StartL))


###~~~~~Game fuctions~~~~~###

def Step(List):
    global Results
    start_time = time.time()
    Ref_List = [[j for j in List[i]] for i in range(len(List))]
    N_List = [[j for j in List[i]] for i in range(len(List))]
    # Look at each cell #
    for i in range(len(Ref_List)):
        for j in range(len(Ref_List[i])):
            # Look at neighbors of each cell #
            Neighbors = 0
            for k in range(-1, 2):
                for l in range(-1, 2):
                    if (k, l) != (0, 0) and i + k >= 0 and j + l >= 0:
                        try:
                            Neighbors += Ref_List[i + k][j + l]
                        except:
                            pass
            ###VVVV GAME RULES VVVV###
            if Ref_List[i][j] == 1 and Neighbors in [2, 3]:
                N_List[i][j] = 1
            elif Ref_List[i][j] == 0 and Neighbors == 3:
                N_List[i][j] = 1
            else:
                N_List[i][j] = 0
    return N_List


def stop():
    begin.config(state='normal')
    stop.config(state='disabled')
    global running
    running = False


def Start():
    begin.config(state='disabled')
    stop.config(state='normal')
    global running
    global StartL
    running = True
    while running == True:
        StartL = Step(StartL)
        UpdateFromL()


root = Tk()

# initilize gameboard
gameboard = Frame(root)
gameboard.pack(side="left")

# initilize options panel
options = Frame(root)
options.pack(side='left')

begin = Button(options, text='Start', width=15, command=Start, state='disabled')  # Start Game Button
stop = Button(options, text='Stop', width=15, command=stop, state='disabled')  # Stop Game Button
generate = Button(options, text='Generate\ngrid', width=15, command=GenGameboard)  # Generate Grid Button
randomizeGrid = Button(options, text='Randomize!!', width=15, command=RandGrid,
                       state='disabled')  # Randomize Grid Button
# Width Slider
Label(options, text='width:').grid(row=2, column=0)
width = Scale(options, width=10, length=70, orient=HORIZONTAL, from_=5, to=50)
# Height Slider
Label(options, text='height:').grid(row=3, column=0)
height = Scale(options, width=10, length=70, orient=HORIZONTAL, from_=5, to=50)
# Speed Slider
Label(options, text='speed per step\n(in ms)').grid(row=6, column=0)
speed = Scale(options, width=10, length=70, orient=HORIZONTAL, from_=100, to=1000)
# Load/Save
PastL = Button(options, text='Load from\nClipboard', width=10, command=Paste)
SavL = Button(options, text='Copy to\nClipboard', width=10, command=Copy)

# GRID EVERYTHING
begin.grid(row=0, column=0, columnspan=2)  # Start
stop.grid(row=1, column=0, columnspan=2)  # End
width.grid(row=2, column=1)  # Width Slider
height.grid(row=3, column=1)  # height Slider
generate.grid(row=4, column=0, columnspan=2)  # Gen. Grid
randomizeGrid.grid(row=5, column=0, columnspan=2)  # Rand. Grid
speed.grid(row=6, column=1)  # Speed Slider
PastL.grid(row=7, column=0)  # Load button
SavL.grid(row=7, column=1)  # Save button

root.mainloop()

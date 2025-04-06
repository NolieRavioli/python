from turtle import *

def graph():
    xmin = float(input("X min?"))
    xmax = float(input("X max?"))
    xstep = float(input("X step?"))
    ymin = float(input("Y min?"))
    ymax = float(input("Y max?"))
    ystep = float(input("Y step?"))

    scale = 60

    win_x = (abs(xmin)+abs(xmax))*scale
    win_y = (abs(ymin)+abs(ymax))*scale

    setworldcoordinates(xmin*scale,ymin*scale,xmax*scale,ymax*scale)

    axisT = Turtle()
    axisT.speed(100000000)
    for turtle in turtles():
        turtle.ht()
    axisT.up()
    axisT.setpos(xmin*scale,0)
    axisT.down()
    axisT.setpos(xmax*scale,0)
    axisT.up()
    axisT.setpos(0,ymin*scale)
    axisT.down()
    axisT.setpos(0,ymax*scale)
    axisT.up()

    for i in range(0,int(xmax)*scale,int(xstep)*scale):
        i = i
        axisT.setpos(i,float(-win_y/200))
        axisT.down()
        axisT.setpos(i,float(win_y/200))
        axisT.up()


    for i in range(0,int(xmin)*scale,-int(xstep)*scale):
        i = i
        axisT.setpos(i,float(-win_y/200))
        axisT.down()
        axisT.setpos(i,float(win_y/200))
        axisT.up()


    for i in range(0,int(ymax)*scale,int(ystep)*scale):
        i = i
        axisT.setpos(float(-win_x/200),i)
        axisT.down()
        axisT.setpos(float(win_x/200),i)
        axisT.up()

    for i in range(0,int(ymin)*scale,-int(ystep)*scale):
        i = i
        axisT.setpos(float(-win_x/200),i)
        axisT.down()
        axisT.setpos(float(win_x/200),i)
        axisT.up()

    num = int(input("Number of eqations"))

    for i in range(num):
        n = input("y{}=".format(str(i+1)))

        n = n.replace('^','**')
        n = '('+n+')'

        for i in range(-len(n)+1,1):
            i = -i
            if n[i] in ['+','-']:
                n = n[:i]+')'+n[i]+'('+n[i+1:]

        for i in range(len(n)):
            if n[i] == 'x' and i != 1 and n[i-1] in ['1','2','4','5','6','7','8','9','0']:
                n = n[:i]+'*'+n[i:]

        colr = input("Line color?")
        axisT.color(colr)

        for i in range(int(xmin*scale),int(xmax*scale)+1):
            i = float(float(i)/float(scale))
            funcrange = n.replace('x', '('+str(i)+')')
            if eval(funcrange)>ymin and eval(funcrange)<ymax:
                axisT.setpos(float(i)*scale,eval(funcrange)*scale)
                axisT.down()

        axisT.up()
    print("Done!")
    done()


graph()
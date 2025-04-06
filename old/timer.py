from threading import Thread
import time

def timer(name, delay, repeat):
    print "Timer:" + name + " Started."
    while repeat >0:
        time.sleep(delay)
        print name + ": " + str(time.ctime(time.time()))
        repeat -= 1
    print "Timer: " + name + " Completed."

def Main():
    t1 = Thread(target = timer, args = ("Timer1", 1, 5))
    t2 = Thread(target = timer, args = ("Timer2", 1, 5))
    #t3 = Thread(target = timer, args = ("Timer3", 1, 5))
    while True:
        try:
            t1.start()
            t2.start()
        except RuntimeError:
            break
    print 'broken'

    print "Main Complete!"

if __name__ == '__main__':
    Main()

sLen = 5 #MUST BE ODD
x = (sLen-1)//2
y = x
c = 1
l = [[0 for j in range(sLen)] for i in range(sLen)]
indexMap = [[j if i%2==1 else -j for j in range(1,i+1)] for i in range(1, sLen+1)]

#[[j if i%2==1 else -j for i in range(1, sLen+1) for j in range(1,i+1)]


for sSide in indexMap:
    for iDiff in i:
        for axis in range(2):
            (lambda a:a = c)(l[y][x+iDiff]) if axis == 0 else (lambda a:a = c)(l[y+iDiff][x]) 
            c+1
            print('yay')

#j if i%2==1 else -j for i in range(1, sLen+1) for j in range(1,i+1) for k in range(2)



print(l)


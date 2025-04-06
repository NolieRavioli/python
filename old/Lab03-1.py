while True:
    try:
        upper_bound = int(input('upper limit? '))
        break
    except:
        pass

for i in range(1, upper_bound*2,2):
    print(f'the next number is {i/2}')

# this Program will generate a list of Prime Numbers from 2 through n, a User-inputted Integer Number (OR ELSE...).

# instead of doing math.sqrt(), I can import only a part of a library
from math import sqrt

# time() will return the current time in seconds.
from time import time


# THIS CODE IS FOR VALIDATING INPUT VVVVV
while True:
    # a forever loop, waiting for a valid input from the user.
    a = input("Primes up to what number: ")
    if a.isdigit() and int(a) > 2:
        a = int(a)
        break
    print('invalid number, try again.')


# THIS CODE IS FOR GENERATING A LIST OF PRIME NUMBERS VVVVVVVVVVV
t1 = time()
primes = [2]
for n in range(3,a+1):
    divisible = False
    for d in primes:
        # assign variable d for each item in list 'primes'.
        # We only need to check if a number is divisable by primes below it, because MATHMATICS.
        if d > sqrt(n):
            # you dont need to check EVERY number, only up to the sqrt of the target number
            #  ends the NESTED loop only. n will still loop.
            break
        if n%d == 0:
            # the modulo operator (%) is REMAINDER. "if the remainder of 'n divided by d' equals 0"
            divisible = True
    if not divisible:
        # append the tested number at the end of the list of primes.
        primes.append(n)
t2 = time()-t1

print(f"Finished in {round(t2,5)} seconds!")
print(primes)

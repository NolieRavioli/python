line = input()
try:
    if line == "":
        raise RuntimeError
except RuntimeError:
    print("yay")

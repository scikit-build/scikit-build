
from random import getrandbits
from sys import stdout

def cycle(N, i, cy_routines, py_routines):
    nCy = len(cy_routines)
    nPy = len(py_routines)

    newI = getrandbits(32)%nPy

    stdout.write("Python ")
    stdout.write("MODULE")
    stdout.write("\n")
    stdout.flush()

    if N:
        stdout.write("PY -> ")
        py_routines[newI](N - 1, newI, cy_routines, py_routines)


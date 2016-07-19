
from random import getrandbits
from sys import stdout


def cycle(n, i, cy_routines, py_routines):
    n_py = len(py_routines)

    new_index = getrandbits(32) % n_py

    stdout.write("Python ")
    stdout.write("MODULE")
    stdout.write("\n")
    stdout.flush()

    if n:
        stdout.write("PY -> ")
        py_routines[new_index](n - 1, new_index, cy_routines, py_routines)

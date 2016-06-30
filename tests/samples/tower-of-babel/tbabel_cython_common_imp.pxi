
# MODULE_TYPE must be defined
#
# DEF MODULE_TYPE = "STATIC"
# include "tbabel/cython_common_imp.pxi"

cdef extern from "stdlib.h":
    unsigned int rand()

from sys import stdout

cdef void _cycle(unsigned int N, unsigned int i,
                 list _cy_routines, list _py_routines):

    cdef unsigned int nCy = len(_cy_routines)
    cdef unsigned int nPy = len(_py_routines)

    cdef unsigned int newI = rand()%(nCy + nPy)

    stdout.write("Cython ")
    stdout.write(MODULE_TYPE)
    stdout.write("\n")
    stdout.flush()

    if N:
        if newI < nCy:
            stdout.write("C  -> ")
            (<cy_routine>(<size_t>(_cy_routines[newI])))(
                N - 1, newI, _cy_routines, _py_routines)

        else:
            stdout.write("PY -> ")
            _py_routines[newI - nCy](
                N - 1, newI, _cy_routines, _py_routines)

def cycle(N, i, cy_routines, py_routines):
    _cycle(N, i, cy_routines, py_routines)

def get_c_handle():
    return <size_t>(_cycle)


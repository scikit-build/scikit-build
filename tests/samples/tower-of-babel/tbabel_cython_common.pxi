
cimport cython

ctypedef void (*cy_routine)(
    unsigned int, unsigned int, list, list)

cdef void _cycle(unsigned int N, unsigned int i,
                 list cy_routines, list py_routines)


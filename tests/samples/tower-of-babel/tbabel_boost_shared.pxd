
cimport cython

cdef extern from "tbabel_boost_shared.h":
    ctypedef void (*cy_routine)(
        unsigned int, unsigned int, list, list)

    void cycle "tb_shared_cycle"(unsigned int N, unsigned int i,
                                 list cy_routines, list py_routines)


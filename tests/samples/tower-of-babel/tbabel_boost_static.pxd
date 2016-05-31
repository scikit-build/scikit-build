
cimport cython

cdef extern from "tbabel_boost_static.h":
    ctypedef void (*cy_routine)(
        unsigned int, unsigned int, list, list)

    void cycle "tb_static_cycle"(unsigned int N, unsigned int i,
                                 list cy_routines, list py_routines)


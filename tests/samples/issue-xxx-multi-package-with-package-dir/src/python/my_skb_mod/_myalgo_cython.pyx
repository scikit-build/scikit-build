import numpy as np
cimport numpy as np


cdef extern from "../../cxx/my_extern_clib.h":
    cdef long external_c_function(long* data_view, int size);


def cython_func(np.ndarray[np.int64_t, ndim=1] data):
    """
    This is a docstring
    """
    cdef long [:] data_view = data
    cdef int size = len(data)
    cdef long result = 0;
    result = external_c_function(&data_view[0], size)
    return result

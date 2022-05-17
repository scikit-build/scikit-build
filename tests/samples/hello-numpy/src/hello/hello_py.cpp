#include <iostream>
#include <pybind11/pybind11.h>

#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION

#include <numpy/arrayobject.h>

namespace py = pybind11;

void hello() {
    std::cout << "Hello, World!" << std::endl;
}

py::object zeros2x2() {
    npy_intp dims[] = {2, 2};
    return py::reinterpret_steal<py::object>(
        PyArray_Zeros(2, dims, PyArray_DescrFromType(NPY_FLOAT64), 0)
    );
}

PYBIND11_MODULE(_hello, m) {
    m.doc() = "_hello";
    m.def("hello", &hello, "Prints \"Hello, World!\"");
    m.def("zeros2x2", &zeros2x2, "Returns a 2x2 array of zeros.");
}

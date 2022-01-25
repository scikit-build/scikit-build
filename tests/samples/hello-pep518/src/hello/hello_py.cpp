#include <iostream>
#include <pybind11/pybind11.h>

namespace py = pybind11;

void hello() {
    std::cout << "Hello, World!" << std::endl;
}

int return_two() {
    return 2;
}

PYBIND11_MODULE(_hello, m) {
    m.doc() = "_hello";
    m.def("hello", &hello, "Prints \"Hello, World!\"");
    m.def("return_two", &return_two, "Returns 2");
}

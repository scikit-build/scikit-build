
#include <pybind11/pybind11.h>

namespace py = pybind11;


class Logic {
};

PYBIND11_MODULE(_pkg, m)
{
    py::class_< Logic > logic(m, "LogicCPP");
    logic.def(py::init());
}

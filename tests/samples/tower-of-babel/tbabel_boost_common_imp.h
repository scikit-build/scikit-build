
#include <cstdlib>
#include <boost/python.hpp>

#include <tbabel_boost_common.h>

void TB_CYCLE(unsigned int N, unsigned int i,
           PyObject *_cy_routines,
           PyObject *_py_routines)
{
  unsigned int nCy = (unsigned int)PyList_Size(_cy_routines);
  unsigned int nPy = (unsigned int)PyList_Size(_py_routines);
  unsigned int newI = ((unsigned int)rand())%(nCy + nPy);

  PySys_WriteStdout("Boost " TOSTR(TBABEL_MODE) "\n");

  if(N)
  {
    if(newI < nCy)
    {
      PySys_WriteStdout("C  -> ");

      PyObject *_addr = PyList_GetItem(_cy_routines, (Py_ssize_t)newI);
      unsigned long addr = PyLong_AsUnsignedLong(_addr);
      ((cy_routine)((*(void **)(&addr))))(
        N - 1, newI, _cy_routines, _py_routines
      );
    }
    else
    {
      PySys_WriteStdout("PY -> ");
      PyObject *func = PyList_GetItem(_py_routines, (Py_ssize_t)newI - nCy);
      PyObject *args = PyTuple_Pack(
        4,
        PyLong_FromSize_t((std::size_t)(N - 1)),
        PyLong_FromSize_t((std::size_t)newI),
        _cy_routines,
        _py_routines
      );

      PyObject_Call(func, args, NULL);

      Py_XDECREF(args);
    }
  }
}

static void cycle(unsigned int N, unsigned int i,
                  boost::python::list &_cy_routines,
                  boost::python::list &_py_routines)
{
  TB_CYCLE(N, i, _cy_routines.ptr(), _py_routines.ptr());
}

static PyObject *get_c_handle()
{
    return PyLong_FromSize_t((std::size_t)(TB_CYCLE));
}

BOOST_PYTHON_MODULE(TB_MODULE)
{
  using namespace boost::python;
  def("cycle", cycle);
  def("get_c_handle", get_c_handle);
}


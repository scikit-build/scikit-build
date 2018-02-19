
// Python includes
#include <Python.h>

// STD includes
#include <stdio.h>

//-----------------------------------------------------------------------------
static PyObject *hello_example(PyObject *self, PyObject *args)
{
  // Unpack a string from the arguments
  const char *strArg;
  if (!PyArg_ParseTuple(args, "s", &strArg))
    return NULL;

  // Print message and return None
  PySys_WriteStdout("Hello, %s! :)\n", strArg);
  Py_RETURN_NONE;
}

//-----------------------------------------------------------------------------
static PyObject *elevation_example(PyObject *self, PyObject *args)
{
  // Return an integer
  return PyLong_FromLong(21463L);
}

//-----------------------------------------------------------------------------
static PyMethodDef hello_methods[] = {
  {
    "hello",
    hello_example,
    METH_VARARGS,
    "Prints back 'Hello <param>', for example example: hello.hello('you')"
  },

  {
    "size",
    elevation_example,
    METH_VARARGS,
    "Returns elevation of Nevado Sajama."
  },
  {NULL, NULL, 0, NULL}        /* Sentinel */
};

//-----------------------------------------------------------------------------
#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC init_hello(void)
{
  (void) Py_InitModule("_hello", hello_methods);
}
#else /* PY_MAJOR_VERSION >= 3 */
static struct PyModuleDef hello_module_def = {
  PyModuleDef_HEAD_INIT,
  "_hello",
  "Internal \"_hello\" module",
  -1,
  hello_methods
};

PyMODINIT_FUNC PyInit__hello(void)
{
  return PyModule_Create(&hello_module_def);
}
#endif /* PY_MAJOR_VERSION >= 3 */

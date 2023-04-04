
// Python includes
#include <Python.h>

// STD includes
#include <stdio.h>

// Macros used for defining symbol visibility
#if (defined(__GNUC__))
#define _EXPORT __attribute__((visibility("default")))
#define _HIDDEN __attribute__((visibility("hidden")))
#else
#define _EXPORT
#define _HIDDEN
#endif

#include <map>

extern "C"
_EXPORT auto& get_map()
{
  static std::map<int,void*> id_to_resource;
  return id_to_resource;
}

//-----------------------------------------------------------------------------
static PyObject *hello_example(PyObject *self, PyObject *args)
{
  get_map();
  // Unpack a string from the arguments
  const char *strArg;
  if (!PyArg_ParseTuple(args, "s", &strArg))
    return NULL;

  // Print message and return None
  PySys_WriteStdout("Hello, %s!\n", strArg);
  Py_RETURN_NONE;
}

//-----------------------------------------------------------------------------
static PyObject *elevation_example(PyObject *self, PyObject *args)
{
  get_map();
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
    "elevation",
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

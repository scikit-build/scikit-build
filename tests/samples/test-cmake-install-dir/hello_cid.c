#include <Python.h>

#include "hello_cid.h"

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT, "hello_cid", NULL, -1, NULL,
};

PyMODINIT_FUNC PyInit_hello_cid(void) {
  PyObject *m = PyModule_Create(&moduledef);
  if (m != NULL && PyModule_AddIntMacro(m, HELLO_ANSWER) < 0) {
    Py_DECREF(m);
    return NULL;
  }
  return m;
}

#include "Python.h"

struct module_state {
    PyObject *error;
};

#if PY_MAJOR_VERSION >= 3
#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
#else
#define GETSTATE(m) (&_state)
static struct module_state _state;
#endif


static PyObject *
test123(PyObject *self, PyObject *args)
{
  const int value = 123;
  return Py_BuildValue("i", value);
}

static PyMethodDef test1_methods[] = {
   { "test123", (PyCFunction)test123, METH_NOARGS, NULL },
   { NULL }
};


#if PY_MAJOR_VERSION >= 3

static int test1_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int test1_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}


static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "test1",
        NULL,
        sizeof(struct module_state),
        test1_methods,
        NULL,
        test1_traverse,
        test1_clear,
        NULL
};

#define INITERROR return NULL

PyObject *
PyInit_test1(void)

#else
#define INITERROR return

void
inittest1(void)
#endif
{
#if PY_MAJOR_VERSION >= 3
    PyObject *module = PyModule_Create(&moduledef);
#else
    PyObject *module = Py_InitModule("test1", test1_methods);
#endif

    if (module == NULL)
        INITERROR;

#if PY_MAJOR_VERSION >= 3
    return module;
#endif
}


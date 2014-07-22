#include <Python.h>

static PyObject *
test123(PyObject *self, PyObject *args)
{
  const int value = 123;
  return Py_BuildValue("i", value);
}


static PyMethodDef module_methods[] = {
   { "test123", (PyCFunction)test123, METH_NOARGS, NULL },
   { NULL }
};


void inittest1(void)
{
    Py_InitModule("test1", module_methods );
}

#include <Python.h>

static PyObject *
spam_system(PyObject *self, PyObject *args)
{
   const char *command;
   int sts;

   if (!PyArg_ParseTuple(args, "s", &command))
       return NULL;
   sts = system(command);
   return PyLong_FromLong(sts);
}


static PyMethodDef spam_methods[] = {
   {"system",  spam_system, METH_VARARGS,
    "Execute a shell command."},
   {NULL, NULL, 0, NULL}        /* Sentinel */
};


#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC init_spam(void)
{
  (void) Py_InitModule("_spam", spam_methods);
}
#else /* PY_MAJOR_VERSION >= 3 */
static struct PyModuleDef spam_module_def = {
  PyModuleDef_HEAD_INIT,
  "_spam",
  "Internal \"_spam\" module",
  -1,
  spam_methods
};

PyMODINIT_FUNC PyInit__spam(void)
{
  return PyModule_Create(&spam_module_def);
}
#endif /* PY_MAJOR_VERSION >= 3 */

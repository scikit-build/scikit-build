#ifndef HELLO_EXPORT
#ifdef WIN32
#define HELLO_EXPORT __declspec(dllexport)
#else
#define HELLO_EXPORT
#endif
#endif


// BEGIN PYTHON BINDINGS
// * python's ctypes module can talk to extern c code
// http://nbviewer.ipython.org/github/pv/SciPy-CookBook/blob/master/ipython/Ctypes.ipynb
#ifdef __cplusplus
extern "C" {
#endif


HELLO_EXPORT int elevation_example()
{
  // Return an integer
  return 21463;
}


#ifdef __cplusplus
} // extern "C"
#endif

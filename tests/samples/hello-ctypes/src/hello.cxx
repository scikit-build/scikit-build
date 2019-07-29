#include "hello.h"


// BEGIN PYTHON BINDINGS
// * python's ctypes module can talk to extern c code
// http://nbviewer.ipython.org/github/pv/SciPy-CookBook/blob/master/ipython/Ctypes.ipynb
extern "C" {


HELLO_EXPORTED int elevation_example()
{
  // Return an integer
  return 21463;
}


} // extern "C"

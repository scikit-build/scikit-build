// Define HELLO_EXPORTED for any platform
// References: https://atomheartother.github.io/c++/2018/07/12/CPPDynLib.html
#if defined _WIN32 || defined __CYGWIN__
  #ifdef HELLO_WIN_EXPORT
    // Exporting...
    #ifdef __GNUC__
      #define HELLO_EXPORTED __attribute__ ((dllexport))
    #else
      #define HELLO_EXPORTED __declspec(dllexport) // Note: actually gcc seems to also supports this syntax.
    #endif
  #else
    #ifdef __GNUC__
      #define HELLO_EXPORTED __attribute__ ((dllimport))
    #else
      #define HELLO_EXPORTED __declspec(dllimport) // Note: actually gcc seems to also supports this syntax.
    #endif
  #endif
  #define HELLO_NOT_EXPORTED
#else
  #if __GNUC__ >= 4
    #define HELLO_EXPORTED __attribute__ ((visibility ("default")))
    #define HELLO_NOT_EXPORTED  __attribute__ ((visibility ("hidden")))
  #else
    #define HELLO_EXPORTED
    #define HELLO_NOT_EXPORTED
  #endif
#endif



// BEGIN PYTHON BINDINGS
// * python's ctypes module can talk to extern c code
// http://nbviewer.ipython.org/github/pv/SciPy-CookBook/blob/master/ipython/Ctypes.ipynb
#ifdef __cplusplus
extern "C" {
#endif


HELLO_EXPORTED int elevation_example()
{
  // Return an integer
  return 21463;
}


#ifdef __cplusplus
} // extern "C"
#endif

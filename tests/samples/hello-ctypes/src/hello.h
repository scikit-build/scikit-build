#ifndef _HELLO_H

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


#define _HELLO_H
#endif

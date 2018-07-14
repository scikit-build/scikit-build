%module swig_mwe

// Add necessary symbols to generated header
%{
#include "foo.h"
%}

// Process symbols in header
%include "foo.h"

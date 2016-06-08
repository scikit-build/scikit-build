
#include <boost/python.hpp>

#define CONCAT(X, Y) CONCAT_(X, Y)
#define CONCAT_(X, Y) X##Y

#define TOSTR(X) TOSTR_(X)
#define TOSTR_(X) #X

#define TB_CYCLE CONCAT(CONCAT(tb_, TBABEL_MODE_LOWER), _cycle)
#define TB_MODULE CONCAT(tbabel_boost_, TBABEL_MODE_LOWER)

typedef void (*cy_routine)(unsigned int, unsigned int,
                           PyObject *, PyObject *);

extern void TB_CYCLE(unsigned int, unsigned int, PyObject *, PyObject *);


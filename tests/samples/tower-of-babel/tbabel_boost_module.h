
#ifndef _TBABEL_BOOST_MODULE_H
#define _TBABEL_BOOST_MODULE_H

#include <boost/python.hpp>

typedef void (*cy_routine)(unsigned int, unsigned int,
                           PyObject *, PyObject *);

extern void tb_module_cycle(unsigned int, unsigned int, PyObject *, PyObject *);

#endif /* !_TBABEL_BOOST_MODULE_H */


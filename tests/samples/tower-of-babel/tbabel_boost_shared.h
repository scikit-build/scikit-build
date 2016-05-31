
#ifndef _TBABEL_BOOST_SHARED_H
#define _TBABEL_BOOST_SHARED_H

#include <boost/python.hpp>

typedef void (*cy_routine)(unsigned int, unsigned int,
                           PyObject *, PyObject *);

extern void tb_shared_cycle(unsigned int, unsigned int, PyObject *, PyObject *);

#endif /* !_TBABEL_BOOST_SHARED_H */


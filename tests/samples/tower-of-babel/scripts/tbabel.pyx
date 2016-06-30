
import sys

cdef extern from "stdlib.h":
    void srand(int)

cdef extern from "time.h":
    long int time(int)

cdef extern from "modules.h":
    pass

import tbabel_cython_static as tb_cy_static
import tbabel_cython_shared as tb_cy_shared
import tbabel_cython_module as tb_cy_module

import tbabel_boost_static as tb_boost_static
import tbabel_boost_shared as tb_boost_shared
import tbabel_boost_module as tb_boost_module

import tbabel_python as tb_python

def main():
    from argparse import ArgumentParser

    parser = ArgumentParser(description=(
        "Integration stress test that tests interoperability between all forms "
        "of extension modules and pure python code."))

    parser.add_argument("--depth", "-d", type=long,
                        default=2000, help="call stack depth")
    args = parser.parse_args()

    srand(time(0))

    modules = (
        tb_cy_static,
        tb_cy_shared,
        tb_cy_module,

        tb_boost_static,
        tb_boost_shared,
        tb_boost_module,
    )

    py_routines = [ x.cycle for x in modules ]
    cy_routines = [ x.get_c_handle() for x in modules ]

    py_routines.append(tb_python.cycle)

    sys.setrecursionlimit(long(1.75*args.depth))
    sys.stdout.write("PY -> ")
    tb_python.cycle(args.depth, 0, cy_routines, py_routines)

if __name__ == "__main__":
    main()


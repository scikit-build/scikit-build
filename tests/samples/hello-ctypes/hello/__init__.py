import ctypes
import sys
from os.path import realpath
from os.path import dirname
from os.path import join


def _get_lib_ext():
    if sys.platform.startswith('win32'):
        ext = '.dll'
    elif sys.platform.startswith('darwin'):
        ext = '.dylib'
    elif sys.platform.startswith('linux'):
        ext = '.so'
    else:
        raise Exception('Unknown operating system: %s' % sys.platform)
    return ext

def _find_ctypes_lib(libname, root_dir):
    ext = _get_lib_ext()
    import glob
    # windows doesnt always start names with lib
    print('Loading ctypes lib from root_dir = {!r}'.format(root_dir))
    print('libname = {!r}'.format(libname))
    candidates = []
    if sys.platform.startswith('win32'):
        candidates += list(glob.glob(join(root_dir, libname + '*' + ext)))
    else:
        candidates += list(glob.glob(join(root_dir, 'lib' + libname + '*' + ext)))

    if len(candidates) == 0:
        raise Exception('Unable to find ctype lib {} in {}'.format(libname, root_dir))
    if len(candidates) > 1:
        raise Exception('Too many matching libs: {}'.format(candidates))

    print('candidates = {!r}'.format(candidates))
    lib_fpath = candidates[0]
    return lib_fpath


def _load_ctypes_lib():
    root_dir = realpath(dirname(__file__))
    libname = 'hello'
    lib_fpath = _find_ctypes_lib(libname, root_dir)

    def def_cfunc(clib, return_type, func_name, arg_type_list):
        """ define the types that python needs to talk to c """
        cfunc = getattr(clib, func_name)
        cfunc.restype = return_type
        cfunc.argtypes = arg_type_list

    clib = ctypes.cdll[lib_fpath]
    clib.__LIB_FPATH__ = lib_fpath

    def_cfunc(clib, ctypes.c_int, 'elevation_example',        [])
    return clib


HELLO_CLIB = _load_ctypes_lib()


def elevation_example():
    return HELLO_CLIB.elevation_example()

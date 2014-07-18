import distutils


def setup(*args, **kw):
    """
    We wrap distutils setup so that we can do the CMake build, then proceed as usual with Distutils, appending
    our CMake-generated output as necessary
    """
    # TODO: implement cmake setup logic here
    # TODO: append outputs from CMake to package_data
    return distutils.setup(*args, **kw)

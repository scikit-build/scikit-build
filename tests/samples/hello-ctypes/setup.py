from skbuild import setup
import sys


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

setup(
    name="hello",
    version="1.2.3",
    description="a minimal example package",
    author='The scikit-build team',
    license="MIT",
    packages=['hello'],
    package_data={'hello': ['*' + _get_lib_ext()]},
)

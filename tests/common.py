
import os
import sys

from nose import with_setup

def force_sys_path():
    for path in os.environ.get("PYTHONPATH", "").split(os.pathsep):
        if path not in sys.path:
            print("INSERTING {}".format(path))
            sys.path.insert(0, path)

def test_case(func):
    return with_setup(force_sys_path, None)(func)


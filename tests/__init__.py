# -*- coding: utf-8 -*-

import inspect
import os
import os.path
import shutil
import sys

from contextlib import contextmanager
from types import FunctionType

from skbuild.cmaker import SKBUILD_DIR

PYTHON2 = (sys.version_info < (3, 0))

# NOTE(opadron): we need to use separate files for the Python 2 and 3 cases
# because there's no way to write code that executes a file that parses
# successfully for both versions.
if PYTHON2:
    from .exec_2 import execute
else:
    from .exec_3 import execute


@contextmanager
def push_dir(dir):
    old_cwd = os.getcwd()
    os.chdir(dir)
    yield
    os.chdir(old_cwd)


@contextmanager
def push_argv(argv):
    old_argv = sys.argv
    sys.argv = argv
    yield
    sys.argv = old_argv


def _noop():
    pass


class project_test():
    def __init__(self, project):
        self.project = project

    def __call__(self, func=_noop):
        def result(*args, **kwargs):
            dir = list(self.project)
            dir.insert(0, os.path.dirname(os.path.abspath(__file__)))
            dir = os.path.join(*dir)

            with push_dir(dir):
                result2 = func(*args, **kwargs)

            return result2

        return FunctionType(
            result.__code__,
            result.__globals__,
            func.__name__,
            result.__defaults__,
            result.__closure__
        )


class project_setup_py_test():
    def __init__(self, project, setup_args, clear_cache=False):
        self.project = project
        self.setup_args = setup_args
        self.clear_cache = clear_cache

        f = inspect.currentframe().f_back
        self.locals = f.f_locals
        self.globals = f.f_globals

    def __call__(self, func=_noop):
        @project_test(self.project)
        def result(*args, **kwargs):
            argv = ["setup.py"] + self.setup_args
            with push_argv(argv):
                if self.clear_cache and os.path.exists(SKBUILD_DIR):
                    shutil.rmtree(SKBUILD_DIR)

                setup_code = None
                with open("setup.py", "r") as fp:
                    setup_code = compile(fp.read(), "setup.py", mode="exec")

                if setup_code is not None:
                    execute(setup_code, self.globals, self.locals)

                result2 = func(*args, **kwargs)

            return result2

        return FunctionType(
            result.__code__,
            result.__globals__,
            func.__name__,
            result.__defaults__,
            result.__closure__
        )

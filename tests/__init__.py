# -*- coding: utf-8 -*-

import os
import os.path
import shutil
import six
import sys

from contextlib import contextmanager

from skbuild.cmaker import SKBUILD_DIR


@contextmanager
def push_dir(directory=None):
    old_cwd = os.getcwd()
    if directory:
        os.chdir(directory)
    yield
    os.chdir(old_cwd)


@contextmanager
def push_argv(argv):
    old_argv = sys.argv
    sys.argv = argv
    yield
    sys.argv = old_argv


def project_setup_py_test(project, setup_args, clear_cache=False):

    def dec(fun):

        @six.wraps(fun)
        def wrapped(*iargs, **ikwargs):

            dir = list(wrapped.project)
            dir.insert(0, os.path.dirname(os.path.abspath(__file__)))
            dir = os.path.join(*dir)

            with push_dir(dir), push_argv(["setup.py"] + wrapped.setup_args):

                if wrapped.clear_cache and os.path.exists(SKBUILD_DIR):
                    shutil.rmtree(SKBUILD_DIR)

                setup_code = None
                with open("setup.py", "r") as fp:
                    setup_code = compile(fp.read(), "setup.py", mode="exec")

                if setup_code is not None:
                    six.exec_(setup_code)

                result2 = fun(*iargs, **ikwargs)

            return result2

        wrapped.project = project
        wrapped.setup_args = setup_args
        wrapped.clear_cache = clear_cache

        return wrapped

    return dec

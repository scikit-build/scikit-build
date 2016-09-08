# -*- coding: utf-8 -*-

import distutils.dir_util
import os
import os.path
import shutil
import six
import sys

from contextlib import contextmanager

from skbuild.cmaker import SKBUILD_DIR
from skbuild.utils import push_dir


@contextmanager
def push_argv(argv):
    old_argv = sys.argv
    sys.argv = argv
    yield
    sys.argv = old_argv


@contextmanager
def push_env(**kwargs):
    """This context manager allow to set/unset environment variables.
    """
    saved_env = dict(os.environ)
    for var, value in kwargs.items():
        if value is not None:
            os.environ[var] = value
        elif var in os.environ:
            del os.environ[var]
    yield
    os.environ.clear()
    for (saved_var, saved_value) in saved_env.items():
        os.environ[saved_var] = saved_value


def project_setup_py_test(project, setup_args, clear_cache=False):

    def dec(fun):

        @six.wraps(fun)
        def wrapped(*iargs, **ikwargs):

            # Clear distutils.dir_util.mkpath() cache
            # See issue scikit-build#120
            distutils.dir_util._path_created = {}

            dir = list(wrapped.project)
            dir.insert(0, os.path.dirname(os.path.abspath(__file__)))
            dir = os.path.join(*dir)

            with push_dir(dir), push_argv(["setup.py"] + wrapped.setup_args):

                if wrapped.clear_cache:
                    # XXX We assume dist_dir is not customized
                    dest_dir = 'dist'
                    for dir_to_remove in [SKBUILD_DIR, dest_dir]:
                        if os.path.exists(dir_to_remove):
                            shutil.rmtree(dir_to_remove)

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

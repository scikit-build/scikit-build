
import os

from contextlib import contextmanager


@contextmanager
def push_dir(directory=None):
    old_cwd = os.getcwd()
    if directory:
        os.chdir(directory)
    yield
    os.chdir(old_cwd)

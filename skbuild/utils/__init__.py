
import errno
import os

from contextlib import contextmanager


@contextmanager
def push_dir(directory=None, make_directory=False):
    old_cwd = os.getcwd()
    if directory:
        if make_directory:
            mkdir_p(directory)
        os.chdir(directory)
    yield
    os.chdir(old_cwd)


def mkdir_p(path):
    # Adapted from http://stackoverflow.com/a/600612/1539918
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:  # pragma: no cover
            raise

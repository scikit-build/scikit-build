
import errno
import os

from functools import wraps


class ContextDecorator(object):
    """A base class or mixin that enables context managers to work as
    decorators."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __enter__(self):
        # Note: Returning self means that in "with ... as x", x will be self
        return self

    def __exit__(self, typ, val, traceback):
        pass

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwds):
            with self:
                return func(*args, **kwds)
        return inner


def mkdir_p(path):
    # Adapted from http://stackoverflow.com/a/600612/1539918
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:  # pragma: no cover
            raise


class push_dir(ContextDecorator):
    """Context manager to change current directory.
    """
    def __init__(self, directory=None, make_directory=False):
        """
        :param directory:
          Path to set as current working directory. If ``None``
          is passed, ``os.getcwd()`` is used instead.

        :param make_directory:
          If True, ``directory`` is created.
        """
        super(push_dir, self).__init__(
            directory=directory, make_directory=make_directory)

    def __enter__(self):
        self.old_cwd = os.getcwd()
        if self.directory:
            if self.make_directory:
                mkdir_p(self.directory)
            os.chdir(self.directory)
        return self

    def __exit__(self, typ, val, traceback):
        os.chdir(self.old_cwd)


def new_style(klass):
    """distutils/setuptools command classes are old-style classes, which
    won't work with mixins.

    To work around this limitation, we dynamically convert them to new style
    classes by creating a new class that inherits from them and also <object>.
    This ensures that <object> is always at the end of the MRO, even after
    being mixed in with other classes.
    """
    return type("NewStyleClass<{}>".format(klass.__name__), (klass, object), {})

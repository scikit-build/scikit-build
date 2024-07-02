from __future__ import annotations

import setuptools  # noqa: F401

try:
    import distutils.dir_util
    import distutils.sysconfig
except ImportError:
    import distutils  # Python < 3.10

import functools
import os
import os.path
import pathlib
import re
import subprocess
import sys
from contextlib import contextmanager
from unittest.mock import patch

import _pytest.tmpdir
import py.path
import requests

from skbuild.platform_specifics import get_platform
from skbuild.utils import push_dir

SAMPLES_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "samples",
)

__all__ = [
    "SAMPLES_DIR",
    "execute_setup_py",
    "get_cmakecache_variables",
    "initialize_git_repo_and_commit",
    "list_ancestors",
    "prepare_project",
    "project_setup_py_test",
    "push_dir",
    "push_env",
]


@contextmanager
def push_argv(argv):
    old_argv = sys.argv
    sys.argv = argv
    yield
    sys.argv = old_argv


@contextmanager
def push_env(**kwargs):
    """This context manager allow to set/unset environment variables."""
    saved_env = dict(os.environ)
    for var, value in kwargs.items():
        if value is not None:
            os.environ[var] = value
        elif var in os.environ:
            del os.environ[var]
    yield
    os.environ.clear()
    for saved_var, saved_value in saved_env.items():
        os.environ[saved_var] = saved_value


@contextmanager
def prepend_sys_path(paths):
    """This context manager allows to prepend paths to ``sys.path`` and restore the
    original list.
    """
    saved_paths = list(sys.path)
    sys.path = paths + saved_paths
    yield
    sys.path = saved_paths


def _tmpdir(basename: str) -> py.path.local:
    """This function returns a temporary directory similar to the one
    returned by the ``tmpdir`` pytest fixture.
    The difference is that the `basetemp` is not configurable using
    the pytest settings."""

    # Adapted from _pytest.tmpdir.tmpdir()
    basename = re.sub(r"[\W]", "_", basename)
    max_val = 30
    if len(basename) > max_val:
        basename = basename[:max_val]

    # Adapted from _pytest.tmpdir.TempdirFactory.getbasetemp()
    try:
        basetemp = _tmpdir._basetemp  # type: ignore[attr-defined]
    except AttributeError:
        temproot = py.path.local.get_temproot()
        user = _pytest.tmpdir.get_user()

        # use a sub-directory in the temproot to speed-up
        # make_numbered_dir() call
        rootdir = temproot.join(f"pytest-of-{user}") if user else temproot

        rootdir.ensure(dir=1)
        basetemp = py.path.local.make_numbered_dir(prefix="pytest-", rootdir=rootdir)

    # Adapted from _pytest.tmpdir.TempdirFactory.mktemp
    return py.path.local.make_numbered_dir(prefix=basename, keep=0, rootdir=basetemp, lock_timeout=None)


def _copy(src, target):
    """
    Copies a single entry (file, dir) named 'src' to 'target'. Softlinks are
    processed properly as well.

    Copied from pytest-datafiles/pytest_datafiles.py (MIT License)
    """
    if not src.exists():
        msg = f"'{src}' does not exist!"
        raise ValueError(msg)

    if src.isdir():
        src.copy(target / src.basename)
    elif src.islink():
        (target / src.basename).mksymlinkto(src.realpath())
    else:  # file
        src.copy(target)


def _copy_dir(target_dir, src_dir, on_duplicate="exception", keep_top_dir=False):
    """
    Copies all entries (files, dirs) from 'src_dir' to 'target_dir' taking
    into account the 'on_duplicate' option (which defines what should happen if
    an entry already exists: raise an exception, overwrite it or ignore it).

    Adapted from pytest-datafiles/pytest_datafiles.py (MIT License)
    """
    src_files = []

    if isinstance(src_dir, str):
        src_dir = py.path.local(src_dir)

    if keep_top_dir:
        src_files = src_dir
    elif src_dir.isdir():
        src_files.extend(src_dir.listdir())
    else:
        src_files.append(src_dir)

    for entry in src_files:
        target_entry = target_dir / entry.basename
        if not target_entry.exists() or on_duplicate == "overwrite":
            _copy(entry, target_dir)
        elif on_duplicate == "exception":
            msg = f"'{target_entry}' already exists (src {entry})"
            raise ValueError(msg)


def initialize_git_repo_and_commit(project_dir, verbose=True):
    """Convenience function creating a git repository in ``project_dir``.

    If ``project_dir`` does NOT contain a ``.git`` directory, a new
    git repository with one commit containing all the directories and files
    is created.
    """
    if isinstance(project_dir, str):
        project_dir = py.path.local(project_dir)

    if project_dir.join(".git").exists():
        return

    # If any, exclude virtualenv files
    project_dir.join(".gitignore").write(".env")

    with push_dir(str(project_dir)):
        for cmd in [
            ["git", "init"],
            ["git", "config", "user.name", "scikit-build"],
            ["git", "config", "user.email", "test@test"],
            ["git", "config", "commit.gpgsign", "false"],
            ["git", "add", "-A"],
            ["git", "reset", ".gitignore"],
            ["git", "commit", "-m", "Initial commit"],
        ]:
            subprocess.run(cmd, stdout=None if verbose else subprocess.PIPE, check=True)


def prepare_project(project, tmp_project_dir, force=False):
    """Convenience function setting up the build directory ``tmp_project_dir``
    for the selected sample ``project``.

    If ``tmp_project_dir`` does not exist, it is created.

    If ``tmp_project_dir`` is empty, the sample ``project`` is copied into it.
    Specifying ``force=True`` will copy the files even if ``tmp_project_dir``
    is not empty.
    """
    if isinstance(tmp_project_dir, str):
        tmp_project_dir = py.path.local(tmp_project_dir)

    # Create project directory if it does not exist
    if not tmp_project_dir.exists():
        tmp_project_dir = _tmpdir(project)

    # If empty or if force is True, copy project files and initialize git
    if not tmp_project_dir.listdir() or force:
        _copy_dir(tmp_project_dir, os.path.join(SAMPLES_DIR, project))


@contextmanager
def execute_setup_py(project_dir, setup_args, disable_languages_test=False):
    """Context manager executing ``setup.py`` with the given arguments.

    It yields after changing the current working directory
    to ``project_dir``.
    """

    # See https://stackoverflow.com/questions/9160227/dir-util-copy-tree-fails-after-shutil-rmtree
    distutils.dir_util._path_created.clear()  # type: ignore[attr-defined]

    # Clear _PYTHON_HOST_PLATFORM to ensure value sets in skbuild.setuptools_wrap.setup() does not
    # influence other tests.
    if "_PYTHON_HOST_PLATFORM" in os.environ:
        del os.environ["_PYTHON_HOST_PLATFORM"]

    with push_dir(str(project_dir)), push_argv(["setup.py", *setup_args]), prepend_sys_path([str(project_dir)]):
        with open("setup.py") as fp:
            setup_code = compile(fp.read(), "setup.py", mode="exec")

            if setup_code is not None:
                if disable_languages_test:
                    platform = get_platform()
                    original_write_test_cmakelist = platform.write_test_cmakelist

                    def write_test_cmakelist_no_languages(_self, _languages):
                        original_write_test_cmakelist([])

                    with patch.object(type(platform), "write_test_cmakelist", new=write_test_cmakelist_no_languages):
                        exec(setup_code)

                else:
                    exec(setup_code)

        yield


def project_setup_py_test(project, setup_args, tmp_dir=None, verbose_git=True, disable_languages_test=False, ret=False):
    def dec(fun):
        @functools.wraps(fun)
        def wrapped(*iargs, **ikwargs):
            if wrapped.tmp_dir is None:  # type: ignore[attr-defined]
                wrapped.tmp_dir = _tmpdir(fun.__name__)  # type: ignore[attr-defined]
                prepare_project(wrapped.project, wrapped.tmp_dir)  # type: ignore[attr-defined]
                initialize_git_repo_and_commit(wrapped.tmp_dir, verbose=wrapped.verbose_git)  # type: ignore[attr-defined]

            with execute_setup_py(wrapped.tmp_dir, wrapped.setup_args, disable_languages_test=disable_languages_test):  # type: ignore[attr-defined]
                result2 = fun(*iargs, **ikwargs)

            if ret:
                return wrapped.tmp_dir, result2  # type: ignore[attr-defined]
            return None

        wrapped.project = project  # type: ignore[attr-defined]
        wrapped.setup_args = setup_args  # type: ignore[attr-defined]
        wrapped.tmp_dir = tmp_dir  # type: ignore[attr-defined]
        wrapped.verbose_git = verbose_git  # type: ignore[attr-defined]

        return wrapped

    return dec


def get_cmakecache_variables(cmakecache):
    """Returns a dictionary of all variables found in given CMakeCache.txt.

    Dictionary entries are tuple of the
    form ``(variable_type, variable_value)``.

    Possible `variable_type` are documented
    `here <https://cmake.org/cmake/help/v3.7/prop_cache/TYPE.html>`_.
    """
    results = {}
    cache_entry_pattern = re.compile(r"^([\w\d_-]+):([\w]+)=")
    with open(cmakecache) as content:
        for full_line in content.readlines():
            line = full_line.strip()
            result = cache_entry_pattern.match(line)
            if result:
                variable_name = result.group(1)
                variable_type = result.group(2)
                variable_value = line.split("=")[1]
                results[variable_name] = (variable_type, variable_value)
    return results


def is_site_reachable(url):
    """Return True if the given website can be accessed"""
    try:
        request = requests.get(url)
        return request.status_code == 200
    except requests.exceptions.ConnectionError:
        return False


def list_ancestors(path):
    """Return logical ancestors of the path."""
    return [str(parent) for parent in pathlib.PurePosixPath(path).parents if str(parent) != "."]


def get_ext_suffix():
    """Return python extension suffix."""
    return distutils.sysconfig.get_config_var("EXT_SUFFIX")

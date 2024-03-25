"""This module defines functions generally useful in scikit-build."""

from __future__ import annotations

import contextlib
import logging
import os
import typing
from contextlib import contextmanager
from typing import Any, Iterable, Iterator, Mapping, NamedTuple, Sequence, TypeVar

from distutils.command.build_py import build_py as distutils_build_py
from distutils.errors import DistutilsTemplateError
from distutils.filelist import FileList
from distutils.text_file import TextFile

from .._compat.typing import Protocol

if typing.TYPE_CHECKING:
    import setuptools._distutils.dist


class CommonLog(Protocol):
    """Protocol for loggers with an info method."""

    # pylint: disable-next=missing-function-docstring
    def info(self, __msg: str, *args: object) -> None: ...


logger: CommonLog

try:
    import setuptools.logging

    skb_log = logging.getLogger("skbuild")
    skb_log.setLevel(logging.INFO)
    logging_module = True
    logger = skb_log

except ImportError:
    from distutils import log as distutils_log

    logger = distutils_log
    logging_module = False


class Distribution(NamedTuple):
    """Distribution stand-in."""

    script_name: str


def _log_warning(msg: str, *args: object) -> None:
    try:
        if logging_module:
            skb_log.warning(msg, *args)
        else:
            distutils_log.warn(msg, *args)
    except ValueError:
        # Setuptools might disconnect the logger. That shouldn't be an error for a warning.
        print(msg % args, flush=True)


def mkdir_p(path: str) -> None:
    """Ensure directory ``path`` exists. If needed, parent directories
    are created.
    """
    return os.makedirs(path, exist_ok=True)


Self = TypeVar("Self", bound="push_dir")


class push_dir(contextlib.ContextDecorator):
    """Context manager to change current directory."""

    def __init__(self, directory: str | None = None, make_directory: bool = False) -> None:
        """
        :param directory:
          Path to set as current working directory. If ``None``
          is passed, ``os.getcwd()`` is used instead.

        :param make_directory:
          If True, ``directory`` is created.
        """
        super().__init__()
        self.directory = directory
        self.make_directory = make_directory
        self.old_cwd: str | None = None

    def __enter__(self: Self) -> Self:
        self.old_cwd = os.getcwd()
        if self.directory:
            if self.make_directory:
                os.makedirs(self.directory, exist_ok=True)
            os.chdir(self.directory)
        return self

    def __exit__(self, typ: None, val: None, traceback: None) -> None:
        assert self.old_cwd is not None
        os.chdir(self.old_cwd)


class PythonModuleFinder(distutils_build_py):
    """Convenience class to search for python modules.

    This class is based on ``distutils.command.build_py.build_by`` and
    provides a specialized version of ``find_all_modules()``.
    """

    distribution: Distribution  # type: ignore[assignment]

    # pylint: disable-next=super-init-not-called
    def __init__(
        self,
        packages: Sequence[str],
        package_dir: Mapping[str, str],
        py_modules: Sequence[str],
        alternative_build_base: str | None = None,
    ) -> None:
        """
        :param packages: List of packages to search.
        :param package_dir: Dictionary mapping ``package`` with ``directory``.
        :param py_modules: List of python modules.
        :param alternative_build_base: Additional directory to search in.
        """
        self.packages = packages
        self.package_dir = package_dir
        self.py_modules = py_modules
        self.alternative_build_base = alternative_build_base

        self.distribution = Distribution("setup.py")

    def find_all_modules(self, project_dir: str | None = None) -> list[Any | tuple[str, str, str]]:
        """Compute the list of all modules that would be built by
        project located in current directory, whether they are
        specified one-module-at-a-time ``py_modules`` or by whole
        packages ``packages``.

        By default, the function will search for modules in the current
        directory. Specifying ``project_dir`` parameter allow to change
        this.

        Return a list of tuples ``(package, module, module_file)``.
        """
        with push_dir(project_dir):
            # TODO: typestubs for distutils
            return super().find_all_modules()  # type: ignore[no-any-return, no-untyped-call]

    def find_package_modules(self, package: str, package_dir: str) -> Iterable[tuple[str, str, str]]:
        """Temporally prepend the ``alternative_build_base`` to ``module_file``.
        Doing so will ensure modules can also be found in other location
        (e.g ``skbuild.constants.CMAKE_INSTALL_DIR``).
        """
        if package_dir and not os.path.exists(package_dir) and self.alternative_build_base is not None:
            package_dir = os.path.join(self.alternative_build_base, package_dir)

        modules: Iterable[tuple[str, str, str]] = super().find_package_modules(package, package_dir)  # type: ignore[no-untyped-call]

        # Strip the alternative base from module_file
        def _strip_directory(entry: tuple[str, str, str]) -> tuple[str, str, str]:
            module_file = entry[2]
            if self.alternative_build_base is not None and module_file.startswith(self.alternative_build_base):
                module_file = module_file[len(self.alternative_build_base) + 1 :]
            return entry[0], entry[1], module_file

        return map(_strip_directory, modules)

    def check_module(self, module: str, module_file: str) -> bool:
        """Return True if ``module_file`` belongs to ``module``."""
        if self.alternative_build_base is not None:
            updated_module_file = os.path.join(self.alternative_build_base, module_file)
            if os.path.exists(updated_module_file):
                module_file = updated_module_file
        if not os.path.isfile(module_file):
            _log_warning("file %s (for module %s) not found", module_file, module)
            return False
        return True


OptStr = TypeVar("OptStr", str, None)


def to_platform_path(path: OptStr) -> OptStr:
    """Return a version of ``path`` where all separator are :attr:`os.sep`"""
    if path is None:
        return path
    return path.replace("/", os.sep).replace("\\", os.sep)


def to_unix_path(path: OptStr) -> OptStr:
    """Return a version of ``path`` where all separator are ``/``"""
    if path is None:
        return path
    return path.replace("\\", "/")


@contextmanager
def distribution_hide_listing(
    distribution: setuptools._distutils.dist.Distribution | Distribution,
) -> Iterator[bool | int]:
    """Given a ``distribution``, this context manager temporarily
    sets distutils threshold to WARN if ``--hide-listing`` argument
    was provided.

    It yields True if ``--hide-listing`` argument was provided.
    """

    hide_listing = getattr(distribution, "hide_listing", False)
    wheel_log = logging.getLogger("wheel")
    root_log = logging.getLogger()  # setuptools 65.6+ needs this hidden too
    if logging_module:
        # Setuptools 60.2+, will always be on Python 3.7+
        old_wheel_level = wheel_log.getEffectiveLevel()
        old_root_level = root_log.getEffectiveLevel()
        try:
            if hide_listing:
                wheel_log.setLevel(logging.WARNING)
                root_log.setLevel(logging.WARNING)
                # The classic logger doesn't respond to set_threshold anymore,
                # but it does log info and above to stdout, so let's hide that
                with open(os.devnull, "w", encoding="utf-8") as f, contextlib.redirect_stdout(f):
                    yield hide_listing
            else:
                yield hide_listing
        finally:
            if hide_listing:
                wheel_log.setLevel(old_wheel_level)
                root_log.setLevel(old_root_level)

    else:
        old_threshold = distutils_log._global_log.threshold  # type: ignore[attr-defined]
        if hide_listing:
            distutils_log.set_threshold(distutils_log.WARN)
        try:
            yield hide_listing
        finally:
            distutils_log.set_threshold(old_threshold)


def parse_manifestin(template: str) -> list[str]:
    """This function parses template file (usually MANIFEST.in)"""
    if not os.path.exists(template):
        return []

    template_file = TextFile(
        template,
        strip_comments=True,
        skip_blanks=True,
        join_lines=True,
        lstrip_ws=True,
        rstrip_ws=True,
        collapse_join=True,
    )

    file_list = FileList()
    try:
        while True:
            line = template_file.readline()
            if line is None:  # end of file
                break

            try:
                file_list.process_template_line(line)
            # the call above can raise a DistutilsTemplateError for
            # malformed lines, or a ValueError from the lower-level
            # convert_path function
            except (DistutilsTemplateError, ValueError) as msg:
                filename = template_file.filename if hasattr(template_file, "filename") else "Unknown"
                current_line = template_file.current_line if hasattr(template_file, "current_line") else "Unknown"
                print(f"{filename}, line {current_line}: {msg}", flush=True)
        return file_list.files
    finally:
        template_file.close()

"""This module defines custom implementation of ``build_py`` setuptools
command."""

from __future__ import annotations

import os

from setuptools.command.build_py import build_py as _build_py

from ..constants import CMAKE_INSTALL_DIR
from ..utils import distribution_hide_listing, logger
from . import set_build_base_mixin


class build_py(set_build_base_mixin, _build_py):
    """Custom implementation of ``build_py`` setuptools command."""

    def initialize_options(self) -> None:
        """Handle --hide-listing option.

        Initializes ``outfiles_count``.
        """
        super().initialize_options()
        self.outfiles_count = 0

    def build_module(self, module: str | list[str] | tuple[str, ...], module_file: str, package: str) -> None:
        """Handle --hide-listing option.

        Increments ``outfiles_count``.
        """
        super().build_module(module, module_file, package)  # type: ignore[no-untyped-call]
        self.outfiles_count += 1

    def run(self, *args: object, **kwargs: object) -> None:
        """Handle --hide-listing option.

        Display number of copied files. It corresponds to the value
        of ``outfiles_count``.
        """
        with distribution_hide_listing(self.distribution):
            super().run(*args, **kwargs)
        logger.info("copied %d files", self.outfiles_count)

    def find_modules(self) -> list[tuple[str, str, str]]:
        """Finds individually-specified Python modules, ie. those listed by
        module name in 'self.py_modules'.  Returns a list of tuples (package,
        module_base, filename): 'package' is a tuple of the path through
        package-space to the module; 'module_base' is the bare (no
        packages, no dots) module name, and 'filename' is the path to the
        ".py" file (relative to the distribution root) that implements the
        module.
        """
        # Map package names to tuples of useful info about the package:
        #    (package_dir, checked)
        # package_dir - the directory where we'll find source files for
        #   this package
        # checked - true if we have checked that the package directory
        #   is valid (exists, contains __init__.py, ... ?)
        packages: dict[str, tuple[str, bool]] = {}

        # List of (package, module, filename) tuples to return
        modules: list[tuple[str, str, str]] = []

        # We treat modules-in-packages almost the same as toplevel modules,
        # just the "package" for a toplevel is empty (either an empty
        # string or empty list, depending on context).  Differences:
        #   - don't check for __init__.py in directory for empty package
        for module in self.py_modules:
            path = module.split(".")
            package = ".".join(path[0:-1])
            module_base = path[-1]

            try:
                (package_dir, checked) = packages[package]
            except KeyError:
                package_dir = self.get_package_dir(package)  # type: ignore[no-untyped-call]
                checked = False

            if not checked:
                init_py = self.check_package(package, package_dir)  # type: ignore[no-untyped-call]
                packages[package] = (package_dir, True)
                if init_py:
                    modules.append((package, "__init__", init_py))

            # XXX perhaps we should also check for just .pyc files
            # (so greedy closed-source bastards can distribute Python
            # modules too)
            module_file = os.path.join(package_dir, module_base + ".py")

            # skbuild: prepend CMAKE_INSTALL_DIR if file exists in the
            # CMake install tree.
            if os.path.exists(os.path.join(CMAKE_INSTALL_DIR(), module_file)):
                module_file = os.path.join(CMAKE_INSTALL_DIR(), module_file)

            if not self.check_module(module, module_file):  # type: ignore[no-untyped-call]
                continue

            modules.append((package, module_base, module_file))

        return modules

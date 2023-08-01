"""This module defines custom implementation of ``egg_info`` setuptools
command."""

from __future__ import annotations

import os
import os.path
from typing import Any

from setuptools.command.egg_info import egg_info as _egg_info

from ..constants import CMAKE_INSTALL_DIR
from ..utils import to_unix_path
from . import set_build_base_mixin


class egg_info(set_build_base_mixin, _egg_info):
    """Custom implementation of ``egg_info`` setuptools command."""

    def finalize_options(self, *args: Any, **kwargs: Any) -> None:
        if self.egg_base is None:
            if self.distribution.package_dir is not None and len(self.distribution.package_dir) == 1:
                # Recover directory specified in setup() function
                # using `package_dir={'':<egg_base>}`
                # This is required to successfully update the python path when
                # running the test command.
                package_name = next(iter(self.distribution.package_dir.keys()))
                egg_base = to_unix_path(next(iter(self.distribution.package_dir.values())))
                cmake_install_dir = to_unix_path(CMAKE_INSTALL_DIR())
                if egg_base.startswith(cmake_install_dir):
                    egg_base = egg_base[len(cmake_install_dir) + 1 :]
                if package_name and egg_base.endswith(package_name):
                    egg_base = egg_base[: -len(package_name) - 1]
                if not egg_base:
                    egg_base = "."
                # pylint:disable=attribute-defined-outside-init
                self.egg_base = egg_base
        else:
            script_path = os.path.abspath(self.distribution.script_name or "")
            script_dir = os.path.dirname(script_path)
            # pylint:disable=attribute-defined-outside-init
            self.egg_base = os.path.join(script_dir, self.egg_base)

        super().finalize_options(*args, **kwargs)  # type: ignore[misc]

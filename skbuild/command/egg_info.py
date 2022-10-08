"""This module defines custom implementation of ``egg_info`` setuptools
command."""

import os
import os.path

from setuptools.command.egg_info import egg_info as _egg_info

from ..constants import CMAKE_INSTALL_DIR
from ..utils import to_unix_path
from . import set_build_base_mixin


class egg_info(set_build_base_mixin, _egg_info):
    """Custom implementation of ``egg_info`` setuptools command."""

    def finalize_options(self, *args: object, **kwargs: object) -> None:
        if self.egg_base is None:
            if self.distribution.package_dir is not None and len(self.distribution.package_dir) == 1:  # type: ignore[attr-defined]
                # Recover directory specified in setup() function
                # using `package_dir={'':<egg_base>}`
                # This is required to successfully update the python path when
                # running the test command.
                package_name = list(self.distribution.package_dir.keys())[0]  # type: ignore[attr-defined]
                egg_base = to_unix_path(list(self.distribution.package_dir.values())[0])  # type: ignore[attr-defined]
                cmake_install_dir = to_unix_path(CMAKE_INSTALL_DIR())
                if egg_base.startswith(cmake_install_dir):
                    egg_base = egg_base[len(cmake_install_dir) + 1 :]
                if package_name and egg_base.endswith(package_name):
                    egg_base = egg_base[: -len(package_name) - 1]
                if egg_base == "":
                    egg_base = "."
                # pylint:disable=attribute-defined-outside-init
                self.egg_base = egg_base
        else:
            script_path = os.path.abspath(self.distribution.script_name)  # type: ignore[attr-defined]
            script_dir = os.path.dirname(script_path)
            # pylint:disable=attribute-defined-outside-init
            self.egg_base = os.path.join(script_dir, self.egg_base)

        super().finalize_options(*args, **kwargs)  # type: ignore[misc]

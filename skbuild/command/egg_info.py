"""This module defines custom implementation of ``egg_info`` setuptools
command."""

import os
import os.path

from setuptools.command.egg_info import egg_info as _egg_info

from . import set_build_base_mixin
from ..utils import new_style


class egg_info(set_build_base_mixin, new_style(_egg_info)):
    """Custom implementation of ``egg_info`` setuptools command."""

    def finalize_options(self):
        if self.egg_base is not None:
            script_path = os.path.abspath(self.distribution.script_name)
            script_dir = os.path.dirname(script_path)
            self.egg_base = os.path.join(script_dir, self.egg_base)

        super(egg_info, self).finalize_options()

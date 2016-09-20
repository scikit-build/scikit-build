"""This module defines custom implementation of ``sdist`` setuptools command."""

from distutils.command.sdist import sdist as _sdist

from . import set_build_base_mixin
from ..utils import new_style


class sdist(set_build_base_mixin, new_style(_sdist)):
    """Custom implementation of ``sdist`` setuptools command."""
    def run(self, *args, **kwargs):
        """Force :class:`.egg_info.egg_info` command to run."""
        self.run_command('egg_info')
        super(sdist, self).run(*args, **kwargs)

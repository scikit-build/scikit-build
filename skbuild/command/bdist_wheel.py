"""This module defines custom implementation of ``bdist_wheel`` setuptools
command."""

from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

from . import set_build_base_mixin
from ..utils import new_style


class bdist_wheel(set_build_base_mixin, new_style(_bdist_wheel)):
    """Custom implementation of ``bdist_wheel`` setuptools command."""

    user_options = _bdist_wheel.user_options + [
        ('hide-listing', None,
         "do not display list of files being included in the distribution"),
    ]

    boolean_options = _bdist_wheel.boolean_options + ['hide-listing']

    def initialize_options(self):
        super(bdist_wheel, self).initialize_options()
        self.hide_listing = 0

    def run(self, *args, **kwargs):
        self.distribution.get_command_obj(
            'build_py').hide_listing = self.hide_listing
        self.distribution.get_command_obj(
            'install_data').hide_listing = self.hide_listing
        self.distribution.get_command_obj(
            'install_lib').hide_listing = self.hide_listing
        self.distribution.get_command_obj(
            'install_scripts').hide_listing = self.hide_listing

        super(bdist_wheel, self).run(*args, **kwargs)


import os

from setuptools.command.egg_info import egg_info as _egg_info

from . import new_style, set_build_base_mixin


class egg_info(set_build_base_mixin, new_style(_egg_info)):
    def finalize_options(self):
        if self.egg_base is not None:
            script_path = os.path.abspath(self.distribution.script_name)
            script_dir = os.path.dirname(script_path)
            self.egg_base = os.path.join(script_dir, self.egg_base)

        super(egg_info, self).finalize_options()


from setuptools.command.install import install as _install

from . import new_style, set_build_base_mixin


class install(set_build_base_mixin, new_style(_install)):
    pass


from setuptools.command.install import install as _install

from . import set_build_base_mixin
from ..utils import new_style


class install(set_build_base_mixin, new_style(_install)):
    pass


try:
    from setuptools.command.build import build as _build
except ImportError:
    from distutils.command.build import build as _build

from . import new_style, set_build_base_mixin


class build(set_build_base_mixin, new_style(_build)):
    pass

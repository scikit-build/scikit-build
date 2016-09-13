
try:
    from setuptools.command.bdist import bdist as _bdist
except ImportError:
    from distutils.command.bdist import bdist as _bdist

from . import set_build_base_mixin
from ..utils import new_style


class bdist(set_build_base_mixin, new_style(_bdist)):
    pass

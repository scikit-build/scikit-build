
from distutils.command.sdist import sdist as _sdist

from . import new_style, set_build_base_mixin


class sdist(set_build_base_mixin, new_style(_sdist)):
    pass

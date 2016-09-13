
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

from . import set_build_base_mixin
from ..utils import new_style


class bdist_wheel(set_build_base_mixin, new_style(_bdist_wheel)):
    pass

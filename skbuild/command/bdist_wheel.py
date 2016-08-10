
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

from . import new_style, set_build_base_mixin


class bdist_wheel(set_build_base_mixin, new_style(_bdist_wheel)):
    pass

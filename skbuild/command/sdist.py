
from distutils.command.sdist import sdist as _sdist

from . import set_build_base_mixin
from ..utils import new_style


class sdist(set_build_base_mixin, new_style(_sdist)):
    def run(self, *args, **kwargs):
        self.run_command('egg_info')
        super(sdist, self).run(*args, **kwargs)

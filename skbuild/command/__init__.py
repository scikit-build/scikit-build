"""Collection of objects allowing to customize behavior of standard
distutils and setuptools commands.
"""

from typing import List, Optional

from .. import cmaker
from ..typing import Protocol
from ..utils import Distribution


class CommandMixinProtocol(Protocol):
    """Protocol for commands that use CMake."""

    build_base: str
    distribution: Distribution
    outfiles: List[str]
    install_lib: Optional[str]
    install_platlib: str

    def finalize_options(self, *args, **kwargs) -> None:
        ...


class set_build_base_mixin:
    """Mixin allowing to override distutils and setuptools commands."""

    def finalize_options(self: CommandMixinProtocol, *args, **kwargs):
        """Override built-in function and set a new `build_base`."""
        try:
            if not self.build_base or self.build_base == "build":
                self.build_base = cmaker.SETUPTOOLS_INSTALL_DIR()
        except AttributeError:
            pass

        super().finalize_options(*args, **kwargs)  # type: ignore[misc]

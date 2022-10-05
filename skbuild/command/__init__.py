"""Collection of objects allowing to customize behavior of standard
distutils and setuptools commands.
"""

from typing import List, Optional

from ..constants import SETUPTOOLS_INSTALL_DIR
from ..typing import Protocol
from ..utils import Distribution


class CommandMixinProtocol(Protocol):
    """Protocol for commands that use CMake."""

    build_base: str
    distribution: Distribution
    outfiles: List[str]
    install_lib: Optional[str]
    install_platlib: str

    def finalize_options(self, *args: object, **kwargs: object) -> None:
        ...


class set_build_base_mixin:
    """Mixin allowing to override distutils and setuptools commands."""

    def finalize_options(self: CommandMixinProtocol, *args: object, **kwargs: object) -> None:
        """Override built-in function and set a new `build_base`."""
        build_base = getattr(self, "build_base", "EMPTY")
        if not build_base or build_base == "build":
            self.build_base = SETUPTOOLS_INSTALL_DIR()

        super().finalize_options(*args, **kwargs)  # type: ignore[misc]

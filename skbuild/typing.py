import sys

if sys.version_info >= (3, 8):
    from typing import Protocol, TypedDict, Final, Literal
else:
    from typing_extensions import Protocol, TypedDict, Final, Literal

__all__ = ["Protocol", "TypedDict", "Final", "Literal"]
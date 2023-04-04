from __future__ import annotations

import sys

if sys.version_info >= (3, 8):
    from typing import Final, Literal, Protocol, TypedDict
else:
    from typing_extensions import Final, Literal, Protocol, TypedDict

__all__ = ["Protocol", "TypedDict", "Final", "Literal"]

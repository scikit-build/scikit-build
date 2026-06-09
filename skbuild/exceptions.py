"""
This module defines exceptions commonly used in scikit-build.

``SKBuildError`` is now an alias of the setuptools ``SetupError`` raised by
the scikit-build-core setuptools plugin, kept so that existing
``except SKBuildError`` clauses continue to work.
"""

from __future__ import annotations

from setuptools.errors import SetupError as SKBuildError

__all__ = ["SKBuildError"]


def __dir__() -> list[str]:
    return __all__

"""
This module defines exceptions commonly used in scikit-build.
"""

from __future__ import annotations


class SKBuildError(RuntimeError):
    """Exception raised when an error occurs while configuring or building a
    project.
    """


class SKBuildInvalidFileInstallationError(SKBuildError):
    """Exception raised when a file is being installed into an invalid location."""


class SKBuildGeneratorNotFoundError(SKBuildError):
    """Exception raised when no suitable generator is found for the current
    platform.
    """

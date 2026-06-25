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


class SKBuildDeprecationWarning(FutureWarning):
    """Warning for scikit-build features that are removed or changed when the
    scikit-build-core setuptools backend takes over in the next major release.
    """

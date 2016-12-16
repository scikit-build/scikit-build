"""
This module defines exceptions commonly used in scikit-build.
"""


class SKBuildError(RuntimeError):
    """Exception raised when an error occurs while configuring or building a
    project.
    """
    pass


class SKBuildGeneratorNotFoundError(SKBuildError):
    """Exception raised when no suitable generator is found for the current
    platform.
    """
    pass

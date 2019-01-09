"""This module defines custom ``generate_source_manifest`` setuptools
command."""

import os
import subprocess
import sys

from distutils.cmd import Command

from . import set_build_base_mixin
from ..constants import SKBUILD_DIR, SKBUILD_MARKER_FILE
from ..utils import new_style


class generate_source_manifest(set_build_base_mixin, new_style(Command)):
    """Custom setuptools command generating a `MANIFEST` file if
    not already provided."""

    description = "generate source MANIFEST"

    # pylint:disable=no-self-use
    def initialize_options(self):
        """Set default values for all the options that this command supports."""
        pass

    def run(self):
        """
        If neither a `MANIFEST`, nor a `MANIFEST.in` file is provided, and
        we are in a git repo, try to create a `MANIFEST` file from the output of
        `git ls-tree --name-only -r HEAD`.

        We need a reliable way to tell if an existing `MANIFEST` file is one
        we've generated.  distutils already uses a first-line comment to tell
        if the `MANIFEST` file was generated from `MANIFEST.in`, so we use a
        dummy file, `_skbuild_MANIFEST`, to avoid confusing distutils.
        """
        do_generate = (
            # If there's a MANIFEST.in file, we assume that we had nothing to do
            # with the project's manifest.
            not os.path.exists('MANIFEST.in')

            # otherwise, we check to see that there is no MANIFEST, ...
            and not os.path.exists('MANIFEST')  # ... or ...

            # ... (if there is one,) that we created it
            or os.path.exists(SKBUILD_MARKER_FILE())
        )

        if do_generate:

            try:
                with open('MANIFEST', 'wb') as manifest_file:
                    # Since Git < 2.11 does not support --recurse-submodules option, fallback to
                    # regular listing.
                    try:
                        manifest_file.write(
                            subprocess.check_output(['git', 'ls-files', '--recurse-submodules'])
                        )
                    except subprocess.CalledProcessError:
                        manifest_file.write(
                             subprocess.check_output(['git', 'ls-files'])
                         )
            except subprocess.CalledProcessError:
                sys.stderr.write(
                    '\n\n'
                    'Since scikit-build could not find MANIFEST.in or '
                    'MANIFEST, it tried to generate a MANIFEST file '
                    'automatically, but could not because it could not '
                    'determine which source files to include.\n\n'
                    'The command used was "git ls-files"\n'
                    '\n\n'
                )
                raise

            if not os.path.exists(SKBUILD_DIR()):
                os.makedirs(SKBUILD_DIR())

            with open(SKBUILD_MARKER_FILE(), 'w'):  # touch
                pass

    def finalize_options(self, *args, **kwargs):
        """Set final values for all the options that this command supports."""
        pass

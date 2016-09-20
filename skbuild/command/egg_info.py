"""This module defines custom implementation of ``egg_info`` setuptools
command."""

import os
import os.path
import subprocess
import sys

from setuptools.command.egg_info import egg_info as _egg_info

from . import set_build_base_mixin
from ..constants import SKBUILD_DIR
from ..utils import new_style

SKBUILD_MARKER_FILE = os.path.join(SKBUILD_DIR, "_skbuild_MANIFEST")


class egg_info(set_build_base_mixin, new_style(_egg_info)):
    """Custom implementation of ``egg_info`` setuptools command generating
    a `MANIFEST` file if not already provided."""
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
            or not os.path.exists('MANIFEST')  # ... or ...

            # ... (if there is one,) that we created it
            or os.path.exists(SKBUILD_MARKER_FILE)
        )

        if do_generate:
            try:
                with open('MANIFEST', 'wb') as manifest_file:
                    manifest_file.write(
                        subprocess.check_output(
                            ['git', 'ls-tree', '--name-only', '-r', 'HEAD'])
                    )
            except subprocess.CalledProcessError:
                sys.stderr.write(
                    '\n\n'
                    'Since scikit-build could not find MANIFEST.in or '
                    'MANIFEST, it tried to generate a MANIFEST file '
                    'automatically, but could not because it could not '
                    'determine which source files to include.\n\n'
                    'The command used was "git ls-tree --name-only -r HEAD"\n'
                    '\n\n'
                )

                raise

            if not os.path.exists(SKBUILD_DIR):
                os.makedirs(SKBUILD_DIR)

            with open(SKBUILD_MARKER_FILE, 'w'):  # touch
                pass

        super(egg_info, self).run()

    def finalize_options(self):
        if self.egg_base is not None:
            script_path = os.path.abspath(self.distribution.script_name)
            script_dir = os.path.dirname(script_path)
            self.egg_base = os.path.join(script_dir, self.egg_base)

        super(egg_info, self).finalize_options()
